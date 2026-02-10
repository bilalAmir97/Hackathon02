"""MCP tool for updating existing tasks.

This module implements the update_task tool that allows authenticated users
to update their tasks via the MCP protocol. Supports partial updates (title,
description, or both) with optimistic concurrency control.
"""

import logging
import time

from src.mcp.middleware.auth_context import extract_user_id, get_mcp_session
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error
from src.mcp.schemas.tool_inputs import UpdateTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput
from src.middleware.error_handler import DatabaseError, TaskNotFoundError
from src.schemas.task import TaskUpdate
from src.use_cases.task_operations import update_task as update_task_use_case

logger = logging.getLogger(__name__)


async def update_task(input_data: dict, headers: dict) -> dict:
    """Update an existing task for the authenticated user.

    Supports partial updates - can update title only, description only, or both.
    Uses optimistic locking to prevent concurrent modification conflicts.

    Args:
        input_data: Dictionary containing:
            - task_id (str): UUID of the task to update (required)
            - title (str, optional): New task title (1-200 chars)
            - description (str, optional): New task description (max 2000 chars)
        headers: Request headers containing authorization token

    Returns:
        Dictionary containing updated task data with incremented version

    Raises:
        Exception: With formatted MCP error for various failure scenarios:
            - UNAUTHORIZED: Missing or invalid auth token
            - INVALID_INPUT: Invalid task_id format or validation errors
            - TASK_NOT_FOUND: Task doesn't exist or doesn't belong to user
            - DATABASE_ERROR: Database operation failed or concurrent modification
            - INTERNAL_ERROR: Unexpected errors

    Example:
        input_data = {
            "task_id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "Updated title"
        }
        headers = {"authorization": "Bearer <token>"}
        result = await update_task(input_data, headers)
    """
    start_time = time.time()

    try:
        # Extract and validate user_id from JWT token
        try:
            user_id = extract_user_id(headers)
            logger.info(f"update_task: Authenticated user_id={user_id}")
        except Exception as e:
            logger.warning(f"update_task: Authentication failed - {str(e)}")
            raise Exception(format_mcp_error(
                MCPErrorCode.UNAUTHORIZED,
                "Authentication required. Please provide a valid authorization token."
            ))

        # Validate and parse input
        try:
            validated_input = UpdateTaskInput(**input_data)
            logger.info(
                f"update_task: Validated input for task_id={validated_input.task_id}, "
                f"title={'provided' if validated_input.title else 'not provided'}, "
                f"description={'provided' if validated_input.description else 'not provided'}"
            )
        except Exception as e:
            logger.warning(f"update_task: Input validation failed - {str(e)}")
            raise Exception(format_mcp_error(
                MCPErrorCode.INVALID_INPUT,
                f"Invalid input data: {str(e)}"
            ))

        # Prepare task update data
        task_update = TaskUpdate(
            title=validated_input.title,
            description=validated_input.description
        )

        # Update task using database session
        async with get_mcp_session() as session:
            try:
                updated_task = await update_task_use_case(
                    session=session,
                    user_id=user_id,
                    task_id=validated_input.task_id,
                    task_data=task_update
                )

                # Convert to output schema
                output = TaskOutput(
                    id=updated_task.id,
                    user_id=updated_task.user_id,
                    title=updated_task.title,
                    description=updated_task.description,
                    status=updated_task.status,
                    version=updated_task.version,
                    created_at=updated_task.created_at.isoformat(),
                    updated_at=updated_task.updated_at.isoformat()
                )

                execution_time = time.time() - start_time
                logger.info(
                    f"update_task: Successfully updated task_id={updated_task.id}, "
                    f"new_version={updated_task.version}, "
                    f"execution_time={execution_time:.3f}s"
                )

                return output.model_dump()

            except TaskNotFoundError:
                logger.warning(
                    f"update_task: Task not found - task_id={validated_input.task_id}, "
                    f"user_id={user_id}"
                )
                raise Exception(format_mcp_error(
                    MCPErrorCode.TASK_NOT_FOUND,
                    "Task not found or you don't have permission to update it."
                ))

            except DatabaseError as e:
                error_msg = str(e)
                logger.error(
                    f"update_task: Database error - task_id={validated_input.task_id}, "
                    f"error={error_msg}"
                )

                # Check if it's a concurrent modification error
                if "concurrent modification" in error_msg.lower():
                    raise Exception(format_mcp_error(
                        MCPErrorCode.DATABASE_ERROR,
                        "Task was modified by another process. Please retry with the latest version."
                    ))
                else:
                    raise Exception(format_mcp_error(
                        MCPErrorCode.DATABASE_ERROR,
                        f"Database operation failed: {error_msg}"
                    ))

            except Exception as e:
                logger.error(
                    f"update_task: Unexpected error during task update - "
                    f"task_id={validated_input.task_id}, error={str(e)}"
                )
                raise Exception(format_mcp_error(
                    MCPErrorCode.INTERNAL_ERROR,
                    f"Failed to update task: {str(e)}"
                ))

    except Exception as e:
        # If exception already contains formatted error, re-raise
        if isinstance(e.args[0], dict) and "error" in e.args[0]:
            raise

        # Otherwise, wrap in internal error
        logger.error(f"update_task: Unhandled error - {str(e)}")
        raise Exception(format_mcp_error(
            MCPErrorCode.INTERNAL_ERROR,
            f"An unexpected error occurred: {str(e)}"
        ))
