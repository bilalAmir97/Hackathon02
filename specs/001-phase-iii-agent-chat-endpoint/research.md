# Research: AI Orchestration Layer - Agent Chat Endpoint

**Date**: 2026-02-09
**Feature**: Phase III AI Agent Chat Endpoint
**Branch**: `001-phase-iii-agent-chat-endpoint`

## Overview

This document captures research findings for implementing a stateless AI agent orchestration layer using OpenAI Agents SDK with MCP tool integration, Groq's `openai/gpt-oss-20b` model, and database-persisted conversation history.

## 1. OpenAI Agents SDK with MCP Integration

### Key Findings

**MCP Tool Integration Pattern**:
- OpenAI Agents SDK supports MCP (Model Context Protocol) tools as an alternative to function tools
- MCP tools are registered via the agent's tool registry with schema definitions
- Tools are invoked through the MCP protocol, maintaining separation between agent logic and tool implementation
- Context (like user_id) is passed through MCP headers/metadata

**Difference: Function Tools vs MCP Tools**:
- **Function Tools**: Directly callable Python functions registered with the agent
- **MCP Tools**: External tools accessed via MCP protocol (client-server architecture)
- **Advantage of MCP**: Separation of concerns, reusability across agents, centralized validation

**Tool Registration Pattern**:
```python
from openai_agents import Agent
from mcp import MCPClient

# Create MCP client connected to existing MCP server
mcp_client = MCPClient(server_url="http://localhost:8000/mcp")

# Register MCP tools with agent
agent = Agent(
    name="todo_assistant",
    model="openai/gpt-oss-20b",
    tools=mcp_client.get_tools(),  # Fetches tool schemas from MCP server
    instructions="You are a helpful assistant for managing tasks..."
)
```

**Context Passing for user_id**:
- MCP tools receive context through headers (existing implementation in `src/mcp/middleware/auth_context.py`)
- Agent adapter must inject JWT token into MCP tool calls
- Existing MCP middleware already validates user_id from JWT

**Error Handling**:
- MCP tools return structured error responses
- Agent can retry on transient failures
- Tool validation errors should be presented to user in natural language

### Decision: Use MCP Adapter Pattern

**Rationale**: Create an adapter layer (`src/agent/mcp_adapter.py`) that:
1. Translates OpenAI Agents SDK tool calls to MCP protocol
2. Injects user_id context from JWT into MCP headers
3. Handles MCP tool responses and errors
4. Implements retry logic for transient failures

**Implementation Approach**:
```python
class MCPToolAdapter:
    """Adapts MCP tools for OpenAI Agents SDK."""

    def __init__(self, mcp_client: MCPClient, user_id: str, jwt_token: str):
        self.mcp_client = mcp_client
        self.user_id = user_id
        self.jwt_token = jwt_token

    async def call_tool(self, tool_name: str, parameters: dict) -> dict:
        """Call MCP tool with user context."""
        headers = {"authorization": f"Bearer {self.jwt_token}"}

        try:
            result = await self.mcp_client.call_tool(
                tool_name=tool_name,
                parameters=parameters,
                headers=headers
            )
            return {"status": "success", "result": result}
        except MCPToolError as e:
            return {"status": "error", "error": str(e)}
```

## 2. Groq Model Configuration

### Key Findings

**API Compatibility**:
- Groq API is OpenAI-compatible (uses same request/response format)
- Can use OpenAI Python SDK with custom base_url pointing to Groq
- Model name: `openai/gpt-oss-20b`

**Rate Limits**:
- 200,000 tokens per minute
- 30 requests per minute
- 1,000 requests per day
- Rate limit errors return HTTP 429 status

**Tool-Calling Capability**:
- Model supports GPT-style function/tool calling
- Compatible with OpenAI Agents SDK tool invocation
- Structured output for tool calls

**Configuration Pattern**:
```python
from openai import AsyncOpenAI

# Groq client (OpenAI-compatible)
groq_client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# OpenAI fallback client
openai_client = AsyncOpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### Decision: Groq Primary with OpenAI Fallback

**Rationale**:
- Groq offers generous free tier for development and testing
- OpenAI fallback ensures reliability during rate limits or outages
- Cost optimization while maintaining service availability

**Fallback Strategy**:
1. Attempt request with Groq client
2. On 429 (rate limit) or 5xx (server error), switch to OpenAI
3. Log model usage for cost tracking
4. Implement exponential backoff for retries

**Implementation**:
```python
class ModelClient:
    """Manages Groq primary and OpenAI fallback."""

    def __init__(self):
        self.groq = groq_client
        self.openai = openai_client
        self.use_fallback = False

    async def create_completion(self, messages, tools):
        """Create completion with automatic fallback."""
        try:
            if not self.use_fallback:
                return await self.groq.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=messages,
                    tools=tools
                )
        except (RateLimitError, ServerError) as e:
            logger.warning(f"Groq error: {e}, falling back to OpenAI")
            self.use_fallback = True

        # Fallback to OpenAI
        return await self.openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools
        )
```

## 3. Stateless Conversation Architecture

### Key Findings

**Database Schema Design**:
- Two tables: `conversations` and `messages`
- Conversation tracks user_id and timestamps
- Message stores role, content, and tool_calls (JSON)
- Foreign key relationship: messages.conversation_id → conversations.id

**Efficient History Fetching**:
- Query: `SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT 100`
- Index on (conversation_id, created_at) for performance
- Limit to 100 most recent messages to prevent memory issues

**Message Array Construction**:
```python
async def build_message_array(conversation_id: int) -> list[dict]:
    """Build message array from database for agent."""
    messages = await db.query(
        Message
    ).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).limit(100).all()

    return [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]
```

**Tool Call Persistence**:
- Store tool_calls as JSON string in Message.tool_calls column
- PostgreSQL JSONB type for efficient querying if needed
- Include: tool_name, input_parameters, output_result, execution_status, error_message, timestamp

**Concurrency Handling**:
- Database transactions ensure consistency
- Row-level locking on conversation updates
- Optimistic concurrency with version field if needed

### Decision: PostgreSQL with JSONB for Tool Calls

**Rationale**:
- PostgreSQL JSONB provides efficient storage and querying for structured data
- Avoids over-normalization (separate tool_calls table)
- Supports future queries like "find all conversations where add_task was called"
- Maintains audit trail in single location

**Schema**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_created ON messages(conversation_id, created_at);
```

## 4. Agent Guardrails and Confirmation Flows

### Key Findings

**Prompt Injection Prevention**:
- Use system-level instructions that cannot be overridden by user input
- Validate tool parameters before execution
- Implement input sanitization in MCP middleware (already exists)
- Limit agent capabilities to defined tools only

**Confirmation Flow Patterns**:
- **Multi-turn**: Agent asks "Are you sure?" → User confirms → Agent executes
- **Single-turn with explicit confirmation**: User says "Delete task 5 and I confirm" → Agent executes immediately
- **Ambiguity resolution**: Agent lists options → User selects → Agent executes

**Ambiguity Detection**:
- Check if task reference matches multiple tasks
- Call list_tasks with filters to find matches
- Present options to user if multiple matches found

**"MCP Tools Only" Policy**:
- System prompt explicitly states: "You can only use the provided MCP tools. Never attempt to access the database directly."
- No database imports in agent code
- All data operations go through MCP tools

### Decision: Multi-turn Confirmation with Explicit Override

**Rationale**:
- Balance between safety and user experience
- Prevents accidental destructive actions
- Allows power users to skip confirmation with explicit language
- Maintains conversation context for confirmation flow

**System Prompt Template**:
```
You are a helpful assistant for managing tasks. You can help users create, view, update, complete, and delete tasks using natural language.

IMPORTANT RULES:
1. You can ONLY use the provided MCP tools: add_task, list_tasks, update_task, complete_task, delete_task
2. NEVER attempt to access the database directly or use any other tools
3. For DESTRUCTIVE operations (complete_task, delete_task):
   - If the user's message does NOT explicitly confirm (e.g., "yes", "confirm", "I'm sure"), ask for confirmation first
   - If the user explicitly confirms in their message, proceed immediately
4. For AMBIGUOUS task references (e.g., "the meeting task"):
   - Call list_tasks to find matching tasks
   - If multiple matches, present options and ask user to clarify
5. Always explain what you did after executing a tool

INTENT MAPPING:
- "create", "add", "make" → add_task
- "show", "list", "view", "what are" → list_tasks
- "update", "change", "rename", "modify" → update_task
- "complete", "done", "finish", "mark as complete" → complete_task
- "delete", "remove" → delete_task
```

**Confirmation Flow Implementation**:
```python
def requires_confirmation(intent: str, message: str) -> bool:
    """Check if destructive action needs confirmation."""
    if intent not in ["complete_task", "delete_task"]:
        return False

    # Check for explicit confirmation in message
    confirmation_keywords = ["confirm", "yes", "sure", "go ahead", "do it"]
    message_lower = message.lower()

    return not any(keyword in message_lower for keyword in confirmation_keywords)
```

## 5. Tool Call Transparency Schema

### Decision: Structured JSON Array

**Schema Format**:
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

**Rationale**:
- Provides complete audit trail
- Enables frontend to display "what the agent did"
- Supports debugging and compliance
- Allows future features like "undo" or "explain"

## Summary of Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| MCP Integration | Adapter pattern with context injection | Maintains separation, reuses existing MCP tools |
| Primary Model | Groq `openai/gpt-oss-20b` | Generous free tier, tool-calling support |
| Fallback Strategy | Automatic OpenAI fallback on rate limit | Ensures reliability and availability |
| Conversation Storage | PostgreSQL with JSONB for tool_calls | Stateless design, efficient querying, audit trail |
| Confirmation Flow | Multi-turn with explicit override | Balance safety and user experience |
| Guardrails | System prompt + tool validation | Prevents prompt injection and incorrect usage |
| Tool Transparency | Structured JSON array in response | Auditability, frontend display, debugging |

## Implementation Priorities

1. **Phase 1A - Foundation** (Week 1):
   - Database models (Conversation, Message)
   - MCP adapter for OpenAI Agents SDK
   - Groq client with fallback

2. **Phase 1B - Core Logic** (Week 1):
   - Agent factory with system instructions
   - Chat endpoint with stateless cycle
   - Tool call transparency

3. **Phase 1C - Safety** (Week 2):
   - Guardrails implementation
   - Confirmation flows
   - Error handling and retry logic

4. **Phase 1D - Testing** (Week 2):
   - Integration tests
   - E2E tests
   - Load testing for concurrency

## References

- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- MCP Protocol: https://modelcontextprotocol.io/docs/develop/build-server
- Groq Model: https://console.groq.com/docs/model/openai/gpt-oss-20b
- Existing MCP Implementation: `Phase-III/backend/src/mcp/`
