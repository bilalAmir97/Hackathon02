# Research Findings: MCP Todo Server Implementation

**Date**: 2026-02-09
**Feature**: 001-phase-iii-mcp-server
**Phase**: Phase 0 - Research

## Overview

This document captures research findings for implementing a stateless MCP (Model Context Protocol) server that exposes todo task operations as tools for AI agents. All research areas identified in plan.md have been investigated and decisions documented.

---

## Research Area 1: Official MCP SDK Integration Patterns

### Decision

Use the **Official Python MCP SDK** (`mcp` package) with FastAPI integration pattern where MCP server runs as a separate ASGI application alongside the existing FastAPI REST API.

### Rationale

- **Official Support**: Python MCP SDK is maintained by Anthropic with comprehensive documentation
- **FastAPI Compatibility**: SDK provides ASGI middleware that integrates seamlessly with FastAPI
- **Separation of Concerns**: Running MCP server on separate port (8001) maintains clean separation from REST API (8000)
- **Stateless Design**: SDK's request-response model aligns perfectly with stateless architecture requirements
- **Tool Registration**: Declarative tool registration using Python decorators simplifies implementation

### Alternatives Considered

1. **Custom MCP Protocol Implementation**
   - Rejected: Reinventing the wheel, high maintenance burden, protocol changes would require updates

2. **Integrated Single-Port Approach**
   - Rejected: Mixing REST and MCP concerns complicates routing and error handling

3. **Third-Party MCP Libraries**
   - Rejected: Official SDK provides best compatibility and long-term support

### Implementation Notes

**Installation**:
```bash
uv add mcp
```

**Server Initialization Pattern**:
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("todo-mcp-server")

@app.tool()
async def add_task(title: str, description: str = None):
    # Tool implementation
    pass

# Run server
if __name__ == "__main__":
    stdio_server(app)
```

**FastAPI Integration**:
- MCP server runs as separate process
- Shares database connection pool with REST API
- Reuses existing domain models and use cases
- Authentication handled via custom middleware

---

## Research Area 2: Tool Schema Design & Validation

### Decision

Use **Pydantic v2 models** for tool input/output schemas with automatic JSON Schema generation for MCP protocol compliance.

### Rationale

- **Type Safety**: Pydantic provides runtime validation and IDE autocomplete
- **JSON Schema Generation**: Automatic conversion to MCP-compatible JSON Schema
- **Existing Infrastructure**: Phase-III backend already uses Pydantic 2.12.5+
- **Validation Errors**: Pydantic error messages map cleanly to MCP error format
- **Documentation**: Schemas serve as both validation and documentation

### Alternatives Considered

1. **Manual JSON Schema Definitions**
   - Rejected: Error-prone, no type safety, duplicates validation logic

2. **Dataclasses with Manual Validation**
   - Rejected: Less powerful validation, no automatic JSON Schema generation

3. **TypedDict**
   - Rejected: Runtime validation requires additional libraries

### Implementation Notes

**Tool Input Schema Pattern**:
```python
from pydantic import BaseModel, Field

class AddTaskInput(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: str | None = Field(None, max_length=2000, description="Optional description")

    model_config = {
        "json_schema_extra": {
            "examples": [{"title": "Buy groceries", "description": "Milk, eggs, bread"}]
        }
    }
```

**Tool Output Schema Pattern**:
```python
class TaskOutput(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    version: int
    created_at: datetime
    updated_at: datetime
```

**MCP Tool Registration**:
```python
@app.tool()
async def add_task(input: AddTaskInput) -> TaskOutput:
    # Pydantic automatically validates input
    # Returns validated output
    pass
```

---

## Research Area 3: Stateless Execution & Database Session Management

### Decision

Use **request-scoped async context managers** with existing SQLAlchemy async session factory, ensuring each tool invocation creates and closes its own database session.

### Rationale

- **Stateless Guarantee**: No session state persists between tool invocations
- **Automatic Cleanup**: Context managers ensure sessions are closed even on errors
- **Connection Pooling**: Reuses existing pool (10 connections, 20 max overflow)
- **Transaction Safety**: Each tool invocation is a single transaction
- **Existing Infrastructure**: Leverages Phase-III database.py session factory

### Alternatives Considered

1. **Global Session with Manual Management**
   - Rejected: Violates stateless architecture, risk of session leaks

2. **Session Per Tool Class Instance**
   - Rejected: Still maintains state, complicates testing

3. **Dependency Injection via FastAPI**
   - Rejected: MCP SDK doesn't use FastAPI dependency injection

### Implementation Notes

**Session Factory Pattern**:
```python
from contextlib import asynccontextmanager
from src.database import async_session_maker

@asynccontextmanager
async def get_mcp_session():
    """Create request-scoped database session for MCP tools."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

**Tool Implementation Pattern**:
```python
@app.tool()
async def add_task(input: AddTaskInput, context: RequestContext) -> TaskOutput:
    user_id = extract_user_id(context)

    async with get_mcp_session() as session:
        # Execute business logic
        task = await create_task(session, user_id, input.title, input.description)
        return TaskOutput.model_validate(task)
```

**Connection Pool Configuration** (existing):
```python
# src/database.py
engine = create_async_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)
```

---

## Research Area 4: Authentication Context Extraction

### Decision

Extract `user_id` from **JWT token in Authorization header** using custom MCP middleware that integrates with existing Phase-III JWT verification logic.

### Rationale

- **Security**: Reuses battle-tested JWT verification from Phase-III
- **Consistency**: Same authentication mechanism as REST API
- **Stateless**: No session storage, token contains all user context
- **MCP Protocol**: Authorization header is standard HTTP header accessible in MCP requests
- **User Isolation**: user_id extracted from verified token ensures ownership enforcement

### Alternatives Considered

1. **user_id as Tool Parameter**
   - Rejected: Security risk (users could spoof user_id), violates separation of concerns

2. **Session-Based Authentication**
   - Rejected: Violates stateless architecture requirement

3. **API Key Authentication**
   - Rejected: Less secure than JWT, doesn't integrate with existing auth system

### Implementation Notes

**MCP Request Context Structure**:
```python
from mcp.server import RequestContext

# MCP SDK provides request context with headers
context.headers  # Dict[str, str] containing HTTP headers
```

**Auth Extraction Pattern**:
```python
from src.auth.token import verify_jwt_token

async def extract_user_id(context: RequestContext) -> UUID:
    """Extract and verify user_id from JWT token in Authorization header."""
    auth_header = context.headers.get("authorization")

    if not auth_header:
        raise MCPAuthError("UNAUTHORIZED", "Missing authentication credentials")

    if not auth_header.startswith("Bearer "):
        raise MCPAuthError("UNAUTHORIZED", "Invalid Authorization header format")

    token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        # Reuse existing JWT verification logic
        payload = verify_jwt_token(token, settings.better_auth_secret)
        user_id = UUID(payload["user_id"])
        return user_id
    except Exception as e:
        raise MCPAuthError("UNAUTHORIZED", f"Invalid token: {str(e)}")
```

**Integration with Existing Middleware**:
```python
# Reuse from src/auth/token.py
def verify_jwt_token(token: str, secret: str) -> dict:
    """Existing JWT verification logic (6-layer security)."""
    # 1. Signature verification
    # 2. Expiration check
    # 3. Claims extraction
    # 4. User existence
    # 5. Account status
    # 6. Password change validation
    pass
```

---

## Research Area 5: Error Handling & Response Formatting

### Decision

Implement **standardized error response format** with machine-readable error codes, human-readable messages, and optional details field, following the format clarified in spec.md.

### Rationale

- **AI Agent Compatibility**: Error codes enable programmatic error handling
- **Debugging Support**: Details field provides context without exposing internals
- **Consistency**: Same format across all tools and error types
- **MCP Protocol Compliance**: JSON error responses are standard in MCP
- **Spec Alignment**: Matches error format defined in clarification session

### Alternatives Considered

1. **Simple String Error Messages**
   - Rejected: Not machine-readable, AI agents can't handle errors programmatically

2. **HTTP Status Code Only**
   - Rejected: Insufficient granularity for different error types

3. **Exception-Based Error Propagation**
   - Rejected: Leaks internal implementation details

### Implementation Notes

**Standard Error Format**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
}
```

**Error Code Taxonomy**:
```python
class MCPErrorCode(str, Enum):
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
```

**Error Response Model**:
```python
class MCPError(BaseModel):
    code: MCPErrorCode
    message: str
    details: dict = Field(default_factory=dict)

class MCPErrorResponse(BaseModel):
    error: MCPError
```

**Error Handler Pattern**:
```python
from mcp.server import MCPError as SDKMCPError

def format_mcp_error(code: MCPErrorCode, message: str, details: dict = None) -> SDKMCPError:
    """Format error in standard MCP error response structure."""
    error_response = MCPErrorResponse(
        error=MCPError(
            code=code,
            message=message,
            details=details or {}
        )
    )
    return SDKMCPError(error_response.model_dump())
```

**Usage in Tools**:
```python
@app.tool()
async def add_task(input: AddTaskInput, context: RequestContext) -> TaskOutput:
    try:
        user_id = extract_user_id(context)
        async with get_mcp_session() as session:
            task = await create_task(session, user_id, input.title, input.description)
            return TaskOutput.model_validate(task)
    except ValidationError as e:
        raise format_mcp_error(
            MCPErrorCode.INVALID_INPUT,
            "Input validation failed",
            {"errors": e.errors()}
        )
    except TaskNotFoundError:
        raise format_mcp_error(
            MCPErrorCode.TASK_NOT_FOUND,
            f"Task not found",
            {}
        )
    except Exception as e:
        raise format_mcp_error(
            MCPErrorCode.INTERNAL_ERROR,
            "An unexpected error occurred",
            {}  # Don't expose internal details
        )
```

---

## Summary of Key Decisions

| Research Area | Decision | Key Benefit |
|---------------|----------|-------------|
| MCP SDK Integration | Official Python MCP SDK with separate ASGI app | Official support, clean separation |
| Tool Schema Design | Pydantic v2 models with JSON Schema generation | Type safety, automatic validation |
| Session Management | Request-scoped async context managers | Stateless guarantee, automatic cleanup |
| Authentication | JWT token in Authorization header | Security, consistency with REST API |
| Error Handling | Standardized error format with codes | AI agent compatibility, debugging support |

---

## Implementation Readiness

All research areas have been resolved with concrete decisions and implementation patterns. The findings provide sufficient detail to proceed with Phase 1 design and contract generation.

**Next Steps**:
1. Generate data-model.md with Task entity version field extension
2. Generate contracts/mcp-tools.json with all 5 tool schemas
3. Generate contracts/error-codes.json with error code definitions
4. Generate quickstart.md with setup and testing instructions
5. Update agent context with MCP SDK knowledge

**No Blockers**: All NEEDS CLARIFICATION items from Technical Context have been resolved.
