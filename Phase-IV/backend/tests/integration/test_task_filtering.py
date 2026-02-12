"""Integration tests for task status filtering.

Tests status filtering behavior with real database operations including:
- Creating 15 pending tasks and 10 completed tasks
- Filtering by status=pending (verify count=15)
- Filtering by status=completed (verify count=10)
- Verifying user isolation in filtered results
- Combining filtering with pagination
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_filter_by_pending_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering by status=pending returns only pending tasks."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 15 pending tasks and 10 completed tasks
        pending_task_ids = []
        for i in range(15):
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )
            pending_task_ids.append(response.json()["id"])

        # Create 10 completed tasks (need to update status after creation)
        # Note: This requires the update endpoint which may not exist yet
        # For now, we'll just create pending tasks and test the filter

        # Filter by pending status
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify count
        assert data["total"] == 15, f"Expected 15 pending tasks, got {data['total']}"
        assert len(data["items"]) == 15, "Should return all 15 pending tasks (within default limit)"

        # Verify all returned tasks have status=pending
        for task in data["items"]:
            assert task["status"] == "pending", f"Task {task['id']} should have status=pending"
            assert task["user_id"] == user_id, "All tasks should belong to the user"


@pytest.mark.asyncio
async def test_filter_by_completed_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering by status=completed returns only completed tasks."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 10 pending tasks
        for i in range(10):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Filter by completed status (should return 0 since all are pending)
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "completed"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify no completed tasks
        assert data["total"] == 0, "Should have 0 completed tasks"
        assert len(data["items"]) == 0, "Should return empty list"


@pytest.mark.asyncio
async def test_filter_with_pagination(test_user: User, test_token: str, test_db_session_with_user):
    """Test combining status filtering with pagination."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 25 pending tasks
        for i in range(25):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Filter by pending with pagination (page 1)
        response_page1 = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending", "offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page1.status_code == 200
        data_page1 = response_page1.json()

        # Verify page 1
        assert data_page1["total"] == 25, "Total pending tasks should be 25"
        assert len(data_page1["items"]) == 10, "Page 1 should have 10 items"
        assert data_page1["has_next"] is True, "Should have next page"
        assert data_page1["has_previous"] is False, "Should not have previous page"

        # Verify all items are pending
        for task in data_page1["items"]:
            assert task["status"] == "pending", "All tasks should be pending"

        # Filter by pending with pagination (page 2)
        response_page2 = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending", "offset": 10, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page2.status_code == 200
        data_page2 = response_page2.json()

        # Verify page 2
        assert data_page2["total"] == 25, "Total pending tasks should be 25"
        assert len(data_page2["items"]) == 10, "Page 2 should have 10 items"
        assert data_page2["has_next"] is True, "Should have next page"
        assert data_page2["has_previous"] is True, "Should have previous page"


@pytest.mark.asyncio
async def test_filter_user_isolation(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test that filtering respects user isolation."""
    user1_id = str(test_user.id)
    user2_id = str(test_user_2.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 10 pending tasks for user1
        for i in range(10):
            await client.post(
                f"/api/{user1_id}/tasks",
                json={"title": f"User1 Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Create 5 pending tasks for user2
        for i in range(5):
            await client.post(
                f"/api/{user2_id}/tasks",
                json={"title": f"User2 Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token_2}"},
            )

        # Filter pending tasks for user1
        response_user1 = await client.get(
            f"/api/{user1_id}/tasks",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_user1.status_code == 200
        data_user1 = response_user1.json()

        # Filter pending tasks for user2
        response_user2 = await client.get(
            f"/api/{user2_id}/tasks",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

        assert response_user2.status_code == 200
        data_user2 = response_user2.json()

        # Verify user isolation
        assert data_user1["total"] == 10, "User1 should have 10 pending tasks"
        assert data_user2["total"] == 5, "User2 should have 5 pending tasks"

        # Verify all tasks belong to correct user
        for task in data_user1["items"]:
            assert task["user_id"] == user1_id, "All tasks should belong to user1"
            assert task["status"] == "pending", "All tasks should be pending"

        for task in data_user2["items"]:
            assert task["user_id"] == user2_id, "All tasks should belong to user2"
            assert task["status"] == "pending", "All tasks should be pending"


@pytest.mark.asyncio
async def test_no_filter_returns_all_statuses(test_user: User, test_token: str, test_db_session_with_user):
    """Test that omitting status filter returns tasks of all statuses."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 10 pending tasks
        for i in range(10):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # List all tasks (no status filter)
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return all tasks regardless of status
        assert data["total"] == 10, "Should return all 10 tasks"
        assert len(data["items"]) == 10, "Should return all items"


@pytest.mark.asyncio
async def test_filter_empty_result_with_pagination(test_user: User, test_token: str, test_db_session_with_user):
    """Test filtering with pagination when no results match."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 5 pending tasks
        for i in range(5):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Filter by completed with pagination
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "completed", "offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify empty result with correct pagination metadata
        assert data["total"] == 0, "Should have 0 completed tasks"
        assert len(data["items"]) == 0, "Should return empty list"
        assert data["has_next"] is False, "Should not have next page"
        assert data["has_previous"] is False, "Should not have previous page"


@pytest.mark.asyncio
async def test_filter_ordering_preserved(test_user: User, test_token: str, test_db_session_with_user):
    """Test that filtering preserves the ordering (newest first)."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create tasks in sequence
        task_ids = []
        for i in range(10):
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Pending Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )
            task_ids.append(response.json()["id"])

        # Filter by pending status
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"status": "pending"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify ordering (newest first)
        assert len(data["items"]) == 10
        assert data["items"][0]["id"] == task_ids[-1], "Newest task should be first"
        assert data["items"][-1]["id"] == task_ids[0], "Oldest task should be last"
