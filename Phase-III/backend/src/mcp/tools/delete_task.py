"""MCP tool for deleting tasks.

This module implements the delete_task tool that allows authenticated users
to permanently delete their tasks via the MCP protocol. Enforces ownership
validation to prevent unauthorized deletions.
"""

import logging
import time

from src.mcp.middleware.auth_context import extract_user_id, get_mcp_session
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error
from src.mcp.schemas.tool_inputs import DeleteTaskInput
from src.mcp.schemas.tool_outputs import DeleteTaskOutput
from src.middleware.error_handler import DatabaseError, TaskNotFoundError
from src.use_cases.task_operations import delete_task as delete_task_use_case

logger = logging.getLogger(__name__)


async def delete_task(input_data: dict, headers: dict) -> dict:
    """Delete a task for the authenticated user.

    Permanently removes the task from the database. This operation cannot be
    undone. Enforces ownership validation to ensure users can only delete
    their own tasks.

    Args:
        input_data: Dictionary containing:
            - task_id (str): UUID of the task to delete (required)
        headers: Request headers containing authorization token

    Returns:
        Dictionary containing deletion confirmation with success flag,
        task_id, and confirmation message

    Raises:
        Exception: With formatted MCP error for various failure scenarios:
            - UNAUTHORIZED: Missing or invalid auth token
            - INVALID_INPUT: Invalid task_id format
            - TASK_NOT_FOUND: Task doesn't exist or doesn't belong to user
            - DATABASE_ERROR: Database operation failed
            - INTERNAL_ERROR: Unexpected errors

    Example:
        input_data = {"task_id": "123e4567-e89b-12d3-a456-426614174000"}
        headers = {"authorization": "Bearer <token>"}
        result = await delete_task(input_data, headers)
    """
    start_time = time.time()

    try:
        # Extract and validate user_id from JWT token
        try:
            user_id = extract_user_id(headers)
            logger.info(f"delete_task: Authenticated user_id={user_id}")
        except Exception as e:
            logger.warning(f"delete_task: Authentication failed - {str(e)}")
            raise Exception(format_mcp_error(
                MCPErrorCode.UNAUTHORIZED,
                "Authentication required. Please provide a valid authorization token."
            ))

        # Validate and parse input
        try:
            validated_input = DeleteTaskInput(**input_data)
            logger.info(f"delete_task: Validated input for task_id={validated_input.task_id}")
        except Exception as e:
            logger.warning(f"delete_task: Input validation failed - {str(e)}")
            raise Exception(format_mcp_error(
                MCPErrorCode.INVALID_INPUT,
                f"Invalid input data: {str(e)}"
            ))

        # Delete task using database session
        async with get_mcp_session() as session:
            try:
                await delete_task_use_case(
                    session=session,
                    user_id=user_id,
                    task_id=validated_input.task_id
                )

                # Create success output
                output = DeleteTaskOutput(
                    success=True,
                    task_id=validated_input.task_id,
                    message="Task deleted successfully"
                )

                execution_time = time.time() - start_time
                logger.info(
                    f"delete_task: Successfully deleted task_id={validated_input.task_id}, "
                    f"execution_time={execution_time:.3f}s"
                )

                return output.model_dump()

            except TaskNotFoundError:
                logger.warning(
                    f"delete_task: Task not found - task_id={validated_input.task_id}, "
                    f"user_id={user_id}"
                )
                raise Exception(format_mcp_error(
                    MCPErrorCode.TASK_NOT_FOUND,
                    "Task not found or you don't have permission to delete it."
                ))

            except DatabaseError as e:
                error_msg = str(e)
                logger.error(
                    f"delete_task: Database error - task_id={validated_input.task_id}, "
                    f"error={error_msg}"
                )
                raise Exception(format_mcp_error(
                    MCPErrorCode.DATABASE_ERROR,
                    f"Database operation failed: {error_msg}"
                ))

            except Exception as e:
                logger.error(
                    f"delete_task: Unexpected error during task deletion - "
                    f"task_id={validated_input.task_id}, error={str(e)}"
                )
                raise Exception(format_mcp_error(
                    MCPErrorCode.INTERNAL_ERROR,
                    f"Failed to delete task: {str(e)}"
                ))

    except Exception as e:
        # If exception already contains formatted error, re-raise
        if isinstance(e.args[0], dict) and "error" in e.args[0]:
            raise

        # Otherwise, wrap in internal error
        logger.error(f"delete_task: Unhandled error - {str(e)}")
        raise Exception(format_mcp_error(
            MCPErrorCode.INTERNAL_ERROR,
            f"An unexpected error occurred: {str(e)}"
        ))
