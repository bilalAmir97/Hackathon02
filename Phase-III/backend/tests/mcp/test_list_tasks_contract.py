"""Contract tests for list_tasks tool.

This module validates that the list_tasks tool implementation matches the
contract defined in contracts/mcp-tools.json. Tests verify input/output
schemas, filtering, and response structure.
"""

import pytest

from src.mcp.schemas.tool_inputs import ListTasksInput
from src.mcp.schemas.tool_outputs import TaskListOutput, TaskOutput


class TestListTasksInputContract:
    """Test list_tasks input schema contract compliance."""

    def test_list_tasks_input_status_default(self):
        """Verify status defaults to 'all'."""
        input_data = ListTasksInput()
        assert input_data.status == "all"

    def test_list_tasks_input_accepts_all(self):
        """Verify status accepts 'all' value."""
        input_data = ListTasksInput(status="all")
        assert input_data.status == "all"

    def test_list_tasks_input_accepts_pending(self):
        """Verify status accepts 'pending' value."""
        input_data = ListTasksInput(status="pending")
        assert input_data.status == "pending"

    def test_list_tasks_input_accepts_completed(self):
        """Verify status accepts 'completed' value."""
        input_data = ListTasksInput(status="completed")
        assert input_data.status == "completed"

    def test_list_tasks_input_rejects_invalid_status(self):
        """Verify status rejects invalid values."""
        with pytest.raises(Exception):
            ListTasksInput(status="invalid")


class TestListTasksOutputContract:
    """Test list_tasks output schema contract compliance."""

    def test_list_tasks_output_has_required_fields(self):
        """Verify output has tasks and count fields."""
        output = TaskListOutput(tasks=[], count=0)
        assert output.tasks == []
        assert output.count == 0

    def test_list_tasks_output_tasks_is_array(self):
        """Verify tasks field is an array."""
        output = TaskListOutput(tasks=[], count=0)
        assert isinstance(output.tasks, list)

    def test_list_tasks_output_count_is_integer(self):
        """Verify count field is an integer."""
        output = TaskListOutput(tasks=[], count=5)
        assert isinstance(output.count, int)
        assert output.count == 5

    def test_list_tasks_output_with_tasks(self):
        """Verify output can contain task objects."""
        from uuid import UUID

        task = TaskOutput(
            id=UUID("123e4567-e89b-12d3-a456-426614174000"),
            user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
            title="Test task",
            description=None,
            status="pending",
            version=1,
            created_at="2026-02-09T10:00:00Z",
            updated_at="2026-02-09T10:00:00Z"
        )

        output = TaskListOutput(tasks=[task], count=1)
        assert len(output.tasks) == 1
        assert output.tasks[0].title == "Test task"
        assert output.count == 1

    def test_list_tasks_output_count_matches_array_length(self):
        """Verify count field matches tasks array length."""
        from uuid import UUID

        tasks = [
            TaskOutput(
                id=UUID("123e4567-e89b-12d3-a456-426614174000"),
                user_id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                title=f"Task {i}",
                description=None,
                status="pending",
                version=1,
                created_at="2026-02-09T10:00:00Z",
                updated_at="2026-02-09T10:00:00Z"
            )
            for i in range(3)
        ]

        output = TaskListOutput(tasks=tasks, count=3)
        assert len(output.tasks) == output.count
