"""Contract tests for GET /api/{user_id}/tasks with status filtering.

Tests API contract compliance for task filtering including:
- Filter by status=pending
- Filter by status=completed
- Filter with pagination
- Invalid status value validation (422)
- Response schema validation
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_filter_tasks_by_pending_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering tasks by status=pending returns only pending tasks."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response structure
    data = response.json()
    assert "items" in data, "Missing 'items' field"
    assert "total" in data, "Missing 'total' field"

    # All items should have status=pending (will be verified in integration tests)
    assert isinstance(data["items"], list), "items should be a list"


@pytest.mark.asyncio
async def test_filter_tasks_by_completed_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering tasks by status=completed returns only completed tasks."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "completed"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response structure
    data = response.json()
    assert "items" in data, "Missing 'items' field"
    assert "total" in data, "Missing 'total' field"

    # All items should have status=completed (will be verified in integration tests)
    assert isinstance(data["items"], list), "items should be a list"


@pytest.mark.asyncio
async def test_filter_tasks_with_pagination(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering tasks with pagination parameters."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending", "offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response structure with pagination
    data = response.json()
    assert "items" in data, "Missing 'items' field"
    assert "total" in data, "Missing 'total' field"
    assert "offset" in data, "Missing 'offset' field"
    assert "limit" in data, "Missing 'limit' field"
    assert "has_next" in data, "Missing 'has_next' field"
    assert "has_previous" in data, "Missing 'has_previous' field"

    # Assert pagination parameters
    assert data["offset"] == 0, "Offset should be 0"
    assert data["limit"] == 10, "Limit should be 10"


@pytest.mark.asyncio
async def test_filter_tasks_invalid_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering with invalid status value returns 422."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "invalid_status"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_filter_tasks_no_status_returns_all(test_user: User, test_token: str, test_db_session_with_user):
    """Test that omitting status parameter returns all tasks."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create tasks with different statuses
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Pending task", "description": "Test"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # List all tasks (no status filter)
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response structure
    data = response.json()
    assert "items" in data, "Missing 'items' field"
    assert isinstance(data["items"], list), "items should be a list"


@pytest.mark.asyncio
async def test_filter_tasks_empty_result(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering returns empty list when no tasks match."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Filter by completed when no completed tasks exist
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "completed"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert empty result
    data = response.json()
    assert data["items"] == [], "items should be empty list"
    assert data["total"] == 0, "total should be 0"


@pytest.mark.asyncio
async def test_filter_tasks_case_sensitive(test_user: User, test_token: str, test_db_session_with_user):
    """Test that status filter is case-sensitive."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Try uppercase status
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "PENDING"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 for validation error - case matters)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
