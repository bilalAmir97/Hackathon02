"""Performance tests for response time validation.

Tests that the chat endpoint responds within acceptable time limits.
Target: 3 seconds for typical requests.
"""

import pytest
import time
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def async_client():
    """Create async test client."""
    from src.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_chat_response_time_under_3_seconds(async_client, test_user, test_token, test_db_session_with_user):
    """Test that chat endpoint responds within 3 seconds for typical requests."""
    # Arrange
    message = "Create a task to test response time"

    # Act
    start_time = time.time()
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    end_time = time.time()

    # Assert
    response_time = end_time - start_time
    assert response.status_code == 200, f"Request failed with status {response.status_code}"
    assert response_time < 3.0, f"Response time {response_time:.2f}s exceeds 3s limit"

    # Log response time for monitoring
    print(f"Response time: {response_time:.3f}s")


@pytest.mark.asyncio
async def test_chat_list_response_time(async_client, test_user, test_token, test_db_session_with_user):
    """Test that list tasks responds quickly."""
    # Arrange - Create a few tasks first
    for i in range(5):
        await async_client.post(
            f"/api/{test_user.id}/chat",
            json={"message": f"Create task {i}"},
            headers={"Authorization": f"Bearer {test_token}"}
        )

    # Act
    start_time = time.time()
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me my tasks"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    end_time = time.time()

    # Assert
    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 3.0, f"List response time {response_time:.2f}s exceeds 3s limit"

    print(f"List response time: {response_time:.3f}s")


@pytest.mark.asyncio
async def test_chat_update_response_time(async_client, test_user, test_token, test_db_session_with_user):
    """Test that update task responds quickly."""
    # Arrange - Create a task
    create_response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to update"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    create_data = create_response.json()
    add_call = next(
        (call for call in create_data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    task_id = add_call["output_result"]["id"]

    # Act
    start_time = time.time()
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Rename task {task_id} to Updated task"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    end_time = time.time()

    # Assert
    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 3.0, f"Update response time {response_time:.2f}s exceeds 3s limit"

    print(f"Update response time: {response_time:.3f}s")


@pytest.mark.asyncio
async def test_chat_conversation_resume_response_time(async_client, test_user, test_token, test_db_session_with_user):
    """Test that resuming conversation responds quickly."""
    # Arrange - Create initial conversation
    response1 = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Act - Resume conversation
    start_time = time.time()
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Show me my tasks",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    end_time = time.time()

    # Assert
    response_time = end_time - start_time
    assert response.status_code == 200
    assert response_time < 3.0, f"Resume response time {response_time:.2f}s exceeds 3s limit"

    print(f"Resume conversation response time: {response_time:.3f}s")
