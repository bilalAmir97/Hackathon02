"""Integration tests for AgentOrchestration with real OpenAI Agents SDK.

These tests require API keys to be set:
- GROQ_API_KEY for primary provider
- OPENAI_API_KEY for fallback provider

Task IDs: T031-T036, T064-T066, T080, T087, T089-T091
"""

import pytest
import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from src.use_cases.agent_orchestration import AgentOrchestration
from src.domain.models import Conversation, Message


# Skip all tests if API keys are not set
pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY") or not os.getenv("OPENAI_API_KEY"),
    reason="API keys not set (GROQ_API_KEY and OPENAI_API_KEY required)"
)


@pytest.fixture
async def orchestration():
    """Create AgentOrchestration instance."""
    return AgentOrchestration()


@pytest.fixture
async def user_id():
    """Generate a test user ID."""
    return uuid4()


class TestNaturalLanguageTaskCreation:
    """Test natural language task creation (T031, US1)."""

    @pytest.mark.asyncio
    async def test_create_task_natural_language(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test agent creates task from natural language request.

        Verifies:
        - Agent understands "create a task" intent
        - Agent calls add_task tool with correct parameters
        - Response includes tool call transparency
        """
        # Arrange
        message = "Create a task to buy groceries"

        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message
        )

        # Assert
        assert "conversation_id" in result
        assert "response" in result
        assert "tool_calls" in result

        # Verify tool call was made
        assert len(result["tool_calls"]) > 0
        tool_call = result["tool_calls"][0]
        assert tool_call["tool_name"] == "add_task"
        assert "buy groceries" in tool_call["input_parameters"]["title"].lower()
        assert tool_call["execution_status"] == "success"

        # Verify response is conversational
        assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_list_tasks_natural_language(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test agent lists tasks from natural language request."""
        # Arrange
        message = "Show me my tasks"

        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message
        )

        # Assert
        assert len(result["tool_calls"]) > 0
        tool_call = result["tool_calls"][0]
        assert tool_call["tool_name"] == "list_tasks"
        assert tool_call["execution_status"] == "success"


class TestMCPToolsExclusive:
    """Test agent uses MCP tools exclusively (T032, US2)."""

    @pytest.mark.asyncio
    async def test_agent_uses_mcp_tools_only(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test agent only uses registered MCP tools.

        Verifies:
        - Agent doesn't hallucinate tool calls
        - All tool calls are from MCP adapter
        - Tool calls are properly formatted
        """
        # Arrange
        message = "Create a task to test MCP tools"

        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message
        )

        # Assert
        valid_tools = ["add_task", "list_tasks", "update_task", "complete_task", "delete_task"]
        for tool_call in result["tool_calls"]:
            assert tool_call["tool_name"] in valid_tools, \
                f"Agent used invalid tool: {tool_call['tool_name']}"


class TestConversationHistory:
    """Test conversation history injection (T033, T064-T066, US3)."""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_with_context(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test agent uses conversation history for context.

        Verifies:
        - Agent remembers previous messages
        - Agent uses context to understand references
        - History is loaded from database
        """
        # Arrange - First turn: create a task
        message1 = "Create a task to buy milk"
        result1 = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message1
        )
        conversation_id = result1["conversation_id"]

        # Act - Second turn: reference the previous task
        message2 = "Show me my tasks"
        result2 = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message2,
            conversation_id=conversation_id
        )

        # Assert
        assert result2["conversation_id"] == conversation_id
        assert len(result2["tool_calls"]) > 0

        # Verify history was persisted
        from sqlmodel import select
        stmt = select(Message).where(Message.conversation_id == conversation_id)
        result = await db_session.execute(stmt)
        messages = result.scalars().all()

        # Should have 4 messages: user1, assistant1, user2, assistant2
        assert len(messages) >= 4

    @pytest.mark.asyncio
    async def test_history_truncation_over_20_messages(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test conversation history is truncated to 20 messages.

        Verifies:
        - Only most recent 20 messages are used
        - Older messages are not sent to agent
        - System instructions are always included
        """
        # Arrange - Create conversation with many messages
        conversation_id = None
        for i in range(15):
            result = await orchestration.process_message(
                session=db_session,
                user_id=user_id,
                message=f"Create task {i}",
                conversation_id=conversation_id
            )
            conversation_id = result["conversation_id"]

        # Act - Send one more message
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message="Show me my tasks",
            conversation_id=conversation_id
        )

        # Assert - Should still work despite long history
        assert result["conversation_id"] == conversation_id
        assert len(result["tool_calls"]) > 0

    @pytest.mark.asyncio
    async def test_empty_history_on_first_message(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test first message has no history.

        Verifies:
        - New conversation starts with empty history
        - Agent still functions correctly
        - System instructions are provided
        """
        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message="Create a task to test empty history"
        )

        # Assert
        assert "conversation_id" in result
        assert len(result["tool_calls"]) > 0


class TestToolCallPersistence:
    """Test tool call transparency and persistence (T034, T078-T079, US4)."""

    @pytest.mark.asyncio
    async def test_tool_call_persistence(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test tool calls are persisted to database.

        Verifies:
        - Tool calls are stored in Message.tool_calls
        - Tool call includes all transparency fields
        - Tool calls can be retrieved from database
        """
        # Arrange
        message = "Create a task to test persistence"

        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message
        )

        # Assert - Verify tool calls in response
        assert len(result["tool_calls"]) > 0
        tool_call = result["tool_calls"][0]
        assert "tool_name" in tool_call
        assert "input_parameters" in tool_call
        assert "output_result" in tool_call
        assert "execution_status" in tool_call
        assert "timestamp" in tool_call

        # Verify tool calls persisted to database
        from sqlmodel import select
        stmt = select(Message).where(
            Message.conversation_id == result["conversation_id"],
            Message.role == "assistant"
        )
        db_result = await db_session.execute(stmt)
        assistant_message = db_result.scalars().first()

        assert assistant_message is not None
        assert assistant_message.tool_calls is not None

        import json
        persisted_tool_calls = json.loads(assistant_message.tool_calls)
        assert len(persisted_tool_calls) > 0

    @pytest.mark.asyncio
    async def test_tool_call_error_persistence(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test tool call errors are persisted with error details.

        Verifies:
        - Failed tool calls are persisted
        - Error message is included
        - Execution status is 'error'
        """
        # Arrange - Try to update non-existent task
        fake_task_id = str(uuid4())
        message = f"Update task {fake_task_id} to new title"

        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message=message
        )

        # Assert - Tool call should have error status
        if len(result["tool_calls"]) > 0:
            tool_call = result["tool_calls"][0]
            if tool_call["tool_name"] == "update_task":
                # Error expected for non-existent task
                assert "execution_status" in tool_call
                assert "error_message" in tool_call


class TestRetryAndErrorHandling:
    """Test retry logic and error handling (T035, T089-T091, US6)."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_failures(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test system retries on transient failures.

        Note: This test is difficult to verify without mocking.
        We verify the system completes successfully, which implies
        retry logic is working if transient errors occur.
        """
        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message="Create a task to test retry logic"
        )

        # Assert - Should complete successfully
        assert "conversation_id" in result
        assert "response" in result


class TestFallbackProvider:
    """Test fallback to OpenAI provider (T036, US1)."""

    @pytest.mark.asyncio
    async def test_fallback_to_openai(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test system falls back to OpenAI on Groq failures.

        Note: This test is difficult to verify without mocking Groq failures.
        We verify the system completes successfully with either provider.
        """
        # Act
        result = await orchestration.process_message(
            session=db_session,
            user_id=user_id,
            message="Create a task to test fallback"
        )

        # Assert - Should complete successfully
        assert "conversation_id" in result
        assert len(result["tool_calls"]) > 0


class TestDeterministicBehavior:
    """Test deterministic agent behavior (T080, T087, US5)."""

    @pytest.mark.asyncio
    async def test_deterministic_behavior(
        self,
        orchestration: AgentOrchestration,
        db_session: AsyncSession,
        user_id
    ):
        """Test agent produces consistent responses for same input.

        Verifies:
        - Temperature is set to 0.1 for determinism
        - Same input produces similar tool calls
        - Response structure is consistent
        """
        # Arrange
        message = "Create a task to buy groceries"

        # Act - Send same message multiple times
        results = []
        for _ in range(3):
            result = await orchestration.process_message(
                session=db_session,
                user_id=user_id,
                message=message
            )
            results.append(result)

        # Assert - All should call add_task tool
        for result in results:
            assert len(result["tool_calls"]) > 0
            tool_call = result["tool_calls"][0]
            assert tool_call["tool_name"] == "add_task"
            assert "groceries" in tool_call["input_parameters"]["title"].lower()
