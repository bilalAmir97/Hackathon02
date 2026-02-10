"""Domain models for the todo application.

This module defines the SQLModel entities for User, Task, Conversation, and Message,
including validation rules, relationships, and database constraints.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Index
from sqlmodel import Field, SQLModel

# Import new conversation models
from .conversation import Conversation
from .message import Message


class UserStatus(str, Enum):
    """User account status enumeration."""
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    COMPLETED = "completed"


class User(SQLModel, table=True):
    """User entity representing a person using the todo application."""
    __tablename__ = "user"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique user identifier",
    )
    email: EmailStr = Field(
        unique=True,
        index=True,
        max_length=255,
        nullable=False,
        description="User email address (RFC 5322 compliant)",
    )
    password_hash: str = Field(
        nullable=False,
        description="Bcrypt hash of user password (never store plaintext)",
    )
    status: UserStatus = Field(
        default=UserStatus.ACTIVE,
        nullable=False,
        index=True,
        description="Account status (active/disabled/deleted)",
    )
    password_changed_at: datetime | None = Field(
        default=None,
        nullable=True,
        description="Timestamp of last password change (for token invalidation)",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Account creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "status": "active",
                "created_at": "2026-01-12T00:00:00Z",
                "updated_at": "2026-01-12T00:00:00Z",
            }
        }


class Task(SQLModel, table=True):
    """Task entity representing a single todo item."""
    __tablename__ = "task"
    __table_args__ = (
        Index("idx_task_user_status", "user_id", "status"),
        Index("idx_task_user_created", "user_id", "created_at"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique task identifier",
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner reference (foreign key to user.id)",
    )
    title: str = Field(
        min_length=1, max_length=200, nullable=False, description="Task title (1-200 characters)"
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Optional task description (max 2000 characters)",
    )
    status: TaskStatus = Field(
        default=TaskStatus.PENDING, nullable=False, description="Task status: pending or completed"
    )
    version: int = Field(
        default=1,
        nullable=False,
        description="Version number for optimistic concurrency control"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project documentation",
                "description": "Write comprehensive API documentation",
                "status": "pending",
                "created_at": "2026-01-12T00:00:00Z",
                "updated_at": "2026-01-12T00:00:00Z",
            }
        }


async def create_tables(engine) -> None:
    """Create all database tables defined in SQLModel metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


__all__ = [
    "User",
    "UserStatus",
    "Task",
    "TaskStatus",
    "Conversation",
    "Message",
    "create_tables",
]
