"""Integration tests for complete task intent with confirmation (User Story 4).

Tests the complete flow for marking tasks as complete with confirmation.
Following TDD approach - these tests should fail until confirmation flow is implemented.
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
async def test_chat_complete_task_requests_confirmation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that 'mark task as done' requests confirmation before executing.

    This is the core US4 test: user asks to complete a task and agent requests confirmation.
    """
    # Arrange - Create a task first
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test completion"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act - Request to complete the task
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Mark task {task_id} as done"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should NOT execute complete_task immediately
    complete_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "complete_task"),
        None
    )
    assert complete_call is None, "Should not execute complete_task without confirmation"

    # Should ask for confirmation in response
    assert "confirm" in data["response"].lower() or "sure" in data["response"].lower()


@pytest.mark.asyncio
async def test_chat_complete_task_executes_after_confirmation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that explicit confirmation executes complete_task."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test confirmation"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Request completion (should ask for confirmation)
    await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Mark task {task_id} as done",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Act - Confirm the action
    confirm_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Yes, please do it",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert confirm_response.status_code == 200
    confirm_data = confirm_response.json()

    # Should now execute complete_task
    complete_call = next(
        (call for call in confirm_data["tool_calls"] if call["tool_name"] == "complete_task"),
        None
    )
    assert complete_call is not None, "Should execute complete_task after confirmation"
    assert complete_call["input_parameters"]["task_id"] == task_id
    assert complete_call["execution_status"] == "success"


@pytest.mark.asyncio
async def test_chat_complete_task_explicit_confirmation_bypasses_prompt(async_client, test_user, test_token, test_db_session_with_user):
    """Test that explicit confirmation in initial message bypasses confirmation prompt."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test explicit confirmation"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Act - Request completion with explicit confirmation (in same conversation)
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Yes, mark task {task_id} as done",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Should execute complete_task immediately (explicit confirmation detected)
    complete_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "complete_task"),
        None
    )
    assert complete_call is not None, "Should execute with explicit confirmation"
    assert complete_call["input_parameters"]["task_id"] == task_id


@pytest.mark.asyncio
async def test_chat_complete_task_rejection_cancels_action(async_client, test_user, test_token, test_db_session_with_user):
    """Test that rejecting confirmation cancels the action."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to test rejection"},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]
    conversation_id = create_data["conversation_id"]

    # Request completion (should ask for confirmation)
    await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": f"Mark task {task_id} as done",
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

    # Should NOT execute complete_task
    complete_call = next(
        (call for call in reject_data["tool_calls"] if call["tool_name"] == "complete_task"),
        None
    )
    assert complete_call is None, "Should not execute after rejection"
    assert "cancel" in reject_data["response"].lower() or "ok" in reject_data["response"].lower()


@pytest.mark.asyncio
async def test_chat_complete_intent_variations(async_client, test_user, test_token, test_db_session_with_user):
    """Test various phrasings that should trigger complete intent."""
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

    # Test different complete phrasings
    messages = [
        f"Mark task {task_id} as done",
        f"Complete task {task_id}",
        f"Finish task {task_id}",
        f"Task {task_id} is done",
        f"Mark {task_id} as completed"
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
        # At minimum, the response should acknowledge the complete intent
        assert "confirm" in data["response"].lower() or "done" in data["response"].lower() or "complete" in data["response"].lower(), \
            f"Message '{message}' should trigger complete intent"
