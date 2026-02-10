"""Authentication business logic operations.

This module implements the core authentication use cases including user
registration, login, and JWT token generation. These functions are used
by the API endpoints to handle authentication flows.

Business Logic:
- User registration with password hashing
- User authentication with credential verification
- JWT token generation for authenticated users
- Database operations for user management

Security Features:
- Bcrypt password hashing with automatic salt
- Timing-safe password verification
- JWT token generation with 30-minute expiration
- Email uniqueness validation
- Account status validation

Example:
    >>> from src.use_cases.auth_operations import create_user, authenticate_user
    >>> from src.database import get_session
    >>>
    >>> async with get_session() as session:
    ...     # Register new user
    ...     user = await create_user("user@example.com", "SecurePass123!", session)
    ...
    ...     # Authenticate user
    ...     auth_user = await authenticate_user("user@example.com", "SecurePass123!", session)
    ...
    ...     # Generate token
    ...     token = generate_jwt_token(auth_user)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.password import hash_password, verify_password
from src.auth.token import create_access_token
from src.domain.models import User, UserStatus


class AuthenticationError(Exception):
    """Raised when authentication fails due to invalid credentials."""

    pass


class DuplicateEmailError(Exception):
    """Raised when attempting to register with an email that already exists."""

    pass


async def create_user(
    email: str,
    password: str,
    db_session: AsyncSession,
) -> User:
    """Create a new user account with hashed password.

    This function handles user registration by:
    1. Hashing the password using bcrypt
    2. Creating a User record in the database
    3. Setting account status to 'active'
    4. Setting timestamps (created_at, updated_at)

    Security Notes:
    - Password is hashed with bcrypt (cost factor: 12)
    - Email uniqueness is enforced at database level
    - Password is never stored in plaintext
    - Account status defaults to 'active'

    Args:
        email: User email address (must be unique)
        password: Plaintext password (will be hashed)
        db_session: Async database session for persistence

    Returns:
        User: The created user object with all fields populated

    Raises:
        DuplicateEmailError: If email already exists in database
        ValueError: If email or password is invalid

    Example:
        >>> from src.database import get_session
        >>> from src.use_cases.auth_operations import create_user
        >>>
        >>> async with get_session() as session:
        ...     user = await create_user(
        ...         email="newuser@example.com",
        ...         password="SecurePass123!",
        ...         db_session=session
        ...     )
        ...     print(f"Created user: {user.id}")
    """
    # Validate inputs
    if not email or not email.strip():
        raise ValueError("Email cannot be empty")

    if not password:
        raise ValueError("Password cannot be empty")

    # Hash password using bcrypt
    password_hash = hash_password(password)

    # Create user object
    user = User(
        email=email.strip().lower(),  # Normalize email to lowercase
        password_hash=password_hash,
        status=UserStatus.ACTIVE,
        password_changed_at=None,  # No password change yet
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Add to database
    db_session.add(user)

    try:
        # Commit transaction
        await db_session.commit()

        # Refresh to get generated ID and timestamps
        await db_session.refresh(user)

        return user

    except IntegrityError as e:
        # Rollback transaction
        await db_session.rollback()

        # Check if error is due to duplicate email
        if "unique constraint" in str(e).lower() or "duplicate" in str(e).lower():
            raise DuplicateEmailError(f"Email {email} already exists")

        # Re-raise other integrity errors
        raise


async def authenticate_user(
    email: str,
    password: str,
    db_session: AsyncSession,
) -> User:
    """Authenticate a user with email and password credentials.

    This function handles user login by:
    1. Looking up user by email
    2. Verifying password using timing-safe comparison
    3. Checking account status (must be 'active')
    4. Returning authenticated user object

    Security Notes:
    - Timing-safe password comparison (prevents timing attacks)
    - Generic error message for invalid credentials (prevents user enumeration)
    - Account status validation (disabled/deleted accounts cannot login)
    - Email lookup is case-insensitive

    Args:
        email: User email address
        password: Plaintext password to verify
        db_session: Async database session for lookup

    Returns:
        User: The authenticated user object if credentials are valid

    Raises:
        AuthenticationError: If credentials are invalid or account is not active

    Example:
        >>> from src.database import get_session
        >>> from src.use_cases.auth_operations import authenticate_user
        >>>
        >>> async with get_session() as session:
        ...     try:
        ...         user = await authenticate_user(
        ...             email="user@example.com",
        ...             password="SecurePass123!",
        ...             db_session=session
        ...         )
        ...         print(f"Authenticated: {user.email}")
        ...     except AuthenticationError:
        ...         print("Invalid credentials")
    """
    # Validate inputs
    if not email or not password:
        raise AuthenticationError("Invalid credentials")

    # Normalize email to lowercase for case-insensitive lookup
    email_normalized = email.strip().lower()

    # Look up user by email
    result = await db_session.execute(
        select(User).where(User.email == email_normalized)
    )
    user = result.scalar_one_or_none()

    # Check if user exists
    if user is None:
        # Generic error message to prevent user enumeration
        raise AuthenticationError("Invalid credentials")

    # Verify password using timing-safe comparison
    if not verify_password(password, user.password_hash):
        # Generic error message (don't reveal that user exists)
        raise AuthenticationError("Invalid credentials")

    # Check account status
    if user.status != UserStatus.ACTIVE:
        raise AuthenticationError("Account is not active")

    # Authentication successful
    return user


def generate_jwt_token(user: User) -> str:
    """Generate a JWT access token for an authenticated user.

    This function creates a signed JWT token containing user identification
    claims. The token is valid for 30 minutes and can be used for stateless
    authentication on protected API endpoints.

    Token Claims:
    - sub: User ID (subject)
    - user_id: User ID (explicit)
    - email: User email address
    - iat: Issued at timestamp
    - exp: Expiration timestamp (iat + 30 minutes)

    Security Notes:
    - Token signed with BETTER_AUTH_SECRET (HMAC-SHA256)
    - Default expiration: 30 minutes
    - Stateless (no server-side storage)
    - Token includes user_id for authorization checks

    Args:
        user: Authenticated user object

    Returns:
        str: Signed JWT token string

    Example:
        >>> from src.use_cases.auth_operations import generate_jwt_token
        >>> from src.domain.models import User
        >>>
        >>> user = User(
        ...     id="550e8400-e29b-41d4-a716-446655440000",
        ...     email="user@example.com",
        ...     status="active"
        ... )
        >>> token = generate_jwt_token(user)
        >>> print(f"Token: {token[:20]}...")
    """
    # Convert UUID to string if needed
    user_id_str = str(user.id) if isinstance(user.id, UUID) else user.id

    # Generate JWT token with user claims
    token = create_access_token(
        user_id=user_id_str,
        email=user.email,
    )

    return token
