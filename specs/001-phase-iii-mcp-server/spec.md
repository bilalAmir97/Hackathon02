# Feature Specification: MCP Todo Server & Tooling Layer

**Feature Branch**: `001-phase-iii-mcp-server`
**Created**: 2026-02-09
**Status**: Draft
**Input**: User description: "MCP Server & Tooling Layer (Spec-1 — Phase-III Todo AI Chatbot) - Design and implement an Official MCP SDK–based server that provides stateless, database-backed tools enabling AI agents to manage todo tasks securely and reliably."

## Clarifications

### Session 2026-02-09

- Q: How should the MCP server receive the user_id for each tool invocation? → A: MCP server extracts user_id from authentication context/headers passed by the AI agent runtime
- Q: What format should task identifiers use? → A: UUID (Universally Unique Identifier)
- Q: In what order should list_tasks return tasks by default? → A: Newest first (descending by creation timestamp)
- Q: What structure should error responses follow? → A: Standard error object with code, message, and details fields: `{"error": {"code": "ERROR_CODE", "message": "description", "details": {}}}`
- Q: Which strategy should be used to handle concurrent updates to the same task? → A: Optimistic concurrency control using version field

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI Agent Creates New Task (Priority: P1)

An AI agent receives a user request to create a new todo task and uses the MCP server to persist it to the database with proper user isolation.

**Why this priority**: Core functionality - without the ability to create tasks, the system has no value. This is the foundational operation that all other features depend on.

**Independent Test**: Can be fully tested by invoking the add_task tool with valid parameters and verifying the task is persisted with correct user_id isolation. Delivers immediate value by enabling task creation.

**Acceptance Scenarios**:

1. **Given** an authenticated user context with user_id, **When** AI agent calls add_task with title and description, **Then** a new task is created and persisted with unique task_id, user_id, pending status, and creation timestamp
2. **Given** an AI agent request with missing required fields, **When** add_task is called, **Then** the tool returns a structured error indicating which fields are missing
3. **Given** multiple concurrent add_task requests from the same user, **When** tasks are created simultaneously, **Then** all tasks are persisted correctly without data loss or corruption

---

### User Story 2 - AI Agent Retrieves User Tasks (Priority: P1)

An AI agent needs to display or process a user's tasks and queries the MCP server to retrieve tasks with optional filtering by status.

**Why this priority**: Essential for user visibility - users must be able to see their tasks. This is equally critical as task creation for a viable MVP.

**Independent Test**: Can be fully tested by creating sample tasks for a user, then invoking list_tasks with various filters (all, pending, completed) and verifying only that user's tasks are returned. Delivers value by enabling task visibility.

**Acceptance Scenarios**:

1. **Given** a user has 5 pending and 3 completed tasks, **When** AI agent calls list_tasks with filter="all", **Then** all 8 tasks are returned ordered by creation timestamp (newest first)
2. **Given** a user has multiple tasks, **When** AI agent calls list_tasks with filter="pending", **Then** only pending tasks are returned
3. **Given** user A has 10 tasks and user B has 5 tasks, **When** AI agent calls list_tasks for user A, **Then** only user A's tasks are returned (strict user isolation)
4. **Given** a user has no tasks, **When** AI agent calls list_tasks, **Then** an empty list is returned with success status

---

### User Story 3 - AI Agent Marks Task Complete (Priority: P2)

An AI agent receives a user request to mark a task as complete and updates the task status through the MCP server.

**Why this priority**: Core workflow completion - users need to mark tasks done. While important, the system can demonstrate value with just create and list operations.

**Independent Test**: Can be fully tested by creating a pending task, invoking complete_task with the task_id, and verifying the status changes to completed with a completion timestamp. Delivers value by enabling task lifecycle management.

**Acceptance Scenarios**:

1. **Given** a pending task exists for user A, **When** AI agent calls complete_task with valid task_id, **Then** task status changes to completed and completion timestamp is recorded
2. **Given** a task belongs to user A, **When** AI agent attempts to complete it on behalf of user B, **Then** the operation is rejected with ownership error
3. **Given** a task is already completed, **When** AI agent calls complete_task again, **Then** the operation succeeds idempotently without error

---

### User Story 4 - AI Agent Updates Task Details (Priority: P3)

An AI agent receives a user request to modify a task's title or description and updates it through the MCP server.

**Why this priority**: Enhancement feature - improves usability but not essential for MVP. Users can work around this by deleting and recreating tasks.

**Independent Test**: Can be fully tested by creating a task, invoking update_task with new title/description, and verifying the changes are persisted while preserving task_id and other metadata. Delivers value by enabling task refinement.

**Acceptance Scenarios**:

1. **Given** a task exists for user A, **When** AI agent calls update_task with new title, **Then** the title is updated while preserving task_id, status, and timestamps
2. **Given** a task belongs to user A, **When** AI agent attempts to update it on behalf of user B, **Then** the operation is rejected with ownership error
3. **Given** an update request with empty title, **When** update_task is called, **Then** the operation is rejected with validation error

---

### User Story 5 - AI Agent Deletes Task (Priority: P3)

An AI agent receives a user request to remove a task permanently and deletes it through the MCP server.

**Why this priority**: Cleanup feature - useful but not critical for MVP. Users can tolerate completed tasks remaining in the system.

**Independent Test**: Can be fully tested by creating a task, invoking delete_task with the task_id, and verifying the task no longer appears in list_tasks results. Delivers value by enabling task cleanup.

**Acceptance Scenarios**:

1. **Given** a task exists for user A, **When** AI agent calls delete_task with valid task_id, **Then** the task is permanently removed from the database
2. **Given** a task belongs to user A, **When** AI agent attempts to delete it on behalf of user B, **Then** the operation is rejected with ownership error
3. **Given** a non-existent task_id, **When** delete_task is called, **Then** the operation returns a not found error

---

### Edge Cases

- What happens when an AI agent attempts to operate on a task that doesn't exist? (System returns structured "task not found" error)
- How does the system handle concurrent updates to the same task? (Optimistic concurrency control using version field detects conflicts and returns error for retry)
- What happens when an AI agent provides invalid user_id format? (System returns validation error before database access)
- How does the system handle database connection failures? (System returns structured error indicating temporary unavailability)
- What happens when task title exceeds reasonable length limits? (System validates and rejects with clear error message)
- How does the system handle malformed JSON in tool requests? (MCP SDK validates schema before tool execution)
- What happens when an AI agent attempts cross-user operations? (Strict ownership checks reject unauthorized access)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an add_task tool that creates new tasks with title and description, extracting user_id from authentication context and generating timestamps automatically
- **FR-002**: System MUST provide a list_tasks tool that retrieves tasks filtered by status (all, pending, completed) for a specific user, ordered by creation timestamp descending (newest first)
- **FR-003**: System MUST provide an update_task tool that modifies task title and/or description while preserving task identity
- **FR-004**: System MUST provide a complete_task tool that transitions task status from pending to completed with timestamp recording
- **FR-005**: System MUST provide a delete_task tool that permanently removes tasks from the system
- **FR-006**: System MUST enforce user isolation on all operations - users can only access their own tasks
- **FR-007**: System MUST validate all tool inputs before execution and return structured error messages following the format: `{"error": {"code": "ERROR_CODE", "message": "human-readable description", "details": {}}}` where code is a machine-readable constant (e.g., TASK_NOT_FOUND, INVALID_INPUT, UNAUTHORIZED)
- **FR-008**: System MUST persist all task data to a database - no in-memory state retention between requests
- **FR-009**: System MUST return deterministic, machine-readable JSON responses for all tool invocations
- **FR-010**: System MUST handle database errors gracefully and return appropriate error responses using the standard error format without exposing internal details (e.g., database connection strings, stack traces)
- **FR-011**: System MUST assign unique UUID identifiers to each task upon creation
- **FR-012**: System MUST record creation timestamps for all tasks automatically
- **FR-013**: System MUST record completion timestamps when tasks are marked complete
- **FR-014**: System MUST support concurrent operations from multiple AI agents without data corruption using optimistic concurrency control (version field incremented on each update)
- **FR-015**: System MUST expose tools through the Official MCP SDK protocol for agent compatibility

### Key Entities

- **Task**: Represents a todo item with title, description, status (pending/completed), user ownership, unique UUID identifier, version number for optimistic concurrency control, creation timestamp, and optional completion timestamp
- **User Context**: Represents the authenticated user making requests through the AI agent, identified by user_id for ownership enforcement

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: AI agents can create tasks and receive confirmation responses in under 500 milliseconds for 95% of requests
- **SC-002**: AI agents can retrieve task lists and receive results in under 300 milliseconds for 95% of requests
- **SC-003**: System maintains 99.9% uptime for tool availability during normal operations
- **SC-004**: 100% of cross-user access attempts are blocked by ownership validation
- **SC-005**: System handles at least 100 concurrent AI agent requests without performance degradation
- **SC-006**: All tool operations return structured, parseable JSON responses with consistent schema
- **SC-007**: System recovers gracefully from database connection failures with appropriate error messages
- **SC-008**: Zero data loss occurs during concurrent task operations from multiple agents
- **SC-009**: All tool invocations complete successfully or return actionable error messages (no silent failures)
- **SC-010**: System can be registered with OpenAI Agents SDK without configuration errors

## Assumptions *(mandatory)*

- User authentication and user_id generation is handled by an external authentication system (Phase II)
- AI agents will provide valid authentication context (headers/tokens) with every tool invocation, from which the MCP server extracts user_id
- Database schema for tasks already exists or will be created through migrations
- Network connectivity between MCP server and database is reliable
- AI agents consuming the MCP tools understand JSON response formats
- The Official MCP SDK provides adequate error handling and validation primitives
- Task titles and descriptions have reasonable length limits (e.g., 200 chars for title, 2000 for description)
- Completed tasks remain in the database indefinitely (no automatic archival/deletion)
- The system operates in a trusted environment where user_id cannot be spoofed by AI agents

## Constraints *(mandatory)*

### Technical Constraints

- Backend implementation must use Python FastAPI framework
- MCP server must be built using the Official MCP SDK only
- Database operations must use SQLModel ORM
- Database must be Neon Serverless PostgreSQL
- All configuration must be environment-based (no hardcoded credentials)

### Architectural Constraints

- Server must be completely stateless - no session or runtime memory
- Server must be horizontally scalable
- All state must be persisted to database
- Tool responses must be deterministic and idempotent where applicable

### Integration Constraints

- Server must be compatible with OpenAI Agents SDK registration
- Tool schemas must follow MCP protocol specifications
- Server must be ready for integration in Phase III of the Agentic Dev Stack workflow

## Dependencies *(mandatory)*

### External Dependencies

- **Phase II Authentication System**: Provides user_id context for all operations
- **Neon PostgreSQL Database**: Provides persistent storage for task data
- **Official MCP SDK**: Provides protocol implementation and tool registration
- **SQLModel Library**: Provides ORM capabilities for database operations

### Internal Dependencies

- Database schema must be defined and migrated before MCP server can operate
- Environment configuration must be set up with database connection strings

## Out of Scope *(mandatory)*

- User authentication and authorization (handled by Phase II)
- Conversation/chat history and message persistence (handled by OpenAI ChatKit frontend - MCP server only provides stateless tools)
- Task sharing or collaboration between users
- Task categories, tags, or labels
- Task priority levels or due dates
- Task attachments or file uploads
- Task search or advanced filtering beyond status
- Task history or audit logging
- Task notifications or reminders
- User interface or frontend components
- Task import/export functionality
- Task templates or recurring tasks
- Performance monitoring or observability dashboards (basic logging only)
- Multi-tenancy or organization-level task management

## Risks & Mitigations *(optional)*

### Risk 1: Database Connection Failures

**Impact**: MCP tools become unavailable, AI agents cannot perform task operations

**Mitigation**: Implement connection pooling, retry logic with exponential backoff, and return clear error messages to AI agents indicating temporary unavailability

### Risk 2: Concurrent Update Conflicts

**Impact**: Multiple AI agents updating the same task simultaneously could cause data inconsistency

**Mitigation**: Implement optimistic concurrency control using a version field on tasks. Each update checks the version matches and increments it atomically. Conflicts return a clear error (CONFLICT error code) prompting the AI agent to retry with fresh data.

### Risk 3: User ID Spoofing

**Impact**: If user_id can be manipulated, users could access other users' tasks

**Mitigation**: Ensure user_id is derived from trusted authentication tokens, not user-provided input. Document security requirements for AI agent integration.

### Risk 4: MCP SDK Compatibility Issues

**Impact**: Official MCP SDK may have limitations or bugs affecting tool implementation

**Mitigation**: Follow official documentation closely, test thoroughly with reference implementations, maintain fallback error handling

## Open Questions *(optional)*

None - all critical aspects are specified or have reasonable defaults documented in Assumptions.
