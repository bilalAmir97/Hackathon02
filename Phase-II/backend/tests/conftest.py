"""Pytest configuration and shared fixtures.

Makes fixtures from fixtures/ directory available to all tests.
Configures pytest-asyncio for async test support.
"""

import pytest_asyncio
from sqlmodel import SQLModel

from src.database import get_session
from src.main import app

# Import fixtures to make them available to all tests
from tests.fixtures.database import (  # noqa: F401
    TestAsyncSessionLocal,
    test_db_session,
    test_db_session_with_user,
    test_db_session_with_two_users,
    test_engine,
)
from tests.fixtures.test_users import (  # noqa: F401
    test_token,
    test_token_2,
    test_user,
    test_user_2,
)

# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_test_database():
    """Set up test database before each test and clean up after.

    This fixture:
    1. Creates all tables in the test database
    2. Overrides the FastAPI database dependency
    3. Cleans up after the test
    """
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    # Override the database dependency
    async def override_get_session():
        async with TestAsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_session] = override_get_session

    yield

    # Clean up: drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    # Clear dependency overrides
    app.dependency_overrides.clear()
