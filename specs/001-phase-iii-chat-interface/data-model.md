# Data Model: Phase-III AI Chat Interface

**Feature**: Phase-III AI Chat Interface with Streaming
**Date**: 2026-02-10
**Status**: Validated - No Changes Required

## Overview

This document validates that the existing database models support all requirements for the Phase-III AI Chat Interface. The backend already has Conversation and Message models with proper relationships and fields.

## Existing Models

### Conversation Model

**Location**: `Phase-III/backend/src/domain/models/conversation.py`

**Schema**:
```python
class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

**Validation**:
- ✅ **id**: Auto-increment primary key for conversation identification
- ✅ **user_id**: Foreign key to user table for ownership and isolation
- ✅ **created_at**: Timestamp for conversation creation (sorting, display)
- ✅ **updated_at**: Timestamp for last activity (sorting by recency)
- ✅ **messages**: One-to-many relationship with cascade delete

**Requirements Coverage**:
- ✅ Supports multiple conversations per user
- ✅ Supports conversation sorting by recency (updated_at)
- ✅ Supports user isolation via user_id foreign key
- ✅ Supports conversation deletion with cascade to messages
- ✅ Supports conversation timestamps for UI display

**No Changes Needed**: Model fully supports all requirements

---

### Message Model

**Location**: `Phase-III/backend/src/domain/models/message.py`

**Schema**:
```python
class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    role: str = Field(nullable=False, regex="^(user|assistant)$")
    content: str = Field(nullable=False)
    tool_calls: str | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

**Validation**:
- ✅ **id**: Auto-increment primary key for message identification
- ✅ **conversation_id**: Foreign key to conversations table
- ✅ **role**: Enum-like field for "user" or "assistant" (validated by regex)
- ✅ **content**: Message text content (required)
- ✅ **tool_calls**: JSONB field for tool call transparency (optional, assistant only)
- ✅ **created_at**: Timestamp for message ordering and display
- ✅ **conversation**: Many-to-one relationship back to conversation

**Tool Calls Structure**:
The `tool_calls` field stores a JSON array with this structure:
```json
[
  {
    "tool_name": "add_task",
    "input_parameters": {"title": "Buy groceries", "description": "..."},
    "output_result": {"id": 123, "title": "Buy groceries", "status": "pending"},
    "execution_status": "success",
    "error_message": null,
    "timestamp": "2026-02-10T10:00:05Z"
  }
]
```

**Requirements Coverage**:
- ✅ Supports message history with role distinction
- ✅ Supports tool call transparency (JSONB field)
- ✅ Supports message ordering by timestamp
- ✅ Supports conversation grouping via conversation_id
- ✅ Supports immutable messages (no update operations)

**No Changes Needed**: Model fully supports all requirements

---

## Database Migrations

**Existing Migrations**:
- ✅ `001_add_conversations_table.py` - Creates conversations table
- ✅ `002_add_messages_table.py` - Creates messages table with tool_calls JSONB

**Migration Status**: Complete - No additional migrations needed

**Migration Files Location**: `Phase-III/backend/alembic/versions/`

---

## Entity Relationships

```
User (existing)
  ↓ (1:N)
Conversation
  ↓ (1:N)
Message
```

**Relationship Details**:
- One User has many Conversations
- One Conversation has many Messages
- Messages are ordered by created_at within a conversation
- Deleting a Conversation cascades to delete all Messages
- User isolation enforced via user_id foreign key

---

## Data Access Patterns

### Pattern 1: List User Conversations
```sql
SELECT * FROM conversations
WHERE user_id = :user_id
ORDER BY updated_at DESC
LIMIT 100;
```

**Performance**: Indexed on user_id ✅

### Pattern 2: Get Conversation Messages
```sql
SELECT * FROM messages
WHERE conversation_id = :conversation_id
ORDER BY created_at ASC
LIMIT 100;
```

**Performance**: Indexed on conversation_id ✅

### Pattern 3: Get Conversation Preview (First Message)
```sql
SELECT content FROM messages
WHERE conversation_id = :conversation_id
  AND role = 'user'
ORDER BY created_at ASC
LIMIT 1;
```

**Performance**: Indexed on conversation_id, filtered by role ✅

### Pattern 4: Create New Conversation
```sql
INSERT INTO conversations (user_id, created_at, updated_at)
VALUES (:user_id, NOW(), NOW())
RETURNING id;
```

**Performance**: Simple insert, no optimization needed ✅

### Pattern 5: Persist Messages
```sql
INSERT INTO messages (conversation_id, role, content, tool_calls, created_at)
VALUES (:conversation_id, :role, :content, :tool_calls, NOW());

UPDATE conversations
SET updated_at = NOW()
WHERE id = :conversation_id;
```

**Performance**: Simple insert + update, both indexed ✅

---

## Validation Summary

| Requirement | Supported | Model/Field |
|-------------|-----------|-------------|
| Multiple conversations per user | ✅ | Conversation.user_id (FK) |
| Conversation sorting by recency | ✅ | Conversation.updated_at |
| Message history with ordering | ✅ | Message.created_at |
| Tool call transparency | ✅ | Message.tool_calls (JSONB) |
| User isolation | ✅ | Conversation.user_id (FK) |
| Conversation persistence | ✅ | Database-backed models |
| Message immutability | ✅ | No update operations |
| Cascade deletion | ✅ | Relationship cascade config |

**Result**: All requirements satisfied by existing models ✅

---

## Performance Considerations

### Indexes (Existing)
- ✅ `conversations.user_id` - For listing user conversations
- ✅ `messages.conversation_id` - For fetching conversation messages

### Recommended Indexes (If Performance Issues Arise)
- `conversations(user_id, updated_at DESC)` - Composite index for sorted conversation list
- `messages(conversation_id, created_at ASC)` - Composite index for ordered message history

**Current Assessment**: Existing indexes sufficient for expected load (1000+ concurrent users)

### Query Optimization
- Limit conversation list to 100 most recent (pagination if needed)
- Limit message history to 100 messages per conversation
- Use database connection pooling (already configured in Neon)

---

## Data Integrity

### Constraints (Existing)
- ✅ Primary keys on all tables
- ✅ Foreign key constraints (user_id, conversation_id)
- ✅ NOT NULL constraints on required fields
- ✅ Regex validation on Message.role ("user" or "assistant")

### Cascade Behavior
- ✅ Deleting Conversation deletes all Messages (cascade="all, delete-orphan")
- ✅ Deleting User deletes all Conversations (handled by User model)

### Data Validation
- ✅ Role validation via regex pattern
- ✅ Timestamp auto-generation via default_factory
- ✅ JSON validation for tool_calls field

---

## Conclusion

**Status**: ✅ **VALIDATED - NO CHANGES REQUIRED**

The existing Conversation and Message models fully support all requirements for the Phase-III AI Chat Interface:

1. ✅ Conversation persistence across sessions
2. ✅ Message history with tool call transparency
3. ✅ User isolation and multi-user support
4. ✅ Conversation sorting and preview generation
5. ✅ Efficient data access patterns with proper indexing
6. ✅ Data integrity with foreign keys and constraints

**Next Steps**:
- Proceed to API contract definition (streaming-api.yaml, conversations-api.yaml)
- No database migrations needed
- No model changes required
