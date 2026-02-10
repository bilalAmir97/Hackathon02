# Data Model: AI Orchestration Layer - Agent Chat Endpoint

**Date**: 2026-02-09
**Feature**: Phase III AI Agent Chat Endpoint
**Branch**: `001-phase-iii-agent-chat-endpoint`

## Overview

This document defines the database schema for conversation persistence in the AI agent orchestration layer. The design supports stateless architecture with complete conversation history stored in PostgreSQL.

## Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│  (existing)     │
└────────┬────────┘
         │ 1
         │
         │ *
┌────────▼────────────┐
│   Conversation      │
│                     │
│  - id (PK)          │
│  - user_id (FK)     │
│  - created_at       │
│  - updated_at       │
└────────┬────────────┘
         │ 1
         │
         │ *
┌────────▼────────────┐
│     Message         │
│                     │
│  - id (PK)          │
│  - conversation_id  │
│  - role             │
│  - content          │
│  - tool_calls       │
│  - created_at       │
└─────────────────────┘
```

## Entity Definitions

### Conversation

**Purpose**: Represents a chat session between a user and the AI agent.

**Attributes**:
- `id` (integer, primary key): Unique conversation identifier
- `user_id` (string/UUID, foreign key): References users.id
- `created_at` (timestamp): When conversation was started
- `updated_at` (timestamp): Last message timestamp

**Relationships**:
- Belongs to one User
- Has many Messages

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user conversation queries

**Business Rules**:
- A conversation must belong to exactly one user
- Conversations cannot be transferred between users
- Conversations are never deleted (soft delete if needed in future)
- `updated_at` is updated whenever a new message is added

**SQLModel Definition**:
```python
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

class Conversation(SQLModel, table=True):
    """Represents a chat session between user and AI agent."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "created_at": "2026-02-09T18:00:00Z",
                "updated_at": "2026-02-09T18:30:00Z"
            }
        }
```

### Message

**Purpose**: Represents a single message in a conversation (user or assistant).

**Attributes**:
- `id` (integer, primary key): Unique message identifier
- `conversation_id` (integer, foreign key): References conversations.id
- `role` (string): Either "user" or "assistant"
- `content` (text): Message text content
- `tool_calls` (JSONB, nullable): Structured tool call data (assistant messages only)
- `created_at` (timestamp): When message was created

**Relationships**:
- Belongs to one Conversation

**Indexes**:
- Primary key on `id`
- Composite index on `(conversation_id, created_at)` for efficient history queries

**Business Rules**:
- `role` must be either "user" or "assistant"
- User messages never have `tool_calls` (always null)
- Assistant messages may have `tool_calls` if tools were invoked
- Messages are immutable once created (no updates)
- Messages are ordered by `created_at` within a conversation

**Tool Calls Schema** (stored as JSONB):
```json
[
  {
    "tool_name": "add_task",
    "input_parameters": {
      "title": "Buy groceries",
      "description": "Milk, eggs, bread"
    },
    "output_result": {
      "id": 123,
      "title": "Buy groceries",
      "status": "pending",
      "version": 1
    },
    "execution_status": "success",
    "error_message": null,
    "timestamp": "2026-02-09T18:30:00Z"
  }
]
```

**SQLModel Definition**:
```python
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel, Column, JSON
from typing import Optional

class Message(SQLModel, table=True):
    """Represents a single message in a conversation."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: str = Field(nullable=False, regex="^(user|assistant)$")
    content: str = Field(nullable=False)
    tool_calls: Optional[str] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")

    class Config:
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
```

## Database Migration

**Alembic Migration Script**:
```python
"""Add conversation and message tables

Revision ID: 001_add_conversations
Revises: <previous_revision>
Create Date: 2026-02-09 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_add_conversations'
down_revision = '<previous_revision>'
branch_labels = None
depends_on = None

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tool_calls', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])

def downgrade():
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_table('messages')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
```

## Query Patterns

### 1. Create New Conversation
```python
async def create_conversation(user_id: str, db: AsyncSession) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(user_id=user_id)
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation
```

### 2. Add Message to Conversation
```python
async def add_message(
    conversation_id: int,
    role: str,
    content: str,
    tool_calls: Optional[list[dict]],
    db: AsyncSession
) -> Message:
    """Add a message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=json.dumps(tool_calls) if tool_calls else None
    )
    db.add(message)

    # Update conversation updated_at
    conversation = await db.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)
    return message
```

### 3. Fetch Conversation History
```python
async def get_conversation_history(
    conversation_id: int,
    limit: int = 100,
    db: AsyncSession
) -> list[Message]:
    """Fetch conversation history (most recent N messages)."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return result.scalars().all()
```

### 4. Get User's Conversations
```python
async def get_user_conversations(
    user_id: str,
    limit: int = 20,
    db: AsyncSession
) -> list[Conversation]:
    """Get user's conversations ordered by most recent."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

### 5. Verify Conversation Ownership
```python
async def verify_conversation_ownership(
    conversation_id: int,
    user_id: str,
    db: AsyncSession
) -> bool:
    """Verify that a conversation belongs to a user."""
    result = await db.execute(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    return result.scalar_one_or_none() is not None
```

## Performance Considerations

### Indexes
- `conversations.user_id`: Enables fast lookup of user's conversations
- `messages.(conversation_id, created_at)`: Composite index for efficient history queries

### Query Optimization
- Limit conversation history to 100 most recent messages
- Use pagination for user's conversation list
- Consider adding `updated_at` index if sorting by recency becomes slow

### Storage Optimization
- JSONB for `tool_calls` provides efficient storage and querying
- Consider archiving old conversations if storage becomes an issue
- Monitor JSONB column size for very long tool call arrays

## Data Validation

### Application-Level Validation
```python
from pydantic import BaseModel, Field, validator

class MessageCreate(BaseModel):
    """Schema for creating a message."""
    conversation_id: int
    role: str = Field(..., regex="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=10000)
    tool_calls: Optional[list[dict]] = None

    @validator('tool_calls')
    def validate_tool_calls(cls, v, values):
        """Validate tool_calls only for assistant messages."""
        if values.get('role') == 'user' and v is not None:
            raise ValueError("User messages cannot have tool_calls")
        return v
```

### Database-Level Constraints
- CHECK constraint on `role` column: `role IN ('user', 'assistant')`
- NOT NULL constraints on required fields
- Foreign key constraints ensure referential integrity

## Testing Considerations

### Unit Tests
- Test model creation and validation
- Test relationship loading (conversation.messages)
- Test JSONB serialization/deserialization

### Integration Tests
- Test conversation creation and message addition
- Test history fetching with various limits
- Test concurrent message additions to same conversation
- Test ownership verification

### Performance Tests
- Benchmark history query with 100+ messages
- Test concurrent writes to different conversations
- Measure JSONB query performance

## Future Enhancements

### Potential Additions (Out of Scope for Phase III)
- Conversation titles (auto-generated from first message)
- Conversation archiving/deletion
- Message reactions or feedback
- Conversation sharing between users
- Full-text search on message content
- Conversation analytics (message count, tool usage stats)

## Summary

This data model provides:
- ✅ Stateless architecture support (all state in database)
- ✅ Complete conversation history persistence
- ✅ Tool call transparency and auditability
- ✅ Efficient querying with proper indexes
- ✅ User isolation and ownership verification
- ✅ Scalability for multiple concurrent conversations
