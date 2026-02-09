"""Integration tests for delete_task tool.

This module tests the delete_task tool with actual database operations,
verifying task deletion, ownership validation, and error handling.
"""

import pytest
from uuid import UUID, uuid4

from src.mcp.tools.delete_task import delete_task
from src.mcp.middleware.error_handler import MCPErrorCode
from src.domain.models import Task
from src.schemas.task import TaskCreate


@pytest.mark.asyncio
class TestDeleteTaskIntegration:
    """Integration tests for delete_task tool with database."""

    async def test_delete_task_removes_task_from_database(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify delete_task removes task from database."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id, title="Task to delete")
        input_data = {"task_id": str(task_id)}

        # Act
        result = await delete_task(input_data, headers)

        # Assert
        assert result["success"] is True
        assert result["task_id"] == str(task_id)
        assert "deleted" in result["message"].lower()

    async def test_delete_task_returns_success_confirmation(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify delete_task returns success confirmation."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id)}

        # Act
        result = await delete_task(input_data, headers)

        # Assert
        assert result["success"] is True
        assert result["task_id"] == str(task_id)
        assert isinstance(result["message"], str)

    async def test_delete_task_enforces_ownership(self, test_db_session, test_user, test_user_2, test_token_2, create_task_with_data):
        """Verify delete_task rejects attempts to delete another user's task."""
        # Arrange
        task_id = await create_task_with_data(test_user.id)
        headers = {"authorization": f"Bearer {test_token_2}"}  # Different user
        input_data = {"task_id": str(task_id)}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] in [MCPErrorCode.TASK_NOT_FOUND.value, MCPErrorCode.FORBIDDEN.value]

    async def test_delete_task_nonexistent_task(self, test_db_session, test_user, test_token):
        """Verify delete_task returns TASK_NOT_FOUND for non-existent task."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        input_data = {"task_id": str(uuid4())}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.TASK_NOT_FOUND.value

    async def test_delete_task_missing_authorization_header(self, test_db_session):
        """Verify delete_task returns UNAUTHORIZED without auth header."""
        # Arrange
        headers = {}
        input_data = {"task_id": str(uuid4())}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_delete_task_invalid_token(self, test_db_session):
        """Verify delete_task returns UNAUTHORIZED with invalid token."""
        # Arrange
        headers = {"authorization": "Bearer invalid-token"}
        input_data = {"task_id": str(uuid4())}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_delete_task_invalid_uuid_format(self, test_db_session, test_user, test_token):
        """Verify delete_task returns INVALID_INPUT for invalid UUID."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        input_data = {"task_id": "not-a-uuid"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_delete_task_verifies_task_removed(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify deleted task cannot be retrieved after deletion."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id)}

        # Act
        await delete_task(input_data, headers)

        # Assert - try to list tasks, deleted task should not appear
        from src.mcp.tools.list_tasks import list_tasks
        tasks_result = await list_tasks({"status": "all"}, headers)
        task_ids = [t["id"] for t in tasks_result["tasks"]]
        assert str(task_id) not in task_ids

    async def test_delete_task_idempotent_behavior(self, test_db_session, test_user, test_token, create_task_with_data):
        """Verify delete_task handles double deletion gracefully."""
        # Arrange
        headers = {"authorization": f"Bearer {test_token}"}
        task_id = await create_task_with_data(test_user.id)
        input_data = {"task_id": str(task_id)}

        # Act - delete once
        result1 = await delete_task(input_data, headers)
        assert result1["success"] is True

        # Act - delete again (should fail with TASK_NOT_FOUND)
        with pytest.raises(Exception) as exc_info:
            await delete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.TASK_NOT_FOUND.value


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
