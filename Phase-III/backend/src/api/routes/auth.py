"""Authentication API endpoints.

Provides user registration and login endpoints that issue JWT tokens
for authenticated access to protected resources.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from src.use_cases.auth_operations import (
    AuthenticationError,
    DuplicateEmailError,
    authenticate_user,
    create_user,
    generate_jwt_token,
)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Creates a new user account with email and password credentials. Returns a JWT token upon successful registration.",
    response_description="User account created with JWT access token",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "status": "active",
                            "created_at": "2026-01-12T10:00:00Z",
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid request (validation error)",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Invalid email format",
                        "detail": "Email must be a valid email address",
                    }
                }
            },
        },
        409: {
            "description": "Email already exists",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Email already exists",
                        "detail": "An account with this email already exists",
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "password"],
                                "msg": "ensure this value has at least 8 characters",
                                "type": "value_error.any_str.min_length",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def register(
    user_data: RegisterRequest,
    session: AsyncSession = Depends(get_session),
):
    """Register a new user account.

    Creates a new user with the provided email and password. The password
    is hashed before storage. Returns a JWT access token valid for 30 minutes.

    Args:
        user_data: Registration data (email, password)
        session: Database session (injected dependency)

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException 409: If email already exists
        HTTPException 400: If validation fails
        HTTPException 422: If request data is invalid
    """
    try:
        # Create user with hashed password
        user = await create_user(
            email=user_data.email,
            password=user_data.password,
            db_session=session,
        )

        # Generate JWT token
        token = generate_jwt_token(user)

        # Build response
        user_response = UserResponse.model_validate(user)
        auth_response = AuthResponse(token=token, user=user_response)

        return auth_response

    except DuplicateEmailError:
        # Handle duplicate email error from auth_operations
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "Email already exists",
                "detail": "An account with this email already exists",
            },
        )
    except ValueError as e:
        # Handle validation errors from business logic
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Validation error",
                "detail": str(e),
            },
        )
    except Exception:
        # Handle unexpected errors
        await session.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during registration",
            },
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with existing credentials",
    description="Authenticates a user with email and password. Returns a JWT token upon successful authentication.",
    response_description="Login successful with JWT access token",
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": {
                        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "user": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "user@example.com",
                            "status": "active",
                            "created_at": "2026-01-12T10:00:00Z",
                        },
                    }
                }
            },
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Authentication failed",
                        "detail": "Invalid email or password",
                    }
                }
            },
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "email"],
                                "msg": "value is not a valid email address",
                                "type": "value_error.email",
                            }
                        ]
                    }
                }
            },
        },
    },
)
async def login(
    credentials: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Login with email and password.

    Authenticates a user by verifying their email and password. Returns
    a JWT access token valid for 30 minutes upon successful authentication.

    Args:
        credentials: Login credentials (email, password)
        session: Database session (injected dependency)

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException 401: If credentials are invalid or account is disabled
        HTTPException 422: If request data is invalid
    """
    try:
        # Authenticate user and verify credentials
        user = await authenticate_user(
            email=credentials.email,
            password=credentials.password,
            db_session=session,
        )

        # Generate JWT token
        token = generate_jwt_token(user)

        # Build response
        user_response = UserResponse.model_validate(user)
        auth_response = AuthResponse(token=token, user=user_response)

        return auth_response

    except AuthenticationError as e:
        # Handle authentication errors (invalid credentials, inactive account)
        error_message = str(e)

        # Determine if it's an account status issue or credential issue
        if "not active" in error_message.lower():
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Account disabled",
                    "detail": "Your account has been disabled",
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "error": "Authentication failed",
                    "detail": "Invalid email or password",
                },
            )
    except Exception:
        # Handle unexpected errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred during login",
            },
        )
