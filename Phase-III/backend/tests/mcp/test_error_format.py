"""Error format tests for MCP error responses.

This module validates that all MCP error responses follow the standard format
defined in contracts/error-codes.json. These tests ensure consistent error
handling across all tools.
"""

import json
from pathlib import Path

import pytest

from src.mcp.middleware.error_handler import (
    MCPErrorCode,
    MCPError,
    MCPErrorResponse,
    format_mcp_error
)


@pytest.fixture
def error_code_contracts():
    """Load error code contracts from contracts/error-codes.json."""
    contracts_path = Path(__file__).parent.parent.parent.parent / "specs" / "001-phase-iii-mcp-server" / "contracts" / "error-codes.json"
    with open(contracts_path) as f:
        return json.load(f)


class TestErrorFormatStructure:
    """Test standard error format structure."""

    def test_error_response_has_error_field(self):
        """Verify error response has top-level 'error' field."""
        error = format_mcp_error(
            MCPErrorCode.TASK_NOT_FOUND,
            "Task not found",
            {}
        )
        assert "error" in error
        assert isinstance(error["error"], dict)

    def test_error_has_required_fields(self):
        """Verify error object has code, message, and details fields."""
        error = format_mcp_error(
            MCPErrorCode.INVALID_INPUT,
            "Validation failed",
            {"field": "title"}
        )
        assert "code" in error["error"]
        assert "message" in error["error"]
        assert "details" in error["error"]

    def test_error_code_is_string(self):
        """Verify error code is a string."""
        error = format_mcp_error(
            MCPErrorCode.UNAUTHORIZED,
            "Missing credentials",
            {}
        )
        assert isinstance(error["error"]["code"], str)

    def test_error_message_is_string(self):
        """Verify error message is a string."""
        error = format_mcp_error(
            MCPErrorCode.DATABASE_ERROR,
            "Database unavailable",
            {}
        )
        assert isinstance(error["error"]["message"], str)

    def test_error_details_is_dict(self):
        """Verify error details is a dictionary."""
        error = format_mcp_error(
            MCPErrorCode.CONFLICT,
            "Version mismatch",
            {"current_version": 5}
        )
        assert isinstance(error["error"]["details"], dict)


class TestErrorCodeEnum:
    """Test error code enumeration."""

    def test_all_error_codes_defined(self, error_code_contracts):
        """Verify all contract error codes are defined in enum."""
        contract_codes = [ec["code"] for ec in error_code_contracts["errorCodes"]]
        enum_codes = [code.value for code in MCPErrorCode]

        for code in contract_codes:
            assert code in enum_codes, f"Error code {code} missing from enum"

    def test_error_codes_are_uppercase_snake_case(self):
        """Verify error codes follow UPPERCASE_SNAKE_CASE convention."""
        for code in MCPErrorCode:
            assert code.value.isupper(), f"Error code {code.value} not uppercase"
            assert "_" in code.value or code.value.isalpha(), f"Error code {code.value} invalid format"


class TestErrorCodeUsage:
    """Test error code usage in format_mcp_error."""

    def test_task_not_found_error(self):
        """Test TASK_NOT_FOUND error formatting."""
        error = format_mcp_error(
            MCPErrorCode.TASK_NOT_FOUND,
            "Task with ID 123 not found",
            {}
        )
        assert error["error"]["code"] == "TASK_NOT_FOUND"

    def test_invalid_input_error(self):
        """Test INVALID_INPUT error formatting."""
        error = format_mcp_error(
            MCPErrorCode.INVALID_INPUT,
            "Input validation failed",
            {"errors": [{"field": "title", "message": "Field required"}]}
        )
        assert error["error"]["code"] == "INVALID_INPUT"
        assert "errors" in error["error"]["details"]

    def test_unauthorized_error(self):
        """Test UNAUTHORIZED error formatting."""
        error = format_mcp_error(
            MCPErrorCode.UNAUTHORIZED,
            "Missing authentication credentials",
            {}
        )
        assert error["error"]["code"] == "UNAUTHORIZED"

    def test_forbidden_error(self):
        """Test FORBIDDEN error formatting."""
        error = format_mcp_error(
            MCPErrorCode.FORBIDDEN,
            "Cannot access another user's resources",
            {}
        )
        assert error["error"]["code"] == "FORBIDDEN"

    def test_conflict_error(self):
        """Test CONFLICT error formatting."""
        error = format_mcp_error(
            MCPErrorCode.CONFLICT,
            "Task was modified by another request",
            {"current_version": 5, "attempted_version": 4}
        )
        assert error["error"]["code"] == "CONFLICT"
        assert error["error"]["details"]["current_version"] == 5

    def test_database_error(self):
        """Test DATABASE_ERROR error formatting."""
        error = format_mcp_error(
            MCPErrorCode.DATABASE_ERROR,
            "Database temporarily unavailable",
            {}
        )
        assert error["error"]["code"] == "DATABASE_ERROR"

    def test_internal_error(self):
        """Test INTERNAL_ERROR error formatting."""
        error = format_mcp_error(
            MCPErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred",
            {}
        )
        assert error["error"]["code"] == "INTERNAL_ERROR"


class TestErrorResponseModels:
    """Test Pydantic error response models."""

    def test_mcp_error_model_validation(self):
        """Test MCPError model validates correctly."""
        error = MCPError(
            code=MCPErrorCode.TASK_NOT_FOUND,
            message="Task not found",
            details={}
        )
        assert error.code == MCPErrorCode.TASK_NOT_FOUND
        assert error.message == "Task not found"
        assert error.details == {}

    def test_mcp_error_response_model_validation(self):
        """Test MCPErrorResponse model validates correctly."""
        error_response = MCPErrorResponse(
            error=MCPError(
                code=MCPErrorCode.INVALID_INPUT,
                message="Validation failed",
                details={"field": "title"}
            )
        )
        assert error_response.error.code == MCPErrorCode.INVALID_INPUT
        assert error_response.error.details["field"] == "title"

    def test_error_response_serialization(self):
        """Test error response serializes to correct format."""
        error_response = MCPErrorResponse(
            error=MCPError(
                code=MCPErrorCode.UNAUTHORIZED,
                message="Missing credentials",
                details={}
            )
        )
        serialized = error_response.model_dump()
        assert serialized == {
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Missing credentials",
                "details": {}
            }
        }
