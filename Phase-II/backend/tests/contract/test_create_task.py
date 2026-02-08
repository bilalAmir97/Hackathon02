"""Contract tests for POST /api/{user_id}/tasks endpoint.

Tests API contract compliance for task creation including:
- Valid task creation (201 Created)
- Invalid data validation (422 Unprocessable Entity)
- Missing required fields
- Location header presence
- Response schema validation
"""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_create_task_success(test_user: User, test_token: str, test_db_session_with_user):
    """Test successful task creation returns 201 with correct response format."""
    user_id = str(test_user.id)
    task_data = {
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    # Assert Location header is present
    assert "Location" in response.headers, "Location header missing"
    location = response.headers["Location"]
    assert location.startswith(f"/api/{user_id}/tasks/"), f"Invalid Location header: {location}"

    # Assert response body matches TaskResponse schema
    data = response.json()
    assert "id" in data, "Missing 'id' field"
    assert "user_id" in data, "Missing 'user_id' field"
    assert "title" in data, "Missing 'title' field"
    assert "description" in data, "Missing 'description' field"
    assert "status" in data, "Missing 'status' field"
    assert "created_at" in data, "Missing 'created_at' field"
    assert "updated_at" in data, "Missing 'updated_at' field"

    # Assert field values
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["user_id"] == user_id
    assert data["status"] == "pending"  # Default status

    # Assert id is valid UUID
    try:
        UUID(data["id"])
    except ValueError:
        pytest.fail(f"Invalid UUID format for id: {data['id']}")


@pytest.mark.asyncio
async def test_create_task_missing_title(test_user: User, test_token: str, test_db_session_with_user):
    """Test task creation without title returns 422."""
    user_id = str(test_user.id)
    task_data = {
        "description": "Missing title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Assert error response format (RFC 7807 or FastAPI validation error)
    data = response.json()
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_create_task_empty_title(test_user: User, test_token: str, test_db_session_with_user):
    """Test task creation with empty title returns 422."""
    user_id = str(test_user.id)
    task_data = {
        "title": "",
        "description": "Empty title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_task_title_too_long(test_user: User, test_token: str, test_db_session_with_user):
    """Test task creation with title exceeding 200 characters returns 422."""
    user_id = str(test_user.id)
    task_data = {
        "title": "x" * 201,  # 201 characters
        "description": "Title too long",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_task_description_too_long(test_user: User, test_token: str, test_db_session_with_user):
    """Test task creation with description exceeding 2000 characters returns 422."""
    user_id = str(test_user.id)
    task_data = {
        "title": "Valid title",
        "description": "x" * 2001,  # 2001 characters
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_task_invalid_user_id_format(test_token: str):
    """Test task creation with invalid user_id format returns 422."""
    user_id = "invalid-uuid"
    task_data = {
        "title": "Valid title",
        "description": "Valid description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_create_task_without_description(test_user: User, test_token: str, test_db_session_with_user):
    """Test task creation without description (optional field) succeeds."""
    user_id = str(test_user.id)
    task_data = {
        "title": "Task without description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    # Assert description is None
    data = response.json()
    assert data["description"] is None, "Description should be None when not provided"
