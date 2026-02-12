"""MCP complete_task tool implementation.

This module implements the complete_task tool that marks tasks as completed
for authenticated users. The tool is idempotent - completing an already-completed
task succeeds without error.
"""

import logging
import time

from pydantic import ValidationError

from src.domain.models import Task
from src.mcp.middleware.auth_context import extract_user_id, get_mcp_session
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error
from src.mcp.schemas.tool_inputs import CompleteTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput
from src.middleware.error_handler import TaskNotFoundError
from src.use_cases.task_operations import toggle_task_completion

logger = logging.getLogger(__name__)


async def complete_task(input_data: dict, headers: dict) -> dict:
    """Mark a task as completed for the authenticated user.

    This tool extracts the user_id from the JWT token in the Authorization
    header, validates the input data, and marks the task as completed.
    The operation is idempotent - completing an already-completed task
    succeeds without error.

    Args:
        input_data: Tool input containing task_id
        headers: HTTP headers containing Authorization header with JWT token

    Returns:
        dict: Updated task with status='completed' and incremented version

    Raises:
        Exception: Wrapped error response for authentication, validation,
                   ownership, or database failures

    Example:
        >>> headers = {"authorization": "Bearer eyJhbGc..."}
        >>> input_data = {"task_id": "123e4567-e89b-12d3-a456-426614174000"}
        >>> result = await complete_task(input_data, headers)
        >>> print(result["status"])
        'completed'
    """
    start_time = time.time()
    user_id = None
    task_id = None

    try:
        # Extract and verify user_id from JWT token
        user_id = extract_user_id(headers)
        logger.info(f"complete_task invoked by user_id={user_id}")

        # Validate input data
        validated_input = CompleteTaskInput(**input_data)
        task_id = validated_input.task_id

        # Create request-scoped database session
        async with get_mcp_session() as session:
            # Execute business logic (toggle handles idempotency)
            task: Task = await toggle_task_completion(session, user_id, task_id)

            # Convert domain model to MCP output
            output = TaskOutput(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                status=task.status.value,
                version=task.version,
                created_at=task.created_at.isoformat() + "Z",
                updated_at=task.updated_at.isoformat() + "Z"
            )

            execution_time = (time.time() - start_time) * 1000
            logger.info(
                f"complete_task completed successfully: user_id={user_id}, "
                f"task_id={task_id}, status={output.status}, "
                f"execution_time={execution_time:.2f}ms"
            )

            return output.model_dump()

    except ValidationError as e:
        # Input validation failed
        execution_time = (time.time() - start_time) * 1000
        logger.warning(
            f"complete_task validation failed: user_id={user_id}, "
            f"task_id={task_id}, execution_time={execution_time:.2f}ms, "
            f"errors={e.errors()}"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.INVALID_INPUT,
                "Input validation failed",
                {"errors": [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]}
            )
        )
    except TaskNotFoundError:
        # Task not found or doesn't belong to user
        execution_time = (time.time() - start_time) * 1000
        logger.warning(
            f"complete_task task not found: user_id={user_id}, "
            f"task_id={task_id}, execution_time={execution_time:.2f}ms"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.TASK_NOT_FOUND,
                f"Task with ID {task_id} not found",
                {}
            )
        )
    except Exception as e:
        # Check if it's already a formatted MCP error
        if isinstance(e.args[0], dict) and "error" in e.args[0]:
            execution_time = (time.time() - start_time) * 1000
            error_code = e.args[0]["error"]["code"]
            logger.error(
                f"complete_task failed: user_id={user_id}, task_id={task_id}, "
                f"error_code={error_code}, execution_time={execution_time:.2f}ms"
            )
            raise

        # Database or unexpected error
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            f"complete_task unexpected error: user_id={user_id}, "
            f"task_id={task_id}, execution_time={execution_time:.2f}ms, "
            f"error={str(e)}"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.DATABASE_ERROR,
                "Failed to complete task",
                {}
            )
        )
