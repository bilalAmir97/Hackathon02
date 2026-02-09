"""Unit tests for task validation edge cases.

Tests validation logic for task creation and updates including:
- Title validation (length, whitespace, edge cases)
- Description validation (length, null handling)
- Status enum validation
- UUID validation
"""

import pytest
from pydantic import ValidationError

from src.domain.models import TaskStatus
from src.schemas.task import TaskCreate, TaskUpdate


class TestTaskCreateValidation:
    """Test validation for TaskCreate schema."""

    def test_title_empty_after_strip(self):
        """Test that title with only whitespace fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="   ", description="Valid description")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",)
            and ("empty" in error["msg"].lower() or "whitespace" in error["msg"].lower())
            for error in errors
        )

    def test_title_exactly_200_chars(self):
        """Test that title with exactly 200 characters is valid."""
        title = "a" * 200
        task = TaskCreate(title=title, description="Valid description")
        assert task.title == title
        assert len(task.title) == 200

    def test_title_201_chars_fails(self):
        """Test that title with 201 characters fails validation."""
        title = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title=title, description="Valid description")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",) and "at most 200 character" in error["msg"].lower()
            for error in errors
        )

    def test_title_minimum_length(self):
        """Test that title with 1 character is valid."""
        task = TaskCreate(title="a", description="Valid description")
        assert task.title == "a"
        assert len(task.title) == 1

    def test_title_empty_string_fails(self):
        """Test that empty title fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="", description="Valid description")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("title",) for error in errors)

    def test_title_missing_fails(self):
        """Test that missing title fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(description="Valid description")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",) and "field required" in error["msg"].lower()
            for error in errors
        )

    def test_description_exactly_2000_chars(self):
        """Test that description with exactly 2000 characters is valid."""
        description = "a" * 2000
        task = TaskCreate(title="Valid title", description=description)
        assert task.description == description
        assert len(task.description) == 2000

    def test_description_2001_chars_fails(self):
        """Test that description with 2001 characters fails validation."""
        description = "a" * 2001
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Valid title", description=description)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("description",) and "at most 2000 character" in error["msg"].lower()
            for error in errors
        )

    def test_description_none_is_valid(self):
        """Test that None description is valid."""
        task = TaskCreate(title="Valid title", description=None)
        assert task.description is None

    def test_description_empty_string_is_valid(self):
        """Test that empty string description is valid."""
        task = TaskCreate(title="Valid title", description="")
        assert task.description == ""

    def test_description_optional(self):
        """Test that description is optional (can be omitted)."""
        task = TaskCreate(title="Valid title")
        assert task.description is None

    def test_title_with_leading_trailing_whitespace(self):
        """Test that title with leading/trailing whitespace is stripped by validator."""
        # Note: Whitespace stripping happens in schema validation
        task = TaskCreate(title="  Valid title  ", description="Description")
        assert task.title == "Valid title"  # Whitespace is stripped by validator

    def test_title_with_special_characters(self):
        """Test that title with special characters is valid."""
        title = "Buy groceries! @#$%^&*() 123"
        task = TaskCreate(title=title, description="Description")
        assert task.title == title

    def test_title_with_unicode_characters(self):
        """Test that title with unicode characters is valid."""
        title = "Acheter des courses 🛒 日本語"
        task = TaskCreate(title=title, description="Description")
        assert task.title == title

    def test_description_with_newlines(self):
        """Test that description with newlines is valid."""
        description = "Line 1\nLine 2\nLine 3"
        task = TaskCreate(title="Valid title", description=description)
        assert task.description == description


class TestTaskUpdateValidation:
    """Test validation for TaskUpdate schema."""

    def test_all_fields_none_fails(self):
        """Test that update with all fields None fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title=None, description=None, status=None)

        errors = exc_info.value.errors()
        assert any(
            "at least one field must be provided" in error["msg"].lower() for error in errors
        )

    def test_empty_update_fails(self):
        """Test that update with no fields fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate()

        errors = exc_info.value.errors()
        assert any(
            "at least one field must be provided" in error["msg"].lower() for error in errors
        )

    def test_only_title_provided(self):
        """Test that update with only title is valid."""
        task = TaskUpdate(title="Updated title")
        assert task.title == "Updated title"
        assert task.description is None
        assert task.status is None

    def test_only_description_provided(self):
        """Test that update with only description is valid."""
        task = TaskUpdate(description="Updated description")
        assert task.title is None
        assert task.description == "Updated description"
        assert task.status is None

    def test_only_status_provided(self):
        """Test that update with only status is valid."""
        task = TaskUpdate(status=TaskStatus.COMPLETED)
        assert task.title is None
        assert task.description is None
        assert task.status == TaskStatus.COMPLETED

    def test_title_empty_after_strip_fails(self):
        """Test that update with whitespace-only title fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title="   ")

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",)
            and ("empty" in error["msg"].lower() or "whitespace" in error["msg"].lower())
            for error in errors
        )

    def test_title_201_chars_fails(self):
        """Test that update with 201-char title fails validation."""
        title = "a" * 201
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(title=title)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("title",) and "at most 200 character" in error["msg"].lower()
            for error in errors
        )

    def test_description_2001_chars_fails(self):
        """Test that update with 2001-char description fails validation."""
        description = "a" * 2001
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(description=description)

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("description",) and "at most 2000 character" in error["msg"].lower()
            for error in errors
        )

    def test_status_invalid_value_fails(self):
        """Test that update with invalid status value fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            TaskUpdate(status="invalid_status")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("status",) for error in errors)

    def test_status_pending_is_valid(self):
        """Test that update with pending status is valid."""
        task = TaskUpdate(status=TaskStatus.PENDING)
        assert task.status == TaskStatus.PENDING

    def test_status_completed_is_valid(self):
        """Test that update with completed status is valid."""
        task = TaskUpdate(status=TaskStatus.COMPLETED)
        assert task.status == TaskStatus.COMPLETED

    def test_multiple_fields_provided(self):
        """Test that update with multiple fields is valid."""
        task = TaskUpdate(
            title="Updated title", description="Updated description", status=TaskStatus.COMPLETED
        )
        assert task.title == "Updated title"
        assert task.description == "Updated description"
        assert task.status == TaskStatus.COMPLETED

    def test_description_empty_string_is_valid(self):
        """Test that update with empty string description is valid."""
        task = TaskUpdate(description="")
        assert task.description == ""


class TestTaskStatusEnum:
    """Test TaskStatus enum validation."""

    def test_pending_status_value(self):
        """Test that PENDING status has correct value."""
        assert TaskStatus.PENDING.value == "pending"

    def test_completed_status_value(self):
        """Test that COMPLETED status has correct value."""
        assert TaskStatus.COMPLETED.value == "completed"

    def test_status_from_string_pending(self):
        """Test creating status from string 'pending'."""
        status = TaskStatus("pending")
        assert status == TaskStatus.PENDING

    def test_status_from_string_completed(self):
        """Test creating status from string 'completed'."""
        status = TaskStatus("completed")
        assert status == TaskStatus.COMPLETED

    def test_status_invalid_string_fails(self):
        """Test that invalid status string raises ValueError."""
        with pytest.raises(ValueError):
            TaskStatus("invalid")

    def test_status_case_sensitive(self):
        """Test that status enum is case-sensitive."""
        with pytest.raises(ValueError):
            TaskStatus("PENDING")

        with pytest.raises(ValueError):
            TaskStatus("Completed")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_title_with_only_numbers(self):
        """Test that title with only numbers is valid."""
        task = TaskCreate(title="12345", description="Description")
        assert task.title == "12345"

    def test_title_with_emoji(self):
        """Test that title with emoji is valid."""
        task = TaskCreate(title="Buy groceries 🛒", description="Description")
        assert task.title == "Buy groceries 🛒"

    def test_description_with_html_tags(self):
        """Test that description with HTML tags is valid (not sanitized)."""
        description = "<script>alert('xss')</script>"
        task = TaskCreate(title="Valid title", description=description)
        assert task.description == description

    def test_title_boundary_199_chars(self):
        """Test that title with 199 characters is valid."""
        title = "a" * 199
        task = TaskCreate(title=title, description="Description")
        assert len(task.title) == 199

    def test_description_boundary_1999_chars(self):
        """Test that description with 1999 characters is valid."""
        description = "a" * 1999
        task = TaskCreate(title="Valid title", description=description)
        assert len(task.description) == 1999

    def test_title_with_tabs_and_newlines(self):
        """Test that title with tabs and newlines is accepted."""
        # Note: Whitespace handling happens in use case, not schema
        title = "Title\twith\ttabs\nand\nnewlines"
        task = TaskCreate(title=title, description="Description")
        assert task.title == title

    def test_description_null_vs_empty_string(self):
        """Test distinction between null and empty string description."""
        task_null = TaskCreate(title="Title", description=None)
        task_empty = TaskCreate(title="Title", description="")

        assert task_null.description is None
        assert task_empty.description == ""
        assert task_null.description != task_empty.description
