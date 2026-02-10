# Quickstart Guide: AI Agent Chat Endpoint

**Feature**: Phase III AI Orchestration Layer
**Branch**: `001-phase-iii-agent-chat-endpoint`
**Date**: 2026-02-09

## Overview

This guide will help you set up and test the AI agent chat endpoint locally. The endpoint provides a conversational interface for task management using OpenAI Agents SDK with MCP tool integration.

## Prerequisites

- Python 3.13+
- PostgreSQL database (Neon Serverless or local)
- Groq API key (free tier available)
- OpenAI API key (for fallback)
- Existing Phase-III backend running

## Environment Setup

### 1. Install Dependencies

```bash
cd Phase-III/backend

# Install new dependencies
uv add openai-agents-sdk groq openai

# Or using pip
pip install openai-agents-sdk groq openai
```

### 2. Configure Environment Variables

Add the following to your `.env` file:

```bash
# Groq Configuration (Primary Model)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
GROQ_MAX_TOKENS=200000
GROQ_MAX_REQUESTS_PER_MINUTE=30
GROQ_MAX_REQUESTS_PER_DAY=1000

# OpenAI Configuration (Fallback Model)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_FALLBACK_MODEL=gpt-4o-mini

# Agent Configuration
AGENT_MAX_RETRIES=3
AGENT_RETRY_BACKOFF_SECONDS=2
AGENT_TIMEOUT_SECONDS=30
AGENT_MAX_CONVERSATION_HISTORY=100

# Feature Flags
ENABLE_GROQ_FALLBACK=true
ENABLE_AGENT_GUARDRAILS=true
ENABLE_CONFIRMATION_FLOWS=true
```

### 3. Get API Keys

**Groq API Key** (Free Tier):
1. Visit https://console.groq.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to your `.env` file

**OpenAI API Key** (Fallback):
1. Visit https://platform.openai.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key to your `.env` file

## Database Setup

### 1. Run Database Migration

```bash
cd Phase-III/backend

# Generate migration
alembic revision --autogenerate -m "Add conversation and message tables"

# Review the generated migration in alembic/versions/

# Apply migration
alembic upgrade head
```

### 2. Verify Tables Created

```bash
# Connect to your database
psql $DATABASE_URL

# Check tables
\dt

# Should see:
# - conversations
# - messages

# Check indexes
\di

# Should see:
# - idx_conversations_user_id
# - idx_messages_conversation_created
```

## Running the Server

### 1. Start the Backend

```bash
cd Phase-III/backend

# Using uvicorn directly
uvicorn src.main:app --reload --port 8000

# Or using the startup script
python main.py
```

### 2. Verify Server is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Should return:
# {"status": "healthy"}
```

## Testing the Chat Endpoint

### 1. Authenticate and Get JWT Token

```bash
# Login to get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "your_password"
  }'

# Save the token from response
export JWT_TOKEN="your_jwt_token_here"
export USER_ID="your_user_id_here"
```

### 2. Start a New Conversation

```bash
# Create a task via chat
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy groceries"
  }'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "I've created a task for you: 'Buy groceries'. The task is now pending.",
#   "tool_calls": [
#     {
#       "tool_name": "add_task",
#       "input_parameters": {
#         "title": "Buy groceries",
#         "description": ""
#       },
#       "output_result": {
#         "id": 123,
#         "title": "Buy groceries",
#         "status": "pending",
#         "version": 1
#       },
#       "execution_status": "success",
#       "error_message": null,
#       "timestamp": "2026-02-09T18:30:00Z"
#     }
#   ]
# }

# Save the conversation_id for next request
export CONVERSATION_ID=1
```

### 3. Resume Conversation

```bash
# List tasks in the same conversation
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Show me my tasks"
  }'
```

### 4. Test Other Operations

**Update Task**:
```bash
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Rename the groceries task to Buy organic groceries"
  }'
```

**Complete Task** (with confirmation):
```bash
# First request (agent asks for confirmation)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Mark the groceries task as done"
  }'

# Second request (user confirms)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Yes, complete it"
  }'
```

**Delete Task** (with confirmation):
```bash
# First request (agent asks for confirmation)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Delete the groceries task"
  }'

# Second request (user confirms)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": '$CONVERSATION_ID',
    "message": "Yes, delete it"
  }'
```

## Verifying Tool Call Transparency

### Check Database Records

```sql
-- View conversation
SELECT * FROM conversations WHERE id = 1;

-- View messages with tool calls
SELECT
  id,
  role,
  content,
  tool_calls::jsonb,
  created_at
FROM messages
WHERE conversation_id = 1
ORDER BY created_at ASC;
```

### Verify Stateless Design

```bash
# 1. Send a message
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": '$CONVERSATION_ID', "message": "Create task: Test stateless"}'

# 2. Restart the server
# Stop the server (Ctrl+C)
# Start it again
uvicorn src.main:app --reload --port 8000

# 3. Resume conversation (should work without any in-memory state)
curl -X POST http://localhost:8000/api/$USER_ID/chat \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": '$CONVERSATION_ID', "message": "Show me my tasks"}'

# Should return all tasks including the one created before restart
```

## Running Tests

### Unit Tests

```bash
cd Phase-III/backend

# Run agent orchestration tests
pytest tests/unit/test_agent_orchestration.py -v

# Run with coverage
pytest tests/unit/test_agent_orchestration.py --cov=src.agent --cov-report=html
```

### Integration Tests

```bash
# Run chat endpoint integration tests
pytest tests/integration/test_chat_endpoint.py -v

# Run all integration tests
pytest tests/integration/ -v
```

### Contract Tests

```bash
# Run contract tests
pytest tests/contract/test_chat_contract.py -v
```

### End-to-End Tests

```bash
# Run E2E tests (requires running server)
pytest tests/e2e/test_chat_e2e.py -v
```

## Troubleshooting

### Issue: "Groq rate limit exceeded"

**Solution**: The system should automatically fallback to OpenAI. Check logs:
```bash
# Check logs for fallback message
tail -f fastapi_server.log | grep "fallback"
```

If fallback isn't working, verify `ENABLE_GROQ_FALLBACK=true` in `.env`.

### Issue: "Conversation not found"

**Solution**: Verify conversation_id exists and belongs to authenticated user:
```sql
SELECT * FROM conversations WHERE id = <conversation_id> AND user_id = '<user_id>';
```

### Issue: "Tool call failed"

**Solution**: Check MCP server logs and verify tools are working:
```bash
# Test MCP tools directly
python test_mcp_tools.py
```

### Issue: "Agent not responding"

**Solution**: Check agent configuration and model availability:
```bash
# Test Groq API directly
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"

# Test OpenAI API
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Issue: "Database connection error"

**Solution**: Verify database connection string:
```bash
# Test database connection
python -c "from src.database import engine; print(engine.url)"
```

## Monitoring and Debugging

### View Agent Logs

```bash
# Tail logs in real-time
tail -f fastapi_server.log

# Filter for agent-related logs
tail -f fastapi_server.log | grep "agent"

# Filter for tool calls
tail -f fastapi_server.log | grep "tool_call"
```

### Check Tool Call Metrics

```bash
# Query tool call statistics
psql $DATABASE_URL -c "
SELECT
  jsonb_array_elements(tool_calls::jsonb)->>'tool_name' as tool_name,
  COUNT(*) as call_count
FROM messages
WHERE tool_calls IS NOT NULL
GROUP BY tool_name
ORDER BY call_count DESC;
"
```

### Monitor Conversation Activity

```bash
# Active conversations in last hour
psql $DATABASE_URL -c "
SELECT
  COUNT(*) as active_conversations,
  COUNT(DISTINCT user_id) as unique_users
FROM conversations
WHERE updated_at > NOW() - INTERVAL '1 hour';
"
```

## Next Steps

1. **Run Integration Tests**: Verify all components work together
2. **Test Edge Cases**: Try ambiguous requests, invalid inputs, concurrent requests
3. **Performance Testing**: Test with multiple concurrent conversations
4. **Frontend Integration**: Connect Next.js frontend to chat endpoint
5. **Production Deployment**: Deploy to Vercel/Heroku with production database

## Additional Resources

- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/docs/develop/build-server)
- [Groq API Documentation](https://console.groq.com/docs)
- [Feature Specification](./spec.md)
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
