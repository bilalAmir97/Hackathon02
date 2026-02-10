# Implementation Plan: Phase-III AI Chat Interface with Streaming

**Branch**: `001-phase-iii-chat-interface` | **Date**: 2026-02-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-iii-chat-interface/spec.md`

## Summary

Implement a modern, minimal, professional AI chat UI using OpenAI ChatKit that integrates with the existing stateless FastAPI agent backend. The frontend will act as a thin client, consuming streaming responses from the backend and displaying tool call transparency inline with assistant messages. The backend already has conversation persistence, agent orchestration, and MCP tool integration - this plan focuses on adding streaming support and building the complete frontend chat experience.

**Core Architecture Principle**: Thin client - all intelligence resides in the backend agent layer. Frontend must never infer agent logic, simulate tool calls, or mutate task data.

## Technical Context

**Language/Version**:
- Backend: Python 3.13+ (existing)
- Frontend: TypeScript 5.x with Next.js 16+ App Router (existing)

**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK, FastMCP, SQLModel, Neon PostgreSQL (existing)
- Frontend: Next.js 16+, React 19.2.1, Custom React Components, Better Auth (existing), Tailwind CSS (existing)

**Storage**:
- Neon Serverless PostgreSQL (existing)
- Conversations table (existing)
- Messages table with tool_calls JSONB (existing)

**Testing**:
- Backend: pytest, pytest-asyncio (existing)
- Frontend: Jest, React Testing Library (existing)
- E2E: Playwright or Cypress

**Target Platform**:
- Backend: Linux server (existing deployment)
- Frontend: Vercel (existing deployment)
- Browser: Modern browsers (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Streaming latency: <500ms to first token
- Token rendering: 20+ tokens per second
- Conversation list load: <1 second for 100 conversations
- UI responsiveness: 60fps during streaming

**Constraints**:
- Backend must remain stateless (existing architecture)
- Frontend must not store authoritative state
- All API requests require JWT authentication (existing)
- No direct MCP tool calls from frontend
- Must support mobile devices (320px minimum width)

**Scale/Scope**:
- Multi-user system (existing)
- Unlimited conversations per user
- Up to 100 messages per conversation (configurable)
- Support for 1000+ concurrent users

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Phase Governance ✅ PASS
- **Phase III Requirements**: AI-powered chatbot with natural language interface
- **Feature Level**: Basic Level via natural language (add, list, update, delete, complete tasks)
- **Technology Stack**: Custom React Components with Tailwind CSS (frontend), OpenAI Agents SDK (backend - existing), MCP tools (existing)
- **No Future-Phase Leakage**: No Intermediate or Advanced features (priorities, tags, recurring tasks, reminders)

### Stateless Services ✅ PASS
- **Backend Architecture**: Already stateless (verified in `agent_orchestration.py`)
- **Conversation Persistence**: Database-persisted (Conversation and Message models exist)
- **No In-Memory State**: All state in PostgreSQL
- **Request Context**: Passed explicitly via JWT and conversation_id

### Clean Architecture ✅ PASS
- **Existing Structure**:
  - Domain: `src/domain/models/` (Conversation, Message, Task, User)
  - Use Cases: `src/use_cases/` (agent_orchestration, auth_operations)
  - Interface Adapters: `src/api/routes/` (chat, tasks, auth)
  - Infrastructure: `src/database.py`, `src/mcp/`, `src/agent/`
- **Dependency Direction**: Inner layers don't depend on outer layers ✅

### Contract-First Design ✅ PASS
- **Existing Contracts**:
  - REST API: `POST /api/{user_id}/chat` (existing)
  - MCP Tools: add_task, list_tasks, update_task, delete_task, complete_task (existing)
- **New Contracts Needed**:
  - Streaming endpoint contract (SSE or fetch streaming)
  - Frontend API client interface
  - ChatResponse schema with streaming support

### Test-Driven Development ⚠️ REQUIRES ATTENTION
- **Existing Tests**: Backend has unit, integration, and contract tests
- **Missing Tests**: Frontend chat UI tests, streaming tests, E2E chat flow tests
- **Action Required**: Write tests before implementation in Phase 2 (tasks.md)

### Security & Compliance ✅ PASS
- **JWT Authentication**: Already enforced on all endpoints (existing)
- **User Isolation**: All queries filtered by user_id (existing)
- **MCP Tools**: Include user_id for access control (existing)
- **No Secrets in Code**: Environment variables used (existing)

### Observability & Monitoring ✅ PASS
- **Structured Logging**: Already implemented in agent_orchestration.py
- **Health Checks**: `/health` endpoint exists
- **Metrics**: RED method for endpoints (existing)
- **Correlation IDs**: Conversation_id used for tracing

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-iii-chat-interface/
├── spec.md                    # Feature specification (existing)
├── plan.md                    # This file
├── research.md                # Phase 0 output (to be created)
├── data-model.md              # Phase 1 output (to be created)
├── quickstart.md              # Phase 1 output (to be created)
├── contracts/                 # Phase 1 output (to be created)
│   ├── streaming-api.yaml     # SSE streaming contract
│   └── chat-client.ts         # Frontend API client interface
└── tasks.md                   # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

**Backend Structure** (existing, minimal additions):
```text
Phase-III/backend/
├── src/
│   ├── agent/                 # Existing: agent_factory, runner_factory, mcp_adapter
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py        # Existing: POST /api/{user_id}/chat
│   │   │   └── chat_stream.py # NEW: Streaming endpoint
│   │   └── schemas/
│   │       └── chat_schemas.py # Existing: ChatRequest, ChatResponse
│   ├── domain/
│   │   └── models/
│   │       ├── conversation.py # Existing
│   │       └── message.py      # Existing
│   ├── use_cases/
│   │   └── agent_orchestration.py # Existing: process_message()
│   └── mcp/                   # Existing: MCP tools
└── tests/
    ├── integration/
    │   └── test_chat_streaming.py # NEW: Streaming tests
    └── contract/
        └── test_streaming_contract.py # NEW: Contract tests
```

**Frontend Structure** (new chat UI):
```text
Phase-III/frontend/
├── src/
│   ├── app/
│   │   ├── chat/              # NEW: Chat page route
│   │   │   ├── page.tsx       # Main chat interface
│   │   │   └── layout.tsx     # Chat-specific layout
│   │   └── api/               # Existing: API routes
│   ├── components/
│   │   ├── chat/              # NEW: Chat UI components
│   │   │   ├── ChatInterface.tsx      # Main chat container
│   │   │   ├── MessageList.tsx        # Message display with streaming
│   │   │   ├── MessageBubble.tsx      # Individual message component
│   │   │   ├── ToolCallIndicator.tsx  # Tool transparency display
│   │   │   ├── ChatInput.tsx          # Message input with send button
│   │   │   ├── ConversationSidebar.tsx # Conversation list
│   │   │   ├── ConversationItem.tsx   # Single conversation preview
│   │   │   ├── TypingIndicator.tsx    # Animated typing indicator
│   │   │   └── ErrorRetry.tsx         # Error display with retry
│   │   └── providers/         # Existing: auth, theme providers
│   ├── lib/
│   │   ├── api/
│   │   │   ├── chat-client.ts # NEW: Authenticated chat API client
│   │   │   └── streaming.ts   # NEW: SSE streaming handler
│   │   └── hooks/
│   │       ├── useChat.ts     # NEW: Chat state management hook
│   │       ├── useStreaming.ts # NEW: Streaming response hook
│   │       └── useConversations.ts # NEW: Conversation list hook
│   └── types/
│       └── chat.ts            # NEW: TypeScript types for chat
└── tests/
    ├── components/
    │   └── chat/              # NEW: Component tests
    └── e2e/
        └── chat-flow.spec.ts  # NEW: E2E chat tests
```

**Structure Decision**: Web application structure with separate backend and frontend directories. Backend already has clean architecture with domain, use cases, and infrastructure layers. Frontend follows Next.js 16 App Router conventions with components, lib, and types directories. New chat UI will be added as a new route under `src/app/chat/` with dedicated components in `src/components/chat/`.

## Complexity Tracking

> **No violations detected. All constitution principles are satisfied.**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

## Phase 0: Research & Discovery

**Objective**: Resolve all technical unknowns and validate technology choices before design phase.

### Research Tasks

#### R1: OpenAI ChatKit Compatibility with Next.js 16 App Router
**Question**: Is OpenAI ChatKit compatible with Next.js 16 App Router and React Server Components?

**Research Approach**:
1. Review OpenAI ChatKit documentation and examples
2. Check for Next.js 16 compatibility notes
3. Identify if ChatKit requires client-side rendering
4. Determine if ChatKit components can be used with App Router
5. Find alternative chat UI libraries if ChatKit is incompatible

**Decision Criteria**:
- Must work with Next.js 16 App Router
- Must support streaming responses
- Must be actively maintained
- Must have TypeScript support

**Fallback**: If ChatKit is incompatible, use custom React components with Tailwind CSS

#### R2: FastAPI Streaming Implementation (SSE vs Fetch Streaming)
**Question**: What's the best approach for streaming responses from FastAPI to Next.js frontend?

**Research Approach**:
1. Compare Server-Sent Events (SSE) vs Fetch API streaming
2. Review FastAPI streaming response patterns
3. Check Next.js fetch API streaming support
4. Evaluate browser compatibility for both approaches
5. Assess error handling and reconnection strategies

**Options**:
- **Option A: Server-Sent Events (SSE)**
  - Pros: Built-in reconnection, event-based, widely supported
  - Cons: Unidirectional, requires EventSource API

- **Option B: Fetch API Streaming**
  - Pros: Bidirectional, modern, works with fetch
  - Cons: Manual reconnection, more complex error handling

**Decision Criteria**:
- Browser compatibility (Chrome, Firefox, Safari, Edge)
- Error handling and reconnection support
- Integration with existing JWT authentication
- Ease of implementation in FastAPI and Next.js

#### R3: Client vs Server State Boundary
**Question**: How to enforce thin client architecture and prevent state duplication?

**Research Approach**:
1. Review React state management patterns for chat UIs
2. Identify what state belongs on server vs client
3. Design state synchronization strategy
4. Plan optimistic UI updates without violating thin client principle
5. Define clear boundaries for client-side state

**State Classification**:
- **Server State (Authoritative)**:
  - Conversation list
  - Message history
  - Tool call results
  - User authentication status

- **Client State (Presentation Only)**:
  - Active conversation ID
  - Streaming buffer (temporary)
  - UI state (sidebar open/closed, input focus)
  - Optimistic message display (before server confirmation)

**Decision Criteria**:
- No business logic in frontend
- All data mutations go through backend API
- Frontend can cache server responses but not modify them
- Optimistic updates must be reconciled with server responses

#### R4: JWT Authentication in Streaming Requests
**Question**: How to attach JWT tokens to streaming requests (SSE or fetch)?

**Research Approach**:
1. Review SSE authentication patterns (query params vs headers)
2. Check fetch streaming with Authorization header
3. Evaluate token refresh during long-lived streams
4. Plan for token expiration handling mid-stream

**Options**:
- **Option A: Authorization Header** (preferred for security)
- **Option B: Query Parameter** (fallback if headers not supported)

**Decision Criteria**:
- Security (no tokens in URLs if possible)
- Browser compatibility
- Token refresh support
- Existing Better Auth integration

#### R5: Conversation Persistence and Resumption
**Question**: How to handle conversation resumption after page refresh or browser restart?

**Research Approach**:
1. Review existing Conversation and Message models
2. Design conversation list API endpoint
3. Plan conversation selection and loading flow
4. Determine conversation preview generation (first message or title)

**Existing Infrastructure**:
- Conversation model with user_id, created_at, updated_at
- Message model with conversation_id, role, content, tool_calls
- Database migrations already exist

**New Requirements**:
- GET /api/{user_id}/conversations endpoint
- GET /api/{user_id}/conversations/{id}/messages endpoint
- Conversation preview logic (first user message)

### Research Deliverable

**Output**: `research.md` file with:
- Decision for each research task
- Rationale for chosen approach
- Alternatives considered and rejected
- Code examples or proof-of-concept snippets
- Links to relevant documentation

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete with all decisions made

### Design Tasks

#### D1: Data Model Review
**Objective**: Validate existing data models support all requirements

**Existing Models** (no changes needed):
- **Conversation**: id, user_id, created_at, updated_at
- **Message**: id, conversation_id, role, content, tool_calls (JSONB), created_at

**Validation**:
- ✅ Supports multiple conversations per user
- ✅ Supports message history with tool call transparency
- ✅ Supports conversation timestamps for sorting
- ✅ Supports user isolation via user_id foreign key

**Output**: `data-model.md` confirming existing models are sufficient

#### D2: API Contracts Definition
**Objective**: Define all API contracts for frontend-backend communication

**New Endpoints**:

1. **GET /api/{user_id}/conversations**
   - Returns list of user's conversations
   - Sorted by updated_at descending
   - Includes conversation preview (first message)

2. **GET /api/{user_id}/conversations/{id}/messages**
   - Returns message history for conversation
   - Includes tool_calls for transparency
   - Paginated (limit 100 messages)

3. **POST /api/{user_id}/chat/stream** (or modify existing /chat)
   - Streaming version of chat endpoint
   - Returns SSE or fetch stream
   - Includes conversation_id, response chunks, tool_calls

**Existing Endpoint** (may need modification):
- **POST /api/{user_id}/chat** (existing)
  - May need to support streaming response
  - Or keep as non-streaming fallback

**Output**: `contracts/` directory with:
- `streaming-api.yaml` - OpenAPI spec for streaming endpoint
- `conversations-api.yaml` - OpenAPI spec for conversation endpoints
- `chat-client.ts` - TypeScript interface for frontend API client

#### D3: Frontend Component Architecture
**Objective**: Design component hierarchy and data flow

**Component Tree**:
```
ChatInterface (container)
├── ConversationSidebar
│   ├── NewChatButton
│   └── ConversationItem[] (list)
└── ChatArea
    ├── MessageList
    │   └── MessageBubble[]
    │       └── ToolCallIndicator (conditional)
    ├── TypingIndicator (conditional)
    ├── ErrorRetry (conditional)
    └── ChatInput
```

**Data Flow**:
1. User sends message → ChatInput
2. ChatInput calls useChat hook
3. useChat calls chat-client API
4. Streaming response → useStreaming hook
5. useStreaming updates MessageList
6. Tool calls rendered via ToolCallIndicator

**State Management**:
- `useChat`: Manages active conversation, message sending, error handling
- `useStreaming`: Handles streaming response, token buffering
- `useConversations`: Manages conversation list, selection, creation

**Output**: Component architecture diagram in `plan.md` (this file)

#### D4: Quickstart Guide
**Objective**: Document how to run and test the feature locally

**Output**: `quickstart.md` with:
- Prerequisites (Node.js, Python, PostgreSQL)
- Backend setup (existing + streaming endpoint)
- Frontend setup (existing + chat UI)
- Environment variables needed
- How to run locally
- How to test streaming
- How to test conversation persistence

### Design Deliverables

**Outputs**:
1. `data-model.md` - Existing models validation
2. `contracts/streaming-api.yaml` - Streaming endpoint contract
3. `contracts/conversations-api.yaml` - Conversation endpoints contract
4. `contracts/chat-client.ts` - Frontend API client interface
5. `quickstart.md` - Local development guide

## Phase 2: Task Decomposition

**Note**: This phase is handled by the `/sp.tasks` command, not `/sp.plan`.

The tasks will be organized by user story priority:
- **P1 Tasks**: Streaming chat interface (core functionality)
- **P2 Tasks**: Tool call transparency
- **P3 Tasks**: Conversation management
- **P4 Tasks**: Error handling and resilience

Each task will include:
- Test task (write tests first)
- Implementation task
- Verification task (tests pass)

## Implementation Strategy

### Backend Implementation Order

1. **Streaming Endpoint** (if research chooses SSE or fetch streaming)
   - Add streaming response to existing chat endpoint
   - Or create new `/chat/stream` endpoint
   - Implement token-by-token streaming
   - Add error handling for stream interruptions

2. **Conversation Endpoints**
   - GET /api/{user_id}/conversations
   - GET /api/{user_id}/conversations/{id}/messages
   - Add conversation preview logic

3. **Testing**
   - Streaming contract tests
   - Integration tests for conversation endpoints
   - E2E tests for complete chat flow

### Frontend Implementation Order

1. **API Client Layer**
   - Authenticated fetch wrapper
   - Streaming response handler
   - Error handling and retry logic

2. **Core Chat Components** (P1)
   - ChatInterface container
   - MessageList with streaming support
   - MessageBubble component
   - ChatInput with send button
   - TypingIndicator

3. **Tool Transparency** (P2)
   - ToolCallIndicator component
   - Parse and display tool_calls from backend
   - Show tool name, status, and result

4. **Conversation Management** (P3)
   - ConversationSidebar
   - ConversationItem with preview
   - New chat button
   - Conversation selection

5. **Error Handling** (P4)
   - ErrorRetry component
   - Network error handling
   - Token expiration handling
   - Stream interruption recovery

6. **Testing**
   - Component tests for all chat components
   - Integration tests for API client
   - E2E tests for complete user flows

## Risks & Mitigations

### Risk 1: OpenAI ChatKit Incompatibility
**Likelihood**: Medium | **Impact**: High

**Mitigation**:
- Research ChatKit compatibility in Phase 0
- Have fallback plan to build custom components
- Use Tailwind CSS for consistent styling
- Leverage existing UI component patterns from dashboard

### Risk 2: Streaming Performance Issues
**Likelihood**: Low | **Impact**: High

**Mitigation**:
- Implement token batching (render every N tokens)
- Use React.memo for message components
- Implement virtual scrolling for long conversations
- Add performance monitoring and logging

### Risk 3: State Synchronization Bugs
**Likelihood**: Medium | **Impact**: Medium

**Mitigation**:
- Clear state boundaries (server vs client)
- Comprehensive integration tests
- Optimistic updates with rollback on error
- Server state as single source of truth

### Risk 4: JWT Token Expiration During Streaming
**Likelihood**: Medium | **Impact**: Medium

**Mitigation**:
- Implement token refresh before expiration
- Handle mid-stream auth failures gracefully
- Preserve partial response on token expiration
- Clear error message prompting re-authentication

## Success Metrics

### Technical Metrics
- Streaming latency: <500ms to first token
- Token rendering rate: 20+ tokens/second
- Conversation list load: <1 second
- UI responsiveness: 60fps during streaming
- Test coverage: >80% for new code

### User Experience Metrics
- Users can send message and see streaming response
- Tool calls visible inline with assistant messages
- Conversations persist across page refresh
- Error recovery works without data loss
- Mobile responsive (320px minimum width)

## Next Steps

1. **Complete Phase 0 Research** (`/sp.plan` command will generate `research.md`)
2. **Complete Phase 1 Design** (`/sp.plan` command will generate contracts and data-model.md)
3. **Run `/sp.tasks`** to generate atomic, testable tasks
4. **Run `/sp.implement`** to execute tasks in TDD workflow
5. **Create ADRs** for significant decisions (streaming approach, state management)
6. **Create PHR** for this planning session

## Architecture Decision Records (ADRs)

The following decisions will require ADRs during implementation:

1. **ADR-001: Streaming Protocol Choice** (SSE vs Fetch Streaming)
   - Decision made in Phase 0 research
   - Document rationale, alternatives, and tradeoffs

2. **ADR-002: State Management Strategy** (Client vs Server Boundary)
   - Decision made in Phase 0 research
   - Document thin client enforcement approach

3. **ADR-003: ChatKit Integration or Custom Components**
   - Decision made in Phase 0 research
   - Document compatibility findings and chosen approach

## Dependencies

### Internal Dependencies (Existing)
- ✅ FastAPI backend with agent orchestration
- ✅ OpenAI Agents SDK integration
- ✅ MCP tools (add_task, list_tasks, update_task, delete_task, complete_task)
- ✅ Conversation and Message models
- ✅ Database migrations for conversations and messages
- ✅ JWT authentication with Better Auth
- ✅ Next.js 16 frontend with App Router

### External Dependencies (To Be Added)
- OpenAI ChatKit (if compatible) or custom chat components
- SSE or fetch streaming implementation
- React hooks for chat state management

### Assumptions
- Backend API is stable and returns consistent response shapes
- JWT tokens have reasonable expiration times (not too short)
- Database can handle concurrent conversation reads/writes
- OpenAI Agents SDK continues to work as expected
- MCP tools remain stable and functional
