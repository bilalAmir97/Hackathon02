"""Integration tests for task lifecycle: create-then-retrieve journey.

Tests the complete workflow of creating a task and retrieving it,
including user isolation and data consistency.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.domain.models import User
from src.main import app


@pytest.mark.asyncio
async def test_create_then_retrieve_task(test_user: User, test_token: str, test_db_session_with_user):
    """Test complete workflow: create a task and retrieve it by ID.

    Verifies that:
    - Task can be created successfully
    - Created task can be retrieved by ID
    - All fields match between creation and retrieval
    - Timestamps are consistent
    """
    user_id = str(test_user.id)
    task_data = {
        "title": "Complete project documentation",
        "description": "Write comprehensive API documentation with examples",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Create task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert create_response.status_code == 201, f"Create failed: {create_response.text}"
        created_task = create_response.json()
        task_id = created_task["id"]

        # Step 2: Retrieve task
        get_response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )

        assert get_response.status_code == 200, f"Retrieve failed: {get_response.text}"
        retrieved_task = get_response.json()

    # Step 3: Verify all fields match
    assert retrieved_task["id"] == created_task["id"], "Task ID mismatch"
    assert retrieved_task["user_id"] == created_task["user_id"], "User ID mismatch"
    assert retrieved_task["title"] == created_task["title"], "Title mismatch"
    assert retrieved_task["description"] == created_task["description"], "Description mismatch"
    assert retrieved_task["status"] == created_task["status"], "Status mismatch"
    assert retrieved_task["created_at"] == created_task["created_at"], "Created timestamp mismatch"
    assert retrieved_task["updated_at"] == created_task["updated_at"], "Updated timestamp mismatch"

    # Step 4: Verify field values
    assert retrieved_task["title"] == task_data["title"]
    assert retrieved_task["description"] == task_data["description"]
    assert retrieved_task["user_id"] == user_id
    assert retrieved_task["status"] == "pending"


@pytest.mark.asyncio
async def test_user_isolation_create_and_retrieve(test_user: User, test_user_2: User, test_token: str, test_token_2: str, test_db_session_with_two_users):
    """Test that users can only retrieve their own tasks.

    Verifies that:
    - User A can create a task
    - User A can retrieve their own task
    - User B cannot retrieve User A's task (404 response)
    - No information leakage about task existence
    """
    user_a_id = str(test_user.id)
    user_b_id = str(test_user_2.id)

    task_data = {
        "title": "User A's private task",
        "description": "This should not be accessible to User B",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # User A creates a task
        create_response = await client.post(
            f"/api/{user_a_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]

        # User A can retrieve their own task
        user_a_get_response = await client.get(
            f"/api/{user_a_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert user_a_get_response.status_code == 200, "User A should access their own task"

        # User B cannot retrieve User A's task
        user_b_get_response = await client.get(
            f"/api/{user_b_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token_2}"},
        )
        assert user_b_get_response.status_code == 404, "User B should get 404 for User A's task"

        # Verify error response doesn't leak information
        error_data = user_b_get_response.json()
        assert "detail" in error_data
        # Should not reveal whether task exists or belongs to another user


@pytest.mark.asyncio
async def test_create_multiple_tasks_and_retrieve_each(test_user: User, test_token: str, test_db_session_with_user):
    """Test creating multiple tasks and retrieving each individually.

    Verifies that:
    - Multiple tasks can be created for the same user
    - Each task has a unique ID
    - Each task can be retrieved independently
    - Task data remains isolated and correct
    """
    user_id = str(test_user.id)

    tasks_data = [
        {"title": "Task 1", "description": "First task"},
        {"title": "Task 2", "description": "Second task"},
        {"title": "Task 3", "description": "Third task"},
    ]

    created_tasks = []

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create all tasks
        for task_data in tasks_data:
            create_response = await client.post(
                f"/api/{user_id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {test_token}"},
            )
            assert create_response.status_code == 201
            created_tasks.append(create_response.json())

        # Verify all tasks have unique IDs
        task_ids = [task["id"] for task in created_tasks]
        assert len(task_ids) == len(set(task_ids)), "Task IDs should be unique"

        # Retrieve and verify each task
        for i, created_task in enumerate(created_tasks):
            task_id = created_task["id"]
            get_response = await client.get(
                f"/api/{user_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {test_token}"},
            )

            assert get_response.status_code == 200
            retrieved_task = get_response.json()

            # Verify task data matches
            assert retrieved_task["id"] == created_task["id"]
            assert retrieved_task["title"] == tasks_data[i]["title"]
            assert retrieved_task["description"] == tasks_data[i]["description"]


@pytest.mark.asyncio
async def test_create_task_without_description_and_retrieve(test_user: User, test_token: str, test_db_session_with_user):
    """Test creating a task without description and retrieving it.

    Verifies that:
    - Tasks can be created without optional description field
    - Retrieved task has description as None
    - All other fields are populated correctly
    """
    user_id = str(test_user.id)
    task_data = {
        "title": "Task without description",
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
        get_response = await client.get(
            f"/api/{user_id}/tasks/{task_id}",
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert get_response.status_code == 200
        retrieved_task = get_response.json()

    # Verify description is None
    assert retrieved_task["description"] is None
    assert created_task["description"] is None

    # Verify other fields are correct
    assert retrieved_task["title"] == task_data["title"]
    assert retrieved_task["status"] == "pending"


@pytest.mark.asyncio
async def test_data_persistence_across_requests(test_user: User, test_token: str, test_db_session_with_user):
    """Test that task data persists correctly across multiple requests.

    Verifies that:
    - Created task data is stored persistently
    - Multiple retrievals return consistent data
    - No data corruption or loss
    """
    user_id = str(test_user.id)
    task_data = {
        "title": "Persistent task",
        "description": "This task should persist across requests",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create task
        create_response = await client.post(
            f"/api/{user_id}/tasks",
            json=task_data,
            headers={"Authorization": f"Bearer {test_token}"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Retrieve task multiple times
        for _ in range(3):
            get_response = await client.get(
                f"/api/{user_id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {test_token}"},
            )
            assert get_response.status_code == 200

            retrieved_task = get_response.json()
            assert retrieved_task["title"] == task_data["title"]
            assert retrieved_task["description"] == task_data["description"]
            assert retrieved_task["status"] == "pending"
