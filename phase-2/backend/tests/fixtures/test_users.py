"""
Test user factory for generating test user data.

Provides realistic, varied test user data using Faker library.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from faker import Faker

fake = Faker()


class UserFactory:
    """Factory for creating test user data."""

    @staticmethod
    def create_user_data(
        email: Optional[str] = None,
        password: Optional[str] = None,
        user_id: Optional[UUID] = None,
    ) -> Dict:
        """
        Create test user data dictionary.

        Args:
            email: User email (generated if not provided)
            password: User password (generated if not provided)
            user_id: User UUID (generated if not provided)

        Returns:
            Dictionary with user data
        """
        return {
            "id": user_id or uuid4(),
            "email": email or fake.email(),
            "password": password or fake.password(length=12, special_chars=True),
            "created_at": datetime.now(timezone.utc),
        }

    @staticmethod
    def create_signup_payload(
        email: Optional[str] = None,
        password: Optional[str] = None,
    ) -> Dict:
        """
        Create signup request payload.

        Args:
            email: User email (generated if not provided)
            password: User password (generated if not provided)

        Returns:
            Dictionary with signup payload
        """
        return {
            "email": email or fake.email(),
            "password": password or fake.password(length=12, special_chars=True),
        }

    @staticmethod
    def create_signin_payload(
        email: str,
        password: str,
    ) -> Dict:
        """
        Create signin request payload.

        Args:
            email: User email
            password: User password

        Returns:
            Dictionary with signin payload
        """
        return {
            "email": email,
            "password": password,
        }

    @staticmethod
    def create_multiple_users(count: int = 3) -> list[Dict]:
        """
        Create multiple test users.

        Args:
            count: Number of users to create

        Returns:
            List of user data dictionaries
        """
        return [UserFactory.create_user_data() for _ in range(count)]


# Convenience fixtures for pytest
import pytest


@pytest.fixture
def test_user_data():
    """Generate test user data."""
    return UserFactory.create_user_data()


@pytest.fixture
def test_user_id():
    """Generate test user UUID."""
    return uuid4()


@pytest.fixture
def other_user_id():
    """Generate different user UUID for isolation tests."""
    return uuid4()


@pytest.fixture
def signup_payload():
    """Generate signup request payload."""
    return UserFactory.create_signup_payload()


@pytest.fixture
def multiple_users():
    """Generate multiple test users."""
    return UserFactory.create_multiple_users(count=3)
