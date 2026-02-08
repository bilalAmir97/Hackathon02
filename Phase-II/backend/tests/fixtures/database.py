"""Database fixtures for testing.

Provides async test database sessions with automatic setup and teardown.
Uses SQLite in-memory database for fast, isolated tests.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from src.domain.models import Task, User  # noqa: F401 - Import to register models

# Create test database engine (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False},  # Required for SQLite
)

# Create async session factory for tests
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture
async def test_db_session() -> AsyncGenerator[AsyncSession]:
    """Provide an async database session for testing.

    Creates all tables before the test and drops them after.
    Each test gets a fresh database with no data.

    Yields:
        AsyncSession: Database session for the test
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Provide session to test
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture
async def test_db_session_with_user(
    test_db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncSession, User]]:
    """Provide a database session with a pre-created test user.

    Useful for tests that need an existing user in the database.

    Yields:
        tuple: (AsyncSession, User) - session and created user
    """
    from uuid import UUID
    from src.auth.password import hash_password

    # Create test user with hashed password
    user = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        status="active",
    )
    test_db_session.add(user)
    await test_db_session.commit()
    await test_db_session.refresh(user)

    yield test_db_session, user


@pytest_asyncio.fixture
async def test_db_session_with_two_users(
    test_db_session: AsyncSession,
) -> AsyncGenerator[tuple[AsyncSession, User, User]]:
    """Provide a database session with two pre-created test users.

    Useful for tests that need to verify user isolation.

    Yields:
        tuple: (AsyncSession, User, User) - session and two created users
    """
    from uuid import UUID
    from src.auth.password import hash_password

    # Create first test user
    user1 = User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        status="active",
    )
    test_db_session.add(user1)

    # Create second test user
    user2 = User(
        id=UUID("660e8400-e29b-41d4-a716-446655440001"),
        email="test2@example.com",
        password_hash=hash_password("testpassword456"),
        status="active",
    )
    test_db_session.add(user2)

    await test_db_session.commit()
    await test_db_session.refresh(user1)
    await test_db_session.refresh(user2)

    yield test_db_session, user1, user2
