"""
Integration tests for Todo API endpoints.

Tests User Story 2: Backend API Contract Validation
Validates all CRUD operations, status codes, request/response schemas, and data isolation.
"""
import pytest
from uuid import uuid4

from tests.fixtures.test_data import TodoFactory
from tests.utils.auth_helpers import AuthHelpers
from tests.utils.assertions import Assertions


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.us2
class TestTodoAPICRUD:
    """Test Todo API CRUD operations."""

    def test_create_todo_with_valid_payload(self, client, test_user_id):
        """
        T033: Test creating a todo with valid payload.

        Given: Authenticated user with valid todo payload
        When: POST /api/todos is called
        Then: 201 Created is returned with todo object
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        response = client.post("/api/todos", json=payload, headers=headers)

        Assertions.assert_http_status(response, 201)
        todo = response.json()
        Assertions.assert_todo_structure(todo)
        assert todo["title"] == "Buy groceries"
        assert todo["description"] == "Milk, eggs, bread"
        assert todo["completed"] is False
        assert todo["version"] == 1
        Assertions.assert_user_owns_todo(todo, test_user_id)

    def test_list_todos_returns_empty_initially(self, client, test_user_id):
        """
        T034: Test listing todos returns empty array initially.

        Given: Authenticated user with no todos
        When: GET /api/todos is called
        Then: 200 OK is returned with empty array
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        response = client.get("/api/todos", headers=headers)

        Assertions.assert_http_status(response, 200)
        todos = response.json()
        assert todos == []

    def test_list_todos_returns_user_todos_only(self, client, test_user_id):
        """
        T034: Test listing todos returns only user's todos.

        Given: Authenticated user with multiple todos
        When: GET /api/todos is called
        Then: 200 OK is returned with user's todos only
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create 3 todos
        for i in range(3):
            payload = TodoFactory.create_todo_payload(title=f"Todo {i+1}")
            response = client.post("/api/todos", json=payload, headers=headers)
            Assertions.assert_http_status(response, 201)

        # List todos
        response = client.get("/api/todos", headers=headers)

        Assertions.assert_http_status(response, 200)
        todos = response.json()
        Assertions.assert_todo_list(todos, expected_count=3)
        Assertions.assert_todos_belong_to_user(todos, test_user_id)

    def test_get_todo_by_id_returns_todo(self, client, test_user_id):
        """
        T035: Test getting specific todo by ID.

        Given: Authenticated user with existing todo
        When: GET /api/todos/{id} is called
        Then: 200 OK is returned with todo object
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Test Todo")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Get the todo
        response = client.get(f"/api/todos/{todo_id}", headers=headers)

        Assertions.assert_http_status(response, 200)
        todo = response.json()
        Assertions.assert_todo_structure(todo)
        assert todo["id"] == todo_id
        assert todo["title"] == "Test Todo"

    def test_get_nonexistent_todo_returns_404(self, client, test_user_id):
        """
        T035: Test getting nonexistent todo returns 404.

        Given: Authenticated user
        When: GET /api/todos/{nonexistent_id} is called
        Then: 404 Not Found is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        nonexistent_id = str(uuid4())

        response = client.get(f"/api/todos/{nonexistent_id}", headers=headers)

        Assertions.assert_http_status(response, 404)

    def test_update_todo_with_valid_payload(self, client, test_user_id):
        """
        T036: Test updating todo with valid payload.

        Given: Authenticated user with existing todo
        When: PUT /api/todos/{id} is called with valid payload
        Then: 200 OK is returned with updated todo
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        create_payload = TodoFactory.create_todo_payload(title="Original Title")
        create_response = client.post("/api/todos", json=create_payload, headers=headers)
        todo = create_response.json()
        todo_id = todo["id"]

        # Update the todo
        update_payload = TodoFactory.create_update_payload(
            title="Updated Title",
            description="Updated Description",
            version=1
        )
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        Assertions.assert_http_status(response, 200)
        updated_todo = response.json()
        assert updated_todo["id"] == todo_id
        assert updated_todo["title"] == "Updated Title"
        assert updated_todo["description"] == "Updated Description"
        Assertions.assert_version_incremented(1, updated_todo["version"])

    def test_delete_todo_removes_todo(self, client, test_user_id):
        """
        T037: Test deleting todo removes it.

        Given: Authenticated user with existing todo
        When: DELETE /api/todos/{id} is called
        Then: 204 No Content is returned and todo is deleted
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="To be deleted")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Delete the todo
        response = client.delete(f"/api/todos/{todo_id}", headers=headers)

        Assertions.assert_http_status(response, 204)

        # Verify deletion
        get_response = client.get(f"/api/todos/{todo_id}", headers=headers)
        Assertions.assert_http_status(get_response, 404)

    def test_toggle_todo_completion_status(self, client, test_user_id):
        """
        T038: Test toggling todo completion status.

        Given: Authenticated user with existing todo
        When: POST /api/todos/{id}/toggle is called
        Then: 200 OK is returned with toggled completion status
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo (initially not completed)
        payload = TodoFactory.create_todo_payload(title="Toggle Test")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo = create_response.json()
        todo_id = todo["id"]
        assert todo["completed"] is False

        # Toggle to completed
        toggle_payload = TodoFactory.create_toggle_payload(version=1)
        response = client.post(f"/api/todos/{todo_id}/toggle", json=toggle_payload, headers=headers)

        Assertions.assert_http_status(response, 200)
        toggled_todo = response.json()
        assert toggled_todo["completed"] is True
        Assertions.assert_version_incremented(1, toggled_todo["version"])

        # Toggle back to not completed
        toggle_payload = TodoFactory.create_toggle_payload(version=2)
        response = client.post(f"/api/todos/{todo_id}/toggle", json=toggle_payload, headers=headers)

        Assertions.assert_http_status(response, 200)
        toggled_todo = response.json()
        assert toggled_todo["completed"] is False
        Assertions.assert_version_incremented(2, toggled_todo["version"])


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.us2
class TestTodoAPIAuthorization:
    """Test API authorization and data isolation."""

    def test_unauthorized_access_returns_401(self, client):
        """
        T039: Test that unauthorized access returns 401.

        Given: No authentication provided
        When: Any protected endpoint is called
        Then: 401 Unauthorized is returned
        """
        # Test all CRUD operations without auth
        endpoints = [
            ("GET", "/api/todos"),
            ("POST", "/api/todos", {"title": "Test"}),
            ("GET", f"/api/todos/{uuid4()}"),
            ("PUT", f"/api/todos/{uuid4()}", {"title": "Test", "version": 1}),
            ("DELETE", f"/api/todos/{uuid4()}"),
            ("POST", f"/api/todos/{uuid4()}/toggle", {"version": 1}),
        ]

        for method, endpoint, *payload in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json=payload[0] if payload else {})
            elif method == "PUT":
                response = client.put(endpoint, json=payload[0] if payload else {})
            elif method == "DELETE":
                response = client.delete(endpoint)

            Assertions.assert_http_status(response, 401, f"{method} {endpoint} should return 401")

    def test_user_cannot_access_other_user_todo(self, client, test_user_id, other_user_id):
        """
        T041: Test that users cannot access other users' todos.

        Given: Two authenticated users
        When: User A tries to access User B's todo
        Then: 404 Not Found is returned
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)

        # User A creates a todo
        payload = TodoFactory.create_todo_payload(title="User A's todo")
        response = client.post("/api/todos", json=payload, headers=user_a_headers)
        todo_id = response.json()["id"]

        # User B tries to access User A's todo
        response = client.get(f"/api/todos/{todo_id}", headers=user_b_headers)
        Assertions.assert_http_status(response, 404)

    def test_user_cannot_update_other_user_todo(self, client, test_user_id, other_user_id):
        """
        T041: Test that users cannot update other users' todos.

        Given: Two authenticated users
        When: User A tries to update User B's todo
        Then: 404 Not Found is returned
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)

        # User A creates a todo
        payload = TodoFactory.create_todo_payload(title="User A's todo")
        response = client.post("/api/todos", json=payload, headers=user_a_headers)
        todo_id = response.json()["id"]

        # User B tries to update User A's todo
        update_payload = TodoFactory.create_update_payload(title="Hacked!", version=1)
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=user_b_headers)
        Assertions.assert_http_status(response, 404)

    def test_user_cannot_delete_other_user_todo(self, client, test_user_id, other_user_id):
        """
        T041: Test that users cannot delete other users' todos.

        Given: Two authenticated users
        When: User A tries to delete User B's todo
        Then: 404 Not Found is returned
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)

        # User A creates a todo
        payload = TodoFactory.create_todo_payload(title="User A's todo")
        response = client.post("/api/todos", json=payload, headers=user_a_headers)
        todo_id = response.json()["id"]

        # User B tries to delete User A's todo
        response = client.delete(f"/api/todos/{todo_id}", headers=user_b_headers)
        Assertions.assert_http_status(response, 404)

        # Verify todo still exists for User A
        response = client.get(f"/api/todos/{todo_id}", headers=user_a_headers)
        Assertions.assert_http_status(response, 200)

    def test_list_todos_shows_only_user_todos(self, client, test_user_id, other_user_id):
        """
        T041: Test that list todos shows only user's own todos.

        Given: Two users with their own todos
        When: Each user lists their todos
        Then: Each sees only their own todos
        """
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)

        # User A creates 2 todos
        for i in range(2):
            payload = TodoFactory.create_todo_payload(title=f"User A Todo {i+1}")
            client.post("/api/todos", json=payload, headers=user_a_headers)

        # User B creates 3 todos
        for i in range(3):
            payload = TodoFactory.create_todo_payload(title=f"User B Todo {i+1}")
            client.post("/api/todos", json=payload, headers=user_b_headers)

        # User A lists todos
        response = client.get("/api/todos", headers=user_a_headers)
        user_a_todos = response.json()
        Assertions.assert_todo_list(user_a_todos, expected_count=2)
        Assertions.assert_todos_belong_to_user(user_a_todos, test_user_id)
        Assertions.assert_no_todos_from_other_user(user_a_todos, other_user_id)

        # User B lists todos
        response = client.get("/api/todos", headers=user_b_headers)
        user_b_todos = response.json()
        Assertions.assert_todo_list(user_b_todos, expected_count=3)
        Assertions.assert_todos_belong_to_user(user_b_todos, other_user_id)
        Assertions.assert_no_todos_from_other_user(user_b_todos, test_user_id)


@pytest.mark.integration
@pytest.mark.api
@pytest.mark.us2
class TestTodoAPIValidation:
    """Test API request validation."""

    def test_create_todo_with_missing_title_returns_422(self, client, test_user_id):
        """
        T040: Test that creating todo without title returns 422.

        Given: Authenticated user with invalid payload (missing title)
        When: POST /api/todos is called
        Then: 422 Unprocessable Entity is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = {"description": "No title provided"}

        response = client.post("/api/todos", json=payload, headers=headers)

        Assertions.assert_http_status(response, 422)

    def test_create_todo_with_empty_title_returns_422(self, client, test_user_id):
        """
        T040: Test that creating todo with empty title returns 422.

        Given: Authenticated user with invalid payload (empty title)
        When: POST /api/todos is called
        Then: 422 Unprocessable Entity is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = {"title": "", "description": "Empty title"}

        response = client.post("/api/todos", json=payload, headers=headers)

        Assertions.assert_http_status(response, 422)

    def test_update_todo_with_invalid_version_returns_409(self, client, test_user_id):
        """
        T040: Test that updating todo with stale version returns 409.

        Given: Authenticated user with existing todo
        When: PUT /api/todos/{id} is called with stale version
        Then: 409 Conflict is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Version Test")
        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Update once (version 1 -> 2)
        update_payload = TodoFactory.create_update_payload(title="First Update", version=1)
        client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        # Try to update with stale version (should fail)
        stale_payload = TodoFactory.create_update_payload(title="Stale Update", version=1)
        response = client.put(f"/api/todos/{todo_id}", json=stale_payload, headers=headers)

        Assertions.assert_http_status(response, 409)
        Assertions.assert_error_response(response, 409, "modified")

    def test_update_todo_with_missing_version_returns_422(self, client, test_user_id):
        """
        T040: Test that updating todo without version returns 422.

        Given: Authenticated user with existing todo
        When: PUT /api/todos/{id} is called without version
        Then: 422 Unprocessable Entity is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Version Test")
        response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = response.json()["id"]

        # Try to update without version
        update_payload = {"title": "No version"}
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        Assertions.assert_http_status(response, 422)
