"""Contract tests for GET /api/{user_id}/tasks/{task_id} endpoint.

Tests API contract compliance for task retrieval including:
- Successful retrieval (200 OK)
- Task not found (404 Not Found)
- Unauthorized access (404 - timing attack prevention)
- Response schema validation
"""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_get_task_success(test_user: User, test_token: str, test_db_session_with_user):
    """Test successful task retrieval returns 200 with correct response format."""
    user_id = str(test_user.id)

    # First create a task
    task_data = {
        "title": "Test task",
        "description": "Test description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]

        # Retrieve task
        response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body matches TaskResponse schema
    data = response.json()
    assert "id" in data, "Missing 'id' field"
    assert "user_id" in data, "Missing 'user_id' field"
    assert "title" in data, "Missing 'title' field"
    assert "description" in data, "Missing 'description' field"
    assert "status" in data, "Missing 'status' field"
    assert "created_at" in data, "Missing 'created_at' field"
    assert "updated_at" in data, "Missing 'updated_at' field"

    # Assert field values match created task
    assert data["id"] == task_id
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["user_id"] == user_id
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_task_not_found(test_user: User, test_token: str, test_db_session_with_user):
    """Test retrieving non-existent task returns 404."""
    user_id = str(test_user.id)
    task_id = "123e4567-e89b-12d3-a456-426614174000"  # Non-existent task

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert error response format (RFC 7807)
    data = response.json()
    assert "type" in data, "Missing 'type' field in error response"
    assert "title" in data, "Missing 'title' field in error response"
    assert "status" in data, "Missing 'status' field in error response"
    assert "detail" in data, "Missing 'detail' field in error response"
    assert "instance" in data, "Missing 'instance' field in error response"
    assert data["status"] == 404


@pytest.mark.asyncio
async def test_get_task_unauthorized_access(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test retrieving another user's task returns 404 (timing attack prevention)."""
    user1_id = str(test_user.id)
    user2_id = str(test_user_2.id)

    # Create task as user1
    task_data = {
        "title": "User1's task",
        "description": "Private task",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create task as user1
        create_response = await client.post(
            f"/api/{user1_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]

        # Try to retrieve as user2
        response = await client.get(
            f"/api/{user2_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

    # Assert status code is 404 (not 403) to prevent information leakage
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data, "Missing 'detail' field in error response"
    # Should not reveal whether task exists or belongs to another user
    assert "does not belong" in data["detail"].lower() or "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_task_invalid_task_id_format(test_user: User, test_token: str):
    """Test retrieving task with invalid task_id format returns 422."""
    user_id = str(test_user.id)
    task_id = "invalid-uuid"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_task_invalid_user_id_format(test_token: str):
    """Test retrieving task with invalid user_id format returns 422."""
    user_id = "invalid-uuid"
    task_id = "123e4567-e89b-12d3-a456-426614174000"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_task_response_schema_validation(test_user: User, test_token: str, test_db_session_with_user):
    """Test that retrieved task response matches expected schema exactly."""
    user_id = str(test_user.id)

    # Create task
    task_data = {
        "title": "Schema validation test",
        "description": "Testing response schema",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        task_id = create_response.json()["id"]

        # Retrieve task
        response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    assert response.status_code == 200
    data = response.json()

    # Validate UUID fields
    try:
        UUID(data["id"])
        UUID(data["user_id"])
    except ValueError as e:
        pytest.fail(f"Invalid UUID format: {e}")

    # Validate string fields
    assert isinstance(data["title"], str)
    assert isinstance(data["description"], (str, type(None)))
    assert isinstance(data["status"], str)
    assert data["status"] in ["pending", "completed"]

    # Validate timestamp fields (ISO 8601 format)
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)
    # Basic ISO 8601 format check
    assert "T" in data["created_at"]
    assert "T" in data["updated_at"]
