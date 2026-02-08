# Data Model: Backend Core & Data Layer

**Feature**: 003-todo-backend-core
**Date**: 2026-01-11
**Phase**: Phase 1 - Data Model Design

## Overview

This document defines the database schema and entity models for the multi-user todo backend. All entities use UUID v4 identifiers and enforce user-scoped data access at the application layer.

## Entity Definitions

### User Entity

**Purpose**: Represents a person using the todo application.

**Table Name**: `user`

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique user identifier (UUID v4) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address (for future authentication) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id` (automatic)
- Unique index on `email`

**Validation Rules**:
- `email`: Must be valid email format (RFC 5322)
- `email`: Maximum 255 characters
- `id`: Must be valid UUID v4 format

**SQLModel Definition**:
```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from pydantic import EmailStr

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Notes**:
- User creation/management is minimal in this spec (assumes users exist)
- Email is indexed for future authentication lookups
- Timestamps use UTC timezone
- User entity prepared for JWT authentication integration in future spec

---

### Task Entity

**Purpose**: Represents a single todo item owned by a user.

**Table Name**: `task`

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique task identifier (UUID v4) |
| user_id | UUID | FOREIGN KEY (user.id), NOT NULL, INDEX | Owner reference |
| title | VARCHAR(200) | NOT NULL | Task title (max 200 chars) |
| description | TEXT | NULLABLE | Task description (max 2000 chars) |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Task status: 'pending' or 'completed' |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- Primary key index on `id` (automatic)
- Index on `user_id` (for user-scoped queries)
- Composite index on `(user_id, created_at)` (for list queries with ordering)
- Composite index on `(user_id, status)` (for filtered list queries)

**Foreign Keys**:
- `user_id` → `user.id` (ON DELETE CASCADE)

**Validation Rules**:
- `id`: Must be valid UUID v4 format
- `user_id`: Must be valid UUID v4 format and reference existing user
- `title`: Required, 1-200 characters, non-empty after trimming
- `description`: Optional, max 2000 characters
- `status`: Must be one of: 'pending', 'completed'

**SQLModel Definition**:
```python
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True, nullable=False)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Notes**:
- Tasks are permanently deleted (no soft deletes in Phase II)
- Status is enum-constrained at application and database level
- Composite indexes optimize common query patterns (list by user, filter by status)
- Foreign key cascade ensures orphaned tasks are deleted when user is deleted

---

## Relationships

### User → Task (One-to-Many)

**Relationship**: One user can have many tasks; each task belongs to exactly one user.

**Cardinality**: 1:N

**Implementation**:
- Foreign key: `task.user_id` → `user.id`
- Cascade delete: When user is deleted, all their tasks are deleted
- Enforced at database level (foreign key constraint)
- Enforced at application level (all queries filter by user_id)

**Query Pattern**:
```python
# Get all tasks for a user
query = select(Task).where(Task.user_id == user_id)

# Get specific task for a user (ownership check)
query = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # Critical: prevents cross-user access
)
```

---

## State Transitions

### Task Status Lifecycle

```
┌─────────┐
│ pending │ ◄──────┐
└────┬────┘        │
     │             │
     │ complete    │ uncomplete
     │             │
     ▼             │
┌───────────┐      │
│ completed │──────┘
└───────────┘
```

**Valid Transitions**:
1. `pending` → `completed` (mark task as done)
2. `completed` → `pending` (reopen task)

**Invalid Transitions**: None (only two states, both transitions allowed)

**Business Rules**:
- Tasks default to `pending` on creation
- Status can be toggled between `pending` and `completed` unlimited times
- No intermediate states (e.g., "in-progress") in Phase II
- Completed tasks remain in the database (no auto-archival)

---

## Validation Rules Summary

### User Validation

**Field-Level**:
- `email`: Valid email format, unique, max 255 chars
- `id`: Valid UUID v4

**Entity-Level**:
- Email must not already exist in database (uniqueness constraint)

### Task Validation

**Field-Level**:
- `title`: Required, 1-200 chars, non-empty after trim
- `description`: Optional, max 2000 chars
- `status`: Must be 'pending' or 'completed'
- `user_id`: Must reference existing user
- `id`: Valid UUID v4

**Entity-Level**:
- Task must belong to a valid user (foreign key constraint)
- Title cannot be only whitespace

**Cross-Entity**:
- User must exist before creating tasks (foreign key enforced)
- Deleting user cascades to delete all their tasks

---

## Database Schema (SQL DDL)

```sql
-- User table
CREATE TABLE "user" (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_email ON "user"(email);

-- Task table
CREATE TABLE task (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_status CHECK (status IN ('pending', 'completed'))
);

CREATE INDEX idx_task_user_id ON task(user_id);
CREATE INDEX idx_task_user_created ON task(user_id, created_at DESC);
CREATE INDEX idx_task_user_status ON task(user_id, status);
```

---

## Data Access Patterns

### Common Queries

**1. List all tasks for a user (paginated, ordered by creation date)**:
```python
query = (
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
    .offset(offset)
    .limit(limit)
)
```
**Index Used**: `idx_task_user_created`

**2. List tasks filtered by status**:
```python
query = (
    select(Task)
    .where(Task.user_id == user_id, Task.status == status)
    .order_by(Task.created_at.desc())
    .offset(offset)
    .limit(limit)
)
```
**Index Used**: `idx_task_user_status`

**3. Get single task by ID (with ownership check)**:
```python
query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
```
**Index Used**: Primary key on `id`, then filter by `user_id`

**4. Count total tasks for a user**:
```python
query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
```
**Index Used**: `idx_task_user_id`

**5. Update task (with ownership check)**:
```python
query = (
    update(Task)
    .where(Task.id == task_id, Task.user_id == user_id)
    .values(title=new_title, updated_at=datetime.utcnow())
)
```

**6. Delete task (with ownership check)**:
```python
query = delete(Task).where(Task.id == task_id, Task.user_id == user_id)
```

---

## Performance Considerations

### Indexing Strategy

**Primary Indexes** (automatic):
- `user.id` (primary key)
- `task.id` (primary key)

**Secondary Indexes** (explicit):
- `user.email` (unique) - For authentication lookups
- `task.user_id` - For user-scoped queries
- `task(user_id, created_at DESC)` - For paginated list queries
- `task(user_id, status)` - For filtered list queries

**Index Rationale**:
- All queries filter by `user_id` first (user isolation)
- List queries order by `created_at` (composite index covers both)
- Status filtering is common (composite index with user_id)

### Query Optimization

**Pagination**:
- Use offset/limit with indexed columns
- Count query uses covering index (no table scan)
- Limit maximum page size to 100 items

**Bulk Operations**:
- Not required for Phase II (single-item CRUD only)
- Can be added in future if needed

---

## Migration Notes

### Initial Schema Creation

**Development** (simple approach):
```python
# In main.py startup event
async with engine.begin() as conn:
    await conn.run_sync(SQLModel.metadata.create_all)
```

**Production** (recommended):
- Use Alembic for versioned migrations
- Create initial migration: `alembic revision --autogenerate -m "Initial schema"`
- Apply migration: `alembic upgrade head`

### Future Schema Changes

**Adding columns**:
- Use Alembic migrations with default values
- Ensure backward compatibility

**Changing constraints**:
- Test migration on copy of production data
- Plan rollback strategy

---

## Data Integrity

### Constraints

**Primary Keys**:
- Enforce uniqueness at database level
- UUID v4 prevents collisions

**Foreign Keys**:
- Enforce referential integrity
- Cascade deletes prevent orphaned records

**Check Constraints**:
- Status enum validation at database level
- Prevents invalid status values

**Unique Constraints**:
- Email uniqueness prevents duplicate accounts

### Application-Level Enforcement

**User Isolation**:
- All queries include `user_id` filter
- Prevents cross-user data access
- Same 404 response for not found vs unauthorized

**Validation**:
- Pydantic models validate input before database
- SQLModel validates on ORM operations
- Database constraints as final safety net

---

## Testing Considerations

### Test Data Setup

**Fixtures**:
```python
@pytest.fixture
async def test_user(session):
    user = User(email="test@example.com")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture
async def test_task(session, test_user):
    task = Task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description"
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
```

### Test Scenarios

**Model Validation**:
- Valid data creates successfully
- Invalid email format rejected
- Title length constraints enforced
- Status enum validation

**Relationships**:
- Task requires valid user_id
- Deleting user cascades to tasks
- Cannot create task with non-existent user_id

**User Isolation**:
- User A cannot access User B's tasks
- Queries filtered by user_id return correct subset
- Cross-user access attempts return 404

---

## Summary

**Entities**: 2 (User, Task)
**Relationships**: 1 (User → Task, one-to-many)
**Indexes**: 5 (1 unique, 4 performance)
**Constraints**: 4 (2 foreign keys, 1 unique, 1 check)
**State Transitions**: 2 (pending ↔ completed)

**Key Design Decisions**:
- UUID v4 for all identifiers (security, distribution)
- User-scoped data access at application layer (simplicity)
- Two-state task model (sufficient for Phase II)
- Composite indexes for common query patterns (performance)
- Cascade deletes for referential integrity (data consistency)
