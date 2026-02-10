"""Agent Factory for OpenAI Agents SDK.

This module provides a factory for creating AI agent instances with
Groq as the primary provider and OpenAI as fallback. It configures
agents with MCP tools and system instructions.

Task ID: T049 - Updated to use RunnerFactory
"""

import logging
from typing import Any

from src.agent.mcp_adapter import MCPAdapter
from src.agent.runner_factory import RunnerFactory
from src.config import settings

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory for creating AI agent instances using OpenAI Agents SDK.

    This factory creates agents configured with:
    - OpenAI Agents SDK Runner
    - Groq as primary LLM provider (openai/gpt-oss-20b)
    - OpenAI as fallback provider (gpt-4o-mini)
    - MCP tools for task management
    - System instructions for deterministic behavior
    - Configuration from settings (temperature, max_tokens, etc.)
    """

    def __init__(self):
        """Initialize the agent factory with RunnerFactory."""
        self._runner_factory = RunnerFactory()
        self._mcp_adapter = self._runner_factory.mcp_adapter
        self._fallback_enabled = settings.openai_fallback_enabled

    def create_agent(self, use_fallback: bool = False) -> tuple[Any, dict[str, Any]]:
        """Create an AI agent instance using OpenAI Agents SDK.

        Args:
            use_fallback: If True, use OpenAI instead of Groq

        Returns:
            Tuple of (Runner instance, config dict)
        """
        if use_fallback and self._fallback_enabled:
            logger.info("Creating agent with OpenAI fallback")
            return self._runner_factory.create_runner(use_fallback=True)
        else:
            logger.info("Creating agent with Groq primary provider")
            return self._runner_factory.create_runner(use_fallback=False)

    def get_runner_factory(self) -> RunnerFactory:
        """Get the RunnerFactory instance.

        Returns:
            RunnerFactory instance
        """
        return self._runner_factory

    def get_mcp_adapter(self) -> MCPAdapter:
        """Get the MCP adapter instance.

        Returns:
            MCPAdapter instance
        """
        return self._mcp_adapter
