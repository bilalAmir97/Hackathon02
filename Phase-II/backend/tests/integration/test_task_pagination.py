"""Integration tests for task pagination navigation.

Tests pagination behavior with real database operations including:
- Creating 25 tasks and navigating through pages
- Verifying has_next and has_previous flags
- Verifying total count accuracy
- Testing edge cases (offset beyond total)
- Verifying correct ordering (newest first)
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_pagination_navigate_through_pages(test_user: User, test_token: str, test_db_session_with_user):
    """Test navigating through multiple pages of tasks."""
    user_id = str(test_user.id)

    # Create 25 tasks
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for i in range(25):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}", "description": f"Description {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Page 1: offset=0, limit=10
        response_page1 = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page1.status_code == 200
        data_page1 = response_page1.json()

        # Verify page 1 data
        assert len(data_page1["items"]) == 10, "Page 1 should have 10 items"
        assert data_page1["total"] == 25, "Total should be 25"
        assert data_page1["offset"] == 0, "Offset should be 0"
        assert data_page1["limit"] == 10, "Limit should be 10"
        assert data_page1["has_previous"] is False, "Page 1 should not have previous"
        assert data_page1["has_next"] is True, "Page 1 should have next (25 > 10)"

        # Page 2: offset=10, limit=10
        response_page2 = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 10, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page2.status_code == 200
        data_page2 = response_page2.json()

        # Verify page 2 data
        assert len(data_page2["items"]) == 10, "Page 2 should have 10 items"
        assert data_page2["total"] == 25, "Total should be 25"
        assert data_page2["offset"] == 10, "Offset should be 10"
        assert data_page2["limit"] == 10, "Limit should be 10"
        assert data_page2["has_previous"] is True, "Page 2 should have previous"
        assert data_page2["has_next"] is True, "Page 2 should have next (25 > 20)"

        # Page 3: offset=20, limit=10
        response_page3 = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 20, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page3.status_code == 200
        data_page3 = response_page3.json()

        # Verify page 3 data (last page with 5 items)
        assert len(data_page3["items"]) == 5, "Page 3 should have 5 items (25 - 20)"
        assert data_page3["total"] == 25, "Total should be 25"
        assert data_page3["offset"] == 20, "Offset should be 20"
        assert data_page3["limit"] == 10, "Limit should be 10"
        assert data_page3["has_previous"] is True, "Page 3 should have previous"
        assert data_page3["has_next"] is False, "Page 3 should not have next (last page)"


@pytest.mark.asyncio
async def test_pagination_offset_beyond_total(test_user: User, test_token: str, test_db_session_with_user):
    """Test pagination when offset is beyond total count."""
    user_id = str(test_user.id)

    # Create 5 tasks
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for i in range(5):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Request offset=10 when only 5 tasks exist
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 10, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return empty items but valid pagination metadata
        assert len(data["items"]) == 0, "Should return empty list"
        assert data["total"] == 5, "Total should still be 5"
        assert data["offset"] == 10, "Offset should be 10"
        assert data["has_previous"] is True, "Should have previous (offset > 0)"
        assert data["has_next"] is False, "Should not have next"


@pytest.mark.asyncio
async def test_pagination_exact_page_boundary(test_user: User, test_token: str, test_db_session_with_user):
    """Test pagination when total is exactly divisible by limit."""
    user_id = str(test_user.id)

    # Create exactly 20 tasks
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for i in range(20):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Page 1: offset=0, limit=10
        response_page1 = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 0, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page1.status_code == 200
        data_page1 = response_page1.json()

        assert len(data_page1["items"]) == 10
        assert data_page1["total"] == 20
        assert data_page1["has_next"] is True, "Should have next page"

        # Page 2: offset=10, limit=10 (last page)
        response_page2 = await client.get(
            f"/api/{user_id}/tasks",
            params={"offset": 10, "limit": 10},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response_page2.status_code == 200
        data_page2 = response_page2.json()

        assert len(data_page2["items"]) == 10
        assert data_page2["total"] == 20
        assert data_page2["has_next"] is False, "Should not have next page (exactly at boundary)"


@pytest.mark.asyncio
async def test_pagination_single_item(test_user: User, test_token: str, test_db_session_with_user):
    """Test pagination with only one task."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 1 task
        await client.post(
            f"/api/{user_id}/tasks",
            json={"title": "Single task"},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        # Request with default pagination
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1, "Should have 1 item"
        assert data["total"] == 1, "Total should be 1"
        assert data["has_previous"] is False, "Should not have previous"
        assert data["has_next"] is False, "Should not have next"


@pytest.mark.asyncio
async def test_pagination_ordering_newest_first(test_user: User, test_token: str, test_db_session_with_user):
    """Test that tasks are ordered by created_at DESC (newest first)."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create tasks in sequence
        task_ids = []
        for i in range(5):
            response = await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )
            task_ids.append(response.json()["id"])

        # List tasks
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify newest task is first
        assert len(data["items"]) == 5
        # The last created task should be first in the list
        assert data["items"][0]["id"] == task_ids[-1], "Newest task should be first"
        assert data["items"][-1]["id"] == task_ids[0], "Oldest task should be last"


@pytest.mark.asyncio
async def test_pagination_user_isolation(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test that pagination only returns tasks for the specified user."""
    user1_id = str(test_user.id)
    user2_id = str(test_user_2.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 10 tasks for user1
        for i in range(10):
            await client.post(
                f"/api/{user1_id}/tasks",
                json={"title": f"User1 Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Create 5 tasks for user2
        for i in range(5):
            await client.post(
                f"/api/{user2_id}/tasks",
                json={"title": f"User2 Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token_2}"},
            )

        # List tasks for user1
        response_user1 = await client.get(
            f"/api/{user1_id}/tasks",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        data_user1 = response_user1.json()

        # List tasks for user2
        response_user2 = await client.get(
            f"/api/{user2_id}/tasks",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )
        data_user2 = response_user2.json()

        # Verify user isolation
        assert data_user1["total"] == 10, "User1 should have 10 tasks"
        assert data_user2["total"] == 5, "User2 should have 5 tasks"

        # Verify all tasks belong to correct user
        for task in data_user1["items"]:
            assert task["user_id"] == user1_id, "All tasks should belong to user1"

        for task in data_user2["items"]:
            assert task["user_id"] == user2_id, "All tasks should belong to user2"


@pytest.mark.asyncio
async def test_pagination_large_limit(test_user: User, test_token: str, test_db_session_with_user):
    """Test pagination with limit=100 (maximum allowed)."""
    user_id = str(test_user.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create 50 tasks
        for i in range(50):
            await client.post(
                f"/api/{user_id}/tasks",
                json={"title": f"Task {i + 1}"},
                headers={"Authorization": f"Bearer {test_token}"},
            )

        # Request with limit=100
        response = await client.get(
            f"/api/{user_id}/tasks",
            params={"limit": 100},
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert response.status_code == 200
        data = response.json()

        # Should return all 50 tasks
        assert len(data["items"]) == 50, "Should return all 50 tasks"
        assert data["total"] == 50
        assert data["limit"] == 100
        assert data["has_next"] is False, "Should not have next page"
