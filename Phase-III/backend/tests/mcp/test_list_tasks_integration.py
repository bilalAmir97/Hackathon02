"""Integration tests for list_tasks tool.

This module tests the list_tasks tool with actual database operations,
verifying task retrieval, filtering, ordering, and user isolation.
"""

import pytest
from uuid import UUID, uuid4

from src.mcp.tools.list_tasks import list_tasks
from src.mcp.middleware.error_handler import MCPErrorCode


@pytest.mark.asyncio
class TestListTasksIntegration:
    """Integration tests for list_tasks tool with database."""

    async def test_list_tasks_returns_empty_list_for_new_user(self, test_db_session, test_user):
        """Verify list_tasks returns empty list when user has no tasks."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"status": "all"}

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["tasks"] == []
        assert result["count"] == 0

    async def test_list_tasks_returns_all_user_tasks(self, test_db_session, test_user, create_test_tasks):
        """Verify list_tasks returns all tasks for user with status='all'."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        await create_test_tasks(test_user["user_id"], count=5)
        input_data = {"status": "all"}

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["count"] == 5
        assert len(result["tasks"]) == 5
        for task in result["tasks"]:
            assert task["user_id"] == str(test_user["user_id"])

    async def test_list_tasks_filters_by_pending_status(self, test_db_session, test_user, create_test_tasks):
        """Verify list_tasks filters tasks by pending status."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        await create_test_tasks(test_user["user_id"], pending=3, completed=2)
        input_data = {"status": "pending"}

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["count"] == 3
        for task in result["tasks"]:
            assert task["status"] == "pending"

    async def test_list_tasks_filters_by_completed_status(self, test_db_session, test_user, create_test_tasks):
        """Verify list_tasks filters tasks by completed status."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        await create_test_tasks(test_user["user_id"], pending=3, completed=2)
        input_data = {"status": "completed"}

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["count"] == 2
        for task in result["tasks"]:
            assert task["status"] == "completed"

    async def test_list_tasks_orders_by_created_at_descending(self, test_db_session, test_user, create_test_tasks):
        """Verify list_tasks returns tasks ordered newest first."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        task_ids = await create_test_tasks(test_user["user_id"], count=5)
        input_data = {"status": "all"}

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["count"] == 5
        # Verify descending order (newest first)
        for i in range(len(result["tasks"]) - 1):
            current_time = result["tasks"][i]["created_at"]
            next_time = result["tasks"][i + 1]["created_at"]
            assert current_time >= next_time

    async def test_list_tasks_enforces_user_isolation(self, test_db_session, test_user, test_user2, create_test_tasks):
        """Verify list_tasks only returns tasks for authenticated user."""
        # Arrange
        headers1 = {"authorization": f"Bearer {test_user['token']}"}
        headers2 = {"authorization": f"Bearer {test_user2['token']}"}

        await create_test_tasks(test_user["user_id"], count=3)
        await create_test_tasks(test_user2["user_id"], count=5)

        input_data = {"status": "all"}

        # Act
        result1 = await list_tasks(input_data, headers1)
        result2 = await list_tasks(input_data, headers2)

        # Assert
        assert result1["count"] == 3
        assert result2["count"] == 5

        for task in result1["tasks"]:
            assert task["user_id"] == str(test_user["user_id"])

        for task in result2["tasks"]:
            assert task["user_id"] == str(test_user2["user_id"])

    async def test_list_tasks_missing_authorization_header(self, test_db_session):
        """Verify list_tasks returns UNAUTHORIZED without auth header."""
        # Arrange
        headers = {}
        input_data = {"status": "all"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await list_tasks(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_list_tasks_invalid_token(self, test_db_session):
        """Verify list_tasks returns UNAUTHORIZED with invalid token."""
        # Arrange
        headers = {"authorization": "Bearer invalid-token"}
        input_data = {"status": "all"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await list_tasks(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_list_tasks_invalid_status_filter(self, test_db_session, test_user):
        """Verify list_tasks returns INVALID_INPUT for invalid status."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"status": "invalid"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await list_tasks(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_list_tasks_default_status_is_all(self, test_db_session, test_user, create_test_tasks):
        """Verify list_tasks defaults to status='all' when not specified."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        await create_test_tasks(test_user["user_id"], pending=2, completed=3)
        input_data = {}  # No status specified

        # Act
        result = await list_tasks(input_data, headers)

        # Assert
        assert result["count"] == 5  # All tasks returned


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
    """Provide second test user for isolation tests."""
    return {
        "user_id": uuid4(),
        "token": "valid-test-token-2"
    }


@pytest.fixture
async def create_test_tasks():
    """Fixture to create test tasks in database."""
    async def _create(user_id: UUID, count: int = 0, pending: int = 0, completed: int = 0):
        """Create test tasks with specified counts and statuses."""
        # This will be implemented when database test utilities are set up
        pass

    return _create
