"""
Database client wrapper for testing.

Provides utilities for direct database access during tests for
validation and setup purposes.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from src.app.models.todo import Todo


class DBClient:
    """Wrapper for database operations in tests."""

    def __init__(self, session: Session):
        """
        Initialize database client.

        Args:
            session: SQLModel session
        """
        self.session = session

    def get_todo_by_id(self, todo_id: UUID) -> Optional[Todo]:
        """
        Get todo by ID directly from database.

        Args:
            todo_id: Todo UUID

        Returns:
            Todo model or None if not found
        """
        return self.session.get(Todo, todo_id)

    def get_todos_by_user(self, user_id: UUID) -> List[Todo]:
        """
        Get all todos for a user directly from database.

        Args:
            user_id: User UUID

        Returns:
            List of Todo models
        """
        statement = select(Todo).where(Todo.user_id == user_id)
        return list(self.session.exec(statement).all())

    def count_todos_by_user(self, user_id: UUID) -> int:
        """
        Count todos for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of todos
        """
        return len(self.get_todos_by_user(user_id))

    def create_todo_directly(self, todo_data: Dict[str, Any]) -> Todo:
        """
        Create todo directly in database (bypassing API).

        Args:
            todo_data: Todo data dictionary

        Returns:
            Created Todo model
        """
        todo = Todo(**todo_data)
        self.session.add(todo)
        self.session.commit()
        self.session.refresh(todo)
        return todo

    def delete_todo_directly(self, todo_id: UUID) -> bool:
        """
        Delete todo directly from database.

        Args:
            todo_id: Todo UUID

        Returns:
            True if deleted, False if not found
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            self.session.delete(todo)
            self.session.commit()
            return True
        return False

    def update_todo_directly(self, todo_id: UUID, updates: Dict[str, Any]) -> Optional[Todo]:
        """
        Update todo directly in database.

        Args:
            todo_id: Todo UUID
            updates: Fields to update

        Returns:
            Updated Todo model or None if not found
        """
        todo = self.get_todo_by_id(todo_id)
        if todo:
            for key, value in updates.items():
                setattr(todo, key, value)
            self.session.add(todo)
            self.session.commit()
            self.session.refresh(todo)
            return todo
        return None

    def clear_all_todos(self):
        """Delete all todos from database."""
        statement = select(Todo)
        todos = self.session.exec(statement).all()
        for todo in todos:
            self.session.delete(todo)
        self.session.commit()

    def verify_todo_exists(self, todo_id: UUID) -> bool:
        """
        Verify todo exists in database.

        Args:
            todo_id: Todo UUID

        Returns:
            True if exists, False otherwise
        """
        return self.get_todo_by_id(todo_id) is not None

    def verify_todo_not_exists(self, todo_id: UUID) -> bool:
        """
        Verify todo does not exist in database.

        Args:
            todo_id: Todo UUID

        Returns:
            True if does not exist, False if exists
        """
        return not self.verify_todo_exists(todo_id)

    def get_todo_version(self, todo_id: UUID) -> Optional[int]:
        """
        Get current version of todo.

        Args:
            todo_id: Todo UUID

        Returns:
            Version number or None if not found
        """
        todo = self.get_todo_by_id(todo_id)
        return todo.version if todo else None


# Pytest fixture
import pytest


@pytest.fixture
def db_client(db_session):
    """Create database client for testing."""
    return DBClient(db_session)
