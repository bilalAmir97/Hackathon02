"""
Test configuration and fixtures for backend tests.
"""
import os
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient
from jose import jwt
from sqlmodel import SQLModel, create_engine, Session

# Set test environment BEFORE any imports
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-only"

from src.app.db import get_engine, get_session
from src.app.main import app
from src.app.middleware.auth import get_auth_secret

BETTER_AUTH_SECRET = get_auth_secret()

# Import fixtures from subdirectories
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.test_users",
    "tests.fixtures.test_data",
    "tests.utils.api_client",
    "tests.utils.auth_helpers",
    "tests.utils.db_client",
]


# Create in-memory SQLite engine for testing
TEST_DATABASE_URL = "sqlite:///test.db"


@pytest.fixture(scope="session")
def engine():
    """Create test engine with SQLite."""
    test_engine = create_engine(TEST_DATABASE_URL, echo=False)
    SQLModel.metadata.create_all(test_engine)
    yield test_engine
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def session(engine):
    """Create a fresh database session for each test."""
    with Session(engine) as session:
        yield session


@pytest.fixture(scope="function")
def client(test_engine, db_session):
    """Create test client with overridden database session."""
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_id():
    """Generate a test user UUID."""
    return uuid4()


@pytest.fixture
def other_user_id():
    """Generate a different user UUID for isolation tests."""
    return uuid4()


@pytest.fixture
def auth_headers(test_user_id):
    """Generate valid JWT auth headers for test user."""
    token = jwt.encode(
        {"sub": str(test_user_id), "exp": datetime.now(timezone.utc).timestamp() + 3600},
        BETTER_AUTH_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def invalid_auth_headers():
    """Generate invalid JWT auth headers."""
    token = jwt.encode(
        {"sub": "invalid-uuid", "exp": datetime.now(timezone.utc).timestamp() + 3600},
        BETTER_AUTH_SECRET,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_todo(test_user_id):
    """Create a sample todo for testing."""
    from src.app.models.todo import Todo
    return Todo(
        id=uuid4(),
        user_id=test_user_id,
        title="Test Todo",
        description="Test Description",
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        version=1,
    )
