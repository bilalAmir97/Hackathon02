"""Contract tests for PUT /api/{user_id}/tasks/{task_id} endpoint.

Tests API contract compliance for task updates including:
- Successful full update (200 OK)
- Partial updates (title, description, status)
- Update non-existent task (404)
- Update unauthorized task (404)
- Invalid data validation (422)
- At least one field required (422)
"""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_update_task_success_full(test_user: User, test_token: str, test_db_session_with_user):
    """Test successful full task update returns 200 with updated data."""
    user_id = str(test_user.id)

    # First create a task
    create_data = {
        "title": "Original title",
        "description": "Original description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Now update the task
        update_data = {
            "title": "Updated title",
            "description": "Updated description",
            "status": "completed",
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body
    data = response.json()
    assert data["id"] == task_id
    assert data["user_id"] == user_id
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["status"] == update_data["status"]
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_update_task_partial_title_only(test_user: User, test_token: str, test_db_session_with_user):
    """Test partial update with only title field."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
        "description": "Original description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        original_description = create_response.json()["description"]
        original_status = create_response.json()["status"]

        # Update only title
        update_data = {
            "title": "Updated title only",
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert only title changed
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == original_description  # Unchanged
    assert data["status"] == original_status  # Unchanged


@pytest.mark.asyncio
async def test_update_task_partial_description_only(test_user: User, test_token: str, test_db_session_with_user):
    """Test partial update with only description field."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
        "description": "Original description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        original_title = create_response.json()["title"]
        original_status = create_response.json()["status"]

        # Update only description
        update_data = {
            "description": "Updated description only",
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert only description changed
    data = response.json()
    assert data["title"] == original_title  # Unchanged
    assert data["description"] == update_data["description"]
    assert data["status"] == original_status  # Unchanged


@pytest.mark.asyncio
async def test_update_task_partial_status_only(test_user: User, test_token: str, test_db_session_with_user):
    """Test partial update with only status field."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
        "description": "Original description",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        original_title = create_response.json()["title"]
        original_description = create_response.json()["description"]

        # Update only status
        update_data = {
            "status": "completed",
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert only status changed
    data = response.json()
    assert data["title"] == original_title  # Unchanged
    assert data["description"] == original_description  # Unchanged
    assert data["status"] == update_data["status"]


@pytest.mark.asyncio
async def test_update_task_not_found(test_user: User, test_token: str, test_db_session_with_user):
    """Test updating non-existent task returns 404."""
    user_id = str(test_user.id)
    task_id = str(uuid4())  # Non-existent task

    update_data = {
        "title": "Updated title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data or "title" in data, "Missing error details"


@pytest.mark.asyncio
async def test_update_task_unauthorized(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test updating task owned by another user returns 404."""
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

        # Try to update as user 2
        update_data = {
            "title": "Hacked title",
        }

        response = await client.put(
            f"/api/{user_id_2}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token_2}"},
        )

    # Assert status code (404 for timing attack prevention)
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_update_task_invalid_title_too_long(test_user: User, test_token: str, test_db_session_with_user):
    """Test updating task with title exceeding 200 characters returns 422."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Update with invalid title
        update_data = {
            "title": "x" * 201,  # 201 characters
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_update_task_invalid_status(test_user: User, test_token: str, test_db_session_with_user):
    """Test updating task with invalid status returns 422."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Update with invalid status
        update_data = {
            "status": "invalid_status",
        }

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_update_task_no_fields_provided(test_user: User, test_token: str, test_db_session_with_user):
    """Test updating task with no fields returns 422."""
    user_id = str(test_user.id)

    # Create a task
    create_data = {
        "title": "Original title",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=create_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Update with no fields
        update_data = {}

        response = await client.put(
            f"/api/{user_id}/tasks/{task_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

    # Assert status code (422 - at least one field required)
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
