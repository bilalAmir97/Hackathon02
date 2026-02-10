# Implementation Plan: OpenAI Agents SDK Integration - Replace Mock Orchestration

**Branch**: `009-phase-iii-openai-agents-sdk` | **Date**: 2026-02-10 | **Spec**: `/home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/spec.md`

**Input**: Feature specification from `/home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/spec.md`

## Summary

Replace all mock intent detection code with OpenAI Agents SDK integration to enable real AI-powered natural language understanding for task management. The system will use Runner → Agent → MCP Adapter → Database flow with Groq as primary provider (openai/gpt-oss-20b) and OpenAI as fallback (gpt-4o-mini). Implementation includes exponential backoff retry logic, conversation history management (20 messages), deterministic agent behavior (temperature 0.1), and structured logging for all agent invocations and tool executions.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI, OpenAI Agents SDK (openai-agents>=0.1.0), Groq SDK (groq>=0.11.0), Official MCP SDK (mcp>=1.26.0), SQLModel, AsyncPG
**Storage**: Neon Serverless PostgreSQL (existing schema with Message.tool_calls JSON field)
**Testing**: pytest, pytest-asyncio, pytest-cov
**Target Platform**: Linux server (Vercel/cloud deployment)
**Project Type**: Web backend (FastAPI REST API)
**Performance Goals**: <5s agent response time (excluding LLM latency), 50 concurrent requests, <500ms tool execution
**Constraints**: Temperature 0.1 for determinism, max 500 tokens per response, 30s timeout, 20 message history window
**Scale/Scope**: Phase III chatbot backend, 5 MCP tools, stateless architecture, conversation persistence

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development Mandate
- Approved spec exists at `/home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/spec.md`
- All requirements documented with acceptance criteria
- Plan references spec throughout implementation

### ✅ Agent Behavior Rules
- Agent will use MCP tools exclusively (no database access)
- System instructions enforce tool usage
- Guardrails prevent data fabrication
- All decisions documented in this plan

### ✅ Phase Governance
- Feature belongs to Phase III (AI-Powered Todo Chatbot)
- Basic Level features only (no Intermediate/Advanced)
- No future-phase feature leakage
- Aligns with Phase III deadline: Dec 21, 2025

### ✅ Test-Driven Development
- Tests will be written before implementation
- Contract tests for agent responses
- Integration tests for Runner → MCP flow
- Unit tests for retry logic and history management

### ✅ Clean Architecture
- Domain layer: Message, Conversation models (existing)
- Use Cases: AgentOrchestration (to be updated)
- Interface Adapters: MCPAdapter (existing), RunnerFactory (new)
- Infrastructure: Groq/OpenAI clients, database session

### ✅ Stateless Services
- No in-memory session storage
- All conversation state in database
- Agent runner is stateless and thread-safe
- Server can restart without data loss

### ✅ Contract-First Design
- MCP tool contracts already defined in MCPAdapter
- Agent response schema documented
- Tool call transparency format specified
- Error handling contracts defined

### ✅ Observability & Monitoring
- Structured JSON logging for all agent invocations
- Tool execution logging with latency metrics
- Retry attempt logging
- Fallback event logging

### ✅ Security & Compliance
- JWT authentication before agent invocation
- User_id injection into all tool calls
- No direct database access from agent
- API keys in environment variables only

## Project Structure

### Documentation (this feature)

```text
specs/009-phase-iii-openai-agents-sdk/
├── plan.md              # This file
├── research.md          # Phase 0 output (OpenAI Agents SDK patterns)
├── data-model.md        # Phase 1 output (retry policy, runner config)
├── quickstart.md        # Phase 1 output (local testing guide)
├── contracts/           # Phase 1 output (agent response schema)
└── tasks.md             # Phase 2 output (NOT created by this plan)
```

### Source Code (repository root)

```text
Phase-III/backend/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── agent_factory.py          # [MODIFY] Update to use OpenAI Agents SDK
│   │   ├── runner_factory.py         # [CREATE] Factory for Runner instances
│   │   ├── retry_policy.py           # [CREATE] Exponential backoff logic
│   │   ├── history_manager.py        # [CREATE] Conversation truncation (20 msgs)
│   │   ├── instructions.py           # [MODIFY] Remove detect_intent function
│   │   ├── mcp_adapter.py            # [KEEP] Already functional
│   │   └── guardrails.py             # [KEEP] Already functional
│   ├── use_cases/
│   │   └── agent_orchestration.py    # [MODIFY] Replace mock with real agent
│   ├── config.py                     # [MODIFY] Update temperature to 0.1, max_tokens to 500
│   └── domain/models/
│       ├── message.py                # [KEEP] Already has tool_calls field
│       └── conversation.py           # [KEEP] Already functional
├── tests/
│   ├── unit/
│   │   ├── test_runner_factory.py    # [CREATE] Test Runner creation
│   │   ├── test_retry_policy.py      # [CREATE] Test exponential backoff
│   │   └── test_history_manager.py   # [CREATE] Test message truncation
│   ├── integration/
│   │   ├── test_agent_orchestration_real.py  # [CREATE] Test real agent flow
│   │   └── test_chat_endpoint_real.py        # [CREATE] End-to-end with real agent
│   └── contract/
│       └── test_agent_response_contract.py   # [CREATE] Validate agent responses
└── .env.example                      # [MODIFY] Add correct agent config values
```

**Structure Decision**: Web application backend structure. All agent-related modules are in `src/agent/` following Clean Architecture. Use cases orchestrate agent interactions. Tests organized by type (unit/integration/contract).

## Complexity Tracking

> **No violations - all changes align with constitution principles**

---

## Phase 0: Research

**Objective**: Understand OpenAI Agents SDK integration patterns, Runner API, and tool registration.

### Research Tasks

#### R1: OpenAI Agents SDK Architecture
- **Goal**: Understand Agent, Runner, and tool registration patterns
- **Method**: Read OpenAI Agents SDK documentation at https://openai.github.io/openai-agents-python/
- **Key Questions**:
  - How to create Agent instances with system instructions?
  - How to register MCP tools with Agent?
  - How to create Runner instances for agent execution?
  - How to pass conversation history to Runner?
  - How to extract tool calls from agent responses?
  - How to handle streaming vs non-streaming responses?
- **Output**: Document Agent/Runner API patterns in `research.md`

#### R2: Groq Integration with OpenAI Agents SDK
- **Goal**: Verify Groq compatibility with OpenAI Agents SDK
- **Method**: Review Groq SDK documentation and OpenAI Agents SDK client compatibility
- **Key Questions**:
  - Does OpenAI Agents SDK support custom OpenAI-compatible clients?
  - How to configure Groq base_url with AsyncOpenAI client?
  - What are Groq rate limit headers and error codes?
  - How to detect rate limit errors for fallback logic?
- **Output**: Document Groq integration pattern in `research.md`

#### R3: Tool Call Extraction and Persistence
- **Goal**: Understand how to extract tool calls from agent responses
- **Method**: Review OpenAI Agents SDK response format and tool call schema
- **Key Questions**:
  - What is the structure of agent responses with tool calls?
  - How to extract tool_name, arguments, and results?
  - How to handle multiple tool calls in one response?
  - How to detect tool call failures?
- **Output**: Document tool call extraction pattern in `research.md`

#### R4: Exponential Backoff Best Practices
- **Goal**: Research retry strategies for LLM and tool failures
- **Method**: Review industry best practices for API retry logic
- **Key Questions**:
  - What are standard exponential backoff parameters?
  - How to detect transient vs permanent failures?
  - Should retries use jitter to avoid thundering herd?
  - How to log retry attempts for observability?
- **Output**: Document retry strategy in `research.md`

#### R5: Conversation History Management
- **Goal**: Understand token limits and history truncation strategies
- **Method**: Review OpenAI token counting and context window management
- **Key Questions**:
  - How to count tokens in conversation history?
  - What is the context window for openai/gpt-oss-20b?
  - Should truncation be message-based or token-based?
  - How to preserve system instructions while truncating history?
- **Output**: Document history management strategy in `research.md`

---

## Phase 1: Design

**Objective**: Design data models, contracts, and architecture for OpenAI Agents SDK integration.

### D1: Runner Factory Design

**Purpose**: Create Runner instances with Groq/OpenAI clients and retry logic.

**Interface**:
```python
class RunnerFactory:
    def create_runner(
        self,
        use_fallback: bool = False
    ) -> tuple[Runner, dict]:
        """Create Runner with Groq or OpenAI client.

        Returns:
            (Runner instance, config dict with provider/model info)
        """

    async def run_with_retry(
        self,
        runner: Runner,
        message: str,
        history: List[Dict[str, str]],
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """Execute runner with exponential backoff retry.

        Returns:
            Agent response with content and tool_calls
        """
```

**Configuration**:
- Primary: Groq client with openai/gpt-oss-20b
- Fallback: OpenAI client with gpt-4o-mini
- Temperature: 0.1 (deterministic)
- Max tokens: 500
- Timeout: 30 seconds
- Tools: From MCPAdapter.get_tools()
- Instructions: From get_system_instructions()

**Error Handling**:
- Rate limit errors → Trigger fallback to OpenAI
- Timeout errors → Retry with exponential backoff
- Invalid tool calls → Log and return error to user
- Network errors → Retry with exponential backoff

### D2: Retry Policy Design

**Purpose**: Implement exponential backoff for transient failures.

**Interface**:
```python
class RetryPolicy:
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay_ms: int = 100,
        max_delay_ms: int = 5000,
        backoff_multiplier: float = 2.0
    ):
        """Initialize retry policy with exponential backoff."""

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic.

        Raises:
            Exception: If all retry attempts fail
        """

    def is_retryable_error(self, error: Exception) -> bool:
        """Determine if error is transient and retryable."""
```

**Retry Logic**:
- Attempt 1: Execute immediately
- Attempt 2: Wait 100ms, then retry
- Attempt 3: Wait 200ms, then retry
- Attempt 4: Wait 400ms, then retry (capped at 5000ms)
- If all fail: Raise exception with full error context

**Retryable Errors**:
- Rate limit errors (429)
- Timeout errors
- Connection errors
- Server errors (500, 502, 503, 504)

**Non-Retryable Errors**:
- Authentication errors (401, 403)
- Invalid request errors (400)
- Not found errors (404)

### D3: History Manager Design

**Purpose**: Truncate conversation history to most recent 20 messages.

**Interface**:
```python
class HistoryManager:
    def __init__(self, max_messages: int = 20):
        """Initialize history manager."""

    def truncate_history(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Keep most recent N messages.

        Returns:
            Truncated message list
        """

    def format_for_agent(
        self,
        messages: List[Dict[str, str]],
        system_instructions: str
    ) -> List[Dict[str, str]]:
        """Format messages for agent with system prompt.

        Returns:
            [{"role": "system", "content": instructions}, ...messages]
        """
```

**Truncation Strategy**:
- Keep most recent 20 messages (10 user + 10 assistant pairs)
- Always preserve system instructions at the beginning
- Log when truncation occurs for observability
- Count messages, not tokens (simpler, more predictable)

### D4: Agent Response Contract

**Purpose**: Define standard format for agent responses with tool calls.

**Schema**:
```json
{
  "content": "I'll create that task for you.",
  "tool_calls": [
    {
      "name": "add_task",
      "arguments": {
        "title": "Buy milk",
        "description": null
      }
    }
  ]
}
```

**Tool Call Transparency Schema** (persisted to database):
```json
[
  {
    "tool_name": "add_task",
    "input_parameters": {
      "title": "Buy milk",
      "description": null
    },
    "output_result": {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "title": "Buy milk",
      "status": "pending",
      "created_at": "2026-02-10T12:00:00Z"
    },
    "execution_status": "success",
    "error_message": null,
    "timestamp": "2026-02-10T12:00:00Z"
  }
]
```

### D5: Updated Agent Orchestration Flow

**Current Flow** (Mock):
```
User Message → detect_intent() → Mock Response → Execute Tool → Persist
```

**New Flow** (Real Agent):
```
User Message → Load History → RunnerFactory.run_with_retry() →
Agent (via Runner) → Tool Calls → MCPAdapter.execute_tool() →
Persist Messages + Tool Calls → Return Response
```

**Detailed Steps**:
1. Validate JWT and extract user_id
2. Create or resume conversation
3. Load conversation history from database (most recent 20 messages)
4. Truncate history if needed (HistoryManager)
5. Create Runner instance (RunnerFactory)
6. Execute agent with retry logic (run_with_retry)
7. Extract tool calls from agent response
8. Execute each tool call through MCPAdapter
9. Persist user message, assistant message, and tool calls atomically
10. Return response with tool call transparency

**Error Handling**:
- Groq rate limit → Fallback to OpenAI
- Transient failures → Retry with exponential backoff
- Tool execution errors → Log and return error in response
- Database errors → Rollback transaction and return 500

### D6: Configuration Updates

**Environment Variables** (.env.example):
```bash
# Agent Configuration
AGENT_TEMPERATURE=0.1  # Deterministic behavior (was 0.3)
AGENT_MAX_TOKENS=500   # Concise responses (was 1000)
AGENT_MAX_HISTORY_MESSAGES=20
AGENT_TIMEOUT_SECONDS=30

# Groq Configuration (Primary Provider)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
GROQ_BASE_URL=https://api.groq.com/openai/v1

# OpenAI Configuration (Fallback Provider)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_FALLBACK_MODEL=gpt-4o-mini
OPENAI_FALLBACK_ENABLED=true

# Retry Configuration
RETRY_MAX_ATTEMPTS=3
RETRY_INITIAL_DELAY_MS=100
RETRY_MAX_DELAY_MS=5000
RETRY_BACKOFF_MULTIPLIER=2.0
```

### D7: Logging Strategy

**Agent Invocation Log**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "level": "INFO",
  "event": "agent_invocation",
  "request_id": "req_123",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "conversation_id": 1,
  "message": "Create a task to buy milk",
  "provider": "groq",
  "model": "openai/gpt-oss-20b",
  "temperature": 0.1,
  "max_tokens": 500,
  "history_message_count": 10,
  "execution_time_ms": 1234
}
```

**Tool Execution Log**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "level": "INFO",
  "event": "tool_execution",
  "request_id": "req_123",
  "tool_name": "add_task",
  "input_parameters": {"title": "Buy milk"},
  "output_result": {"id": "...", "title": "Buy milk"},
  "execution_status": "success",
  "error_message": null,
  "latency_ms": 45
}
```

**Retry Attempt Log**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "level": "WARNING",
  "event": "retry_attempt",
  "request_id": "req_123",
  "attempt": 2,
  "max_attempts": 3,
  "error_type": "RateLimitError",
  "delay_ms": 200,
  "next_action": "retry"
}
```

**Fallback Event Log**:
```json
{
  "timestamp": "2026-02-10T12:00:00Z",
  "level": "WARNING",
  "event": "provider_fallback",
  "request_id": "req_123",
  "from_provider": "groq",
  "to_provider": "openai",
  "reason": "rate_limit_exceeded"
}
```

---

## Phase 2: Implementation Sequence

**Objective**: Implement OpenAI Agents SDK integration in testable, incremental steps.

### Implementation Order

**Rationale**: Bottom-up approach starting with foundational utilities (retry, history), then core integration (runner factory), then orchestration updates, and finally cleanup.

### Step 1: Create Retry Policy Module
**File**: `Phase-III/backend/src/agent/retry_policy.py`

**Purpose**: Implement exponential backoff retry logic for transient failures.

**Implementation**:
- Create `RetryPolicy` class with configurable parameters
- Implement `execute_with_retry()` async method
- Implement `is_retryable_error()` to classify errors
- Add structured logging for retry attempts
- Handle rate limit errors (429), timeouts, connection errors
- Cap delay at max_delay_ms (5000ms)
- Raise exception with full context after max attempts

**Dependencies**: None (pure utility)

**Tests**: `tests/unit/test_retry_policy.py`
- Test successful execution on first attempt
- Test retry on transient error
- Test exponential backoff timing
- Test max attempts exceeded
- Test non-retryable errors fail immediately

---

### Step 2: Create History Manager Module
**File**: `Phase-III/backend/src/agent/history_manager.py`

**Purpose**: Truncate conversation history to most recent 20 messages.

**Implementation**:
- Create `HistoryManager` class with max_messages parameter
- Implement `truncate_history()` to keep most recent N messages
- Implement `format_for_agent()` to add system instructions
- Log when truncation occurs
- Preserve message order (oldest to newest)

**Dependencies**: None (pure utility)

**Tests**: `tests/unit/test_history_manager.py`
- Test no truncation when under limit
- Test truncation when over limit
- Test system instructions added correctly
- Test empty history handling
- Test message order preservation

---

### Step 3: Create Runner Factory Module
**File**: `Phase-III/backend/src/agent/runner_factory.py`

**Purpose**: Create OpenAI Agents SDK Runner instances with Groq/OpenAI clients.

**Implementation**:
- Create `RunnerFactory` class
- Implement `create_runner()` to instantiate Runner with Agent
- Configure Agent with system instructions and MCP tools
- Create AsyncOpenAI client for Groq (base_url="https://api.groq.com/openai/v1")
- Create AsyncOpenAI client for OpenAI (fallback)
- Implement `run_with_retry()` using RetryPolicy
- Extract tool calls from agent response
- Handle rate limit errors and trigger fallback
- Add structured logging for agent invocations

**Dependencies**:
- `src/agent/retry_policy.py` (Step 1)
- `src/agent/mcp_adapter.py` (existing)
- `src/config.py` (existing)
- `openai-agents` package
- `groq` package

**Tests**: `tests/unit/test_runner_factory.py`
- Test Groq runner creation
- Test OpenAI runner creation
- Test tool registration
- Test retry logic integration
- Test fallback on rate limit
- Test response parsing

---

### Step 4: Update Agent Factory
**File**: `Phase-III/backend/src/agent/agent_factory.py`

**Purpose**: Update to use RunnerFactory instead of returning config dict.

**Implementation**:
- Import `RunnerFactory`
- Update `create_agent()` to return Runner instance
- Delegate to `RunnerFactory.create_runner()`
- Keep `get_mcp_adapter()` method unchanged
- Remove old client creation logic (moved to RunnerFactory)

**Dependencies**:
- `src/agent/runner_factory.py` (Step 3)

**Tests**: Update `tests/unit/test_agent_factory.py`
- Test agent factory returns Runner
- Test MCP adapter access

---

### Step 5: Update Agent Orchestration
**File**: `Phase-III/backend/src/use_cases/agent_orchestration.py`

**Purpose**: Replace mock intent detection with real OpenAI Agents SDK calls.

**Implementation**:
- Import `RunnerFactory` and `HistoryManager`
- Update `_call_agent()` method:
  - Remove all mock intent detection logic
  - Truncate history using HistoryManager
  - Create Runner using RunnerFactory
  - Call `runner_factory.run_with_retry()` with message and history
  - Extract tool calls from agent response
  - Return response with tool_calls array
- Keep confirmation flow logic (guardrails)
- Keep tool execution logic unchanged
- Keep message persistence logic unchanged
- Add structured logging for agent invocations

**Dependencies**:
- `src/agent/runner_factory.py` (Step 3)
- `src/agent/history_manager.py` (Step 2)

**Tests**: `tests/integration/test_agent_orchestration_real.py`
- Test natural language task creation
- Test agent uses MCP tools
- Test conversation history injection
- Test tool call persistence
- Test retry on transient failures
- Test fallback to OpenAI

---

### Step 6: Remove Mock Intent Detection
**File**: `Phase-III/backend/src/agent/instructions.py`

**Purpose**: Remove detect_intent() function and related mock code.

**Implementation**:
- Delete `detect_intent()` function
- Delete `INTENT_KEYWORDS` dictionary
- Keep `SYSTEM_INSTRUCTIONS` constant
- Keep `get_system_instructions()` function

**Dependencies**: None (cleanup)

**Tests**: Verify no imports of `detect_intent` remain in codebase

---

### Step 7: Update Configuration
**File**: `Phase-III/backend/src/config.py`

**Purpose**: Update agent configuration to match spec requirements.

**Implementation**:
- Change `agent_temperature` default from 0.3 to **0.1**
- Change `agent_max_tokens` default from 1000 to **500**
- Keep all other settings unchanged
- Verify Groq and OpenAI config fields exist

**Dependencies**: None

**Tests**: `tests/unit/test_config.py`
- Test temperature is 0.1
- Test max_tokens is 500
- Test all required fields present

---

### Step 8: Update Environment Example
**File**: `Phase-III/backend/.env.example`

**Purpose**: Document correct agent configuration values.

**Implementation**:
- Update `AGENT_TEMPERATURE` comment and value to 0.1
- Update `AGENT_MAX_TOKENS` comment and value to 500
- Add detailed comments explaining deterministic behavior
- Verify all Groq and OpenAI fields documented

**Dependencies**: None

**Tests**: Manual verification

---

### Step 9: Integration Testing
**Files**:
- `tests/integration/test_agent_orchestration_real.py`
- `tests/integration/test_chat_endpoint_real.py`

**Purpose**: Verify end-to-end flow with real OpenAI Agents SDK.

**Implementation**:
- Test natural language task creation
- Test multi-turn conversations with context
- Test tool call transparency
- Test retry logic with simulated failures
- Test fallback to OpenAI
- Test conversation history truncation
- Test deterministic behavior (same input → similar output)

**Dependencies**: All previous steps

**Tests**: Integration test suite

---

### Step 10: Contract Testing
**File**: `tests/contract/test_agent_response_contract.py`

**Purpose**: Validate agent responses match expected schema.

**Implementation**:
- Test agent response has content field
- Test agent response has tool_calls array
- Test tool calls have correct structure
- Test tool call transparency format
- Test error responses have proper structure

**Dependencies**: All previous steps

**Tests**: Contract test suite

---

## Risk Mitigation

### Risk 1: OpenAI Agents SDK API Changes
**Impact**: High - Could break integration
**Probability**: Low - SDK is stable
**Mitigation**:
- Pin exact SDK version in pyproject.toml
- Monitor SDK release notes
- Test thoroughly before deployment

### Risk 2: Groq Rate Limits Lower Than Expected
**Impact**: Medium - Frequent fallbacks to OpenAI
**Probability**: Medium - Free tier limits
**Mitigation**:
- Implement aggressive retry logic
- Monitor rate limit usage
- Consider request queuing
- Use OpenAI fallback seamlessly

### Risk 3: Agent Hallucinations Despite Low Temperature
**Impact**: Medium - Incorrect tool calls
**Probability**: Low - Temperature 0.1 is very deterministic
**Mitigation**:
- Strict input validation in MCP adapter
- Log all tool calls for monitoring
- Use structured output format
- Add guardrails for destructive actions

### Risk 4: Conversation History Token Limits
**Impact**: Low - Truncation may lose context
**Probability**: Medium - Long conversations
**Mitigation**:
- Implement 20-message window (simple, predictable)
- Log when truncation occurs
- Consider summarization in future iteration
- Test with long conversation scenarios

---

## Success Metrics

### Functional Metrics
- ✅ 100% of requests use OpenAI Agents SDK (no mock code)
- ✅ 95%+ accuracy in intent detection (measured by tool call correctness)
- ✅ 100% tool call persistence (no data loss)
- ✅ 100% conversation history injection
- ✅ 100% Groq rate limit fallback success

### Performance Metrics
- ✅ <5s agent response time (excluding LLM latency)
- ✅ <500ms tool execution time
- ✅ <500ms conversation history loading
- ✅ 50 concurrent requests without degradation

### Reliability Metrics
- ✅ 95%+ success rate after retries
- ✅ 90%+ deterministic responses (same input → similar output)
- ✅ 100% atomic persistence (no partial writes)

### Observability Metrics
- ✅ 100% agent invocations logged
- ✅ 100% tool executions logged
- ✅ 100% retry attempts logged
- ✅ 100% fallback events logged

---

## Rollout Plan

### Phase 1: Development (Local Testing)
1. Implement all modules in order (Steps 1-8)
2. Run unit tests for each module
3. Run integration tests with real Groq/OpenAI APIs
4. Verify logging output and metrics

### Phase 2: Staging (Pre-Production)
1. Deploy to staging environment
2. Run end-to-end tests with real users
3. Monitor agent response quality
4. Monitor rate limits and fallback frequency
5. Verify tool call persistence

### Phase 3: Production (Gradual Rollout)
1. Deploy to production
2. Monitor error rates and latency
3. Monitor Groq/OpenAI API usage
4. Collect user feedback on response quality
5. Adjust temperature/max_tokens if needed

---

## Next Steps

After this plan is approved:
1. Run `/sp.tasks` to generate atomic implementation tasks
2. Execute tasks in dependency order
3. Follow TDD: write tests → verify failure → implement → verify pass
4. Create PHR for every user interaction
5. Commit small, atomic changes
6. Run tests continuously
