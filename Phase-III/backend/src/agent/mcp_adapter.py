"""MCP Adapter for OpenAI Agents SDK.

This module provides an adapter that wraps existing MCP tools and makes them
compatible with OpenAI Agents SDK function calling format. It handles user_id
context injection, retry logic, and structured logging for tool execution.

Task IDs: T022b, T022e
"""

import logging
import time
from typing import Any
from uuid import UUID

from src.agent.retry_policy import RetryPolicy
from src.use_cases.task_operations import (
    create_task,
    toggle_task_completion,
)
from src.use_cases.task_operations import (
    delete_task as delete_task_op,
)
from src.use_cases.task_operations import (
    list_tasks as list_tasks_op,
)
from src.use_cases.task_operations import (
    update_task as update_task_op,
)

logger = logging.getLogger(__name__)


class MCPAdapter:
    """Adapter for MCP tools to work with OpenAI Agents SDK.
    
    This adapter wraps the existing MCP tools (add_task, list_tasks, etc.)
    and provides them in OpenAI function calling format. It also handles
    user_id context injection for all tool calls.
    """

    def __init__(self):
        """Initialize the MCP adapter with retry policy."""
        self._tools = self._define_tools()
        # Initialize retry policy for tool execution (max 2 attempts)
        self._retry_policy = RetryPolicy(max_attempts=2, initial_delay_ms=100, max_delay_ms=5000)

    def get_tools(self) -> list[dict[str, Any]]:
        """Get all MCP tools in OpenAI function calling format.
        
        Returns:
            List of tool definitions with name, description, and parameters.
        """
        return self._tools

    def _define_tools(self) -> list[dict[str, Any]]:
        """Define all MCP tools in OpenAI function calling format.
        
        Returns:
            List of tool definitions following OpenAI function calling schema.
        """
        return [
            {
                "name": "add_task",
                "description": "Create a new task for the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (1-200 characters)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description (max 2000 characters)"
                        }
                    },
                    "required": ["title"]
                }
            },
            {
                "name": "list_tasks",
                "description": "List all tasks for the user, optionally filtered by status",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["pending", "completed"],
                            "description": "Filter tasks by status (optional)"
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "update_task",
                "description": "Update an existing task's title or description",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to update"
                        },
                        "title": {
                            "type": "string",
                            "description": "New task title (optional)"
                        },
                        "description": {
                            "type": "string",
                            "description": "New task description (optional)"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to complete"
                        }
                    },
                    "required": ["task_id"]
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "UUID of the task to delete"
                        }
                    },
                    "required": ["task_id"]
                }
            }
        ]

    async def execute_tool(
        self,
        session: Any,
        tool_name: str,
        user_id: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute an MCP tool with user context, retry logic, and structured logging.

        Args:
            session: Database session to use for tool execution
            tool_name: Name of the tool to execute
            user_id: User ID for context injection
            parameters: Tool parameters

        Returns:
            Tool execution result with structured logging

        Raises:
            ValueError: If tool_name is not recognized
        """
        start_time = time.time()
        execution_status = "success"
        error_message = None
        output_result = None
        # Import MCP tools dynamically to avoid circular imports

        # Validate tool name
        valid_tools = ['add_task', 'list_tasks', 'update_task', 'complete_task', 'delete_task']
        if tool_name not in valid_tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        try:
            # Execute tool with retry logic
            output_result = await self._retry_policy.execute_with_retry(
                self._execute_tool_internal,
                session,
                tool_name,
                user_id,
                parameters
            )
        except Exception as e:
            execution_status = "error"
            error_message = str(e)
            output_result = {
                'error': str(e),
                'tool_name': tool_name
            }
        finally:
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Structured logging
            logger.info(
                f"Tool execution: {tool_name}",
                extra={
                    "event": "tool_execution",
                    "tool_name": tool_name,
                    "input_parameters": parameters,
                    "output_result": output_result,
                    "execution_status": execution_status,
                    "error_message": error_message,
                    "latency_ms": latency_ms,
                }
            )

        return output_result

    async def _execute_tool_internal(
        self,
        session: Any,
        tool_name: str,
        user_id: str,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Internal method to execute tool (called by retry policy).

        Args:
            session: Database session
            tool_name: Tool name
            user_id: User ID
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        try:
            # Execute the appropriate tool using the provided session
            if tool_name == 'add_task':
                from src.schemas.task import TaskCreate

                task_data = TaskCreate(
                    title=parameters['title'],
                    description=parameters.get('description')
                )
                result = await create_task(
                    session=session,
                    user_id=UUID(user_id),
                    task_data=task_data
                )
                return {
                    'id': str(result.id),
                    'title': result.title,
                    'description': result.description,
                    'status': result.status.value,
                    'created_at': result.created_at.isoformat()
                }

            elif tool_name == 'list_tasks':
                status_filter = parameters.get('status')
                # Convert string status to TaskStatus enum if provided
                from src.domain.models import TaskStatus
                status_enum = None
                if status_filter:
                    status_enum = TaskStatus(status_filter)

                results = await list_tasks_op(
                    session=session,
                    user_id=UUID(user_id),
                    status=status_enum
                )
                return {
                    'tasks': [
                        {
                            'id': str(task.id),
                            'title': task.title,
                            'description': task.description,
                            'status': task.status.value
                        }
                        for task in results
                    ],
                    'count': len(results)
                }

            elif tool_name == 'update_task':
                from src.schemas.task import TaskUpdate

                task_data = TaskUpdate(
                    title=parameters.get('title'),
                    description=parameters.get('description')
                )
                result = await update_task_op(
                    session=session,
                    user_id=UUID(user_id),
                    task_id=UUID(parameters['task_id']),
                    task_data=task_data
                )
                return {
                    'id': str(result.id),
                    'title': result.title,
                    'description': result.description,
                    'status': result.status.value
                }

            elif tool_name == 'complete_task':
                result = await toggle_task_completion(
                    session=session,
                    user_id=UUID(user_id),
                    task_id=UUID(parameters['task_id'])
                )
                return {
                    'id': str(result.id),
                    'title': result.title,
                    'status': result.status.value
                }

            elif tool_name == 'delete_task':
                await delete_task_op(
                    session=session,
                    user_id=UUID(user_id),
                    task_id=UUID(parameters['task_id'])
                )
                return {
                    'success': True,
                    'message': f'Task {parameters["task_id"]} deleted successfully'
                }

        except Exception:
            # Re-raise exception to be handled by retry policy
            raise
