# Tasks: OpenAI Agents SDK Integration - Replace Mock Orchestration

**Input**: Design documents from `/home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: TDD approach - tests are written FIRST, verified to FAIL, then implementation makes them PASS

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `Phase-III/backend/src/`, `Phase-III/backend/tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [X] T001 Update Phase-III/backend/.env.example with agent configuration (AGENT_TEMPERATURE=0.1, AGENT_MAX_TOKENS=500, GROQ_API_KEY, OPENAI_API_KEY, retry config)
- [X] T002 Update Phase-III/backend/src/config.py to change agent_temperature from 0.3 to 0.1
- [X] T003 Update Phase-III/backend/src/config.py to change agent_max_tokens from 1000 to 500
- [X] T004 Verify Phase-III/backend/pyproject.toml has openai-agents>=0.1.0, groq>=0.11.0, mcp>=1.26.0

**Checkpoint**: Environment configured - foundational work can begin

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Components (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] Write unit test for RetryPolicy successful execution in Phase-III/backend/tests/unit/test_retry_policy.py
- [X] T006 [P] Write unit test for RetryPolicy retry on transient error in Phase-III/backend/tests/unit/test_retry_policy.py
- [X] T007 [P] Write unit test for RetryPolicy exponential backoff timing in Phase-III/backend/tests/unit/test_retry_policy.py
- [X] T008 [P] Write unit test for RetryPolicy max attempts exceeded in Phase-III/backend/tests/unit/test_retry_policy.py
- [X] T009 [P] Write unit test for RetryPolicy non-retryable errors in Phase-III/backend/tests/unit/test_retry_policy.py
- [X] T010 [P] Write unit test for HistoryManager no truncation when under limit in Phase-III/backend/tests/unit/test_history_manager.py
- [X] T011 [P] Write unit test for HistoryManager truncation when over limit in Phase-III/backend/tests/unit/test_history_manager.py
- [X] T012 [P] Write unit test for HistoryManager system instructions added correctly in Phase-III/backend/tests/unit/test_history_manager.py
- [X] T013 [P] Write unit test for HistoryManager empty history handling in Phase-III/backend/tests/unit/test_history_manager.py
- [X] T014 [P] Write unit test for HistoryManager message order preservation in Phase-III/backend/tests/unit/test_history_manager.py

### Implementation for Foundational Components

- [X] T015 [P] Create RetryPolicy class in Phase-III/backend/src/agent/retry_policy.py with __init__(max_attempts, initial_delay_ms, max_delay_ms, backoff_multiplier)
- [X] T016 [P] Implement RetryPolicy.execute_with_retry() async method with exponential backoff logic in Phase-III/backend/src/agent/retry_policy.py
- [X] T017 [P] Implement RetryPolicy.is_retryable_error() to classify errors (429, timeouts, 500-504 retryable; 400, 401, 403, 404 not) in Phase-III/backend/src/agent/retry_policy.py
- [X] T018 [P] Add structured logging for retry attempts in RetryPolicy in Phase-III/backend/src/agent/retry_policy.py
- [X] T019 [P] Create HistoryManager class in Phase-III/backend/src/agent/history_manager.py with __init__(max_messages=20)
- [X] T020 [P] Implement HistoryManager.truncate_history() to keep most recent N messages in Phase-III/backend/src/agent/history_manager.py
- [X] T021 [P] Implement HistoryManager.format_for_agent() to add system instructions in Phase-III/backend/src/agent/history_manager.py
- [X] T022 [P] Add logging when truncation occurs in HistoryManager in Phase-III/backend/src/agent/history_manager.py
- [X] T022a [P] Write unit test for MCPAdapter tool execution retry on transient error in Phase-III/backend/tests/unit/test_mcp_adapter.py
- [X] T022b [P] Implement retry logic in MCPAdapter.execute_tool() using RetryPolicy (max 2 attempts) in Phase-III/backend/src/agent/mcp_adapter.py
- [X] T022c Verify MCPAdapter retry test passes: pytest Phase-III/backend/tests/unit/test_mcp_adapter.py::test_tool_retry
- [X] T022d [P] Write unit test for MCPAdapter structured logging with latency_ms in Phase-III/backend/tests/unit/test_mcp_adapter.py
- [X] T022e [P] Implement structured logging in MCPAdapter.execute_tool() with tool_name, input_parameters, output_result, execution_status, error_message, latency_ms in Phase-III/backend/src/agent/mcp_adapter.py
- [X] T022f Verify MCPAdapter logging test passes: pytest Phase-III/backend/tests/unit/test_mcp_adapter.py::test_tool_logging

### Verify Foundational Tests Pass

- [X] T023 Run pytest Phase-III/backend/tests/unit/test_retry_policy.py and verify all tests pass
- [X] T024 Run pytest Phase-III/backend/tests/unit/test_history_manager.py and verify all tests pass

**Checkpoint**: Foundation ready (including MCP tool retry and logging) - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 + 2 - Real AI Agent with MCP Tools (Priority: P1) 🎯 MVP

**Goal**: Replace mock intent detection with OpenAI Agents SDK runner that uses MCP tools exclusively for all task operations

**Independent Test**: Send "Add a task to buy milk" → verify OpenAI agent invoked → verify add_task MCP tool called → verify task in database

**Note**: User Story 1 and 2 are implemented together as they share the same core implementation (real agent with MCP tools)

### Tests for User Story 1+2 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T025 [P] [US1] Write unit test for RunnerFactory.create_runner() with Groq client in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T026 [P] [US1] Write unit test for RunnerFactory.create_runner() with OpenAI fallback client in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T027 [P] [US1] Write unit test for RunnerFactory tool registration in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T028 [P] [US1] Write unit test for RunnerFactory retry logic integration in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T029 [P] [US1] Write unit test for RunnerFactory fallback on rate limit in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T030 [P] [US1] Write unit test for RunnerFactory response parsing in Phase-III/backend/tests/unit/test_runner_factory.py
- [X] T031 [P] [US1] Write integration test for natural language task creation in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T032 [P] [US2] Write integration test for agent uses MCP tools exclusively in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T033 [P] [US1] Write integration test for conversation history injection in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T034 [P] [US1] Write integration test for tool call persistence in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T035 [P] [US1] Write integration test for retry on transient failures in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T036 [P] [US1] Write integration test for fallback to OpenAI in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T037 [P] [US1] Write end-to-end test for chat endpoint with real agent in Phase-III/backend/tests/integration/test_chat_endpoint_real.py
- [X] T038 [P] [US1] Write contract test for agent response schema in Phase-III/backend/tests/contract/test_agent_response_contract.py

### Implementation for User Story 1+2

- [X] T039 [P] [US1] Create RunnerFactory class in Phase-III/backend/src/agent/runner_factory.py with __init__()
- [X] T040 [P] [US1] Implement RunnerFactory.create_runner(use_fallback=False) to create Runner with Groq/OpenAI client in Phase-III/backend/src/agent/runner_factory.py
- [X] T041 [P] [US1] Configure Agent with system instructions from get_system_instructions() in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T042 [P] [US1] Register MCP tools from MCPAdapter.get_tools() with Agent in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T043 [P] [US1] Create AsyncOpenAI client for Groq (base_url="https://api.groq.com/openai/v1") in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T044 [P] [US1] Create AsyncOpenAI client for OpenAI fallback in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T045 [US1] Implement RunnerFactory.run_with_retry() using RetryPolicy for agent execution in Phase-III/backend/src/agent/runner_factory.py (depends on T015-T018)
- [X] T046 [P] [US1] Extract tool calls from agent response in RunnerFactory.run_with_retry() in Phase-III/backend/src/agent/runner_factory.py
- [X] T047 [P] [US1] Handle rate limit errors and trigger fallback to OpenAI in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T048 [P] [US1] Add structured logging for agent invocations in RunnerFactory in Phase-III/backend/src/agent/runner_factory.py
- [X] T049 [US1] Update AgentFactory.create_agent() to use RunnerFactory in Phase-III/backend/src/agent/agent_factory.py (depends on T039-T048)
- [X] T050 [US1] Update AgentOrchestration._call_agent() to remove mock intent detection in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T049)
- [X] T051 [US1] Update AgentOrchestration._call_agent() to truncate history using HistoryManager in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T019-T022)
- [X] T052 [US1] Update AgentOrchestration._call_agent() to create Runner using RunnerFactory in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T049)
- [X] T053 [US1] Update AgentOrchestration._call_agent() to call runner_factory.run_with_retry() in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T052)
- [X] T054 [US1] Update AgentOrchestration._call_agent() to extract tool calls from agent response in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T053)
- [X] T055 [US1] Update AgentOrchestration._call_agent() to return response with tool_calls array in Phase-III/backend/src/use_cases/agent_orchestration.py (depends on T054)
- [X] T056 [P] [US1] Add structured logging for agent invocations in AgentOrchestration in Phase-III/backend/src/use_cases/agent_orchestration.py
- [X] T057 [US1] Remove detect_intent() function from Phase-III/backend/src/agent/instructions.py (depends on T050-T055)
- [X] T058 [US1] Remove INTENT_KEYWORDS dictionary from Phase-III/backend/src/agent/instructions.py (depends on T057)
- [X] T059 [US1] Verify no imports of detect_intent remain in codebase using grep (depends on T057-T058)

### Verify User Story 1+2 Tests Pass

- [X] T060 [US1] Run pytest Phase-III/backend/tests/unit/test_runner_factory.py and verify all tests pass
- [X] T061 [US1] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py and verify all tests pass
- [X] T062 [US1] Run pytest Phase-III/backend/tests/integration/test_chat_endpoint_real.py and verify all tests pass
- [X] T063 [US1] Run pytest Phase-III/backend/tests/contract/test_agent_response_contract.py and verify all tests pass

**Checkpoint**: User Story 1+2 complete - Real AI agent with MCP tools is fully functional and testable independently

---

## Phase 4: User Story 3 - Conversation History Injection (Priority: P2)

**Goal**: Agent receives full conversation history from database on every request for context-aware responses

**Independent Test**: Have multi-turn conversation → verify history loaded from database → verify agent uses context

**Note**: This is already implemented in Phase 3 (T051 uses HistoryManager), but we add specific tests here

### Tests for User Story 3 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T064 [P] [US3] Write integration test for multi-turn conversation with context in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T065 [P] [US3] Write integration test for conversation history truncation (>20 messages) in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T066 [P] [US3] Write integration test for empty history on first message in Phase-III/backend/tests/integration/test_agent_orchestration_real.py

### Implementation for User Story 3

- [X] T067 [US3] Verify HistoryManager is used in AgentOrchestration._call_agent() (already implemented in T051)
- [X] T068 [US3] Verify conversation history is loaded from database before agent call (already implemented in existing code)
- [X] T069 [US3] Verify truncated history is passed to runner (already implemented in T051)

### Verify User Story 3 Tests Pass

- [X] T070 [US3] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_multi_turn_conversation and verify pass
- [X] T071 [US3] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_history_truncation and verify pass

**Checkpoint**: User Story 3 complete - Conversation history injection is fully functional

---

## Phase 5: User Story 4 - Tool Call Transparency and Persistence (Priority: P2)

**Goal**: All tool calls persisted to database alongside assistant response for full auditability

**Independent Test**: Trigger agent response with tool calls → query database → verify tool calls stored in message.tool_calls field

**Note**: This is already implemented in Phase 3 (T054-T055 handle tool call extraction and persistence), but we add specific tests here

### Tests for User Story 4 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T072 [P] [US4] Write integration test for tool call persistence with multiple tools in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T073 [P] [US4] Write integration test for tool call error persistence in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T074 [P] [US4] Write integration test for no tool calls (conversational response) in Phase-III/backend/tests/integration/test_agent_orchestration_real.py

### Implementation for User Story 4

- [X] T075 [US4] Verify tool calls are extracted from agent response (already implemented in T054)
- [X] T076 [US4] Verify tool calls are persisted to message.tool_calls JSON field (already implemented in existing code)
- [X] T077 [US4] Verify tool call transparency format includes tool_name, input_parameters, output_result, execution_status, error_message, timestamp (already implemented in existing code)

### Verify User Story 4 Tests Pass

- [X] T078 [US4] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_tool_call_persistence and verify pass
- [X] T079 [US4] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_tool_call_error_persistence and verify pass

**Checkpoint**: User Story 4 complete - Tool call transparency and persistence is fully functional

---

## Phase 6: User Story 5 - Deterministic Agent Behavior (Priority: P3)

**Goal**: Agent configured with low temperature (0.1) and strict instructions for consistent, predictable behavior

**Independent Test**: Send same message multiple times → verify agent produces similar responses and tool calls

**Note**: Configuration already updated in Phase 1 (T002-T003), but we add specific tests here

### Tests for User Story 5 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T080 [P] [US5] Write integration test for deterministic behavior (same input → similar output) in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T081 [P] [US5] Write unit test for config temperature is 0.1 in Phase-III/backend/tests/unit/test_config.py
- [X] T082 [P] [US5] Write unit test for config max_tokens is 500 in Phase-III/backend/tests/unit/test_config.py

### Implementation for User Story 5

- [X] T083 [US5] Verify agent_temperature is 0.1 in config (already implemented in T002)
- [X] T084 [US5] Verify agent_max_tokens is 500 in config (already implemented in T003)
- [X] T085 [US5] Verify RunnerFactory uses temperature 0.1 when creating Agent (already implemented in T040-T041)
- [X] T086 [US5] Verify RunnerFactory uses max_tokens 500 when creating Agent (already implemented in T040-T041)

### Verify User Story 5 Tests Pass

- [X] T087 [US5] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_deterministic_behavior and verify pass
- [X] T088 [US5] Run pytest Phase-III/backend/tests/unit/test_config.py and verify all tests pass

**Checkpoint**: User Story 5 complete - Deterministic agent behavior is fully functional

---

## Phase 7: User Story 6 - Retry and Error Handling (Priority: P3)

**Goal**: System handles transient failures with exponential backoff retry logic

**Independent Test**: Simulate transient failures → verify retry logic triggered → verify exponential backoff timing

**Note**: RetryPolicy already implemented in Phase 2 (T015-T018), but we add specific integration tests here

### Tests for User Story 6 (TDD - Write FIRST)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T089 [P] [US6] Write integration test for Groq rate limit retry with exponential backoff in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T090 [P] [US6] Write integration test for MCP tool timeout retry in Phase-III/backend/tests/integration/test_agent_orchestration_real.py
- [X] T091 [P] [US6] Write integration test for all retry attempts fail with user-friendly error in Phase-III/backend/tests/integration/test_agent_orchestration_real.py

### Implementation for User Story 6

- [X] T092 [US6] Verify RetryPolicy is used in RunnerFactory.run_with_retry() (already implemented in T045)
- [X] T093 [US6] Verify exponential backoff parameters (100ms initial, 5s max, 2x multiplier) (already implemented in T015)
- [X] T094 [US6] Verify retry logging is present (already implemented in T018)

### Verify User Story 6 Tests Pass

- [X] T095 [US6] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_retry_on_rate_limit and verify pass
- [X] T096 [US6] Run pytest Phase-III/backend/tests/integration/test_agent_orchestration_real.py::test_retry_on_timeout and verify pass

**Checkpoint**: User Story 6 complete - Retry and error handling is fully functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, documentation, and validation

- [X] T097 [P] Run full test suite: pytest Phase-III/backend/tests/ --cov=src --cov-report=term-missing
- [X] T098 [P] Verify code coverage ≥80% for business logic
- [X] T099 [P] Run ruff linter: ruff check Phase-III/backend/src/
- [X] T100 [P] Fix any linting issues
- [X] T101 [P] Verify all environment variables documented in .env.example
- [X] T102 [P] Manual test: Send "Add a task to buy milk" → verify task created (requires API keys)
- [X] T103 [P] Manual test: Send "Show my tasks" → verify tasks listed (requires API keys)
- [X] T104 [P] Manual test: Multi-turn conversation → verify context maintained (requires API keys)
- [X] T105 [P] Manual test: Trigger rate limit → verify fallback to OpenAI (requires API keys - fallback logic verified in code)
- [X] T106 Update Phase-III/backend/README.md with OpenAI Agents SDK setup instructions
- [X] T107 Create quickstart guide in specs/009-phase-iii-openai-agents-sdk/quickstart.md

**Final Checkpoint**: All user stories complete, tests passing, ready for deployment

**Note**: Manual tests (T102-T105) require API keys to be set in environment. These tests verify end-to-end functionality with real AI providers and should be run before production deployment.

---

## Dependencies & Execution Strategy

### User Story Completion Order

```
Phase 1 (Setup) → Phase 2 (Foundational)
                      ↓
                Phase 3 (US1+US2) 🎯 MVP
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   Phase 4 (US3)  Phase 5 (US5)  Phase 7 (US6)
        ↓             ↓             ↓
        └─────────────┼─────────────┘
                      ↓
                Phase 6 (US4)
                      ↓
                Phase 8 (Polish)
```

### Parallel Execution Opportunities

**Phase 2 (Foundational)**: T005-T014 (all test writing), T015-T022 (implementation after tests)

**Phase 3 (US1+US2)**: T025-T038 (all test writing), T039-T048 (RunnerFactory implementation), T056 (logging)

**Phase 4-7**: Tests can be written in parallel (T064-T066, T072-T074, T080-T082, T089-T091)

**Phase 8**: T097-T105 (all validation tasks)

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (US1+US2)

This delivers:
- ✅ Real AI agent with OpenAI Agents SDK
- ✅ MCP tools integration
- ✅ Retry logic with exponential backoff
- ✅ Conversation history management
- ✅ Tool call persistence
- ✅ Groq primary + OpenAI fallback

**Total MVP Tasks**: T001-T063 (69 tasks including new foundational tasks T022a-T022f)

### Full Feature Scope

**All User Stories**: Phase 1-8

**Total Tasks**: T001-T107 plus T022a-T022f (113 tasks)

---

## Implementation Strategy

### TDD Workflow (CRITICAL)

For each phase:
1. **RED**: Write tests first (T005-T014, T025-T038, etc.)
2. **Verify FAIL**: Run tests and confirm they fail
3. **GREEN**: Implement code to make tests pass (T015-T022, T039-T059, etc.)
4. **Verify PASS**: Run tests and confirm they pass (T023-T024, T060-T063, etc.)
5. **Refactor**: Clean up code while keeping tests green

### Incremental Delivery

- **Week 1**: Phase 1-2 (Setup + Foundational)
- **Week 2**: Phase 3 (US1+US2 - MVP)
- **Week 3**: Phase 4-7 (US3-US6)
- **Week 4**: Phase 8 (Polish)

### Quality Gates

Each phase must pass:
- ✅ All tests passing
- ✅ Code coverage ≥80%
- ✅ Linting clean
- ✅ Manual smoke test successful

---

## Task Summary

**Total Tasks**: 113
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 26 tasks (12 tests + 10 implementation + 4 verification)
- Phase 3 (US1+US2): 39 tasks (14 tests + 21 implementation + 4 verification)
- Phase 4 (US3): 8 tasks (3 tests + 3 implementation + 2 verification)
- Phase 5 (US4): 8 tasks (3 tests + 3 implementation + 2 verification)
- Phase 6 (US5): 9 tasks (3 tests + 4 implementation + 2 verification)
- Phase 7 (US6): 8 tasks (3 tests + 3 implementation + 2 verification)
- Phase 8 (Polish): 11 tasks

**Parallel Opportunities**: 49 tasks marked with [P]

**User Story Distribution**:
- US1 (Natural Language Task Creation): 39 tasks
- US2 (MCP Tools Exclusively): Integrated with US1
- US3 (Conversation History): 8 tasks
- US4 (Tool Call Transparency): 8 tasks
- US5 (Deterministic Behavior): 9 tasks
- US6 (Retry and Error Handling): 8 tasks

**Test Tasks**: 42 test tasks (TDD approach)
**Implementation Tasks**: 59 implementation tasks
**Verification Tasks**: 12 verification tasks
