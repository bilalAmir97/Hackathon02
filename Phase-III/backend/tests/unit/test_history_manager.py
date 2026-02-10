"""Unit tests for HistoryManager.

Task IDs: T010-T014
Tests conversation history truncation and formatting.
"""

import pytest

from src.agent.history_manager import HistoryManager


class TestHistoryManagerNoTruncation:
    """Test no truncation when under limit (T010)."""

    def test_no_truncation_when_under_limit(self):
        """Given a history with fewer messages than max_messages,
        when truncate_history is called, then all messages should be preserved."""
        manager = HistoryManager(max_messages=20)
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
        ]

        result = manager.truncate_history(messages)

        assert len(result) == 4
        assert result == messages

    def test_no_truncation_when_exactly_at_limit(self):
        """Given a history with exactly max_messages,
        when truncate_history is called, then all messages should be preserved."""
        manager = HistoryManager(max_messages=4)
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
        ]

        result = manager.truncate_history(messages)

        assert len(result) == 4
        assert result == messages


class TestHistoryManagerTruncation:
    """Test truncation when over limit (T011)."""

    def test_truncation_keeps_most_recent_messages(self):
        """Given a history with more messages than max_messages,
        when truncate_history is called, then only most recent N messages should be kept."""
        manager = HistoryManager(max_messages=4)
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "Message 3"},
            {"role": "assistant", "content": "Response 3"},
            {"role": "user", "content": "Message 4"},
            {"role": "assistant", "content": "Response 4"},
        ]

        result = manager.truncate_history(messages)

        assert len(result) == 4
        assert result[0]["content"] == "Message 3"
        assert result[1]["content"] == "Response 3"
        assert result[2]["content"] == "Message 4"
        assert result[3]["content"] == "Response 4"

    def test_truncation_with_20_message_limit(self):
        """Given a history with 30 messages and max_messages=20,
        when truncate_history is called, then only most recent 20 should be kept."""
        manager = HistoryManager(max_messages=20)
        messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"} for i in range(30)]

        result = manager.truncate_history(messages)

        assert len(result) == 20
        assert result[0]["content"] == "Message 10"
        assert result[-1]["content"] == "Message 29"


class TestHistoryManagerSystemInstructions:
    """Test system instructions added correctly (T012)."""

    def test_system_instructions_prepended(self):
        """Given messages and system instructions,
        when format_for_agent is called, then system message should be first."""
        manager = HistoryManager(max_messages=20)
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
        ]
        system_instructions = "You are a helpful task management assistant."

        result = manager.format_for_agent(messages, system_instructions)

        assert len(result) == 3
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_instructions
        assert result[1] == messages[0]
        assert result[2] == messages[1]

    def test_system_instructions_with_truncated_history(self):
        """Given a long history that needs truncation,
        when format_for_agent is called, then system instructions should be preserved."""
        manager = HistoryManager(max_messages=4)
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "Message 3"},
            {"role": "assistant", "content": "Response 3"},
        ]
        system_instructions = "You are a helpful assistant."

        result = manager.format_for_agent(messages, system_instructions)

        # Should have system message + 4 most recent messages
        assert len(result) == 5
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_instructions
        assert result[1]["content"] == "Message 2"
        assert result[-1]["content"] == "Response 3"


class TestHistoryManagerEmptyHistory:
    """Test empty history handling (T013)."""

    def test_empty_history_returns_empty_list(self):
        """Given an empty history,
        when truncate_history is called, then empty list should be returned."""
        manager = HistoryManager(max_messages=20)
        messages = []

        result = manager.truncate_history(messages)

        assert result == []
        assert len(result) == 0

    def test_empty_history_with_system_instructions(self):
        """Given an empty history and system instructions,
        when format_for_agent is called, then only system message should be returned."""
        manager = HistoryManager(max_messages=20)
        messages = []
        system_instructions = "You are a helpful assistant."

        result = manager.format_for_agent(messages, system_instructions)

        assert len(result) == 1
        assert result[0]["role"] == "system"
        assert result[0]["content"] == system_instructions


class TestHistoryManagerMessageOrderPreservation:
    """Test message order preservation (T014)."""

    def test_message_order_preserved_after_truncation(self):
        """Given a history with specific message order,
        when truncate_history is called, then order should be preserved (oldest to newest)."""
        manager = HistoryManager(max_messages=6)
        messages = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
            {"role": "user", "content": "Message 3"},
            {"role": "assistant", "content": "Response 3"},
            {"role": "user", "content": "Message 4"},
            {"role": "assistant", "content": "Response 4"},
            {"role": "user", "content": "Message 5"},
            {"role": "assistant", "content": "Response 5"},
        ]

        result = manager.truncate_history(messages)

        assert len(result) == 6
        # Should keep messages 3, 4, 5 (most recent 6 messages)
        assert result[0]["content"] == "Message 3"
        assert result[1]["content"] == "Response 3"
        assert result[2]["content"] == "Message 4"
        assert result[3]["content"] == "Response 4"
        assert result[4]["content"] == "Message 5"
        assert result[5]["content"] == "Response 5"

    def test_chronological_order_maintained(self):
        """Given messages in chronological order,
        when format_for_agent is called, then chronological order should be maintained."""
        manager = HistoryManager(max_messages=20)
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Second"},
            {"role": "user", "content": "Third"},
        ]
        system_instructions = "System"

        result = manager.format_for_agent(messages, system_instructions)

        assert result[0]["content"] == "System"
        assert result[1]["content"] == "First"
        assert result[2]["content"] == "Second"
        assert result[3]["content"] == "Third"
