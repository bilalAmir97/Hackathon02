"""Integration tests for protected API endpoints with authentication.

Tests complete authentication and authorization flows for protected endpoints including:
- Protected endpoint access with valid JWT tokens
- User isolation enforcement (users can only access their own data)
- Authorization header validation
- User ID matching between token and path parameter

These tests verify the integration between:
- JWT authentication middleware (src/middleware/jwt_auth.py)
- FastAPI dependencies (src/dependencies.py - get_current_user)
- Protected API routes (src/api/routes/tasks.py)
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.domain.models import User, UserStatus
from src.main import app


class TestProtectedEndpointAccess:
    """Test protected endpoint access with valid JWT tokens (T038)."""

    @pytest.mark.asyncio
    async def test_get_tasks_with_valid_token_returns_200(self, test_db_session):
        """Test that GET /api/{user_id}/tasks with valid token returns 200.

        Verifies FR-006, FR-007, FR-008, FR-009: System MUST verify JWT token and allow
        access to protected endpoints for authenticated users.
        """
        # Step 1: Create a test user in database
        user = User(
            id=uuid4(),
            email="validuser@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Step 2: Create a valid JWT token for this user
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Make authenticated request to protected endpoint
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user.id}/tasks",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Step 4: Verify successful response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Step 5: Verify response is a paginated response with items list
        data = response.json()
        assert "items" in data, "Response should contain 'items' field"
        assert isinstance(data["items"], list), "Items should be a list of tasks"
        assert "total" in data, "Response should contain 'total' field"
        assert "limit" in data, "Response should contain 'limit' field"
        assert "offset" in data, "Response should contain 'offset' field"

    @pytest.mark.asyncio
    async def test_post_task_with_valid_token_returns_201(self, test_db_session):
        """Test that POST /api/{user_id}/tasks with valid token returns 201.

        Verifies FR-016: System MUST automatically associate created data with authenticated user.
        """
        # Step 1: Create a test user
        user = User(
            id=uuid4(),
            email="createtask@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Step 2: Create a valid JWT token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Create a task via authenticated request
        task_data = {
            "title": "Test Task",
            "description": "Test Description",
        }

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"},
            )

        # Step 4: Verify successful creation
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        # Step 5: Verify task is associated with authenticated user
        created_task = response.json()
        assert created_task["user_id"] == str(user.id), "Task should be associated with authenticated user"
        assert created_task["title"] == task_data["title"], "Task title should match"

    @pytest.mark.asyncio
    async def test_get_task_by_id_with_valid_token_returns_200(self, test_db_session):
        """Test that GET /api/{user_id}/tasks/{task_id} with valid token returns 200.

        Verifies that authenticated users can access their own task details.
        """
        # Step 1: Create a test user
        user = User(
            id=uuid4(),
            email="gettask@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Step 2: Create a valid JWT token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Create a task first
        task_data = {"title": "Task to Get", "description": "Description"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                f"/api/{user.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            assert create_response.status_code == 201, "Task creation should succeed"
            task_id = create_response.json()["id"]

            # Step 4: Get the task by ID
            get_response = await client.get(
                f"/api/{user.id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Step 5: Verify successful retrieval
        assert get_response.status_code == 200, f"Expected 200, got {get_response.status_code}"
        task = get_response.json()
        assert task["id"] == task_id, "Task ID should match"
        assert task["user_id"] == str(user.id), "Task should belong to authenticated user"

    @pytest.mark.asyncio
    async def test_update_task_with_valid_token_returns_200(self, test_db_session):
        """Test that PUT /api/{user_id}/tasks/{task_id} with valid token returns 200.

        Verifies that authenticated users can update their own tasks.
        """
        # Step 1: Create a test user
        user = User(
            id=uuid4(),
            email="updatetask@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Step 2: Create a valid JWT token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Create a task first
        task_data = {"title": "Original Title", "description": "Original Description"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                f"/api/{user.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            task_id = create_response.json()["id"]

            # Step 4: Update the task
            update_data = {"title": "Updated Title", "description": "Updated Description", "status": "completed"}
            update_response = await client.put(
                f"/api/{user.id}/tasks/{task_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {token}"},
            )

        # Step 5: Verify successful update
        assert update_response.status_code == 200, f"Expected 200, got {update_response.status_code}"
        updated_task = update_response.json()
        assert updated_task["title"] == "Updated Title", "Task title should be updated"
        assert updated_task["status"] == "completed", "Task status should be updated to completed"

    @pytest.mark.asyncio
    async def test_delete_task_with_valid_token_returns_204(self, test_db_session):
        """Test that DELETE /api/{user_id}/tasks/{task_id} with valid token returns 204.

        Verifies that authenticated users can delete their own tasks.
        """
        # Step 1: Create a test user
        user = User(
            id=uuid4(),
            email="deletetask@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Step 2: Create a valid JWT token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Create a task first
        task_data = {"title": "Task to Delete", "description": "Description"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                f"/api/{user.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token}"},
            )
            task_id = create_response.json()["id"]

            # Step 4: Delete the task
            delete_response = await client.delete(
                f"/api/{user.id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

        # Step 5: Verify successful deletion
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}"


class TestUserIsolationEnforcement:
    """Test user isolation enforcement (T039)."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_access_user_b_tasks(self, test_db_session):
        """Test that User A token cannot access User B's tasks.

        Verifies FR-010, FR-015: System MUST enforce user_id match and prevent cross-user access.
        """
        # Step 1: Create User A
        user_a = User(
            id=uuid4(),
            email="usera@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_a)

        # Step 2: Create User B
        user_b = User(
            id=uuid4(),
            email="userb@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_b)
        await test_db_session.commit()
        await test_db_session.refresh(user_a)
        await test_db_session.refresh(user_b)

        # Step 3: Create JWT token for User A
        token_a = jwt.encode(
            {
                "sub": str(user_a.id),
                "user_id": str(user_a.id),
                "email": user_a.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        # Step 4: User A attempts to access User B's tasks
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                f"/api/{user_b.id}/tasks",  # User B's endpoint
                headers={"Authorization": f"Bearer {token_a}"},  # User A's token
            )

        # Step 5: Verify access is denied with 401 Unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

        # Step 6: Verify error response format
        error_data = response.json()
        assert "error" in error_data, "Error response must contain 'error' field"

        # Step 7: Verify error message indicates unauthorized access
        error_msg = error_data["error"].lower()
        assert "unauthorized" in error_msg or "cannot access" in error_msg or "mismatch" in error_msg

    @pytest.mark.asyncio
    async def test_user_a_cannot_create_task_for_user_b(self, test_db_session):
        """Test that User A token cannot create tasks for User B.

        Verifies that user isolation is enforced on POST operations.
        """
        # Step 1: Create User A and User B
        user_a = User(
            id=uuid4(),
            email="usera_create@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        user_b = User(
            id=uuid4(),
            email="userb_create@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_a)
        test_db_session.add(user_b)
        await test_db_session.commit()
        await test_db_session.refresh(user_a)
        await test_db_session.refresh(user_b)

        # Step 2: Create JWT token for User A
        token_a = jwt.encode(
            {
                "sub": str(user_a.id),
                "user_id": str(user_a.id),
                "email": user_a.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        # Step 3: User A attempts to create task for User B
        task_data = {"title": "Malicious Task", "description": "Should not be created"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                f"/api/{user_b.id}/tasks",  # User B's endpoint
                json=task_data,
                headers={"Authorization": f"Bearer {token_a}"},  # User A's token
            )

        # Step 4: Verify access is denied with 401 Unauthorized
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_user_a_cannot_update_user_b_task(self, test_db_session):
        """Test that User A token cannot update User B's tasks.

        Verifies that user isolation is enforced on PUT operations.
        """
        # Step 1: Create User A and User B
        user_a = User(
            id=uuid4(),
            email="usera_update@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        user_b = User(
            id=uuid4(),
            email="userb_update@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_a)
        test_db_session.add(user_b)
        await test_db_session.commit()
        await test_db_session.refresh(user_a)
        await test_db_session.refresh(user_b)

        # Step 2: Create tokens for both users
        token_a = jwt.encode(
            {
                "sub": str(user_a.id),
                "user_id": str(user_a.id),
                "email": user_a.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        token_b = jwt.encode(
            {
                "sub": str(user_b.id),
                "user_id": str(user_b.id),
                "email": user_b.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        # Step 3: User B creates a task
        task_data = {"title": "User B Task", "description": "Belongs to User B"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                f"/api/{user_b.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token_b}"},
            )
            task_id = create_response.json()["id"]

            # Step 4: User A attempts to update User B's task
            update_data = {"title": "Hacked Title", "description": "Malicious update", "completed": True}
            update_response = await client.put(
                f"/api/{user_b.id}/tasks/{task_id}",
                json=update_data,
                headers={"Authorization": f"Bearer {token_a}"},  # User A's token
            )

        # Step 5: Verify access is denied with 401 Unauthorized
        assert update_response.status_code == 401, f"Expected 401, got {update_response.status_code}"

    @pytest.mark.asyncio
    async def test_user_a_cannot_delete_user_b_task(self, test_db_session):
        """Test that User A token cannot delete User B's tasks.

        Verifies that user isolation is enforced on DELETE operations.
        """
        # Step 1: Create User A and User B
        user_a = User(
            id=uuid4(),
            email="usera_delete@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        user_b = User(
            id=uuid4(),
            email="userb_delete@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_a)
        test_db_session.add(user_b)
        await test_db_session.commit()
        await test_db_session.refresh(user_a)
        await test_db_session.refresh(user_b)

        # Step 2: Create tokens for both users
        token_a = jwt.encode(
            {
                "sub": str(user_a.id),
                "user_id": str(user_a.id),
                "email": user_a.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        token_b = jwt.encode(
            {
                "sub": str(user_b.id),
                "user_id": str(user_b.id),
                "email": user_b.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        # Step 3: User B creates a task
        task_data = {"title": "User B Task", "description": "Should not be deleted by User A"}

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            create_response = await client.post(
                f"/api/{user_b.id}/tasks",
                json=task_data,
                headers={"Authorization": f"Bearer {token_b}"},
            )
            task_id = create_response.json()["id"]

            # Step 4: User A attempts to delete User B's task
            delete_response = await client.delete(
                f"/api/{user_b.id}/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token_a}"},  # User A's token
            )

        # Step 5: Verify access is denied with 401 Unauthorized
        assert delete_response.status_code == 401, f"Expected 401, got {delete_response.status_code}"

    @pytest.mark.asyncio
    async def test_user_can_only_see_own_tasks(self, test_db_session):
        """Test that users can only see their own tasks in list view.

        Verifies that task listing is filtered by authenticated user_id.
        """
        # Step 1: Create User A and User B
        user_a = User(
            id=uuid4(),
            email="usera_list@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        user_b = User(
            id=uuid4(),
            email="userb_list@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user_a)
        test_db_session.add(user_b)
        await test_db_session.commit()
        await test_db_session.refresh(user_a)
        await test_db_session.refresh(user_b)

        # Step 2: Create tokens for both users
        token_a = jwt.encode(
            {
                "sub": str(user_a.id),
                "user_id": str(user_a.id),
                "email": user_a.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        token_b = jwt.encode(
            {
                "sub": str(user_b.id),
                "user_id": str(user_b.id),
                "email": user_b.email,
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            },
            settings.better_auth_secret,
            algorithm="HS256",
        )

        # Step 3: User A creates tasks
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post(
                f"/api/{user_a.id}/tasks",
                json={"title": "User A Task 1", "description": "Task 1"},
                headers={"Authorization": f"Bearer {token_a}"},
            )
            await client.post(
                f"/api/{user_a.id}/tasks",
                json={"title": "User A Task 2", "description": "Task 2"},
                headers={"Authorization": f"Bearer {token_a}"},
            )

            # Step 4: User B creates tasks
            await client.post(
                f"/api/{user_b.id}/tasks",
                json={"title": "User B Task 1", "description": "Task 1"},
                headers={"Authorization": f"Bearer {token_b}"},
            )

            # Step 5: User A lists their tasks
            response_a = await client.get(
                f"/api/{user_a.id}/tasks",
                headers={"Authorization": f"Bearer {token_a}"},
            )

        # Step 6: Verify User A only sees their own tasks
        assert response_a.status_code == 200, "User A should be able to list their tasks"
        data_a = response_a.json()
        assert "items" in data_a, "Response should contain 'items' field"
        tasks_a = data_a["items"]
        assert len(tasks_a) == 2, "User A should see exactly 2 tasks"

        # Verify all tasks belong to User A
        for task in tasks_a:
            assert task["user_id"] == str(user_a.id), "All tasks should belong to User A"
            assert "User A" in task["title"], "Task titles should indicate User A ownership"
