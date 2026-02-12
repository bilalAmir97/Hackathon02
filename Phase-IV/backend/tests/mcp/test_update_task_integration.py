"""Integration tests for update_task tool.

This module tests the update_task tool with actual database operations,
verifying task updates, version increment, optimistic locking, ownership
validation, and error handling.
"""

import pytest
from uuid import UUID, uuid4

from src.mcp.tools.update_task import update_task
from src.mcp.middleware.error_handler import MCPErrorCode
from src.domain.models import Task
from src.schemas.task import TaskCreate


@pytest.mark.asyncio
class TestUpdateTaskIntegration:
    """Integration tests for update_task tool with database."""

    async def test_update_task_updates_title(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task updates task title."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id, title="Old title")
        input_data = {"task_id": str(task_id), "title": "New title"}

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["id"] == str(task_id)
        assert result["title"] == "New title"
        assert result["user_id"] == str(test_user.id)

    async def test_update_task_updates_description(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task updates task description."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id, description="Old description")
        input_data = {"task_id": str(task_id), "description": "New description"}

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["id"] == str(task_id)
        assert result["description"] == "New description"

    async def test_update_task_updates_both_fields(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task can update both title and description."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id, title="Old", description="Old desc")
        input_data = {
            "task_id": str(task_id),
            "title": "New title",
            "description": "New description"
        }

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["title"] == "New title"
        assert result["description"] == "New description"

    async def test_update_task_increments_version(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task increments version number."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id), "title": "Updated"}

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["version"] == 2  # Incremented from 1

    async def test_update_task_preserves_task_id(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task preserves task_id."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id), "title": "Updated"}

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["id"] == str(task_id)

    async def test_update_task_updates_timestamp(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task updates the updated_at timestamp."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)

        # Get initial task state
        from src.mcp.tools.list_tasks import list_tasks
        initial_tasks = await list_tasks({"status": "all"}, headers)
        initial_task = next(t for t in initial_tasks["tasks"] if t["id"] == str(task_id))
        initial_updated_at = initial_task["updated_at"]

        input_data = {"task_id": str(task_id), "title": "Updated"}

        # Act
        result = await update_task(input_data, headers)

        # Assert
        assert result["updated_at"] > initial_updated_at

    async def test_update_task_enforces_ownership(self, test_db_session, test_user, test_user_2, test_token_2, create_task_with_data):
        """Verify update_task rejects attempts to update another user's task."""
        # Arrange
        task_id = await create_task_with_data(test_user.id)
        headers = {"authorization": f"Bearer {test_token_2}"}  # Different user
        input_data = {"task_id": str(task_id), "title": "Hacked"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] in [MCPErrorCode.TASK_NOT_FOUND.value, MCPErrorCode.FORBIDDEN.value]

    async def test_update_task_nonexistent_task(self, test_db_session, test_user, test_token):
        """Verify update_task returns TASK_NOT_FOUND for non-existent task."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        input_data = {"task_id": str(uuid4()), "title": "Updated"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.TASK_NOT_FOUND.value

    async def test_update_task_missing_authorization_header(self, test_db_session):
        """Verify update_task returns UNAUTHORIZED without auth header."""
        # Arrange
        headers = {}
        input_data = {"task_id": str(uuid4()), "title": "Updated"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_update_task_invalid_token(self, test_db_session):
        """Verify update_task returns UNAUTHORIZED with invalid token."""
        # Arrange
        headers = {"authorization": "Bearer invalid-token"}
        input_data = {"task_id": str(uuid4()), "title": "Updated"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_update_task_empty_title(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task returns INVALID_INPUT for empty title."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id), "title": ""}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_update_task_title_too_long(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task returns INVALID_INPUT for title > 200 chars."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id), "title": "x" * 201}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_update_task_description_too_long(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify update_task returns INVALID_INPUT for description > 2000 chars."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id), "description": "x" * 2001}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await update_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value


# Fixture for creating tasks in database
@pytest.fixture
async def create_task_with_data(test_db_session):
    """Fixture to create a task with specific data in database."""
    from src.use_cases.task_operations import create_task

    async def _create(user_id: UUID, title: str = "Test task", description: str | None = None) -> UUID:
        """Create a task and return its ID."""
        task_data = TaskCreate(title=title, description=description)
        task = await create_task(test_db_session, user_id, task_data)
        return task.id

    return _create
