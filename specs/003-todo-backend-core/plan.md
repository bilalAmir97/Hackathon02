# Implementation Plan: Backend Core & Data Layer for Multi-User Todo Web Application

**Branch**: `003-todo-backend-core` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-todo-backend-core/spec.md`

**Note**: This plan implements Phase II backend requirements: persistent FastAPI backend with user-scoped data access, prepared for JWT authentication integration in future spec.

## Summary

Implement a persistent, stateless FastAPI backend for multi-user task management with Neon Serverless PostgreSQL. The backend provides RESTful CRUD endpoints for tasks with strict user-scoped data isolation enforced at the query level. All endpoints accept user_id as a path parameter (authentication deferred to future spec). The system uses UUID v4 identifiers, RFC 7807 error responses, offset/limit pagination with metadata, and structured JSON logging. Architecture prioritizes simplicity and correctness over premature optimization, suitable for hackathon timeline while maintaining production-ready patterns.

**Key Design Decisions**:
- User-scoped data access at application layer (not database row-level security)
- Stateless backend design ready for JWT middleware integration
- Two-state task model (pending/completed) sufficient for Phase II
- Async-only FastAPI + SQLModel for concurrent request handling
- Environment-based configuration (no hardcoded secrets)

## Technical Context

**Language/Version**: Python 3.13+ (constitution requirement)
**Primary Dependencies**: FastAPI (web framework), SQLModel (async ORM), asyncpg (PostgreSQL driver), pydantic (validation), python-dotenv (env config)
**Storage**: Neon Serverless PostgreSQL (async connection pool via SQLAlchemy async engine)
**Testing**: pytest, pytest-asyncio, httpx (async test client), pytest-cov (coverage)
**Target Platform**: Linux server (Vercel/Railway/Render for deployment)
**Project Type**: Web application (backend only - Phase II backend, frontend in separate spec)
**Performance Goals**:
- API response time: <1s at p95 under 10 req/s
- Concurrent requests: 100+ without errors
- List queries: <3s for 1000 tasks (with pagination)
**Constraints**:
- <200ms p95 for simple CRUD operations
- <500ms for error responses
- Async-only (no blocking I/O)
- Stateless (no in-memory session storage)
**Scale/Scope**:
- Phase II: Basic CRUD operations (5 endpoints)
- Support 100+ concurrent users
- Handle 1000+ tasks per user efficiently

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development Mandate
- Approved spec exists: `specs/003-todo-backend-core/spec.md`
- Following workflow: Constitution → Spec → Plan → Tasks → Implementation
- All requirements traced to spec functional requirements (FR-001 through FR-015)

### ✅ II. Agent Behavior Rules
- No manual coding - all work follows approved specifications
- All decisions documented in plan.md and will be recorded in PHRs
- Task IDs will be referenced in all code implementations
- MCP tools and CLI commands used as authoritative sources

### ✅ III. Phase Governance
- **Phase**: Phase II (Full-Stack Web Application)
- **Feature Level**: Basic Level ONLY (5 core CRUD operations)
- **No future-phase leakage**: No Intermediate/Advanced features (priorities, tags, recurring tasks, reminders)
- **Technology compliance**: FastAPI, SQLModel, Neon PostgreSQL (per constitution)
- **Deployment target**: Backend API (publicly accessible)

### ✅ IV. Test-Driven Development
- Test tasks will be defined before implementation tasks in tasks.md
- Test coverage target: 80% minimum for business logic
- Test types: Unit (models, services), Integration (API endpoints, database), Contract (API specifications)

### ✅ V. Clean Architecture
- **Domain Layer**: SQLModel models (User, Task) - no framework dependencies in entity definitions
- **Use Cases Layer**: Service functions for CRUD operations
- **Interface Adapters**: FastAPI route handlers, Pydantic schemas
- **Infrastructure**: Database session management, async engine configuration
- Dependencies point inward (services use models, routes use services)

### ✅ VI. Stateless Services
- No in-memory session storage (user_id passed in path parameters)
- All state persisted to Neon PostgreSQL
- Services can be killed/restarted without data loss
- Ready for horizontal scaling and JWT middleware integration

### ✅ VII. Contract-First Design
- API contracts will be defined in `specs/003-todo-backend-core/contracts/` before implementation
- OpenAPI specification for all REST endpoints
- JSON Schema for request/response payloads
- RFC 7807 Problem Details for error responses

### ✅ VIII. Observability & Monitoring
- Structured JSON logging with context fields (timestamp, level, request_id, user_id, method, path, status_code, duration_ms)
- Health check endpoint: `/health` (Phase II requirement)
- Request/response logging for all API calls
- Error logging with stack traces (server-side only, not exposed to clients)

### ✅ IX. Security & Compliance
- User isolation enforced at query level (all queries filtered by user_id)
- No hardcoded secrets (environment variables only)
- SQL injection prevention (SQLModel parameterized queries)
- Input validation (Pydantic models)
- Error message safety (RFC 7807 without internal details)
- **Note**: JWT authentication deferred to future spec (user_id trusted in this spec)

### ✅ X. Feature Progression Governance
- **Feature Level**: Basic Level ONLY
  1. ✅ Add Task (Create new todo items)
  2. ✅ Delete Task (Remove tasks from list)
  3. ✅ Update Task (Modify existing task details)
  4. ✅ View Task List (Display all tasks)
  5. ✅ Mark as Complete (Toggle task completion status)
- **No Intermediate/Advanced features**: No priorities, tags, search, recurring tasks, or reminders

### ✅ XI. AGENTS.md Integration
- AGENTS.md exists in project root with SDD workflow
- CLAUDE.md references AGENTS.md
- All agent interactions follow spec-driven workflow
- PHRs will be created for all user interactions

### ✅ XII. Deployment & Submission Standards
- GitHub repository with source code
- Backend API publicly accessible
- Neon Serverless PostgreSQL database
- /specs folder with all specifications
- README.md with setup instructions

**Constitution Compliance**: ✅ PASS - All gates satisfied, no violations requiring justification

## Project Structure

### Documentation (this feature)

```text
specs/003-todo-backend-core/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (local setup guide)
├── contracts/           # Phase 1 output (API specifications)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   ├── errors.json      # RFC 7807 error schemas
│   └── schemas/         # JSON Schema definitions
│       ├── task.json
│       ├── user.json
│       └── pagination.json
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
Phase-II/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application factory
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # Async engine, session dependency
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   └── models.py        # SQLModel entities (User, Task, TaskStatus)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── task.py          # Pydantic request/response schemas
│   │   │   ├── error.py         # RFC 7807 error schemas
│   │   │   └── pagination.py    # Pagination metadata schemas
│   │   ├── use_cases/
│   │   │   ├── __init__.py
│   │   │   └── task_operations.py  # Business logic for task operations
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py          # Dependency injection (DB session)
│   │   │   ├── health.py        # Health check endpoint
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       └── tasks.py     # Task CRUD endpoints
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py       # Structured JSON logging middleware
│   │   │   └── error_handler.py # RFC 7807 exception handlers
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py        # Structured logging configuration
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py          # Pytest fixtures (test DB, client)
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py   # Model validation tests
│   │   │   └── test_use_cases.py # Use case logic tests
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_database.py # Database operations tests
│   │   │   └── test_api_tasks.py # API endpoint tests
│   │   └── contract/
│   │       ├── __init__.py
│   │       └── test_api_contract.py # OpenAPI contract tests
│   ├── .env.example             # Environment variable template
│   ├── pyproject.toml           # UV project configuration
│   ├── README.md                # Backend setup instructions
│   └── alembic/                 # Database migrations (if using Alembic)
│       ├── versions/
│       └── env.py
└── frontend/                    # Frontend (separate spec - not in this plan)
    └── (Next.js application)
```

**Structure Decision**: Web application structure (Option 2) selected because this is Phase II backend implementation. The `Phase-II/backend/` directory contains the FastAPI application with clean architecture layers:
- **Domain Layer**: `domain/` (SQLModel entities: User, Task, TaskStatus)
- **Use Cases Layer**: `use_cases/` (business logic for task operations)
- **Interface Adapters**: `api/` (FastAPI routes), `schemas/` (Pydantic DTOs)
- **Infrastructure**: `database.py` (async engine), `middleware/` (logging, errors)

Frontend will be implemented in a separate specification and will reside in `Phase-II/frontend/`.

## Complexity Tracking

> **No violations requiring justification** - All constitution principles satisfied without exceptions.

---

## Implementation Phases Summary

### Phase 0: Research (Completed)

**Output**: `research.md`

**Key Decisions**:
1. FastAPI async patterns with AsyncSession
2. SQLModel with SQLAlchemy async engine
3. Neon PostgreSQL with asyncpg driver
4. UUID v4 for all identifiers
5. RFC 7807 Problem Details for errors
6. Structured JSON logging
7. Offset/limit pagination with metadata
8. User-scoped data access at application layer

**All NEEDS CLARIFICATION items resolved** - No unknowns remaining.

---

### Phase 1: Design & Contracts (Completed)

**Outputs**:
- `data-model.md` - Entity definitions with validation rules
- `contracts/openapi.yaml` - Complete OpenAPI 3.0 specification
- `contracts/errors.json` - RFC 7807 error schemas
- `contracts/schemas/user.json` - User JSON Schema
- `contracts/schemas/task.json` - Task JSON Schema
- `contracts/schemas/pagination.json` - Pagination JSON Schema
- `quickstart.md` - Local development setup guide

**Key Artifacts**:
- 2 entities (User, Task) with UUID v4 identifiers
- 1 relationship (User → Task, one-to-many)
- 6 REST endpoints (health check + 5 task CRUD operations)
- 5 database indexes (1 unique, 4 performance)
- Complete API contract with request/response schemas

---

### Phase 2: Task Decomposition (Next Step)

**Command**: `/sp.tasks`

**Expected Output**: `tasks.md` with atomic, testable implementation tasks

**Task Organization**:
- Grouped by user story (US1: Create/Retrieve, US2: Update/Delete, US3: List/Filter)
- Test tasks before implementation tasks (TDD)
- Parallelizable tasks marked with [P]
- Dependencies clearly indicated

---

## Architecture Overview

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                   │
│  Routes, Middleware, Exception Handlers, Dependencies    │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Interface Adapters (Pydantic)               │
│    Request/Response Schemas, DTOs, Validation            │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Use Cases (Services)                        │
│    Business Logic, CRUD Operations, User Isolation       │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Domain (SQLModel)                           │
│    Entities, Validation Rules, State Transitions         │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│         Infrastructure (Database, Logging)               │
│    Async Engine, Session Management, JSON Logging        │
└─────────────────────────────────────────────────────────┘
```

### Request Flow

```
1. HTTP Request → FastAPI Route Handler
2. Route Handler → Validate with Pydantic Schema
3. Route Handler → Get Database Session (Dependency Injection)
4. Route Handler → Call Service Function
5. Service Function → Query Database (SQLModel + AsyncSession)
6. Service Function → Enforce User Isolation (filter by user_id)
7. Service Function → Return Domain Entity
8. Route Handler → Convert to Response Schema
9. Route Handler → Return JSON Response
10. Middleware → Log Request/Response (Structured JSON)
```

### Error Handling Flow

```
1. Exception Raised → FastAPI Exception Handler
2. Exception Handler → Convert to RFC 7807 ProblemDetail
3. Exception Handler → Log Error (Structured JSON)
4. Exception Handler → Return JSON Response (appropriate status code)
5. Client Receives → Consistent error format
```

---

## Key Design Patterns

### Dependency Injection

**Pattern**: FastAPI's `Depends()` for database sessions

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@app.get("/users/{user_id}/tasks")
async def list_tasks(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    # Session automatically managed (created and closed)
    pass
```

**Benefits**:
- Automatic session lifecycle management
- Easy to mock for testing
- Clean separation of concerns

---

### Repository Pattern (Simplified)

**Pattern**: Use case functions encapsulate database operations

```python
# use_cases/task_operations.py
async def get_user_tasks(
    session: AsyncSession,
    user_id: UUID,
    status: Optional[TaskStatus] = None,
    offset: int = 0,
    limit: int = 20
) -> PaginatedResponse[Task]:
    # All database logic encapsulated
    # User isolation enforced here
    pass
```

**Benefits**:
- Business logic separated from route handlers
- Reusable across multiple endpoints
- Easy to test in isolation

---

### Middleware Pattern

**Pattern**: Request/response interceptors for cross-cutting concerns

```python
@app.middleware("http")
async def logging_middleware(request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id

    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    logger.info("Request completed", extra={
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms
    })

    return response
```

**Benefits**:
- Centralized logging for all requests
- Request ID correlation
- Performance monitoring

---

## Security Considerations

### User Isolation Enforcement

**Critical Pattern**: Always filter by user_id

```python
# ✅ CORRECT: Filter by user_id
query = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id  # Critical security check
)

# ❌ INCORRECT: Missing user_id filter
query = select(Task).where(Task.id == task_id)
```

**Timing Attack Prevention**:
- Same 404 response for "not found" and "unauthorized"
- Consistent query patterns (always filter by user_id first)
- No information leakage about task existence

---

### Input Validation

**Layers of Defense**:
1. **Pydantic Schemas**: Validate request data before processing
2. **SQLModel**: Validate data before database operations
3. **Database Constraints**: Final safety net (foreign keys, check constraints)

---

### SQL Injection Prevention

**Protection**: SQLModel uses parameterized queries exclusively

```python
# ✅ SAFE: Parameterized query via SQLModel
query = select(Task).where(Task.user_id == user_id)

# ❌ UNSAFE: String interpolation (never do this)
query = f"SELECT * FROM task WHERE user_id = '{user_id}'"
```

---

### Task Deletion Strategy

**Decision**: Hard delete (permanent removal)

**Rationale**:
- Spec assumption #5 states: "Deleted tasks are permanently removed from the database (no trash/recovery feature in v1)"
- Simpler implementation for Phase II
- No additional storage overhead
- Aligns with Basic Level feature requirements

**Implementation**:
```python
# use_cases/task_operations.py
async def delete_task(session: AsyncSession, user_id: UUID, task_id: UUID):
    # Verify ownership
    task = await session.get(Task, task_id)
    if not task or task.user_id != user_id:
        raise TaskNotFoundError()

    # Hard delete - permanent removal
    await session.delete(task)
    await session.commit()
```

**Future Consideration**: Soft delete (archived status) can be added in Phase V if needed for audit trails or recovery features.

---

## Performance Optimization

### Database Indexing

**Strategy**: Index columns used in WHERE clauses and ORDER BY

```sql
-- User-scoped queries (most common)
CREATE INDEX idx_task_user_id ON task(user_id);

-- Paginated list queries (user_id + created_at)
CREATE INDEX idx_task_user_created ON task(user_id, created_at DESC);

-- Filtered list queries (user_id + status)
CREATE INDEX idx_task_user_status ON task(user_id, status);
```

**Query Patterns Covered**:
- List all tasks for user (uses idx_task_user_created)
- List tasks by status (uses idx_task_user_status)
- Get single task (uses primary key + user_id filter)

---

### Connection Pooling

**Configuration**:
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # Base pool size
    max_overflow=20,     # Additional connections under load
    pool_pre_ping=True,  # Verify connections before use
)
```

**Benefits**:
- Reuse database connections (avoid connection overhead)
- Handle concurrent requests efficiently
- Automatic connection health checks

---

### Pagination

**Strategy**: Offset/limit with total count

```python
# Count query (uses covering index)
count_query = select(func.count()).select_from(Task).where(Task.user_id == user_id)
total = await session.scalar(count_query)

# Data query (uses composite index)
query = select(Task).where(Task.user_id == user_id).offset(offset).limit(limit)
items = await session.execute(query)
```

**Performance Notes**:
- Count query uses index (no table scan)
- Limit maximum page size to 100 items
- Offset/limit sufficient for Phase II (can migrate to cursor-based later)

---

## Testing Strategy

### Test Pyramid

```
        ┌─────────────┐
        │   Contract  │  (API specification compliance)
        │    Tests    │
        ├─────────────┤
        │ Integration │  (API endpoints + database)
        │    Tests    │
        ├─────────────┤
        │    Unit     │  (Models, services, validation)
        │    Tests    │
        └─────────────┘
```

### Test Coverage Targets

- **Unit Tests**: 80%+ coverage for business logic
- **Integration Tests**: All API endpoints
- **Contract Tests**: All OpenAPI operations

### Test Database Strategy

**Approach**: Separate Neon database branch for testing

**Benefits**:
- Isolated from development database
- Fast setup/teardown
- No impact on development data

---

## Deployment Readiness

### Environment Variables

**Required**:
- `DATABASE_URL` - Neon PostgreSQL connection string
- `DATABASE_POOL_SIZE` - Connection pool size (default: 10)
- `DATABASE_MAX_OVERFLOW` - Max overflow connections (default: 20)
- `APP_ENV` - Environment (development/production)
- `LOG_LEVEL` - Logging level (INFO/DEBUG/ERROR)

### Health Check

**Endpoint**: `GET /health`

**Purpose**: Load balancer health checks, monitoring

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-11T10:30:45.123Z"
}
```

---

## Future Integration Points

### JWT Authentication (Future Spec)

**Integration Points**:
1. **Middleware**: Add JWT verification middleware before route handlers
2. **User Extraction**: Extract user_id from JWT token
3. **Path Validation**: Verify JWT user_id matches path user_id parameter
4. **Error Handling**: Return 401 for invalid/missing tokens

**Current Design Supports**:
- Stateless backend (no session storage)
- User_id in path parameters (ready for JWT validation)
- User isolation at application layer (JWT will provide trusted user_id)

---

## Monitoring & Observability

### Structured Logging

**Format**: JSON with context fields

**Fields**:
- `timestamp` - ISO 8601 UTC timestamp
- `level` - Log level (INFO, ERROR, etc.)
- `request_id` - Correlation ID for request tracing
- `user_id` - User performing action (if available)
- `method` - HTTP method
- `path` - Request path
- `status_code` - Response status
- `duration_ms` - Request duration

**Benefits**:
- Machine-parseable for log aggregation
- Efficient searching and filtering
- Request correlation via request_id

---

## Summary

**Implementation Plan Complete**: ✅

**Phase 0 (Research)**: Complete - All technology decisions documented
**Phase 1 (Design)**: Complete - Data model, contracts, and quickstart guide created
**Phase 2 (Tasks)**: Ready - Run `/sp.tasks` to generate implementation tasks

**Artifacts Generated**:
1. `plan.md` - This implementation plan
2. `research.md` - Technology research and decisions
3. `data-model.md` - Entity definitions and validation rules
4. `contracts/openapi.yaml` - Complete API specification
5. `contracts/errors.json` - RFC 7807 error schemas
6. `contracts/schemas/*.json` - JSON Schema definitions
7. `quickstart.md` - Local development setup guide

**Ready for Implementation**: All design decisions made, contracts defined, no unknowns remaining.

**Next Command**: `/sp.tasks` to generate atomic, testable implementation tasks from this plan.
