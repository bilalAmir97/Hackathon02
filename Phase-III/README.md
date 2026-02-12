# Phase III: AI-Powered Todo Application with Conversational Interface

**Status**: ✅ Complete (AI Chat Integration Implemented)
**Last Updated**: 2026-02-11
**Branch**: `001-todo`

## Overview

Phase III extends Phase II by adding an AI-powered conversational interface for task management. Users can interact with an intelligent assistant through natural language to create, update, complete, and delete tasks without navigating through traditional UI forms.

### Key Features

- ✅ **AI Chat Assistant**: Natural language task management through conversational interface
- ✅ **MCP Tools Integration**: Model Context Protocol tools for structured task operations
- ✅ **Real-time Streaming**: Token-by-token response streaming for better UX
- ✅ **Tool Call Transparency**: Users see exactly what actions the AI is performing
- ✅ **Conversation Persistence**: Chat history stored and retrieved across sessions
- ✅ **Multi-Provider Support**: Groq (primary) and OpenAI (fallback) for reliability
- ✅ **User Authentication**: Inherited secure JWT-based authentication from Phase II
- ✅ **Chat Widget**: Integrated floating chat widget accessible from dashboard

## Architecture

### Technology Stack

**Backend**:
- **Framework**: FastAPI (Python 3.13+)
- **Database**: Neon Serverless PostgreSQL
- **ORM**: SQLModel with Alembic migrations
- **AI Integration**: OpenAI Agents SDK
- **LLM Providers**:
  - Primary: Groq (openai/gpt-oss-20b)
  - Fallback: OpenAI (gpt-4o-mini)
- **Authentication**: PyJWT for token verification
- **Testing**: pytest with async support

**Frontend**:
- **Framework**: Next.js 15.5.12 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Authentication**: Better Auth with JWT plugin
- **UI Components**: Custom Soft Dark theme with glassmorphism

**AI Agent Architecture**:
- **Agent Factory**: Creates and configures AI agents with MCP tools
- **Runner Factory**: Manages OpenAI ChatCompletions with retry logic
- **MCP Adapter**: Converts MCP tools to OpenAI function calling format
- **Agent Orchestration**: Coordinates agent execution, tool calls, and persistence
- **History Manager**: Manages conversation history with truncation

### Project Structure

```
Phase-III/
├── backend/
│   ├── src/
│   │   ├── agent/
│   │   │   ├── agent_factory.py      # AI agent creation
│   │   │   ├── runner_factory.py     # OpenAI client management
│   │   │   ├── mcp_adapter.py        # MCP tool integration
│   │   │   ├── instructions.py       # System prompt
│   │   │   ├── history_manager.py    # Conversation truncation
│   │   │   └── guardrails.py         # Confirmation management
│   │   ├── mcp/
│   │   │   └── tools/
│   │   │       ├── add_task.py       # Create task tool
│   │   │       ├── list_tasks.py     # List tasks tool
│   │   │       ├── update_task.py    # Update task tool
│   │   │       ├── complete_task.py  # Complete task tool
│   │   │       └── delete_task.py    # Delete task tool
│   │   ├── use_cases/
│   │   │   └── agent_orchestration.py # Agent workflow coordination
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── chat.py           # Chat endpoint
│   │   │       ├── chat_stream.py    # Streaming chat endpoint
│   │   │       └── conversations.py  # Conversation management
│   │   └── domain/
│   │       └── models.py             # Database models (+ Conversation, Message)
│   └── tests/
│       └── integration/              # E2E tests
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── dashboard/            # Main dashboard with chat widget
    │   │   ├── login/                # Login page
    │   │   └── register/             # Registration page
    │   ├── components/
    │   │   ├── chat/
    │   │   │   ├── ChatWidget.tsx    # Floating chat widget
    │   │   │   ├── ChatInterface.tsx # Chat UI
    │   │   │   ├── MessageList.tsx   # Message display
    │   │   │   ├── ChatInput.tsx     # Message input
    │   │   │   └── ToolCallIndicator.tsx # Tool execution display
    │   │   ├── navigation/
    │   │   │   ├── Sidebar.tsx       # Main navigation
    │   │   │   └── TopNavigation.tsx # Top bar
    │   │   └── tasks/
    │   │       └── TaskCard.tsx      # Task display component
    │   └── hooks/
    │       ├── useAuth.tsx           # Authentication hook
    │       └── useChat.tsx           # Chat management hook
    └── package.json
```

## AI Chat Features

### Conversational Task Management

Users can manage tasks through natural language:

**Examples**:
- "Add a task to buy groceries"
- "Mark the medicine task as complete"
- "Delete the task named bro"
- "Show me all my pending tasks"
- "Update the grocery task description to include milk and eggs"

### MCP Tools

The AI assistant has access to 5 MCP tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `add_task` | Create a new task | `title`, `description` (optional) |
| `list_tasks` | List user's tasks | `status` (optional: pending/completed/all) |
| `update_task` | Update existing task | `task_id`, `title`, `description` |
| `complete_task` | Toggle task completion | `task_id` |
| `delete_task` | Delete a task | `task_id` |

### Tool Call Transparency

Every tool execution is displayed to the user with:
- Tool name
- Input parameters
- Output result
- Execution status (success/error)
- Timestamp

### Conversation Flow

```
User: "Add a task to buy groceries"
  ↓
AI Agent: Processes intent
  ↓
Tool Call: add_task(title="buy groceries")
  ↓
Database: Creates task
  ↓
AI Response: "I've created a task for you: 'buy groceries'"
  ↓
User sees: Message + Tool execution details
```

## API Endpoints

### Chat Endpoints (Protected)

All chat endpoints require `Authorization: Bearer <token>` header.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | `/api/{user_id}/chat` | Send message to AI | `{ conversation_id, response, tool_calls }` |
| POST | `/api/{user_id}/chat/stream` | Stream AI response | Server-Sent Events |
| GET | `/api/{user_id}/conversations` | List conversations | `[{ id, created_at, ... }]` |
| GET | `/api/{user_id}/conversations/{id}/messages` | Get conversation history | `[{ role, content, ... }]` |
| DELETE | `/api/{user_id}/conversations/{id}` | Delete conversation | `{ message }` |

### Authentication & Task Endpoints

See Phase II documentation for authentication and task management endpoints.

## Setup Instructions

### Prerequisites

- Node.js 18.x+ (for Next.js 15)
- Python 3.13+ (for FastAPI)
- UV package manager
- Neon PostgreSQL account
- Groq API key (primary LLM provider)
- OpenAI API key (optional fallback)

### Environment Variables

**Backend (`.env`)**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/database

# Authentication
BETTER_AUTH_SECRET=<32+ character secret>
FRONTEND_URL=http://localhost:3000

# AI Providers
GROQ_API_KEY=<your-groq-api-key>
GROQ_MODEL=openai/gpt-oss-20b
OPENAI_API_KEY=<your-openai-api-key>  # Optional fallback
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_FALLBACK_ENABLED=true

# Agent Configuration
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000
AGENT_MAX_HISTORY_MESSAGES=20

# CORS
CORS_ALLOW_CREDENTIALS=true
CORS_MAX_AGE=3600
```

**Frontend (`.env.local`)**:
```bash
BETTER_AUTH_SECRET=<same as backend>
BETTER_AUTH_URL=http://localhost:3000
DATABASE_URL=<same as backend>
NEXT_PUBLIC_API_URL=http://localhost:8001
```

### Running Locally

**Terminal 1 - Backend**:
```bash
cd Phase-III/backend
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend**:
```bash
cd Phase-III/frontend
npm run dev
```

**Access**:
- Backend API: http://localhost:8001
- API Documentation: http://localhost:8001/docs
- Frontend: http://localhost:3000

## Testing

### Backend Tests

```bash
cd Phase-III/backend

# Run all tests
uv run pytest

# Run integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Manual Testing

**Test AI Chat Flow**:
```bash
# 1. Register and login to get token
TOKEN="<your-jwt-token>"
USER_ID="<your-user-id>"

# 2. Send chat message
curl -X POST http://localhost:8001/api/${USER_ID}/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'

# 3. List conversations
curl http://localhost:8001/api/${USER_ID}/conversations \
  -H "Authorization: Bearer ${TOKEN}"

# 4. Get conversation messages
curl http://localhost:8001/api/${USER_ID}/conversations/1/messages \
  -H "Authorization: Bearer ${TOKEN}"
```

## Deployment

### Production Deployment

**Frontend**: Deployed on Netlify
- Production URL: https://rainbow-froyo-cda32b.netlify.app
- Auto-deploys from `001-todo` branch

**Backend**: Requires deployment to Railway/Render/Fly.io

**Environment Variables** (Production):
```bash
# Backend
DATABASE_URL=<neon-production-url>
BETTER_AUTH_SECRET=<strong-secret-32+chars>
FRONTEND_URL=https://rainbow-froyo-cda32b.netlify.app
GROQ_API_KEY=<production-groq-key>
OPENAI_API_KEY=<production-openai-key>
APP_ENV=production
LOG_LEVEL=INFO

# Frontend
BETTER_AUTH_SECRET=<same-as-backend>
BETTER_AUTH_URL=https://rainbow-froyo-cda32b.netlify.app
DATABASE_URL=<neon-production-url>
NEXT_PUBLIC_API_URL=<backend-production-url>
```

### Database Migrations

```bash
cd Phase-III/backend
DATABASE_URL=<production-url> uv run alembic upgrade head
```

## Recent Changes

### 2026-02-11
- ✅ Removed AI Chat navigation from sidebar (chat accessible via widget only)
- ✅ Removed non-functional search bar from top navigation
- ✅ Restored to working state after glassmorphism UI issues
- ✅ Deployed to production

### Key Implementation Details
- AI chat operations (add, update, delete, complete tasks) fully functional
- Chat widget integrated into dashboard with floating UI
- Conversation history persisted across sessions
- Tool call transparency shows all AI actions to users

## Troubleshooting

### Common Issues

**Issue**: AI responses are empty or incomplete
**Solution**: Check that `GROQ_API_KEY` is valid and has sufficient credits

**Issue**: Tool calls fail with "User not found"
**Solution**: Ensure JWT token is valid and user_id matches token claims

**Issue**: Chat widget not appearing
**Solution**: Verify you're logged in and on the dashboard page

**Issue**: "Rate limit exceeded" errors
**Solution**: Fallback to OpenAI is automatic if `OPENAI_FALLBACK_ENABLED=true`

**Issue**: Conversation history not loading
**Solution**: Run database migrations to ensure `conversations` and `messages` tables exist

## Development Workflow

### Making Changes

1. **Backend AI changes**: Modify files in `src/agent/` or `src/mcp/tools/`
2. **Frontend chat UI**: Modify files in `src/components/chat/`
3. **System prompt**: Edit `src/agent/instructions.py`
4. **Add new MCP tool**: Create tool in `src/mcp/tools/` and register in `mcp_adapter.py`

### Testing AI Behavior

```bash
# Test with different prompts
curl -X POST http://localhost:8001/api/${USER_ID}/chat \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Your test prompt here"}'
```

## Resources

- **API Documentation**: http://localhost:8001/docs (when backend running)
- **OpenAI Agents SDK**: https://github.com/openai/openai-agents-sdk
- **Groq Documentation**: https://console.groq.com/docs
- **MCP Protocol**: https://modelcontextprotocol.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

## Contributing

When adding new features:

1. Follow existing code patterns and architecture
2. Add MCP tools for new AI capabilities
3. Update system instructions if needed
4. Add integration tests for new flows
5. Update this README with new features
6. Test locally before deploying

## License

[Your License Here]

---

**Questions or Issues?** Check the troubleshooting section or review Phase II documentation for authentication setup.
