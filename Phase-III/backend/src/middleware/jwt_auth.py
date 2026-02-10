"""JWT authentication middleware for token verification.

This module provides JWT token verification functionality including signature
validation, expiration checking, claims extraction, user existence validation,
account status validation, and password change timestamp validation.

Security Features:
- Verifies JWT signature using BETTER_AUTH_SECRET (HS256 algorithm)
- Validates token expiration timestamps
- Ensures user exists in database
- Validates account status (only ACTIVE accounts allowed)
- Invalidates tokens issued before password changes
- Fail-fast validation order for optimal security

Usage:
    from src.middleware.jwt_auth import verify_jwt_token

    try:
        claims = await verify_jwt_token(token, db_session)
        user_id = claims["user_id"]
    except (InvalidTokenError, ExpiredTokenError, UnauthorizedError) as e:
        # Handle authentication failure
        raise HTTPException(status_code=401, detail=str(e))
"""

import logging
import time
from datetime import UTC, datetime
from uuid import UUID

import jwt
from jwt.exceptions import ExpiredSignatureError
from jwt.exceptions import InvalidTokenError as JWTInvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.domain.models import User, UserStatus

# Configure logger for JWT authentication events
logger = logging.getLogger(__name__)

# Performance monitoring threshold (milliseconds)
SLOW_AUTH_THRESHOLD_MS = 100


def _log_structured(level: str, event_type: str, **context):
    """Log structured authentication event with consistent format.

    Args:
        level: Log level (INFO, WARNING, ERROR)
        event_type: Type of authentication event
        **context: Additional context fields (user_id, email, reason, duration_ms, etc.)
    """
    timestamp = datetime.now(UTC).isoformat()
    log_data = {
        "timestamp": timestamp,
        "event_type": event_type,
        **context
    }

    # Format as JSON-like string for easy parsing
    log_message = " | ".join([f"{k}={v}" for k, v in log_data.items()])

    if level == "INFO":
        logger.info(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    elif level == "ERROR":
        logger.error(log_message)


class InvalidTokenError(Exception):
    """Raised when JWT token has invalid signature or is malformed.

    This exception indicates that the token cannot be trusted due to:
    - Invalid signature (token was tampered with or signed with wrong secret)
    - Malformed token structure (not a valid JWT format)
    - Missing required claims

    HTTP Status: 401 Unauthorized
    """
    pass


class ExpiredTokenError(Exception):
    """Raised when JWT token has expired.

    This exception indicates that the token's expiration time (exp claim)
    has passed. The user must re-authenticate to obtain a new token.

    HTTP Status: 401 Unauthorized
    """
    pass


class UnauthorizedError(Exception):
    """Raised when authentication fails due to user state or token invalidation.

    This exception indicates that while the token may be structurally valid,
    the user cannot be authenticated due to:
    - User not found in database
    - Account is disabled or deleted
    - Token was issued before password change (invalidated)

    HTTP Status: 401 Unauthorized
    """
    pass


async def verify_jwt_token(
    token: str,
    db_session: AsyncSession,
) -> dict:
    """Verify JWT token and return claims with user validation.

    This function performs comprehensive JWT token verification following
    a fail-fast validation order for optimal security and performance:

    1. Decode and verify signature (PyJWT) - T042
    2. Check expiration - T043
    3. Extract and validate required claims - T044
    4. Validate user exists in database - T045
    5. Validate account status is ACTIVE - T046
    6. Validate token issued after password change - T047

    Args:
        token: JWT token string (without "Bearer " prefix)
        db_session: SQLAlchemy async database session

    Returns:
        dict: Token claims containing:
            - user_id (str): User's unique identifier
            - email (str): User's email address
            - iat (int): Token issued-at timestamp
            - exp (int): Token expiration timestamp
            - sub (str): Subject (same as user_id)

    Raises:
        InvalidTokenError: Token signature invalid, malformed, or missing required claims
        ExpiredSignatureError: Token has expired (from PyJWT)
        UnauthorizedError: User not found, account disabled/deleted, or token invalidated

    Security Notes:
        - Uses HS256 algorithm with BETTER_AUTH_SECRET
        - Validates signature before any database queries (fail fast)
        - Checks account status on every request (no caching)
        - Enforces password change token invalidation

    Example:
        >>> claims = await verify_jwt_token(token, db_session)
        >>> user_id = claims["user_id"]
        >>> email = claims["email"]
    """
    # T079: Start performance monitoring for total authentication time
    auth_start_time = time.perf_counter()

    # T042: JWT signature validation
    # T079: Measure JWT decode time
    # Decode token and verify signature using BETTER_AUTH_SECRET
    # This will raise ExpiredSignatureError if token is expired
    # This will raise JWTInvalidTokenError if signature is invalid
    decode_start_time = time.perf_counter()
    try:
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["exp", "iat"],  # Require expiration and issued-at claims
            }
        )
        decode_duration_ms = (time.perf_counter() - decode_start_time) * 1000
    except ExpiredSignatureError:
        # T043: Token expiration validation
        # T078: Structured logging for token expiration events
        try:
            # Decode token without verification to extract claims for logging
            unverified_payload = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False}
            )
            email = unverified_payload.get("email", "unknown")
            user_id = unverified_payload.get("user_id", "unknown")
            iat = unverified_payload.get("iat")
            exp = unverified_payload.get("exp")

            # Format timestamps for logging
            iat_str = datetime.fromtimestamp(iat, tz=UTC).isoformat() if iat else "unknown"
            exp_str = datetime.fromtimestamp(exp, tz=UTC).isoformat() if exp else "unknown"

            # T078: Structured logging for token expiration
            _log_structured(
                "WARNING",
                "token_expired",
                user_id=user_id,
                email=email,
                reason="token_expired",
                issued_at=iat_str,
                expired_at=exp_str
            )
        except Exception as log_error:
            # If logging fails, don't break authentication flow
            _log_structured(
                "WARNING",
                "token_expired",
                reason="token_expired",
                error=f"unable_to_extract_claims: {str(log_error)}"
            )

        # Re-raise ExpiredSignatureError directly (expected by tests)
        raise
    except JWTInvalidTokenError as e:
        # T078: Structured logging for security events (invalid signature, tampered tokens)
        _log_structured(
            "ERROR",
            "invalid_token_signature",
            reason="invalid_signature_or_malformed",
            error=str(e)
        )
        # Invalid signature, malformed token, or decoding error
        raise InvalidTokenError(f"Invalid token signature or format: {str(e)}")
    except Exception as e:
        # T078: Structured logging for unexpected token verification errors
        _log_structured(
            "ERROR",
            "token_verification_failed",
            reason="unexpected_error",
            error=str(e)
        )
        # Catch any other JWT-related errors
        raise InvalidTokenError(f"Token verification failed: {str(e)}")

    # T044: Claims extraction and validation
    # Extract required claims from payload
    user_id_str = payload.get("user_id")
    email = payload.get("email")
    iat = payload.get("iat")

    # Validate all required claims are present
    if not user_id_str:
        # T078: Structured logging for missing claims
        _log_structured(
            "ERROR",
            "invalid_token_claims",
            reason="missing_user_id_claim",
            email=email or "unknown"
        )
        raise InvalidTokenError("Missing required claim: user_id")
    if not email:
        # T078: Structured logging for missing claims
        _log_structured(
            "ERROR",
            "invalid_token_claims",
            reason="missing_email_claim",
            user_id=user_id_str
        )
        raise InvalidTokenError("Missing required claim: email")
    if not iat:
        # T078: Structured logging for missing claims
        _log_structured(
            "ERROR",
            "invalid_token_claims",
            reason="missing_iat_claim",
            user_id=user_id_str,
            email=email
        )
        raise InvalidTokenError("Missing required claim: iat")

    # Convert user_id string to UUID for database query
    try:
        user_id = UUID(user_id_str)
    except (ValueError, AttributeError, TypeError) as e:
        # T078: Structured logging for invalid user_id format
        _log_structured(
            "ERROR",
            "invalid_token_claims",
            reason="invalid_user_id_format",
            user_id=user_id_str,
            email=email,
            error=str(e),
            error_type=type(e).__name__
        )
        raise InvalidTokenError(f"Invalid user_id format: {str(e)} ({type(e).__name__})")

    # T045: User existence validation
    # T079: Measure database lookup time
    # Query database to verify user exists
    db_start_time = time.perf_counter()
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    db_duration_ms = (time.perf_counter() - db_start_time) * 1000

    if user is None:
        # T078: Structured logging for user not found
        _log_structured(
            "WARNING",
            "authentication_failed",
            reason="user_not_found",
            user_id=user_id_str,
            email=email
        )
        raise UnauthorizedError(f"User not found: {user_id_str}")

    # T046: Account status validation
    # Verify account is ACTIVE (not DISABLED or DELETED)
    if user.status != UserStatus.ACTIVE:
        # T078: Structured logging for account status issues
        _log_structured(
            "WARNING",
            "authentication_failed",
            reason=f"account_status_{user.status.value.lower()}",
            user_id=user_id_str,
            email=email,
            account_status=user.status.value
        )
        raise UnauthorizedError(f"Account is {user.status.value}: authentication denied")

    # T047: Password change timestamp validation
    # If user has changed password, verify token was issued AFTER the change
    if user.password_changed_at is not None:
        # Convert iat (Unix timestamp) to datetime for comparison
        token_issued_at = datetime.fromtimestamp(iat, tz=UTC)

        # Ensure password_changed_at is timezone-aware for comparison
        password_changed_at = user.password_changed_at
        if password_changed_at.tzinfo is None:
            # If stored as naive datetime, assume UTC
            password_changed_at = password_changed_at.replace(tzinfo=UTC)

        # Token must be issued AFTER password change
        if token_issued_at < password_changed_at:
            # T078: Structured logging for invalidated tokens (password change)
            _log_structured(
                "WARNING",
                "authentication_failed",
                reason="token_invalidated_password_changed",
                user_id=user_id_str,
                email=email,
                token_issued_at=token_issued_at.isoformat(),
                password_changed_at=password_changed_at.isoformat()
            )
            raise UnauthorizedError(
                "Token invalidated: issued before password change. Please re-authenticate."
            )

    # T079: Calculate total authentication time
    total_duration_ms = (time.perf_counter() - auth_start_time) * 1000

    # T078: Structured logging for successful authentication
    _log_structured(
        "INFO",
        "authentication_success",
        user_id=user_id_str,
        email=email,
        decode_duration_ms=f"{decode_duration_ms:.2f}",
        db_lookup_duration_ms=f"{db_duration_ms:.2f}",
        total_duration_ms=f"{total_duration_ms:.2f}"
    )

    # T079: Performance monitoring - alert on slow authentication
    if total_duration_ms > SLOW_AUTH_THRESHOLD_MS:
        _log_structured(
            "WARNING",
            "slow_authentication",
            user_id=user_id_str,
            email=email,
            total_duration_ms=f"{total_duration_ms:.2f}",
            threshold_ms=SLOW_AUTH_THRESHOLD_MS,
            decode_duration_ms=f"{decode_duration_ms:.2f}",
            db_lookup_duration_ms=f"{db_duration_ms:.2f}"
        )

    # All validations passed - return claims
    return {
        "user_id": user_id_str,
        "email": email,
        "iat": iat,
        "exp": payload.get("exp"),
        "sub": payload.get("sub"),
    }
