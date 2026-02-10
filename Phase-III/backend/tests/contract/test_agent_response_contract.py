"""Contract tests for agent response schema.

Validates that agent responses conform to the expected schema
regardless of the underlying implementation.

Task ID: T038
"""

import pytest
from typing import Dict, Any, List


def validate_tool_call_schema(tool_call: Dict[str, Any]) -> None:
    """Validate a single tool call matches the expected schema.

    Expected schema:
    {
        "tool_name": str,
        "input_parameters": dict,
        "output_result": dict,
        "execution_status": "success" | "error",
        "error_message": str | None,
        "timestamp": str (ISO 8601)
    }
    """
    # Required fields
    assert "tool_name" in tool_call, "tool_call missing 'tool_name'"
    assert "input_parameters" in tool_call, "tool_call missing 'input_parameters'"
    assert "output_result" in tool_call, "tool_call missing 'output_result'"
    assert "execution_status" in tool_call, "tool_call missing 'execution_status'"
    assert "timestamp" in tool_call, "tool_call missing 'timestamp'"

    # Type validation
    assert isinstance(tool_call["tool_name"], str), "tool_name must be string"
    assert isinstance(tool_call["input_parameters"], dict), "input_parameters must be dict"
    assert isinstance(tool_call["output_result"], dict), "output_result must be dict"
    assert isinstance(tool_call["execution_status"], str), "execution_status must be string"
    assert isinstance(tool_call["timestamp"], str), "timestamp must be string"

    # Value validation
    assert tool_call["execution_status"] in ["success", "error"], \
        f"execution_status must be 'success' or 'error', got '{tool_call['execution_status']}'"

    # Tool name validation
    valid_tools = ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"]
    assert tool_call["tool_name"] in valid_tools, \
        f"tool_name must be one of {valid_tools}, got '{tool_call['tool_name']}'"

    # Timestamp format validation (ISO 8601)
    assert "T" in tool_call["timestamp"], "timestamp must be ISO 8601 format"
    assert tool_call["timestamp"].endswith("Z"), "timestamp must end with 'Z' (UTC)"

    # Error message validation
    if "error_message" in tool_call:
        if tool_call["execution_status"] == "error":
            assert tool_call["error_message"] is not None, \
                "error_message must be present when execution_status is 'error'"
        else:
            assert tool_call["error_message"] is None, \
                "error_message must be None when execution_status is 'success'"


def validate_agent_response_schema(response: Dict[str, Any]) -> None:
    """Validate agent response matches the expected schema.

    Expected schema:
    {
        "conversation_id": int,
        "response": str,
        "tool_calls": List[ToolCall]
    }
    """
    # Required fields
    assert "conversation_id" in response, "response missing 'conversation_id'"
    assert "response" in response, "response missing 'response'"
    assert "tool_calls" in response, "response missing 'tool_calls'"

    # Type validation
    assert isinstance(response["conversation_id"], int), "conversation_id must be int"
    assert isinstance(response["response"], str), "response must be string"
    assert isinstance(response["tool_calls"], list), "tool_calls must be list"

    # Value validation
    assert response["conversation_id"] > 0, "conversation_id must be positive"
    assert len(response["response"]) > 0, "response must not be empty"

    # Validate each tool call
    for tool_call in response["tool_calls"]:
        validate_tool_call_schema(tool_call)


class TestAgentResponseContract:
    """Contract tests for agent response schema."""

    def test_successful_tool_call_schema(self):
        """Test successful tool call matches schema."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {"title": "Test task", "description": None},
            "output_result": {"task_id": "123e4567-e89b-12d3-a456-426614174000"},
            "execution_status": "success",
            "error_message": None,
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        validate_tool_call_schema(tool_call)

    def test_failed_tool_call_schema(self):
        """Test failed tool call matches schema."""
        # Arrange
        tool_call = {
            "tool_name": "update_task",
            "input_parameters": {"task_id": "invalid-id", "title": "New title"},
            "output_result": {},
            "execution_status": "error",
            "error_message": "Task not found",
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        validate_tool_call_schema(tool_call)

    def test_agent_response_schema(self):
        """Test complete agent response matches schema."""
        # Arrange
        response = {
            "conversation_id": 1,
            "response": "I've created that task for you.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "input_parameters": {"title": "Test task", "description": None},
                    "output_result": {"task_id": "123e4567-e89b-12d3-a456-426614174000"},
                    "execution_status": "success",
                    "error_message": None,
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            ]
        }

        # Act & Assert
        validate_agent_response_schema(response)

    def test_agent_response_with_multiple_tool_calls(self):
        """Test agent response with multiple tool calls."""
        # Arrange
        response = {
            "conversation_id": 2,
            "response": "I've created the task and listed your tasks.",
            "tool_calls": [
                {
                    "tool_name": "add_task",
                    "input_parameters": {"title": "Task 1", "description": None},
                    "output_result": {"task_id": "123e4567-e89b-12d3-a456-426614174000"},
                    "execution_status": "success",
                    "error_message": None,
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                {
                    "tool_name": "list_tasks",
                    "input_parameters": {},
                    "output_result": {"tasks": []},
                    "execution_status": "success",
                    "error_message": None,
                    "timestamp": "2024-01-15T10:30:01Z"
                }
            ]
        }

        # Act & Assert
        validate_agent_response_schema(response)

    def test_agent_response_with_no_tool_calls(self):
        """Test agent response with no tool calls (conversational only)."""
        # Arrange
        response = {
            "conversation_id": 3,
            "response": "How can I help you with your tasks?",
            "tool_calls": []
        }

        # Act & Assert
        validate_agent_response_schema(response)

    def test_invalid_tool_name_rejected(self):
        """Test invalid tool name is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "invalid_tool",
            "input_parameters": {},
            "output_result": {},
            "execution_status": "success",
            "error_message": None,
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="tool_name must be one of"):
            validate_tool_call_schema(tool_call)

    def test_invalid_execution_status_rejected(self):
        """Test invalid execution status is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {},
            "output_result": {},
            "execution_status": "pending",  # Invalid status
            "error_message": None,
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="execution_status must be"):
            validate_tool_call_schema(tool_call)

    def test_missing_required_field_rejected(self):
        """Test missing required field is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {},
            # Missing output_result
            "execution_status": "success",
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="missing 'output_result'"):
            validate_tool_call_schema(tool_call)

    def test_invalid_timestamp_format_rejected(self):
        """Test invalid timestamp format is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {},
            "output_result": {},
            "execution_status": "success",
            "error_message": None,
            "timestamp": "2024-01-15 10:30:00"  # Invalid format (missing T and Z)
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="timestamp must be ISO 8601"):
            validate_tool_call_schema(tool_call)

    def test_error_without_error_message_rejected(self):
        """Test error status without error message is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {},
            "output_result": {},
            "execution_status": "error",
            "error_message": None,  # Should have error message
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="error_message must be present"):
            validate_tool_call_schema(tool_call)

    def test_success_with_error_message_rejected(self):
        """Test success status with error message is rejected."""
        # Arrange
        tool_call = {
            "tool_name": "add_task",
            "input_parameters": {},
            "output_result": {},
            "execution_status": "success",
            "error_message": "Some error",  # Should be None
            "timestamp": "2024-01-15T10:30:00Z"
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="error_message must be None"):
            validate_tool_call_schema(tool_call)

    def test_empty_response_text_rejected(self):
        """Test empty response text is rejected."""
        # Arrange
        response = {
            "conversation_id": 1,
            "response": "",  # Empty response
            "tool_calls": []
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="response must not be empty"):
            validate_agent_response_schema(response)

    def test_negative_conversation_id_rejected(self):
        """Test negative conversation ID is rejected."""
        # Arrange
        response = {
            "conversation_id": -1,  # Invalid
            "response": "Test",
            "tool_calls": []
        }

        # Act & Assert
        with pytest.raises(AssertionError, match="conversation_id must be positive"):
            validate_agent_response_schema(response)
