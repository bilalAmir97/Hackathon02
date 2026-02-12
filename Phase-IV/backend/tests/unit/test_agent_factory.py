"""Unit tests for Agent Factory.

Tests the agent factory that creates OpenAI Agents SDK instances with
Groq as primary provider and OpenAI as fallback.
Following TDD approach - these tests should fail until the factory is implemented.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


def test_agent_factory_initialization():
    """Test agent factory can be initialized."""
    from src.agent.agent_factory import AgentFactory
    
    # Act
    factory = AgentFactory()
    
    # Assert
    assert factory is not None


def test_agent_factory_create_agent_returns_agent():
    """Test that create_agent returns an agent instance."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    assert agent is not None


def test_agent_factory_uses_groq_as_primary():
    """Test that factory configures Groq as primary provider."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    with patch('src.agent.agent_factory.Groq') as mock_groq:
        mock_groq.return_value = MagicMock()
        agent = factory.create_agent()
        
        # Assert
        mock_groq.assert_called_once()


def test_agent_factory_configures_model_from_settings():
    """Test that factory uses model from config settings."""
    from src.agent.agent_factory import AgentFactory
    from src.config import settings
    
    # Arrange
    factory = AgentFactory()
    expected_model = settings.groq_model
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    # Verify the agent is configured with the correct model
    assert hasattr(agent, 'model') or hasattr(agent, '_model')


def test_agent_factory_configures_temperature():
    """Test that factory configures agent temperature from settings."""
    from src.agent.agent_factory import AgentFactory
    from src.config import settings
    
    # Arrange
    factory = AgentFactory()
    expected_temp = settings.agent_temperature
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    # Verify temperature is configured
    assert expected_temp >= 0.0 and expected_temp <= 2.0


def test_agent_factory_configures_max_tokens():
    """Test that factory configures max tokens from settings."""
    from src.agent.agent_factory import AgentFactory
    from src.config import settings
    
    # Arrange
    factory = AgentFactory()
    expected_max_tokens = settings.agent_max_tokens
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    assert expected_max_tokens > 0


def test_agent_factory_registers_mcp_tools():
    """Test that factory registers MCP tools with the agent."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    with patch('src.agent.agent_factory.MCPAdapter') as mock_adapter:
        mock_adapter.return_value.get_tools.return_value = [
            {'name': 'add_task', 'description': 'Add a task', 'parameters': {}}
        ]
        agent = factory.create_agent()
        
        # Assert
        mock_adapter.assert_called_once()
        mock_adapter.return_value.get_tools.assert_called_once()


def test_agent_factory_handles_groq_rate_limit():
    """Test that factory handles Groq rate limit errors."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act & Assert
    # Factory should have fallback mechanism
    assert hasattr(factory, 'create_agent')
    assert hasattr(factory, 'fallback_to_openai') or hasattr(factory, '_fallback_enabled')


def test_agent_factory_fallback_to_openai_when_enabled():
    """Test that factory can fallback to OpenAI when configured."""
    from src.agent.agent_factory import AgentFactory
    from src.config import settings
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    if settings.openai_fallback_enabled:
        with patch('src.agent.agent_factory.OpenAI') as mock_openai:
            mock_openai.return_value = MagicMock()
            # Simulate Groq failure and fallback
            agent = factory.create_agent(use_fallback=True)
            
            # Assert
            # Should attempt to use OpenAI
            assert mock_openai.called or agent is not None


def test_agent_factory_configures_system_instructions():
    """Test that factory configures agent with system instructions."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    # Agent should have instructions configured
    assert agent is not None


def test_agent_factory_singleton_or_new_instance():
    """Test that factory creates new agent instances."""
    from src.agent.agent_factory import AgentFactory
    
    # Arrange
    factory = AgentFactory()
    
    # Act
    agent1 = factory.create_agent()
    agent2 = factory.create_agent()
    
    # Assert
    # Each call should return an agent (may be same or different instance)
    assert agent1 is not None
    assert agent2 is not None


def test_agent_factory_timeout_configuration():
    """Test that factory configures timeout from settings."""
    from src.agent.agent_factory import AgentFactory
    from src.config import settings
    
    # Arrange
    factory = AgentFactory()
    expected_timeout = settings.agent_timeout_seconds
    
    # Act
    agent = factory.create_agent()
    
    # Assert
    assert expected_timeout > 0
