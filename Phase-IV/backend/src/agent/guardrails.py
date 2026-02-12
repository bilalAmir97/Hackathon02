"""Guardrails module for confirmation flows and safety checks.

This module implements confirmation flows for destructive actions like
completing or deleting tasks. It ensures users explicitly confirm before
executing potentially unwanted operations.
"""

import re
from datetime import datetime
from typing import Any

# Actions that require confirmation before execution
CONFIRMATION_REQUIRED_ACTIONS = {
    'complete_task',
    'delete_task'
}

# Keywords indicating explicit confirmation
CONFIRMATION_KEYWORDS = {
    'yes', 'confirm', 'go ahead', 'do it', 'proceed', 'sure', 'ok', 'okay'
}

# Keywords indicating rejection/cancellation
REJECTION_KEYWORDS = {
    'no', 'cancel', 'stop', 'don\'t', 'nevermind', 'never mind'
}


def requires_confirmation(action: str) -> bool:
    """Check if an action requires confirmation before execution.

    Args:
        action: The action/tool name to check

    Returns:
        True if confirmation is required, False otherwise
    """
    return action in CONFIRMATION_REQUIRED_ACTIONS


def is_explicit_confirmation(message: str) -> bool:
    """Detect if a message contains explicit confirmation.

    Args:
        message: User message to analyze

    Returns:
        True if message contains confirmation, False otherwise
    """
    message_lower = message.lower().strip()

    # First check for rejection keywords to avoid false positives
    # (e.g., "don't do it" should not match "do it")
    for keyword in REJECTION_KEYWORDS:
        if keyword in message_lower:
            return False

    # Check for confirmation keywords using word boundaries
    # Split into words and check for exact matches
    words = re.split(r'\W+', message_lower)

    for keyword in CONFIRMATION_KEYWORDS:
        # Handle multi-word keywords like "go ahead" and "do it"
        keyword_words = keyword.split()
        if len(keyword_words) == 1:
            # Single word - check if it's in the word list
            if keyword in words:
                return True
        else:
            # Multi-word - check if the phrase appears in the message
            # Use word boundaries to avoid substring matches
            pattern = r'\b' + r'\s+'.join(re.escape(word) for word in keyword_words) + r'\b'
            if re.search(pattern, message_lower):
                return True

    return False


def is_rejection(message: str) -> bool:
    """Detect if a message contains rejection/cancellation.

    Args:
        message: User message to analyze

    Returns:
        True if message contains rejection, False otherwise
    """
    message_lower = message.lower().strip()

    # Check for rejection keywords
    for keyword in REJECTION_KEYWORDS:
        if keyword in message_lower:
            return True

    return False


class ConfirmationManager:
    """Manages pending confirmation state for conversations.

    Tracks actions awaiting user confirmation and handles timeouts.
    """

    def __init__(self, timeout_seconds: int = 300):
        """Initialize confirmation manager.

        Args:
            timeout_seconds: How long to keep pending confirmations (default 5 minutes)
        """
        self._pending: dict[int, dict[str, Any]] = {}
        self._timeout_seconds = timeout_seconds

    def set_pending_confirmation(
        self,
        conversation_id: int,
        action: str,
        parameters: dict[str, Any]
    ) -> None:
        """Set a pending confirmation for a conversation.

        Args:
            conversation_id: ID of the conversation
            action: Action awaiting confirmation
            parameters: Parameters for the action
        """
        self._pending[conversation_id] = {
            'action': action,
            'parameters': parameters,
            'timestamp': datetime.utcnow()
        }

    def has_pending_confirmation(self, conversation_id: int) -> bool:
        """Check if a conversation has a pending confirmation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            True if pending confirmation exists and hasn't expired
        """
        if conversation_id not in self._pending:
            return False

        # Check if expired
        pending = self._pending[conversation_id]
        age = datetime.utcnow() - pending['timestamp']

        if age.total_seconds() > self._timeout_seconds:
            # Expired - remove it
            del self._pending[conversation_id]
            return False

        return True

    def get_pending_confirmation(self, conversation_id: int) -> dict[str, Any] | None:
        """Get pending confirmation details for a conversation.

        Args:
            conversation_id: ID of the conversation

        Returns:
            Pending confirmation details or None if not found/expired
        """
        if not self.has_pending_confirmation(conversation_id):
            return None

        return self._pending[conversation_id]

    def clear_pending_confirmation(self, conversation_id: int) -> None:
        """Clear pending confirmation for a conversation.

        Args:
            conversation_id: ID of the conversation
        """
        if conversation_id in self._pending:
            del self._pending[conversation_id]


# Global confirmation manager instance
_confirmation_manager = ConfirmationManager()


def generate_confirmation_prompt(action: str, parameters: dict[str, Any]) -> str:
    """Generate a confirmation prompt for an action.

    Args:
        action: The action requiring confirmation
        parameters: Parameters for the action

    Returns:
        Confirmation prompt message
    """
    if action == 'complete_task':
        task_id = parameters.get('task_id', 'this task')
        return f"Are you sure you want to mark task {task_id} as completed? Please confirm (yes/no)."

    elif action == 'delete_task':
        task_id = parameters.get('task_id', 'this task')
        return f"Are you sure you want to delete task {task_id}? This action cannot be undone. Please confirm (yes/no)."

    else:
        return f"Are you sure you want to {action}? Please confirm (yes/no)."


def should_request_confirmation(
    action: str,
    message: str,
    conversation_history: list[dict[str, str]]
) -> bool:
    """Determine if confirmation should be requested for an action.

    Args:
        action: The action to check
        message: Current user message
        conversation_history: Previous messages in conversation

    Returns:
        True if confirmation should be requested, False otherwise
    """
    # If action doesn't require confirmation, no need to request
    if not requires_confirmation(action):
        return False

    # If message contains explicit confirmation, no need to request
    if is_explicit_confirmation(message):
        return False

    # Otherwise, request confirmation
    return True


def get_confirmation_manager() -> ConfirmationManager:
    """Get the global confirmation manager instance.

    Returns:
        Global ConfirmationManager instance
    """
    return _confirmation_manager
