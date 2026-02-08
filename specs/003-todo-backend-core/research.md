# Research: Backend Core & Data Layer

**Feature**: 003-todo-backend-core
**Date**: 2026-01-11
**Phase**: Phase 0 - Technology Research

## Overview

This document captures research findings and technology decisions for implementing a persistent FastAPI backend with Neon Serverless PostgreSQL, user-scoped data access, and production-ready patterns.

## Technology Decisions

### 1. FastAPI Async Patterns

**Decision**: Use async/await throughout the application with AsyncSession for database operations.

**Rationale**:
- FastAPI has native async support with excellent performance
- Async I/O prevents blocking during database operations
- Enables handling 100+ concurrent requests efficiently
- Required for Neon PostgreSQL async driver (asyncpg)

**Best Practices**:
- All route handlers use `async def`
- Database sessions use `AsyncSession` from SQLAlchemy
- Use `await` for all database queries
- Dependency injection for database sessions via `Depends()`
- Connection pooling configured in async engine

**Example Pattern**:
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from fastapi import Depends

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@app.get("/users/{user_id}/tasks")
async def list_tasks(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Task).where(Task.user_id == user_id))
    return result.scalars().all()
```

**Alternatives Considered**:
- Sync FastAPI with blocking database calls - Rejected: Poor performance under load, doesn't scale
- Threading with sync SQLAlchemy - Rejected: More complex, worse performance than async

---

### 2. SQLModel Async Sessions

**Decision**: Use SQLModel with SQLAlchemy async engine and AsyncSession.

**Rationale**:
- SQLModel combines Pydantic validation with SQLAlchemy ORM
- Type hints provide excellent IDE support and validation
- Async support via SQLAlchemy 2.0+ async engine
- Automatic Pydantic schema generation from models
- Prevents SQL injection via parameterized queries

**Best Practices**:
- Define models with `SQLModel` base class and `table=True`
- Use `Field()` for column definitions with validation
- Configure async engine with connection pooling
- Use `select()` statements with async execution
- Separate read models (Pydantic) from table models (SQLModel)

**Configuration**:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@host/db"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True for SQL logging in dev
    pool_size=10,  # Connection pool size
    max_overflow=20,  # Max connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
)

async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

**Alternatives Considered**:
- Raw asyncpg - Rejected: No ORM features, manual SQL, more boilerplate
- Tortoise ORM - Rejected: Less mature, smaller ecosystem than SQLAlchemy
- SQLAlchemy Core only - Rejected: More verbose, no model validation

---

### 3. Neon Serverless PostgreSQL Setup

**Decision**: Use Neon PostgreSQL with asyncpg driver and connection pooling.

**Rationale**:
- Serverless PostgreSQL with automatic scaling
- Built-in connection pooling (PgBouncer)
- Excellent async support via asyncpg
- Free tier suitable for development and testing
- Branch-based development (database branching)

**Connection String Format**:
```
postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
```

**Best Practices**:
- Always use SSL (`sslmode=require`)
- Store connection string in environment variable
- Use Neon's connection pooling endpoint for production
- Configure appropriate pool size (10-20 connections)
- Enable `pool_pre_ping` to handle connection drops
- Use database branching for testing (separate test database)

**Environment Configuration**:
```python
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db?sslmode=require
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20
```

**Alternatives Considered**:
- Self-hosted PostgreSQL - Rejected: More operational overhead, no serverless scaling
- Supabase - Rejected: Not specified in constitution, adds unnecessary features
- PlanetScale (MySQL) - Rejected: Constitution requires PostgreSQL

---

### 4. UUID v4 for Identifiers

**Decision**: Use UUID v4 for all primary keys (user_id, task_id).

**Rationale** (from clarification session):
- Security: Prevents enumeration attacks
- No collision risk in distributed systems
- Industry standard for user-facing APIs
- Native PostgreSQL UUID type support
- Works well with Neon's distributed architecture

**Implementation**:
```python
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
```

**Best Practices**:
- Use Python's `uuid.UUID` type for type hints
- Use `uuid4()` for generation (not uuid1 - leaks timestamp/MAC)
- Index foreign key columns (user_id) for query performance
- Validate UUID format in path parameters (FastAPI does this automatically)

**Alternatives Considered**:
- Integer auto-increment - Rejected: Allows enumeration, not distributed-safe
- ULID - Rejected: Not standard, adds dependency
- Composite keys - Rejected: More complex, unnecessary for this use case

---

### 5. RFC 7807 Problem Details for Errors

**Decision**: Use RFC 7807 Problem Details format for all error responses.

**Rationale** (from clarification session):
- Industry standard for HTTP API errors
- Well-documented and widely supported
- Extensible for additional context
- FastAPI has good support via exception handlers
- Consistent error format across all endpoints

**Schema**:
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000"
}
```

**Implementation**:
```python
from fastapi import HTTPException
from pydantic import BaseModel

class ProblemDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=ProblemDetail(
            type=f"https://api.example.com/errors/{exc.status_code}",
            title=exc.detail,
            status=exc.status_code,
            detail=exc.detail,
            instance=str(request.url)
        ).dict()
    )
```

**Alternatives Considered**:
- Simple `{"error": "message"}` - Rejected: Not standard, lacks structure
- Custom format - Rejected: Reinventing the wheel, less interoperable

---

### 6. Structured JSON Logging

**Decision**: Use structured JSON logging with context fields for all requests and errors.

**Rationale** (from clarification session):
- Machine-parseable for log aggregation tools
- Enables efficient searching and filtering
- Includes correlation IDs for request tracing
- Industry standard for production systems
- FastAPI middleware support

**Log Format**:
```json
{
  "timestamp": "2026-01-11T10:30:45.123Z",
  "level": "INFO",
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "method": "GET",
  "path": "/users/123e4567-e89b-12d3-a456-426614174000/tasks",
  "status_code": 200,
  "duration_ms": 45
}
```

**Implementation**:
```python
import logging
import json
from uuid import uuid4

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        return json.dumps(log_data)

# Middleware to add request_id
@app.middleware("http")
async def logging_middleware(request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms
        }
    )
    return response
```

**Alternatives Considered**:
- Plain text logs - Rejected: Hard to parse, not machine-readable
- Minimal logging - Rejected: Insufficient for debugging production issues

---

### 7. Offset/Limit Pagination with Metadata

**Decision**: Use offset/limit pagination with total count and navigation flags.

**Rationale** (from clarification session):
- Matches spec's stated approach
- Simple to implement with SQLAlchemy
- Provides total count for UI display
- Includes has_next/has_previous for navigation
- Sufficient for Phase II requirements

**Response Format**:
```json
{
  "items": [...],
  "total": 150,
  "offset": 0,
  "limit": 20,
  "has_next": true,
  "has_previous": false
}
```

**Implementation**:
```python
from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    offset: int
    limit: int
    has_next: bool
    has_previous: bool

async def paginate_tasks(
    session: AsyncSession,
    user_id: UUID,
    offset: int = 0,
    limit: int = 20
) -> PaginatedResponse[Task]:
    # Get total count
    count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
    total = await session.scalar(count_query)

    # Get paginated items
    query = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_next=offset + limit < total,
        has_previous=offset > 0
    )
```

**Alternatives Considered**:
- Cursor-based pagination - Rejected: More complex, overkill for Phase II
- Page number pagination - Rejected: Less flexible than offset/limit

---

### 8. User-Scoped Data Access Pattern

**Decision**: Enforce user isolation at the application layer by filtering all queries with user_id.

**Rationale**:
- Simpler than database row-level security
- Explicit and easy to audit
- Works well with trusted user_id (no JWT yet)
- Prevents timing attacks (same 404 for not found vs unauthorized)
- Ready for JWT middleware integration

**Pattern**:
```python
# Always filter by user_id
async def get_task(session: AsyncSession, user_id: UUID, task_id: UUID):
    query = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Critical: always filter by user_id
    )
    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if not task:
        # Same response whether task doesn't exist or belongs to another user
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

**Security Considerations**:
- Never expose whether a task exists for another user
- Always return 404 (not 403) to prevent information leakage
- Consistent response times to prevent timing attacks
- Index user_id column for query performance

**Alternatives Considered**:
- PostgreSQL row-level security - Rejected: More complex, harder to debug
- Separate databases per user - Rejected: Not scalable, operational nightmare

---

## Migration Strategy

**Decision**: Use Alembic for database migrations (optional for Phase II, can use SQLModel.metadata.create_all for simplicity).

**Rationale**:
- Alembic is the standard migration tool for SQLAlchemy
- Version-controlled schema changes
- Supports rollbacks and forward migrations
- Can be added later if needed

**Simplified Approach for Phase II**:
```python
# In main.py startup event
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

**Production Approach** (future):
- Use Alembic for versioned migrations
- Run migrations in CI/CD pipeline
- Never use create_all in production

---

## Testing Strategy

### Test Database Setup

**Decision**: Use separate Neon database branch for testing.

**Approach**:
```python
# conftest.py
@pytest.fixture(scope="session")
def test_database_url():
    return os.getenv("TEST_DATABASE_URL")

@pytest.fixture
async def test_session():
    engine = create_async_engine(test_database_url)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
```

### Test Types

1. **Unit Tests**: Models, services (mocked database)
2. **Integration Tests**: API endpoints with test database
3. **Contract Tests**: Validate OpenAPI specification compliance

---

## Key Tradeoffs

| Decision | Tradeoff | Justification |
|----------|----------|---------------|
| Async-only | More complex than sync | Required for performance and Neon async driver |
| UUID v4 | Larger than integers (16 bytes vs 4-8 bytes) | Security and distribution benefits outweigh storage cost |
| Application-layer isolation | Repeated user_id filters in queries | Simpler than row-level security, easier to audit |
| Offset/limit pagination | Not ideal for very large datasets | Sufficient for Phase II, can migrate to cursor later |
| SQLModel | Less mature than pure SQLAlchemy | Type safety and Pydantic integration worth it |

---

## Dependencies

**Core**:
- `fastapi` - Web framework
- `sqlmodel` - ORM with Pydantic integration
- `asyncpg` - Async PostgreSQL driver
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration
- `uvicorn` - ASGI server

**Testing**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client for testing
- `pytest-cov` - Coverage reporting

**Optional**:
- `alembic` - Database migrations (can add later)
- `python-multipart` - File upload support (not needed for Phase II)

---

## Next Steps

Phase 1 will produce:
1. `data-model.md` - Entity definitions with validation rules
2. `contracts/openapi.yaml` - Complete API specification
3. `contracts/errors.json` - RFC 7807 error schemas
4. `contracts/schemas/` - JSON Schema definitions
5. `quickstart.md` - Local development setup guide
