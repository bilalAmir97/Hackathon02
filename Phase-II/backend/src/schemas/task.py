"""Pydantic schemas for task request/response validation.

Defines data transfer objects (DTOs) for task operations including
creation, updates, and responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from src.domain.models import TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new task.

    Attributes:
        title: Task title (1-200 characters, required)
        description: Task description (max 2000 characters, optional)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)",
        examples=["Buy groceries", "Complete project documentation"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters, optional)",
        examples=["Milk, eggs, bread", "Write comprehensive API documentation"],
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate and normalize title field.

        Strips whitespace and ensures title is not empty after stripping.

        Args:
            v: Title string to validate

        Returns:
            Stripped title string

        Raises:
            ValueError: If title is empty after stripping whitespace
        """
        # Strip whitespace
        v = v.strip()

        # Ensure not empty after stripping
        if not v:
            raise ValueError("Title cannot be empty or only whitespace")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                },
                {
                    "title": "Complete project documentation",
                    "description": None,
                },
            ]
        }
    }


class TaskUpdate(BaseModel):
    """Schema for updating an existing task.

    All fields are optional, but at least one field must be provided.
    Only provided fields will be updated (partial update support).

    Attributes:
        title: Task title (1-200 characters, optional)
        description: Task description (max 2000 characters, optional)
        status: Task status (pending or completed, optional)
    """

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters, optional)",
        examples=["Updated task title"],
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Task description (max 2000 characters, optional)",
        examples=["Updated description"],
    )

    status: TaskStatus | None = Field(
        default=None,
        description="Task status: pending or completed (optional)",
        examples=["completed"],
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        """Validate and normalize title field.

        Strips whitespace and ensures title is not empty after stripping.

        Args:
            v: Title string to validate (or None)

        Returns:
            Stripped title string or None

        Raises:
            ValueError: If title is empty after stripping whitespace
        """
        if v is None:
            return None

        # Strip whitespace
        v = v.strip()

        # Ensure not empty after stripping
        if not v:
            raise ValueError("Title cannot be empty or only whitespace")

        return v

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "TaskUpdate":
        """Validate that at least one field is provided for update.

        Raises:
            ValueError: If all fields are None
        """
        if self.title is None and self.description is None and self.status is None:
            raise ValueError("At least one field must be provided for update")

        return self

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated task title",
                    "description": "Updated description",
                    "status": "completed",
                },
                {
                    "title": "Only title updated",
                },
                {
                    "status": "completed",
                },
            ]
        }
    }


class TaskResponse(BaseModel):
    """Schema for task response data.

    Represents a complete task with all fields including metadata.
    Used for API responses when returning task data.

    Attributes:
        id: Unique task identifier (UUID v4)
        user_id: Owner reference (UUID v4)
        title: Task title
        description: Task description (optional)
        status: Task status (pending or completed)
        created_at: Task creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
    """

    id: UUID = Field(
        ...,
        description="Unique task identifier",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )

    user_id: UUID = Field(
        ...,
        description="Owner reference (user ID)",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    title: str = Field(
        ...,
        description="Task title",
        examples=["Buy groceries"],
    )

    description: str | None = Field(
        default=None,
        description="Task description (optional)",
        examples=["Milk, eggs, bread"],
    )

    status: TaskStatus = Field(
        ...,
        description="Task status: pending or completed",
        examples=["pending"],
    )

    created_at: datetime = Field(
        ...,
        description="Task creation timestamp (UTC)",
        examples=["2026-01-12T00:00:00Z"],
    )

    updated_at: datetime = Field(
        ...,
        description="Last update timestamp (UTC)",
        examples=["2026-01-12T00:00:00Z"],
    )

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLModel compatibility
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Complete project documentation",
                    "description": "Write comprehensive API documentation",
                    "status": "pending",
                    "created_at": "2026-01-12T00:00:00Z",
                    "updated_at": "2026-01-12T00:00:00Z",
                }
            ]
        },
    }


class PaginatedTaskResponse(BaseModel):
    """Schema for paginated task list response.

    Wraps a list of tasks with pagination metadata including total count,
    offset, limit, and navigation flags (has_next, has_previous).

    Attributes:
        items: List of tasks for the current page
        total: Total number of tasks matching the query
        offset: Current offset (starting position)
        limit: Maximum number of items per page
        has_next: Whether there are more items after this page
        has_previous: Whether there are items before this page
    """

    items: list[TaskResponse] = Field(
        ...,
        description="List of tasks for the current page",
        examples=[[]],
    )

    total: int = Field(
        ...,
        ge=0,
        description="Total number of tasks matching the query",
        examples=[25],
    )

    offset: int = Field(
        ...,
        ge=0,
        description="Current offset (starting position)",
        examples=[0],
    )

    limit: int = Field(
        ...,
        ge=1,
        le=100,
        description="Maximum number of items per page",
        examples=[20],
    )

    has_next: bool = Field(
        ...,
        description="Whether there are more items after this page",
        examples=[True],
    )

    has_previous: bool = Field(
        ...,
        description="Whether there are items before this page",
        examples=[False],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "status": "pending",
                            "created_at": "2026-01-12T00:00:00Z",
                            "updated_at": "2026-01-12T00:00:00Z",
                        }
                    ],
                    "total": 25,
                    "offset": 0,
                    "limit": 20,
                    "has_next": True,
                    "has_previous": False,
                }
            ]
        }
    }


class TaskListParams(BaseModel):
    """Schema for task list query parameters.

    Validates and normalizes query parameters for listing tasks including
    optional status filtering and pagination parameters.

    Attributes:
        status: Optional status filter (pending or completed)
        offset: Starting position for pagination (default: 0, min: 0)
        limit: Maximum items per page (default: 20, min: 1, max: 100)
    """

    status: TaskStatus | None = Field(
        default=None,
        description="Optional status filter (pending or completed)",
        examples=["pending", "completed", None],
    )

    offset: int = Field(
        default=0,
        ge=0,
        description="Starting position for pagination (min: 0)",
        examples=[0, 10, 20],
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum items per page (min: 1, max: 100)",
        examples=[10, 20, 50],
    )

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Validate offset is non-negative.

        Args:
            v: Offset value to validate

        Returns:
            Validated offset value

        Raises:
            ValueError: If offset is negative
        """
        if v < 0:
            raise ValueError("Offset must be greater than or equal to 0")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit is within acceptable range.

        Args:
            v: Limit value to validate

        Returns:
            Validated limit value

        Raises:
            ValueError: If limit is outside range [1, 100]
        """
        if v < 1:
            raise ValueError("Limit must be at least 1")
        if v > 100:
            raise ValueError("Limit must not exceed 100")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "pending",
                    "offset": 0,
                    "limit": 20,
                },
                {
                    "status": None,
                    "offset": 10,
                    "limit": 10,
                },
            ]
        }
    }
