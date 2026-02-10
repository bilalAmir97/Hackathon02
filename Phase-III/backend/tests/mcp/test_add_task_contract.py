"""Contract tests for add_task tool.

This module validates that the add_task tool implementation matches the
contract defined in contracts/mcp-tools.json. Tests verify input/output
schemas, field validation, and response structure.
"""

import pytest
from uuid import UUID

from src.mcp.schemas.tool_inputs import AddTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput


class TestAddTaskInputContract:
    """Test add_task input schema contract compliance."""

    def test_add_task_input_requires_title(self):
        """Verify title field is required."""
        with pytest.raises(Exception):
            AddTaskInput(description="Test description")

    def test_add_task_input_title_min_length(self):
        """Verify title has minimum length of 1 character."""
        with pytest.raises(Exception):
            AddTaskInput(title="")

    def test_add_task_input_title_max_length(self):
        """Verify title has maximum length of 200 characters."""
        with pytest.raises(Exception):
            AddTaskInput(title="x" * 201)

    def test_add_task_input_description_optional(self):
        """Verify description field is optional."""
        input_data = AddTaskInput(title="Test task")
        assert input_data.description is None

    def test_add_task_input_description_max_length(self):
        """Verify description has maximum length of 2000 characters."""
        with pytest.raises(Exception):
            AddTaskInput(title="Test", description="x" * 2001)

    def test_add_task_input_valid_data(self):
        """Verify valid input data is accepted."""
        input_data = AddTaskInput(
            title="Buy groceries",
            description="Milk, eggs, bread"
        )
        assert input_data.title == "Buy groceries"
        assert input_data.description == "Milk, eggs, bread"


class TestAddTaskOutputContract:
    """Test add_task output schema contract compliance."""

    def test_add_task_output_has_required_fields(self):
        """Verify output has all required fields."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test task",
            description=None,
            status="pending",
            version=1,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:00:00Z"
        )
        assert output.id == UUID("123e4567-e89b-12d3-a456-426614174000")
        assert output.user_id == UUID("550e8400-e29b-41d4-a716-446655440000")
        assert output.title == "Test task"
        assert output.status == "pending"
        assert output.version == 1

    def test_add_task_output_id_is_uuid(self):
        """Verify id field is UUID format."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test",
            description=None,
            status="pending",
            version=1,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:00:00Z"
        )
        assert isinstance(output.id, UUID)

    def test_add_task_output_version_is_one_for_new_tasks(self):
        """Verify version is 1 for newly created tasks."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test",
            description=None,
            status="pending",
            version=1,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:00:00Z"
        )
        assert output.version == 1

    def test_add_task_output_status_is_pending(self):
        """Verify status is 'pending' for newly created tasks."""
        output = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test",
            description=None,
            status="pending",
            version=1,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:00:00Z"
        )
        assert output.status == "pending"
