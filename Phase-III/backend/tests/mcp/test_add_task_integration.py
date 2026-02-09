"""Integration tests for add_task tool.

This module tests the add_task tool with actual database operations,
verifying task persistence, user isolation, and error handling.
"""

import pytest
from uuid import UUID, uuid4

from src.mcp.tools.add_task import add_task
from src.mcp.middleware.error_handler import MCPErrorCode


@pytest.mark.asyncio
class TestAddTaskIntegration:
    """Integration tests for add_task tool with database."""

    async def test_add_task_creates_task_in_database(self, test_db_session, test_user):
        """Verify add_task persists task to database."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        }

        # Act
        result = await add_task(input_data, headers)

        # Assert
        assert result["id"] is not None
        assert result["user_id"] == str(test_user["user_id"])
        assert result["title"] == "Buy groceries"
        assert result["description"] == "Milk, eggs, bread"
        assert result["status"] == "pending"
        assert result["version"] == 1
        assert result["created_at"] is not None
        assert result["updated_at"] is not None

    async def test_add_task_generates_unique_uuid(self, test_db_session, test_user):
        """Verify each task gets a unique UUID."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"title": "Task 1"}

        # Act
        result1 = await add_task(input_data, headers)
        result2 = await add_task(input_data, headers)

        # Assert
        assert result1["id"] != result2["id"]
        assert UUID(result1["id"])  # Valid UUID
        assert UUID(result2["id"])  # Valid UUID

    async def test_add_task_enforces_user_isolation(self, test_db_session, test_user, test_user2):
        """Verify tasks are isolated by user_id."""
        # Arrange
        headers1 = {"authorization": f"Bearer {test_user['token']}"}
        headers2 = {"authorization": f"Bearer {test_user2['token']}"}
        input_data = {"title": "Test task"}

        # Act
        result1 = await add_task(input_data, headers1)
        result2 = await add_task(input_data, headers2)

        # Assert
        assert result1["user_id"] == str(test_user["user_id"])
        assert result2["user_id"] == str(test_user2["user_id"])
        assert result1["user_id"] != result2["user_id"]

    async def test_add_task_without_description(self, test_db_session, test_user):
        """Verify add_task works with only title (description optional)."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"title": "Simple task"}

        # Act
        result = await add_task(input_data, headers)

        # Assert
        assert result["title"] == "Simple task"
        assert result["description"] is None

    async def test_add_task_missing_authorization_header(self, test_db_session):
        """Verify add_task returns UNAUTHORIZED without auth header."""
        # Arrange
        headers = {}
        input_data = {"title": "Test task"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await add_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_add_task_invalid_token(self, test_db_session):
        """Verify add_task returns UNAUTHORIZED with invalid token."""
        # Arrange
        headers = {"authorization": "Bearer invalid-token"}
        input_data = {"title": "Test task"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await add_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.UNAUTHORIZED.value

    async def test_add_task_missing_title(self, test_db_session, test_user):
        """Verify add_task returns INVALID_INPUT without title."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"description": "No title provided"}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await add_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_add_task_title_too_long(self, test_db_session, test_user):
        """Verify add_task returns INVALID_INPUT for title > 200 chars."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {"title": "x" * 201}

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await add_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_add_task_description_too_long(self, test_db_session, test_user):
        """Verify add_task returns INVALID_INPUT for description > 2000 chars."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        input_data = {
            "title": "Test",
            "description": "x" * 2001
        }

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await add_task(input_data, headers)

        error = exc_info.value.args[0]
        assert error["error"]["code"] == MCPErrorCode.INVALID_INPUT.value

    async def test_add_task_concurrent_requests(self, test_db_session, test_user):
        """Verify add_task handles concurrent requests without data loss."""
        # Arrange
        headers = {"authorization": f"Bearer {test_user['token']}"}
        tasks = [
            {"title": f"Task {i}", "description": f"Description {i}"}
            for i in range(10)
        ]

        # Act
        import asyncio
        results = await asyncio.gather(*[
            add_task(task, headers) for task in tasks
        ])

        # Assert
        assert len(results) == 10
        task_ids = [r["id"] for r in results]
        assert len(set(task_ids)) == 10  # All unique IDs
        for i, result in enumerate(results):
            assert result["title"] == f"Task {i}"
            assert result["user_id"] == str(test_user["user_id"])


# Fixtures for testing
@pytest.fixture
async def test_db_session():
    """Provide test database session."""
    # This will be implemented when database test utilities are set up
    pass


@pytest.fixture
async def test_user():
    """Provide test user with valid JWT token."""
    # This will be implemented when auth test utilities are set up
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
