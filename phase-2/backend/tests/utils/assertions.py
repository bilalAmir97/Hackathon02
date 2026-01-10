"""
Custom assertions for E2E testing.

Provides domain-specific assertions for validating API responses,
database state, and business logic.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID


class Assertions:
    """Custom assertions for E2E testing."""

    @staticmethod
    def assert_valid_uuid(value: Any, field_name: str = "id"):
        """
        Assert that value is a valid UUID string.

        Args:
            value: Value to check
            field_name: Field name for error message
        """
        assert value is not None, f"{field_name} should not be None"
        assert isinstance(value, str), f"{field_name} should be a string"
        try:
            UUID(value)
        except ValueError:
            raise AssertionError(f"{field_name} is not a valid UUID: {value}")

    @staticmethod
    def assert_valid_timestamp(value: Any, field_name: str = "timestamp"):
        """
        Assert that value is a valid ISO timestamp string.

        Args:
            value: Value to check
            field_name: Field name for error message
        """
        assert value is not None, f"{field_name} should not be None"
        assert isinstance(value, str), f"{field_name} should be a string"
        # Basic ISO format check
        assert "T" in value or "-" in value, f"{field_name} is not a valid timestamp: {value}"

    @staticmethod
    def assert_todo_structure(todo: Dict[str, Any], check_timestamps: bool = True):
        """
        Assert that todo has correct structure.

        Args:
            todo: Todo dictionary to validate
            check_timestamps: Whether to validate timestamp fields
        """
        required_fields = ["id", "user_id", "title", "completed", "version"]
        for field in required_fields:
            assert field in todo, f"Todo missing required field: {field}"

        Assertions.assert_valid_uuid(todo["id"], "todo.id")
        Assertions.assert_valid_uuid(todo["user_id"], "todo.user_id")
        assert isinstance(todo["title"], str), "todo.title should be a string"
        assert isinstance(todo["completed"], bool), "todo.completed should be a boolean"
        assert isinstance(todo["version"], int), "todo.version should be an integer"
        assert todo["version"] >= 1, "todo.version should be >= 1"

        if check_timestamps:
            if "created_at" in todo:
                Assertions.assert_valid_timestamp(todo["created_at"], "todo.created_at")
            if "updated_at" in todo:
                Assertions.assert_valid_timestamp(todo["updated_at"], "todo.updated_at")

    @staticmethod
    def assert_todo_list(todos: List[Dict[str, Any]], expected_count: Optional[int] = None):
        """
        Assert that todos list has correct structure.

        Args:
            todos: List of todo dictionaries
            expected_count: Expected number of todos (optional)
        """
        assert isinstance(todos, list), "Todos should be a list"

        if expected_count is not None:
            assert len(todos) == expected_count, f"Expected {expected_count} todos, got {len(todos)}"

        for todo in todos:
            Assertions.assert_todo_structure(todo)

    @staticmethod
    def assert_user_owns_todo(todo: Dict[str, Any], user_id: UUID):
        """
        Assert that todo belongs to specified user.

        Args:
            todo: Todo dictionary
            user_id: Expected owner user ID
        """
        assert "user_id" in todo, "Todo missing user_id field"
        assert todo["user_id"] == str(user_id), f"Todo belongs to {todo['user_id']}, not {user_id}"

    @staticmethod
    def assert_http_status(response, expected_status: int, message: Optional[str] = None):
        """
        Assert HTTP response status code.

        Args:
            response: HTTP response object
            expected_status: Expected status code
            message: Optional custom error message
        """
        actual_status = response.status_code
        error_msg = message or f"Expected status {expected_status}, got {actual_status}"

        if actual_status != expected_status:
            # Include response body for debugging
            try:
                body = response.json()
                error_msg += f"\nResponse body: {body}"
            except:
                error_msg += f"\nResponse text: {response.text}"

        assert actual_status == expected_status, error_msg

    @staticmethod
    def assert_error_response(response, expected_status: int, expected_detail: Optional[str] = None):
        """
        Assert error response structure and content.

        Args:
            response: HTTP response object
            expected_status: Expected error status code
            expected_detail: Expected error detail message (substring match)
        """
        Assertions.assert_http_status(response, expected_status)

        body = response.json()
        assert "detail" in body, "Error response should have 'detail' field"

        if expected_detail:
            detail = body["detail"]
            assert expected_detail.lower() in detail.lower(), \
                f"Expected detail to contain '{expected_detail}', got '{detail}'"

    @staticmethod
    def assert_jwt_token_structure(token: str):
        """
        Assert JWT token has correct structure (3 parts separated by dots).

        Args:
            token: JWT token string
        """
        assert isinstance(token, str), "Token should be a string"
        parts = token.split(".")
        assert len(parts) == 3, f"JWT should have 3 parts, got {len(parts)}"
        for i, part in enumerate(parts):
            assert len(part) > 0, f"JWT part {i} should not be empty"

    @staticmethod
    def assert_version_incremented(old_version: int, new_version: int):
        """
        Assert that version was incremented by 1.

        Args:
            old_version: Previous version number
            new_version: New version number
        """
        assert new_version == old_version + 1, \
            f"Version should increment by 1: {old_version} -> {new_version}"

    @staticmethod
    def assert_todos_belong_to_user(todos: List[Dict[str, Any]], user_id: UUID):
        """
        Assert that all todos in list belong to specified user.

        Args:
            todos: List of todo dictionaries
            user_id: Expected owner user ID
        """
        for todo in todos:
            Assertions.assert_user_owns_todo(todo, user_id)

    @staticmethod
    def assert_no_todos_from_other_user(todos: List[Dict[str, Any]], other_user_id: UUID):
        """
        Assert that no todos in list belong to other user.

        Args:
            todos: List of todo dictionaries
            other_user_id: User ID that should NOT own any todos
        """
        for todo in todos:
            assert todo["user_id"] != str(other_user_id), \
                f"Found todo belonging to other user: {todo['id']}"
