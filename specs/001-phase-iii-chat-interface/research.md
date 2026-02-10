# Research & Discovery: Phase-III AI Chat Interface

**Feature**: Phase-III AI Chat Interface with Streaming
**Date**: 2026-02-10
**Status**: Complete

## Overview

This document captures research findings and technical decisions made during Phase 0 of the implementation planning. Each research task addresses a specific technical unknown that must be resolved before proceeding to design and implementation.

## R1: OpenAI ChatKit Compatibility with Next.js 16 App Router

### Question
Is OpenAI ChatKit compatible with Next.js 16 App Router and React Server Components?

### Research Findings

**OpenAI ChatKit Status**:
- OpenAI ChatKit is a UI component library for building chat interfaces
- Designed primarily for client-side React applications
- Requires client-side rendering for interactive features
- May have compatibility issues with Next.js 16 App Router's server components

**Next.js 16 App Router Considerations**:
- App Router uses React Server Components by default
- Client components must be explicitly marked with `'use client'` directive
- ChatKit components would need to be wrapped in client components
- Streaming and real-time updates work better with client-side rendering

**Compatibility Assessment**:
- ChatKit can work with Next.js 16 if properly wrapped in client components
- However, dependency on specific React versions may cause conflicts
- Custom components provide more control and flexibility
- Existing project already has Tailwind CSS and component patterns

### Decision

**Use custom React components with Tailwind CSS instead of OpenAI ChatKit**

### Rationale

1. **Full Control**: Custom components give complete control over styling, behavior, and integration
2. **No Version Conflicts**: Avoid potential React version mismatches
3. **Existing Patterns**: Project already has established UI patterns and Tailwind CSS
4. **Simpler Integration**: No need to wrap third-party components or manage additional dependencies
5. **Flexibility**: Easier to customize for specific requirements (tool transparency, streaming, etc.)
6. **Maintenance**: Fewer external dependencies to maintain and update

### Alternatives Considered

- **OpenAI ChatKit**: Rejected due to potential compatibility issues and lack of control
- **react-chat-elements**: Rejected due to limited customization options
- **stream-chat-react**: Rejected due to heavy dependencies and overkill for requirements

### Implementation Approach

Build custom chat components using:
- React 19.2.1 with TypeScript
- Tailwind CSS for styling
- Next.js 16 App Router with client components
- Existing UI patterns from dashboard components

### Code Example

```typescript
// src/components/chat/ChatInterface.tsx
'use client';

import { useState } from 'react';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { ConversationSidebar } from './ConversationSidebar';

export function ChatInterface() {
  const [activeConversationId, setActiveConversationId] = useState<number | null>(null);

  return (
    <div className="flex h-screen bg-gray-50">
      <ConversationSidebar
        activeId={activeConversationId}
        onSelect={setActiveConversationId}
      />
      <div className="flex-1 flex flex-col">
        <MessageList conversationId={activeConversationId} />
        <ChatInput conversationId={activeConversationId} />
      </div>
    </div>
  );
}
```

---

## R2: FastAPI Streaming Implementation (SSE vs Fetch Streaming)

### Question
What's the best approach for streaming responses from FastAPI to Next.js frontend?

### Research Findings

**Server-Sent Events (SSE)**:
- Pros:
  - Built-in browser support via EventSource API
  - Automatic reconnection on connection loss
  - Event-based architecture (easy to handle different event types)
  - Widely supported across all modern browsers
  - Simple to implement in FastAPI with StreamingResponse
- Cons:
  - Unidirectional (server to client only)
  - Limited to text data (JSON must be stringified)
  - Cannot send custom headers after connection established
  - EventSource doesn't support custom headers (auth must be in URL or cookies)

**Fetch API Streaming**:
- Pros:
  - Bidirectional communication possible
  - Full control over request headers (easy JWT auth)
  - Works with standard fetch API
  - Can send binary data
  - More modern approach
- Cons:
  - Manual reconnection logic required
  - More complex error handling
  - Requires ReadableStream API
  - More code to implement correctly

**Browser Compatibility**:
- SSE (EventSource): Supported in all modern browsers (Chrome, Firefox, Safari, Edge)
- Fetch Streaming (ReadableStream): Supported in all modern browsers (Chrome 52+, Firefox 65+, Safari 14.1+, Edge 79+)

**JWT Authentication**:
- SSE: Cannot send Authorization header with EventSource (must use query param or cookie)
- Fetch: Can send Authorization header normally

**FastAPI Implementation**:
- Both approaches work well with FastAPI
- StreamingResponse supports both SSE and fetch streaming
- Existing agent orchestration already returns structured responses

### Decision

**Use Fetch API Streaming with ReadableStream**

### Rationale

1. **Security**: Can send JWT token in Authorization header (no token in URL)
2. **Flexibility**: Full control over request/response headers
3. **Modern**: Aligns with modern web standards and fetch API
4. **Integration**: Works seamlessly with existing JWT authentication
5. **Control**: More control over error handling and reconnection logic
6. **Compatibility**: Supported in all target browsers (modern browsers only)

### Alternatives Considered

- **SSE with EventSource**: Rejected due to JWT authentication challenges (would need token in URL or cookie)
- **WebSockets**: Rejected as overkill for unidirectional streaming (server to client)
- **Long Polling**: Rejected as outdated and inefficient

### Implementation Approach

**Backend (FastAPI)**:
```python
from fastapi import StreamingResponse
from fastapi.responses import StreamingResponse
import json

async def stream_chat_response(message: str, history: list):
    async def generate():
        # Stream response tokens
        async for token in agent.stream_response(message, history):
            chunk = json.dumps({"type": "token", "content": token})
            yield f"{chunk}\n"

        # Stream tool calls
        for tool_call in tool_calls:
            chunk = json.dumps({"type": "tool_call", "data": tool_call})
            yield f"{chunk}\n"

        # Stream completion
        yield json.dumps({"type": "done"}) + "\n"

    return StreamingResponse(
        generate(),
        media_type="application/x-ndjson",
        headers={"X-Content-Type-Options": "nosniff"}
    )
```

**Frontend (Next.js)**:
```typescript
async function streamChatResponse(message: string, conversationId: number | null) {
  const response = await fetch(`/api/${userId}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${jwtToken}`
    },
    body: JSON.stringify({ message, conversation_id: conversationId })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.trim());

    for (const line of lines) {
      const data = JSON.parse(line);

      if (data.type === 'token') {
        // Append token to streaming buffer
        appendToken(data.content);
      } else if (data.type === 'tool_call') {
        // Display tool call indicator
        showToolCall(data.data);
      } else if (data.type === 'done') {
        // Finalize message
        finalizeMessage();
      }
    }
  }
}
```

### Protocol Format

**NDJSON (Newline Delimited JSON)**:
- Each line is a complete JSON object
- Easy to parse incrementally
- Supports different message types

**Message Types**:
```json
{"type": "token", "content": "Hello"}
{"type": "token", "content": " world"}
{"type": "tool_call", "data": {"tool_name": "add_task", "status": "pending"}}
{"type": "tool_call", "data": {"tool_name": "add_task", "status": "success", "result": {...}}}
{"type": "done"}
```

---

## R3: Client vs Server State Boundary

### Question
How to enforce thin client architecture and prevent state duplication?

### Research Findings

**Thin Client Principles**:
- Frontend is purely presentational
- All business logic resides in backend
- Frontend never mutates data directly
- Server is single source of truth

**React State Management Patterns**:
- useState for local UI state
- useEffect for data fetching
- Custom hooks for reusable logic
- No global state management needed (Redux, Zustand, etc.)

**Chat UI State Requirements**:
- Active conversation selection (client-side)
- Message streaming buffer (temporary client-side)
- Conversation list (server-side, cached client-side)
- Message history (server-side, cached client-side)
- Tool call results (server-side only)

### Decision

**Clear State Boundaries with Server as Authority**

### State Classification

**Server State (Authoritative)**:
- ✅ Conversation list (fetched from GET /api/{user_id}/conversations)
- ✅ Message history (fetched from GET /api/{user_id}/conversations/{id}/messages)
- ✅ Tool call results (returned from POST /api/{user_id}/chat)
- ✅ User authentication status (JWT token validation)
- ✅ Conversation metadata (created_at, updated_at)

**Client State (Presentation Only)**:
- ✅ Active conversation ID (which conversation is selected)
- ✅ Streaming buffer (temporary tokens before message complete)
- ✅ UI state (sidebar open/closed, input focus, scroll position)
- ✅ Optimistic message display (user message before server confirmation)
- ✅ Loading states (is message sending, is conversation loading)
- ✅ Error states (network error, auth error, validation error)

**Forbidden Client State**:
- ❌ Message content modification
- ❌ Tool call simulation or inference
- ❌ Conversation creation without server confirmation
- ❌ Message deletion or editing
- ❌ Any business logic or data transformation

### Rationale

1. **Separation of Concerns**: Clear boundary between presentation and logic
2. **Data Integrity**: Server is always the source of truth
3. **Testability**: Business logic tested on backend only
4. **Maintainability**: Changes to logic don't require frontend updates
5. **Security**: No way for client to bypass business rules

### Implementation Approach

**Custom Hooks for State Management**:

```typescript
// useConversations.ts - Server state with client-side caching
export function useConversations(userId: string) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchConversations() {
      try {
        const data = await chatClient.getConversations(userId);
        setConversations(data); // Cache server response
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchConversations();
  }, [userId]);

  return { conversations, loading, error };
}

// useChat.ts - Manages active conversation (client state)
export function useChat(conversationId: number | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const [isSending, setIsSending] = useState(false);

  // Fetch messages from server (server state)
  useEffect(() => {
    if (conversationId) {
      chatClient.getMessages(conversationId).then(setMessages);
    }
  }, [conversationId]);

  // Send message (triggers server mutation)
  async function sendMessage(content: string) {
    setIsSending(true);

    // Optimistic update (client state)
    const optimisticMessage = { role: 'user', content, id: 'temp' };
    setMessages(prev => [...prev, optimisticMessage]);

    try {
      // Stream response from server
      await chatClient.streamMessage(content, conversationId, {
        onToken: (token) => setStreamingMessage(prev => prev + token),
        onComplete: (serverMessage) => {
          // Replace optimistic message with server response
          setMessages(prev => prev.filter(m => m.id !== 'temp').concat(serverMessage));
          setStreamingMessage('');
        }
      });
    } catch (error) {
      // Rollback optimistic update on error
      setMessages(prev => prev.filter(m => m.id !== 'temp'));
      throw error;
    } finally {
      setIsSending(false);
    }
  }

  return { messages, streamingMessage, isSending, sendMessage };
}
```

### Validation Rules

**Before Deployment**:
- ✅ No business logic in frontend components
- ✅ All data mutations go through backend API
- ✅ Frontend never modifies server responses
- ✅ Optimistic updates reconciled with server responses
- ✅ No tool call simulation or inference in frontend

---

## R4: JWT Authentication in Streaming Requests

### Question
How to attach JWT tokens to streaming requests (SSE or fetch)?

### Research Findings

**Fetch API with Authorization Header**:
- Standard approach: `Authorization: Bearer <token>`
- Works seamlessly with existing Better Auth integration
- Token sent securely in header (not in URL)
- Supported by all modern browsers

**Token Refresh Strategy**:
- Better Auth handles token refresh automatically
- Frontend should check token expiration before long requests
- If token expires mid-stream, handle gracefully

**Existing Authentication Flow**:
- Better Auth issues JWT tokens on login
- Tokens stored securely (httpOnly cookies or secure storage)
- Backend validates tokens on every request
- User ID extracted from token for authorization

### Decision

**Use Authorization Header with Fetch API**

### Rationale

1. **Security**: Token in header, not URL (no token leakage in logs)
2. **Standard**: Industry-standard approach for JWT authentication
3. **Integration**: Works with existing Better Auth setup
4. **Simplicity**: No special handling needed for streaming vs non-streaming

### Implementation Approach

**Frontend API Client**:
```typescript
// src/lib/api/chat-client.ts
export class ChatClient {
  private baseUrl: string;
  private getToken: () => Promise<string>;

  constructor(baseUrl: string, getToken: () => Promise<string>) {
    this.baseUrl = baseUrl;
    this.getToken = getToken;
  }

  async streamMessage(
    message: string,
    conversationId: number | null,
    callbacks: {
      onToken: (token: string) => void;
      onToolCall: (toolCall: ToolCall) => void;
      onComplete: (message: Message) => void;
      onError: (error: Error) => void;
    }
  ) {
    const token = await this.getToken();
    const userId = this.getUserIdFromToken(token);

    const response = await fetch(`${this.baseUrl}/api/${userId}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ message, conversation_id: conversationId })
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication expired. Please log in again.');
      }
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Stream processing...
  }
}
```

**Token Expiration Handling**:
```typescript
async function ensureValidToken(): Promise<string> {
  const token = await getStoredToken();
  const decoded = jwtDecode(token);

  // Refresh if token expires in less than 5 minutes
  if (decoded.exp * 1000 - Date.now() < 5 * 60 * 1000) {
    return await refreshToken();
  }

  return token;
}
```

**Mid-Stream Expiration**:
- If 401 error during stream, stop streaming
- Display clear error message: "Session expired. Please log in again."
- Preserve partial response if possible
- Redirect to login page

---

## R5: Conversation Persistence and Resumption

### Question
How to handle conversation resumption after page refresh or browser restart?

### Research Findings

**Existing Infrastructure**:
- ✅ Conversation model with id, user_id, created_at, updated_at
- ✅ Message model with conversation_id, role, content, tool_calls
- ✅ Database migrations already exist
- ✅ Agent orchestration persists messages automatically

**Requirements**:
- List all user conversations
- Display conversation preview (first message or title)
- Load message history when conversation selected
- Maintain active conversation across page refresh

### Decision

**Implement Conversation List and Message History Endpoints**

### API Endpoints

**1. GET /api/{user_id}/conversations**

Returns list of user's conversations sorted by most recent activity.

**Response**:
```json
{
  "conversations": [
    {
      "id": 1,
      "created_at": "2026-02-10T10:00:00Z",
      "updated_at": "2026-02-10T10:30:00Z",
      "preview": "Create a task to buy groceries",
      "message_count": 8
    },
    {
      "id": 2,
      "created_at": "2026-02-09T15:00:00Z",
      "updated_at": "2026-02-09T15:45:00Z",
      "preview": "Show me all my tasks",
      "message_count": 4
    }
  ]
}
```

**2. GET /api/{user_id}/conversations/{id}/messages**

Returns message history for a specific conversation.

**Query Parameters**:
- `limit`: Maximum messages to return (default: 100)
- `offset`: Pagination offset (default: 0)

**Response**:
```json
{
  "conversation_id": 1,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Create a task to buy groceries",
      "created_at": "2026-02-10T10:00:00Z",
      "tool_calls": null
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "I'll create that task for you.",
      "created_at": "2026-02-10T10:00:05Z",
      "tool_calls": [
        {
          "tool_name": "add_task",
          "input_parameters": {"title": "Buy groceries"},
          "output_result": {"id": 123, "title": "Buy groceries"},
          "execution_status": "success"
        }
      ]
    }
  ]
}
```

### Conversation Preview Logic

**Option 1: First User Message** (Chosen)
- Use the first user message as preview
- Simple and always available
- Represents what user asked about

**Option 2: Generated Title**
- Use AI to generate conversation title
- More descriptive but adds complexity
- Requires additional API call

**Decision**: Use first user message as preview (simpler, no additional cost)

### Implementation Approach

**Backend Routes**:
```python
# src/api/routes/conversations.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

router = APIRouter(prefix="/api", tags=["conversations"])

@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    # Validate user_id matches JWT
    if user_id != current_user_id:
        raise HTTPException(status_code=403)

    # Fetch conversations with message count
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = result.scalars().all()

    # Get preview (first user message) for each conversation
    conversation_list = []
    for conv in conversations:
        first_message = await session.execute(
            select(Message)
            .where(Message.conversation_id == conv.id, Message.role == 'user')
            .order_by(Message.created_at)
            .limit(1)
        )
        first_msg = first_message.scalar_one_or_none()

        conversation_list.append({
            "id": conv.id,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at,
            "preview": first_msg.content if first_msg else "New conversation",
            "message_count": len(conv.messages)
        })

    return {"conversations": conversation_list}
```

**Frontend State Persistence**:
```typescript
// Store active conversation ID in URL or localStorage
function useActiveConversation() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const conversationId = searchParams.get('conversation');

  function setActiveConversation(id: number) {
    router.push(`/chat?conversation=${id}`);
  }

  return { conversationId, setActiveConversation };
}
```

---

## Summary of Decisions

| Research Task | Decision | Rationale |
|---------------|----------|-----------|
| R1: ChatKit Compatibility | Use custom React components with Tailwind CSS | Full control, no version conflicts, existing patterns |
| R2: Streaming Approach | Fetch API Streaming with ReadableStream | Security (JWT in header), flexibility, modern standard |
| R3: State Boundary | Clear separation: server authoritative, client presentational | Thin client architecture, data integrity, maintainability |
| R4: JWT Authentication | Authorization header with Fetch API | Security, standard approach, existing integration |
| R5: Conversation Persistence | New endpoints for list and messages | Simple, efficient, uses existing models |

## Next Steps

1. ✅ Research complete - all technical unknowns resolved
2. ➡️ Proceed to Phase 1: Design & Contracts
   - Create data-model.md (validate existing models)
   - Create API contracts (streaming-api.yaml, conversations-api.yaml)
   - Create frontend client interface (chat-client.ts)
   - Create quickstart.md (local development guide)
3. ➡️ Proceed to Phase 2: Task Decomposition (`/sp.tasks`)

## References

- FastAPI Streaming: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- Fetch API Streaming: https://developer.mozilla.org/en-US/docs/Web/API/Streams_API/Using_readable_streams
- React State Management: https://react.dev/learn/managing-state
- JWT Best Practices: https://datatracker.ietf.org/doc/html/rfc8725
- NDJSON Format: http://ndjson.org/
