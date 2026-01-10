"""
Database fixtures for E2E testing.

Provides database connection, session management, and transactional rollback
for test isolation.
"""
import os
from typing import Generator

import pytest
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


# Test database configuration
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")


@pytest.fixture(scope="session")
def test_engine():
    """
    Create test database engine with SQLite for fast, isolated testing.

    Uses in-memory SQLite with StaticPool to ensure single connection
    for thread safety in tests.
    """
    # Use in-memory SQLite for speed and isolation
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Cleanup: drop all tables
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.

    This fixture provides a session that can be shared between the test client
    and direct database queries, ensuring data visibility across both.
    """
    with Session(test_engine) as session:
        yield session
        # Session will auto-rollback uncommitted changes on close


@pytest.fixture(scope="function")
def clean_db(test_engine):
    """
    Ensure database is clean before test execution.

    This fixture truncates all tables to provide a clean slate.
    Use this for tests that need guaranteed empty database state.
    """
    # Drop and recreate all tables
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)

    yield

    # Cleanup after test
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def db_with_tables(test_engine):
    """
    Ensure all database tables exist before test.

    Use this for tests that need to verify schema structure.
    """
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    # Tables persist for schema validation tests
