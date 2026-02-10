"""Agent orchestration use case.

Coordinates between the AI agent, MCP tools, and conversation persistence
to provide a stateless conversational interface for task management.

Task IDs: T050-T056 - Updated to use OpenAI Agents SDK via RunnerFactory
"""

import logging
import time
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.agent.agent_factory import AgentFactory
from src.agent.guardrails import (
    get_confirmation_manager,
    is_explicit_confirmation,
    is_rejection,
)
from src.agent.history_manager import HistoryManager
from src.agent.instructions import get_system_instructions
from src.config import settings
from src.domain.models import Conversation, Message

logger = logging.getLogger(__name__)


class AgentOrchestration:
    """Orchestrates AI agent interactions with conversation persistence.
    
    This use case handles the complete flow:
    1. Create or resume conversation
    2. Fetch conversation history
    3. Call AI agent with context
    4. Execute tool calls through MCP adapter
    5. Persist messages to database
    6. Return response with tool call transparency
    """

    def __init__(self):
        """Initialize agent orchestration with RunnerFactory and HistoryManager."""
        self._agent_factory = AgentFactory()
        self._runner_factory = self._agent_factory.get_runner_factory()
        self._mcp_adapter = self._agent_factory.get_mcp_adapter()
        self._history_manager = HistoryManager(max_messages=settings.agent_max_history_messages)
        self._confirmation_manager = get_confirmation_manager()

    async def process_message(
        self,
        session: AsyncSession,
        user_id: UUID,
        message: str,
        conversation_id: int | None = None
    ) -> dict[str, Any]:
        """Process a user message and return agent response.

        Args:
            session: Database session
            user_id: User ID
            message: User's message text
            conversation_id: Optional conversation ID to resume

        Returns:
            Dictionary with conversation_id, response, and tool_calls

        Raises:
            PermissionError: If conversation doesn't belong to user
        """
        # Step 1: Create or resume conversation
        if conversation_id is None:
            conversation_id = await self._create_conversation(session, user_id)
        else:
            await self._validate_conversation_ownership(session, conversation_id, user_id)

        # Step 2: Fetch conversation history
        history = await self._fetch_conversation_history(session, conversation_id)

        # Step 3: Call AI agent (with confirmation flow handling)
        agent_response = await self._call_agent(message, history, conversation_id)

        # Step 4: Execute tool calls
        tool_calls = []
        if agent_response.get('tool_calls'):
            for tool_call in agent_response['tool_calls']:
                result = await self._execute_tool_call(
                    session=session,
                    tool_name=tool_call['name'],
                    user_id=user_id,
                    parameters=tool_call.get('arguments', {})
                )
                tool_calls.append(result)

        # Step 5: Persist messages
        await self._persist_messages(
            session=session,
            conversation_id=conversation_id,
            user_message=message,
            assistant_message=agent_response['content'],
            tool_calls=tool_calls
        )

        # Step 6: Return response
        return {
            'conversation_id': conversation_id,
            'response': agent_response['content'],
            'tool_calls': tool_calls
        }

    async def _create_conversation(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> int:
        """Create a new conversation.
        
        Args:
            session: Database session
            user_id: User ID
            
        Returns:
            Conversation ID
        """
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)

        logger.info(f"Created conversation {conversation.id} for user {user_id}")
        return conversation.id

    async def _validate_conversation_ownership(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_id: UUID
    ) -> None:
        """Validate that conversation belongs to user.
        
        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID
            
        Raises:
            PermissionError: If conversation doesn't belong to user
        """
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise PermissionError(f"Conversation {conversation_id} not found")

        if conversation.user_id != user_id:
            raise PermissionError(f"Conversation {conversation_id} does not belong to user")

    async def _fetch_conversation_history(
        self,
        session: AsyncSession,
        conversation_id: int
    ) -> list[dict[str, str]]:
        """Fetch conversation history with tool call results.

        Args:
            session: Database session
            conversation_id: Conversation ID

        Returns:
            List of messages with role, content, and tool results
        """
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(settings.agent_max_history_messages)
        )
        messages = result.scalars().all()

        history = []
        for msg in messages:
            # Add the main message
            history.append({'role': msg.role, 'content': msg.content})

            # If this is an assistant message with tool calls, add tool results
            if msg.role == 'assistant' and msg.tool_calls:
                import json
                tool_calls = json.loads(msg.tool_calls) if isinstance(msg.tool_calls, str) else msg.tool_calls

                # Format tool results as a summary for the agent
                if tool_calls:
                    tool_results_text = "Tool execution results:\n"
                    for tool_call in tool_calls:
                        tool_name = tool_call.get('tool_name', 'unknown')
                        output = tool_call.get('output_result', {})
                        tool_results_text += f"- {tool_name}: {json.dumps(output)}\n"

                    # Add tool results as a system message for context
                    history.append({'role': 'system', 'content': tool_results_text})

        return history

    async def _call_agent(
        self,
        message: str,
        history: list[dict[str, str]],
        conversation_id: int
    ) -> dict[str, Any]:
        """Call AI agent with message and history using OpenAI Agents SDK.

        Task IDs: T050-T056
        Replaces mock intent detection with real OpenAI Agents SDK execution.

        Args:
            message: User's message
            history: Conversation history
            conversation_id: Conversation ID for confirmation tracking

        Returns:
            Agent response with content and tool_calls
        """
        start_time = time.time()

        # Check for pending confirmation first (guardrails)
        if self._confirmation_manager.has_pending_confirmation(conversation_id):
            pending = self._confirmation_manager.get_pending_confirmation(conversation_id)

            # Check if user confirmed
            if is_explicit_confirmation(message):
                # Execute the pending action
                self._confirmation_manager.clear_pending_confirmation(conversation_id)
                return {
                    'content': f"Confirmed. I'll {pending['action'].replace('_', ' ')} now.",
                    'tool_calls': [
                        {
                            'name': pending['action'],
                            'arguments': pending['parameters']
                        }
                    ]
                }

            # Check if user rejected
            if is_rejection(message):
                # Cancel the action
                self._confirmation_manager.clear_pending_confirmation(conversation_id)
                return {
                    'content': "Okay, I've cancelled that action.",
                    'tool_calls': []
                }

        # T051: Truncate history using HistoryManager
        system_instructions = get_system_instructions()
        formatted_history = self._history_manager.format_for_agent(history, system_instructions)

        # T052: Create OpenAI client using RunnerFactory
        client, config = self._runner_factory.create_client(use_fallback=False)

        # T053: Call runner_factory.run_with_retry()
        try:
            agent_response = await self._runner_factory.run_with_retry(
                client=client,
                config=config,
                message=message,
                history=formatted_history,
                max_attempts=3
            )
        except Exception as e:
            logger.error(
                "Agent execution failed",
                extra={
                    "event": "agent_execution_failed",
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "conversation_id": conversation_id
                }
            )
            # Return error response
            return {
                'content': "I'm sorry, I encountered an error processing your request. Please try again.",
                'tool_calls': []
            }

        # T054: Extract tool calls from agent response (already done by RunnerFactory)
        # T055: Return response with tool_calls array
        response = {
            'content': agent_response.get('content', ''),
            'tool_calls': agent_response.get('tool_calls', [])
        }

        # T056: Add structured logging for agent invocations
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(
            "Agent orchestration completed",
            extra={
                "event": "agent_orchestration",
                "conversation_id": conversation_id,
                "provider": config.get("provider", "unknown"),
                "model": config.get("model", "unknown"),
                "tool_calls_count": len(response['tool_calls']),
                "latency_ms": latency_ms,
                "status": "success"
            }
        )

        return response


    async def _execute_tool_call(
        self,
        session: AsyncSession,
        tool_name: str,
        user_id: UUID,
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a tool call through MCP adapter.

        Args:
            session: Database session
            tool_name: Name of the tool
            user_id: User ID for context
            parameters: Tool parameters

        Returns:
            Tool call result with transparency fields
        """
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Log tool call initiation
        logger.info(
            f"Executing tool call: {tool_name}",
            extra={
                "tool_name": tool_name,
                "user_id": str(user_id),
                "parameters": parameters,
                "timestamp": timestamp
            }
        )

        try:
            start_time = datetime.utcnow()

            result = await self._mcp_adapter.execute_tool(
                session=session,
                tool_name=tool_name,
                user_id=str(user_id),
                parameters=parameters
            )

            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Log successful tool execution
            logger.info(
                f"Tool call succeeded: {tool_name}",
                extra={
                    "tool_name": tool_name,
                    "user_id": str(user_id),
                    "execution_time_ms": execution_time_ms,
                    "result_keys": list(result.keys()) if isinstance(result, dict) else None,
                    "timestamp": timestamp
                }
            )

            return {
                'tool_name': tool_name,
                'input_parameters': parameters,
                'output_result': result,
                'execution_status': 'success',
                'error_message': None,
                'timestamp': timestamp
            }
        except Exception as e:
            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Log tool execution failure with full context
            logger.error(
                f"Tool call failed: {tool_name} - {str(e)}",
                extra={
                    "tool_name": tool_name,
                    "user_id": str(user_id),
                    "parameters": parameters,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "execution_time_ms": execution_time_ms,
                    "timestamp": timestamp
                },
                exc_info=True
            )

            return {
                'tool_name': tool_name,
                'input_parameters': parameters,
                'output_result': {},
                'execution_status': 'error',
                'error_message': str(e),
                'timestamp': timestamp
            }

    async def _persist_messages(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_message: str,
        assistant_message: str,
        tool_calls: list[dict[str, Any]]
    ) -> None:
        """Persist user and assistant messages to database.
        
        Args:
            session: Database session
            conversation_id: Conversation ID
            user_message: User's message text
            assistant_message: Assistant's response text
            tool_calls: List of tool calls for transparency
        """
        # Persist user message
        user_msg = Message(
            conversation_id=conversation_id,
            role='user',
            content=user_message,
            tool_calls=None
        )
        session.add(user_msg)

        # Persist assistant message with tool calls
        import json
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None

        assistant_msg = Message(
            conversation_id=conversation_id,
            role='assistant',
            content=assistant_message,
            tool_calls=tool_calls_json
        )
        session.add(assistant_msg)

        # Update conversation updated_at
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one()
        conversation.updated_at = datetime.utcnow()

        await session.commit()

        logger.info(f"Persisted messages for conversation {conversation_id}")

    async def stream_message(
        self,
        session: AsyncSession,
        user_id: UUID,
        message: str,
        conversation_id: int | None = None
    ):
        """Stream a user message with token-by-token response.

        Yields streaming chunks in the format:
        - {"type": "token", "content": "word"}
        - {"type": "tool_call", "data": {...}}
        - {"type": "done", "conversation_id": 1, "message_id": 123}

        Args:
            session: Database session
            user_id: User ID
            message: User's message text
            conversation_id: Optional conversation ID to resume

        Yields:
            Dictionary chunks for streaming response
        """
        # Step 1: Create or resume conversation
        if conversation_id is None:
            conversation_id = await self._create_conversation(session, user_id)
        else:
            await self._validate_conversation_ownership(session, conversation_id, user_id)

        # Step 2: Fetch conversation history
        history = await self._fetch_conversation_history(session, conversation_id)

        # Step 3: Call agent and stream response
        full_response = ""
        tool_calls_list = []

        try:
            # Get agent response (non-streaming for now, will be enhanced later)
            agent_response = await self._call_agent(message, history, conversation_id)

            # Stream the response content token-by-token
            # Split response into words for streaming simulation
            response_text = agent_response.get('content', '')
            words = response_text.split()

            for word in words:
                # Yield token chunk
                yield {
                    "type": "token",
                    "content": word + " "
                }
                full_response += word + " "

            full_response = full_response.strip()

            # Step 4: Execute and stream tool calls
            if agent_response.get('tool_calls'):
                for tool_call in agent_response['tool_calls']:
                    # Yield pending tool call
                    yield {
                        "type": "tool_call",
                        "data": {
                            "tool_name": tool_call['name'],
                            "input_parameters": tool_call.get('arguments', {}),
                            "output_result": None,
                            "execution_status": "pending",
                            "error_message": None,
                            "timestamp": datetime.utcnow().isoformat() + 'Z'
                        }
                    }

                    # Execute tool call
                    result = await self._execute_tool_call(
                        session=session,
                        tool_name=tool_call['name'],
                        user_id=user_id,
                        parameters=tool_call.get('arguments', {})
                    )
                    tool_calls_list.append(result)

                    # Yield completed tool call
                    yield {
                        "type": "tool_call",
                        "data": result
                    }

            # Step 5: Persist messages
            await self._persist_messages(
                session=session,
                conversation_id=conversation_id,
                user_message=message,
                assistant_message=full_response,
                tool_calls=tool_calls_list
            )

            # Step 6: Yield done chunk
            yield {
                "type": "done",
                "conversation_id": conversation_id
            }

            logger.info(
                f"Streaming completed for user {user_id}, "
                f"conversation {conversation_id}, "
                f"tool_calls: {len(tool_calls_list)}"
            )

        except PermissionError as e:
            logger.warning(f"Permission denied for user {user_id}: {str(e)}")
            yield {
                "type": "error",
                "message": str(e),
                "code": "PERMISSION_DENIED"
            }

        except Exception as e:
            logger.error(
                f"Streaming error for user {user_id}: {str(e)}",
                exc_info=True
            )
            yield {
                "type": "error",
                "message": "Failed to process message",
                "code": "INTERNAL_ERROR"
            }

