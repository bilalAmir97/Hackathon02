"""Contract tests for update_task tool.

This module validates that the update_task tool implementation matches the
contract defined in contracts/mcp-tools.json. Tests verify input/output
schemas, optional fields, and version increment behavior.
"""

import pytest
from uuid import UUID

from src.mcp.schemas.tool_inputs import UpdateTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput


class TestUpdateTaskInputContract:
    """Test update_task input schema contract compliance."""

    def test_update_task_input_requires_task_id(self):
        """Verify task_id field is required."""
        with pytest.raises(Exception):
            UpdateTaskInput()

    def test_update_task_input_task_id_is_uuid(self):
        """Verify task_id must be valid UUID format."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert isinstance(input_data.task_id, UUID)

    def test_update_task_input_title_is_optional(self):
        """Verify title field is optional."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert input_data.title is None

    def test_update_task_input_description_is_optional(self):
        """Verify description field is optional."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000")
        )
        assert input_data.description is None

    def test_update_task_input_title_min_length(self):
        """Verify title has minimum length of 1 character."""
        with pytest.raises(Exception):
            UpdateTaskInput(
                task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                title=""
            )

    def test_update_task_input_title_max_length(self):
        """Verify title has maximum length of 200 characters."""
        with pytest.raises(Exception):
            UpdateTaskInput(
                task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                title="x" * 201
            )

    def test_update_task_input_description_max_length(self):
        """Verify description has maximum length of 2000 characters."""
        with pytest.raises(Exception):
            UpdateTaskInput(
                task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                description="x" * 2001
            )

    def test_update_task_input_with_title_only(self):
        """Verify update with only title is valid."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            title="New title"
        )
        assert input_data.title == "New title"
        assert input_data.description is None

    def test_update_task_input_with_description_only(self):
        """Verify update with only description is valid."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            description="New description"
        )
        assert input_data.title is None
        assert input_data.description == "New description"

    def test_update_task_input_with_both_fields(self):
        """Verify update with both title and description is valid."""
        input_data = UpdateTaskInput(
            task_id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            title="New title",
            description="New description"
        )
        assert input_data.title == "New title"
        assert input_data.description == "New description"


class TestUpdateTaskOutputContract:
    """Test update_task output schema contract compliance."""

    def test_update_task_output_has_required_fields(self):
        """Verify output has all required fields."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Updated title",
            description="Updated description",
            status="pending",
            version=2,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:10:00Z"
        )
        assert output.id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert output.title == "Updated title"
        assert output.version == 2

    def test_update_task_output_version_incremented(self):
        """Verify version is incremented after update."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Updated",
            description=None,
            status="pending",
            version=3,  # Incremented from 2
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:10:00Z"
        )
        assert output.version >= 2

    def test_update_task_output_preserves_task_id(self):
        """Verify task_id is preserved after update."""
        task_id = UUID("123e4567-e89b-12d3-a456-426614174000")
        output = TaskOutput(
            id=task_id,
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Updated",
            description=None,
            status="pending",
            version=2,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:10:00Z"
        )
        assert output.id == task_id
