"""Contract tests for PATCH /api/{user_id}/tasks/{task_id}/complete endpoint.

Tests API contract compliance for task completion toggle including:
- Toggle pending → completed (200 OK)
- Toggle completed → pending (200 OK)
- Complete non-existent task (404)
- Complete unauthorized task (404)
"""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_complete_task_pending_to_completed(test_user: User, test_token: str, test_db_session_with_user):
    """Test toggling task from pending to completed returns 200."""
    user_id = str(test_user.id)

    # Create a task (defaults to pending)
    create_data = {
        "title": "Task to complete",
        "description": "Will be marked as completed",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        assert create_response.json()["status"] == "pending"

        # Toggle to completed
        response = await client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body
    data = response.json()
    assert data["id"] == task_id
    assert data["user_id"] == user_id
    assert data["status"] == "completed", "Status should be 'completed'"
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_complete_task_completed_to_pending(test_user: User, test_token: str, test_db_session_with_user):
    """Test toggling task from completed back to pending returns 200."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Task to toggle",
        "description": "Will be toggled twice",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # First toggle: pending → completed
        first_toggle = await client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert first_toggle.status_code == 200
        assert first_toggle.json()["status"] == "completed"

        # Second toggle: completed → pending
        response = await client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body
    data = response.json()
    assert data["id"] == task_id
    assert data["status"] == "pending", "Status should be 'pending' after second toggle"


@pytest.mark.asyncio
async def test_complete_task_not_found(test_user: User, test_token: str, test_db_session_with_user):
    """Test completing non-existent task returns 404."""
    user_id = str(test_user.id)
    task_id = str(uuid4())  # Non-existent task

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data or "title" in data, "Missing error details"


@pytest.mark.asyncio
async def test_complete_task_unauthorized(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test completing task owned by another user returns 404."""
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

        # Try to complete as user 2
        response = await client.patch(
            f"/api/{user_id_2}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

    # Assert status code (404 for timing attack prevention)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_complete_task_invalid_task_id_format(test_user: User, test_token: str):
    """Test completing task with invalid task_id format returns 422."""
    user_id = str(test_user.id)
    task_id = "invalid-uuid"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.patch(
            f"/api/{user_id}/tasks/{task_id}/complete",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
