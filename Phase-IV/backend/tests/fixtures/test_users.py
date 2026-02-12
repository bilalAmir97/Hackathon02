"""Test user fixtures for testing.

Provides reusable user instances for test scenarios with predictable UUIDs.
"""

from uuid import UUID

import pytest

from src.auth.token import create_access_token
from src.domain.models import User


@pytest.fixture
def test_user() -> User:
    """Create a test user with a fixed UUID for predictable testing.

    Returns:
        User instance with UUID 550e8400-e29b-41d4-a716-446655440000
        and email test@example.com
    """
    return User(
        id=UUID("550e8400-e29b-41d4-a716-446655440000"),
        email="test@example.com",
    )


@pytest.fixture
def test_user_2() -> User:
    """Create a second test user for multi-user testing scenarios.

    Returns:
        User instance with different UUID for testing user isolation
    """
    return User(
        id=UUID("660e8400-e29b-41d4-a716-446655440001"),
        email="test2@example.com",
    )


@pytest.fixture
def test_token(test_user: User) -> str:
    """Generate a valid JWT token for the test user.

    This fixture creates a JWT token that can be used in Authorization headers
    for testing protected endpoints.

    Args:
        test_user: The test user fixture

    Returns:
        str: Valid JWT token for the test user
    """
    return create_access_token(
        user_id=str(test_user.id),
        email=test_user.email,
    )


@pytest.fixture
def test_token_2(test_user_2: User) -> str:
    """Generate a valid JWT token for the second test user.

    This fixture creates a JWT token for test_user_2, useful for testing
    user isolation scenarios.

    Args:
        test_user_2: The second test user fixture

    Returns:
        str: Valid JWT token for the second test user
    """
    return create_access_token(
        user_id=str(test_user_2.id),
        email=test_user_2.email,
    )
