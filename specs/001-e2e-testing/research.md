# Research: End-to-End Testing for Phase 2

**Feature**: 001-e2e-testing
**Date**: 2026-01-10
**Status**: Phase 0 Complete

## Overview

This document consolidates research findings for implementing comprehensive E2E testing infrastructure for Phase 2 system. Research covers testing framework selection, best practices for authentication/database/API/frontend testing, and strategies for deterministic, repeatable test execution.

## Testing Framework Selection

### Decision 1: Playwright for Browser Automation

**Chosen**: Playwright (TypeScript/JavaScript)

**Rationale**:
- Modern browser automation with excellent async/await support
- Built-in test runner with parallel execution
- Auto-waiting for elements (reduces flakiness)
- Network interception and mocking capabilities
- Screenshot and video recording on failure
- Cross-browser support (Chromium, Firefox, WebKit)
- Excellent TypeScript support for Next.js integration
- Active development and strong community

**Alternatives Considered**:
- **Selenium**: Older, more verbose API, requires explicit waits, higher flakiness
- **Cypress**: Good but limited to Chromium, runs inside browser (architectural limitation)
- **Puppeteer**: Chrome-only, no built-in test runner, less feature-complete

**Best Practices**:
- Use page object model (POM) for maintainability
- Leverage auto-waiting (avoid manual `sleep()` calls)
- Use data-testid attributes for stable selectors
- Run tests in headless mode for CI/CD
- Capture screenshots/videos only on failure
- Use fixtures for authentication state reuse

### Decision 2: pytest for Backend Testing

**Chosen**: pytest with pytest-asyncio

**Rationale**:
- De facto standard for Python testing
- Excellent fixture system for setup/teardown
- Async/await support via pytest-asyncio
- Parametrized tests for data-driven testing
- Rich plugin ecosystem (coverage, xdist for parallel execution)
- Clear assertion introspection
- Compatible with FastAPI testing patterns

**Alternatives Considered**:
- **unittest**: Standard library but more verbose, less powerful fixtures
- **nose2**: Less active development, smaller community

**Best Practices**:
- Use fixtures for database setup/teardown
- Leverage `pytest.mark.asyncio` for async tests
- Use `pytest-xdist` for parallel test execution
- Organize tests by feature/layer (integration, contract)
- Use `conftest.py` for shared fixtures
- Parametrize tests for multiple scenarios

### Decision 3: httpx for HTTP Client

**Chosen**: httpx (async HTTP client)

**Rationale**:
- Async/await support (matches FastAPI async patterns)
- Requests-compatible API (familiar to Python developers)
- HTTP/2 support
- Connection pooling for performance
- Excellent for testing REST APIs
- Built-in timeout and retry support

**Alternatives Considered**:
- **requests**: Synchronous only, no async support
- **aiohttp**: More complex API, less requests-compatible

**Best Practices**:
- Use async context managers for client lifecycle
- Set reasonable timeouts (avoid hanging tests)
- Reuse client instances via fixtures
- Validate response status codes and schemas
- Test both success and error paths

### Decision 4: psycopg2 for Database Testing

**Chosen**: psycopg2 (PostgreSQL adapter)

**Rationale**:
- Standard PostgreSQL adapter for Python
- Mature, stable, well-documented
- Supports connection pooling
- Compatible with Neon PostgreSQL
- Allows direct database validation (beyond ORM)

**Alternatives Considered**:
- **asyncpg**: Async-only, more complex for simple validation queries
- **SQLAlchemy**: ORM overhead for simple test queries

**Best Practices**:
- Use transactions with rollback for test isolation
- Create dedicated test database (separate from production)
- Use fixtures for database connection management
- Validate schema structure (tables, columns, constraints)
- Test data isolation (user A cannot access user B's data)

## Testing Architecture Patterns

### Pattern 1: Test Pyramid

**Structure**:
```
        /\
       /E2E\        <- Few, slow, high-value (critical user journeys)
      /------\
     /Integr-\      <- More, medium speed (API + DB validation)
    /----------\
   /  Contract  \   <- Many, fast (schema validation)
  /--------------\
```

**Application to Phase 2**:
- **Contract Tests**: Validate API schemas, database schema, JWT structure
- **Integration Tests**: Test API endpoints with real database, auth middleware
- **E2E Tests**: Full user journeys in browser (signup → signin → CRUD → logout)

**Rationale**: Balances speed and confidence. Fast contract tests catch schema issues early. Integration tests validate component interactions. E2E tests validate complete user experience.

### Pattern 2: Test Isolation via Database Transactions

**Strategy**: Each test runs in a transaction that rolls back after completion

**Implementation**:
```python
@pytest.fixture
async def db_transaction():
    async with db.begin() as transaction:
        yield transaction
        await transaction.rollback()
```

**Benefits**:
- No test data pollution
- Fast cleanup (rollback vs. DELETE queries)
- Deterministic test execution
- Parallel test execution possible

**Rationale**: Ensures tests don't interfere with each other. Critical for deterministic, repeatable execution.

### Pattern 3: Authentication State Reuse

**Strategy**: Authenticate once, reuse session across tests

**Playwright Implementation**:
```typescript
// Global setup: authenticate and save state
await page.goto('/signin');
await page.fill('[data-testid="email"]', 'test@example.com');
await page.fill('[data-testid="password"]', 'password123');
await page.click('[data-testid="signin-button"]');
await page.context().storageState({ path: 'auth-state.json' });

// Tests: reuse authentication state
const context = await browser.newContext({ storageState: 'auth-state.json' });
```

**Benefits**:
- Faster test execution (no repeated login)
- Reduces flakiness (fewer network requests)
- Tests focus on feature validation, not auth setup

**Rationale**: Authentication is tested separately. Other tests should assume authenticated state to reduce execution time and complexity.

### Pattern 4: Page Object Model (POM)

**Structure**:
```typescript
class TodoPage {
  constructor(private page: Page) {}

  async createTodo(title: string) {
    await this.page.fill('[data-testid="todo-input"]', title);
    await this.page.click('[data-testid="add-button"]');
  }

  async getTodos() {
    return await this.page.locator('[data-testid="todo-item"]').allTextContents();
  }
}
```

**Benefits**:
- Encapsulates page interactions
- Reduces duplication
- Easier to maintain (UI changes update one place)
- More readable tests

**Rationale**: E2E tests are brittle when tightly coupled to DOM structure. POM provides abstraction layer.

## Testing Best Practices

### Authentication Testing

**Key Validations**:
1. Password hashing (bcrypt/argon2, no plaintext)
2. JWT token structure (header, payload, signature)
3. JWT expiration claims
4. Authorization header requirement
5. Token validation on protected routes
6. Session termination on logout

**Test Strategy**:
- Integration tests: Validate auth middleware behavior
- E2E tests: Validate complete signup/signin/logout flows
- Contract tests: Validate JWT structure and claims

### Database Testing

**Key Validations**:
1. Schema structure (tables, columns, types, constraints)
2. Migration execution (idempotent, no errors)
3. Data persistence (survives application restart)
4. User data isolation (user A cannot access user B's data)
5. Password hashing in database

**Test Strategy**:
- Direct SQL queries to validate schema
- Create test users, verify isolation
- Test CRUD operations, verify persistence
- Use transactions for test isolation

### API Testing

**Key Validations**:
1. HTTP status codes (200, 201, 204, 401, 422)
2. Response schemas (match OpenAPI spec)
3. Request validation (reject invalid payloads)
4. Authentication enforcement (401 for missing token)
5. Authorization enforcement (users see only their data)
6. Error messages (clear, actionable)

**Test Strategy**:
- Integration tests with httpx client
- Parametrized tests for multiple scenarios
- Test both success and error paths
- Validate response schemas with JSON Schema

### Frontend Testing

**Key Validations**:
1. Page rendering (no errors, expected elements present)
2. Form submissions (success feedback, error handling)
3. UI state updates (reflect backend changes)
4. Authentication redirects (protected pages → signin)
5. Responsive behavior (mobile, tablet, desktop)
6. Data persistence (refresh page, data still present)

**Test Strategy**:
- E2E tests with Playwright
- Use data-testid for stable selectors
- Test critical user journeys
- Validate UI state matches backend state

## Deterministic Test Execution

### Strategy 1: Isolated Test Database

**Implementation**:
- Use dedicated test database (separate from production)
- Reset database before each test run
- Use transactions with rollback for test isolation

**Benefits**: No shared state between tests, no production data contamination

### Strategy 2: Explicit Test Ordering

**Implementation**:
- Tests should not depend on execution order
- Each test sets up its own data
- Use fixtures for consistent setup

**Benefits**: Tests can run in any order or in parallel

### Strategy 3: Avoid Time-Based Logic

**Implementation**:
- Mock current time for time-sensitive tests
- Use fixed timestamps in test data
- Avoid `sleep()` calls (use auto-waiting)

**Benefits**: Tests produce same results regardless of execution time

### Strategy 4: Network Stability

**Implementation**:
- Use localhost for backend (no external network)
- Mock external API calls
- Set reasonable timeouts (fail fast on issues)

**Benefits**: Tests don't fail due to network issues

## Performance Optimization

### Target: Complete test suite in under 5 minutes

**Strategies**:
1. **Parallel Execution**: Use pytest-xdist and Playwright workers
2. **Authentication State Reuse**: Authenticate once, reuse across tests
3. **Database Transactions**: Fast rollback vs. DELETE queries
4. **Selective E2E Tests**: Only critical user journeys (not every edge case)
5. **Headless Browser**: Faster than headed mode
6. **Connection Pooling**: Reuse database and HTTP connections

**Expected Breakdown**:
- Contract tests: 30 seconds (fast schema validation)
- Integration tests: 2 minutes (API + database validation)
- E2E tests: 2.5 minutes (browser automation)
- Total: ~5 minutes

## Test Reporting

### Requirements:
1. Clear pass/fail status for each test
2. Execution time tracking
3. Failed test details (error message, stack trace)
4. HTTP request/response capture on failure
5. Database state capture on failure
6. Screenshots/videos for E2E failures

### Implementation:
- pytest: Use `pytest-html` for HTML reports
- Playwright: Built-in HTML reporter with screenshots/videos
- CI/CD: Upload test artifacts (reports, screenshots, videos)

## Environment Configuration

### Required Environment Variables:
```bash
# Test Database
TEST_DATABASE_URL=postgresql://user:pass@localhost:5432/test_db

# Backend
TEST_BACKEND_URL=http://localhost:8000

# Frontend
TEST_FRONTEND_URL=http://localhost:3000

# Authentication
TEST_JWT_SECRET=test-secret-key-not-for-production
BETTER_AUTH_SECRET=test-auth-secret-not-for-production

# Test User Credentials
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=TestPassword123!
```

### Configuration Files:
- `pytest.ini`: pytest configuration
- `playwright.config.ts`: Playwright configuration
- `conftest.py`: Shared pytest fixtures
- `.env.test`: Test environment variables

## Risk Mitigation

### Risk 1: Flaky Tests

**Mitigation**:
- Use Playwright auto-waiting (no manual sleeps)
- Use stable selectors (data-testid)
- Implement retry logic for network requests
- Use transactions for test isolation

### Risk 2: Slow Test Execution

**Mitigation**:
- Parallel execution (pytest-xdist, Playwright workers)
- Authentication state reuse
- Selective E2E testing (critical paths only)
- Database transaction rollback (fast cleanup)

### Risk 3: Test Data Pollution

**Mitigation**:
- Isolated test database
- Transaction rollback after each test
- Unique test data per test (UUIDs, timestamps)

### Risk 4: Phase 2 Implementation Incomplete

**Mitigation**:
- Verify Phase 2 implementation exists before writing tests
- Document dependencies in spec
- Fail fast with clear error messages if dependencies missing

## Summary

**Key Decisions**:
1. Playwright for browser automation (modern, reliable, feature-rich)
2. pytest for backend testing (standard, powerful fixtures)
3. httpx for HTTP client (async support, requests-compatible)
4. psycopg2 for database testing (mature, stable)

**Key Patterns**:
1. Test pyramid (contract → integration → E2E)
2. Database transactions for isolation
3. Authentication state reuse for performance
4. Page Object Model for maintainability

**Key Practices**:
1. Deterministic execution (no flaky tests)
2. Parallel execution (under 5 minutes)
3. Clear reporting (pass/fail, artifacts on failure)
4. Test isolation (no shared state)

**Next Steps**: Proceed to Phase 1 (Design & Contracts) to define test data models, API contracts, and quickstart guide.
