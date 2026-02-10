---
title: Hackathon02 Backend API
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# Backend Core & Data Layer - FastAPI Todo Application

Multi-user todo application backend with FastAPI, SQLModel, and Neon PostgreSQL.

## Features

- RESTful API for task management (CRUD operations)
- **AI-Powered Conversational Interface** - Natural language task management via chat endpoint
- **OpenAI Agents SDK Integration** - Real AI agent with MCP tools for task operations
- **Dual Provider Support** - Groq (primary) with OpenAI fallback for reliability
- **Conversation History** - Context-aware multi-turn conversations with automatic truncation
- **Tool Call Transparency** - Full auditability of all AI tool executions
- User-scoped data isolation
- Async database operations with connection pooling
- RFC 7807 Problem Details error responses
- Structured JSON logging with latency tracking
- Pagination support for list endpoints
- Retry logic with exponential backoff for transient failures

## Tech Stack

- **Framework**: FastAPI (async web framework)
- **ORM**: SQLModel (async SQLAlchemy wrapper)
- **Database**: Neon Serverless PostgreSQL
- **AI Agent**: OpenAI Agents SDK with Groq (primary) and OpenAI (fallback)
- **MCP Tools**: Model Context Protocol for tool integration
- **Validation**: Pydantic v2
- **Testing**: pytest, pytest-asyncio, httpx
- **Code Quality**: ruff (linting & formatting)

## Prerequisites

- Python 3.13+
- UV package manager
- Neon PostgreSQL database

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd Phase-II/backend
```

### 2. Install dependencies

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 3. Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your configuration:
# 1. Neon database credentials (required)
# 2. Groq API key (required for AI agent)
# 3. OpenAI API key (optional, for fallback)
# 4. Better Auth secret (required for JWT authentication)
```

**Required Configuration**:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `GROQ_API_KEY`: Get from https://console.groq.com/keys
- `BETTER_AUTH_SECRET`: Generate with `openssl rand -base64 32`

**Optional Configuration**:
- `OPENAI_API_KEY`: Get from https://platform.openai.com/api-keys (for fallback)
- `OPENAI_FALLBACK_ENABLED`: Set to `true` to enable OpenAI fallback on Groq rate limits

See `.env.example` for all available configuration options.

### 4. Run database migrations (if applicable)

```bash
# Create tables (will be implemented in Phase 2)
uv run python -m src.database
```

## Running the Application

### Development server

```bash
# Run with auto-reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- OpenAPI spec: http://localhost:8000/openapi.json

### Production server

```bash
# Run with multiple workers
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Running Tests

### Run all tests

```bash
uv run pytest
```

### Run with coverage

```bash
uv run pytest --cov=src --cov-report=html
```

### Run specific test types

```bash
# Unit tests only
uv run pytest tests/unit/

# Integration tests only
uv run pytest tests/integration/

# Contract tests only
uv run pytest tests/contract/
```

## Code Quality

### Linting

```bash
# Check code quality
uv run ruff check src/ tests/

# Auto-fix issues
uv run ruff check --fix src/ tests/
```

### Formatting

```bash
# Check formatting
uv run ruff format --check src/ tests/

# Format code
uv run ruff format src/ tests/
```

## Project Structure

```
Phase-II/backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application factory
│   ├── config.py            # Environment configuration
│   ├── database.py          # Database session management
│   ├── domain/              # Domain models (SQLModel entities)
│   ├── schemas/             # Pydantic request/response schemas
│   ├── use_cases/           # Business logic layer
│   ├── api/                 # API routes and dependencies
│   ├── middleware/          # Logging and error handling
│   └── utils/               # Shared utilities
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   ├── contract/            # API contract tests
│   └── fixtures/            # Test fixtures and helpers
├── .env.example             # Environment variable template
├── .gitignore               # Git ignore patterns
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## API Endpoints

### Health Check

- `GET /health` - Check API health status

**Example**:
```bash
curl http://localhost:8000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:45.123Z"
}
```

### Task Management

All task endpoints require a valid user UUID in the path. Tasks are scoped to users - each user can only access their own tasks.

#### Create a Task

**Endpoint**: `POST /users/{user_id}/tasks`

**Description**: Create a new task for the specified user.

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response** (201 Created):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T00:00:00Z"
}
```

#### Get a Task by ID

**Endpoint**: `GET /users/{user_id}/tasks/{task_id}`

**Description**: Retrieve a specific task by its ID. Only returns tasks owned by the specified user.

**Example**:
```bash
curl http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T00:00:00Z"
}
```

#### List Tasks

**Endpoint**: `GET /users/{user_id}/tasks`

**Description**: Retrieve a paginated list of tasks for the specified user with optional status filtering.

**Query Parameters**:
- `status` (optional): Filter by status (`pending` or `completed`)
- `offset` (optional): Starting position for pagination (default: 0)
- `limit` (optional): Maximum items per page (default: 20, max: 100)

**Examples**:
```bash
# List all tasks for user
curl http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks

# Filter by status
curl "http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks?status=pending"

# Pagination
curl "http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks?offset=20&limit=10"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2026-01-12T00:00:00Z",
      "updated_at": "2026-01-12T00:00:00Z"
    }
  ],
  "total": 25,
  "offset": 0,
  "limit": 20,
  "has_next": true,
  "has_previous": false
}
```

#### Update a Task

**Endpoint**: `PUT /users/{user_id}/tasks/{task_id}`

**Description**: Update an existing task. Supports partial updates - only provided fields will be updated.

**Request Body** (all fields optional, but at least one required):
```json
{
  "title": "Buy organic groceries",
  "description": "Organic milk, free-range eggs",
  "status": "completed"
}
```

**Example**:
```bash
curl -X PUT http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy organic groceries",
    "description": "Organic milk, free-range eggs",
    "status": "completed"
  }'
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy organic groceries",
  "description": "Organic milk, free-range eggs",
  "status": "completed",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T01:00:00Z"
}
```

#### Toggle Task Completion

**Endpoint**: `PATCH /users/{user_id}/tasks/{task_id}/complete`

**Description**: Toggle a task between pending and completed status.

**Example**:
```bash
curl -X PATCH http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000/complete
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T01:00:00Z"
}
```

#### Delete a Task

**Endpoint**: `DELETE /users/{user_id}/tasks/{task_id}`

**Description**: Permanently delete a task. This operation cannot be undone.

**Example**:
```bash
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response** (204 No Content): Empty response body

### Error Responses

All errors follow RFC 7807 Problem Details format:

**404 Not Found**:
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000"
}
```

**422 Validation Error**:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**503 Service Unavailable**:
```json
{
  "type": "https://api.example.com/errors/service-unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "Database connection unavailable. Please try again later.",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks"
}
```

### AI Chat Endpoint (Phase III)

**Endpoint**: `POST /users/{user_id}/chat`

**Description**: Conversational AI interface for natural language task management. The agent understands user intent and executes appropriate MCP tools (add_task, list_tasks, update_task, complete_task, delete_task).

**Features**:
- Natural language understanding for task operations
- Multi-turn conversations with context awareness
- Automatic conversation history management (last 20 messages)
- Full tool call transparency and auditability
- Retry logic with exponential backoff
- Groq primary provider with OpenAI fallback

**Request Body**:
```json
{
  "message": "Add a task to buy groceries",
  "conversation_id": 123
}
```

**Fields**:
- `message` (required): User's natural language message
- `conversation_id` (optional): Resume existing conversation (omit for new conversation)

**Example - Create Task**:
```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Response** (200 OK):
```json
{
  "conversation_id": 123,
  "response": "I've added a task to buy groceries for you.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "input_parameters": {
        "title": "Buy groceries"
      },
      "output_result": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "title": "Buy groceries",
        "status": "pending"
      },
      "execution_status": "success",
      "error_message": null,
      "timestamp": "2026-02-10T10:30:45.123Z"
    }
  ]
}
```

**Example - List Tasks**:
```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": 123
  }'
```

**Example - Multi-turn Conversation**:
```bash
# First message
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{"message": "Add a task to buy milk"}'

# Second message (uses context from first)
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt-token>" \
  -d '{
    "message": "Mark it as complete",
    "conversation_id": 123
  }'
```

**Tool Call Transparency**:

Every tool execution includes full transparency:
- `tool_name`: Which MCP tool was called
- `input_parameters`: Parameters passed to the tool
- `output_result`: Result returned by the tool
- `execution_status`: "success" or "error"
- `error_message`: Error details if execution failed
- `timestamp`: ISO 8601 timestamp of execution

**Supported Natural Language Patterns**:
- Create: "Add a task to...", "Create a task for...", "I need to..."
- List: "Show my tasks", "What tasks do I have?", "List all tasks"
- Update: "Change task X to...", "Update the title of..."
- Complete: "Mark task X as done", "Complete the task about..."
- Delete: "Remove task X", "Delete the task about..."

**AI Agent Configuration**:
- **Primary Provider**: Groq (openai/gpt-oss-20b model)
- **Fallback Provider**: OpenAI (gpt-4o-mini model)
- **Temperature**: 0.1 (deterministic, consistent responses)
- **Max Tokens**: 500 (concise responses)
- **History Limit**: 20 messages (automatic truncation)
- **Retry Policy**: 3 attempts with exponential backoff (100ms → 5s)

**Error Handling**:
- Transient failures (rate limits, timeouts) trigger automatic retry
- Groq rate limit triggers automatic fallback to OpenAI
- Tool execution errors are captured and returned in tool_calls
- User receives friendly error messages for all failure scenarios

### Authentication Notes

**Current Implementation**: This API currently uses user UUIDs in the URL path for user identification. In production, you should implement proper authentication:

- **JWT Tokens**: Add Bearer token authentication with JWT
- **OAuth2**: Integrate OAuth2 flows for third-party authentication
- **API Keys**: Use API keys for service-to-service communication

The user_id in the path should be validated against the authenticated user's identity to prevent unauthorized access.

**Recommended Approach**:
1. Add authentication middleware to verify JWT tokens
2. Extract user_id from the authenticated token
3. Validate that path user_id matches authenticated user_id
4. Return 403 Forbidden if user_id mismatch detected

## Environment Variables

See `.env.example` for all available configuration options:

- `DATABASE_URL` - Neon PostgreSQL connection string (required)
- `DATABASE_POOL_SIZE` - Connection pool size (default: 10)
- `DATABASE_MAX_OVERFLOW` - Max overflow connections (default: 20)
- `APP_ENV` - Environment (development/production/test)
- `LOG_LEVEL` - Logging level (DEBUG/INFO/WARNING/ERROR)
- `API_HOST` - API server host (default: 0.0.0.0)
- `API_PORT` - API server port (default: 8000)

## Development Workflow

1. Create a feature branch from `main`
2. Implement changes following clean architecture principles
3. Write tests (TDD approach preferred)
4. Run linting and formatting: `uv run ruff check --fix . && uv run ruff format .`
5. Run tests: `uv run pytest`
6. Commit changes with descriptive messages
7. Create a pull request

## Architecture

This backend follows clean architecture principles with clear separation of concerns:

- **Domain Layer**: SQLModel entities with business rules
- **Use Cases Layer**: Business logic and data operations
- **Interface Adapters**: FastAPI routes and Pydantic schemas
- **Infrastructure**: Database connections, logging, middleware

## Security

- User-scoped data access enforced at query level
- SQL injection prevention via ORM parameterized queries
- Input validation with Pydantic models
- Environment-based configuration (no hardcoded secrets)
- RFC 7807 error responses (no internal details exposed)

## Contributing

Please follow the project's coding standards and test requirements. All code must:

- Pass ruff linting and formatting checks
- Have 80%+ test coverage for business logic
- Include appropriate error handling
- Follow REST API conventions

## License

[Add license information]

## Support

For issues or questions, please refer to the project documentation in `/specs/003-todo-backend-core/`.
