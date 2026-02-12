"""MCP add_task tool implementation.

This module implements the add_task tool that creates new todo tasks
for authenticated users. The tool extracts user_id from JWT token,
validates input, and persists tasks to the database.
"""

import logging
import time

from pydantic import ValidationError

from src.domain.models import Task
from src.mcp.middleware.auth_context import extract_user_id, get_mcp_session
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error
from src.mcp.schemas.tool_inputs import AddTaskInput
from src.mcp.schemas.tool_outputs import TaskOutput
from src.schemas.task import TaskCreate
from src.use_cases.task_operations import create_task

logger = logging.getLogger(__name__)


async def add_task(input_data: dict, headers: dict) -> dict:
    """Create a new todo task for the authenticated user.

    This tool extracts the user_id from the JWT token in the Authorization
    header, validates the input data, and creates a new task in the database.
    All tasks are created with pending status and version 1.

    Args:
        input_data: Tool input containing title and optional description
        headers: HTTP headers containing Authorization header with JWT token

    Returns:
        dict: Created task with id, user_id, title, description, status,
              version, created_at, and updated_at fields

    Raises:
        Exception: Wrapped error response for authentication, validation,
                   or database failures

    Example:
        >>> headers = {"authorization": "Bearer eyJhbGc..."}
        >>> input_data = {"title": "Buy groceries", "description": "Milk, eggs"}
        >>> result = await add_task(input_data, headers)
        >>> print(result["id"])
        '123e4567-e89b-12d3-a456-426614174000'
    """
    start_time = time.time()
    user_id = None
    task_id = None

    try:
        # Extract and verify user_id from JWT token
        user_id = extract_user_id(headers)
        logger.info(f"add_task invoked by user_id={user_id}")

        # Validate input data
        validated_input = AddTaskInput(**input_data)

        # Create request-scoped database session
        async with get_mcp_session() as session:
            # Convert MCP input to use case input
            task_data = TaskCreate(
                title=validated_input.title,
                description=validated_input.description
            )

            # Execute business logic
            task: Task = await create_task(session, user_id, task_data)
            task_id = task.id

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
                f"add_task completed successfully: user_id={user_id}, "
                f"task_id={task_id}, execution_time={execution_time:.2f}ms"
            )

            return output.model_dump()

    except ValidationError as e:
        # Input validation failed
        execution_time = (time.time() - start_time) * 1000
        logger.warning(
            f"add_task validation failed: user_id={user_id}, "
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
                f"add_task failed: user_id={user_id}, task_id={task_id}, "
                f"error_code={error_code}, execution_time={execution_time:.2f}ms"
            )
            raise

        # Database or unexpected error
        execution_time = (time.time() - start_time) * 1000
        logger.error(
            f"add_task unexpected error: user_id={user_id}, task_id={task_id}, "
            f"execution_time={execution_time:.2f}ms, error={str(e)}"
        )
        raise Exception(
            format_mcp_error(
                MCPErrorCode.DATABASE_ERROR,
                "Failed to create task",
                {}
            )
        )
