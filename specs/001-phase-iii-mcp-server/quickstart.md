# Quickstart Guide: MCP Todo Server

**Feature**: 001-phase-iii-mcp-server
**Last Updated**: 2026-02-09

## Overview

This guide walks you through setting up and testing the MCP (Model Context Protocol) Todo Server that exposes task operations as tools for AI agents. The server integrates with the existing Phase-III FastAPI backend and provides stateless, database-backed tools compatible with OpenAI Agents SDK.

---

## Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.13+** installed
- ✅ **UV package manager** installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- ✅ **Phase-III backend** set up and running
- ✅ **Neon PostgreSQL database** configured
- ✅ **Valid JWT token** for authentication testing

---

## Installation

### Step 1: Install MCP SDK

Navigate to the Phase-III backend directory and add the MCP SDK:

```bash
cd Phase-III/backend
uv add mcp
```

**Expected Output**:
```
Resolved 1 package in 0.5s
Installed 1 package in 10ms
 + mcp==1.0.0
```

### Step 2: Verify Installation

```bash
uv run python -c "import mcp; print(f'MCP SDK version: {mcp.__version__}')"
```

---

## Database Migration

### Step 1: Create Migration for Version Field

Generate an Alembic migration to add the `version` field to the Task table:

```bash
cd Phase-III/backend
uv run alembic revision --autogenerate -m "add task version field for optimistic concurrency"
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected added column 'task.version'
  Generating /path/to/alembic/versions/abc123_add_task_version_field.py ... done
```

### Step 2: Review Migration File

Open the generated migration file and verify it adds the version column:

```python
def upgrade() -> None:
    op.add_column('task', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
    op.alter_column('task', 'version', server_default=None)

def downgrade() -> None:
    op.drop_column('task', 'version')
```

### Step 3: Apply Migration

```bash
uv run alembic upgrade head
```

**Expected Output**:
```
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, add task version field
```

### Step 4: Verify Migration

```bash
uv run python -c "
from src.database import engine
from sqlalchemy import text
import asyncio

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text('SELECT version FROM task LIMIT 1'))
        print('✅ Version column exists')

asyncio.run(check())
"
```

---

## Configuration

### Step 1: Update Environment Variables

Add MCP server configuration to `Phase-III/backend/.env`:

```bash
# MCP Server Configuration
MCP_SERVER_ENABLED=true
MCP_SERVER_PORT=8001
MCP_TOOL_TIMEOUT=30000

# Existing configuration (keep these)
DATABASE_URL=postgresql+asyncpg://...
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
FRONTEND_URL=http://localhost:3000
```

### Step 2: Update Config Module

Add MCP settings to `src/config.py`:

```python
class Settings(BaseSettings):
    # ... existing fields ...

    # MCP Server Configuration
    mcp_server_enabled: bool = Field(
        default=True,
        description="Enable MCP server for AI agent tools"
    )
    mcp_server_port: int = Field(
        default=8001,
        description="Port for MCP server",
        ge=1,
        le=65535
    )
    mcp_tool_timeout: int = Field(
        default=30000,
        description="Tool execution timeout in milliseconds",
        ge=1000,
        le=300000
    )
```

---

## Running the MCP Server

### Option 1: Development Mode (Recommended)

Run the MCP server in a separate terminal:

```bash
cd Phase-III/backend
uv run python -m src.mcp.server
```

**Expected Output**:
```
INFO: MCP Todo Server starting...
INFO: Server name: todo-mcp-server
INFO: Registered tools: add_task, list_tasks, update_task, complete_task, delete_task
INFO: Listening on stdio (port 8001)
INFO: Ready for tool invocations
```

### Option 2: Integrated with FastAPI

Add MCP routes to the existing FastAPI app (implementation in tasks.md).

---

## Testing MCP Tools

### Prerequisites for Testing

1. **Get a Valid JWT Token**:

```bash
# Register or login to get a token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123!"}' \
  | jq -r '.token'
```

Save the token as an environment variable:
```bash
export JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Test 1: Add Task

**Tool**: `add_task`

**Request**:
```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Expected Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "version": 1,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:30:00Z"
}
```

### Test 2: List Tasks

**Tool**: `list_tasks`

**Request** (all tasks):
```bash
curl -X POST http://localhost:8001/tools/list_tasks \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "all"}'
```

**Expected Response**:
```json
{
  "tasks": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "version": 1,
      "created_at": "2026-02-09T10:30:00Z",
      "updated_at": "2026-02-09T10:30:00Z"
    }
  ],
  "count": 1
}
```

### Test 3: Complete Task

**Tool**: `complete_task`

**Request**:
```bash
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "123e4567-e89b-12d3-a456-426614174000"}'
```

**Expected Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "version": 2,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:35:00Z"
}
```

### Test 4: Update Task

**Tool**: `update_task`

**Request**:
```bash
curl -X POST http://localhost:8001/tools/update_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries and cook dinner"
  }'
```

**Expected Response**:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "version": 3,
  "created_at": "2026-02-09T10:30:00Z",
  "updated_at": "2026-02-09T10:40:00Z"
}
```

### Test 5: Delete Task

**Tool**: `delete_task`

**Request**:
```bash
curl -X POST http://localhost:8001/tools/delete_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "123e4567-e89b-12d3-a456-426614174000"}'
```

**Expected Response**:
```json
{
  "message": "Task deleted successfully",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

---

## Testing Error Scenarios

### Test: Missing Authentication

```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}'
```

**Expected Error**:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing authentication credentials",
    "details": {}
  }
}
```

### Test: Invalid Input

```bash
curl -X POST http://localhost:8001/tools/add_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Missing title"}'
```

**Expected Error**:
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Input validation failed",
    "details": {
      "errors": [
        {
          "field": "title",
          "message": "Field required",
          "type": "value_error.missing"
        }
      ]
    }
  }
}
```

### Test: Task Not Found

```bash
curl -X POST http://localhost:8001/tools/complete_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "00000000-0000-0000-0000-000000000000"}'
```

**Expected Error**:
```json
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with ID 00000000-0000-0000-0000-000000000000 not found",
    "details": {}
  }
}
```

---

## Integration with OpenAI Agents SDK

### Step 1: Register MCP Server

Create an MCP server configuration file for OpenAI Agents SDK:

```json
{
  "name": "todo-mcp-server",
  "url": "http://localhost:8001",
  "tools": [
    "add_task",
    "list_tasks",
    "update_task",
    "complete_task",
    "delete_task"
  ],
  "authentication": {
    "type": "bearer",
    "token_env": "JWT_TOKEN"
  }
}
```

### Step 2: Test with OpenAI Agent

```python
from openai import OpenAI
from openai.agents import Agent

client = OpenAI(api_key="your-openai-api-key")

agent = Agent(
    name="Todo Assistant",
    instructions="You help users manage their todo tasks.",
    mcp_servers=["http://localhost:8001"]
)

# Test natural language interaction
response = agent.run("Add a task to buy groceries")
print(response)
```

---

## Troubleshooting

### Issue: "Module 'mcp' not found"

**Solution**: Install MCP SDK
```bash
uv add mcp
```

### Issue: "Column 'version' does not exist"

**Solution**: Run database migration
```bash
uv run alembic upgrade head
```

### Issue: "UNAUTHORIZED" error with valid token

**Solution**: Verify `BETTER_AUTH_SECRET` matches between frontend and backend
```bash
# Check backend .env
grep BETTER_AUTH_SECRET Phase-III/backend/.env

# Check frontend .env.local
grep BETTER_AUTH_SECRET Phase-III/frontend/.env.local
```

### Issue: "DATABASE_ERROR" responses

**Solution**: Check database connection
```bash
# Test database connectivity
uv run python -c "
from src.database import engine
import asyncio

async def test():
    async with engine.connect() as conn:
        print('✅ Database connection successful')

asyncio.run(test())
"
```

### Issue: MCP server not responding

**Solution**: Check if server is running and port is correct
```bash
# Check if port 8001 is in use
lsof -i :8001

# Restart MCP server
uv run python -m src.mcp.server
```

---

## Performance Validation

### Test: Tool Execution Time

```bash
# Measure add_task performance
time curl -X POST http://localhost:8001/tools/add_task \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Performance test"}'
```

**Expected**: < 500ms for 95% of requests

### Test: Concurrent Requests

```bash
# Run 100 concurrent requests
for i in {1..100}; do
  curl -X POST http://localhost:8001/tools/add_task \
    -H "Authorization: Bearer $JWT_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Task $i\"}" &
done
wait
```

**Expected**: All requests succeed without errors

---

## Next Steps

1. ✅ **MCP Server Running**: Verify all 5 tools are accessible
2. ✅ **Database Migration**: Confirm version field exists
3. ✅ **Authentication**: Test with valid JWT tokens
4. ✅ **Error Handling**: Verify standard error format
5. ⏭️ **Integration**: Connect with OpenAI Agents SDK
6. ⏭️ **Implementation**: Execute tasks via `/sp.tasks` and `/sp.implement`

---

## Resources

- **Specification**: [spec.md](./spec.md)
- **Implementation Plan**: [plan.md](./plan.md)
- **Research Findings**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Tool Contracts**: [contracts/mcp-tools.json](./contracts/mcp-tools.json)
- **Error Codes**: [contracts/error-codes.json](./contracts/error-codes.json)
- **Official MCP Docs**: https://modelcontextprotocol.io/docs/develop/build-server

---

**Questions or Issues?** Check the troubleshooting section or review the implementation plan for detailed architecture information.
