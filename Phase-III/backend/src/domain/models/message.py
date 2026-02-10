"""Message model for conversation messages.

This module defines the Message entity that represents a single message
in a conversation between a user and the AI agent. Messages can be from
either the user or the assistant, and assistant messages may include
tool call transparency data.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.domain.models.conversation import Conversation


class Message(SQLModel, table=True):
    """Represents a single message in a conversation.
    
    Messages are immutable once created and belong to exactly one conversation.
    User messages contain only text content, while assistant messages may also
    include structured tool call data for transparency and auditability.
    
    Attributes:
        id: Unique message identifier (auto-increment)
        conversation_id: Parent conversation reference
        role: Message sender ("user" or "assistant")
        content: Message text content
        tool_calls: Optional JSONB array of tool invocations (assistant only)
        created_at: When message was created (UTC)
        conversation: Parent conversation relationship
    """

    __tablename__ = "messages"

    id: int | None = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="Unique message identifier"
    )

    conversation_id: int = Field(
        foreign_key="conversations.id",
        index=True,
        nullable=False,
        description="Parent conversation reference"
    )

    role: str = Field(
        nullable=False,
        regex="^(user|assistant)$",
        description="Message sender: 'user' or 'assistant'"
    )

    content: str = Field(
        nullable=False,
        description="Message text content"
    )

    tool_calls: str | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Optional JSONB array of tool invocations (assistant only)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When message was created (UTC)"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "conversation_id": 1,
                "role": "user",
                "content": "Create a task to buy groceries",
                "tool_calls": None,
                "created_at": "2026-02-09T18:30:00Z"
            }
        }
