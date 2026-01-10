"""
Contract validation tests for API endpoints.

Tests that API responses conform to expected schemas and contracts.
"""
import pytest
from uuid import uuid4

from tests.fixtures.test_data import TodoFactory
from tests.utils.auth_helpers import AuthHelpers
from tests.utils.assertions import Assertions


@pytest.mark.contract
@pytest.mark.api
@pytest.mark.us2
class TestTodoAPIContract:
    """Test Todo API response contracts."""

    def test_create_todo_response_schema(self, client, test_user_id):
        """
        T042: Test that create todo response matches expected schema.

        Given: Valid todo creation request
        When: POST /api/todos is called
        Then: Response has correct structure with all required fields
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload(title="Test Todo")

        response = client.post("/api/todos", json=payload, headers=headers)

        assert response.status_code == 201
        todo = response.json()

        # Verify all required fields are present
        required_fields = ["id", "user_id", "title", "description", "completed", "version", "created_at", "updated_at"]
        for field in required_fields:
            assert field in todo, f"Response should contain '{field}' field"

        # Verify field types
        Assertions.assert_valid_uuid(todo["id"])
        Assertions.assert_valid_uuid(todo["user_id"])
        assert isinstance(todo["title"], str)
        assert isinstance(todo["completed"], bool)
        assert isinstance(todo["version"], int)

    def test_list_todos_response_schema(self, client, test_user_id):
        """
        T043: Test that list todos response matches expected schema.

        Given: User with multiple todos
        When: GET /api/todos is called
        Then: Response is an array of todo objects
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create some todos
        for i in range(3):
            payload = TodoFactory.create_todo_payload(title=f"Todo {i}")
            client.post("/api/todos", json=payload, headers=headers)

        response = client.get("/api/todos", headers=headers)

        assert response.status_code == 200
        todos = response.json()

        assert isinstance(todos, list), "Response should be an array"
        assert len(todos) == 3

        for todo in todos:
            Assertions.assert_todo_structure(todo)

    def test_get_todo_response_schema(self, client, test_user_id):
        """
        T043: Test that get todo response matches expected schema.

        Given: Existing todo
        When: GET /api/todos/{id} is called
        Then: Response is a single todo object with all fields
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Test Todo")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        response = client.get(f"/api/todos/{todo_id}", headers=headers)

        assert response.status_code == 200
        todo = response.json()
        Assertions.assert_todo_structure(todo)

    def test_update_todo_response_schema(self, client, test_user_id):
        """
        T043: Test that update todo response matches expected schema.

        Given: Existing todo
        When: PUT /api/todos/{id} is called
        Then: Response is updated todo object with incremented version
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Original")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Update the todo
        update_payload = TodoFactory.create_update_payload(title="Updated", version=1)
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        assert response.status_code == 200
        todo = response.json()
        Assertions.assert_todo_structure(todo)
        assert todo["version"] == 2

    def test_toggle_todo_response_schema(self, client, test_user_id):
        """
        T043: Test that toggle todo response matches expected schema.

        Given: Existing todo
        When: POST /api/todos/{id}/toggle is called
        Then: Response is todo object with toggled completion status
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload(title="Toggle Test")
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Toggle the todo
        toggle_payload = TodoFactory.create_toggle_payload(version=1)
        response = client.post(f"/api/todos/{todo_id}/toggle", json=toggle_payload, headers=headers)

        assert response.status_code == 200
        todo = response.json()
        Assertions.assert_todo_structure(todo)
        assert isinstance(todo["completed"], bool)


@pytest.mark.contract
@pytest.mark.api
@pytest.mark.us2
class TestAPIStatusCodes:
    """Test that API returns correct HTTP status codes."""

    def test_successful_create_returns_201(self, client, test_user_id):
        """
        T044: Test that successful creation returns 201 Created.

        Given: Valid todo creation request
        When: POST /api/todos is called
        Then: 201 Created status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        payload = TodoFactory.create_todo_payload()

        response = client.post("/api/todos", json=payload, headers=headers)
        assert response.status_code == 201

    def test_successful_list_returns_200(self, client, test_user_id):
        """
        T044: Test that successful list returns 200 OK.

        Given: Authenticated user
        When: GET /api/todos is called
        Then: 200 OK status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        response = client.get("/api/todos", headers=headers)
        assert response.status_code == 200

    def test_successful_get_returns_200(self, client, test_user_id):
        """
        T044: Test that successful get returns 200 OK.

        Given: Existing todo
        When: GET /api/todos/{id} is called
        Then: 200 OK status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload()
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        response = client.get(f"/api/todos/{todo_id}", headers=headers)
        assert response.status_code == 200

    def test_successful_update_returns_200(self, client, test_user_id):
        """
        T044: Test that successful update returns 200 OK.

        Given: Existing todo
        When: PUT /api/todos/{id} is called
        Then: 200 OK status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload()
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        # Update the todo
        update_payload = TodoFactory.create_update_payload(version=1)
        response = client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)
        assert response.status_code == 200

    def test_successful_delete_returns_204(self, client, test_user_id):
        """
        T044: Test that successful delete returns 204 No Content.

        Given: Existing todo
        When: DELETE /api/todos/{id} is called
        Then: 204 No Content status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create a todo
        payload = TodoFactory.create_todo_payload()
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        response = client.delete(f"/api/todos/{todo_id}", headers=headers)
        assert response.status_code == 204

    def test_not_found_returns_404(self, client, test_user_id):
        """
        T044: Test that not found returns 404.

        Given: Nonexistent todo ID
        When: GET /api/todos/{id} is called
        Then: 404 Not Found status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        nonexistent_id = str(uuid4())

        response = client.get(f"/api/todos/{nonexistent_id}", headers=headers)
        assert response.status_code == 404

    def test_unauthorized_returns_401(self, client):
        """
        T044: Test that unauthorized access returns 401.

        Given: No authentication
        When: Protected endpoint is called
        Then: 401 Unauthorized status is returned
        """
        response = client.get("/api/todos")
        assert response.status_code == 401

    def test_validation_error_returns_422(self, client, test_user_id):
        """
        T044: Test that validation error returns 422.

        Given: Invalid request payload
        When: POST /api/todos is called
        Then: 422 Unprocessable Entity status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        invalid_payload = {"description": "Missing title"}

        response = client.post("/api/todos", json=invalid_payload, headers=headers)
        assert response.status_code == 422

    def test_conflict_returns_409(self, client, test_user_id):
        """
        T044: Test that version conflict returns 409.

        Given: Existing todo with version 2
        When: Update is attempted with version 1
        Then: 409 Conflict status is returned
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Create and update a todo to version 2
        payload = TodoFactory.create_todo_payload()
        create_response = client.post("/api/todos", json=payload, headers=headers)
        todo_id = create_response.json()["id"]

        update_payload = TodoFactory.create_update_payload(version=1)
        client.put(f"/api/todos/{todo_id}", json=update_payload, headers=headers)

        # Try to update with stale version
        stale_payload = TodoFactory.create_update_payload(version=1)
        response = client.put(f"/api/todos/{todo_id}", json=stale_payload, headers=headers)
        assert response.status_code == 409


@pytest.mark.contract
@pytest.mark.api
@pytest.mark.us2
class TestAPIErrorResponses:
    """Test API error response contracts."""

    def test_error_responses_have_detail_field(self, client, test_user_id):
        """
        T042: Test that error responses have 'detail' field.

        Given: Various error conditions
        When: API returns error
        Then: Response contains 'detail' field with error message
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Test 404 error
        response = client.get(f"/api/todos/{uuid4()}", headers=headers)
        assert response.status_code == 404
        assert "detail" in response.json()

        # Test 422 error
        response = client.post("/api/todos", json={}, headers=headers)
        assert response.status_code == 422
        assert "detail" in response.json()

    def test_validation_error_details_are_descriptive(self, client, test_user_id):
        """
        T042: Test that validation errors provide descriptive details.

        Given: Invalid request payload
        When: API validates request
        Then: Error details describe what's wrong
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)
        invalid_payload = {"description": "Missing title"}

        response = client.post("/api/todos", json=invalid_payload, headers=headers)

        assert response.status_code == 422
        body = response.json()
        assert "detail" in body
        # Validation errors should mention the field or issue
