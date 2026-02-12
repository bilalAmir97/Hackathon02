"""Unit tests for guardrails module (confirmation flows).

Tests the confirmation flow detection and management for destructive actions.
Following TDD approach - these tests should fail until guardrails are implemented.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch


@pytest.mark.asyncio
async def test_guardrails_detects_confirmation_required_action():
    """Test that guardrails detect actions requiring confirmation."""
    from src.agent.guardrails import requires_confirmation

    # Arrange
    actions_requiring_confirmation = [
        'complete_task',
        'delete_task'
    ]

    actions_not_requiring_confirmation = [
        'add_task',
        'list_tasks',
        'update_task'
    ]

    # Act & Assert
    for action in actions_requiring_confirmation:
        assert requires_confirmation(action) is True, f"{action} should require confirmation"

    for action in actions_not_requiring_confirmation:
        assert requires_confirmation(action) is False, f"{action} should not require confirmation"


@pytest.mark.asyncio
async def test_guardrails_detects_explicit_confirmation():
    """Test that guardrails detect explicit confirmation in messages."""
    from src.agent.guardrails import is_explicit_confirmation

    # Arrange
    confirmation_messages = [
        "Yes",
        "Yes, please do it",
        "Confirm",
        "Go ahead",
        "Do it",
        "Proceed",
        "Yes, I'm sure"
    ]

    non_confirmation_messages = [
        "No",
        "Cancel",
        "Don't do it",
        "Maybe later",
        "I'm not sure",
        "Create a task"
    ]

    # Act & Assert
    for message in confirmation_messages:
        assert is_explicit_confirmation(message) is True, f"'{message}' should be detected as confirmation"

    for message in non_confirmation_messages:
        assert is_explicit_confirmation(message) is False, f"'{message}' should not be detected as confirmation"


@pytest.mark.asyncio
async def test_guardrails_detects_rejection():
    """Test that guardrails detect rejection/cancellation in messages."""
    from src.agent.guardrails import is_rejection

    # Arrange
    rejection_messages = [
        "No",
        "Cancel",
        "Don't do it",
        "No, cancel that",
        "Stop",
        "Nevermind",
        "No thanks"
    ]

    non_rejection_messages = [
        "Yes",
        "Confirm",
        "Create a task",
        "Show me tasks"
    ]

    # Act & Assert
    for message in rejection_messages:
        assert is_rejection(message) is True, f"'{message}' should be detected as rejection"

    for message in non_rejection_messages:
        assert is_rejection(message) is False, f"'{message}' should not be detected as rejection"


@pytest.mark.asyncio
async def test_guardrails_manages_pending_confirmation_state():
    """Test that guardrails can track pending confirmation state."""
    from src.agent.guardrails import ConfirmationManager

    # Arrange
    manager = ConfirmationManager()
    conversation_id = 1
    action = 'complete_task'
    parameters = {'task_id': '123'}

    # Act - Set pending confirmation
    manager.set_pending_confirmation(conversation_id, action, parameters)

    # Assert
    assert manager.has_pending_confirmation(conversation_id) is True
    pending = manager.get_pending_confirmation(conversation_id)
    assert pending is not None
    assert pending['action'] == action
    assert pending['parameters'] == parameters


@pytest.mark.asyncio
async def test_guardrails_clears_pending_confirmation():
    """Test that guardrails can clear pending confirmation state."""
    from src.agent.guardrails import ConfirmationManager

    # Arrange
    manager = ConfirmationManager()
    conversation_id = 1
    manager.set_pending_confirmation(conversation_id, 'complete_task', {'task_id': '123'})

    # Act
    manager.clear_pending_confirmation(conversation_id)

    # Assert
    assert manager.has_pending_confirmation(conversation_id) is False
    assert manager.get_pending_confirmation(conversation_id) is None


@pytest.mark.asyncio
async def test_guardrails_handles_confirmation_timeout():
    """Test that pending confirmations expire after timeout."""
    from src.agent.guardrails import ConfirmationManager
    import time

    # Arrange
    manager = ConfirmationManager(timeout_seconds=1)  # 1 second timeout
    conversation_id = 1
    manager.set_pending_confirmation(conversation_id, 'complete_task', {'task_id': '123'})

    # Act - Wait for timeout
    time.sleep(1.5)

    # Assert
    assert manager.has_pending_confirmation(conversation_id) is False, "Should expire after timeout"


@pytest.mark.asyncio
async def test_guardrails_generates_confirmation_prompt():
    """Test that guardrails generate appropriate confirmation prompts."""
    from src.agent.guardrails import generate_confirmation_prompt

    # Arrange
    test_cases = [
        ('complete_task', {'task_id': '123'}, 'complete'),
        ('delete_task', {'task_id': '456'}, 'delete')
    ]

    # Act & Assert
    for action, parameters, expected_keyword in test_cases:
        prompt = generate_confirmation_prompt(action, parameters)
        assert expected_keyword in prompt.lower(), f"Prompt should mention {expected_keyword}"
        assert 'confirm' in prompt.lower() or 'sure' in prompt.lower(), "Prompt should ask for confirmation"


@pytest.mark.asyncio
async def test_guardrails_integrates_with_orchestration():
    """Test that guardrails integrate with agent orchestration flow."""
    from src.agent.guardrails import should_request_confirmation

    # Arrange
    conversation_history = [
        {'role': 'user', 'content': 'Create a task'},
        {'role': 'assistant', 'content': 'Task created'}
    ]

    # Test case 1: Action requires confirmation, no explicit confirmation in message
    message = "Mark task 123 as done"
    action = "complete_task"

    # Act
    result = should_request_confirmation(action, message, conversation_history)

    # Assert
    assert result is True, "Should request confirmation for complete_task without explicit confirmation"

    # Test case 2: Action requires confirmation, but explicit confirmation in message
    message_with_confirmation = "Yes, mark task 123 as done"

    # Act
    result2 = should_request_confirmation(action, message_with_confirmation, conversation_history)

    # Assert
    assert result2 is False, "Should not request confirmation when explicit confirmation present"

    # Test case 3: Action doesn't require confirmation
    action_no_confirmation = "add_task"
    message3 = "Create a task"

    # Act
    result3 = should_request_confirmation(action_no_confirmation, message3, conversation_history)

    # Assert
    assert result3 is False, "Should not request confirmation for add_task"
