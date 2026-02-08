# Tasks: Backend Core & Data Layer

**Feature**: 003-todo-backend-core
**Input**: Design documents from `/specs/003-todo-backend-core/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This project uses web app structure:
- Backend: `Phase-II/backend/src/`, `Phase-II/backend/tests/`
- Clean architecture layers: api/, domain/, infrastructure/, use_cases/

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Phase-II/backend/ directory structure per plan.md
- [X] T002 Initialize UV project with Python 3.13+ in Phase-II/backend/
- [X] T003 [P] Install FastAPI, SQLModel, asyncpg, pydantic, python-dotenv, uvicorn dependencies
- [X] T004 [P] Install dev dependencies: pytest, pytest-asyncio, httpx, pytest-cov, ruff
- [X] T005 [P] Create .env.example with DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW, APP_ENV, LOG_LEVEL, API_HOST, API_PORT
- [X] T006 [P] Create .gitignore with .env, __pycache__, .pytest_cache, htmlcov/, .ruff_cache/
- [X] T007 [P] Configure ruff linting and formatting in pyproject.toml
- [X] T008 Create Phase-II/backend/src/ directory with __init__.py
- [X] T009 Create Phase-II/backend/tests/ directory structure: unit/, integration/, contract/, fixtures/
- [X] T010 [P] Create Phase-II/backend/README.md with quickstart instructions

**Checkpoint**: Project structure ready for foundational implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Configuration

- [X] T011 Create Phase-II/backend/src/config.py with Settings class using pydantic-settings
- [X] T012 Create Phase-II/backend/src/database.py with async engine, AsyncSession factory, get_session dependency
- [X] T013 Configure connection pooling (pool_size=10, max_overflow=20) in database.py
- [X] T014 Add database health check function in database.py

### Domain Models

- [X] T015 [P] Create Phase-II/backend/src/domain/__init__.py
- [X] T016 [P] Create Phase-II/backend/src/domain/models.py with SQLModel base
- [X] T017 Create User model in domain/models.py (id: UUID, email: EmailStr, created_at, updated_at)
- [X] T018 Create Task model in domain/models.py (id: UUID, user_id: UUID FK, title: str, description: str|None, status: enum, timestamps)
- [X] T019 Create TaskStatus enum in domain/models.py (PENDING, COMPLETED)
- [X] T020 Add table creation function in domain/models.py using SQLModel.metadata.create_all

### API Infrastructure

- [X] T021 [P] Create Phase-II/backend/src/api/__init__.py
- [X] T022 Create Phase-II/backend/src/middleware/logging.py with structured JSON logging middleware
- [X] T023 Create Phase-II/backend/src/middleware/error_handler.py with RFC 7807 Problem Details exception handler
- [X] T024 Create Phase-II/backend/src/schemas/__init__.py for Pydantic request/response schemas
- [X] T025 Create Phase-II/backend/src/main.py with FastAPI app factory, middleware registration, startup/shutdown events

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and Retrieve Personal Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks and retrieve individual tasks by ID

**Independent Test**: Create a task via POST, then retrieve it via GET by ID - verify task data matches

### Tests for User Story 1 (TDD - Write FIRST, ensure FAIL)

- [X] T026 [P] [US1] Create tests/fixtures/test_users.py with user fixture (UUID: 550e8400-e29b-41d4-a716-446655440000)
- [X] T027 [P] [US1] Create tests/fixtures/database.py with async test database session fixture
- [X] T028 [P] [US1] Contract test for POST /users/{user_id}/tasks in tests/contract/test_create_task.py
- [X] T029 [P] [US1] Contract test for GET /users/{user_id}/tasks/{task_id} in tests/contract/test_get_task.py
- [X] T030 [P] [US1] Integration test for create-then-retrieve journey in tests/integration/test_task_lifecycle.py

### Schemas for User Story 1

- [X] T031 [P] [US1] Create TaskCreate schema in src/schemas/task.py (title: str, description: str|None)
- [X] T032 [P] [US1] Create TaskResponse schema in src/schemas/task.py (id, user_id, title, description, status, created_at, updated_at)
- [X] T033 [P] [US1] Create ErrorResponse schema in src/schemas/error.py (RFC 7807: type, title, status, detail, instance)

### Use Cases for User Story 1

- [X] T034 [P] [US1] Create src/use_cases/__init__.py
- [X] T035 [US1] Implement create_task use case in src/use_cases/task_operations.py (validate title 1-200 chars, set user_id, generate UUID, set timestamps)
- [X] T036 [US1] Implement get_task_by_id use case in src/use_cases/task_operations.py (verify ownership: task.user_id == user_id, raise 404 if not found/not owned)

### API Endpoints for User Story 1

- [X] T037 Create src/api/routes/__init__.py
- [X] T038 Create src/api/routes/health.py with GET /health endpoint (status: healthy, timestamp)
- [X] T039 [US1] Create src/api/routes/tasks.py with router setup
- [X] T040 [US1] Implement POST /users/{user_id}/tasks endpoint in tasks.py (201 Created, Location header, return TaskResponse)
- [X] T041 [US1] Implement GET /users/{user_id}/tasks/{task_id} endpoint in tasks.py (200 OK or 404 Not Found)
- [X] T042 [US1] Add input validation for user_id and task_id path parameters (UUID format)
- [X] T043 [US1] Add error handling for database connection failures (503 Service Unavailable)
- [X] T044 [US1] Register tasks router in src/main.py with prefix /users/{user_id}/tasks
- [X] T045 [US1] Run tests for User Story 1 - verify all pass

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Update and Delete Personal Tasks (Priority: P2)

**Goal**: Users can update existing tasks (full or partial) and delete tasks they own

**Independent Test**: Create task, update it via PUT, verify changes, then delete via DELETE, verify 404 on subsequent GET

### Tests for User Story 2 (TDD - Write FIRST, ensure FAIL)

- [X] T046 [P] [US2] Contract test for PUT /users/{user_id}/tasks/{task_id} in tests/contract/test_update_task.py
- [X] T047 [P] [US2] Contract test for DELETE /users/{user_id}/tasks/{task_id} in tests/contract/test_delete_task.py
- [X] T048 [P] [US2] Contract test for PATCH /users/{user_id}/tasks/{task_id}/complete in tests/contract/test_complete_task.py
- [X] T049 [US2] Integration test for update-then-delete journey in tests/integration/test_task_mutations.py

### Schemas for User Story 2

- [X] T050 [P] [US2] Create TaskUpdate schema in src/schemas/task.py (title: str|None, description: str|None, status: TaskStatus|None)
- [X] T051 [P] [US2] Add validation to TaskUpdate: at least one field must be provided

### Use Cases for User Story 2

- [X] T052 [US2] Implement update_task use case in src/use_cases/task_operations.py (verify ownership, validate fields, update updated_at timestamp)
- [X] T053 [US2] Implement delete_task use case in src/use_cases/task_operations.py (verify ownership, hard delete - permanent removal)
- [X] T054 [US2] Implement toggle_task_completion use case in src/use_cases/task_operations.py (toggle PENDING ↔ COMPLETED)

### API Endpoints for User Story 2

- [X] T055 [US2] Implement PUT /users/{user_id}/tasks/{task_id} endpoint in src/api/routes/tasks.py (200 OK, return updated TaskResponse)
- [X] T056 [US2] Implement DELETE /users/{user_id}/tasks/{task_id} endpoint in src/api/routes/tasks.py (204 No Content)
- [X] T057 [US2] Implement PATCH /users/{user_id}/tasks/{task_id}/complete endpoint in src/api/routes/tasks.py (200 OK, return TaskResponse)
- [X] T058 [US2] Add ownership verification for all mutation endpoints (403 Forbidden if user doesn't own task)
- [X] T059 [US2] Add optimistic concurrency handling (check updated_at if needed)
- [X] T060 [US2] Run tests for User Story 2 - verify all pass

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - List and Filter Personal Tasks (Priority: P3)

**Goal**: Users can list all their tasks with pagination and filter by status

**Independent Test**: Create 25 tasks (15 pending, 10 completed), list with pagination (limit=10), filter by status=pending, verify counts and data

### Tests for User Story 3 (TDD - Write FIRST, ensure FAIL)

- [X] T061 [P] [US3] Contract test for GET /users/{user_id}/tasks with pagination in tests/contract/test_list_tasks.py
- [X] T062 [P] [US3] Contract test for GET /users/{user_id}/tasks?status=pending in tests/contract/test_filter_tasks.py
- [X] T063 [US3] Integration test for pagination navigation (offset/limit) in tests/integration/test_task_pagination.py
- [X] T064 [US3] Integration test for status filtering in tests/integration/test_task_filtering.py

### Schemas for User Story 3

- [X] T065 [P] [US3] Create PaginatedTaskResponse schema in src/schemas/task.py (items: list[TaskResponse], total: int, offset: int, limit: int, has_next: bool, has_previous: bool)
- [X] T066 [P] [US3] Create TaskListParams schema in src/schemas/task.py (status: TaskStatus|None, offset: int=0, limit: int=20)

### Use Cases for User Story 3

- [X] T067 [US3] Implement list_tasks use case in src/use_cases/task_operations.py (filter by user_id, optional status filter, apply offset/limit)
- [X] T068 [US3] Implement count_tasks use case in src/use_cases/task_operations.py (count total matching tasks for pagination metadata)
- [X] T069 [US3] Add pagination metadata calculation (has_next, has_previous) in list_tasks use case

### API Endpoints for User Story 3

- [X] T070 [US3] Implement GET /users/{user_id}/tasks endpoint in src/api/routes/tasks.py (200 OK, return PaginatedTaskResponse)
- [X] T071 [US3] Add query parameters: status (optional), offset (default=0), limit (default=20, max=100)
- [X] T072 [US3] Add validation for pagination parameters (offset >= 0, 1 <= limit <= 100)
- [X] T073 [US3] Add database indexes for performance: (user_id, status), (user_id, created_at DESC)
- [X] T074 [US3] Add sorting by created_at DESC (newest first)
- [X] T075 [US3] Run tests for User Story 3 - verify all pass

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Documentation

- [X] T076 [P] Update Phase-II/backend/README.md with API usage examples from quickstart.md
- [X] T077 [P] Create Phase-II/backend/docs/API.md with complete endpoint documentation
- [X] T078 [P] Add inline docstrings to all use cases and API endpoints

### Testing & Quality

- [X] T079 Run full test suite with coverage report (target: 80%+ coverage)
- [X] T080 [P] Add unit tests for edge cases in tests/unit/test_task_validation.py
- [X] T081 [P] Add unit tests for pagination logic in tests/unit/test_pagination.py
- [X] T082 Run ruff linting and fix all issues
- [X] T083 Run ruff formatting on all source files

### Deployment Readiness

- [X] T084 Verify quickstart.md instructions work end-to-end
- [X] T085 Create Phase-II/backend/.env.test for test database configuration
- [X] T086 [P] Add database migration strategy documentation in docs/MIGRATIONS.md
- [X] T087 [P] Add logging configuration for production in src/config.py
- [X] T088 Verify all environment variables are documented in .env.example

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 endpoints but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Uses US1 schemas but independently testable

### Within Each User Story

1. Tests MUST be written FIRST and FAIL before implementation (TDD)
2. Schemas before use cases
3. Use cases before API endpoints
4. Core implementation before integration
5. Story complete and tested before moving to next priority

### Parallel Opportunities

- **Phase 1**: T003, T004, T005, T006, T007, T010 can run in parallel
- **Phase 2**: T015, T016, T021 can run in parallel
- **User Story 1 Tests**: T026, T027, T028, T029, T030 can run in parallel
- **User Story 1 Schemas**: T031, T032, T033 can run in parallel
- **User Story 1 Use Cases**: T034, T035 can run in parallel (T036 depends on T035)
- **User Story 2 Tests**: T046, T047, T048 can run in parallel
- **User Story 2 Schemas**: T050, T051 can run in parallel
- **User Story 3 Tests**: T061, T062 can run in parallel
- **User Story 3 Schemas**: T065, T066 can run in parallel
- **Polish**: T076, T077, T078, T080, T081, T086, T087 can run in parallel
- **All user stories (Phase 3-5)** can be worked on in parallel by different team members after Phase 2 completes

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD - write first):
Task T026: "Create tests/fixtures/test_users.py with user fixture"
Task T027: "Create tests/fixtures/database.py with async test database session fixture"
Task T028: "Contract test for POST /users/{user_id}/tasks"
Task T029: "Contract test for GET /users/{user_id}/tasks/{task_id}"
Task T030: "Integration test for create-then-retrieve journey"

# Launch all schemas for User Story 1 together:
Task T031: "Create TaskCreate schema in src/schemas/task.py"
Task T032: "Create TaskResponse schema in src/schemas/task.py"
Task T033: "Create ErrorResponse schema in src/schemas/error.py"

# Then implement use cases sequentially:
Task T035: "Implement create_task use case"
Task T036: "Implement get_task_by_id use case" (depends on T035)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T025) - CRITICAL
3. Complete Phase 3: User Story 1 (T026-T045)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Polish → Final production-ready release

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T025)
2. Once Foundational is done:
   - Developer A: User Story 1 (T026-T045)
   - Developer B: User Story 2 (T046-T060)
   - Developer C: User Story 3 (T061-T075)
3. Stories complete and integrate independently
4. Team completes Polish together (T076-T088)

---

## Notes

- **[P]** tasks = different files, no dependencies, can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD**: Verify tests fail before implementing (Red → Green → Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All tasks include exact file paths for clarity
- User isolation enforced at query level (always filter by user_id)
- UUID v4 identifiers prevent enumeration attacks
- RFC 7807 error responses for consistent error handling
- Structured JSON logging for observability
- Offset/limit pagination with metadata (total, has_next, has_previous)

---

## Task Count Summary

- **Phase 1 (Setup)**: 10 tasks (T001-T010)
- **Phase 2 (Foundational)**: 15 tasks (T011-T025)
- **Phase 3 (User Story 1)**: 20 tasks (T026-T045)
- **Phase 4 (User Story 2)**: 15 tasks (T046-T060)
- **Phase 5 (User Story 3)**: 15 tasks (T061-T075)
- **Phase 6 (Polish)**: 13 tasks (T076-T088)
- **Total**: 88 tasks

**Estimated Effort** (assuming 1 task = 30-60 minutes):
- MVP (Phases 1-3): ~45 tasks = 22-45 hours
- Full Feature (All phases): ~88 tasks = 44-88 hours
