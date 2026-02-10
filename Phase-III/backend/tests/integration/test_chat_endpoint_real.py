"""End-to-end integration tests for /chat endpoint with real OpenAI Agents SDK.

These tests require API keys to be set:
- GROQ_API_KEY for primary provider
- OPENAI_API_KEY for fallback provider

Task ID: T037
"""

import pytest
import os
from uuid import uuid4
from httpx import AsyncClient

from src.main import create_app


# Skip all tests if API keys are not set
pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or not os.getenv("OPENAI_API_KEY"),
    reason="API keys not set (GROQ_API_KEY and OPENAI_API_KEY required)"
)


@pytest.fixture
async def client():
    """Create test client."""
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """Create authentication headers with test user ID."""
    user_id = str(uuid4())
    return {"X-User-ID": user_id}


class TestChatEndpointWithRealAgent:
    """End-to-end tests for /chat endpoint with real AI agent."""

    @pytest.mark.asyncio
    async def test_chat_create_task_end_to_end(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test complete flow: HTTP request → Agent → MCP tools → HTTP response.

        Verifies:
        - Chat endpoint accepts POST requests
        - Request is processed by real agent
        - Agent calls MCP tools
        - Response includes conversation_id, response, and tool_calls
        - Response format matches API contract
        """
        # Arrange
        payload = {
            "message": "Create a task to buy groceries"
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200

        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        assert "tool_calls" in data

        # Verify tool calls
        assert len(data["tool_calls"]) > 0
        tool_call = data["tool_calls"][0]
        assert tool_call["tool_name"] == "add_task"
        assert "buy groceries" in tool_call["input_parameters"]["title"].lower()
        assert tool_call["execution_status"] == "success"

        # Verify response is conversational
        assert isinstance(data["response"], str)
        assert len(data["response"]) > 0

    @pytest.mark.asyncio
    async def test_chat_multi_turn_conversation(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test multi-turn conversation through chat endpoint.

        Verifies:
        - Conversation ID is returned and can be reused
        - Agent maintains context across turns
        - History is persisted and loaded correctly
        """
        # Arrange - First turn
        payload1 = {
            "message": "Create a task to buy milk"
        }

        # Act - First turn
        response1 = await client.post(
            "/chat",
            json=payload1,
            headers=auth_headers
        )

        # Assert - First turn
        assert response1.status_code == 200
        data1 = response1.json()
        conversation_id = data1["conversation_id"]

        # Act - Second turn with conversation_id
        payload2 = {
            "message": "Show me my tasks",
            "conversation_id": conversation_id
        }
        response2 = await client.post(
            "/chat",
            json=payload2,
            headers=auth_headers
        )

        # Assert - Second turn
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["conversation_id"] == conversation_id
        assert len(data2["tool_calls"]) > 0

    @pytest.mark.asyncio
    async def test_chat_list_tasks(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test listing tasks through chat endpoint."""
        # Arrange
        payload = {
            "message": "Show me all my tasks"
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data["tool_calls"]) > 0
        tool_call = data["tool_calls"][0]
        assert tool_call["tool_name"] == "list_tasks"
        assert tool_call["execution_status"] == "success"

    @pytest.mark.asyncio
    async def test_chat_invalid_conversation_id(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test error handling for invalid conversation ID."""
        # Arrange
        payload = {
            "message": "Create a task",
            "conversation_id": 99999  # Non-existent conversation
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert - Should return error
        assert response.status_code in [403, 404, 500]

    @pytest.mark.asyncio
    async def test_chat_missing_message(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for missing message."""
        # Arrange
        payload = {}  # Missing message field

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_empty_message(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test validation error for empty message."""
        # Arrange
        payload = {
            "message": ""
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_chat_missing_auth_header(
        self,
        client: AsyncClient
    ):
        """Test authentication error for missing user ID."""
        # Arrange
        payload = {
            "message": "Create a task"
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload
            # No auth headers
        )

        # Assert
        assert response.status_code == 401  # Unauthorized

    @pytest.mark.asyncio
    async def test_chat_tool_call_transparency(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test tool call transparency in response.

        Verifies:
        - All tool calls include transparency fields
        - Tool call format matches specification
        - Timestamps are included
        """
        # Arrange
        payload = {
            "message": "Create a task to test transparency"
        }

        # Act
        response = await client.post(
            "/chat",
            json=payload,
            headers=auth_headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()

        # Verify tool call transparency
        assert len(data["tool_calls"]) > 0
        for tool_call in data["tool_calls"]:
            assert "tool_name" in tool_call
            assert "input_parameters" in tool_call
            assert "output_result" in tool_call
            assert "execution_status" in tool_call
            assert "timestamp" in tool_call
            assert tool_call["execution_status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_chat_deterministic_behavior(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """Test agent produces consistent responses.

        Verifies:
        - Same input produces similar tool calls
        - Agent behavior is deterministic (temperature 0.1)
        """
        # Arrange
        payload = {
            "message": "Create a task to buy groceries"
        }

        # Act - Send same message multiple times
        responses = []
        for _ in range(3):
            response = await client.post(
                "/chat",
                json=payload,
                headers=auth_headers
            )
            responses.append(response.json())

        # Assert - All should call add_task tool
        for data in responses:
            assert len(data["tool_calls"]) > 0
            tool_call = data["tool_calls"][0]
            assert tool_call["tool_name"] == "add_task"
            assert "groceries" in tool_call["input_parameters"]["title"].lower()
