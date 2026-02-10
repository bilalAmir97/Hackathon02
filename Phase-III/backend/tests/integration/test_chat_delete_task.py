"""Integration tests for delete task intent with confirmation (User Story 5).

Tests the complete flow for deleting tasks with confirmation.
Following TDD approach - these tests should fail until delete flow is implemented.
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
async def test_chat_delete_task_requests_confirmation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that 'delete task' requests confirmation before executing.

    This is the core US5 test: user asks to delete a task and agent requests confirmation.
    """
    # Arrange - Create a task first
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test deletion"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act - Request to delete the task
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Delete task {task_id}"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should NOT execute delete_task immediately
    delete_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "delete_task"),
        None
    )
    assert delete_call is None, "Should not execute delete_task without confirmation"

    # Should ask for confirmation in response
    assert "confirm" in data["response"].lower() or "sure" in data["response"].lower()


@pytest.mark.asyncio
async def test_chat_delete_task_executes_after_confirmation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that explicit confirmation executes delete_task."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test delete confirmation"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Request deletion (should ask for confirmation)
    await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Delete task {task_id}",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Act - Confirm the action
    confirm_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Yes, delete it",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert confirm_response.status_code == 200
    confirm_data = confirm_response.json()

    # Should now execute delete_task
    delete_call = next(
        (call for call in confirm_data["tool_calls"] if call["tool_name"] == "delete_task"),
        None
    )
    assert delete_call is not None, "Should execute delete_task after confirmation"
    assert delete_call["input_parameters"]["task_id"] == task_id
    assert delete_call["execution_status"] == "success"


@pytest.mark.asyncio
async def test_chat_delete_task_explicit_confirmation_bypasses_prompt(async_client, test_user, test_token, test_db_session_with_user):
    """Test that explicit confirmation in initial message bypasses confirmation prompt."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test explicit delete confirmation"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Act - Request deletion with explicit confirmation (in same conversation)
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Yes, delete task {task_id}",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should execute delete_task immediately (explicit confirmation detected)
    delete_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "delete_task"),
        None
    )
    assert delete_call is not None, "Should execute with explicit confirmation"
    assert delete_call["input_parameters"]["task_id"] == task_id


@pytest.mark.asyncio
async def test_chat_delete_task_rejection_cancels_action(async_client, test_user, test_token, test_db_session_with_user):
    """Test that rejecting confirmation cancels the delete action."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test delete rejection"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Request deletion (should ask for confirmation)
    await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Delete task {task_id}",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Act - Reject the action
    reject_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "No, cancel that",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert reject_response.status_code == 200
    reject_data = reject_response.json()

    # Should NOT execute delete_task
    delete_call = next(
        (call for call in reject_data["tool_calls"] if call["tool_name"] == "delete_task"),
        None
    )
    assert delete_call is None, "Should not execute after rejection"
    assert "cancel" in reject_data["response"].lower() or "ok" in reject_data["response"].lower()


@pytest.mark.asyncio
async def test_chat_delete_intent_variations(async_client, test_user, test_token, test_db_session_with_user):
    """Test various phrasings that should trigger delete intent."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test delete variations"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Test different delete phrasings
    messages = [
        f"Delete task {task_id}",
        f"Remove task {task_id}",
        f"Cancel task {task_id}",
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

        # Each should either request confirmation or execute (if explicit confirmation detected)
        # At minimum, the response should acknowledge the delete intent
        assert "confirm" in data["response"].lower() or "delete" in data["response"].lower() or "remove" in data["response"].lower(), \
            f"Message '{message}' should trigger delete intent"
