"""Contract tests for DELETE /api/{user_id}/tasks/{task_id} endpoint.

Tests API contract compliance for task deletion including:
- Successful deletion (204 No Content)
- Delete non-existent task (404)
- Delete unauthorized task (404)
- Verify task deleted (404 on subsequent GET)
"""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_delete_task_success(test_user: User, test_token: str, test_db_session_with_user):
    """Test successful task deletion returns 204 No Content."""
    user_id = str(test_user.id)

    # First create a task
    create_data = {
        "title": "Task to delete",
        "description": "This will be deleted",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Delete the task
        response = await client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.text}"

    # Assert no content in response body
    assert response.text == "", "Response body should be empty for 204"


@pytest.mark.asyncio
async def test_delete_task_not_found(test_user: User, test_token: str, test_db_session_with_user):
    """Test deleting non-existent task returns 404."""
    user_id = str(test_user.id)
    task_id = str(uuid4())  # Non-existent task

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data or "title" in data, "Missing error details"


@pytest.mark.asyncio
async def test_delete_task_unauthorized(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test deleting task owned by another user returns 404."""
    user_id_1 = str(test_user.id)
    user_id_2 = str(test_user_2.id)

    # Create task as user 1
    create_data = {
        "title": "User 1 task",
        "description": "Owned by user 1",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id_1}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Try to delete as user 2
        response = await client.delete(
            f"/api/{user_id_2}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

    # Assert status code (404 for timing attack prevention)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_delete_task_verify_deleted(test_user: User, test_token: str, test_db_session_with_user):
    """Test that deleted task cannot be retrieved (404 on subsequent GET)."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Task to delete and verify",
        "description": "Will be deleted",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Verify task exists
        get_response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert get_response.status_code == 200

        # Delete the task
        delete_response = await client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert delete_response.status_code == 204

        # Try to get deleted task
        get_after_delete = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert task is not found after deletion
    assert get_after_delete.status_code == 404, f"Expected 404, got {get_after_delete.status_code}"


@pytest.mark.asyncio
async def test_delete_task_invalid_task_id_format(test_user: User, test_token: str):
    """Test deleting task with invalid task_id format returns 422."""
    user_id = str(test_user.id)
    task_id = "invalid-uuid"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.delete(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
