"""Contract tests for MCP tool schemas.

This module validates that all MCP tool schemas match the contracts defined
in contracts/mcp-tools.json. These tests ensure API contract compliance and
prevent breaking changes to tool interfaces.
"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def mcp_tool_contracts():
    """Load MCP tool contracts from contracts/mcp-tools.json."""
    contracts_path = Path(__file__).parent.parent.parent.parent / "specs" / "001-phase-iii-mcp-server" / "contracts" / "mcp-tools.json"
    with open(contracts_path) as f:
        return json.load(f)


class TestAddTaskContract:
    """Contract tests for add_task tool."""

    def test_add_task_input_schema(self, mcp_tool_contracts):
        """Verify add_task input schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "add_task")
        input_schema = tool["inputSchema"]

        # Verify required fields
        assert "title" in input_schema["required"]
        assert input_schema["properties"]["title"]["type"] == "string"
        assert input_schema["properties"]["title"]["minLength"] == 1
        assert input_schema["properties"]["title"]["maxLength"] == 200

        # Verify optional description
        assert "description" not in input_schema["required"]
        assert input_schema["properties"]["description"]["type"] == "string"
        assert input_schema["properties"]["description"]["maxLength"] == 2000

    def test_add_task_output_schema(self, mcp_tool_contracts):
        """Verify add_task output schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "add_task")
        output_schema = tool["outputSchema"]

        # Verify all required fields present
        required_fields = ["id", "user_id", "title", "status", "version", "created_at", "updated_at"]
        for field in required_fields:
            assert field in output_schema["required"]
            assert field in output_schema["properties"]

        # Verify field types
        assert output_schema["properties"]["id"]["format"] == "uuid"
        assert output_schema["properties"]["user_id"]["format"] == "uuid"
        assert output_schema["properties"]["status"]["enum"] == ["pending", "completed"]
        assert output_schema["properties"]["version"]["type"] == "integer"


class TestListTasksContract:
    """Contract tests for list_tasks tool."""

    def test_list_tasks_input_schema(self, mcp_tool_contracts):
        """Verify list_tasks input schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "list_tasks")
        input_schema = tool["inputSchema"]

        # Verify status filter
        assert input_schema["properties"]["status"]["enum"] == ["all", "pending", "completed"]
        assert input_schema["properties"]["status"]["default"] == "all"

    def test_list_tasks_output_schema(self, mcp_tool_contracts):
        """Verify list_tasks output schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "list_tasks")
        output_schema = tool["outputSchema"]

        # Verify required fields
        assert "tasks" in output_schema["required"]
        assert "count" in output_schema["required"]

        # Verify tasks array structure
        assert output_schema["properties"]["tasks"]["type"] == "array"
        assert output_schema["properties"]["count"]["type"] == "integer"


class TestUpdateTaskContract:
    """Contract tests for update_task tool."""

    def test_update_task_input_schema(self, mcp_tool_contracts):
        """Verify update_task input schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "update_task")
        input_schema = tool["inputSchema"]

        # Verify task_id required
        assert "task_id" in input_schema["required"]
        assert input_schema["properties"]["task_id"]["format"] == "uuid"

        # Verify optional fields
        assert "title" not in input_schema["required"]
        assert "description" not in input_schema["required"]


class TestCompleteTaskContract:
    """Contract tests for complete_task tool."""

    def test_complete_task_input_schema(self, mcp_tool_contracts):
        """Verify complete_task input schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "complete_task")
        input_schema = tool["inputSchema"]

        # Verify task_id required
        assert "task_id" in input_schema["required"]
        assert input_schema["properties"]["task_id"]["format"] == "uuid"


class TestDeleteTaskContract:
    """Contract tests for delete_task tool."""

    def test_delete_task_input_schema(self, mcp_tool_contracts):
        """Verify delete_task input schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "delete_task")
        input_schema = tool["inputSchema"]

        # Verify task_id required
        assert "task_id" in input_schema["required"]
        assert input_schema["properties"]["task_id"]["format"] == "uuid"

    def test_delete_task_output_schema(self, mcp_tool_contracts):
        """Verify delete_task output schema matches contract."""
        tool = next(t for t in mcp_tool_contracts["tools"] if t["name"] == "delete_task")
        output_schema = tool["outputSchema"]

        # Verify required fields
        assert "message" in output_schema["required"]
        assert "task_id" in output_schema["required"]
        assert output_schema["properties"]["task_id"]["format"] == "uuid"
