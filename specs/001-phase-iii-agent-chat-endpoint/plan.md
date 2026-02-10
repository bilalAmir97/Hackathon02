# Implementation Plan: AI Orchestration Layer - Agent Chat Endpoint

**Branch**: `001-phase-iii-agent-chat-endpoint` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-iii-agent-chat-endpoint/spec.md`

## Summary

Implement a stateless AI agent orchestration layer that uses OpenAI Agents SDK with MCP tool integration to provide a conversational interface for task management. The system will persist conversation history to Neon PostgreSQL, expose a single chat endpoint `/api/{user_id}/chat`, and return tool call transparency for all operations. The agent will use existing MCP tools (add_task, list_tasks, update_task, complete_task, delete_task) exclusively for data mutations, with Groq's `openai/gpt-oss-20b` model as the primary AI provider.

## Technical Context

**Language/Version**: Python 3.13+ (existing backend)
**Primary Dependencies**:
- FastAPI (existing)
- SQLModel (existing ORM)
- OpenAI Agents SDK (new - for agent orchestration)
- Official MCP SDK (existing - tools already implemented)
- Groq API client (new - for `openai/gpt-oss-20b` model)
- Neon Serverless PostgreSQL (existing)

**Storage**: Neon PostgreSQL with SQLModel ORM (existing connection in `src/database.py`)
**Testing**: pytest, pytest-asyncio (existing test infrastructure)
**Target Platform**: Linux server (FastAPI backend deployment)
**Project Type**: Web application (existing Phase-III structure)

**Performance Goals**:
- Chat endpoint response < 3 seconds (excluding AI model latency)
- Database queries < 500ms for conversation history (up to 100 messages)
- Support 50 concurrent chat requests

**Constraints**:
- Groq rate limits: 200,000 tokens/min, 30 requests/min, 1000 requests/day
- Stateless design (no in-memory conversation state)
- JWT authentication required (existing middleware)
- MCP tools only (no direct database mutations in agent code)

**Scale/Scope**:
- Multi-user system (existing user isolation via JWT)
- Conversation history persistence (new requirement)
- Tool call transparency (new requirement)
- Agent guardrails and confirmation flows (new requirement)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Governance ✅ PASS
- **Phase III Requirements**: AI-powered chatbot with OpenAI Agents SDK and MCP tools
- **Feature Level**: Basic Level only (5 core CRUD operations via natural language)
- **No Future-Phase Leakage**: No Intermediate/Advanced features (priorities, tags, recurring tasks, reminders)
- **Verification**: Spec explicitly limits to Basic Level task operations through conversational interface

### Spec-Driven Development ✅ PASS
- **Approved Spec**: `/specs/001-phase-iii-agent-chat-endpoint/spec.md` exists and validated
- **Plan Before Code**: This plan.md created before implementation
- **Tasks Next**: Will generate tasks.md via `/sp.tasks` after plan approval
- **Implementation Last**: Code written only after tasks approved

### Agent Behavior Rules ✅ PASS
- **MCP Tools Only**: Agent will use existing MCP tools exclusively (no direct DB access)
- **No Feature Invention**: Agent limited to 5 Basic Level operations defined in spec
- **Decision Documentation**: Architectural decisions will be documented in ADRs
- **Task References**: All code will reference Task IDs from tasks.md

### Stateless Services ✅ PASS (Phase III Requirement)
- **No In-Memory State**: Conversation history persisted to database
- **Stateless Request Cycle**: Store message → fetch history → run agent → persist response → return
- **Restart Safe**: Server can restart without data loss
- **Horizontal Scalability**: Design supports multiple backend instances

### Contract-First Design ✅ PASS
- **API Contracts**: Will define OpenAPI spec for `/api/{user_id}/chat` endpoint
- **MCP Tool Contracts**: Existing tools already have defined schemas
- **Request/Response Schemas**: Will define Conversation and Message models
- **Tool Call Schema**: Will define structured tool_calls transparency format

### Test-Driven Development ✅ PASS
- **Tests First**: Will write tests before implementation
- **Contract Tests**: Will test chat endpoint contract compliance
- **Integration Tests**: Will test agent → MCP tool → database flow
- **E2E Tests**: Will test complete user journeys (create, list, update, complete, delete)

### Clean Architecture ✅ PASS
- **Existing Structure**: Backend already follows clean architecture
  - Domain: `src/domain/` (models)
  - Use Cases: `src/use_cases/` (business logic)
  - API: `src/api/` (controllers)
  - Infrastructure: `src/database.py`, `src/mcp/` (external services)
- **New Components**: Agent orchestration will fit into use_cases layer

### Security & Compliance ✅ PASS
- **JWT Authentication**: Existing middleware in `src/middleware/`
- **User Isolation**: Existing user_id enforcement in MCP tools
- **Path Validation**: Chat endpoint will validate user_id in path matches JWT token
- **Agent Guardrails**: Will implement prompt injection prevention and confirmation flows

### Observability & Monitoring ✅ PASS
- **Structured Logging**: Will log all tool calls with request_id, user_id, inputs, outputs, timing
- **Health Checks**: Existing `/health` endpoint
- **Error Tracking**: Will implement comprehensive error handling with retry logic
- **Metrics**: Will track response times and tool execution metrics

### Technology Constraints ✅ PASS
- **Backend**: Python 3.13+ with FastAPI ✓
- **Database**: Neon Serverless PostgreSQL ✓
- **ORM**: SQLModel ✓
- **AI Framework**: OpenAI Agents SDK (specified in constitution for Phase III) ✓
- **MCP Protocol**: Official MCP SDK (existing implementation) ✓
- **Testing**: pytest ✓

**Constitution Compliance**: ALL GATES PASSED ✅

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-iii-agent-chat-endpoint/
├── spec.md                  # Feature specification (completed)
├── plan.md                  # This file (in progress)
├── research.md              # Phase 0 output (to be created)
├── data-model.md            # Phase 1 output (to be created)
├── quickstart.md            # Phase 1 output (to be created)
├── contracts/               # Phase 1 output (to be created)
│   ├── chat-endpoint.openapi.yaml
│   └── tool-call-schema.json
└── tasks.md                 # Phase 2 output (via /sp.tasks - NOT created by /sp.plan)
```

### Source Code (existing Phase-III structure)

```text
Phase-III/
├── backend/
│   ├── src/
│   │   ├── domain/
│   │   │   └── models/
│   │   │       ├── user.py              # Existing
│   │   │       ├── task.py              # Existing
│   │   │       ├── conversation.py      # NEW - Phase 1
│   │   │       └── message.py           # NEW - Phase 1
│   │   ├── use_cases/
│   │   │   ├── task_operations.py       # Existing
│   │   │   └── agent_orchestration.py   # NEW - Phase 1
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── tasks.py             # Existing
│   │   │   │   └── chat.py              # NEW - Phase 1
│   │   │   └── schemas/
│   │   │       ├── task_schemas.py      # Existing
│   │   │       └── chat_schemas.py      # NEW - Phase 1
│   │   ├── mcp/
│   │   │   ├── server.py                # Existing MCP server
│   │   │   ├── tools/                   # Existing MCP tools
│   │   │   │   ├── add_task.py
│   │   │   │   ├── list_tasks.py
│   │   │   │   ├── update_task.py
│   │   │   │   ├── complete_task.py
│   │   │   │   └── delete_task.py
│   │   │   └── middleware/              # Existing
│   │   │       ├── auth_context.py
│   │   │       └── error_handler.py
│   │   ├── agent/                       # NEW - Phase 1
│   │   │   ├── __init__.py
│   │   │   ├── agent_factory.py         # Agent creation and configuration
│   │   │   ├── mcp_adapter.py           # MCP tool adapter for OpenAI Agents SDK
│   │   │   ├── guardrails.py            # Prompt injection prevention, confirmation logic
│   │   │   └── instructions.py          # System prompts and agent behavior
│   │   ├── middleware/
│   │   │   └── auth.py                  # Existing JWT middleware
│   │   ├── database.py                  # Existing database connection
│   │   ├── config.py                    # Existing config (will add Groq API key)
│   │   └── main.py                      # Existing FastAPI app
│   └── tests/
│       ├── unit/
│       │   └── test_agent_orchestration.py  # NEW
│       ├── integration/
│       │   └── test_chat_endpoint.py        # NEW
│       └── contract/
│           └── test_chat_contract.py        # NEW
└── frontend/
    └── src/                             # Existing Next.js frontend (out of scope)
```

**Structure Decision**: Using existing Phase-III web application structure. Backend follows clean architecture with domain models, use cases, API routes, and infrastructure layers. New agent orchestration components will be added to `src/agent/` directory, new database models to `src/domain/models/`, and new chat endpoint to `src/api/routes/chat.py`. This maintains separation of concerns and aligns with existing codebase patterns.

## Complexity Tracking

> **No violations detected - all constitution gates passed**

## Phase 0: Research & Discovery

### Research Tasks

#### 1. OpenAI Agents SDK with MCP Integration

**Objective**: Understand how to create agents that use MCP tools instead of function tools

**Key Questions**:
- How does OpenAI Agents SDK integrate with MCP protocol?
- What's the difference between function tools and MCP tools in agent context?
- How to register MCP tools with the agent?
- How to pass user_id context through MCP tool calls?
- How to handle tool call responses and errors?

**Research Sources**:
- OpenAI Agents SDK documentation: https://openai.github.io/openai-agents-python/
- Official MCP SDK documentation: https://modelcontextprotocol.io/docs/develop/build-server
- Existing MCP server implementation: `Phase-III/backend/src/mcp/server.py`

**Expected Findings**:
- MCP tool registration pattern for OpenAI Agents SDK
- Context passing mechanism for user_id enforcement
- Tool schema definition format
- Error handling and retry patterns

#### 2. Groq Model Configuration

**Objective**: Configure `openai/gpt-oss-20b` model via Groq API with fallback strategy

**Key Questions**:
- How to configure Groq API client for OpenAI Agents SDK?
- What's the API compatibility between Groq and OpenAI?
- How to implement rate limit handling (200k tokens/min, 30 req/min, 1000 req/day)?
- How to implement fallback to OpenAI models on Groq failure?
- What's the model's tool-calling capability?

**Research Sources**:
- Groq model documentation: https://console.groq.com/docs/model/openai/gpt-oss-20b
- Groq API reference
- OpenAI Agents SDK model configuration

**Expected Findings**:
- Groq API client configuration
- Rate limit detection and handling strategy
- Fallback model selection criteria
- Model performance characteristics

#### 3. Stateless Conversation Architecture

**Objective**: Design database schema and request cycle for stateless conversation management

**Key Questions**:
- How to structure Conversation and Message models?
- How to efficiently fetch conversation history (up to 100 messages)?
- How to build message array for agent from database records?
- How to persist tool calls with transparency data?
- How to handle concurrent requests to same conversation?

**Research Sources**:
- Existing database models: `Phase-III/backend/src/domain/models/`
- SQLModel documentation
- OpenAI Agents SDK conversation handling

**Expected Findings**:
- Conversation and Message model schemas
- Database query optimization strategies
- Tool call transparency schema format
- Concurrency handling approach

#### 4. Agent Guardrails and Confirmation Flows

**Objective**: Implement prompt injection prevention and destructive action confirmation

**Key Questions**:
- How to prevent prompt injection attacks in agent instructions?
- How to implement confirmation flows for destructive operations (complete, delete)?
- How to detect ambiguous task references and request clarification?
- How to enforce "MCP tools only" policy in agent behavior?

**Research Sources**:
- OpenAI Agents SDK guardrails documentation
- Security best practices for LLM agents
- Existing MCP tool validation: `Phase-III/backend/src/mcp/middleware/`

**Expected Findings**:
- Guardrail implementation patterns
- Confirmation flow state management
- Ambiguity detection strategies
- System prompt templates

### Research Output

**Deliverable**: `research.md` containing:
- MCP tool integration patterns with code examples
- Groq model configuration and fallback strategy
- Conversation persistence architecture
- Agent guardrail implementation approach
- Architectural decision rationale for key choices

**Decision Points to Document**:
1. **Groq-only vs Fallback Strategy**: Use Groq as primary with OpenAI fallback on rate limit or failure
2. **Tool Transparency Schema**: JSON structure for tool_calls array in API response
3. **Guardrail Strictness**: Balance between security and agent flexibility
4. **Confirmation Flow**: Multi-turn conversation vs single-turn with explicit confirmation

## Phase 1: Design & Contracts

### 1. Data Model Design

**Objective**: Define Conversation and Message models with relationships

**Deliverable**: `data-model.md`

#### Conversation Model

```python
class Conversation(SQLModel, table=True):
    """Represents a chat session between user and AI agent."""
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")
    user: "User" = Relationship(back_populates="conversations")
```

#### Message Model

```python
class Message(SQLModel, table=True):
    """Represents a single message in a conversation."""
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    role: str = Field(...)  # "user" or "assistant"
    content: str = Field(...)  # Message text
    tool_calls: str | None = Field(default=None)  # JSON array of tool invocations
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

#### Tool Call Transparency Schema

```json
{
  "tool_calls": [
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
}
```

### 2. API Contract Design

**Objective**: Define OpenAPI specification for chat endpoint

**Deliverable**: `contracts/chat-endpoint.openapi.yaml`

#### Chat Endpoint Contract

```yaml
openapi: 3.0.0
info:
  title: AI Chat Endpoint
  version: 1.0.0

paths:
  /api/{user_id}/chat:
    post:
      summary: Send message to AI agent
      security:
        - BearerAuth: []
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                conversation_id:
                  type: integer
                  description: Optional conversation ID to resume
                message:
                  type: string
                  description: User message text
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                required:
                  - conversation_id
                  - response
                  - tool_calls
                properties:
                  conversation_id:
                    type: integer
                  response:
                    type: string
                  tool_calls:
                    type: array
                    items:
                      $ref: '#/components/schemas/ToolCall'
        '401':
          description: Unauthorized (invalid JWT or user_id mismatch)
        '403':
          description: Forbidden (conversation belongs to different user)
        '429':
          description: Rate limit exceeded
        '500':
          description: Internal server error

components:
  schemas:
    ToolCall:
      type: object
      required:
        - tool_name
        - input_parameters
        - output_result
        - execution_status
      properties:
        tool_name:
          type: string
          enum: [add_task, list_tasks, update_task, complete_task, delete_task]
        input_parameters:
          type: object
        output_result:
          type: object
        execution_status:
          type: string
          enum: [success, error]
        error_message:
          type: string
          nullable: true
        timestamp:
          type: string
          format: date-time

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

### 3. Agent Architecture Design

**Objective**: Design agent orchestration layer with MCP integration

**Components**:

#### Agent Factory (`src/agent/agent_factory.py`)
- Creates and configures OpenAI Agents SDK agent
- Registers MCP tools with agent
- Sets up Groq model configuration with fallback
- Applies system instructions and guardrails

#### MCP Adapter (`src/agent/mcp_adapter.py`)
- Adapts existing MCP tools for OpenAI Agents SDK
- Handles context passing (user_id from JWT)
- Translates tool responses to agent format
- Implements retry logic for transient failures

#### Guardrails (`src/agent/guardrails.py`)
- Prompt injection prevention
- Confirmation flow for destructive operations
- Ambiguity detection and clarification requests
- "MCP tools only" policy enforcement

#### Instructions (`src/agent/instructions.py`)
- System prompt templates
- Intent-to-tool mapping rules
- Confirmation prompt templates
- Error message templates

### 4. Request Cycle Design

**Stateless Request Flow**:

```
1. Request arrives: POST /api/{user_id}/chat
   ↓
2. Validate JWT token and user_id match
   ↓
3. Store user message to database (Message table)
   ↓
4. Fetch conversation history from database (if conversation_id provided)
   ↓
5. Build message array: [history messages] + [new user message]
   ↓
6. Run agent with message array and MCP tools
   ↓
7. Agent interprets intent and calls MCP tools
   ↓
8. Collect tool call results with transparency data
   ↓
9. Agent generates response based on tool results
   ↓
10. Store assistant response + tool_calls to database
    ↓
11. Return response with conversation_id and tool_calls array
```

### 5. Configuration Design

**Environment Variables** (add to `src/config.py`):

```python
# Groq Configuration
GROQ_API_KEY: str
GROQ_MODEL: str = "openai/gpt-oss-20b"
GROQ_MAX_TOKENS: int = 200000
GROQ_MAX_REQUESTS_PER_MINUTE: int = 30
GROQ_MAX_REQUESTS_PER_DAY: int = 1000

# OpenAI Fallback Configuration
OPENAI_API_KEY: str
OPENAI_FALLBACK_MODEL: str = "gpt-4o-mini"

# Agent Configuration
AGENT_MAX_RETRIES: int = 3
AGENT_RETRY_BACKOFF_SECONDS: int = 2
AGENT_TIMEOUT_SECONDS: int = 30
AGENT_MAX_CONVERSATION_HISTORY: int = 100

# Feature Flags
ENABLE_GROQ_FALLBACK: bool = True
ENABLE_AGENT_GUARDRAILS: bool = True
ENABLE_CONFIRMATION_FLOWS: bool = True
```

### 6. Quickstart Guide

**Deliverable**: `quickstart.md`

**Contents**:
- Environment setup (Groq API key, OpenAI API key)
- Database migration for Conversation and Message tables
- Running the chat endpoint locally
- Testing with curl/Postman examples
- Verifying tool call transparency
- Troubleshooting common issues

## Phase 2: Task Decomposition

**Note**: This phase is executed via `/sp.tasks` command, NOT by `/sp.plan`.

The `/sp.tasks` command will generate `tasks.md` with atomic, testable tasks organized by user story:

**Expected Task Categories**:
1. Database schema and migrations (Conversation, Message models)
2. Agent factory and MCP adapter implementation
3. Chat endpoint implementation
4. Guardrails and confirmation flows
5. Groq model configuration and fallback
6. Tool call transparency and logging
7. Integration tests
8. End-to-end tests
9. Documentation and deployment

## Architecture Decision Records (ADRs)

### ADR-001: Groq as Primary Model with OpenAI Fallback

**Decision**: Use Groq's `openai/gpt-oss-20b` as primary model with automatic fallback to OpenAI `gpt-4o-mini` on rate limit or failure.

**Rationale**:
- Groq offers generous free tier (200k tokens/min, 30 req/min, 1000 req/day)
- Model supports GPT-style tool calling required for MCP integration
- OpenAI fallback ensures reliability during Groq outages or rate limits
- Cost optimization while maintaining service availability

**Alternatives Considered**:
- OpenAI-only: Higher cost, no free tier
- Groq-only: Risk of service disruption on rate limits
- Multiple model providers: Increased complexity

**Implementation**:
- Detect Groq rate limit errors (429 status)
- Automatic fallback to OpenAI on Groq failure
- Log model usage for cost tracking
- Configuration flag to disable fallback for testing

### ADR-002: Database-Persisted Conversation History

**Decision**: Store all conversation messages in PostgreSQL with tool_calls as JSON column.

**Rationale**:
- Stateless design requirement (no in-memory state)
- Enables conversation resume after server restart
- Provides audit trail for all tool operations
- Supports conversation replay and debugging

**Alternatives Considered**:
- Redis cache: Loses data on restart, no persistence guarantee
- In-memory: Violates stateless requirement
- Separate tool_calls table: Over-normalization for JSON data

**Implementation**:
- Conversation and Message models with SQLModel
- tool_calls stored as JSON string (PostgreSQL JSONB type)
- Index on conversation_id and created_at for efficient history queries
- Limit history fetch to 100 most recent messages

### ADR-003: MCP Tools Only Policy

**Decision**: Agent uses existing MCP tools exclusively; no direct database access in agent code.

**Rationale**:
- Maintains separation of concerns (agent orchestration vs data operations)
- Leverages existing MCP tool validation and error handling
- Ensures user_id enforcement through MCP middleware
- Simplifies agent logic and testing

**Alternatives Considered**:
- Direct database access: Bypasses MCP validation, duplicates logic
- Hybrid approach: Inconsistent patterns, harder to maintain

**Implementation**:
- Agent factory registers MCP tools with OpenAI Agents SDK
- MCP adapter translates tool calls to MCP protocol
- Guardrails enforce "MCP tools only" in system prompt
- No SQLModel imports in agent code

### ADR-004: Tool Call Transparency Schema

**Decision**: Return structured tool_calls array in every API response with tool name, inputs, outputs, status, and timestamp.

**Rationale**:
- Enables frontend to display tool operations to users
- Provides audit trail for debugging and compliance
- Supports UI features like "undo" or "explain what you did"
- Aligns with spec requirement for transparency

**Alternatives Considered**:
- Opaque responses: Poor user experience, no auditability
- Separate audit endpoint: Extra API call, inconsistent data
- Logs only: Not accessible to frontend

**Implementation**:
- Capture tool calls during agent execution
- Store in Message.tool_calls as JSON
- Include in API response as structured array
- Log tool calls separately for backend monitoring

## Risk Mitigation

### Risk 1: OpenAI Agents SDK MCP Integration Complexity

**Mitigation**:
- Research phase will validate MCP integration feasibility
- Fallback plan: Use function tools with MCP wrapper if native integration unavailable
- Prototype MCP adapter early in Phase 1
- Document integration patterns in research.md

### Risk 2: Groq Rate Limit Exhaustion

**Mitigation**:
- Implement automatic fallback to OpenAI on rate limit
- Add rate limit tracking and alerting
- Implement exponential backoff for retries
- Consider request queuing for high traffic

### Risk 3: Conversation History Performance Degradation

**Mitigation**:
- Limit history fetch to 100 most recent messages
- Add database indexes on conversation_id and created_at
- Implement pagination if needed in future
- Monitor query performance in production

### Risk 4: Agent Hallucination or Incorrect Tool Usage

**Mitigation**:
- Implement strict guardrails in system prompt
- Use structured tool schemas with validation
- Add confirmation flows for destructive operations
- Log all tool calls for review and debugging
- Test with diverse user inputs during development

## Next Steps

1. **User Approval**: Review and approve this implementation plan
2. **Phase 0 Execution**: Complete research tasks and document findings in `research.md`
3. **Phase 1 Execution**: Create data models, contracts, and architecture components
4. **ADR Creation**: Document significant decisions in `history/adr/`
5. **Task Generation**: Run `/sp.tasks` to generate atomic implementation tasks
6. **Implementation**: Execute tasks via `/sp.implement` with TDD approach

## Success Criteria

- [ ] Conversation and Message models created with migrations
- [ ] Chat endpoint `/api/{user_id}/chat` implemented and tested
- [ ] Agent orchestration layer integrated with MCP tools
- [ ] Groq model configured with OpenAI fallback
- [ ] Tool call transparency in all API responses
- [ ] JWT authentication and user_id validation enforced
- [ ] Guardrails prevent prompt injection and enforce confirmations
- [ ] Stateless design verified (server restart doesn't lose conversations)
- [ ] Integration tests pass for all user stories
- [ ] E2E tests validate complete user journeys
- [ ] Documentation complete (quickstart.md, research.md, data-model.md)
- [ ] Constitution compliance verified (all gates pass)
