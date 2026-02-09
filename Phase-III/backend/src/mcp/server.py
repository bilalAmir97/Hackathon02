"""MCP server initialization and tool registration.

This module sets up the MCP server instance and provides the entry point
for running the server. Tools are registered here and the server listens
on stdio for MCP protocol communication.
"""

from mcp.server import Server
from mcp.server.stdio import stdio_server

from src.config import settings
from src.mcp.tools.add_task import add_task
from src.mcp.tools.list_tasks import list_tasks
from src.mcp.tools.complete_task import complete_task
from src.mcp.tools.update_task import update_task
from src.mcp.tools.delete_task import delete_task

# Initialize MCP server instance
app = Server("todo-mcp-server")


# Register MCP tools
@app.tool()
async def add_task_tool(title: str, description: str | None = None) -> dict:
    """Create a new todo task for the authenticated user.

    Args:
        title: Task title (1-200 characters, required)
        description: Optional task description (max 2000 characters)

    Returns:
        Created task with id, user_id, title, description, status, version, timestamps
    """
    headers = {}  # TODO: Extract from MCP request context
    input_data = {"title": title, "description": description}
    return await add_task(input_data, headers)


@app.tool()
async def list_tasks_tool(status: str = "all") -> dict:
    """Retrieve tasks for the authenticated user with optional status filtering.

    Args:
        status: Filter tasks by status (all, pending, completed) - default: all

    Returns:
        TaskListOutput with tasks array and count
    """
    headers = {}  # TODO: Extract from MCP request context
    input_data = {"status": status}
    return await list_tasks(input_data, headers)


@app.tool()
async def complete_task_tool(task_id: str) -> dict:
    """Mark a task as completed for the authenticated user.

    Args:
        task_id: UUID of the task to complete

    Returns:
        Updated task with status='completed' and incremented version
    """
    headers = {}  # TODO: Extract from MCP request context
    input_data = {"task_id": task_id}
    return await complete_task(input_data, headers)


@app.tool()
async def update_task_tool(task_id: str, title: str | None = None, description: str | None = None) -> dict:
    """Update an existing task for the authenticated user.

    Supports partial updates - can update title only, description only, or both.
    Uses optimistic locking to prevent concurrent modification conflicts.

    Args:
        task_id: UUID of the task to update (required)
        title: New task title (1-200 characters, optional)
        description: New task description (max 2000 characters, optional)

    Returns:
        Updated task with incremented version and updated timestamp
    """
    headers = {}  # TODO: Extract from MCP request context
    input_data = {"task_id": task_id, "title": title, "description": description}
    return await update_task(input_data, headers)


@app.tool()
async def delete_task_tool(task_id: str) -> dict:
    """Delete a task for the authenticated user.

    Permanently removes the task from the database. This operation cannot be undone.
    Enforces ownership validation to ensure users can only delete their own tasks.

    Args:
        task_id: UUID of the task to delete

    Returns:
        Deletion confirmation with success flag, task_id, and message
    """
    headers = {}  # TODO: Extract from MCP request context
    input_data = {"task_id": task_id}
    return await delete_task(input_data, headers)


async def main():
    """Run MCP server on stdio.

    This is the main entry point for the MCP server. It starts the server
    and listens for tool invocations via stdio (standard input/output).

    The server runs indefinitely until terminated by the parent process.

    Example:
        Run the server:
        $ uv run python -m src.mcp.server
    """
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
