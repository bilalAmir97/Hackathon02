"""Conversation history manager with truncation.

Task IDs: T019-T022
Manages conversation history truncation to stay within token limits.
"""

import logging

logger = logging.getLogger(__name__)


class HistoryManager:
    """Manages conversation history with message-based truncation.

    Truncates conversation history to most recent N messages to stay within
    token limits. Uses simple message counting rather than token counting
    for predictability and simplicity.
    """

    def __init__(self, max_messages: int = 20):
        """Initialize history manager.

        Args:
            max_messages: Maximum number of messages to keep (default: 20)
        """
        self.max_messages = max_messages

    def truncate_history(self, messages: list[dict[str, str]]) -> list[dict[str, str]]:
        """Keep most recent N messages.

        Truncates message list to keep only the most recent max_messages.
        Preserves message order (oldest to newest).

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys

        Returns:
            Truncated message list (most recent N messages)
        """
        if len(messages) <= self.max_messages:
            return messages

        # Log truncation event
        truncated_count = len(messages) - self.max_messages
        logger.info(
            "Truncating conversation history",
            extra={
                "event": "history_truncation",
                "original_count": len(messages),
                "truncated_count": truncated_count,
                "kept_count": self.max_messages,
            },
        )

        # Keep most recent N messages
        return messages[-self.max_messages :]

    def format_for_agent(
        self, messages: list[dict[str, str]], system_instructions: str
    ) -> list[dict[str, str]]:
        """Format messages for agent with system prompt.

        Truncates history if needed and prepends system instructions.

        Args:
            messages: List of message dictionaries
            system_instructions: System prompt to prepend

        Returns:
            Formatted message list: [system_message, ...truncated_messages]
        """
        # Truncate history first
        truncated_messages = self.truncate_history(messages)

        # Prepend system instructions
        formatted_messages = [{"role": "system", "content": system_instructions}]
        formatted_messages.extend(truncated_messages)

        return formatted_messages
