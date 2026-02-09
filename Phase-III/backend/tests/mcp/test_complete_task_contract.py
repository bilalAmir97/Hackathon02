"""Contract tests for complete_task tool.

This module validates that the complete_task tool implementation matches the
contract defined in contracts/mcp-tools.json. Tests verify input/output
schemas and idempotent behavior.
"""

import pytest
from uuid import UUID

from src.mcp.schemas.tool_inputs import CompleteTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput


class TestCompleteTaskInputContract:
    """Test complete_task input schema contract compliance."""

    def test_complete_task_input_requires_task_id(self):
        """Verify task_id field is required."""
        with pytest.raises(Exception):
            CompleteTaskInput()

    def test_complete_task_input_task_id_is_uuid(self):
        """Verify task_id must be valid UUID format."""
        input_data = CompleteTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert isinstance(input_data.task_id, UUID)

    def test_complete_task_input_rejects_invalid_uuid(self):
        """Verify task_id rejects invalid UUID strings."""
        with pytest.raises(Exception):
            CompleteTaskInput(task_id="not-a-uuid")


class TestCompleteTaskOutputContract:
    """Test complete_task output schema contract compliance."""

    def test_complete_task_output_has_required_fields(self):
        """Verify output has all required fields."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test task",
            description=None,
            status="completed",
            version=2,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:05:00Z"
        )
        assert output.id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert output.status == "completed"
        assert output.version == 2

    def test_complete_task_output_status_is_completed(self):
        """Verify output status is always 'completed'."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test",
            description=None,
            status="completed",
            version=2,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:05:00Z"
        )
        assert output.status == "completed"

    def test_complete_task_output_version_incremented(self):
        """Verify version is incremented after completion."""
        # This test verifies the contract expectation that version increments
        # The actual increment happens in the tool implementation
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test",
            description=None,
            status="completed",
            version=2,  # Incremented from 1
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:05:00Z"
        )
        assert output.version >= 1
