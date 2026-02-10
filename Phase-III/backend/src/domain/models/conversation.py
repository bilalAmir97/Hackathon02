"""Conversation model for AI agent chat sessions.

This module defines the Conversation entity that represents a chat session
between a user and the AI agent. Conversations persist across server restarts
and maintain the complete message history.
"""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.domain.models.message import Message


class Conversation(SQLModel, table=True):
    """Represents a chat session between user and AI agent.
    
    A conversation is a container for messages exchanged between a user and
    the AI agent. Each conversation belongs to exactly one user and maintains
    timestamps for creation and last update.
    
    Attributes:
        id: Unique conversation identifier (auto-increment)
        user_id: Owner reference (foreign key to user.id)
        created_at: When conversation was started (UTC)
        updated_at: Last message timestamp (UTC)
        messages: List of messages in this conversation
    """

    __tablename__ = "conversations"

    id: int | None = Field(
        default=None,
        primary_key=True,
        nullable=False,
        description="Unique conversation identifier"
    )

    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner reference (foreign key to user.id, UUID)"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="When conversation was started (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last message timestamp (UTC)"
    )

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-09T18:00:00Z",
                "updated_at": "2026-02-09T18:30:00Z"
            }
        }
