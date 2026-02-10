# Tasks: Phase-III AI Chat Interface with Streaming

**Input**: Design documents from `/specs/001-phase-iii-chat-interface/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are included following TDD workflow (write tests → verify fail → implement → verify pass)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Total Tasks**: 92 tasks across 7 phases (including performance, security, and edge case verification)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend**: `Phase-III/backend/src/`
- **Frontend**: `Phase-III/frontend/src/`
- **Backend Tests**: `Phase-III/backend/tests/`
- **Frontend Tests**: `Phase-III/frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Minimal setup - most infrastructure already exists

- [X] T001 [P] Create frontend chat directory structure: `Phase-III/frontend/src/components/chat/`, `Phase-III/frontend/src/lib/api/`, `Phase-III/frontend/src/lib/hooks/`, `Phase-III/frontend/src/types/`
- [X] T002 [P] Create backend contracts directory for streaming tests: `Phase-III/backend/tests/contract/`, `Phase-III/backend/tests/integration/`
- [X] T003 [P] Create frontend test directories: `Phase-III/frontend/tests/components/chat/`, `Phase-III/frontend/tests/e2e/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Foundation

- [X] T004 Create TypeScript types for chat in `Phase-III/frontend/src/types/chat.ts` (Conversation, Message, ToolCall, StreamChunk interfaces from contracts/chat-client.ts)
- [X] T005 Implement ChatClient class in `Phase-III/frontend/src/lib/api/chat-client.ts` (authenticated fetch wrapper, token extraction, error handling)
- [X] T006 Implement streaming handler in `Phase-III/frontend/src/lib/api/streaming.ts` (ReadableStream processing, NDJSON parsing, chunk buffering)
- [X] T007 Create streaming endpoint in `Phase-III/backend/src/api/routes/chat_stream.py` (POST /api/{user_id}/chat/stream with NDJSON response)
- [X] T008 Create conversations endpoint in `Phase-III/backend/src/api/routes/conversations.py` (GET /api/{user_id}/conversations and GET /api/{user_id}/conversations/{id}/messages)

### Frontend Foundation

- [X] T009 [P] Create useAuth hook wrapper in `Phase-III/frontend/src/lib/hooks/useAuth.ts` (wraps Better Auth, provides getToken function)
- [X] T010 [P] Create base chat layout component in `Phase-III/frontend/src/app/chat/layout.tsx` (authenticated route wrapper)
- [X] T011 [P] Create chat page route in `Phase-III/frontend/src/app/chat/page.tsx` (main chat interface container)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Send Message and Receive Streaming Response (Priority: P1) 🎯 MVP

**Goal**: Users can send a message and see the AI's response appear word-by-word in real-time

**Independent Test**: Send "Hello" and verify response streams token-by-token rather than appearing all at once

### Tests for User Story 1 (TDD)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Contract test for streaming endpoint in `Phase-III/backend/tests/contract/test_streaming_contract.py` (verify NDJSON format, token chunks, done chunk)
- [ ] T013 [P] [US1] Integration test for streaming flow in `Phase-III/backend/tests/integration/test_chat_streaming.py` (send message, verify stream, check persistence)
- [ ] T014 [P] [US1] Component test for MessageList in `Phase-III/frontend/tests/components/chat/MessageList.test.tsx` (render messages, streaming updates, auto-scroll)
- [ ] T015 [P] [US1] Component test for ChatInput in `Phase-III/frontend/tests/components/chat/ChatInput.test.tsx` (send message, disable during streaming, validation)

### Implementation for User Story 1

#### Backend Implementation

- [X] T016 [US1] Modify agent_orchestration.py to support streaming: Add `stream_response()` method that yields tokens from OpenAI Agents SDK in `Phase-III/backend/src/use_cases/agent_orchestration.py`
- [X] T017 [US1] Implement streaming endpoint handler in `Phase-III/backend/src/api/routes/chat_stream.py`: Process message, stream tokens as NDJSON, emit tool_calls, emit done with conversation_id
- [X] T018 [US1] Add streaming endpoint to FastAPI router in `Phase-III/backend/src/main.py`: Register chat_stream router

#### Frontend Implementation

- [X] T019 [P] [US1] Create MessageBubble component in `Phase-III/frontend/src/components/chat/MessageBubble.tsx` (display user/assistant messages with role styling, timestamp, content)
- [X] T020 [P] [US1] Create TypingIndicator component in `Phase-III/frontend/src/components/chat/TypingIndicator.tsx` (animated dots, shows during streaming)
- [X] T021 [US1] Create MessageList component in `Phase-III/frontend/src/components/chat/MessageList.tsx` (render message array, streaming message buffer, auto-scroll to bottom)
- [X] T022 [US1] Create ChatInput component in `Phase-III/frontend/src/components/chat/ChatInput.tsx` (textarea, send button, disable during streaming, Enter to send)
- [X] T023 [US1] Create useStreaming hook in `Phase-III/frontend/src/lib/hooks/useStreaming.ts` (manage streaming state, token buffering, callbacks)
- [X] T024 [US1] Create useChat hook in `Phase-III/frontend/src/lib/hooks/useChat.ts` (send message, manage messages array, optimistic updates, error handling)
- [X] T025 [US1] Create ChatInterface component in `Phase-III/frontend/src/components/chat/ChatInterface.tsx` (compose MessageList + ChatInput, manage active conversation)
- [X] T026 [US1] Integrate ChatInterface into chat page in `Phase-III/frontend/src/app/chat/page.tsx` (render ChatInterface with auth check)

#### Verification

- [ ] T027 [US1] Run backend streaming tests: `pytest Phase-III/backend/tests/integration/test_chat_streaming.py -v`
- [ ] T028 [US1] Run frontend component tests: `npm test -- components/chat`
- [ ] T029 [US1] Manual E2E test: Send message, verify streaming, check persistence

**Checkpoint**: At this point, User Story 1 should be fully functional - users can send messages and see streaming responses

---

## Phase 4: User Story 2 - See Tool Execution Transparency (Priority: P2)

**Goal**: Users see inline indicators when the AI agent calls tools, understanding what actions the AI is taking

**Independent Test**: Send "Create a task called 'Test task'" and verify inline indicators show "Calling add_task..." followed by "✅ Task created"

### Tests for User Story 2 (TDD)

- [ ] T030 [P] [US2] Component test for ToolCallIndicator in `Phase-III/frontend/tests/components/chat/ToolCallIndicator.test.tsx` (render pending, success, error states)
- [ ] T031 [P] [US2] Integration test for tool call display in `Phase-III/frontend/tests/e2e/tool-transparency.spec.ts` (send message with tool call, verify indicators appear)

### Implementation for User Story 2

- [X] T032 [P] [US2] Create ToolCallIndicator component in `Phase-III/frontend/src/components/chat/ToolCallIndicator.tsx` (display tool name, status icon, input/output, timestamp)
- [X] T033 [US2] Update MessageBubble to render tool calls in `Phase-III/frontend/src/components/chat/MessageBubble.tsx` (parse tool_calls array, render ToolCallIndicator for each)
- [X] T034 [US2] Update useStreaming hook to handle tool_call chunks in `Phase-III/frontend/src/lib/hooks/useStreaming.ts` (onToolCall callback, append to tool calls array)
- [X] T035 [US2] Update streaming endpoint to emit tool_call chunks in `Phase-III/backend/src/api/routes/chat_stream.py` (emit pending before execution, emit success/error after)

#### Verification

- [ ] T036 [US2] Run tool transparency tests: `npm test -- components/chat/ToolCallIndicator`
- [ ] T037 [US2] Manual E2E test: Send "Create a task", verify tool indicators appear inline

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - users see streaming responses with tool transparency

---

## Phase 5: User Story 3 - Manage Multiple Conversations (Priority: P3)

**Goal**: Users can create new conversations, view a list of previous conversations, and resume any conversation

**Independent Test**: Create 3 conversations, close browser, reopen, verify all 3 appear in sidebar and can be resumed

### Tests for User Story 3 (TDD)

- [ ] T038 [P] [US3] Contract test for conversations endpoint in `Phase-III/backend/tests/contract/test_conversations_contract.py` (verify response schema, pagination)
- [ ] T039 [P] [US3] Integration test for conversation list in `Phase-III/backend/tests/integration/test_conversations_list.py` (create conversations, fetch list, verify sorting)
- [ ] T040 [P] [US3] Component test for ConversationSidebar in `Phase-III/frontend/tests/components/chat/ConversationSidebar.test.tsx` (render list, select conversation, new chat)
- [ ] T041 [P] [US3] Component test for ConversationItem in `Phase-III/frontend/tests/components/chat/ConversationItem.test.tsx` (render preview, highlight active, click to select)

### Implementation for User Story 3

#### Backend Implementation

- [X] T042 [US3] Implement list conversations handler in `Phase-III/backend/src/api/routes/conversations.py`: GET /api/{user_id}/conversations (fetch conversations, get preview from first message, sort by updated_at)
- [X] T043 [US3] Implement get messages handler in `Phase-III/backend/src/api/routes/conversations.py`: GET /api/{user_id}/conversations/{id}/messages (fetch messages, include tool_calls, pagination)
- [X] T044 [US3] Add conversations router to FastAPI in `Phase-III/backend/src/main.py`: Register conversations router

#### Frontend Implementation

- [X] T045 [P] [US3] Create ConversationItem component in `Phase-III/frontend/src/components/chat/ConversationItem.tsx` (display preview, timestamp, message count, active highlight)
- [X] T046 [P] [US3] Create NewChatButton component in `Phase-III/frontend/src/components/chat/NewChatButton.tsx` (button to create new conversation)
- [X] T047 [US3] Create ConversationSidebar component in `Phase-III/frontend/src/components/chat/ConversationSidebar.tsx` (render conversation list, NewChatButton, handle selection)
- [X] T048 [US3] Create useConversations hook in `Phase-III/frontend/src/lib/hooks/useConversations.ts` (fetch conversations, create new, select conversation, cache list)
- [X] T049 [US3] Update ChatInterface to include sidebar in `Phase-III/frontend/src/components/chat/ChatInterface.tsx` (add ConversationSidebar, manage active conversation, load messages on selection)
- [X] T050 [US3] Update useChat hook to load conversation history in `Phase-III/frontend/src/lib/hooks/useChat.ts` (fetch messages when conversation selected, merge with new messages)
- [X] T051 [US3] Add conversation ID to URL params in `Phase-III/frontend/src/app/chat/page.tsx` (persist active conversation in URL, restore on page load)

#### Verification

- [ ] T052 [US3] Run conversation tests: `pytest Phase-III/backend/tests/integration/test_conversations_list.py -v`
- [ ] T053 [US3] Run sidebar component tests: `npm test -- components/chat/ConversationSidebar`
- [ ] T054 [US3] Manual E2E test: Create 3 conversations, refresh page, verify persistence

**Checkpoint**: All core user stories (1, 2, 3) should now be independently functional

---

## Phase 6: User Story 4 - Recover from Errors Gracefully (Priority: P4)

**Goal**: When network errors or backend failures occur, users can see clear error messages and retry without losing context

**Independent Test**: Simulate network failure, send message, see error, reconnect, successfully retry

### Tests for User Story 4 (TDD)

- [ ] T055 [P] [US4] Component test for ErrorRetry in `Phase-III/frontend/tests/components/chat/ErrorRetry.test.tsx` (render error message, retry button, dismiss)
- [ ] T056 [P] [US4] Integration test for error handling in `Phase-III/frontend/tests/e2e/error-recovery.spec.ts` (simulate network error, verify retry, check no duplicates)

### Implementation for User Story 4

- [X] T057 [P] [US4] Create ErrorRetry component in `Phase-III/frontend/src/components/chat/ErrorRetry.tsx` (display error message, retry button, dismiss button)
- [X] T058 [US4] Update useChat hook with error handling in `Phase-III/frontend/src/lib/hooks/useChat.ts` (catch errors, store error state, retry logic, rollback optimistic updates)
- [X] T059 [US4] Update useStreaming hook with stream interruption handling in `Phase-III/frontend/src/lib/hooks/useStreaming.ts` (detect stream interruption, preserve partial response, enable retry)
- [X] T060 [US4] Add token expiration handling in `Phase-III/frontend/src/lib/api/chat-client.ts` (detect 401 errors, clear error message, redirect to login)
- [X] T061 [US4] Update ChatInterface to display errors in `Phase-III/frontend/src/components/chat/ChatInterface.tsx` (render ErrorRetry when error exists, pass retry callback)
- [X] T062 [US4] Add request cancellation on navigation in `Phase-III/frontend/src/lib/hooks/useChat.ts` (AbortController for fetch requests, cleanup on unmount)

#### Verification

- [ ] T063 [US4] Run error handling tests: `npm test -- components/chat/ErrorRetry`
- [ ] T064 [US4] Manual E2E test: Disconnect network, send message, reconnect, retry successfully

**Checkpoint**: All user stories (1-4) should now be complete with full error resilience

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Styling & UX Polish

- [X] T065 [P] Add responsive styles for mobile in `Phase-III/frontend/src/components/chat/ChatInterface.tsx` (320px minimum width, collapsible sidebar)
- [X] T066 [P] Add accessibility attributes in all chat components (ARIA labels, keyboard navigation, focus indicators)
- [X] T067 [P] Add reduced-motion support in `Phase-III/frontend/src/components/chat/TypingIndicator.tsx` (respect prefers-reduced-motion)
- [X] T068 [P] Optimize re-renders with React.memo in `Phase-III/frontend/src/components/chat/MessageBubble.tsx` and `Phase-III/frontend/src/components/chat/ConversationItem.tsx`

### Performance Optimization

- [X] T069 [P] Implement token batching in streaming handler in `Phase-III/frontend/src/lib/api/streaming.ts` (render every N tokens instead of every token)
- [ ] T070 [P] Add virtual scrolling for long conversations in `Phase-III/frontend/src/components/chat/MessageList.tsx` (use react-window or similar)
- [ ] T071 [P] Add conversation list pagination in `Phase-III/frontend/src/lib/hooks/useConversations.ts` (load more on scroll)

### Testing & Documentation

- [ ] T072 [P] Add E2E test for complete chat flow in `Phase-III/frontend/tests/e2e/chat-flow.spec.ts` (login, send message, see streaming, create new chat, switch conversations)
- [ ] T073 [P] Add performance tests for streaming in `Phase-III/backend/tests/performance/test_streaming_performance.py` (measure latency, throughput, concurrent users)
- [ ] T074 [P] Update quickstart.md with final setup instructions in `specs/001-phase-iii-chat-interface/quickstart.md`
- [X] T075 [P] Add API documentation comments in `Phase-III/backend/src/api/routes/chat_stream.py` and `Phase-III/backend/src/api/routes/conversations.py`

### Security & Monitoring

- [ ] T076 [P] Add rate limiting to streaming endpoint in `Phase-III/backend/src/api/routes/chat_stream.py` (prevent abuse)
- [X] T077 [P] Add structured logging for streaming events in `Phase-III/backend/src/api/routes/chat_stream.py` (stream start, tokens sent, completion, errors)
- [ ] T078 [P] Add client-side error tracking in `Phase-III/frontend/src/lib/api/chat-client.ts` (log errors to monitoring service)

### Final Validation

- [ ] T079 Run full test suite: `pytest Phase-III/backend/tests/ && npm test --prefix Phase-III/frontend`
- [ ] T080 Run quickstart.md validation: Follow all steps in quickstart.md and verify they work
- [ ] T081 Manual testing checklist: Test all user stories end-to-end, verify mobile responsive, check accessibility

### Additional Performance & Security Tasks

- [ ] T082 [P] Measure streaming performance in `Phase-III/backend/tests/performance/test_streaming_performance.py` (verify 20+ tokens/second rendering rate, measure latency, test with 1000+ token responses) - maps to NFR-003
- [ ] T083 [P] Measure UI responsiveness during streaming in `Phase-III/frontend/tests/performance/test_ui_performance.spec.ts` (verify 60fps maintained, measure frame drops, test with long conversations) - maps to NFR-004
- [ ] T084 [US1] Implement non-streaming fallback in `Phase-III/frontend/src/lib/api/chat-client.ts` (detect streaming unavailable, fallback to regular fetch, display complete response at once) - maps to FR-016
- [ ] T085 [P] Audit logging for sensitive data in `Phase-III/backend/src/` (scan all log statements, ensure no JWT tokens, passwords, or user data logged, add linting rule) - maps to NFR-007

### Edge Case Verification Tasks

- [ ] T086 [P] Test extremely long streaming responses in `Phase-III/frontend/tests/e2e/edge-cases.spec.ts` (send message generating 10,000+ tokens, verify no performance degradation, check memory usage)
- [ ] T087 [P] Test rapid-fire message sending in `Phase-III/frontend/tests/e2e/edge-cases.spec.ts` (send multiple messages quickly, verify queue handling, check no race conditions)
- [ ] T088 [P] Test navigation during streaming in `Phase-III/frontend/tests/e2e/edge-cases.spec.ts` (navigate away mid-stream, verify cleanup, check no memory leaks)
- [ ] T089 [P] Test long-running tool calls in `Phase-III/backend/tests/integration/test_tool_timeout.py` (simulate 30+ second tool execution, verify timeout handling, check user feedback)
- [ ] T090 [P] Test malformed tool_calls data in `Phase-III/frontend/tests/components/chat/ToolCallIndicator.test.tsx` (send invalid JSON, missing fields, verify graceful degradation)
- [ ] T091 [P] Test large conversation performance in `Phase-III/frontend/tests/performance/test_large_conversations.spec.ts` (load conversation with 100+ messages, verify render time, check scroll performance)
- [ ] T092 [P] Test concurrent tab access in `Phase-III/frontend/tests/e2e/concurrent-tabs.spec.ts` (open same conversation in 2 tabs, send messages, verify no conflicts or duplicates)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD)
- Backend endpoints before frontend integration
- Components before hooks
- Hooks before page integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- Backend foundation (T004-T008) and Frontend foundation (T009-T011) can run in parallel within Phase 2
- All tests for a user story can run in parallel (marked with [P])
- Components within a story can run in parallel (marked with [P])
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All Polish tasks (T065-T078) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T012: Contract test for streaming endpoint
Task T013: Integration test for streaming flow
Task T014: Component test for MessageList
Task T015: Component test for ChatInput

# Launch all independent components for User Story 1 together:
Task T019: Create MessageBubble component
Task T020: Create TypingIndicator component
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T029)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add Polish → Final release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T011)
2. Once Foundational is done:
   - Developer A: User Story 1 (T012-T029)
   - Developer B: User Story 2 (T030-T037)
   - Developer C: User Story 3 (T038-T054)
   - Developer D: User Story 4 (T055-T064)
3. Stories complete and integrate independently
4. Team completes Polish together (T065-T081)

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Follow TDD: Write tests first, verify they fail, implement, verify they pass
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend already has: agent orchestration, MCP tools, Conversation/Message models, JWT auth
- Frontend already has: Next.js 16 App Router, Better Auth, Tailwind CSS, existing dashboard
- No database migrations needed - Conversation and Message tables already exist
- **Total Tasks**: 92 (including 11 new performance, security, and edge case tasks added after analysis)
