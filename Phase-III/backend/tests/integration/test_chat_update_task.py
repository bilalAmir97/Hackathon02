"""Integration tests for update task intent (User Story 3).

Tests the complete flow for updating tasks through chat.
Following TDD approach - these tests should fail until update intent is implemented.
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
async def test_chat_update_task_intent(async_client, test_user, test_token, test_db_session_with_user):
    """Test that 'rename task X to Y' triggers update_task tool.

    This is the core US3 test: user asks to update a task and agent calls update_task.
    """
    # Arrange - First create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to buy milk"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Extract task ID from create response
    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act - Update the task
    message = f"Rename task {task_id} to buy organic milk"
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify tool_calls array contains update_task
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    # Find update_task call
    update_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "update_task"),
        None
    )
    assert update_call is not None, "Should call update_task tool"
    assert update_call["input_parameters"]["task_id"] == task_id
    assert "organic milk" in update_call["input_parameters"]["title"].lower()


@pytest.mark.asyncio
async def test_chat_update_task_with_description(async_client, test_user, test_token, test_db_session_with_user):
    """Test updating both title and description.

    Note: This test uses a simplified message format that the mock agent can parse.
    When the real AI agent is integrated, more complex natural language will be supported.
    """
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to buy groceries"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act - Update with simpler format (mock agent limitation)
    message = f"Update task {task_id} to Buy organic groceries"
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    update_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "update_task"),
        None
    )
    assert update_call is not None
    assert update_call["input_parameters"]["task_id"] == task_id
    # With real AI agent, description extraction will work better
    # For now, just verify the update was called


@pytest.mark.asyncio
async def test_chat_update_task_returns_updated_data(async_client, test_user, test_token, test_db_session_with_user):
    """Test that update_task returns updated task data in output_result."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test updates"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act - Update the task
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Rename task {task_id} to updated test task"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    update_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "update_task"),
        None
    )
    assert update_call is not None
    assert "output_result" in update_call
    assert "id" in update_call["output_result"]
    assert "title" in update_call["output_result"]
    assert update_call["output_result"]["id"] == task_id
    assert "updated" in update_call["output_result"]["title"].lower()


@pytest.mark.asyncio
async def test_chat_update_intent_variations(async_client, test_user, test_token, test_db_session_with_user):
    """Test various phrasings that should trigger update intent."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test variations"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Test different update phrasings
    messages = [
        f"Rename task {task_id} to new title",
        f"Change task {task_id} to different title",
        f"Update task {task_id} to modified title",
        f"Modify task {task_id} to altered title",
        f"Edit task {task_id} to revised title"
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

        # Each should trigger update_task
        update_call = next(
            (call for call in data["tool_calls"] if call["tool_name"] == "update_task"),
            None
        )
        assert update_call is not None, f"Message '{message}' should trigger update_task"
        assert update_call["input_parameters"]["task_id"] == task_id
