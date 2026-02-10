"""JWT token generation and verification using PyJWT.

This module provides functions for creating and verifying JSON Web Tokens (JWT)
for stateless authentication. Tokens are signed with HMAC-SHA256 using a shared
secret and include user identification claims.

Token Structure:
- Header: {"alg": "HS256", "typ": "JWT"}
- Payload: {sub, user_id, email, iat, exp}
- Signature: HMACSHA256(header.payload, secret)

Security Features:
- HMAC-SHA256 signature verification
- Token expiration validation (30 minutes)
- Shared secret from environment configuration
- Stateless authentication (no server-side storage)

Example:
    >>> from src.auth.token import create_access_token, verify_token
    >>>
    >>> # Create token
    >>> token = create_access_token(
    ...     user_id="550e8400-e29b-41d4-a716-446655440000",
    ...     email="user@example.com"
    ... )
    >>>
    >>> # Verify token
    >>> is_valid = verify_token(token)
    >>> assert is_valid is True
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from src.config import settings


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token with user identification claims.

    Generates a signed JWT token containing user information and expiration.
    The token is signed with BETTER_AUTH_SECRET using HMAC-SHA256 algorithm.

    Token Claims:
    - sub: Subject (user_id) - standard JWT claim
    - user_id: User identifier (redundant with sub for clarity)
    - email: User email address
    - iat: Issued at timestamp (Unix epoch)
    - exp: Expiration timestamp (Unix epoch, default: iat + 30 minutes)

    Security Notes:
    - Default expiration: 30 minutes (1800 seconds)
    - Algorithm: HS256 (HMAC-SHA256)
    - Secret: BETTER_AUTH_SECRET from environment
    - Tokens are stateless (no server-side storage)

    Args:
        user_id: Unique user identifier (UUID string)
        email: User email address
        expires_delta: Optional custom expiration duration (default: 30 minutes)

    Returns:
        str: Signed JWT token string (format: header.payload.signature)

    Example:
        >>> # Create token with default 30-minute expiration
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com"
        ... )
        >>>
        >>> # Create token with custom expiration
        >>> from datetime import timedelta
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com",
        ...     expires_delta=timedelta(hours=1)
        ... )
    """
    # Calculate expiration time
    if expires_delta is None:
        expires_delta = timedelta(minutes=30)  # Default: 30 minutes

    # Get current time in UTC
    now = datetime.now(UTC)
    expire = now + expires_delta

    # Build JWT payload with required claims
    payload = {
        "sub": user_id,  # Subject (standard JWT claim)
        "user_id": user_id,  # Explicit user_id for clarity
        "email": email,  # User email
        "iat": int(now.timestamp()),  # Issued at (Unix timestamp)
        "exp": int(expire.timestamp()),  # Expiration (Unix timestamp)
    }

    # Sign token with BETTER_AUTH_SECRET using HS256 algorithm
    token = jwt.encode(
        payload,
        settings.better_auth_secret,
        algorithm="HS256",
    )

    return token


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token, raising exceptions for invalid tokens.

    This function decodes the token payload and verifies both signature and
    expiration. It raises specific exceptions for different failure modes,
    allowing callers to handle different error cases appropriately.

    Use this function when you need to extract token claims and want to
    handle specific error cases (expired vs invalid signature vs malformed).

    Args:
        token: JWT token string to decode

    Returns:
        dict: Decoded token payload with all claims

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidSignatureError: If token signature is invalid
        jwt.DecodeError: If token is malformed or cannot be decoded
        jwt.InvalidTokenError: If token format is invalid

    Example:
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com"
        ... )
        >>> payload = decode_token(token)
        >>> assert payload["user_id"] == "550e8400-e29b-41d4-a716-446655440000"
        >>> assert payload["email"] == "user@example.com"
        >>> assert "iat" in payload
        >>> assert "exp" in payload
    """
    # Decode with full verification (signature and expiration)
    payload = jwt.decode(
        token,
        settings.better_auth_secret,
        algorithms=["HS256"],
    )

    return payload


def verify_token(token: str) -> bool:
    """Verify a JWT token signature and expiration.

    This function performs full token validation including:
    - Signature verification using BETTER_AUTH_SECRET
    - Expiration timestamp validation
    - Token format validation

    Use this function for production authentication to ensure tokens
    are valid and have not been tampered with or expired.

    Security Notes:
    - Verifies HMAC-SHA256 signature
    - Checks token expiration (exp claim)
    - Returns False for any validation failure
    - Timing-safe comparison (built into PyJWT)

    Args:
        token: JWT token string to verify

    Returns:
        bool: True if token is valid and not expired, False otherwise

    Example:
        >>> # Valid token
        >>> token = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com"
        ... )
        >>> assert verify_token(token) is True
        >>>
        >>> # Tampered token
        >>> tampered = token[:-1] + "X"
        >>> assert verify_token(tampered) is False
        >>>
        >>> # Expired token
        >>> from datetime import timedelta
        >>> expired = create_access_token(
        ...     user_id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com",
        ...     expires_delta=timedelta(seconds=-1)
        ... )
        >>> assert verify_token(expired) is False
    """
    try:
        # Verify token signature and expiration
        jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )
        return True

    except jwt.ExpiredSignatureError:
        # Token has expired
        return False

    except jwt.InvalidTokenError:
        # Invalid signature, malformed token, or other error
        return False

    except Exception:
        # Catch any other unexpected errors
        return False
