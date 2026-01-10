# Tasks: End-to-End Testing for Phase 2

**Input**: Design documents from `/specs/001-e2e-testing/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- Backend tests: `phase-2/backend/tests/`
- Frontend tests: `phase-2/frontend/tests/e2e/`
- Shared fixtures: `phase-2/backend/tests/fixtures/`
- Test utilities: `phase-2/backend/tests/utils/`

---

## Phase 1: Setup (Test Infrastructure)

**Purpose**: Initialize test infrastructure and configuration

- [ ] T001 Create pytest configuration file in phase-2/backend/tests/pytest.ini
- [ ] T002 Create pytest conftest.py with base fixtures in phase-2/backend/tests/conftest.py
- [ ] T003 [P] Create test environment configuration template in phase-2/.env.test.example
- [ ] T004 [P] Create test fixtures directory structure in phase-2/backend/tests/fixtures/
- [ ] T005 [P] Create test utilities directory structure in phase-2/backend/tests/utils/
- [ ] T006 [P] Create integration tests directory in phase-2/backend/tests/integration/
- [ ] T007 [P] Create contract tests directory in phase-2/backend/tests/contract/
- [ ] T008 [P] Create frontend E2E tests directory in phase-2/frontend/tests/e2e/
- [ ] T009 Install backend testing dependencies (pytest, pytest-asyncio, httpx, psycopg2-binary, faker)

---

## Phase 2: Foundational (Shared Test Infrastructure)

**Purpose**: Core test utilities and fixtures that ALL user stories depend on

**⚠️ CRITICAL**: No user story test implementation can begin until this phase is complete

- [ ] T010 Implement database connection fixture in phase-2/backend/tests/fixtures/database.py
- [ ] T011 Implement transactional rollback fixture in phase-2/backend/tests/fixtures/database.py
- [ ] T012 [P] Implement test user factory in phase-2/backend/tests/fixtures/test_users.py
- [ ] T013 [P] Implement test todo factory in phase-2/backend/tests/fixtures/test_data.py
- [ ] T014 [P] Implement HTTP client wrapper in phase-2/backend/tests/utils/api_client.py
- [ ] T015 [P] Implement database client wrapper in phase-2/backend/tests/utils/db_client.py
- [ ] T016 [P] Implement custom assertions helper in phase-2/backend/tests/utils/assertions.py
- [ ] T017 [P] Implement JWT token generator utility in phase-2/backend/tests/utils/auth_helpers.py
- [ ] T018 Configure test database connection string and environment variables

**Checkpoint**: Foundation ready - user story test implementation can now begin in parallel

---

## Phase 3: User Story 1 - Complete Authentication Flow Validation (Priority: P1) 🎯 MVP

**Goal**: Validate complete user authentication lifecycle from signup through authenticated access, ensuring security best practices and JWT token handling

**Independent Test**: Execute signup → signin → access protected dashboard → logout sequence in real browser and verify all authentication boundaries work correctly

### Backend Integration Tests for User Story 1

- [ ] T019 [P] [US1] Implement signup endpoint test in phase-2/backend/tests/integration/test_auth.py
- [ ] T020 [P] [US1] Implement signin endpoint test in phase-2/backend/tests/integration/test_auth.py
- [ ] T021 [P] [US1] Implement logout endpoint test in phase-2/backend/tests/integration/test_auth.py
- [ ] T022 [P] [US1] Implement JWT token validation test in phase-2/backend/tests/integration/test_auth.py
- [ ] T023 [P] [US1] Implement password hashing verification test in phase-2/backend/tests/integration/test_auth.py
- [ ] T024 [P] [US1] Implement protected route authorization test in phase-2/backend/tests/integration/test_auth.py
- [ ] T025 [P] [US1] Implement unauthorized access rejection test in phase-2/backend/tests/integration/test_auth.py

### Contract Tests for User Story 1

- [ ] T026 [P] [US1] Implement auth contract validation test in phase-2/backend/tests/contract/test_auth_contract.py
- [ ] T027 [P] [US1] Implement JWT token structure validation test in phase-2/backend/tests/contract/test_auth_contract.py

### Frontend E2E Tests for User Story 1

- [ ] T028 [US1] Implement signup flow E2E test in phase-2/frontend/tests/e2e/auth.spec.ts
- [ ] T029 [US1] Implement signin flow E2E test in phase-2/frontend/tests/e2e/auth.spec.ts
- [ ] T030 [US1] Implement logout flow E2E test in phase-2/frontend/tests/e2e/auth.spec.ts
- [ ] T031 [US1] Implement protected route redirect test in phase-2/frontend/tests/e2e/auth.spec.ts
- [ ] T032 [US1] Implement authentication state persistence test in phase-2/frontend/tests/e2e/auth.spec.ts

**Checkpoint**: At this point, User Story 1 (Authentication) should be fully validated and all auth tests passing

---

## Phase 4: User Story 2 - Backend API Contract Validation (Priority: P2)

**Goal**: Validate that all FastAPI backend endpoints conform to documented contracts, handle requests correctly, and enforce authentication

**Independent Test**: Make HTTP requests to all REST endpoints with various payloads, verify response schemas, status codes, and database state changes

### Backend Integration Tests for User Story 2

- [ ] T033 [P] [US2] Implement create todo API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T034 [P] [US2] Implement list todos API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T035 [P] [US2] Implement get todo by ID API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T036 [P] [US2] Implement update todo API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T037 [P] [US2] Implement delete todo API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T038 [P] [US2] Implement toggle todo completion API test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T039 [P] [US2] Implement unauthorized API access test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T040 [P] [US2] Implement invalid payload validation test in phase-2/backend/tests/integration/test_api_todos.py
- [ ] T041 [P] [US2] Implement user data isolation test in phase-2/backend/tests/integration/test_api_todos.py

### Contract Tests for User Story 2

- [ ] T042 [P] [US2] Implement API contract validation test in phase-2/backend/tests/contract/test_api_contract.py
- [ ] T043 [P] [US2] Implement response schema validation test in phase-2/backend/tests/contract/test_api_contract.py
- [ ] T044 [P] [US2] Implement HTTP status code validation test in phase-2/backend/tests/contract/test_api_contract.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both be fully validated

---

## Phase 5: User Story 3 - Database Integration and Schema Validation (Priority: P3)

**Goal**: Validate database schema is correctly created, migrations execute successfully, data persists correctly, and user data isolation is enforced

**Independent Test**: Connect to test database, run migrations, execute CRUD operations, and verify schema structure and data isolation

### Database Integration Tests for User Story 3

- [ ] T045 [P] [US3] Implement database schema validation test in phase-2/backend/tests/integration/test_database.py
- [ ] T046 [P] [US3] Implement migration execution test in phase-2/backend/tests/integration/test_database.py
- [ ] T047 [P] [US3] Implement data persistence test in phase-2/backend/tests/integration/test_database.py
- [ ] T048 [P] [US3] Implement user data isolation test in phase-2/backend/tests/integration/test_database.py
- [ ] T049 [P] [US3] Implement password hashing storage test in phase-2/backend/tests/integration/test_database.py
- [ ] T050 [P] [US3] Implement database connection test in phase-2/backend/tests/integration/test_database.py
- [ ] T051 [P] [US3] Implement cascade delete test in phase-2/backend/tests/integration/test_database.py
- [ ] T052 [P] [US3] Implement timestamp auto-update test in phase-2/backend/tests/integration/test_database.py

### Contract Tests for User Story 3

- [ ] T053 [P] [US3] Implement database schema contract validation test in phase-2/backend/tests/contract/test_database_schema.py
- [ ] T054 [P] [US3] Implement table structure validation test in phase-2/backend/tests/contract/test_database_schema.py
- [ ] T055 [P] [US3] Implement constraint validation test in phase-2/backend/tests/contract/test_database_schema.py

**Checkpoint**: All backend validation (Auth, API, Database) should now be complete and passing

---

## Phase 6: User Story 4 - Frontend Integration and User Journey Validation (Priority: P4)

**Goal**: Validate Next.js frontend correctly integrates with backend, renders pages properly, handles authentication state, and provides complete user experience

**Independent Test**: Navigate through application in real browser, interact with forms, and verify UI state updates reflect backend changes

### Frontend E2E Tests for User Story 4

- [ ] T056 [P] [US4] Implement landing page rendering test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T057 [P] [US4] Implement dashboard rendering test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T058 [US4] Implement create todo UI flow test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T059 [US4] Implement update todo UI flow test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T060 [US4] Implement delete todo UI flow test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T061 [US4] Implement toggle todo completion UI flow test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T062 [US4] Implement todo list display test in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T063 [US4] Implement UI state persistence test (page refresh) in phase-2/frontend/tests/e2e/todos.spec.ts
- [ ] T064 [US4] Implement form validation error display test in phase-2/frontend/tests/e2e/todos.spec.ts

### Responsive UI Tests for User Story 4

- [ ] T065 [P] [US4] Implement mobile viewport rendering test in phase-2/frontend/tests/e2e/responsive.spec.ts
- [ ] T066 [P] [US4] Implement tablet viewport rendering test in phase-2/frontend/tests/e2e/responsive.spec.ts
- [ ] T067 [P] [US4] Implement desktop viewport rendering test in phase-2/frontend/tests/e2e/responsive.spec.ts

**Checkpoint**: All user stories should now be independently validated and all tests passing

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and validations that affect multiple user stories

- [ ] T068 [P] Create test execution documentation in specs/001-e2e-testing/quickstart.md (verify existing)
- [ ] T069 [P] Create test reporting configuration for pytest-html
- [ ] T070 [P] Implement test data cleanup verification
- [ ] T071 [P] Add test execution time tracking and validation (<5 minutes target)
- [ ] T072 [P] Implement edge case tests for expired JWT tokens
- [ ] T073 [P] Implement edge case tests for malformed JWT tokens
- [ ] T074 [P] Implement edge case tests for concurrent operations
- [ ] T075 [P] Implement edge case tests for special characters in todo content
- [ ] T076 [P] Implement edge case tests for duplicate email signup
- [ ] T077 [P] Implement edge case tests for empty todo content
- [ ] T078 Validate all tests are deterministic (run suite 3 times, verify consistent results)
- [ ] T079 Validate test suite execution time (<5 minutes)
- [ ] T080 Run complete test suite and generate coverage report
- [ ] T081 Validate quickstart.md instructions work correctly
- [ ] T082 Create CI/CD integration documentation

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
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 auth fixtures but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with US1 auth but independently testable

### Within Each User Story

- Backend integration tests can run in parallel (marked [P])
- Contract tests can run in parallel (marked [P])
- Frontend E2E tests should run sequentially (browser state dependencies)
- All tests for a story should pass before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T003-T008)
- All Foundational tasks marked [P] can run in parallel (T012-T017)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each user story, all tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Authentication Tests)

```bash
# Launch all backend integration tests for US1 together:
Task: "Implement signup endpoint test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement signin endpoint test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement logout endpoint test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement JWT token validation test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement password hashing verification test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement protected route authorization test in phase-2/backend/tests/integration/test_auth.py"
Task: "Implement unauthorized access rejection test in phase-2/backend/tests/integration/test_auth.py"

# Launch all contract tests for US1 together:
Task: "Implement auth contract validation test in phase-2/backend/tests/contract/test_auth_contract.py"
Task: "Implement JWT token structure validation test in phase-2/backend/tests/contract/test_auth_contract.py"
```

---

## Parallel Example: User Story 2 (API Contract Tests)

```bash
# Launch all backend integration tests for US2 together:
Task: "Implement create todo API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement list todos API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement get todo by ID API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement update todo API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement delete todo API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement toggle todo completion API test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement unauthorized API access test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement invalid payload validation test in phase-2/backend/tests/integration/test_api_todos.py"
Task: "Implement user data isolation test in phase-2/backend/tests/integration/test_api_todos.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T018) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T019-T032)
4. **STOP and VALIDATE**: Run all US1 tests, verify authentication flow works end-to-end
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Validate auth works (MVP!)
3. Add User Story 2 → Test independently → Validate API contracts work
4. Add User Story 3 → Test independently → Validate database integration works
5. Add User Story 4 → Test independently → Validate frontend integration works
6. Each story adds validation coverage without breaking previous tests

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T018)
2. Once Foundational is done:
   - Developer A: User Story 1 (Authentication tests)
   - Developer B: User Story 2 (API contract tests)
   - Developer C: User Story 3 (Database tests)
   - Developer D: User Story 4 (Frontend E2E tests)
3. Stories complete and validate independently

---

## Test Execution Validation

### Success Criteria

- ✅ All 82 tasks completed
- ✅ Complete test suite executes in under 5 minutes
- ✅ 100% of tests pass consistently (0% flaky tests)
- ✅ All authentication flows validated end-to-end
- ✅ All API contracts validated against specifications
- ✅ Database schema and data isolation validated
- ✅ Frontend integration validated in real browser
- ✅ Test data cleanup verified (no leftover data)
- ✅ All edge cases covered

### Test Coverage Targets

- **Authentication**: 100% of auth flows (signup, signin, logout, protected routes)
- **API Endpoints**: 100% of CRUD operations (create, read, update, delete, toggle)
- **Database**: 100% of schema validation and data isolation
- **Frontend**: 100% of critical user journeys (landing → signup → dashboard → CRUD → logout)
- **Edge Cases**: 80% of identified edge cases

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- All tests validate existing Phase 2 implementation (no production code changes)
- Use transactional rollback for test isolation (no persistent test data)
- Playwright MCP is already installed for frontend E2E tests
- Backend tests use pytest + httpx for API testing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
