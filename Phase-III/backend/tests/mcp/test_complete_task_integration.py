"""Integration tests for complete_task tool.

This module tests the complete_task tool with actual database operations,
verifying task completion, idempotency, ownership validation, and error handling.
"""

import pytest
from uuid import UUID, uuid4

from src.mcp.tools.complete_task import complete_task
from src.mcp.middleware.error_handler import MCPErrorCode


@pytest.mark.asyncio
class TestCompleteTaskIntegration:
    """Integration tests for complete_task tool with database."""

    async def test_complete_task_changes_status_to_completed(self, test_db_session, test_user, create_pending_task):
        """Verify complete_task changes task status from pending to completed."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        task_id = await create_pending_task(test_user["user_id"])
        input_data = {"task_id": str(task_id)}

        # Act
        result = await complete_task(input_data, headers)

        # Assert
        assert result["id"] == str(task_id)
        assert result["status"] == "completed"
        assert result["user_id"] == str(test_user["user_id"])

    async def test_complete_task_increments_version(self, test_db_session, test_user, create_pending_task):
        """Verify complete_task increments version number."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        task_id = await create_pending_task(test_user["user_id"])
        input_data = {"task_id": str(task_id)}

        # Act
        result = await complete_task(input_data, headers)

        # Assert
        assert result["version"] == 2  # Incremented from 1

    async def test_complete_task_updates_timestamp(self, test_db_session, test_user, create_pending_task):
        """Verify complete_task updates the updated_at timestamp."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        task_id = await create_pending_task(test_user["user_id"])
        input_data = {"task_id": str(task_id)}

        # Get initial task state
        from src.mcp.tools.list_tasks import list_tasks
        initial_tasks = await list_tasks({"status": "all"}, headers)
        initial_task = next(t for t in initial_tasks["tasks"] if t["id"] == str(task_id))
        initial_updated_at = initial_task["updated_at"]

        # Act
        result = await complete_task(input_data, headers)

        # Assert
        assert result["updated_at"] > initial_updated_at

    async def test_complete_task_is_idempotent(self, test_db_session, test_user, create_pending_task):
        """Verify completing an already-completed task succeeds without error."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        task_id = await create_pending_task(test_user["user_id"])
        input_data = {"task_id": str(task_id)}

        # Act - complete twice
        result1 = await complete_task(input_data, headers)
        result2 = await complete_task(input_data, headers)

        # Assert - both succeed
        assert result1["status"] == "completed"
        assert result2["status"] == "completed"
        assert result1["id"] == result2["id"]

    async def test_complete_task_enforces_ownership(self, test_db_session, test_user, test_user2, create_pending_task):
        """Verify complete_task rejects attempts to complete another user's task."""
        # Arrange
        task_id = await create_pending_task(test_user["user_id"])
        headers = {"authorization": f"Bearer {test_user2['token']}"}  # Different user
        input_data = {"task_id": str(task_id)}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] in [MCPErrorCode.TASK_NOT_FOUND.value, MCPErrorCode.FORBIDDEN.value]

    async def test_complete_task_nonexistent_task(self, test_db_session, test_user):
        """Verify complete_task returns TASK_NOT_FOUND for non-existent task."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"task_id": str(uuid4())}  # Random UUID

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.TASK_NOT_FOUND.value

    async def test_complete_task_missing_authorization_header(self, test_db_session):
        """Verify complete_task returns UNAUTHORIZED without auth header."""
        # Arrange
        headers = {}
        input_data = {"task_id": str(uuid4())}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_complete_task_invalid_token(self, test_db_session):
        """Verify complete_task returns UNAUTHORIZED with invalid token."""
        # Arrange
        headers = {"authorization": "Bearer invalid-token"}
        input_data = {"task_id": str(uuid4())}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_complete_task_invalid_uuid_format(self, test_db_session, test_user):
        """Verify complete_task returns INVALID_INPUT for invalid UUID."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"task_id": "not-a-uuid"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_complete_task_missing_task_id(self, test_db_session, test_user):
        """Verify complete_task returns INVALID_INPUT without task_id."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {}  # Missing task_id

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await complete_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value


# Fixtures for testing
@pytest.fixture
async def test_db_session():
    """Provide test database session."""
    pass


@pytest.fixture
async def test_user():
    """Provide test user with valid JWT token."""
    return {
        "user_id": uuid4(),
        "token": "valid-test-token"
    }


@pytest.fixture
async def test_user2():
    """Provide second test user for ownership tests."""
    return {
        "user_id": uuid4(),
        "token": "valid-test-token-2"
    }


@pytest.fixture
async def create_pending_task():
    """Fixture to create a pending task in database."""
    async def _create(user_id: UUID) -> UUID:
        """Create a pending task and return its ID."""
        # This will be implemented when database test utilities are set up
        return uuid4()

    return _create
