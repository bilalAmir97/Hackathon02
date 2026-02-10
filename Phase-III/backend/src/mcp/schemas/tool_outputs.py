"""MCP tool output schemas.

This module defines Pydantic models for MCP tool outputs.
All schemas follow the contracts defined in contracts/mcp-tools.json.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class TaskOutput(BaseModel):
    """Output schema for task operations.

    This schema is used by add_task, list_tasks, update_task, and
    complete_task tools to return task data.

    Attributes:
        id: Unique task identifier (UUID v4)
        user_id: Owner user identifier (extracted from JWT token)
        title: Task title
        description: Task description (null if not provided)
        status: Task status (pending or completed)
        version: Version number for optimistic concurrency control
        created_at: Task creation timestamp (ISO 8601 UTC)
        updated_at: Last update timestamp (ISO 8601 UTC)
    """

    id: UUID = Field(description="Unique task identifier")
    user_id: UUID = Field(description="Owner user identifier")
    title: str = Field(description="Task title")
    description: str | None = Field(description="Task description")
    status: str = Field(description="Task status (pending or completed)")
    version: int = Field(description="Version number for optimistic concurrency control")
    created_at: str = Field(description="Task creation timestamp (ISO 8601 UTC)")
    updated_at: str = Field(description="Last update timestamp (ISO 8601 UTC)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread",
                    "status": "pending",
                    "version": 1,
                    "created_at": "2026-02-09T10:00:00Z",
                    "updated_at": "2026-02-09T10:00:00Z"
                }
            ]
        }
    }


class TaskListOutput(BaseModel):
    """Output schema for list_tasks tool.

    Attributes:
        tasks: Array of tasks ordered by created_at descending (newest first)
        count: Total number of tasks returned
    """

    tasks: list[TaskOutput] = Field(description="Array of tasks")
    count: int = Field(description="Total number of tasks returned")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tasks": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "user_id": "550e8400-e29b-41d4-a716-446655440000",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "status": "pending",
                            "version": 1,
                            "created_at": "2026-02-09T10:00:00Z",
                            "updated_at": "2026-02-09T10:00:00Z"
                        }
                    ],
                    "count": 1
                }
            ]
        }
    }


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool.

    Attributes:
        success: Boolean indicating successful deletion
        task_id: UUID of the deleted task
        message: Confirmation message
    """

    success: bool = Field(description="Boolean indicating successful deletion")
    task_id: UUID = Field(description="UUID of the deleted task")
    message: str = Field(description="Confirmation message")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "message": "Task deleted successfully"
                }
            ]
        }
    }
