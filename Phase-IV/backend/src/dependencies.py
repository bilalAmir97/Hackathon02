"""FastAPI dependencies for authentication and authorization.

This module provides reusable dependency functions for FastAPI endpoints,
including JWT token extraction, verification, and user authentication.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.middleware.jwt_auth import (
    ExpiredTokenError,
    InvalidTokenError,
    UnauthorizedError,
    verify_jwt_token,
)

# T080: Define security scheme for OpenAPI documentation
# This enables the "Authorize" button in Swagger UI and marks endpoints as protected
security = HTTPBearer(
    scheme_name="JWT Bearer Token",
    description="JWT token obtained from /api/auth/login or /api/auth/register",
    auto_error=False,  # We handle errors manually for better error messages
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> dict:
    """Extract and verify JWT token from Authorization header.

    This dependency extracts the JWT token from the Authorization header using
    FastAPI's HTTPBearer security scheme, verifies its signature and validity,
    and returns the authenticated user's claims. It performs comprehensive
    validation including:
    - Token signature verification
    - Expiration checking
    - User existence validation
    - Account status validation
    - Password change timestamp validation

    Args:
        credentials: HTTPAuthorizationCredentials from HTTPBearer (contains token)
        db: Database session (injected dependency)

    Returns:
        dict: User claims containing:
            - user_id (str): User's unique identifier
            - email (str): User's email address
            - iat (int): Token issued-at timestamp
            - exp (int): Token expiration timestamp
            - sub (str): Subject (same as user_id)

    Raises:
        HTTPException 401: Invalid, expired, or unauthorized token

    Usage:
        @router.get("/protected")
        async def protected_endpoint(
            current_user: dict = Depends(get_current_user)
        ):
            user_id = current_user["user_id"]
            return {"message": f"Hello, user {user_id}"}
    """
    # T072: Check if Authorization header is present
    # HTTPBearer returns None if header is missing or invalid format
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from credentials object
    token = credentials.credentials

    # Verify JWT token using middleware
    try:
        claims = await verify_jwt_token(token, db)
        return claims

    except ExpiredSignatureError:
        # Token has expired - user must re-authenticate
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please re-authenticate.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except ExpiredTokenError as e:
        # Token has expired (custom exception from middleware)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError as e:
        # Invalid token signature or malformed token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UnauthorizedError as e:
        # User not found, account disabled, or token invalidated
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Catch any unexpected errors during token verification
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    current_user: dict = Depends(get_current_user)
) -> UUID:
    """Extract user_id from authenticated user claims.

    This is a convenience dependency that extracts just the user_id
    from the JWT claims, converting it to UUID type.

    Args:
        current_user: User claims from get_current_user dependency

    Returns:
        UUID: User's unique identifier

    Usage:
        @router.get("/api/{user_id}/resource")
        async def get_resource(
            user_id: UUID = Path(...),
            current_user_id: UUID = Depends(get_current_user_id)
        ):
            # Validate user_id matches current_user_id
            if user_id != current_user_id:
                raise HTTPException(403, "Forbidden")
            return {"user_id": user_id}
    """
    return UUID(current_user["user_id"])
