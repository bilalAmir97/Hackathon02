"""RunnerFactory for OpenAI ChatCompletions with tool calling.

Task IDs: T039-T048
Creates and configures OpenAI ChatCompletions client with Groq/OpenAI providers.
Handles tool calling directly through OpenAI API instead of Agents SDK.
"""

import json
import logging
import time
import traceback
from typing import Any

from openai import AsyncOpenAI

from src.agent.instructions import get_system_instructions
from src.agent.mcp_adapter import MCPAdapter
from src.agent.retry_policy import RetryPolicy
from src.config import settings

logger = logging.getLogger(__name__)


class RunnerFactory:
    """Factory for creating and managing OpenAI ChatCompletions with tool calling.

    Handles client creation with Groq (primary) or OpenAI (fallback),
    tool registration, retry logic, and response parsing.
    Uses raw OpenAI ChatCompletions API instead of Agents SDK.
    """

    def __init__(self):
        """Initialize RunnerFactory with MCP adapter and retry policy."""
        self.mcp_adapter = MCPAdapter()
        self.retry_policy = RetryPolicy(
            max_attempts=3,  # LLM failures get 3 attempts
            initial_delay_ms=100,
            max_delay_ms=5000,
            backoff_multiplier=2.0
        )

    def create_client(self, use_fallback: bool = False) -> tuple[AsyncOpenAI, dict[str, Any]]:
        """Create OpenAI client with Groq or OpenAI provider.

        Args:
            use_fallback: If True, use OpenAI client; if False, use Groq client

        Returns:
            Tuple of (AsyncOpenAI client, config dict with provider/model info)
        """
        # Get MCP tools in OpenAI function calling format
        tools = self.mcp_adapter.get_tools()

        # Create appropriate client
        if use_fallback:
            # OpenAI fallback (only if API key is available)
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured, cannot use fallback")
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            model_name = settings.openai_fallback_model
            provider = "openai"
        else:
            # Groq primary
            client = AsyncOpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            model_name = settings.groq_model
            provider = "groq"

        # Return client and config info
        config = {
            "provider": provider,
            "model": model_name,
            "temperature": settings.agent_temperature,
            "max_tokens": settings.agent_max_tokens,
            "tools": tools
        }

        return client, config

    async def run_with_retry(
        self,
        client: AsyncOpenAI,
        config: dict[str, Any],
        message: str,
        history: list[dict[str, str]],
        max_attempts: int = 3
    ) -> dict[str, Any]:
        """Execute ChatCompletions with retry logic and fallback support.

        Args:
            client: AsyncOpenAI client instance
            config: Configuration dict with model, tools, etc.
            message: User message to process
            history: Conversation history (already formatted)
            max_attempts: Maximum retry attempts

        Returns:
            Dict with 'content' (agent response) and 'tool_calls' (list of tool calls)
        """
        start_time = time.time()
        attempt = 0
        last_exception = None
        used_fallback = False

        # Get system instructions
        system_instructions = get_system_instructions()

        while attempt < max_attempts:
            attempt += 1

            try:
                # Build messages array (system + history + new message)
                messages = [{"role": "system", "content": system_instructions}]
                messages.extend(history)
                messages.append({"role": "user", "content": message})

                # Convert MCP tools to OpenAI function calling format
                tools_formatted = []
                for tool in config["tools"]:
                    tools_formatted.append({
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "description": tool["description"],
                            "parameters": tool["parameters"]
                        }
                    })

                # Call OpenAI ChatCompletions API with tools
                response = await client.chat.completions.create(
                    model=config["model"],
                    messages=messages,
                    tools=tools_formatted if tools_formatted else None,
                    tool_choice="auto" if tools_formatted else None,
                    temperature=config["temperature"],
                    max_tokens=config["max_tokens"]
                )

                # Extract response content and tool calls
                parsed_response = self._parse_completion_response(response)

                # Log successful execution
                latency_ms = int((time.time() - start_time) * 1000)
                logger.info(
                    "Agent invocation successful",
                    extra={
                        "event": "agent_invocation",
                        "provider": config["provider"],
                        "attempt": attempt,
                        "latency_ms": latency_ms,
                        "tool_calls_count": len(parsed_response.get("tool_calls", [])),
                        "status": "success"
                    }
                )

                return parsed_response

            except Exception as e:
                last_exception = e
                error_str = str(e).lower()

                # Log full traceback immediately for debugging
                logger.error(
                    f"Agent execution exception caught: {type(e).__name__}: {str(e)}",
                    extra={
                        "event": "agent_exception",
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc(),
                        "attempt": attempt
                    }
                )

                # Check if this is a rate limit error requiring fallback
                if "429" in error_str or "rate limit" in error_str:
                    if not used_fallback and settings.openai_fallback_enabled:
                        logger.warning(
                            "Groq rate limit hit, falling back to OpenAI",
                            extra={
                                "event": "fallback_triggered",
                                "reason": "rate_limit",
                                "attempt": attempt
                            }
                        )
                        # Create new client with OpenAI fallback
                        client, config = self.create_client(use_fallback=True)
                        used_fallback = True
                        continue

                # Check if error is retryable
                if not self.retry_policy.is_retryable_error(e):
                    logger.error(
                        "Non-retryable error in agent execution",
                        extra={
                            "event": "agent_error",
                            "error_type": type(e).__name__,
                            "error_message": str(e),
                            "attempt": attempt
                        }
                    )
                    raise

                # If this was the last attempt, raise
                if attempt >= max_attempts:
                    logger.error(
                        "Max retry attempts exceeded for agent execution",
                        extra={
                            "event": "max_attempts_exceeded",
                            "max_attempts": max_attempts,
                            "error_type": type(e).__name__,
                            "error_message": str(e)
                        }
                    )
                    raise

                # Log retry attempt
                delay_ms = min(
                    int(self.retry_policy.initial_delay_ms * (self.retry_policy.backoff_multiplier ** (attempt - 1))),
                    self.retry_policy.max_delay_ms
                )
                logger.warning(
                    "Retrying agent execution after transient error",
                    extra={
                        "event": "agent_retry",
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "error_type": type(e).__name__,
                        "delay_ms": delay_ms
                    }
                )

                # Wait before retrying
                import asyncio
                await asyncio.sleep(delay_ms / 1000.0)

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception

    def _parse_completion_response(self, response: Any) -> dict[str, Any]:
        """Parse OpenAI ChatCompletion response and extract tool calls.

        Args:
            response: ChatCompletion response from OpenAI API

        Returns:
            Dict with 'content' and 'tool_calls' keys
        """
        # Extract message from response
        message = response.choices[0].message

        # Extract content
        content = message.content if message.content else ""

        # Extract tool calls
        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                # Parse arguments JSON string
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}

                tool_calls.append({
                    "name": tool_call.function.name,
                    "arguments": arguments
                })

        return {
            "content": content,
            "tool_calls": tool_calls
        }
