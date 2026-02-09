"""Contract tests for delete_task tool.

This module validates that the delete_task tool implementation matches the
contract defined in contracts/mcp-tools.json. Tests verify input/output
schemas and deletion confirmation behavior.
"""

import pytest
from uuid import UUID

from src.mcp.schemas.tool_inputs import DeleteTaskInput
from src.mcp.schemas.tool_outputs import DeleteTaskOutput


class TestDeleteTaskInputContract:
    """Test delete_task input schema contract compliance."""

    def test_delete_task_input_requires_task_id(self):
        """Verify task_id field is required."""
        with pytest.raises(Exception):
            DeleteTaskInput()

    def test_delete_task_input_task_id_is_uuid(self):
        """Verify task_id must be valid UUID format."""
        input_data = DeleteTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert isinstance(input_data.task_id, UUID)

    def test_delete_task_input_accepts_valid_uuid(self):
        """Verify delete_task accepts valid UUID string."""
        input_data = DeleteTaskInput(
            task_id=UUID("550e8400-e29b-41d4-a716-446655440000")
        )
        assert str(input_data.task_id) == "550e8400-e29b-41d4-a716-446655440000"

    def test_delete_task_input_rejects_invalid_uuid(self):
        """Verify delete_task rejects invalid UUID format."""
        with pytest.raises(Exception):
            DeleteTaskInput(task_id="not-a-uuid")


class TestDeleteTaskOutputContract:
    """Test delete_task output schema contract compliance."""

    def test_delete_task_output_has_required_fields(self):
        """Verify output has all required fields."""
        output = DeleteTaskOutput(
            success=True,
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            message="Task deleted successfully"
        )
        assert output.success is True
        assert output.task_id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert output.message == "Task deleted successfully"

    def test_delete_task_output_success_is_boolean(self):
        """Verify success field is boolean type."""
        output = DeleteTaskOutput(
            success=True,
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            message="Task deleted successfully"
        )
        assert isinstance(output.success, bool)

    def test_delete_task_output_task_id_is_uuid(self):
        """Verify task_id field is UUID type."""
        output = DeleteTaskOutput(
            success=True,
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            message="Task deleted successfully"
        )
        assert isinstance(output.task_id, UUID)

    def test_delete_task_output_message_is_string(self):
        """Verify message field is string type."""
        output = DeleteTaskOutput(
            success=True,
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            message="Task deleted successfully"
        )
        assert isinstance(output.message, str)

    def test_delete_task_output_confirms_deletion(self):
        """Verify output confirms successful deletion."""
        output = DeleteTaskOutput(
            success=True,
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            message="Task deleted successfully"
        )
        assert output.success is True
        assert "deleted" in output.message.lower()
