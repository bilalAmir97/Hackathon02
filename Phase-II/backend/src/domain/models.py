"""Domain models for the todo application.

This module defines the SQLModel entities for User and Task, including
validation rules, relationships, and database constraints. All models
use UUID v4 identifiers and UTC timestamps.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from pydantic import EmailStr
from sqlalchemy import Index
from sqlmodel import Field, SQLModel


class UserStatus(str, Enum):
    """User account status enumeration.

    Defines the valid states for a user account. Users can transition between
    active, disabled, and deleted states based on administrative actions or
    security policies.

    Attributes:
        ACTIVE: User account is active and can authenticate
        DISABLED: User account is temporarily disabled (can be re-enabled)
        DELETED: User account is marked as deleted (terminal state)
    """

    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class TaskStatus(str, Enum):
    """Task status enumeration.

    Defines the valid states for a task. Tasks can transition between
    pending and completed states freely.

    Attributes:
        PENDING: Task is not yet completed
        COMPLETED: Task has been marked as done
    """

    PENDING = "pending"
    COMPLETED = "completed"


class User(SQLModel, table=True):
    """User entity representing a person using the todo application.

    Users own tasks and are identified by UUID v4. Email is used for
    authentication. Extended with password hashing, account status tracking,
    and password change timestamp for JWT token invalidation.

    Attributes:
        id: Unique user identifier (UUID v4)
        email: User email address (unique, validated)
        password_hash: Bcrypt hash of user password (never store plaintext)
        status: Account status (active/disabled/deleted)
        password_changed_at: Timestamp of last password change (for token invalidation)
        created_at: Account creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
    """

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
        """Pydantic model configuration."""

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
    """Task entity representing a single todo item.

    Tasks are owned by users and have a title, optional description,
    and status. All tasks are user-scoped and enforce ownership at
    the application layer.

    Database Indexes:
        - idx_task_user_id: Single-column index on user_id (for ownership queries)
        - idx_task_user_status: Composite index on (user_id, status) for filtered queries
        - idx_task_user_created: Composite index on (user_id, created_at DESC) for ordered queries

    Attributes:
        id: Unique task identifier (UUID v4)
        user_id: Owner reference (foreign key to user.id)
        title: Task title (1-200 characters)
        description: Optional task description (max 2000 characters)
        status: Task status (pending or completed)
        created_at: Task creation timestamp (UTC)
        updated_at: Last update timestamp (UTC)
    """

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
        """Pydantic model configuration."""

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
    """Create all database tables defined in SQLModel metadata.

    This function creates tables for User and Task entities with all
    constraints, indexes, and foreign keys. Should be called during
    application startup in development.

    Args:
        engine: SQLAlchemy async engine instance

    Note:
        For production deployments, use Alembic migrations instead of
        this function to manage schema changes with proper versioning.

    Example:
        from src.database import engine
        from src.domain.models import create_tables

        async def startup():
            await create_tables(engine)
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
