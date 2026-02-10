"""Integration tests for list tasks intent (User Story 2).

Tests the complete flow for listing and querying tasks through chat.
Following TDD approach - these tests should fail until list intent is implemented.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def async_client():
    """Create async test client."""
    from src.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_chat_list_tasks_intent(async_client, test_user, test_token, test_db_session_with_user):
    """Test that 'show me my tasks' triggers list_tasks tool.

    This is the core US2 test: user asks to see tasks and agent calls list_tasks.
    """
    # Arrange
    message = "Show me my tasks"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify tool_calls array contains list_tasks
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    # Find list_tasks call
    list_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "list_tasks"),
        None
    )
    assert list_call is not None, "Should call list_tasks tool"


@pytest.mark.asyncio
async def test_chat_list_tasks_with_status_filter(async_client, test_user, test_token, test_db_session_with_user):
    """Test that 'show pending tasks' filters by status."""
    # Arrange
    message = "Show me my pending tasks"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify list_tasks called with status filter
    list_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "list_tasks"),
        None
    )
    assert list_call is not None
    assert "status" in list_call["input_parameters"]
    assert list_call["input_parameters"]["status"] == "pending"


@pytest.mark.asyncio
async def test_chat_list_tasks_returns_task_data(async_client, test_user, test_token, test_db_session_with_user):
    """Test that list_tasks returns task data in output_result."""
    # Arrange - First create a task
    await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test listing"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Act - List tasks
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me my tasks"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    list_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "list_tasks"),
        None
    )
    assert list_call is not None
    assert "output_result" in list_call
    assert "tasks" in list_call["output_result"]
    assert isinstance(list_call["output_result"]["tasks"], list)


@pytest.mark.asyncio
async def test_chat_list_tasks_empty_list(async_client, test_user, test_token, test_db_session_with_user):
    """Test that empty task list is handled gracefully."""
    # Arrange
    message = "What tasks do I have?"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should still call list_tasks even if empty
    list_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "list_tasks"),
        None
    )
    assert list_call is not None
    assert list_call["execution_status"] == "success"


@pytest.mark.asyncio
async def test_chat_list_intent_variations(async_client, test_user, test_token, test_db_session_with_user):
    """Test various phrasings that should trigger list intent."""
    # Arrange
    messages = [
        "Show me my tasks",
        "List all tasks",
        "What tasks do I have?",
        "Display my tasks",
        "View my tasks"
    ]

    # Act & Assert
    for message in messages:
        response = await async_client.post(
            f"/api/{test_user.id}/chat",
            json={"message": message},
            headers={"Authorization": f"Bearer {test_token}"}
        )

        assert response.status_code == 200, f"Failed for message: {message}"
        data = response.json()

        # Each should trigger list_tasks
        list_call = next(
            (call for call in data["tool_calls"] if call["tool_name"] == "list_tasks"),
            None
        )
        assert list_call is not None, f"Message '{message}' should trigger list_tasks"
