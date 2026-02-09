# Data Model: MCP Todo Server

**Date**: 2026-02-09
**Feature**: 001-phase-iii-mcp-server
**Phase**: Phase 1 - Design

## Overview

This document defines the data model extensions required for the MCP Todo Server. The existing Phase-III database schema (User and Task entities) is largely sufficient, requiring only a single field addition for optimistic concurrency control.

---

## Existing Entities (No Changes Required)

### User Entity

**Table**: `user`
**Purpose**: Represents authenticated users who own tasks

**Fields**:
- `id` (UUID, PK): Unique user identifier
- `email` (EmailStr, unique, indexed): User email address
- `password_hash` (str): Bcrypt hash of password
- `status` (UserStatus, indexed): Account status (active/disabled/deleted)
- `password_changed_at` (datetime, nullable): Last password change timestamp
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp

**Status**: ✅ No changes required - existing implementation sufficient

---

## Modified Entities

### Task Entity Extension

**Table**: `task`
**Purpose**: Represents todo items with optimistic concurrency control

**New Field**:

```python
version: int = Field(
    default=1,
    nullable=False,
    description="Version number for optimistic concurrency control"
)
```

**Complete Updated Schema**:

```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Index

class Task(SQLModel, table=True):
    """Task entity with optimistic concurrency control."""

    __tablename__ = "task"
    __table_args__ = (
        Index("idx_task_user_status", "user_id", "status"),
        Index("idx_task_user_created", "user_id", "created_at"),
    )

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Unique task identifier (UUID v4)"
    )

    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
        description="Owner reference (foreign key to user.id)"
    )

    title: str = Field(
        min_length=1,
        max_length=200,
        nullable=False,
        description="Task title (1-200 characters)"
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        nullable=True,
        description="Optional task description (max 2000 characters)"
    )

    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        nullable=False,
        description="Task status: pending or completed"
    )

    version: int = Field(
        default=1,
        nullable=False,
        description="Version number for optimistic concurrency control"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Task creation timestamp (UTC)"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="Last update timestamp (UTC)"
    )
```

**Rationale for Version Field**:
- **Optimistic Concurrency**: Detects concurrent updates without database locks
- **Stateless Architecture**: No need to maintain lock state between requests
- **Performance**: Better than pessimistic locking for low-conflict scenarios
- **Error Handling**: Clear CONFLICT error when version mismatch occurs

**Version Field Behavior**:
1. New tasks created with `version=1`
2. Each update increments version: `version = version + 1`
3. Update operations check: `WHERE id = ? AND version = ?`
4. If no rows affected → version mismatch → CONFLICT error
5. Successful update returns task with new version number

---

## Database Migration

### Alembic Migration Required

**Migration File**: `alembic/versions/XXXXXX_add_task_version_field.py`

**Up Migration**:
```python
def upgrade() -> None:
    # Add version column with default value 1
    op.add_column(
        'task',
        sa.Column('version', sa.Integer(), nullable=False, server_default='1')
    )

    # Remove server default after column is populated
    op.alter_column('task', 'version', server_default=None)
```

**Down Migration**:
```python
def downgrade() -> None:
    op.drop_column('task', 'version')
```

**Migration Command**:
```bash
cd Phase-III/backend
uv run alembic revision --autogenerate -m "add task version field"
uv run alembic upgrade head
```

---

## Entity Relationships

```
User (1) ──────< (N) Task
  │                   │
  └─ id (PK)         └─ user_id (FK)
```

**Relationship Rules**:
- One user can have many tasks (1:N)
- Each task belongs to exactly one user
- Cascade delete: When user deleted, all their tasks deleted
- User isolation: Tasks filtered by user_id on all operations

---

## Indexes

### Existing Indexes (Maintained)

1. **idx_task_user_status** (user_id, status)
   - Purpose: Fast filtering by user and status (pending/completed)
   - Used by: list_tasks tool with status filter

2. **idx_task_user_created** (user_id, created_at)
   - Purpose: Fast ordering by creation time (newest first)
   - Used by: list_tasks tool for chronological ordering

3. **user_id** (single column, auto-created by FK)
   - Purpose: Fast user ownership lookups
   - Used by: All MCP tools for user isolation

### No New Indexes Required

The version field does not require an index because:
- It's only used in WHERE clauses with id (which is PK)
- Query pattern: `WHERE id = ? AND version = ?`
- Primary key index on id is sufficient

---

## Data Validation Rules

### Task Entity Validation

**Title**:
- Required: Yes
- Min length: 1 character
- Max length: 200 characters
- Validation: Pydantic Field with min_length/max_length

**Description**:
- Required: No (nullable)
- Max length: 2000 characters
- Validation: Pydantic Field with max_length

**Status**:
- Required: Yes
- Valid values: "pending", "completed"
- Default: "pending"
- Validation: TaskStatus enum

**Version**:
- Required: Yes
- Type: Integer
- Default: 1
- Validation: Automatic (database constraint)
- Update rule: Increment on each modification

**User ID**:
- Required: Yes
- Type: UUID v4
- Validation: Foreign key constraint to user.id
- Extracted from: JWT token (not user input)

---

## State Transitions

### Task Status Lifecycle

```
[Created] → PENDING
              ↓
         (complete_task)
              ↓
          COMPLETED
              ↓
         (complete_task again)
              ↓
          COMPLETED (idempotent)
```

**Allowed Transitions**:
- PENDING → COMPLETED (via complete_task tool)
- COMPLETED → COMPLETED (idempotent, no error)

**Not Implemented** (out of scope for Phase III):
- COMPLETED → PENDING (uncomplete/reopen)
- ARCHIVED status
- DELETED status (tasks are hard-deleted)

---

## Concurrency Control

### Optimistic Locking Pattern

**Update Operation Flow**:
```sql
-- 1. Read current task with version
SELECT * FROM task WHERE id = ? AND user_id = ?;
-- Returns: {id, version: 5, ...}

-- 2. Attempt update with version check
UPDATE task
SET title = ?, description = ?, version = version + 1, updated_at = NOW()
WHERE id = ? AND user_id = ? AND version = 5;

-- 3. Check rows affected
-- If 0 rows: Version mismatch → CONFLICT error
-- If 1 row: Success → Return updated task with version = 6
```

**Conflict Resolution**:
- MCP tool returns CONFLICT error with current version
- AI agent must retry with fresh data
- No automatic retry (agent decides strategy)

---

## Data Integrity Constraints

### Database-Level Constraints

1. **Primary Keys**: Enforce uniqueness
   - user.id (UUID)
   - task.id (UUID)

2. **Foreign Keys**: Enforce referential integrity
   - task.user_id → user.id (CASCADE on delete)

3. **Unique Constraints**: Prevent duplicates
   - user.email (unique)

4. **Not Null Constraints**: Enforce required fields
   - All fields except: task.description, user.password_changed_at

5. **Check Constraints**: Enforce valid values
   - user.status IN ('active', 'disabled', 'deleted')
   - task.status IN ('pending', 'completed')

### Application-Level Validation

1. **Length Constraints**: Pydantic Field validation
2. **Format Validation**: EmailStr, UUID types
3. **Business Rules**: User isolation, ownership checks

---

## Summary of Changes

| Entity | Change Type | Field | Purpose |
|--------|-------------|-------|---------|
| Task | Add | version (int) | Optimistic concurrency control |
| User | None | - | Existing schema sufficient |

**Migration Impact**:
- **Breaking Change**: No (version field has default value)
- **Data Loss**: None (existing tasks get version=1)
- **Downtime Required**: No (online migration possible)
- **Rollback Safe**: Yes (down migration drops column)

**Testing Requirements**:
- Unit tests for version increment logic
- Integration tests for concurrent update scenarios
- Migration tests (up and down)
- Data integrity tests after migration

---

## Next Steps

1. Create Alembic migration for version field
2. Update Task model in src/domain/models.py
3. Update task_operations.py use cases to handle version
4. Add integration tests for optimistic locking
5. Document version field in API contracts
