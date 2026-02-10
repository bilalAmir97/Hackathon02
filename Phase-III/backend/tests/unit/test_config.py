"""Unit tests for configuration settings.

Task IDs: T081-T082
"""

import pytest
from src.config import settings


class TestAgentConfiguration:
    """Test agent configuration settings."""

    def test_agent_temperature_is_0_1(self):
        """Test agent temperature is set to 0.1 for deterministic behavior.

        Task ID: T081
        User Story: US5 - Deterministic Agent Behavior

        Verifies:
        - Temperature is exactly 0.1
        - Low temperature ensures consistent responses
        """
        assert settings.agent_temperature == 0.1, \
            f"Expected agent_temperature to be 0.1, got {settings.agent_temperature}"

    def test_agent_max_tokens_is_500(self):
        """Test agent max_tokens is set to 500 for concise responses.

        Task ID: T082
        User Story: US5 - Deterministic Agent Behavior

        Verifies:
        - Max tokens is exactly 500
        - Ensures concise, focused responses
        """
        assert settings.agent_max_tokens == 500, \
            f"Expected agent_max_tokens to be 500, got {settings.agent_max_tokens}"

    def test_agent_max_history_messages_is_20(self):
        """Test conversation history is limited to 20 messages.

        User Story: US3 - Conversation History Injection

        Verifies:
        - History limit is 20 messages
        - Prevents context window overflow
        """
        assert settings.agent_max_history_messages == 20, \
            f"Expected agent_max_history_messages to be 20, got {settings.agent_max_history_messages}"

    def test_retry_configuration(self):
        """Test retry policy configuration.

        User Story: US6 - Retry and Error Handling

        Verifies:
        - Retry attempts are configured
        - Backoff parameters are set
        """
        # LLM retry attempts
        assert settings.retry_max_attempts_llm >= 3, \
            "LLM retry attempts should be at least 3"

        # Tool retry attempts
        assert settings.retry_max_attempts_tool >= 2, \
            "Tool retry attempts should be at least 2"

        # Backoff configuration
        assert settings.retry_initial_delay_ms > 0, \
            "Initial delay must be positive"
        assert settings.retry_max_delay_ms > settings.retry_initial_delay_ms, \
            "Max delay must be greater than initial delay"
        assert settings.retry_backoff_multiplier >= 1.0, \
            "Backoff multiplier must be at least 1.0"

    def test_openai_fallback_enabled(self):
        """Test OpenAI fallback is enabled.

        User Story: US1 - Real AI Agent with Natural Language Understanding

        Verifies:
        - Fallback to OpenAI is enabled
        - System can handle Groq failures
        """
        assert settings.openai_fallback_enabled is True, \
            "OpenAI fallback should be enabled"

    def test_api_keys_configured(self):
        """Test API keys are configured (or can be configured).

        Note: This test checks that the settings have the fields,
        not that they are actually set (which depends on environment).
        """
        # Check that settings have the API key fields
        assert hasattr(settings, 'groq_api_key'), \
            "Settings should have groq_api_key field"
        assert hasattr(settings, 'openai_api_key'), \
            "Settings should have openai_api_key field"
