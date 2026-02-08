"""Contract tests for GET /api/{user_id}/tasks endpoint with pagination.

Tests API contract compliance for task listing including:
- Default pagination behavior
- Custom offset and limit parameters
- Pagination metadata (total, has_next, has_previous)
- Empty list handling
- Parameter validation (limit max 100, offset >= 0)
- Response schema validation
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_list_tasks_default_pagination(test_user: User, test_token: str, test_db_session_with_user):
    """Test listing tasks with default pagination returns 200 with correct format."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body matches PaginatedTaskResponse schema
    data = response.json()
    assert "items" in data, "Missing 'items' field"
    assert "total" in data, "Missing 'total' field"
    assert "offset" in data, "Missing 'offset' field"
    assert "limit" in data, "Missing 'limit' field"
    assert "has_next" in data, "Missing 'has_next' field"
    assert "has_previous" in data, "Missing 'has_previous' field"

    # Assert items is a list
    assert isinstance(data["items"], list), "items should be a list"

    # Assert default pagination values
    assert data["offset"] == 0, "Default offset should be 0"
    assert data["limit"] == 20, "Default limit should be 20"


@pytest.mark.asyncio
async def test_list_tasks_custom_pagination(test_user: User, test_token: str, test_db_session_with_user):
    """Test listing tasks with custom offset and limit."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 10, "limit": 5},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert pagination parameters are respected
    data = response.json()
    assert data["offset"] == 10, "Offset should be 10"
    assert data["limit"] == 5, "Limit should be 5"


@pytest.mark.asyncio
async def test_list_tasks_pagination_metadata(test_user: User, test_token: str, test_db_session_with_user):
    """Test pagination metadata calculation (has_next, has_previous)."""
    user_id = str(test_user.id)

    # First page (offset=0, limit=10)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    assert response.status_code == 200
    data = response.json()

    # Assert has_previous is False on first page
    assert data["has_previous"] is False, "has_previous should be False on first page"

    # has_next depends on total count (will be tested in integration tests)
    assert isinstance(data["has_next"], bool), "has_next should be a boolean"


@pytest.mark.asyncio
async def test_list_tasks_empty_list(test_user: User, test_token: str, test_db_session_with_user):
    """Test listing tasks when user has no tasks returns empty list."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert empty list
    data = response.json()
    assert data["items"] == [], "items should be empty list"
    assert data["total"] == 0, "total should be 0"
    assert data["has_next"] is False, "has_next should be False"
    assert data["has_previous"] is False, "has_previous should be False"


@pytest.mark.asyncio
async def test_list_tasks_limit_validation_max(test_user: User, test_token: str, test_db_session_with_user):
    """Test limit parameter validation - max 100."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"limit": 101},  # Exceeds max
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_list_tasks_limit_validation_min(test_user: User, test_token: str, test_db_session_with_user):
    """Test limit parameter validation - min 1."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"limit": 0},  # Below min
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_list_tasks_offset_validation(test_user: User, test_token: str, test_db_session_with_user):
    """Test offset parameter validation - must be >= 0."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": -1},  # Negative offset
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_list_tasks_invalid_user_id_format(test_token: str):
    """Test listing tasks with invalid user_id format returns 422."""
    user_id = "invalid-uuid"

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_list_tasks_response_item_schema(test_user: User, test_token: str, test_db_session_with_user):
    """Test that each item in the list matches TaskResponse schema."""
    user_id = str(test_user.id)

    # Create a task first
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Test task", "description": "Test description"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # List tasks
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    assert response.status_code == 200
    data = response.json()

    # Assert at least one task exists
    assert len(data["items"]) > 0, "Should have at least one task"

    # Assert first item has all required fields
    task = data["items"][0]
    assert "id" in task, "Missing 'id' field in task"
    assert "user_id" in task, "Missing 'user_id' field in task"
    assert "title" in task, "Missing 'title' field in task"
    assert "description" in task, "Missing 'description' field in task"
    assert "status" in task, "Missing 'status' field in task"
    assert "created_at" in task, "Missing 'created_at' field in task"
    assert "updated_at" in task, "Missing 'updated_at' field in task"
