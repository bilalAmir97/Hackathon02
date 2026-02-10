# Quickstart Guide: Phase-III AI Chat Interface

**Feature**: Phase-III AI Chat Interface with Streaming
**Date**: 2026-02-10
**Audience**: Developers setting up local development environment

## Overview

This guide walks you through setting up and running the Phase-III AI Chat Interface locally. The feature consists of a FastAPI backend with streaming support and a Next.js frontend with custom chat UI components.

## Prerequisites

### Required Software
- **Python**: 3.13+ (backend)
- **Node.js**: 18+ (frontend)
- **PostgreSQL**: 14+ (database) - or Neon Serverless PostgreSQL account
- **Git**: For version control
- **UV**: Python package manager (install via `pip install uv`)

### Required Accounts
- **Neon**: Serverless PostgreSQL database (https://neon.tech)
- **OpenAI**: API key for OpenAI Agents SDK (https://platform.openai.com)
- **Better Auth**: Already configured in existing project

### Knowledge Requirements
- Basic understanding of FastAPI and Next.js
- Familiarity with JWT authentication
- Understanding of streaming responses

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd Phase-III/backend
```

### 2. Install Dependencies

```bash
# Install Python dependencies using UV
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### 3. Configure Environment Variables

Create or update `.env` file:

```bash
# Database
DATABASE_URL=postgresql://user:password@host/database?sslmode=require

# OpenAI
OPENAI_API_KEY=sk-...

# Authentication
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Agent Configuration
AGENT_MAX_HISTORY_MESSAGES=100
AGENT_MODEL=gpt-4
AGENT_TEMPERATURE=0.7

# Server
PORT=8000
HOST=0.0.0.0
```

### 4. Run Database Migrations

```bash
# Apply existing migrations (conversations and messages tables)
alembic upgrade head

# Verify migrations
alembic current
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade -> 001_add_conversations_table
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002_add_messages_table
```

### 5. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the startup script
python -m src.main
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6. Verify Backend Health

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy"}
```

### 7. Test Existing Chat Endpoint (Non-Streaming)

```bash
# Get JWT token first (use existing auth endpoint)
TOKEN="your-jwt-token-here"
USER_ID="your-user-id-here"

# Send test message
curl -X POST http://localhost:8000/api/${USER_ID}/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"message": "Hello, create a test task"}'

# Expected response:
# {
#   "conversation_id": 1,
#   "response": "I'll create that task for you.",
#   "tool_calls": [...]
# }
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd Phase-III/frontend
```

### 2. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Or using yarn
yarn install
```

### 3. Configure Environment Variables

Create or update `.env.local` file:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth (already configured)
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000

# Feature Flags (optional)
NEXT_PUBLIC_ENABLE_CHAT=true
```

### 4. Start Frontend Development Server

```bash
# Development mode with hot reload
npm run dev

# Or using yarn
yarn dev
```

Expected output:
```
   ▲ Next.js 16.0.10
   - Local:        http://localhost:3000
   - Network:      http://192.168.1.x:3000

 ✓ Ready in 2.3s
```

### 5. Verify Frontend

Open browser and navigate to:
- **Landing Page**: http://localhost:3000
- **Dashboard**: http://localhost:3000/dashboard (requires login)
- **Chat Interface**: http://localhost:3000/chat (to be implemented)

---

## Testing the Chat Interface

### 1. Backend Streaming Endpoint Test

Once the streaming endpoint is implemented, test with:

```bash
# Stream chat response
curl -N -X POST http://localhost:8000/api/${USER_ID}/chat/stream \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -d '{"message": "Create a task to buy groceries"}'

# Expected output (NDJSON stream):
# {"type":"token","content":"I'll"}
# {"type":"token","content":" create"}
# {"type":"token","content":" that"}
# {"type":"tool_call","data":{"tool_name":"add_task","status":"pending"}}
# {"type":"tool_call","data":{"tool_name":"add_task","status":"success",...}}
# {"type":"done","conversation_id":1}
```

### 2. Conversation List Test

```bash
# Get user's conversations
curl http://localhost:8000/api/${USER_ID}/conversations \
  -H "Authorization: Bearer ${TOKEN}"

# Expected response:
# {
#   "conversations": [
#     {
#       "id": 1,
#       "created_at": "2026-02-10T10:00:00Z",
#       "updated_at": "2026-02-10T10:30:00Z",
#       "preview": "Create a task to buy groceries",
#       "message_count": 8
#     }
#   ]
# }
```

### 3. Message History Test

```bash
# Get conversation messages
curl http://localhost:8000/api/${USER_ID}/conversations/1/messages \
  -H "Authorization: Bearer ${TOKEN}"

# Expected response:
# {
#   "conversation_id": 1,
#   "messages": [
#     {
#       "id": 1,
#       "role": "user",
#       "content": "Create a task to buy groceries",
#       "tool_calls": null,
#       "created_at": "2026-02-10T10:00:00Z"
#     },
#     {
#       "id": 2,
#       "role": "assistant",
#       "content": "I'll create that task for you.",
#       "tool_calls": [...],
#       "created_at": "2026-02-10T10:00:05Z"
#     }
#   ]
# }
```

### 4. Frontend Chat UI Test

Once implemented, test the chat interface:

1. **Login**: Navigate to http://localhost:3000 and log in
2. **Access Chat**: Navigate to http://localhost:3000/chat
3. **Send Message**: Type "Create a task to buy groceries" and press send
4. **Verify Streaming**: Watch response appear word-by-word
5. **Verify Tool Calls**: See inline indicators for tool execution
6. **Verify Persistence**: Refresh page and verify conversation persists
7. **Create New Chat**: Click "New Chat" button
8. **Switch Conversations**: Select different conversation from sidebar

---

## Running Tests

### Backend Tests

```bash
cd Phase-III/backend

# Run all tests
pytest

# Run specific test categories
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/contract/          # Contract tests

# Run with coverage
pytest --cov=src --cov-report=html

# Run streaming tests (once implemented)
pytest tests/integration/test_chat_streaming.py -v
```

### Frontend Tests

```bash
cd Phase-III/frontend

# Run all tests
npm test

# Run specific test suites
npm test -- components/chat     # Chat component tests
npm test -- lib/api             # API client tests

# Run E2E tests
npm run test:e2e

# Run with coverage
npm test -- --coverage
```

---

## Troubleshooting

### Backend Issues

**Issue**: Database connection error
```
Solution:
1. Verify DATABASE_URL in .env
2. Check Neon database is running
3. Verify network connectivity
4. Check SSL mode is set to 'require'
```

**Issue**: OpenAI API key error
```
Solution:
1. Verify OPENAI_API_KEY in .env
2. Check API key is valid on OpenAI platform
3. Verify API key has sufficient credits
```

**Issue**: JWT authentication fails
```
Solution:
1. Verify BETTER_AUTH_SECRET matches frontend
2. Check JWT_SECRET is set
3. Verify token is not expired
4. Check Authorization header format: "Bearer <token>"
```

**Issue**: Streaming not working
```
Solution:
1. Verify streaming endpoint is implemented
2. Check NDJSON format is correct
3. Test with curl -N flag for no buffering
4. Check browser supports ReadableStream API
```

### Frontend Issues

**Issue**: Cannot connect to backend
```
Solution:
1. Verify NEXT_PUBLIC_API_URL in .env.local
2. Check backend is running on correct port
3. Verify CORS is configured in backend
4. Check network connectivity
```

**Issue**: Authentication not working
```
Solution:
1. Verify Better Auth is configured
2. Check BETTER_AUTH_SECRET matches backend
3. Clear browser cookies and try again
4. Check JWT token is being sent in requests
```

**Issue**: Streaming response not rendering
```
Solution:
1. Check browser console for errors
2. Verify fetch streaming is implemented correctly
3. Check NDJSON parsing logic
4. Test with browser DevTools Network tab
```

---

## Development Workflow

### 1. Start Both Servers

```bash
# Terminal 1: Backend
cd Phase-III/backend
source .venv/bin/activate
uvicorn src.main:app --reload

# Terminal 2: Frontend
cd Phase-III/frontend
npm run dev
```

### 2. Make Changes

- **Backend**: Edit files in `Phase-III/backend/src/`
- **Frontend**: Edit files in `Phase-III/frontend/src/`
- Both servers auto-reload on file changes

### 3. Test Changes

- **Backend**: Run `pytest` after changes
- **Frontend**: Run `npm test` after changes
- **E2E**: Test complete flow in browser

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat(chat): implement streaming endpoint"

# Push to feature branch
git push origin 001-phase-iii-chat-interface
```

---

## Useful Commands

### Backend

```bash
# Check Python version
python --version

# List installed packages
uv pip list

# Run linter
ruff check src/

# Format code
ruff format src/

# Generate migration
alembic revision --autogenerate -m "description"

# View logs
tail -f logs/app.log
```

### Frontend

```bash
# Check Node version
node --version

# List installed packages
npm list --depth=0

# Run linter
npm run lint

# Format code
npm run format

# Build for production
npm run build

# Analyze bundle size
npm run analyze
```

---

## Next Steps

After local setup is complete:

1. **Implement Streaming Endpoint**: Add streaming support to chat endpoint
2. **Implement Conversation Endpoints**: Add list and messages endpoints
3. **Build Chat UI Components**: Create React components for chat interface
4. **Integrate Streaming**: Connect frontend to streaming backend
5. **Add Tool Transparency**: Display tool calls inline with messages
6. **Test E2E Flow**: Verify complete user journey
7. **Deploy to Staging**: Test in staging environment
8. **Deploy to Production**: Release to production

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs
- **OpenAI Agents SDK**: https://openai.github.io/openai-agents-python/
- **MCP Documentation**: https://modelcontextprotocol.io/docs
- **Better Auth Docs**: https://www.better-auth.com/docs
- **Neon Docs**: https://neon.tech/docs

---

## Support

For issues or questions:
1. Check this quickstart guide
2. Review existing documentation in `specs/001-phase-iii-chat-interface/`
3. Check backend logs: `Phase-III/backend/logs/`
4. Check browser console for frontend errors
5. Review API contracts in `contracts/` directory
