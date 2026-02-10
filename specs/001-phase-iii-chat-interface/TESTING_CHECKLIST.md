# Manual Testing Checklist: Phase-III AI Chat Interface

**Date**: 2026-02-10
**Feature**: Phase-III AI Chat Interface with Streaming
**Status**: Ready for Testing

## Pre-Testing Setup

### Backend Setup
- [ ] Backend server running on http://localhost:8000
- [ ] Database migrations applied (conversations and messages tables exist)
- [ ] Environment variables configured (.env file with DATABASE_URL, OPENAI_API_KEY, JWT_SECRET)
- [ ] MCP tools functional (add_task, list_tasks, etc.)

### Frontend Setup
- [ ] Frontend server running on http://localhost:3000
- [ ] Environment variables configured (.env.local with NEXT_PUBLIC_API_URL)
- [ ] Better Auth configured and working
- [ ] User account created and can log in

---

## User Story 1: Send Message and Receive Streaming Response (P1)

### Test 1.1: Basic Streaming
- [ ] Navigate to /chat route
- [ ] Send message: "Hello"
- [ ] **Expected**: Response appears word-by-word (streaming)
- [ ] **Expected**: Typing indicator shows before response
- [ ] **Expected**: Message persists after streaming completes

### Test 1.2: Auto-Scroll
- [ ] Send multiple messages to fill the screen
- [ ] **Expected**: Chat auto-scrolls to show latest message
- [ ] **Expected**: Scroll position stays at bottom during streaming

### Test 1.3: Input Disabled During Streaming
- [ ] Send a message
- [ ] Try to send another message while streaming
- [ ] **Expected**: Input is disabled with "Waiting for response..." placeholder
- [ ] **Expected**: Send button is disabled

### Test 1.4: Optimistic UI Updates
- [ ] Send message: "Test message"
- [ ] **Expected**: User message appears immediately (before backend response)
- [ ] **Expected**: Assistant response streams after user message

---

## User Story 2: See Tool Execution Transparency (P2)

### Test 2.1: Tool Call Display
- [ ] Send message: "Create a task to buy groceries"
- [ ] **Expected**: Tool call indicator appears showing "Add Task"
- [ ] **Expected**: Status shows "Executing..." with spinner
- [ ] **Expected**: Status changes to "Completed" with green checkmark
- [ ] **Expected**: Tool result is displayed

### Test 2.2: Multiple Tool Calls
- [ ] Send message: "Show me all my tasks"
- [ ] **Expected**: "List Tasks" tool call indicator appears
- [ ] **Expected**: Tool result shows task list
- [ ] Send message: "Complete the first task"
- [ ] **Expected**: Multiple tool calls may appear (list + complete)

### Test 2.3: Tool Call Error Handling
- [ ] Send message with invalid parameters (if possible)
- [ ] **Expected**: Tool call indicator shows "Failed" with red X
- [ ] **Expected**: Error message is displayed

---

## User Story 3: Manage Multiple Conversations (P3)

### Test 3.1: Create New Conversation
- [ ] Click "New Chat" button
- [ ] **Expected**: Conversation list updates
- [ ] **Expected**: Chat area clears
- [ ] Send a message in new conversation
- [ ] **Expected**: New conversation appears in sidebar with preview

### Test 3.2: Switch Between Conversations
- [ ] Create 3 different conversations with different first messages
- [ ] Click on second conversation in sidebar
- [ ] **Expected**: Messages from second conversation load
- [ ] **Expected**: Second conversation is highlighted in sidebar
- [ ] Click on third conversation
- [ ] **Expected**: Messages from third conversation load

### Test 3.3: Conversation Persistence
- [ ] Create a conversation and send messages
- [ ] Refresh the page (F5)
- [ ] **Expected**: Conversation list persists
- [ ] **Expected**: Active conversation is still selected
- [ ] **Expected**: Message history is intact

### Test 3.4: Conversation Preview
- [ ] Check sidebar conversation items
- [ ] **Expected**: Each shows first user message as preview
- [ ] **Expected**: Each shows timestamp (e.g., "5m ago", "2h ago")
- [ ] **Expected**: Each shows message count

---

## User Story 4: Recover from Errors Gracefully (P4)

### Test 4.1: Network Error Recovery
- [ ] Disconnect network (turn off WiFi)
- [ ] Send a message
- [ ] **Expected**: Error banner appears with clear message
- [ ] **Expected**: "Retry" button is visible
- [ ] Reconnect network
- [ ] Click "Retry"
- [ ] **Expected**: Message sends successfully

### Test 4.2: Token Expiration
- [ ] Wait for JWT token to expire (or manually expire it)
- [ ] Send a message
- [ ] **Expected**: "Session expired. Please log in again." message
- [ ] **Expected**: Redirect to login page after 2 seconds

### Test 4.3: Stream Interruption
- [ ] Send a message that generates a long response
- [ ] Refresh page mid-stream
- [ ] **Expected**: Partial response is preserved (if possible)
- [ ] **Expected**: Can retry or continue conversation

### Test 4.4: Optimistic Update Rollback
- [ ] Simulate backend error (disconnect network)
- [ ] Send a message
- [ ] **Expected**: User message appears (optimistic)
- [ ] **Expected**: Error occurs
- [ ] **Expected**: User message is removed (rollback)
- [ ] **Expected**: Error message is displayed

---

## Polish & Cross-Cutting Concerns

### Test 5.1: Responsive Mobile Design
- [ ] Resize browser to 320px width
- [ ] **Expected**: Interface remains usable
- [ ] **Expected**: Sidebar is hidden by default
- [ ] **Expected**: Hamburger menu button appears
- [ ] Click hamburger menu
- [ ] **Expected**: Sidebar slides in as overlay
- [ ] Select a conversation
- [ ] **Expected**: Sidebar closes automatically

### Test 5.2: Accessibility
- [ ] Navigate using Tab key only
- [ ] **Expected**: All interactive elements are reachable
- [ ] **Expected**: Focus indicators are visible
- [ ] **Expected**: Can send message using Enter key
- [ ] Test with screen reader (if available)
- [ ] **Expected**: ARIA labels are announced correctly

### Test 5.3: Reduced Motion
- [ ] Enable "Reduce motion" in OS settings
- [ ] **Expected**: Typing indicator doesn't bounce
- [ ] **Expected**: Streaming pulse animation is disabled
- [ ] **Expected**: Sidebar transitions are instant

### Test 5.4: Performance
- [ ] Create conversation with 50+ messages
- [ ] **Expected**: Scrolling is smooth (60fps)
- [ ] **Expected**: No lag when typing
- [ ] Send message with long response (1000+ tokens)
- [ ] **Expected**: Streaming renders smoothly
- [ ] **Expected**: No browser freezing

---

## Edge Cases

### Test 6.1: Empty States
- [ ] New user with no conversations
- [ ] **Expected**: "No conversations yet" message in sidebar
- [ ] **Expected**: "Start a conversation" message in chat area

### Test 6.2: Long Messages
- [ ] Send very long message (1000+ characters)
- [ ] **Expected**: Message wraps correctly
- [ ] **Expected**: Doesn't break layout

### Test 6.3: Special Characters
- [ ] Send message with emojis: "Hello 👋 🎉"
- [ ] **Expected**: Emojis render correctly
- [ ] Send message with code: "```python\nprint('hello')\n```"
- [ ] **Expected**: Code is displayed (no syntax highlighting expected)

### Test 6.4: Rapid Message Sending
- [ ] Send 5 messages quickly in succession
- [ ] **Expected**: All messages are queued and sent
- [ ] **Expected**: No duplicate messages
- [ ] **Expected**: Responses stream in order

---

## Browser Compatibility

### Test 7.1: Chrome/Edge
- [ ] All features work in Chrome
- [ ] All features work in Edge

### Test 7.2: Firefox
- [ ] All features work in Firefox
- [ ] Streaming works correctly

### Test 7.3: Safari
- [ ] All features work in Safari
- [ ] Streaming works correctly

---

## Security

### Test 8.1: Authentication
- [ ] Try accessing /chat without logging in
- [ ] **Expected**: Redirect to login page
- [ ] Log in and access /chat
- [ ] **Expected**: Chat interface loads

### Test 8.2: Authorization
- [ ] Check network tab for API requests
- [ ] **Expected**: All requests include Authorization header
- [ ] **Expected**: JWT token is present in header

---

## Summary

**Total Tests**: 40+
**Passed**: ___
**Failed**: ___
**Blocked**: ___

**Critical Issues Found**: ___

**Notes**:
