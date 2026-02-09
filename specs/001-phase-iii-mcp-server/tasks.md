# Tasks: MCP Todo Server & Tooling Layer

**Input**: Design documents from `/specs/001-phase-iii-mcp-server/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each MCP tool.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `Phase-III/backend/src/`, `Phase-III/backend/tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install MCP SDK and create project structure for MCP server module

- [X] T001 Install MCP SDK via UV in Phase-III/backend: `uv add mcp`
- [X] T002 [P] Create MCP module directory structure: Phase-III/backend/src/mcp/ with __init__.py
- [X] T003 [P] Create MCP tools subdirectory: Phase-III/backend/src/mcp/tools/ with __init__.py
- [X] T004 [P] Create MCP schemas subdirectory: Phase-III/backend/src/mcp/schemas/ with __init__.py
- [X] T005 [P] Create MCP middleware subdirectory: Phase-III/backend/src/mcp/middleware/ with __init__.py
- [X] T006 [P] Create MCP tests directory: Phase-III/backend/tests/mcp/ with __init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Add version field to Task model in Phase-III/backend/src/domain/models.py (default=1, nullable=False)
- [X] T008 Create Alembic migration for version field: `uv run alembic revision --autogenerate -m "add task version field"`
- [X] T009 Apply database migration: `uv run alembic upgrade head`
- [X] T010 [P] Add MCP server configuration to Phase-III/backend/src/config.py (mcp_server_enabled, mcp_server_port, mcp_tool_timeout)
- [X] T011 [P] Create MCP error code enum in Phase-III/backend/src/mcp/middleware/error_handler.py (TASK_NOT_FOUND, INVALID_INPUT, UNAUTHORIZED, FORBIDDEN, CONFLICT, DATABASE_ERROR, INTERNAL_ERROR)
- [X] T012 [P] Create MCP error response models in Phase-III/backend/src/mcp/middleware/error_handler.py (MCPError, MCPErrorResponse, format_mcp_error function)
- [X] T013 [P] Create authentication context extractor in Phase-III/backend/src/mcp/middleware/auth_context.py (extract_user_id function with JWT verification)
- [X] T014 [P] Create request-scoped session factory in Phase-III/backend/src/mcp/middleware/auth_context.py (get_mcp_session async context manager)
- [X] T015 Create MCP server initialization in Phase-III/backend/src/mcp/server.py (Server instance, stdio_server setup)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 2.5: Test Infrastructure Setup (TDD Compliance)

**Purpose**: Establish test infrastructure and contract tests BEFORE implementing user stories (per constitution Section IV)

**⚠️ CRITICAL**: Tests must be written and verified to fail BEFORE implementation begins

- [X] T015a [P] Create MCP contract test suite in Phase-III/backend/tests/mcp/test_contracts.py (validate tool schemas against contracts/mcp-tools.json)
- [X] T015b [P] Create MCP error format test suite in Phase-III/backend/tests/mcp/test_error_format.py (validate error responses against contracts/error-codes.json)

**Checkpoint**: Test infrastructure ready - user story test-first implementation can now begin

---

## Phase 3: User Story 1 - AI Agent Creates New Task (Priority: P1) 🎯 MVP

**Goal**: Enable AI agents to create new todo tasks with title and description, persisted to database with user isolation

**Independent Test**: Invoke add_task tool with valid JWT token, title, and description. Verify task is created in database with correct user_id, UUID, version=1, and pending status.

### Test-First Implementation for User Story 1 (TDD)

**⚠️ CRITICAL**: Write tests FIRST, verify they FAIL, then implement

- [X] T015c [P] [US1] Write contract test for add_task tool in Phase-III/backend/tests/mcp/test_add_task_contract.py (validate input/output schemas match contracts/mcp-tools.json)
- [X] T015d [P] [US1] Write integration test for add_task in Phase-III/backend/tests/mcp/test_add_task_integration.py (test database persistence, user isolation, error cases)
- [X] T015e [US1] Run tests and verify they FAIL (expected - tool not implemented yet)

### Implementation for User Story 1

- [X] T016 [P] [US1] Create AddTaskInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py (title: str with min/max length, description: str | None)
- [X] T017 [P] [US1] Create TaskOutput schema in Phase-III/backend/src/mcp/schemas/tool_outputs.py (id, user_id, title, description, status, version, created_at, updated_at)
- [X] T018 [US1] Implement add_task tool in Phase-III/backend/src/mcp/tools/add_task.py (extract user_id, create session, call create_task use case, return TaskOutput)
- [X] T019 [US1] Register add_task tool in Phase-III/backend/src/mcp/server.py (@app.tool() decorator)
- [X] T020 [US1] Add input validation error handling to add_task tool (catch ValidationError, return INVALID_INPUT error)
- [X] T021 [US1] Add database error handling to add_task tool (catch database exceptions, return DATABASE_ERROR)
- [X] T022 [US1] Add authentication error handling to add_task tool (catch auth exceptions, return UNAUTHORIZED)
- [X] T023 [US1] Add structured logging for add_task operations in Phase-III/backend/src/mcp/tools/add_task.py (log tool invocation, user_id, execution time)

**Checkpoint**: At this point, User Story 1 should be fully functional - AI agents can create tasks via add_task tool

---

## Phase 4: User Story 2 - AI Agent Retrieves User Tasks (Priority: P1)

**Goal**: Enable AI agents to retrieve user's tasks with optional status filtering, ordered newest first

**Independent Test**: Create sample tasks for a user, invoke list_tasks with different status filters (all, pending, completed). Verify only that user's tasks are returned in correct order.

### Test-First Implementation for User Story 2 (TDD)

**⚠️ CRITICAL**: Write tests FIRST, verify they FAIL, then implement

- [X] T023a [P] [US2] Write contract test for list_tasks tool in Phase-III/backend/tests/mcp/test_list_tasks_contract.py (validate input/output schemas match contracts/mcp-tools.json)
- [X] T023b [P] [US2] Write integration test for list_tasks in Phase-III/backend/tests/mcp/test_list_tasks_integration.py (test filtering, ordering, user isolation, empty results)
- [X] T023c [US2] Run tests and verify they FAIL (expected - tool not implemented yet)

### Implementation for User Story 2

- [X] T024 [P] [US2] Create ListTasksInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py (status: str with enum validation for "all", "pending", "completed")
- [X] T025 [P] [US2] Create TaskListOutput schema in Phase-III/backend/src/mcp/schemas/tool_outputs.py (tasks: list[TaskOutput], count: int)
- [X] T026 [US2] Implement list_tasks tool in Phase-III/backend/src/mcp/tools/list_tasks.py (extract user_id, create session, call list_tasks use case with status filter and descending order)
- [X] T027 [US2] Register list_tasks tool in Phase-III/backend/src/mcp/server.py (@app.tool() decorator)
- [X] T028 [US2] Add input validation error handling to list_tasks tool (catch ValidationError, return INVALID_INPUT error)
- [X] T029 [US2] Add database error handling to list_tasks tool (catch database exceptions, return DATABASE_ERROR)
- [X] T030 [US2] Add authentication error handling to list_tasks tool (catch auth exceptions, return UNAUTHORIZED)
- [X] T031 [US2] Add structured logging for list_tasks operations in Phase-III/backend/src/mcp/tools/list_tasks.py (log tool invocation, user_id, filter, result count, execution time)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - AI agents can create and list tasks

---

## Phase 5: User Story 3 - AI Agent Marks Task Complete (Priority: P2)

**Goal**: Enable AI agents to mark tasks as completed, with idempotent behavior

**Independent Test**: Create a pending task, invoke complete_task with task_id. Verify status changes to completed. Invoke again to verify idempotent behavior (no error).

### Test-First Implementation for User Story 3 (TDD)

**⚠️ CRITICAL**: Write tests FIRST, verify they FAIL, then implement

- [X] T031a [P] [US3] Write contract test for complete_task tool in Phase-III/backend/tests/mcp/test_complete_task_contract.py (validate input/output schemas match contracts/mcp-tools.json)
- [X] T031b [P] [US3] Write integration test for complete_task in Phase-III/backend/tests/mcp/test_complete_task_integration.py (test status change, idempotency, ownership validation, not found errors)
- [X] T031c [US3] Run tests and verify they FAIL (expected - tool not implemented yet)

### Implementation for User Story 3

- [X] T032 [P] [US3] Create CompleteTaskInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py (task_id: UUID)
- [X] T033 [US3] Implement complete_task tool in Phase-III/backend/src/mcp/tools/complete_task.py (extract user_id, create session, call toggle_task_completion use case, return TaskOutput)
- [X] T034 [US3] Register complete_task tool in Phase-III/backend/src/mcp/server.py (@app.tool() decorator)
- [X] T035 [US3] Add task not found error handling to complete_task tool (catch TaskNotFoundError, return TASK_NOT_FOUND error)
- [X] T036 [US3] Add ownership validation error handling to complete_task tool (verify user_id matches, return FORBIDDEN if mismatch)
- [X] T037 [US3] Add input validation error handling to complete_task tool (catch ValidationError, return INVALID_INPUT error)
- [X] T038 [US3] Add database error handling to complete_task tool (catch database exceptions, return DATABASE_ERROR)
- [X] T039 [US3] Add authentication error handling to complete_task tool (catch auth exceptions, return UNAUTHORIZED)
- [X] T040 [US3] Implement idempotent behavior in complete_task tool (if already completed, return success without error)
- [X] T041 [US3] Add structured logging for complete_task operations in Phase-III/backend/src/mcp/tools/complete_task.py (log tool invocation, user_id, task_id, execution time)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - AI agents can create, list, and complete tasks

---

## Phase 6: User Story 4 - AI Agent Updates Task Details (Priority: P3)

**Goal**: Enable AI agents to update task title and/or description with optimistic concurrency control

**Independent Test**: Create a task, invoke update_task with new title. Verify title is updated while preserving task_id and incrementing version. Test concurrent updates to verify CONFLICT error.

### Test-First Implementation for User Story 4 (TDD)

**⚠️ CRITICAL**: Write tests FIRST, verify they FAIL, then implement

- [X] T041a [P] [US4] Write contract test for update_task tool in Phase-III/backend/tests/mcp/test_update_task_contract.py (validate input/output schemas match contracts/mcp-tools.json)
- [X] T041b [P] [US4] Write integration test for update_task in Phase-III/backend/tests/mcp/test_update_task_integration.py (test field updates, version increment, optimistic locking conflicts, ownership validation)
- [X] T041c [US4] Run tests and verify they FAIL (expected - tool not implemented yet)

### Implementation for User Story 4

- [ ] T042 [P] [US4] Create UpdateTaskInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py (task_id: UUID, title: str | None with min/max length, description: str | None)
- [ ] T043 [US4] Update task_operations.py update_task use case in Phase-III/backend/src/use_cases/task_operations.py to implement optimistic locking (WHERE id = ? AND version = ?, increment version)
- [ ] T044 [US4] Implement update_task tool in Phase-III/backend/src/mcp/tools/update_task.py (extract user_id, create session, call update_task use case with version check, return TaskOutput)
- [ ] T045 [US4] Register update_task tool in Phase-III/backend/src/mcp/server.py (@app.tool() decorator)
- [ ] T046 [US4] Add task not found error handling to update_task tool (catch TaskNotFoundError, return TASK_NOT_FOUND error)
- [ ] T047 [US4] Add ownership validation error handling to update_task tool (verify user_id matches, return FORBIDDEN if mismatch)
- [ ] T048 [US4] Add optimistic concurrency conflict handling to update_task tool (if version mismatch, return CONFLICT error with current version in details)
- [ ] T049 [US4] Add input validation error handling to update_task tool (catch ValidationError for empty title, return INVALID_INPUT error)
- [ ] T050 [US4] Add database error handling to update_task tool (catch database exceptions, return DATABASE_ERROR)
- [ ] T051 [US4] Add authentication error handling to update_task tool (catch auth exceptions, return UNAUTHORIZED)
- [ ] T052 [US4] Add structured logging for update_task operations in Phase-III/backend/src/mcp/tools/update_task.py (log tool invocation, user_id, task_id, version, execution time)

**Checkpoint**: At this point, User Stories 1-4 should all work independently - AI agents can create, list, complete, and update tasks

---

## Phase 7: User Story 5 - AI Agent Deletes Task (Priority: P3)

**Goal**: Enable AI agents to permanently delete tasks with ownership enforcement

**Independent Test**: Create a task, invoke delete_task with task_id. Verify task is removed from database and no longer appears in list_tasks results.

### Test-First Implementation for User Story 5 (TDD)

**⚠️ CRITICAL**: Write tests FIRST, verify they FAIL, then implement

- [ ] T062a [P] [US5] Write contract test for delete_task tool in Phase-III/backend/tests/mcp/test_delete_task_contract.py (validate input/output schemas match contracts/mcp-tools.json)
- [ ] T062b [P] [US5] Write integration test for delete_task in Phase-III/backend/tests/mcp/test_delete_task_integration.py (test deletion, ownership validation, not found errors, verify removal from list_tasks)
- [ ] T062c [US5] Run tests and verify they FAIL (expected - tool not implemented yet)

### Implementation for User Story 5

- [ ] T053 [P] [US5] Create DeleteTaskInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py (task_id: UUID)
- [ ] T054 [P] [US5] Create DeleteTaskOutput schema in Phase-III/backend/src/mcp/schemas/tool_outputs.py (message: str, task_id: UUID)
- [ ] T055 [US5] Implement delete_task tool in Phase-III/backend/src/mcp/tools/delete_task.py (extract user_id, create session, call delete_task use case, return DeleteTaskOutput)
- [ ] T056 [US5] Register delete_task tool in Phase-III/backend/src/mcp/server.py (@app.tool() decorator)
- [ ] T057 [US5] Add task not found error handling to delete_task tool (catch TaskNotFoundError, return TASK_NOT_FOUND error)
- [ ] T058 [US5] Add ownership validation error handling to delete_task tool (verify user_id matches, return FORBIDDEN if mismatch)
- [ ] T059 [US5] Add input validation error handling to delete_task tool (catch ValidationError, return INVALID_INPUT error)
- [ ] T060 [US5] Add database error handling to delete_task tool (catch database exceptions, return DATABASE_ERROR)
- [ ] T061 [US5] Add authentication error handling to delete_task tool (catch auth exceptions, return UNAUTHORIZED)
- [ ] T062 [US5] Add structured logging for delete_task operations in Phase-III/backend/src/mcp/tools/delete_task.py (log tool invocation, user_id, task_id, execution time)

**Checkpoint**: All user stories should now be independently functional - AI agents have full CRUD capabilities via MCP tools

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T063 [P] Export all tool schemas in Phase-III/backend/src/mcp/schemas/__init__.py
- [ ] T064 [P] Export all tools in Phase-III/backend/src/mcp/tools/__init__.py
- [ ] T065 [P] Export middleware utilities in Phase-III/backend/src/mcp/middleware/__init__.py
- [ ] T066 [P] Add MCP server startup script in Phase-III/backend/src/mcp/__main__.py for running server standalone
- [ ] T067 [P] Update Phase-III/backend/.env.example with MCP configuration variables (MCP_SERVER_ENABLED, MCP_SERVER_PORT, MCP_TOOL_TIMEOUT)
- [ ] T068 Validate all 5 tools against quickstart.md test scenarios (add_task, list_tasks, complete_task, update_task, delete_task)
- [ ] T069 [P] Add performance logging for tool execution times in Phase-III/backend/src/mcp/middleware/auth_context.py
- [ ] T070 [P] Add health check endpoint for MCP server in Phase-III/backend/src/mcp/server.py
- [ ] T071 Verify stateless architecture (restart server, verify all tools still work with database state)
- [ ] T072 Verify user isolation (test with multiple user tokens, ensure no cross-user data access)
- [ ] T073 Verify optimistic concurrency (simulate concurrent updates, verify CONFLICT errors)
- [ ] T074 [P] Update Phase-III/backend/README.md with MCP server documentation
- [ ] T075 Code cleanup and remove any unused imports across MCP module

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P3 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1)
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1/US2)
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Depends on T043 (optimistic locking in use case)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories (can run parallel with US1-4)

### Within Each User Story

- Schemas before tool implementation
- Tool implementation before registration
- Core implementation before error handling
- Error handling before logging
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002-T006 can all run in parallel (different directories)
- **Phase 2 (Foundational)**: T010-T014 can run in parallel (different files)
- **Phase 3 (US1)**: T016-T017 can run in parallel (different schema files)
- **Phase 4 (US2)**: T024-T025 can run in parallel (different schema files)
- **Phase 5 (US3)**: T032 is single schema file
- **Phase 6 (US4)**: T042 is single schema file
- **Phase 7 (US5)**: T053-T054 can run in parallel (different schema files)
- **Phase 8 (Polish)**: T063-T067, T069-T070, T074 can all run in parallel (different files)
- **Cross-Story Parallelism**: After Phase 2, all user stories (Phase 3-7) can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch schema creation tasks together:
Task T016: "Create AddTaskInput schema in Phase-III/backend/src/mcp/schemas/tool_inputs.py"
Task T017: "Create TaskOutput schema in Phase-III/backend/src/mcp/schemas/tool_outputs.py"

# Then implement tool (depends on schemas):
Task T018: "Implement add_task tool in Phase-III/backend/src/mcp/tools/add_task.py"
```

---

## Parallel Example: Multiple User Stories

```bash
# After Foundational phase completes, launch all user stories in parallel:
Developer A: Phase 3 (User Story 1 - add_task)
Developer B: Phase 4 (User Story 2 - list_tasks)
Developer C: Phase 5 (User Story 3 - complete_task)
Developer D: Phase 6 (User Story 4 - update_task)
Developer E: Phase 7 (User Story 5 - delete_task)
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T015) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 - add_task (T016-T023)
4. Complete Phase 4: User Story 2 - list_tasks (T024-T031)
5. **STOP and VALIDATE**: Test add_task and list_tasks independently
6. Deploy/demo if ready - AI agents can now create and view tasks

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (T001-T015)
2. Add User Story 1 (add_task) → Test independently → Deploy/Demo (T016-T023)
3. Add User Story 2 (list_tasks) → Test independently → Deploy/Demo (T024-T031)
4. Add User Story 3 (complete_task) → Test independently → Deploy/Demo (T032-T041)
5. Add User Story 4 (update_task) → Test independently → Deploy/Demo (T042-T052)
6. Add User Story 5 (delete_task) → Test independently → Deploy/Demo (T053-T062)
7. Polish & validate → Final deployment (T063-T075)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T015)
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T023)
   - Developer B: User Story 2 (T024-T031)
   - Developer C: User Story 3 (T032-T041)
   - Developer D: User Story 4 (T042-T052)
   - Developer E: User Story 5 (T053-T062)
3. Stories complete and integrate independently
4. Team completes Polish together (T063-T075)

---

## Task Summary

**Total Tasks**: 75

**Tasks by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 9 tasks
- Phase 3 (User Story 1 - add_task): 8 tasks
- Phase 4 (User Story 2 - list_tasks): 8 tasks
- Phase 5 (User Story 3 - complete_task): 10 tasks
- Phase 6 (User Story 4 - update_task): 11 tasks
- Phase 7 (User Story 5 - delete_task): 10 tasks
- Phase 8 (Polish): 13 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- **US1**: Invoke add_task, verify task created in database
- **US2**: Invoke list_tasks, verify correct tasks returned in order
- **US3**: Invoke complete_task, verify status changed to completed
- **US4**: Invoke update_task, verify changes persisted with version increment
- **US5**: Invoke delete_task, verify task removed from database

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 + Phase 4 (User Stories 1 & 2 - create and list tasks)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks follow strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Tests are NOT included as they were not explicitly requested in the specification
- Optimistic concurrency control (version field) is implemented in User Story 4
- All tools enforce user isolation via JWT token extraction
- All tools return standardized error format with machine-readable codes
