"""
Test todo factory for generating test todo data.

Provides realistic, varied test todo data using Faker library.
"""
from datetime import datetime, timezone
from typing import Dict, Optional
from uuid import UUID, uuid4

from faker import Faker

fake = Faker()


class TodoFactory:
    """Factory for creating test todo data."""

    @staticmethod
    def create_todo_data(
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: bool = False,
        todo_id: Optional[UUID] = None,
    ) -> Dict:
        """
        Create test todo data dictionary.

        Args:
            user_id: Owner user UUID
            title: Todo title (generated if not provided)
            description: Todo description (generated if not provided)
            completed: Completion status
            todo_id: Todo UUID (generated if not provided)

        Returns:
            Dictionary with todo data
        """
        return {
            "id": todo_id or uuid4(),
            "user_id": user_id,
            "title": title or fake.sentence(nb_words=5),
            "description": description or fake.paragraph(nb_sentences=2),
            "completed": completed,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "version": 1,
        }

    @staticmethod
    def create_todo_payload(
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict:
        """
        Create todo creation request payload.

        Args:
            title: Todo title (generated if not provided)
            description: Todo description (generated if not provided)

        Returns:
            Dictionary with todo creation payload
        """
        return {
            "title": title or fake.sentence(nb_words=5),
            "description": description or fake.paragraph(nb_sentences=2),
        }

    @staticmethod
    def create_update_payload(
        title: Optional[str] = None,
        description: Optional[str] = None,
        version: int = 1,
    ) -> Dict:
        """
        Create todo update request payload.

        Args:
            title: Updated title (generated if not provided)
            description: Updated description (generated if not provided)
            version: Current version for optimistic locking

        Returns:
            Dictionary with todo update payload
        """
        payload = {"version": version}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        return payload

    @staticmethod
    def create_toggle_payload(version: int = 1) -> Dict:
        """
        Create todo toggle completion payload.

        Args:
            version: Current version for optimistic locking

        Returns:
            Dictionary with toggle payload
        """
        return {"version": version}

    @staticmethod
    def create_multiple_todos(user_id: UUID, count: int = 5) -> list[Dict]:
        """
        Create multiple test todos for a user.

        Args:
            user_id: Owner user UUID
            count: Number of todos to create

        Returns:
            List of todo data dictionaries
        """
        return [TodoFactory.create_todo_data(user_id) for _ in range(count)]


# Convenience fixtures for pytest
import pytest


@pytest.fixture
def todo_payload():
    """Generate todo creation payload."""
    return TodoFactory.create_todo_payload()


@pytest.fixture
def sample_todo(test_user_id):
    """Generate sample todo data."""
    return TodoFactory.create_todo_data(test_user_id)


@pytest.fixture
def multiple_todos(test_user_id):
    """Generate multiple todos for test user."""
    return TodoFactory.create_multiple_todos(test_user_id, count=5)
