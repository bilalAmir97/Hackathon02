"""
End-to-end integration tests for the Todo API.

Tests the complete workflow from authentication through CRUD operations.
"""
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from jose import jwt

# Set test environment
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-e2e-testing"


class TestE2EWorkflow:
    """End-to-end tests for complete Todo workflow."""

    def test_complete_todo_lifecycle(self, client):
        """Test complete lifecycle: create, read, update, toggle, delete."""
        # Setup: Create JWT token for test user
        user_id = str(uuid4())
        token = jwt.encode(
            {"sub": user_id, "exp": datetime.now(timezone.utc).timestamp() + 3600},
            os.getenv("BETTER_AUTH_SECRET"),
            algorithm="HS256",
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Verify empty list initially
        response = client.get("/api/todos", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

        # Step 2: Create a todo
        create_payload = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
        }
        response = client.post("/api/todos", json=create_payload, headers=headers)
        assert response.status_code == 201
        todo = response.json()
        assert todo["title"] == "Buy groceries"
        assert todo["description"] == "Milk, eggs, bread"
        assert todo["completed"] is False
        assert todo["version"] == 1
        todo_id = todo["id"]

        # Step 3: List todos (should have 1)
        response = client.get("/api/todos", headers=headers)
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["id"] == todo_id

        # Step 4: Get specific todo
        response = client.get(f"/api/todos/{todo_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == todo_id

        # Step 5: Update todo
        update_payload = {
            "title": "Buy groceries and cook dinner",
            "description": "Milk, eggs, bread, chicken",
            "version": 1,
        }
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)
        assert response.status_code == 200
        updated_todo = response.json()
        assert updated_todo["title"] == "Buy groceries and cook dinner"
        assert updated_todo["version"] == 2

        # Step 6: Toggle completion
        toggle_payload = {"version": 2}
        response = client.post(f"/api/todos/{todo_id}/toggle", json=toggle_payload, headers=headers)
        assert response.status_code == 200
        toggled_todo = response.json()
        assert toggled_todo["completed"] is True
        assert toggled_todo["version"] == 3

        # Step 7: Delete todo
        response = client.delete(f"/api/todos/{todo_id}", headers=headers)
        assert response.status_code == 204

        # Step 8: Verify deletion
        response = client.get("/api/todos", headers=headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_user_isolation_e2e(self, client):
        """Test that users can only access their own todos."""
        # Create two users
        user1_id = str(uuid4())
        user2_id = str(uuid4())

        secret = os.getenv("BETTER_AUTH_SECRET")

        user1_token = jwt.encode(
            {"sub": user1_id, "exp": datetime.now(timezone.utc).timestamp() + 3600},
            secret,
            algorithm="HS256",
        )
        user2_token = jwt.encode(
            {"sub": user2_id, "exp": datetime.now(timezone.utc).timestamp() + 3600},
            secret,
            algorithm="HS256",
        )

        user1_headers = {"Authorization": f"Bearer {user1_token}"}
        user2_headers = {"Authorization": f"Bearer {user2_token}"}

        # User 1 creates a todo
        response = client.post(
            "/api/todos",
            json={"title": "User 1's todo"},
            headers=user1_headers,
        )
        assert response.status_code == 201
        user1_todo_id = response.json()["id"]

        # User 2 creates a todo
        response = client.post(
            "/api/todos",
            json={"title": "User 2's todo"},
            headers=user2_headers,
        )
        assert response.status_code == 201
        user2_todo_id = response.json()["id"]

        # User 1 can only see their own todo
        response = client.get("/api/todos", headers=user1_headers)
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["id"] == user1_todo_id

        # User 2 can only see their own todo
        response = client.get("/api/todos", headers=user2_headers)
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 1
        assert todos[0]["id"] == user2_todo_id

        # User 1 cannot access User 2's todo
        response = client.get(f"/api/todos/{user2_todo_id}", headers=user1_headers)
        assert response.status_code == 404

        # User 2 cannot access User 1's todo
        response = client.get(f"/api/todos/{user1_todo_id}", headers=user2_headers)
        assert response.status_code == 404

    def test_optimistic_locking_e2e(self, client):
        """Test optimistic locking prevents concurrent update conflicts."""
        # Setup user
        user_id = str(uuid4())
        token = jwt.encode(
            {"sub": user_id, "exp": datetime.now(timezone.utc).timestamp() + 3600},
            os.getenv("BETTER_AUTH_SECRET"),
            algorithm="HS256",
        )
        headers = {"Authorization": f"Bearer {token}"}

        # Create a todo
        response = client.post(
            "/api/todos",
            json={"title": "Test optimistic locking"},
            headers=headers,
        )
        assert response.status_code == 201
        todo = response.json()
        todo_id = todo["id"]
        assert todo["version"] == 1

        # First update succeeds
        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Updated title", "version": 1},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["version"] == 2

        # Second update with stale version fails
        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Another update", "version": 1},
            headers=headers,
        )
        assert response.status_code == 409
        assert "modified by another request" in response.json()["detail"]

        # Update with correct version succeeds
        response = client.put(
            f"/api/todos/{todo_id}",
            json={"title": "Final update", "version": 2},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json()["version"] == 3
