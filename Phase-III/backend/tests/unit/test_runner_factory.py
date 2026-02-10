"""Unit tests for RunnerFactory.

Task IDs: T025-T030
Tests OpenAI ChatCompletions API integration with tool calling.
"""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agent.runner_factory import RunnerFactory


class TestRunnerFactoryCreation:
    """Test RunnerFactory.create_client() with Groq client (T025)."""

    def test_create_client_with_groq(self):
        """Given RunnerFactory with Groq configuration,
        when create_client is called with use_fallback=False,
        then it should create AsyncOpenAI client with Groq configuration."""
        factory = RunnerFactory()

        client, config = factory.create_client(use_fallback=False)

        assert client is not None
        assert config is not None
        assert config["provider"] == "groq"
        assert config["model"] == "openai/gpt-oss-20b"


class TestRunnerFactoryFallback:
    """Test RunnerFactory.create_client() with OpenAI fallback (T026)."""

    def test_create_client_with_openai_fallback(self):
        """Given RunnerFactory with OpenAI configuration,
        when create_client is called with use_fallback=True,
        then it should create AsyncOpenAI client with OpenAI configuration."""
        factory = RunnerFactory()

        client, config = factory.create_client(use_fallback=True)

        assert client is not None
        assert config is not None
        assert config["provider"] == "openai"
        assert config["model"] == "gpt-4o-mini"


class TestRunnerFactoryToolRegistration:
    """Test RunnerFactory tool registration (T027)."""

    def test_tools_registered_in_config(self):
        """Given RunnerFactory,
        when create_client is called,
        then all 5 MCP tools should be registered in config."""
        factory = RunnerFactory()

        client, config = factory.create_client()

        # Verify tools are registered in config
        assert "tools" in config
        assert len(config["tools"]) == 5
        tool_names = [tool["name"] for tool in config["tools"]]
        assert "add_task" in tool_names
        assert "list_tasks" in tool_names
        assert "update_task" in tool_names
        assert "complete_task" in tool_names
        assert "delete_task" in tool_names


class TestRunnerFactoryRetryIntegration:
    """Test RunnerFactory retry logic integration (T028)."""

    @pytest.mark.asyncio
    async def test_run_with_retry_on_transient_error(self):
        """Given a client that fails with rate limit then succeeds,
        when run_with_retry is called,
        then it should retry and return success."""
        factory = RunnerFactory()
        mock_client = MagicMock()
        config = {
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
            "temperature": 0.1,
            "max_tokens": 500,
            "tools": []
        }

        # Mock chat.completions.create() to fail once then succeed
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "Success"
        mock_completion.choices[0].message.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(
            side_effect=[Exception("Connection error"), mock_completion]
        )

        result = await factory.run_with_retry(
            client=mock_client,
            config=config,
            message="Test message",
            history=[]
        )

        assert result is not None
        assert result["content"] == "Success"
        assert mock_client.chat.completions.create.call_count == 2


class TestRunnerFactoryRateLimitFallback:
    """Test RunnerFactory fallback on rate limit (T029)."""

    @pytest.mark.asyncio
    async def test_fallback_to_openai_on_groq_rate_limit(self):
        """Given Groq client that hits rate limit,
        when run_with_retry detects rate limit,
        then it should fallback to OpenAI."""
        factory = RunnerFactory()

        # Mock create_client to return different clients
        with patch.object(factory, 'create_client') as mock_create:
            groq_client = MagicMock()
            openai_client = MagicMock()

            # First call returns Groq, second returns OpenAI
            mock_create.side_effect = [
                (groq_client, {"provider": "groq", "model": "openai/gpt-oss-20b", "temperature": 0.1, "max_tokens": 500, "tools": []}),
                (openai_client, {"provider": "openai", "model": "gpt-4o-mini", "temperature": 0.1, "max_tokens": 500, "tools": []})
            ]

            # Mock Groq to fail with rate limit
            groq_client.chat.completions.create = AsyncMock(
                side_effect=Exception("429 Rate Limit")
            )

            # Mock OpenAI to succeed
            mock_completion = MagicMock()
            mock_completion.choices = [MagicMock()]
            mock_completion.choices[0].message = MagicMock()
            mock_completion.choices[0].message.content = "Success"
            mock_completion.choices[0].message.tool_calls = None

            openai_client.chat.completions.create = AsyncMock(return_value=mock_completion)

            # Get initial client
            client, config = factory.create_client(use_fallback=False)

            result = await factory.run_with_retry(
                client=client,
                config=config,
                message="Test message",
                history=[],
                max_attempts=3
            )

            # Should have fallen back to OpenAI
            assert result["content"] == "Success"
            assert mock_create.call_count == 2  # Initial + fallback


class TestRunnerFactoryResponseParsing:
    """Test RunnerFactory response parsing (T030)."""

    @pytest.mark.asyncio
    async def test_parse_completion_response_with_tool_calls(self):
        """Given ChatCompletion response with tool calls,
        when run_with_retry completes,
        then it should extract and format tool calls."""
        factory = RunnerFactory()
        mock_client = MagicMock()
        config = {
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
            "temperature": 0.1,
            "max_tokens": 500,
            "tools": [
                {
                    "name": "add_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"}
                        },
                        "required": ["title"]
                    }
                }
            ]
        }

        # Mock ChatCompletion response with tool calls
        mock_tool_call = MagicMock()
        mock_tool_call.function.name = "add_task"
        mock_tool_call.function.arguments = json.dumps({"title": "Buy milk"})

        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = ""
        mock_completion.choices[0].message.tool_calls = [mock_tool_call]

        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        result = await factory.run_with_retry(
            client=mock_client,
            config=config,
            message="Add a task to buy milk",
            history=[]
        )

        assert "content" in result
        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["name"] == "add_task"
        assert result["tool_calls"][0]["arguments"]["title"] == "Buy milk"

    @pytest.mark.asyncio
    async def test_parse_completion_response_without_tool_calls(self):
        """Given ChatCompletion response without tool calls,
        when run_with_retry completes,
        then it should return response with empty tool_calls array."""
        factory = RunnerFactory()
        mock_client = MagicMock()
        config = {
            "provider": "groq",
            "model": "openai/gpt-oss-20b",
            "temperature": 0.1,
            "max_tokens": 500,
            "tools": []
        }

        # Mock ChatCompletion response without tool calls
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message = MagicMock()
        mock_completion.choices[0].message.content = "I can help you with that. What would you like to do?"
        mock_completion.choices[0].message.tool_calls = None

        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)

        result = await factory.run_with_retry(
            client=mock_client,
            config=config,
            message="Hello",
            history=[]
        )

        assert "content" in result
        assert result["content"] == "I can help you with that. What would you like to do?"
        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 0
