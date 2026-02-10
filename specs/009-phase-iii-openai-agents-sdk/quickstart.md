# Quickstart Guide: OpenAI Agents SDK Integration

**Feature**: Phase III - Replace Mock Agent with Real OpenAI Agents SDK

**Status**: ✅ Implementation Complete

**Last Updated**: 2026-02-10

---

## Overview

This guide helps you quickly set up and test the AI-powered conversational task management system using OpenAI Agents SDK with Groq and OpenAI providers.

## What Was Implemented

### Core Features

1. **Real AI Agent** - Replaced mock intent detection with OpenAI Agents SDK
2. **MCP Tools Integration** - 5 tools for task operations (add, list, update, complete, delete)
3. **Dual Provider Support** - Groq (primary) with OpenAI (fallback)
4. **Conversation History** - Context-aware multi-turn conversations
5. **Tool Call Transparency** - Full auditability of all AI actions
6. **Retry Logic** - Exponential backoff for transient failures
7. **Deterministic Behavior** - Temperature 0.1 for consistent responses

### Architecture

```
User Message
    ↓
Chat Endpoint (/users/{user_id}/chat)
    ↓
AgentOrchestration
    ↓
RunnerFactory (OpenAI Agents SDK)
    ↓
Groq API (primary) ←→ OpenAI API (fallback)
    ↓
MCP Tools (add_task, list_tasks, etc.)
    ↓
Database (Neon PostgreSQL)
```

---

## Prerequisites

1. **Python 3.13+** installed
2. **UV package manager** installed
3. **Neon PostgreSQL** database
4. **Groq API key** (required) - Get from https://console.groq.com/keys
5. **OpenAI API key** (optional) - Get from https://platform.openai.com/api-keys

---

## Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd Phase-III/backend
uv sync
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and set these required variables:
# - DATABASE_URL (your Neon PostgreSQL connection string)
# - GROQ_API_KEY (your Groq API key)
# - BETTER_AUTH_SECRET (generate with: openssl rand -base64 32)

# Optional: Set OPENAI_API_KEY for fallback support
```

**Minimum Required Configuration**:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database?sslmode=require
GROQ_API_KEY=your-groq-api-key-here
BETTER_AUTH_SECRET=your-32-char-secret-here
```

### Step 3: Run Database Migrations

```bash
uv run alembic upgrade head
```

### Step 4: Start the Server

```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs

---

## Testing the AI Agent

### Test 1: Create a Task

```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "response": "I've added a task to buy groceries for you.",
  "tool_calls": [
    {
      "tool_name": "add_task",
      "input_parameters": {"title": "Buy groceries"},
      "output_result": {"id": "...", "title": "Buy groceries", "status": "pending"},
      "execution_status": "success",
      "error_message": null,
      "timestamp": "2026-02-10T10:30:45.123Z"
    }
  ]
}
```

### Test 2: List Tasks

```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Show me my tasks",
    "conversation_id": 1
  }'
```

### Test 3: Multi-turn Conversation

```bash
# First message
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"message": "Add a task to buy milk"}'

# Second message (agent remembers context)
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Mark it as complete",
    "conversation_id": 1
  }'
```

---

## Running Tests

### Unit Tests

```bash
# Run all unit tests
uv run pytest tests/unit/ -v

# Run specific test file
uv run pytest tests/unit/test_runner_factory.py -v
```

### Integration Tests (Requires API Keys)

```bash
# Set API keys in environment
export GROQ_API_KEY=your-groq-api-key
export OPENAI_API_KEY=your-openai-api-key

# Run integration tests
uv run pytest tests/integration/test_agent_orchestration_real.py -v
```

### Contract Tests

```bash
# Run contract tests (no API keys needed)
uv run pytest tests/contract/test_agent_response_contract.py -v
```

### Full Test Suite with Coverage

```bash
uv run pytest --cov=src --cov-report=html
```

---

## Configuration Options

### Agent Behavior

```env
# Temperature (0.0 = deterministic, 1.0 = creative)
AGENT_TEMPERATURE=0.1

# Maximum tokens in response
AGENT_MAX_TOKENS=500

# Maximum conversation history messages
AGENT_MAX_HISTORY_MESSAGES=20

# Request timeout (seconds)
AGENT_TIMEOUT_SECONDS=30
```

### Provider Configuration

```env
# Groq (Primary Provider)
GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_RATE_LIMIT_TPM=200000
GROQ_RATE_LIMIT_RPM=30
GROQ_RATE_LIMIT_RPD=1000

# OpenAI (Fallback Provider)
OPENAI_API_KEY=your-openai-api-key
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_FALLBACK_ENABLED=true
```

### Retry Configuration

```env
# Maximum retry attempts
RETRY_MAX_ATTEMPTS_LLM=3
RETRY_MAX_ATTEMPTS_TOOL=2

# Exponential backoff settings
RETRY_INITIAL_DELAY_MS=100
RETRY_MAX_DELAY_MS=5000
RETRY_BACKOFF_MULTIPLIER=2.0
```

---

## Natural Language Patterns

The AI agent understands various natural language patterns:

### Create Tasks
- "Add a task to buy groceries"
- "Create a task for calling mom"
- "I need to finish the report"
- "Remind me to pay bills"

### List Tasks
- "Show me my tasks"
- "What tasks do I have?"
- "List all my pending tasks"
- "What's on my todo list?"

### Update Tasks
- "Change the title of task X to..."
- "Update the description of..."
- "Rename the task about..."

### Complete Tasks
- "Mark task X as done"
- "Complete the task about groceries"
- "I finished the report task"

### Delete Tasks
- "Remove task X"
- "Delete the task about..."
- "Get rid of the groceries task"

---

## Troubleshooting

### Issue: "Module 'openai' not found"

**Solution**: Install dependencies
```bash
uv sync
```

### Issue: "GROQ_API_KEY not set"

**Solution**: Add API key to .env file
```env
GROQ_API_KEY=your-groq-api-key-here
```

### Issue: "Rate limit exceeded"

**Solution**: Enable OpenAI fallback
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_FALLBACK_ENABLED=true
```

### Issue: Integration tests are skipped

**Reason**: API keys not set in environment

**Solution**: Export API keys before running tests
```bash
export GROQ_API_KEY=your-groq-api-key
export OPENAI_API_KEY=your-openai-api-key
uv run pytest tests/integration/
```

### Issue: Agent responses are inconsistent

**Solution**: Lower temperature for more deterministic behavior
```env
AGENT_TEMPERATURE=0.1  # More deterministic
```

---

## Architecture Details

### Components

1. **RunnerFactory** (`src/agent/runner_factory.py`)
   - Creates OpenAI Agents SDK Agent instances
   - Configures Groq/OpenAI clients
   - Handles retry logic and fallback

2. **MCPAdapter** (`src/agent/mcp_adapter.py`)
   - Wraps MCP tools for OpenAI function calling format
   - Handles user_id context injection
   - Provides retry logic for tool execution

3. **AgentOrchestration** (`src/use_cases/agent_orchestration.py`)
   - Orchestrates agent execution flow
   - Manages conversation history
   - Persists messages and tool calls

4. **HistoryManager** (`src/agent/history_manager.py`)
   - Truncates conversation history to last 20 messages
   - Formats history for agent consumption
   - Adds system instructions

5. **RetryPolicy** (`src/agent/retry_policy.py`)
   - Implements exponential backoff
   - Classifies retryable vs non-retryable errors
   - Provides structured logging

### Data Flow

1. User sends message to `/users/{user_id}/chat`
2. AgentOrchestration loads conversation history from database
3. HistoryManager truncates history to last 20 messages
4. RunnerFactory creates Agent with MCP tools
5. Agent processes message and decides which tools to call
6. MCPAdapter executes tools with user_id context
7. Tool results are returned to agent
8. Agent generates response
9. Messages and tool calls are persisted to database
10. Response is returned to user with full transparency

---

## Performance Considerations

### Latency

- **Groq**: ~1-2 seconds per request (fast)
- **OpenAI**: ~2-4 seconds per request (slower but more reliable)
- **Database**: <100ms per query (Neon serverless)

### Rate Limits

**Groq Free Tier**:
- 200,000 tokens/minute
- 30 requests/minute
- 1,000 requests/day

**OpenAI (gpt-4o-mini)**:
- Pay-as-you-go pricing
- Higher rate limits
- More expensive than Groq

### Optimization Tips

1. **Use Groq as primary** - Faster and free tier available
2. **Enable OpenAI fallback** - Ensures reliability during rate limits
3. **Lower temperature** - Faster responses, more deterministic
4. **Limit max_tokens** - Faster responses, lower costs
5. **Truncate history** - Reduces context size, faster processing

---

## Security Notes

1. **Never commit API keys** - Use .env files (gitignored)
2. **Rotate secrets regularly** - Especially BETTER_AUTH_SECRET
3. **Use HTTPS in production** - Protect API keys in transit
4. **Validate user_id** - Ensure JWT token matches path user_id
5. **Rate limit endpoints** - Prevent abuse and cost overruns

---

## Next Steps

1. **Test with real users** - Gather feedback on natural language understanding
2. **Monitor costs** - Track Groq/OpenAI API usage
3. **Tune temperature** - Adjust for desired creativity vs consistency
4. **Add more tools** - Extend MCP adapter with additional capabilities
5. **Implement guardrails** - Add confirmation prompts for destructive actions

---

## Support

- **Documentation**: `/specs/009-phase-iii-openai-agents-sdk/`
- **API Docs**: http://localhost:8000/docs
- **Issues**: Report bugs in project issue tracker

---

## Summary

✅ **Implementation Complete**
- Real AI agent with OpenAI Agents SDK
- MCP tools integration (5 tools)
- Groq primary + OpenAI fallback
- Conversation history management
- Tool call transparency
- Retry logic with exponential backoff
- Comprehensive test coverage

🎯 **Ready for Production**
- All unit tests passing
- Integration tests written (require API keys)
- Contract tests passing
- Linting clean
- Documentation complete
