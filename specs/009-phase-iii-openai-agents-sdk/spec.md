# Feature Specification: OpenAI Agents SDK Integration - Replace Mock Orchestration

**Feature Branch**: `009-phase-iii-openai-agents-sdk`
**Created**: 2026-02-10
**Status**: Draft
**Input**: Replace Mock Orchestration with OpenAI Agents SDK + MCP (Spec-2 Completion)

## Clarifications

### Session 2026-02-10

- Q: How many recent messages should be kept when conversation history exceeds token limits? → A: 20 messages
- Q: What are the exponential backoff timing parameters for retry logic? → A: 100ms initial, 5s max, 2x multiplier
- Q: What is the maximum execution timeout for the agent runner before it's considered failed? → A: 30 seconds
- Q: What exact temperature value should be used for the agent configuration? → A: 0.1
- Q: What is the maximum number of tokens allowed for agent responses? → A: 500 tokens

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Natural Language Task Creation via Real AI Agent (Priority: P1)

A user sends "Add a task to buy milk" and the OpenAI Agents SDK runner processes the message, invokes the agent with MCP tools, and the agent calls add_task to create the task in the database.

**Why this priority**: This is the core value proposition - replacing mock intent detection with real AI understanding. Without this, the system cannot interpret natural language accurately.

**Independent Test**: Can be fully tested by sending a natural language message, verifying the OpenAI agent is invoked (not mock detection), MCP tool is called, and task is persisted to database with correct user_id.

**Acceptance Scenarios**:

1. **Given** an authenticated user sends "Add a task to buy milk", **When** the agent processes the message, **Then** the OpenAI Agents SDK runner invokes the agent, the agent calls add_task MCP tool, and a task is created in the database
2. **Given** a user sends "Create three tasks: buy milk, call dentist, and finish report", **When** the agent processes the message, **Then** the agent makes three separate add_task tool calls and all three tasks are persisted
3. **Given** a user sends an ambiguous request "Add a task", **When** the agent processes it, **Then** the agent asks for clarification about what task to create without making any tool calls

---

### User Story 2 - Agent Uses MCP Tools Exclusively (Priority: P1)

The agent must use only MCP tools for all task operations and never directly access the database or fabricate task data.

**Why this priority**: This enforces the architectural constraint that the agent cannot bypass the MCP layer, ensuring data integrity and auditability.

**Independent Test**: Can be fully tested by monitoring tool calls during agent execution and verifying no direct database access occurs, only MCP tool invocations.

**Acceptance Scenarios**:

1. **Given** a user requests to list tasks, **When** the agent processes the request, **Then** the agent calls list_tasks MCP tool and returns results from the tool, not from direct database queries
2. **Given** a user requests to update a task, **When** the agent processes the request, **Then** the agent calls update_task MCP tool with correct parameters and does not attempt direct database updates
3. **Given** the MCP tool returns an error, **When** the agent receives the error, **Then** the agent communicates the error to the user in natural language without attempting to bypass the tool

---

### User Story 3 - Conversation History Injection (Priority: P2)

The agent receives full conversation history from the database on every request, enabling context-aware responses across multiple turns.

**Why this priority**: Context awareness is essential for multi-turn conversations, but the system can demonstrate basic functionality without it.

**Independent Test**: Can be fully tested by having a multi-turn conversation, verifying conversation history is fetched from database and passed to the agent runner on each request.

**Acceptance Scenarios**:

1. **Given** a user previously created a task "buy milk" in the conversation, **When** the user says "mark it as done", **Then** the agent uses conversation history to identify which task to complete
2. **Given** a conversation has 10 previous messages, **When** a new message is sent, **Then** all 10 previous messages are loaded from database and passed to the agent runner
3. **Given** a user starts a new conversation, **When** the first message is sent, **Then** the agent receives an empty history and processes the message without prior context

---

### User Story 4 - Tool Call Transparency and Persistence (Priority: P2)

All tool calls made by the agent are persisted to the database alongside the assistant's response, providing full auditability.

**Why this priority**: Transparency is important for debugging and auditability, but the system can function without persisting tool calls initially.

**Independent Test**: Can be fully tested by triggering an agent response with tool calls, then querying the database to verify tool calls are stored in the messages table.

**Acceptance Scenarios**:

1. **Given** an agent makes two tool calls (list_tasks and add_task), **When** the response is persisted, **Then** both tool calls are stored in the message.tool_calls JSON field with tool name, inputs, outputs, and status
2. **Given** a tool call fails with an error, **When** the response is persisted, **Then** the tool call is stored with execution_status='error' and error_message populated
3. **Given** an agent response has no tool calls, **When** the response is persisted, **Then** the message.tool_calls field is null or empty array

---

### User Story 5 - Deterministic Agent Behavior (Priority: P3)

The agent is configured with low temperature and strict instructions to ensure consistent, predictable behavior.

**Why this priority**: Determinism improves reliability but is not essential for initial functionality.

**Independent Test**: Can be fully tested by sending the same message multiple times and verifying the agent produces similar responses and tool calls.

**Acceptance Scenarios**:

1. **Given** the agent is configured with temperature=0.1, **When** the same message is sent twice, **Then** the agent produces nearly identical responses and tool calls
2. **Given** the agent receives system instructions to always use MCP tools, **When** processing any task operation, **Then** the agent never attempts to simulate or fabricate data
3. **Given** the agent is instructed to confirm destructive actions, **When** a user says "delete all tasks", **Then** the agent asks for confirmation before calling delete_task

---

### User Story 6 - Retry and Error Handling (Priority: P3)

The system handles transient failures from the AI model or MCP tools with exponential backoff retry logic.

**Why this priority**: Resilience is important for production but not required for initial implementation.

**Independent Test**: Can be fully tested by simulating transient failures (rate limits, timeouts) and verifying retry logic is triggered with exponential backoff.

**Acceptance Scenarios**:

1. **Given** the Groq API returns a rate limit error, **When** the agent orchestration detects the error, **Then** the system retries with exponential backoff up to 3 attempts
2. **Given** an MCP tool call times out, **When** the timeout is detected, **Then** the system retries the tool call once before returning an error to the user
3. **Given** all retry attempts fail, **When** the final failure occurs, **Then** the system returns a user-friendly error message and logs the failure with full context

---

### Edge Cases

- What happens when the OpenAI Agents SDK runner fails to initialize? (System returns 500 error and logs initialization failure)
- How does the system handle very long conversation histories? (Implement message window or summarization strategy to stay within token limits)
- What happens when the agent attempts to call a non-existent tool? (Agent receives error from MCP adapter and communicates to user)
- How does the system handle concurrent requests to the same conversation? (Database transactions ensure consistency; agent runs are independent)
- What happens when JWT token is expired during agent execution? (Request is rejected before agent invocation)
- How does the system handle malformed tool call arguments from the agent? (MCP adapter validates inputs and returns structured error)
- What happens when the agent produces no tool calls but user expects an action? (Agent explains why no action was taken or asks for clarification)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST replace all mock intent detection code with OpenAI Agents SDK runner invocation
- **FR-002**: System MUST use Runner → Agent → MCP Adapter → Database flow for all task operations
- **FR-003**: System MUST configure the agent with system instructions that enforce MCP tool usage exclusively
- **FR-004**: System MUST register all five MCP tools (add_task, list_tasks, update_task, complete_task, delete_task) with the agent using strict JSON schemas
- **FR-005**: System MUST pass conversation history from database to the agent runner on every request
- **FR-006**: System MUST persist assistant responses and tool calls atomically to the database after agent execution
- **FR-007**: System MUST store tool calls in the message.tool_calls JSON field with tool_name, input_parameters, output_result, execution_status, error_message, and timestamp
- **FR-008**: System MUST configure agent with temperature = 0.1 for deterministic behavior
- **FR-009**: System MUST use Groq as primary LLM provider with openai/gpt-oss-20b model
- **FR-010**: System MUST implement fallback to OpenAI gpt-4o-mini when Groq fails or rate limits are exceeded
- **FR-011**: System MUST implement exponential backoff retry logic for transient LLM failures (max 3 attempts)
- **FR-012**: System MUST implement exponential backoff retry logic for transient MCP tool failures (max 2 attempts)
- **FR-013**: System MUST log all agent invocations with request_id, user_id, conversation_id, message, response, tool_calls, and execution_time_ms
- **FR-014**: System MUST log all tool executions with tool_name, input_parameters, output_result, execution_status, error_message, and latency_ms
- **FR-015**: System MUST inject user_id context into all MCP tool calls to enforce user isolation
- **FR-016**: System MUST validate JWT authentication before invoking the agent runner
- **FR-017**: System MUST remain stateless - all conversation state must be persisted to and loaded from database
- **FR-018**: System MUST handle agent responses that contain no tool calls (conversational responses)
- **FR-019**: System MUST handle agent responses that contain multiple tool calls in sequence
- **FR-020**: System MUST configure all LLM API keys and model names via environment variables
- **FR-021**: System MUST implement async execution for all agent runner and MCP tool operations
- **FR-022**: System MUST enforce agent guardrails: no database access, no data fabrication, always use tools
- **FR-023**: System MUST handle token limit errors by truncating conversation history (keep most recent 20 messages)
- **FR-024**: System MUST return structured tool_calls array in chat endpoint response for transparency
- **FR-025**: System MUST remove all mock intent detection code (detect_intent function and related logic)

### Key Entities

- **Agent Configuration**: Contains system instructions, temperature (0.1), max_tokens (500), timeout (30 seconds), and tool definitions. Configured once at startup and reused for all requests.
- **Agent Runner**: OpenAI Agents SDK runner instance that executes the agent with conversation history and returns responses with tool calls. Stateless and thread-safe.
- **Tool Call Record**: Embedded in Message.tool_calls JSON field. Contains tool_name, input_parameters (JSON), output_result (JSON), execution_status (success/error), error_message (if failed), and timestamp. Used for auditability and debugging.
- **Retry Policy**: Configuration for exponential backoff retry logic. Contains max_attempts, initial_delay_ms (100ms), max_delay_ms (5000ms), and backoff_multiplier (2x). Applied to both LLM and tool failures.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create, read, update, complete, and delete tasks using natural language with 95% accuracy in intent detection, measured by:
  - Test suite: 100 natural language prompts covering all 5 CRUD operations (20 prompts per operation)
  - Matching criteria: Agent's tool call name and primary parameters match expected operation (e.g., "add_task" with correct title)
  - Calculation: (Correct tool calls / Total prompts) × 100 ≥ 95%
  - Test prompts include variations: direct commands ("Add task X"), conversational ("I need to X"), ambiguous ("Can you help with X")
- **SC-002**: System processes natural language messages through OpenAI Agents SDK runner with 100% of requests (no mock intent detection code remains)
- **SC-003**: Agent makes correct MCP tool calls for task operations with 98% accuracy (measured by tool call validation against expected operations)
- **SC-004**: All tool calls are persisted to database with 100% reliability (no data loss)
- **SC-005**: Conversation history is injected into agent runs with 100% consistency (all previous messages loaded from database)
- **SC-006**: System handles Groq rate limits gracefully with automatic fallback to OpenAI in 100% of cases
- **SC-007**: Transient failures are retried with exponential backoff, achieving 95% success rate after retries
- **SC-008**: Agent responses are deterministic with temperature=0.1, producing identical tool calls for identical inputs in 90% of cases, measured by:
  - Test suite: 20 natural language prompts (covering all 5 CRUD operations)
  - Test method: Send each prompt 5 times (100 total requests)
  - Matching criteria: Exact tool call match (same tool_name, same input_parameters)
  - Calculation: (Requests with identical tool calls / Total requests) × 100 ≥ 90%
  - Note: Response text may vary slightly; only tool calls must match exactly
- **SC-009**: System responds to user messages within 5 seconds under normal load (excluding LLM latency which is external)
- **SC-010**: All agent invocations and tool executions are logged with structured data, enabling complete audit trail reconstruction

## Scope *(mandatory)*

### In Scope

- Replace mock intent detection with OpenAI Agents SDK runner
- Configure agent with system instructions and MCP tool definitions
- Implement Runner → Agent → MCP Adapter → Database flow
- Persist tool calls to database in message.tool_calls JSON field
- Inject conversation history into agent runs
- Implement retry logic with exponential backoff for LLM and tool failures
- Implement Groq primary provider with OpenAI fallback
- Configure deterministic agent behavior (low temperature)
- Implement structured logging for agent invocations and tool executions
- Remove all mock intent detection code from codebase
- Validate agent guardrails (no database access, always use tools)
- Handle token limit errors with conversation history truncation
- Support multi-turn conversations with context awareness

### Out of Scope

- Standalone MCP server integration (using MCP Adapter only)
- Custom LLM wrappers or non-OpenAI Agents SDK implementations
- Real-time streaming responses (single response per request)
- Conversation summarization or compression (simple truncation only)
- Multi-agent orchestration or agent handoffs
- Custom tool creation or dynamic tool registration
- Voice or audio input/output
- Frontend UI changes (backend API only)
- Changes to existing MCP tool implementations
- Changes to database schema (using existing Message.tool_calls field)

## Assumptions *(mandatory)*

- OpenAI Agents SDK supports MCP tool integration as documented
- Groq API provides access to openai/gpt-oss-20b model with sufficient rate limits
- OpenAI API provides access to gpt-4o-mini model as fallback
- Existing Message model has tool_calls JSON field for storing tool call records
- Existing MCP Adapter implementation is functional and tested
- Existing conversation persistence logic works correctly
- Database connection pooling is configured for concurrent requests
- Environment variables are securely managed and not committed to version control
- JWT authentication middleware is functional and validates tokens correctly
- Existing guardrails module provides confirmation management for destructive actions

## Dependencies *(mandatory)*

### Internal Dependencies

- **Existing MCP Adapter**: Functional MCP adapter with all five tools (add_task, list_tasks, update_task, complete_task, delete_task)
- **Existing Database Schema**: Message model with tool_calls JSON field for storing tool call records
- **Existing Conversation Persistence**: Conversation and Message models with proper relationships and persistence logic
- **Existing JWT Authentication**: JWT middleware that validates tokens and extracts user_id
- **Existing Guardrails Module**: Confirmation manager for handling destructive action confirmations

### External Dependencies

- **OpenAI Agents SDK**: Python library for building AI agents with tool support (openai-agents package)
- **Groq API**: High-throughput AI model provider with openai/gpt-oss-20b model access
- **OpenAI API**: Fallback AI model provider with gpt-4o-mini model access
- **Neon PostgreSQL**: Serverless database service for conversation and tool call persistence

### Risks

- **Risk 1**: OpenAI Agents SDK may have breaking changes or bugs that affect MCP tool integration
  - *Mitigation*: Pin specific SDK version, test thoroughly, monitor SDK release notes
- **Risk 2**: Groq rate limits may be lower than expected, causing frequent fallbacks to OpenAI
  - *Mitigation*: Implement aggressive retry logic, monitor rate limit usage, consider request queuing
- **Risk 3**: Agent may hallucinate tool calls or provide incorrect parameters despite strict schemas
  - *Mitigation*: Implement strict input validation in MCP adapter, log all tool calls for monitoring, use low temperature
- **Risk 4**: Conversation history may exceed token limits for long conversations
  - *Mitigation*: Implement message window (keep most recent N messages), add token counting logic, consider summarization in future

## Non-Functional Requirements *(optional)*

### Performance

- Agent runner must respond within 5 seconds (excluding external LLM latency)
- Tool call persistence must complete within 500ms
- Conversation history loading must complete within 500ms for conversations up to 100 messages
- System must handle 50 concurrent agent requests without degradation

### Security

- All agent requests must be authenticated with valid JWT tokens
- User_id must be validated and injected into all MCP tool calls
- Agent must not have direct database access (only through MCP adapter)
- Tool call inputs must be validated and sanitized before execution
- API keys must be stored in environment variables only
- All agent invocations must be logged for security auditing

### Reliability

- System must persist tool calls atomically with assistant responses (no partial writes)
- Failed tool calls must be retried with exponential backoff (max 2 attempts)
- Failed LLM calls must be retried with exponential backoff (max 3 attempts)
- System must gracefully handle Groq rate limits with automatic OpenAI fallback
- Conversation state must survive server restarts (stateless design)

### Observability

- All agent invocations must be logged with request_id, user_id, conversation_id, message, response, tool_calls, execution_time_ms
- All tool executions must be logged with tool_name, input_parameters, output_result, execution_status, error_message, latency_ms
- All retry attempts must be logged with attempt number, delay, and outcome
- All fallback events (Groq → OpenAI) must be logged with reason and timestamp
- Performance metrics must be collected for agent response times and tool execution times

## Open Questions *(optional)*

None - all requirements are specified with reasonable defaults where needed.

## References *(optional)*

- MCP Server & Tooling: https://modelcontextprotocol.io/docs/develop/build-server
- OpenAI Agents SDK Documentation: https://openai.github.io/openai-agents-python/
- Groq Model Documentation: https://console.groq.com/docs/model/openai/gpt-oss-20b
- Existing Phase III Spec (Agent Chat Endpoint): specs/001-phase-iii-agent-chat-endpoint/spec.md
- Existing Phase III Spec (MCP Server): specs/001-phase-iii-mcp-server/spec.md
