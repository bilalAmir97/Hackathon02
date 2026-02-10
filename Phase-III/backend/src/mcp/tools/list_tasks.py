"""MCP list_tasks tool implementation.

This module implements the list_tasks tool that retrieves todo tasks
for authenticated users with optional status filtering. Tasks are returned
ordered by creation time (newest first).
"""

import logging
import time

from pydantic import ValidationError

from src.domain.models import Task, TaskStatus
from src.mcp.middleware.auth_context import extract_user_id, get_mcp_session
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error
from src.mcp.schemas.tool_inputs import ListTasksInput
from src.mcp.schemas.tool_outputs import TaskListOutput, TaskOutput
from src.use_cases.task_operations import list_tasks as list_tasks_use_case

logger = logging.getLogger(__name__)


async def list_tasks(input_data: dict, headers: dict) -> dict:
    """Retrieve tasks for the authenticated user with optional status filtering.

    This tool extracts the user_id from the JWT token in the Authorization
    header, validates the input data, and retrieves tasks from the database.
    Tasks are returned ordered by creation time (newest first).

    Args:
        input_data: Tool input containing optional status filter
        headers: HTTP headers containing Authorization header with JWT token

    Returns:
        dict: TaskListOutput with tasks array and count

    Raises:
        Exception: Wrapped error response for authentication, validation,
                   or database failures

    Example:
        >>> headers = {"authorization": "Bearer eyJhbGc..."}
        >>> input_data = {"status": "pending"}
        >>> result = await list_tasks(input_data, headers)
        >>> print(result["count"])
        5
    """
    start_time = time.time()
    user_id = None

    try:
        # Extract and verify user_id from JWT token
        user_id = extract_user_id(headers)
        logger.info(f"list_tasks invoked by user_id={user_id}")

        # Validate input data
        validated_input = ListTasksInput(**input_data)

        # Map string status to TaskStatus enum or None
        status_filter = None
        if validated_input.status == "pending":
            status_filter = TaskStatus.PENDING
        elif validated_input.status == "completed":
            status_filter = TaskStatus.COMPLETED
        # "all" maps to None (no filter)

        # Create request-scoped database session
        async with get_mcp_session() as session:
            # Execute business logic (no pagination for MCP - return all matching tasks)
            tasks: list[Task] = await list_tasks_use_case(
                session,
                user_id,
                status=status_filter,
                offset=0,
                limit=1000  # High limit to return all tasks
            )

            # Convert domain models to MCP output
            task_outputs = [
                TaskOutput(
                    id=task.id,
                    user_id=task.user_id,
                    title=task.title,
                    description=task.description,
                    status=task.status.value,
                    version=task.version,
                    created_at=task.created_at.isoformat() + "Z",
                    updated_at=task.updated_at.isoformat() + "Z"
                )
                for task in tasks
            ]

            output = TaskListOutput(
                tasks=task_outputs,
                count=len(task_outputs)
            )

            execution_time = (time.time() - start_time) * 1000
            logger.info(
                f"list_tasks completed successfully: user_id={user_id}, "
                f"status_filter={validated_input.status}, count={output.count}, "
                f"execution_time={execution_time:.2f}ms"
            )

            return output.model_dump()

    except ValidationError as e:
        # Input validation failed
        execution_time = (time.time() - start_time) * 1000
        logger.warning(
            f"list_tasks validation failed: user_id={user_id}, "
            f"execution_time={execution_time:.2f}ms, errors={e.errors()}"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.INVALID_INPUT,
                "Input validation failed",
                {"errors": [{"field": err["loc"][0], "message": err["msg"]} for err in e.errors()]}
            )
        )
    except Exception as e:
        # Check if it's already a formatted MCP error
        if isinstance(e.args[0], dict) and "error" in e.args[0]:
            execution_time = (time.time() - start_time) * 1000
            error_code = e.args[0]["error"]["code"]
            logger.error(
                f"list_tasks failed: user_id={user_id}, "
                f"error_code={error_code}, execution_time={execution_time:.2f}ms"
            )
            raise

        # Database or unexpected error
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            f"list_tasks unexpected error: user_id={user_id}, "
            f"execution_time={execution_time:.2f}ms, error={str(e)}"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.DATABASE_ERROR,
                "Failed to retrieve tasks",
                {}
            )
        )
