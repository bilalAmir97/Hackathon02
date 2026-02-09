# Implementation Plan: MCP Todo Server & Tooling Layer

**Branch**: `001-phase-iii-mcp-server` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-iii-mcp-server/spec.md`

## Summary

Build a stateless MCP (Model Context Protocol) server using the Official MCP SDK that exposes task operations as reliable, database-backed tools for AI agents. The server will integrate with the existing Phase-III FastAPI backend, leveraging the established SQLModel + Neon PostgreSQL architecture while maintaining complete statelessness. All tools will enforce strict user isolation, validate inputs, and return structured JSON responses compatible with OpenAI Agents SDK.

**Key Approach**: Extend existing FastAPI backend with MCP server capabilities, reusing domain models, use cases, and database infrastructure while adding MCP-specific tool definitions and request-scoped session management.

## Technical Context

**Language/Version**: Python 3.13+ (existing backend)
**Primary Dependencies**:
- Official MCP SDK (Python) - for MCP protocol implementation
- FastAPI 0.128.0+ - existing API framework
- SQLModel 0.0.31+ - existing ORM
- Pydantic 2.12.5+ - existing validation
- PyJWT 2.9.0+ - existing authentication
- asyncpg 0.31.0+ - existing async PostgreSQL driver

**Storage**: Neon Serverless PostgreSQL (existing database with User and Task tables)
**Testing**: pytest 9.0.2+, pytest-asyncio 1.3.0+ (existing test infrastructure)
**Target Platform**: Linux server (FastAPI deployment)
**Project Type**: Web application (backend extension)

**Performance Goals**:
- Tool execution: <500ms for 95% of add_task requests
- Tool execution: <300ms for 95% of list_tasks requests
- Concurrent agents: Support 100+ simultaneous tool invocations
- Database connection pooling: Reuse existing pool (10 connections, 20 max overflow)

**Constraints**:
- Stateless architecture: No in-memory state between requests
- Request-scoped sessions: Database sessions created and closed per tool invocation
- User isolation: All operations filtered by user_id from authentication context
- Deterministic responses: Consistent JSON structure for success and error cases
- OpenAI Agents SDK compatibility: Tool schemas must follow MCP protocol specifications

**Scale/Scope**:
- 5 MCP tools (add_task, list_tasks, update_task, complete_task, delete_task)
- Existing database schema (User and Task tables with UUID identifiers)
- Integration with existing authentication middleware (JWT token verification)
- Reuse of existing use cases and domain models

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Governance ✅ PASS
- **Phase III Scope**: AI-Powered Todo Chatbot with MCP server
- **Feature Level**: Basic Level (5 core CRUD operations via natural language)
- **Technology Compliance**: Python FastAPI, SQLModel, Neon PostgreSQL, Official MCP SDK
- **No Future-Phase Leakage**: No Intermediate/Advanced features (priorities, tags, recurring tasks)

### Stateless Services ✅ PASS
- **Stateless Design**: MCP server holds no session or runtime memory
- **State Management**: All state persisted to Neon PostgreSQL
- **Request Context**: user_id extracted from authentication headers per request
- **Database Sessions**: Request-scoped sessions (created and closed per tool invocation)
- **Horizontal Scalability**: Stateless architecture enables multiple server instances

### Clean Architecture ✅ PASS
- **Domain Layer**: Reuse existing models.py (User, Task entities)
- **Use Cases Layer**: Reuse existing task_operations.py (business logic)
- **Interface Adapters**: New MCP tool definitions wrapping existing use cases
- **Infrastructure**: Reuse existing database.py, config.py, dependencies.py

### Contract-First Design ✅ PASS
- **MCP Tool Contracts**: Will be defined in `contracts/mcp-tools.json`
- **Tool Schemas**: Input/output schemas for all 5 tools
- **Error Schemas**: Standardized error format with code, message, details
- **Integration Contract**: OpenAI Agents SDK compatibility requirements

### Test-Driven Development ✅ PASS
- **Test Strategy**: Unit tests for tool validation, integration tests for database operations
- **Existing Test Infrastructure**: Reuse pytest setup, async test utilities
- **Contract Tests**: Validate tool schemas against MCP protocol specifications
- **Coverage Target**: 80%+ for new MCP tool code (if tests are implemented per constitution Section IV)
- **Note**: Test tasks are optional per feature specification but recommended for production readiness

### Security & Compliance ✅ PASS
- **Authentication**: JWT token verification via existing middleware
- **User Isolation**: user_id extracted from token, enforced on all operations
- **Input Validation**: Pydantic schemas for all tool inputs
- **Error Handling**: No internal details exposed in error responses
- **OWASP Compliance**: Reuse existing security patterns (parameterized queries, XSS prevention)

### Observability & Monitoring ✅ PASS
- **Structured Logging**: Extend existing logging middleware for MCP tool events
- **Metrics**: Tool execution time, success/failure rates
- **Health Checks**: Extend existing /api/health endpoint
- **Error Tracking**: Structured error logging with correlation IDs

**Constitution Compliance**: ✅ ALL GATES PASS - Ready for Phase 0 research

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-iii-mcp-server/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── mcp-tools.json   # MCP tool schemas
│   └── error-codes.json # Error code definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (Phase-III directory)

```text
Phase-III/
├── backend/
│   ├── src/
│   │   ├── mcp/                    # NEW: MCP server implementation
│   │   │   ├── __init__.py
│   │   │   ├── server.py           # MCP server initialization
│   │   │   ├── tools/              # MCP tool definitions
│   │   │   │   ├── __init__.py
│   │   │   │   ├── add_task.py     # add_task tool
│   │   │   │   ├── list_tasks.py   # list_tasks tool
│   │   │   │   ├── update_task.py  # update_task tool
│   │   │   │   ├── complete_task.py # complete_task tool
│   │   │   │   └── delete_task.py  # delete_task tool
│   │   │   ├── schemas/            # MCP-specific schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── tool_inputs.py  # Tool input schemas
│   │   │   │   └── tool_outputs.py # Tool output schemas
│   │   │   └── middleware/         # MCP-specific middleware
│   │   │       ├── __init__.py
│   │   │       ├── auth_context.py # Extract user_id from headers
│   │   │       └── error_handler.py # MCP error formatting
│   │   ├── domain/                 # EXISTING: Reuse models
│   │   │   └── models.py           # User, Task entities (add version field)
│   │   ├── use_cases/              # EXISTING: Reuse business logic
│   │   │   └── task_operations.py  # CRUD operations
│   │   ├── database.py             # EXISTING: Database connection
│   │   ├── config.py               # EXISTING: Configuration (add MCP settings)
│   │   └── main.py                 # EXISTING: FastAPI app (add MCP routes)
│   └── tests/
│       ├── mcp/                    # NEW: MCP-specific tests
│       │   ├── test_tools.py       # Tool execution tests
│       │   ├── test_auth_context.py # Auth extraction tests
│       │   └── test_error_handling.py # Error format tests
│       ├── contract/               # EXISTING: Add MCP contract tests
│       ├── integration/            # EXISTING: Add MCP integration tests
│       └── unit/                   # EXISTING: Add MCP unit tests
│
└── frontend/                       # EXISTING: No changes for Spec-1
    └── (Next.js app - unchanged)
```

**Structure Decision**: Extend existing Phase-III backend with new `src/mcp/` module. This approach:
- Reuses existing domain models, use cases, and database infrastructure
- Maintains clean separation between REST API and MCP server concerns
- Enables gradual migration and testing without disrupting existing functionality
- Follows Clean Architecture principles (MCP tools as new interface adapters)

## Complexity Tracking

> **No Constitution violations requiring justification**

All complexity is justified by Phase III requirements:
- MCP server integration: Required for AI chatbot functionality
- Stateless architecture: Required by constitution for Phase III+
- Tool schema definitions: Required by MCP protocol specifications
- User isolation enforcement: Required by security principles

---

## Phase 0: Outline & Research

### Research Tasks

#### 1. Official MCP SDK Integration Patterns

**Research Question**: How to integrate Official MCP SDK with existing FastAPI application?

**Investigation Areas**:
- MCP SDK installation and initialization
- FastAPI route integration vs standalone server
- Request/response lifecycle in MCP protocol
- Tool registration and discovery mechanisms
- Error handling patterns in MCP SDK

**Expected Findings**:
- MCP SDK Python package name and installation method
- Code examples for FastAPI integration
- Tool schema format and validation requirements
- Best practices for stateless tool execution

#### 2. Tool Schema Design & Validation

**Research Question**: What schema format does MCP protocol require for tool definitions?

**Investigation Areas**:
- MCP tool schema specification (JSON Schema, Pydantic, etc.)
- Input parameter validation patterns
- Output response structure requirements
- Error response format in MCP protocol
- OpenAI Agents SDK compatibility requirements

**Expected Findings**:
- Tool schema template and examples
- Required vs optional fields in tool definitions
- Validation error handling patterns
- Integration with Pydantic for type safety

#### 3. Stateless Execution & Database Session Management

**Research Question**: How to manage database sessions in stateless MCP tool execution?

**Investigation Areas**:
- Request-scoped session patterns in async Python
- SQLAlchemy async session lifecycle
- Connection pooling best practices for stateless services
- Transaction management in tool execution
- Error handling and session cleanup

**Expected Findings**:
- Session factory pattern for MCP tools
- Context manager usage for automatic cleanup
- Connection pool configuration for concurrent tools
- Rollback strategies for failed operations

#### 4. Authentication Context Extraction

**Research Question**: How to extract user_id from authentication headers in MCP tool context?

**Investigation Areas**:
- MCP protocol request context structure
- Header access patterns in MCP SDK
- JWT token verification in tool middleware
- User context propagation to use cases
- Security best practices for stateless auth

**Expected Findings**:
- MCP request context API
- Header extraction patterns
- Integration with existing JWT middleware
- User context dependency injection

#### 5. Error Handling & Response Formatting

**Research Question**: What error format ensures MCP protocol compliance and AI agent compatibility?

**Investigation Areas**:
- MCP protocol error response structure
- Error code taxonomy for tool operations
- Machine-readable vs human-readable error messages
- Error details field usage patterns
- OpenAI Agents SDK error handling expectations

**Expected Findings**:
- Standard error response template
- Error code naming conventions
- Error details structure for debugging
- Integration with existing error middleware

### Research Output

All findings will be documented in `research.md` with:
- **Decision**: Chosen approach for each research area
- **Rationale**: Why this approach was selected
- **Alternatives Considered**: Other options evaluated and rejected
- **Implementation Notes**: Key details for Phase 1 design

---

## Phase 1: Design & Contracts

### Data Model Extensions

**File**: `data-model.md`

#### Task Entity Extension

Add version field for optimistic concurrency control (from spec clarifications):

```python
class Task(SQLModel, table=True):
    # ... existing fields ...

    version: int = Field(
        default=1,
        nullable=False,
        description="Version number for optimistic concurrency control"
    )
```

**Migration Required**: Alembic migration to add `version` column with default value 1.

#### No New Entities Required

Existing User and Task entities are sufficient for MCP server functionality. All clarified requirements (UUID identifiers, timestamps, status enums) are already implemented in Phase-II models.

### MCP Tool Contracts

**File**: `contracts/mcp-tools.json`

#### Tool 1: add_task

**Purpose**: Create new task with title and description

**Input Schema**:
```json
{
  "name": "add_task",
  "description": "Create a new todo task for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "Task title (1-200 characters)"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "Optional task description (max 2000 characters)"
      }
    },
    "required": ["title"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "id": { "type": "string", "format": "uuid" },
    "user_id": { "type": "string", "format": "uuid" },
    "title": { "type": "string" },
    "description": { "type": "string", "nullable": true },
    "status": { "type": "string", "enum": ["pending", "completed"] },
    "version": { "type": "integer" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  },
  "required": ["id", "user_id", "title", "status", "version", "created_at", "updated_at"]
}
```

**Authentication**: user_id extracted from Authorization header (JWT token)

#### Tool 2: list_tasks

**Purpose**: Retrieve user's tasks with optional status filtering

**Input Schema**:
```json
{
  "name": "list_tasks",
  "description": "List tasks for the authenticated user with optional status filter",
  "inputSchema": {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter tasks by status"
      }
    }
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "format": "uuid" },
          "user_id": { "type": "string", "format": "uuid" },
          "title": { "type": "string" },
          "description": { "type": "string", "nullable": true },
          "status": { "type": "string", "enum": ["pending", "completed"] },
          "version": { "type": "integer" },
          "created_at": { "type": "string", "format": "date-time" },
          "updated_at": { "type": "string", "format": "date-time" }
        }
      }
    },
    "count": { "type": "integer" }
  },
  "required": ["tasks", "count"]
}
```

**Ordering**: Tasks returned newest first (descending by created_at)

#### Tool 3: update_task

**Purpose**: Modify task title and/or description

**Input Schema**:
```json
{
  "name": "update_task",
  "description": "Update task title and/or description for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to update"
      },
      "title": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200,
        "description": "New task title (optional)"
      },
      "description": {
        "type": "string",
        "maxLength": 2000,
        "description": "New task description (optional)"
      }
    },
    "required": ["task_id"]
  }
}
```

**Output Schema**: Same as add_task output (full task object)

**Concurrency**: Uses optimistic locking with version field

#### Tool 4: complete_task

**Purpose**: Mark task as completed

**Input Schema**:
```json
{
  "name": "complete_task",
  "description": "Mark a task as completed for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to complete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Output Schema**: Same as add_task output (full task object with status="completed")

**Idempotency**: Completing an already-completed task succeeds without error

#### Tool 5: delete_task

**Purpose**: Permanently remove task

**Input Schema**:
```json
{
  "name": "delete_task",
  "description": "Permanently delete a task for the authenticated user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "task_id": {
        "type": "string",
        "format": "uuid",
        "description": "UUID of the task to delete"
      }
    },
    "required": ["task_id"]
  }
}
```

**Output Schema**:
```json
{
  "type": "object",
  "properties": {
    "message": { "type": "string" },
    "task_id": { "type": "string", "format": "uuid" }
  },
  "required": ["message", "task_id"]
}
```

### Error Response Contract

**File**: `contracts/error-codes.json`

**Standard Error Format** (from spec clarifications):
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

**Error Codes**:
- `TASK_NOT_FOUND`: Task with specified ID does not exist
- `INVALID_INPUT`: Input validation failed (details contain field errors)
- `UNAUTHORIZED`: Missing or invalid authentication token
- `FORBIDDEN`: User attempting to access another user's task
- `CONFLICT`: Optimistic concurrency conflict (version mismatch)
- `DATABASE_ERROR`: Temporary database unavailability
- `INTERNAL_ERROR`: Unexpected server error

### Architecture Diagrams

#### MCP Tool Execution Flow

```
AI Agent → MCP Server → Auth Middleware → Tool Handler → Use Case → Database
                            ↓                  ↓            ↓
                       Extract user_id    Validate input  Execute query
                            ↓                  ↓            ↓
                       Verify JWT         Create session  Return result
                            ↓                  ↓            ↓
AI Agent ← JSON Response ← Format output ← Close session ← Commit/Rollback
```

#### Stateless Session Management

```
Tool Invocation Start
    ↓
Create AsyncSession (from pool)
    ↓
Execute Business Logic
    ↓
Commit Transaction
    ↓
Close Session (return to pool)
    ↓
Tool Invocation Complete
```

**Key Principle**: No session state persists between tool invocations. Each tool call is completely independent.

### Quickstart Guide

**File**: `quickstart.md`

Will include:
1. **Prerequisites**: Python 3.13+, UV, existing Phase-III backend
2. **Installation**: MCP SDK installation via UV
3. **Configuration**: Environment variables for MCP server
4. **Database Migration**: Add version field to Task table
5. **Running MCP Server**: Command to start server
6. **Testing Tools**: Manual tool invocation examples
7. **Integration with OpenAI Agents SDK**: Registration steps

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh claude` to add:
- Official MCP SDK (Python)
- MCP tool schema patterns
- Stateless session management patterns

---

## Phase 2: Task Decomposition

**Note**: This phase is executed by `/sp.tasks` command, NOT by `/sp.plan`.

The tasks.md file will break down implementation into atomic, testable tasks organized by user story:

**Expected Task Categories**:
1. **Research Tasks** (Phase 0 output validation)
2. **Database Migration Tasks** (add version field)
3. **MCP Server Setup Tasks** (SDK integration, server initialization)
4. **Tool Implementation Tasks** (5 tools × implementation + tests)
5. **Authentication Middleware Tasks** (user_id extraction)
6. **Error Handling Tasks** (standard error format)
7. **Integration Testing Tasks** (end-to-end tool execution)
8. **Documentation Tasks** (quickstart, API docs)

---

## Implementation Strategy

### Reuse Existing Infrastructure

**Maximize Code Reuse**:
- ✅ Domain models (User, Task) - add version field only
- ✅ Use cases (task_operations.py) - reuse all CRUD logic
- ✅ Database connection (database.py) - reuse session factory
- ✅ Configuration (config.py) - add MCP-specific settings
- ✅ JWT middleware (jwt_auth.py) - adapt for MCP context
- ✅ Error handling (error_handler.py) - extend for MCP errors

**New Components**:
- MCP server initialization and tool registration
- MCP tool wrappers around existing use cases
- MCP-specific input/output schemas
- Authentication context extraction for MCP requests
- MCP error response formatting

### Stateless Architecture Enforcement

**Session Management Pattern**:
```python
async def execute_tool(tool_input, auth_context):
    # Extract user_id from auth context
    user_id = extract_user_id(auth_context)

    # Create request-scoped session
    async with get_session() as session:
        # Execute business logic
        result = await use_case_function(session, user_id, tool_input)

        # Commit transaction
        await session.commit()

        # Return result (session auto-closes)
        return result
```

**No State Retention**:
- No module-level variables storing user data
- No caching of user sessions or task data
- No in-memory conversation history
- All state queries hit database on every tool invocation

### Testing Strategy

**Test Pyramid**:
1. **Unit Tests** (60%):
   - Tool input validation
   - Error response formatting
   - Auth context extraction
   - Schema compliance

2. **Integration Tests** (30%):
   - Tool execution with database
   - User isolation enforcement
   - Concurrent tool invocations
   - Error handling flows

3. **Contract Tests** (10%):
   - MCP tool schema validation
   - OpenAI Agents SDK compatibility
   - Error format compliance

**Test Coverage Target**: 80%+ for new MCP code

### Deployment Considerations

**Environment Variables** (add to existing .env):
```bash
# MCP Server Configuration
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_TOOL_TIMEOUT=30000  # 30 seconds

# OpenAI Agents SDK Integration
OPENAI_API_KEY=<key>
OPENAI_AGENT_ID=<agent-id>
```

**Server Startup**:
- Option 1: Separate process (recommended for Phase III)
- Option 2: Integrated with FastAPI (single process)

**Health Checks**:
- Extend existing /api/health endpoint
- Add MCP-specific health indicators

---

## Risk Mitigation

### Risk 1: MCP SDK Learning Curve

**Mitigation**:
- Phase 0 research includes SDK documentation review
- Start with simplest tool (add_task) as proof of concept
- Leverage existing FastAPI patterns where possible

### Risk 2: Stateless Session Management Complexity

**Mitigation**:
- Reuse existing database.py session factory
- Use context managers for automatic cleanup
- Add integration tests for session lifecycle

### Risk 3: Authentication Context Extraction

**Mitigation**:
- Research MCP request context structure in Phase 0
- Adapt existing JWT middleware patterns
- Add unit tests for auth extraction logic

### Risk 4: Optimistic Concurrency Implementation

**Mitigation**:
- Add version field in database migration
- Implement version check in update operations
- Return clear CONFLICT error on version mismatch
- Add integration tests for concurrent updates

---

## Success Criteria Validation

**From Specification**:

✅ **SC-001**: Tool execution <500ms for 95% of add_task requests
- **Validation**: Performance testing with database connection pooling

✅ **SC-002**: Tool execution <300ms for 95% of list_tasks requests
- **Validation**: Query optimization with existing indexes

✅ **SC-003**: 99.9% uptime for tool availability
- **Validation**: Health check endpoint, error recovery testing

✅ **SC-004**: 100% cross-user access blocked
- **Validation**: Integration tests for user isolation

✅ **SC-005**: Support 100+ concurrent agent requests
- **Validation**: Load testing with concurrent tool invocations

✅ **SC-006**: Structured, parseable JSON responses
- **Validation**: Contract tests for response schema

✅ **SC-007**: Graceful database failure recovery
- **Validation**: Error handling tests with database unavailability

✅ **SC-008**: Zero data loss during concurrent operations
- **Validation**: Optimistic concurrency tests

✅ **SC-009**: No silent failures
- **Validation**: Error logging and response validation

✅ **SC-010**: OpenAI Agents SDK compatibility
- **Validation**: Integration testing with Agents SDK

---

## Next Steps

1. **Execute Phase 0**: Run research tasks and document findings in `research.md`
2. **Execute Phase 1**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Update Agent Context**: Run update script to add MCP SDK knowledge
4. **Execute `/sp.tasks`**: Generate atomic task breakdown in `tasks.md`
5. **Begin Implementation**: Execute tasks via `/sp.implement`

**Ready for**: Phase 0 research execution
