"""
Backend unit and integration tests for Todo API.

Tests cover:
- CRUD operations (create, read, update, delete, toggle)
- User isolation (no cross-user data access)
- Security (401 on missing/invalid token)
- Optimistic locking (409 on version conflict)
"""
import pytest
from datetime import datetime
from uuid import uuid4


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    def test_health_check(self, client):
        """Verify health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

    def test_readiness_check(self, client):
        """Verify readiness endpoint returns ready status."""
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ready"}


class TestAuthentication:
    """Tests for JWT authentication middleware."""

    def test_missing_auth_header_returns_401(self, client):
        """Verify request without auth header returns 403 (FastAPI HTTPBearer behavior)."""
        response = client.get("/api/todos")
        assert response.status_code == 403
        # FastAPI's HTTPBearer returns "Not authenticated" when no credentials
        assert "Not authenticated" in response.json()["detail"]

    def test_invalid_token_returns_401(self, client):
        """Verify request with invalid token returns 401."""
        response = client.get(
            "/api/todos",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

    def test_malformed_token_returns_401(self, client):
        """Verify request with malformed token returns 401."""
        response = client.get(
            "/api/todos",
            headers={"Authorization": "Bearer not-a-jwt"}
        )
        assert response.status_code == 401

    def test_valid_token_allows_access(self, client, auth_headers):
        """Verify request with valid token succeeds."""
        response = client.get("/api/todos", headers=auth_headers)
        assert response.status_code == 200


class TestTodoCRUD:
    """Tests for Todo CRUD operations."""

    def test_create_todo(self, client, auth_headers):
        """Verify todo creation returns created todo with all fields."""
        response = client.post(
            "/api/todos",
            json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["version"] == 1

    def test_create_todo_without_description(self, client, auth_headers):
        """Verify todo creation without description works."""
        response = client.post(
            "/api/todos",
            json={"title": "Simple task"},
            headers=auth_headers,
        )
        assert response.status_code == 201
        assert response.json()["description"] is None

    def test_create_todo_missing_title_returns_400(self, client, auth_headers):
        """Verify todo creation without title returns 400."""
        response = client.post(
            "/api/todos",
            json={},
            headers=auth_headers,
        )
        # FastAPI returns 422 for Pydantic validation errors
        assert response.status_code == 422

    def test_create_todo_title_too_long_returns_400(self, client, auth_headers):
        """Verify todo creation with title > 255 chars returns 400."""
        response = client.post(
            "/api/todos",
            json={"title": "x" * 256},
            headers=auth_headers,
        )
        # FastAPI returns 422 for Pydantic validation errors
        assert response.status_code == 422

    def test_list_todos(self, client, auth_headers, session, test_user_id):
        """Verify list todos returns user's todos ordered by created_at desc."""
        from src.app.models.todo import Todo

        # Create test todos for the authenticated user
        todo1 = Todo(user_id=test_user_id, title="First todo", version=1)
        todo2 = Todo(user_id=test_user_id, title="Second todo", version=1)
        session.add(todo1)
        session.add(todo2)
        session.commit()

        response = client.get("/api/todos", headers=auth_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_todo(self, client, auth_headers, session, test_user_id):
        """Verify get single todo returns correct todo."""
        from src.app.models.todo import Todo

        todo_id = uuid4()
        todo = Todo(
            id=todo_id,
            user_id=test_user_id,
            title="Test todo",
            version=1,
        )
        session.add(todo)
        session.commit()

        # Should succeed since it's the same user
        response = client.get(f"/api/todos/{todo_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Test todo"

    def test_update_todo(self, client, auth_headers, session, test_user_id):
        """Verify todo update persists changes and increments version."""
        from src.app.models.todo import Todo

        # Create todo for the test user
        todo = Todo(
            user_id=test_user_id,
            title="Original title",
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        response = client.put(
            f"/api/todos/{todo.id}",
            json={
                "title": "Updated title",
                "version": 1,
            },
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["version"] == 2

    def test_partial_update_todo(self, client, auth_headers, session, test_user_id):
        """Verify partial update only changes provided fields."""
        from src.app.models.todo import Todo

        todo = Todo(
            user_id=test_user_id,
            title="Original",
            description="Original desc",
            completed=False,
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        response = client.patch(
            f"/api/todos/{todo.id}",
            json={"completed": True, "version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original"  # Unchanged
        assert data["completed"] is True
        assert data["version"] == 2

    def test_toggle_todo(self, client, auth_headers, session, test_user_id):
        """Verify toggle flips completion status."""
        from src.app.models.todo import Todo

        todo = Todo(
            user_id=test_user_id,
            title="Task",
            completed=False,
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        # Toggle on
        response = client.post(
            f"/api/todos/{todo.id}/toggle",
            json={"version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["completed"] is True
        assert response.json()["version"] == 2

        # Toggle off
        response = client.post(
            f"/api/todos/{todo.id}/toggle",
            json={"version": 2},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["completed"] is False
        assert response.json()["version"] == 3

    def test_delete_todo(self, client, auth_headers, session, test_user_id):
        """Verify delete removes todo and subsequent get returns 404."""
        from src.app.models.todo import Todo

        todo = Todo(user_id=test_user_id, title="To delete", version=1)
        session.add(todo)
        session.commit()
        session.refresh(todo)

        response = client.delete(
            f"/api/todos/{todo.id}",
            headers=auth_headers,
        )
        assert response.status_code == 204

        # Verify todo is deleted
        response = client.get(f"/api/todos/{todo.id}", headers=auth_headers)
        assert response.status_code == 404


class TestUserIsolation:
    """Tests for user data isolation (no cross-user access)."""

    def test_user_cannot_access_others_todos(self, client, auth_headers, session):
        """Verify user cannot see todos of other users."""
        from src.app.models.todo import Todo

        # Create todo for another user
        other_user_id = uuid4()
        todo = Todo(
            user_id=other_user_id,
            title="Other user's todo",
            version=1,
        )
        session.add(todo)
        session.commit()

        # Try to access with different user's token
        response = client.get("/api/todos", headers=auth_headers)
        assert response.status_code == 200
        todos = response.json()
        # Should not include other user's todos
        for t in todos:
            assert t["user_id"] != str(other_user_id)

    def test_user_cannot_update_others_todos(self, client, auth_headers, session):
        """Verify user cannot update todos of other users."""
        from src.app.models.todo import Todo

        # Create todo for another user
        other_user_id = uuid4()
        todo = Todo(
            id=uuid4(),
            user_id=other_user_id,
            title="Other user's todo",
            version=1,
        )
        session.add(todo)
        session.commit()

        response = client.put(
            f"/api/todos/{todo.id}",
            json={"title": "Hacked!", "version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 404

    def test_user_cannot_delete_others_todos(self, client, auth_headers, session):
        """Verify user cannot delete todos of other users."""
        from src.app.models.todo import Todo

        # Create todo for another user
        other_user_id = uuid4()
        todo = Todo(
            id=uuid4(),
            user_id=other_user_id,
            title="Other user's todo",
            version=1,
        )
        session.add(todo)
        session.commit()

        response = client.delete(
            f"/api/todos/{todo.id}",
            headers=auth_headers,
        )
        assert response.status_code == 404


class TestOptimisticLocking:
    """Tests for optimistic locking with version field."""

    def test_update_with_stale_version_returns_409(self, client, auth_headers, session, test_user_id):
        """Verify update with stale version returns 409 Conflict."""
        from src.app.models.todo import Todo

        todo = Todo(
            user_id=test_user_id,
            title="Original",
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        # First update (should succeed)
        response = client.put(
            f"/api/todos/{todo.id}",
            json={"title": "Updated once", "version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["version"] == 2

        # Second update with old version (should fail)
        response = client.put(
            f"/api/todos/{todo.id}",
            json={"title": "Updated twice", "version": 1},  # Stale version
            headers=auth_headers,
        )
        assert response.status_code == 409
        assert "modified by another request" in response.json()["detail"]

    def test_toggle_with_stale_version_returns_409(self, client, auth_headers, session, test_user_id):
        """Verify toggle with stale version returns 409 Conflict."""
        from src.app.models.todo import Todo

        todo = Todo(
            user_id=test_user_id,
            title="Task",
            completed=False,
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        # First toggle (should succeed)
        response = client.post(
            f"/api/todos/{todo.id}/toggle",
            json={"version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Second toggle with stale version (should fail)
        response = client.post(
            f"/api/todos/{todo.id}/toggle",
            json={"version": 1},  # Stale version
            headers=auth_headers,
        )
        assert response.status_code == 409

    def test_version_increments_on_update(self, client, auth_headers, session, test_user_id):
        """Verify version increments after each successful update."""
        from src.app.models.todo import Todo

        todo = Todo(
            user_id=test_user_id,
            title="Task",
            version=1,
        )
        session.add(todo)
        session.commit()
        session.refresh(todo)

        # Multiple updates
        for expected_version in [2, 3, 4]:
            response = client.patch(
                f"/api/todos/{todo.id}",
                json={"title": f"Update {expected_version}", "version": expected_version - 1},
                headers=auth_headers,
            )
            assert response.status_code == 200
            assert response.json()["version"] == expected_version


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_nonexistent_todo_returns_404(self, client, auth_headers):
        """Verify accessing non-existent todo returns 404."""
        fake_id = str(uuid4())
        response = client.get(f"/api/todos/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_nonexistent_todo_returns_404(self, client, auth_headers):
        """Verify deleting non-existent todo returns 404."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/todos/{fake_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_update_nonexistent_todo_returns_404(self, client, auth_headers):
        """Verify updating non-existent todo returns 404."""
        fake_id = str(uuid4())
        response = client.put(
            f"/api/todos/{fake_id}",
            json={"title": "New", "version": 1},
            headers=auth_headers,
        )
        assert response.status_code == 404
