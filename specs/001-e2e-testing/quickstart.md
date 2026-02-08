# E2E Testing Quickstart Guide

This guide explains how to set up and run the end-to-end test suite for Phase 2 of the Todo application.

## Prerequisites

- Python 3.13+ installed
- Node.js 18+ and npm installed
- UV package manager installed (`pip install uv`)
- Access to Neon PostgreSQL test database
- Phase 2 backend and frontend implementations complete

## Environment Setup

### 1. Install Dependencies

**Backend Testing Dependencies:**
```bash
cd phase-2/backend
uv pip install pytest pytest-asyncio httpx psycopg2-binary python-dotenv
```

**Frontend E2E Testing:**
Playwright MCP is already installed and configured. No additional installation required.

### 2. Configure Test Environment

Create a `.env.test` file in the project root:

```bash
# Test Database (Neon PostgreSQL - isolated from production)
TEST_DATABASE_URL=postgresql://user:password@test-db.neon.tech/test_db

# Authentication Secret (must match backend BETTER_AUTH_SECRET)
BETTER_AUTH_SECRET=your-test-secret-key-min-32-chars

# Backend API URL (for E2E tests)
BACKEND_API_URL=http://localhost:8000

# Frontend URL (for E2E tests)
FRONTEND_URL=http://localhost:3000

# Test User Credentials
TEST_USER_EMAIL=test@example.com
TEST_USER_PASSWORD=TestPassword123!
```

**Important:** Use a separate test database, NOT your production database. Tests will create and delete data.

### 3. Database Setup

Initialize the test database schema:

```bash
# Run database migrations on test database
cd phase-2/backend
uv run alembic upgrade head
```

Verify schema matches contract:
```bash
psql $TEST_DATABASE_URL -f specs/001-e2e-testing/contracts/database-schema.sql
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest phase-2/ -v
```

### Run Tests by Layer

**Backend Integration Tests:**
```bash
pytest phase-2/backend/tests/integration/ -v
```

**Backend Contract Tests:**
```bash
pytest phase-2/backend/tests/contract/ -v
```

**Frontend E2E Tests:**
```bash
# Playwright MCP is already installed - use MCP tools for E2E testing
# Tests will be executed via Playwright MCP integration
```

### Run Specific Test Files

```bash
# Authentication tests
pytest phase-2/backend/tests/integration/test_auth.py -v

# Todo CRUD API tests
pytest phase-2/backend/tests/integration/test_api_todos.py -v

# Database integration tests
pytest phase-2/backend/tests/integration/test_database.py -v

# Frontend E2E tests - use Playwright MCP tools
# Tests will be executed via MCP integration
```

### Run Tests with Coverage

```bash
pytest phase-2/ --cov=phase-2/backend/src --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html
```

## Test Execution Workflow

### 1. Start Backend Server (Test Mode)

```bash
cd phase-2/backend
export ENV=test
export DATABASE_URL=$TEST_DATABASE_URL
uv run uvicorn src.main:app --reload --port 8000
```

### 2. Start Frontend Server (Test Mode)

```bash
cd phase-2/frontend
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### 3. Run Test Suite

In a separate terminal:
```bash
# Run backend integration tests
pytest phase-2/backend/tests/ -v

# Frontend E2E tests use Playwright MCP - execute via MCP tools
```

## Test Data Management

### Clean Test Database

Before running tests, clean the test database:

```bash
psql $TEST_DATABASE_URL -c "TRUNCATE TABLE todos, users CASCADE;"
```

### Seed Test Data

```bash
# Run test data seeding script
python phase-2/tests/fixtures/seed_test_data.py
```

## Debugging Tests

### Backend Tests

Run with verbose output and stop on first failure:
```bash
pytest phase-2/backend/tests/ -vv -x
```

Run with Python debugger:
```bash
pytest phase-2/backend/tests/integration/test_auth.py -v --pdb
```

### Frontend E2E Tests

Playwright MCP is already installed and configured. E2E tests will be executed via Playwright MCP tools with built-in debugging capabilities:
- Browser automation through MCP integration
- Automatic screenshot and trace capture on failures
- Access to Playwright's debugging features through MCP

## Continuous Integration

### GitHub Actions Workflow

Tests run automatically on every push and pull request:

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install -r requirements.txt
      - name: Run backend tests
        run: pytest phase-2/backend/tests/ -v
      - name: Run E2E tests
        run: |
          # E2E tests use Playwright MCP (already configured)
          # Execute via MCP integration
```

## Test Execution Time

Expected execution times:
- Backend integration tests: ~30 seconds
- Backend contract tests: ~10 seconds
- Frontend E2E tests: ~2 minutes
- **Total test suite: < 5 minutes**

## Troubleshooting

### Database Connection Errors

```bash
# Verify database connection
psql $TEST_DATABASE_URL -c "SELECT 1;"

# Check database exists
psql $TEST_DATABASE_URL -c "\l"
```

### Authentication Errors

```bash
# Verify BETTER_AUTH_SECRET matches between frontend and backend
echo $BETTER_AUTH_SECRET

# Test JWT token generation
python -c "import jwt; print(jwt.encode({'user_id': '123'}, 'your-secret', algorithm='HS256'))"
```

### Port Conflicts

```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill processes if needed
kill -9 <PID>
```

### Playwright Browser Issues

Playwright MCP is already installed and configured. Browser management is handled automatically by the MCP integration. If you encounter browser-related issues, verify the MCP server is running correctly.

## Test Reports

### Pytest HTML Report

```bash
pytest phase-2/ --html=report.html --self-contained-html
open report.html
```

### Playwright HTML Report

E2E test reports are generated automatically by Playwright MCP integration. Test results, screenshots, and traces are captured through the MCP server.

## Next Steps

After running tests successfully:
1. Review test coverage report
2. Fix any failing tests
3. Add additional test scenarios as needed
4. Integrate tests into CI/CD pipeline
5. Document any test-specific configuration

## Support

For issues or questions:
- Check test logs in `phase-2/tests/logs/`
- Review contract specifications in `specs/001-e2e-testing/contracts/`
- Consult the implementation plan in `specs/001-e2e-testing/plan.md`
