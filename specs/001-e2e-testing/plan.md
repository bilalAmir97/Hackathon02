# Implementation Plan: End-to-End Testing for Phase 2

**Branch**: `001-e2e-testing` | **Date**: 2026-01-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-e2e-testing/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement comprehensive end-to-end testing infrastructure for Phase 2 system, validating the complete integration of authentication (Better Auth + JWT), database (Neon PostgreSQL), FastAPI backend REST APIs, and Next.js frontend. The test suite will execute all critical user journeys in real browser environments, verify API contracts, validate database schema and data isolation, and ensure security boundaries are properly enforced. Tests must be deterministic, repeatable, and execute in under 5 minutes.

## Technical Context

**Language/Version**: Python 3.13+ (backend testing), TypeScript/JavaScript (frontend testing)
**Primary Dependencies**: Playwright (browser automation), pytest (test framework), httpx (HTTP client), psycopg2 (PostgreSQL client)
**Storage**: Neon PostgreSQL test database (isolated from production)
**Testing**: pytest, pytest-asyncio, Playwright Test Runner
**Target Platform**: Web application (FastAPI backend + Next.js frontend)
**Project Type**: Web testing suite (E2E + integration + contract tests)
**Performance Goals**: Complete test suite execution in under 5 minutes, individual tests under 30 seconds
**Constraints**: Must use isolated test database, no production data, 0% flaky tests, deterministic execution
**Scale/Scope**: 4 user stories, 20+ functional requirements, testing authentication + database + backend APIs + frontend UI

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development Mandate
- Approved spec exists at `/specs/001-e2e-testing/spec.md`
- Following workflow: Constitution → Spec → Plan → Tasks → Implementation
- All test code will reference spec requirements

### ✅ Agent Behavior Rules
- No production code modification (testing only)
- All decisions documented in this plan
- Using external tools (Playwright, pytest) as authoritative sources
- Will stop and request clarification if Phase 2 implementation is incomplete

### ✅ Phase Governance
- This is a testing feature for Phase 2 validation
- Tests validate ONLY Basic Level features (Phase 2 scope)
- No future-phase features tested (Intermediate/Advanced features are Phase 5)
- Tests do not implement new application features

### ✅ Test-Driven Development
- This feature IS the test implementation for Phase 2
- Tests will validate all Phase 2 user stories and acceptance criteria
- Test coverage target: 100% of critical user journeys

### ✅ Clean Architecture
- Test structure will follow layered approach:
  - E2E tests (outer layer): Full user journey validation
  - Integration tests (middle layer): API + database validation
  - Contract tests (inner layer): Schema and contract validation
- Test fixtures and utilities will be reusable and maintainable

### ✅ Contract-First Design
- Tests will validate API contracts defined in Phase 2 specs
- Contract tests will verify OpenAPI specifications
- Database schema tests will validate migration outputs

### ✅ Security & Compliance
- Tests validate JWT authentication and authorization
- Tests verify user data isolation
- Tests confirm password hashing (no plaintext storage)
- Tests use isolated test database (no production data)

### ✅ Feature Progression Governance
- Tests validate ONLY Basic Level features for Phase 2:
  - Add Task, Delete Task, Update Task, View Task List, Mark as Complete
- No tests for Intermediate or Advanced features (Phase 5 only)

### ⚠️ Observability & Monitoring
- Test reporting will provide clear pass/fail status
- Failed tests will capture HTTP requests/responses and database state
- Test execution time will be tracked for performance validation

**GATE STATUS**: ✅ PASS - All applicable constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/001-e2e-testing/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (testing frameworks, best practices)
├── data-model.md        # Phase 1 output (test data models, fixtures)
├── quickstart.md        # Phase 1 output (how to run tests locally)
└── contracts/           # Phase 1 output (test contracts, expected schemas)
    ├── auth-contract.json       # Authentication flow contract
    ├── api-contract.json        # REST API contract validation
    └── database-schema.sql      # Expected database schema
```

### Source Code (repository root)

```text
phase-2/
├── backend/
│   ├── src/                      # Backend application code (existing)
│   │   └── app/                  # FastAPI application
│   └── tests/                    # Backend tests (existing directory)
│       ├── integration/          # Backend integration tests (to be created)
│       │   ├── test_auth.py      # Authentication middleware tests
│       │   ├── test_api_todos.py # Todo CRUD API tests
│       │   └── test_database.py  # Database integration tests
│       ├── contract/             # API contract validation tests (to be created)
│       │   └── test_openapi.py   # OpenAPI spec validation
│       ├── fixtures/             # Shared test fixtures (to be created)
│       │   ├── database.py       # Database setup/teardown
│       │   ├── test_users.py     # Test user fixtures
│       │   └── test_data.py      # Test data generators
│       ├── utils/                # Test utilities (to be created)
│       │   ├── api_client.py     # HTTP client wrapper
│       │   ├── db_client.py      # Database client wrapper
│       │   └── assertions.py     # Custom assertions
│       ├── conftest.py           # Pytest configuration (to be created)
│       └── pytest.ini            # Pytest settings (to be created)
│
└── frontend/
    ├── src/                      # Frontend application code (existing)
    │   ├── app/                  # Next.js app directory
    │   ├── components/           # React components
    │   └── lib/                  # Utility libraries
    └── tests/                    # Frontend tests (to be created)
        └── e2e/                  # End-to-end browser tests
            ├── auth.spec.ts      # Authentication flow E2E tests
            ├── todos.spec.ts     # Todo CRUD E2E tests
            └── responsive.spec.ts # Responsive UI tests
```

**Structure Decision**: Tests are organized by layer (E2E, integration, contract) and co-located with the code they test. Backend tests live in `phase-2/backend/tests/` (existing directory), frontend E2E tests will be created in `phase-2/frontend/tests/e2e/`. Backend tests use pytest, frontend E2E tests use Playwright MCP (already installed). Shared fixtures and utilities are in `phase-2/backend/tests/fixtures/` and `phase-2/backend/tests/utils/` for reusability.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations. All constitution principles are satisfied for this testing feature.

---

## Phase 0: Research & Unknowns

**Objective**: Resolve all NEEDS CLARIFICATION items and research best practices for E2E testing.

### Research Outputs

All research findings documented in: `specs/001-e2e-testing/research.md`

**Key Research Areas:**
1. ✅ Playwright vs Selenium vs Cypress for browser automation
2. ✅ pytest fixtures and test isolation strategies
3. ✅ Database transaction rollback patterns for test isolation
4. ✅ JWT token validation in test scenarios
5. ✅ Contract testing best practices (OpenAPI validation)
6. ✅ Test data generation and management
7. ✅ Parallel test execution strategies
8. ✅ Test reporting and failure diagnostics

**Research Decisions:**
- **Browser Automation**: Playwright (official Microsoft tool, better async support, faster than Selenium)
- **Backend Testing**: pytest + httpx (async HTTP client, FastAPI-native)
- **Database Isolation**: Transactional fixtures with rollback (no persistent test data)
- **Contract Validation**: OpenAPI schema validation using openapi-spec-validator
- **Test Data**: Factory pattern with faker library for realistic data generation
- **Reporting**: pytest-html for backend, Playwright HTML reporter for E2E

---

## Phase 1: Design & Contracts

**Objective**: Define test data models, API contracts, and execution architecture.

### Design Outputs

**Data Model**: `specs/001-e2e-testing/data-model.md`
- Test user fixtures (email, password, JWT tokens)
- Test todo fixtures (title, description, completion status)
- Database state assertions
- Expected API response schemas

**Contracts**: `specs/001-e2e-testing/contracts/`
- ✅ `auth-contract.json` - Authentication flow contracts
- ✅ `api-contract.json` - REST API endpoint contracts
- ✅ `database-schema.sql` - Expected database schema

**Quickstart Guide**: `specs/001-e2e-testing/quickstart.md`
- Environment setup instructions
- Test execution commands
- Debugging procedures
- CI/CD integration

### Test Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     E2E Test Suite                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │   Contract   │  │ Integration  │  │     E2E      │    │
│  │    Tests     │  │    Tests     │  │   Tests      │    │
│  │              │  │              │  │              │    │
│  │ • OpenAPI    │  │ • Auth API   │  │ • Browser    │    │
│  │ • DB Schema  │  │ • Todo API   │  │ • Full Flow  │    │
│  │ • JWT Format │  │ • Database   │  │ • UI Tests   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         │                  │                  │            │
│         └──────────────────┴──────────────────┘            │
│                            │                               │
│                   ┌────────▼────────┐                      │
│                   │  Test Fixtures  │                      │
│                   │  & Utilities    │                      │
│                   └─────────────────┘                      │
│                            │                               │
│         ┌──────────────────┼──────────────────┐           │
│         │                  │                  │           │
│    ┌────▼────┐      ┌──────▼──────┐    ┌─────▼─────┐    │
│    │ Test DB │      │   Backend   │    │  Frontend │    │
│    │ (Neon)  │      │  (FastAPI)  │    │ (Next.js) │    │
│    └─────────┘      └─────────────┘    └───────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**Layer Responsibilities:**

1. **Contract Tests** (Fastest, ~10 seconds)
   - Validate OpenAPI specifications
   - Verify database schema matches expected structure
   - Validate JWT token format and claims
   - No actual API calls or database operations

2. **Integration Tests** (Fast, ~30 seconds)
   - Test backend API endpoints with real database
   - Validate authentication middleware behavior
   - Test database CRUD operations
   - Verify user data isolation
   - Use transactional fixtures for isolation

3. **E2E Tests** (Slower, ~2 minutes)
   - Full user journey validation in real browser
   - Test authentication flows (signup, signin, logout)
   - Test todo CRUD operations via UI
   - Validate responsive behavior
   - Test error handling and edge cases

---

## Key Architectural Decisions

### Decision 1: Test Database Isolation Strategy

**Context**: Tests need isolated database state to be deterministic and repeatable.

**Options Considered:**
1. **Shared test database with cleanup** - Simple but prone to race conditions
2. **Transactional rollback per test** - Fast, isolated, but requires transaction support
3. **Separate database per test run** - Complete isolation but slow setup

**Decision**: Use transactional rollback per test (Option 2)

**Rationale**:
- Fastest execution (no database recreation overhead)
- Complete isolation between tests (each test runs in a transaction that rolls back)
- Deterministic (no leftover data from previous tests)
- Supports parallel test execution

**Implementation**:
```python
@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.begin_nested()
        session = AsyncSession(bind=conn)
        yield session
        await session.rollback()
```

### Decision 2: Browser Automation Framework

**Context**: Need to test frontend UI flows in real browser environment.

**Options Considered:**
1. **Selenium** - Mature, widely used, but slower and more flaky
2. **Cypress** - Popular, but JavaScript-only and limited browser support
3. **Playwright** - Modern, fast, multi-browser, official Microsoft tool

**Decision**: Use Playwright (Option 3)

**Rationale**:
- Official Microsoft tool with active development
- Faster than Selenium (native browser automation)
- Better async/await support (matches FastAPI patterns)
- Multi-browser support (Chromium, Firefox, WebKit)
- Built-in test retry and video recording
- Excellent debugging tools (trace viewer, inspector)

### Decision 3: Test Data Management

**Context**: Tests need realistic, varied test data without manual creation.

**Options Considered:**
1. **Hardcoded test data** - Simple but inflexible and unrealistic
2. **Factory pattern with faker** - Flexible, realistic, reusable
3. **Database seeding scripts** - Persistent but requires cleanup

**Decision**: Use factory pattern with faker library (Option 2)

**Rationale**:
- Generates realistic test data (emails, names, descriptions)
- Flexible (can create variations for edge cases)
- Reusable across all test types
- No persistent state (data created per test)
- Supports parameterized testing

**Implementation**:
```python
class UserFactory:
    @staticmethod
    def create(email=None, password=None):
        return {
            "email": email or fake.email(),
            "password": password or fake.password(length=12)
        }
```

### Decision 4: Contract Validation Approach

**Context**: Need to validate API responses match OpenAPI specifications.

**Options Considered:**
1. **Manual assertions** - Tedious, error-prone, hard to maintain
2. **OpenAPI schema validation** - Automated, comprehensive, spec-driven
3. **Snapshot testing** - Detects changes but doesn't validate correctness

**Decision**: Use OpenAPI schema validation (Option 2)

**Rationale**:
- Automatically validates all response fields against spec
- Catches schema drift between spec and implementation
- Validates data types, required fields, formats
- Aligns with contract-first design principle
- Reduces manual assertion code

### Decision 5: Test Execution Order

**Context**: Tests should be independent but some scenarios build on others.

**Options Considered:**
1. **Random order** - Ensures independence but harder to debug
2. **Dependency-based order** - Faster but creates coupling
3. **Layered order (contract → integration → E2E)** - Fail fast, clear feedback

**Decision**: Use layered order with independent tests (Option 3)

**Rationale**:
- Fail fast (contract tests run first, catch schema issues early)
- Clear feedback (know which layer failed)
- Tests remain independent (no shared state)
- Supports parallel execution within layers
- Aligns with testing pyramid best practices

---

## Risk Analysis

### Risk 1: Test Database Conflicts with Production

**Likelihood**: Medium
**Impact**: Critical
**Mitigation**:
- Use separate `TEST_DATABASE_URL` environment variable
- Require explicit `ENV=test` flag to run tests
- Add database name validation (must contain "test")
- Document test database setup in quickstart.md

### Risk 2: Flaky E2E Tests

**Likelihood**: High
**Impact**: Medium
**Mitigation**:
- Use Playwright's built-in retry mechanism (3 retries)
- Add explicit waits for dynamic content
- Use data-testid attributes for stable selectors
- Record video traces for failed tests
- Run tests in headed mode during development

### Risk 3: Slow Test Execution

**Likelihood**: Medium
**Impact**: Medium
**Mitigation**:
- Target: Complete suite in under 5 minutes
- Run contract tests first (fastest feedback)
- Parallelize integration tests (pytest-xdist)
- Parallelize E2E tests (Playwright workers)
- Use transactional rollback (no database cleanup overhead)

### Risk 4: JWT Token Expiration During Tests

**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- Generate fresh tokens per test
- Use long expiration for test tokens (1 hour)
- Add token refresh logic in test utilities
- Validate token expiration in contract tests

### Risk 5: Phase 2 Implementation Incomplete

**Likelihood**: Medium
**Impact**: High
**Mitigation**:
- Document prerequisites in quickstart.md
- Add health check tests to verify backend/frontend running
- Fail fast with clear error messages if services unavailable
- Provide troubleshooting guide for common issues

---

## Implementation Notes

### Test Execution Workflow

1. **Pre-Test Setup**
   - Verify test database connection
   - Verify backend and frontend services running
   - Clean test database (truncate tables)
   - Generate test fixtures

2. **Test Execution**
   - Run contract tests (validate schemas)
   - Run integration tests (validate APIs)
   - Run E2E tests (validate UI flows)
   - Collect test results and coverage

3. **Post-Test Cleanup**
   - Rollback database transactions
   - Close browser contexts
   - Generate test reports
   - Archive failure traces

### Test Coverage Goals

- **Backend API Endpoints**: 100% (all CRUD operations)
- **Authentication Flows**: 100% (signup, signin, logout, protected routes)
- **Database Operations**: 100% (create, read, update, delete, isolation)
- **Frontend UI Flows**: 100% (all critical user journeys)
- **Error Scenarios**: 80% (common error cases)

### Performance Targets

- Contract tests: < 10 seconds
- Integration tests: < 30 seconds
- E2E tests: < 2 minutes
- **Total suite: < 5 minutes**

### Success Criteria

✅ All tests pass consistently (0% flaky tests)
✅ Test suite completes in under 5 minutes
✅ 100% coverage of Phase 2 Basic Level features
✅ Clear failure diagnostics (HTTP logs, DB state, screenshots)
✅ Tests run successfully in CI/CD pipeline
✅ Documentation complete (quickstart, contracts, data models)

---

## Next Steps

After plan approval:
1. Run `/sp.tasks` to generate atomic implementation tasks
2. Implement test fixtures and utilities
3. Implement contract validation tests
4. Implement backend integration tests
5. Implement frontend E2E tests
6. Integrate tests into CI/CD pipeline
7. Document test results and coverage

**Branch**: `001-e2e-testing`
**Plan Location**: `/specs/001-e2e-testing/plan.md`
**Artifacts Generated**:
- ✅ `research.md` (Phase 0)
- ✅ `data-model.md` (Phase 1)
- ✅ `contracts/` (Phase 1)
- ✅ `quickstart.md` (Phase 1)
