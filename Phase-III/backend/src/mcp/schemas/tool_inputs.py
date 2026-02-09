"""MCP tool input schemas.

This module defines Pydantic models for validating MCP tool inputs.
All schemas follow the contracts defined in contracts/mcp-tools.json.
"""

from uuid import UUID

from pydantic import BaseModel, Field


class AddTaskInput(BaseModel):
    """Input schema for add_task tool.

    Attributes:
        title: Task title (1-200 characters, required)
        description: Optional task description (max 2000 characters)
    """

    title: str = Field(
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Optional task description (max 2000 characters)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Buy groceries",
                    "description": "Milk, eggs, bread"
                }
            ]
        }
    }


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool.

    Attributes:
        status: Filter tasks by status (all, pending, completed)
    """

    status: str = Field(
        default="all",
        pattern="^(all|pending|completed)$",
        description="Filter tasks by status"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "all"},
                {"status": "pending"},
                {"status": "completed"}
            ]
        }
    }


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool.

    Attributes:
        task_id: UUID of the task to update (required)
        title: New task title (optional, 1-200 characters)
        description: New task description (optional, max 2000 characters)
    """

    task_id: UUID = Field(
        description="UUID of the task to update"
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="New task title (optional)"
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="New task description (optional)"
    )


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool.

    Attributes:
        task_id: UUID of the task to complete (required)
    """

    task_id: UUID = Field(
        description="UUID of the task to complete"
    )


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool.

    Attributes:
        task_id: UUID of the task to delete (required)
    """

    task_id: UUID = Field(
        description="UUID of the task to delete"
    )
