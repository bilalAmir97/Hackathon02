"""Unit tests for MCPAdapter retry and logging.

Task IDs: T022a, T022d
Tests MCP tool execution retry logic and structured logging.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.agent.mcp_adapter import MCPAdapter


class TestMCPAdapterRetry:
    """Test MCPAdapter tool execution retry on transient error (T022a)."""

    @pytest.mark.asyncio
    async def test_retry_on_connection_error(self):
        """Given a tool execution that fails with connection error then succeeds,
        when execute_tool is called, then it should retry and return success."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        # Mock the task operation to fail once then succeed
        with patch('src.use_cases.task_operations.create_task') as mock_create:
            mock_task = MagicMock()
            mock_task.id = uuid4()
            mock_task.title = "Test Task"
            mock_task.description = None
            mock_task.status.value = "pending"
            mock_task.created_at.isoformat.return_value = "2026-02-10T12:00:00"

            mock_create.side_effect = [ConnectionError("Connection failed"), mock_task]

            result = await adapter.execute_tool(
                session=session,
                tool_name="add_task",
                user_id=user_id,
                parameters={"title": "Test Task"}
            )

            assert "id" in result
            assert result["title"] == "Test Task"
            assert mock_create.call_count == 2

    @pytest.mark.asyncio
    async def test_retry_on_timeout_error(self):
        """Given a tool execution that times out then succeeds,
        when execute_tool is called, then it should retry and return success."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        with patch('src.use_cases.task_operations.list_tasks') as mock_list:
            mock_list.side_effect = [asyncio.TimeoutError(), []]

            result = await adapter.execute_tool(
                session=session,
                tool_name="list_tasks",
                user_id=user_id,
                parameters={}
            )

            assert "tasks" in result
            assert mock_list.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retry_attempts_exceeded(self):
        """Given a tool execution that always fails,
        when execute_tool is called, then it should fail after max attempts."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        with patch('src.use_cases.task_operations.create_task') as mock_create:
            mock_create.side_effect = ConnectionError("Persistent error")

            result = await adapter.execute_tool(
                session=session,
                tool_name="add_task",
                user_id=user_id,
                parameters={"title": "Test Task"}
            )

            # Should return error after retries
            assert "error" in result
            assert mock_create.call_count == 2  # max 2 attempts for tools


class TestMCPAdapterLogging:
    """Test MCPAdapter structured logging with latency_ms (T022d)."""

    @pytest.mark.asyncio
    async def test_logging_includes_latency(self):
        """Given a tool execution,
        when execute_tool is called, then structured log should include latency_ms."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        with patch('src.use_cases.task_operations.create_task') as mock_create, \
             patch('src.agent.mcp_adapter.logger') as mock_logger:

            mock_task = MagicMock()
            mock_task.id = uuid4()
            mock_task.title = "Test Task"
            mock_task.description = None
            mock_task.status.value = "pending"
            mock_task.created_at.isoformat.return_value = "2026-02-10T12:00:00"
            mock_create.return_value = mock_task

            result = await adapter.execute_tool(
                session=session,
                tool_name="add_task",
                user_id=user_id,
                parameters={"title": "Test Task"}
            )

            # Verify logging was called with latency_ms
            assert mock_logger.info.called
            log_call = mock_logger.info.call_args
            assert "extra" in log_call.kwargs
            extra = log_call.kwargs["extra"]
            assert "latency_ms" in extra
            assert extra["latency_ms"] >= 0

    @pytest.mark.asyncio
    async def test_logging_includes_tool_details(self):
        """Given a tool execution,
        when execute_tool is called, then log should include tool_name, input, output, status."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        with patch('src.use_cases.task_operations.list_tasks') as mock_list, \
             patch('src.agent.mcp_adapter.logger') as mock_logger:

            mock_list.return_value = []

            result = await adapter.execute_tool(
                session=session,
                tool_name="list_tasks",
                user_id=user_id,
                parameters={"status": "pending"}
            )

            # Verify logging includes all required fields
            assert mock_logger.info.called
            log_call = mock_logger.info.call_args
            extra = log_call.kwargs["extra"]
            assert extra["event"] == "tool_execution"
            assert extra["tool_name"] == "list_tasks"
            assert "input_parameters" in extra
            assert "output_result" in extra
            assert extra["execution_status"] == "success"
            assert "latency_ms" in extra

    @pytest.mark.asyncio
    async def test_logging_on_error(self):
        """Given a tool execution that fails,
        when execute_tool is called, then log should include error details."""
        adapter = MCPAdapter()
        session = MagicMock()
        user_id = str(uuid4())

        with patch('src.use_cases.task_operations.create_task') as mock_create, \
             patch('src.agent.mcp_adapter.logger') as mock_logger:

            mock_create.side_effect = ValueError("Invalid input")

            result = await adapter.execute_tool(
                session=session,
                tool_name="add_task",
                user_id=user_id,
                parameters={"title": "Test Task"}
            )

            # Verify error logging
            assert mock_logger.info.called
            log_call = mock_logger.info.call_args
            extra = log_call.kwargs["extra"]
            assert extra["execution_status"] == "error"
            assert "error_message" in extra
