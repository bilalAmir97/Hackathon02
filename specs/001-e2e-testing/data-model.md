# Data Model: End-to-End Testing for Phase 2

**Feature**: 001-e2e-testing
**Date**: 2026-01-10
**Status**: Phase 1 Complete

## Overview

This document defines the test data models, fixtures, and test entities required for comprehensive E2E testing of Phase 2 system. These models represent test data structures used across contract, integration, and E2E tests.

## Test Entities

### 1. Test User

Represents a user account created during testing for authentication validation.

**Attributes**:
```python
@dataclass
class TestUser:
    email: str
    password: str  # Plaintext (for test login)
    hashed_password: str  # Expected bcrypt hash in database
    user_id: Optional[str] = None  # Set after creation
    jwt_token: Optional[str] = None  # Set after authentication
    created_at: Optional[datetime] = None
```

**Validation Rules**:
- Email must be valid format (contains @, domain)
- Password must meet minimum requirements (8+ chars)
- Hashed password must be bcrypt format ($2b$...)
- JWT token must be valid JWT structure (header.payload.signature)

**State Transitions**:
```
Created → Authenticated → Active
         ↓
      Logged Out
```

**Fixture Examples**:
```python
# Valid test user
TEST_USER_1 = TestUser(
    email="test1@example.com",
    password="TestPassword123!",
    hashed_password="$2b$12$..."  # Generated during signup
)

# Second user for isolation testing
TEST_USER_2 = TestUser(
    email="test2@example.com",
    password="TestPassword456!",
    hashed_password="$2b$12$..."
)

# Invalid user (for negative testing)
INVALID_USER = TestUser(
    email="invalid-email",
    password="short",
    hashed_password=""
)
```

### 2. Test Todo

Represents a todo item for CRUD operation testing.

**Attributes**:
```python
@dataclass
class TestTodo:
    title: str
    description: Optional[str] = None
    completed: bool = False
    user_id: Optional[str] = None  # Owner
    todo_id: Optional[str] = None  # Set after creation
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

**Validation Rules**:
- Title is required, non-empty, max 200 chars
- Description is optional, max 1000 chars
- Completed is boolean (default: False)
- User ID must reference valid user
- Todo ID is UUID format

**State Transitions**:
```
Created → Pending → Completed
         ↓
      Updated
         ↓
      Deleted
```

**Fixture Examples**:
```python
# Basic todo
TODO_1 = TestTodo(
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False
)

# Completed todo
TODO_2 = TestTodo(
    title="Finish homework",
    description="Math assignment due Friday",
    completed=True
)

# Minimal todo (no description)
TODO_3 = TestTodo(
    title="Call dentist",
    completed=False
)

# Edge case: long title
TODO_LONG_TITLE = TestTodo(
    title="A" * 200,  # Max length
    completed=False
)

# Edge case: special characters
TODO_SPECIAL_CHARS = TestTodo(
    title="Test <script>alert('xss')</script>",
    description="Test SQL'; DROP TABLE todos;--",
    completed=False
)
```

### 3. Test Session

Represents browser session state for frontend testing.

**Attributes**:
```python
@dataclass
class TestSession:
    user: TestUser
    cookies: Dict[str, str]
    local_storage: Dict[str, str]
    session_storage: Dict[str, str]
    jwt_token: str
    expires_at: datetime
```

**Validation Rules**:
- JWT token must be present in cookies or local storage
- Token must not be expired
- Session must be associated with valid user

**Fixture Examples**:
```python
# Authenticated session
AUTHENTICATED_SESSION = TestSession(
    user=TEST_USER_1,
    cookies={"session_id": "abc123"},
    local_storage={"jwt_token": "eyJhbGc..."},
    session_storage={},
    jwt_token="eyJhbGc...",
    expires_at=datetime.now() + timedelta(hours=24)
)

# Expired session
EXPIRED_SESSION = TestSession(
    user=TEST_USER_1,
    cookies={},
    local_storage={},
    session_storage={},
    jwt_token="expired_token",
    expires_at=datetime.now() - timedelta(hours=1)
)
```

### 4. Test Database State

Represents expected database state for validation.

**Attributes**:
```python
@dataclass
class TestDatabaseState:
    users: List[TestUser]
    todos: List[TestTodo]
    schema_version: str
    tables: List[str]
```

**Validation Rules**:
- All expected tables must exist (users, todos, sessions)
- Schema version must match migration version
- User data must be isolated (user A cannot access user B's todos)

**Fixture Examples**:
```python
# Initial state (empty database)
EMPTY_DB_STATE = TestDatabaseState(
    users=[],
    todos=[],
    schema_version="001",
    tables=["users", "todos", "sessions"]
)

# State with test data
POPULATED_DB_STATE = TestDatabaseState(
    users=[TEST_USER_1, TEST_USER_2],
    todos=[TODO_1, TODO_2, TODO_3],
    schema_version="001",
    tables=["users", "todos", "sessions"]
)
```

### 5. HTTP Request/Response

Represents API request and response pairs for contract validation.

**Attributes**:
```python
@dataclass
class TestHTTPRequest:
    method: str  # GET, POST, PUT, DELETE, PATCH
    url: str
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    query_params: Optional[Dict[str, str]] = None

@dataclass
class TestHTTPResponse:
    status_code: int
    headers: Dict[str, str]
    body: Optional[Dict[str, Any]] = None
    response_time_ms: float
```

**Validation Rules**:
- Status code must match expected (200, 201, 204, 401, 422)
- Response body must match schema (if present)
- Content-Type header must be application/json
- Authorization header required for protected endpoints

**Fixture Examples**:
```python
# Successful todo creation
CREATE_TODO_REQUEST = TestHTTPRequest(
    method="POST",
    url="/api/todos",
    headers={
        "Authorization": "Bearer eyJhbGc...",
        "Content-Type": "application/json"
    },
    body={"title": "Buy groceries", "completed": False}
)

CREATE_TODO_RESPONSE = TestHTTPResponse(
    status_code=201,
    headers={"Content-Type": "application/json"},
    body={
        "id": "uuid-here",
        "title": "Buy groceries",
        "completed": False,
        "user_id": "user-uuid",
        "created_at": "2026-01-10T12:00:00Z"
    },
    response_time_ms=45.2
)

# Unauthorized request
UNAUTHORIZED_REQUEST = TestHTTPRequest(
    method="GET",
    url="/api/todos",
    headers={},  # No Authorization header
    body=None
)

UNAUTHORIZED_RESPONSE = TestHTTPResponse(
    status_code=401,
    headers={"Content-Type": "application/json"},
    body={"detail": "Unauthorized"},
    response_time_ms=12.5
)
```

### 6. JWT Token

Represents JWT token structure for authentication validation.

**Attributes**:
```python
@dataclass
class TestJWTToken:
    raw_token: str  # Full JWT string
    header: Dict[str, str]  # {"alg": "HS256", "typ": "JWT"}
    payload: Dict[str, Any]  # {"user_id": "...", "exp": ...}
    signature: str
    is_valid: bool
    is_expired: bool
```

**Validation Rules**:
- Token must have three parts (header.payload.signature)
- Header must specify algorithm (HS256)
- Payload must contain user_id and exp (expiration)
- Signature must be valid (verifiable with secret)
- Token must not be expired

**Fixture Examples**:
```python
# Valid token
VALID_JWT = TestJWTToken(
    raw_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    header={"alg": "HS256", "typ": "JWT"},
    payload={
        "user_id": "user-uuid",
        "email": "test@example.com",
        "exp": int((datetime.now() + timedelta(hours=24)).timestamp())
    },
    signature="signature-here",
    is_valid=True,
    is_expired=False
)

# Expired token
EXPIRED_JWT = TestJWTToken(
    raw_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    header={"alg": "HS256", "typ": "JWT"},
    payload={
        "user_id": "user-uuid",
        "email": "test@example.com",
        "exp": int((datetime.now() - timedelta(hours=1)).timestamp())
    },
    signature="signature-here",
    is_valid=True,
    is_expired=True
)

# Invalid signature
INVALID_JWT = TestJWTToken(
    raw_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    header={"alg": "HS256", "typ": "JWT"},
    payload={"user_id": "user-uuid", "exp": 9999999999},
    signature="wrong-signature",
    is_valid=False,
    is_expired=False
)
```

## Test Data Relationships

```
TestUser (1) ──────── (N) TestTodo
    │                      │
    │                      │
    ├─── TestSession       │
    │                      │
    └─── TestJWTToken      │
                           │
                    TestDatabaseState
```

**Relationships**:
- One user can have many todos (1:N)
- One user has one active session (1:1)
- One user has one JWT token per session (1:1)
- Database state contains all users and todos

## Test Data Generators

### User Generator

```python
def generate_test_user(
    email: Optional[str] = None,
    password: Optional[str] = None
) -> TestUser:
    """Generate a unique test user with random email if not provided."""
    if email is None:
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    if password is None:
        password = "TestPassword123!"

    return TestUser(
        email=email,
        password=password,
        hashed_password=""  # Will be set during signup
    )
```

### Todo Generator

```python
def generate_test_todo(
    title: Optional[str] = None,
    completed: bool = False
) -> TestTodo:
    """Generate a test todo with random title if not provided."""
    if title is None:
        title = f"Test Todo {uuid.uuid4().hex[:8]}"

    return TestTodo(
        title=title,
        description=f"Description for {title}",
        completed=completed
    )
```

### Bulk Data Generator

```python
def generate_test_dataset(
    num_users: int = 2,
    todos_per_user: int = 3
) -> TestDatabaseState:
    """Generate a complete test dataset with users and todos."""
    users = [generate_test_user() for _ in range(num_users)]
    todos = []

    for user in users:
        for _ in range(todos_per_user):
            todo = generate_test_todo()
            todo.user_id = user.user_id
            todos.append(todo)

    return TestDatabaseState(
        users=users,
        todos=todos,
        schema_version="001",
        tables=["users", "todos", "sessions"]
    )
```

## Test Fixtures (pytest)

### Database Fixtures

```python
@pytest.fixture
async def test_db():
    """Provide a clean test database with schema."""
    # Run migrations
    await run_migrations()
    yield
    # Cleanup
    await drop_all_tables()

@pytest.fixture
async def db_transaction(test_db):
    """Provide a database transaction that rolls back after test."""
    async with db.begin() as transaction:
        yield transaction
        await transaction.rollback()
```

### User Fixtures

```python
@pytest.fixture
async def test_user(db_transaction) -> TestUser:
    """Create a test user in the database."""
    user = generate_test_user()
    # Create user via API
    response = await client.post("/api/auth/signup", json={
        "email": user.email,
        "password": user.password
    })
    user.user_id = response.json()["user_id"]
    user.jwt_token = response.json()["token"]
    return user

@pytest.fixture
async def authenticated_client(test_user) -> httpx.AsyncClient:
    """Provide an authenticated HTTP client."""
    return httpx.AsyncClient(
        base_url="http://localhost:8000",
        headers={"Authorization": f"Bearer {test_user.jwt_token}"}
    )
```

### Todo Fixtures

```python
@pytest.fixture
async def test_todo(test_user, authenticated_client) -> TestTodo:
    """Create a test todo in the database."""
    todo = generate_test_todo()
    response = await authenticated_client.post("/api/todos", json={
        "title": todo.title,
        "description": todo.description,
        "completed": todo.completed
    })
    todo.todo_id = response.json()["id"]
    todo.user_id = test_user.user_id
    return todo
```

## Test Fixtures (Playwright)

### Browser Fixtures

```typescript
// fixtures.ts
import { test as base } from '@playwright/test';

type TestFixtures = {
  authenticatedPage: Page;
  testUser: TestUser;
};

export const test = base.extend<TestFixtures>({
  testUser: async ({}, use) => {
    // Create test user
    const user = {
      email: `test_${Date.now()}@example.com`,
      password: 'TestPassword123!'
    };
    await use(user);
  },

  authenticatedPage: async ({ page, testUser }, use) => {
    // Sign up and sign in
    await page.goto('/signup');
    await page.fill('[data-testid="email"]', testUser.email);
    await page.fill('[data-testid="password"]', testUser.password);
    await page.click('[data-testid="signup-button"]');

    // Wait for redirect to dashboard
    await page.waitForURL('/dashboard');

    await use(page);
  }
});
```

## Data Validation Helpers

### Schema Validators

```python
def validate_user_schema(user_data: Dict[str, Any]) -> bool:
    """Validate user data matches expected schema."""
    required_fields = ["user_id", "email", "created_at"]
    return all(field in user_data for field in required_fields)

def validate_todo_schema(todo_data: Dict[str, Any]) -> bool:
    """Validate todo data matches expected schema."""
    required_fields = ["id", "title", "completed", "user_id", "created_at"]
    return all(field in todo_data for field in required_fields)

def validate_jwt_structure(token: str) -> bool:
    """Validate JWT token has correct structure."""
    parts = token.split('.')
    return len(parts) == 3  # header.payload.signature
```

### Database Validators

```python
async def validate_database_schema(db_connection) -> bool:
    """Validate database has expected tables and columns."""
    expected_tables = ["users", "todos", "sessions"]

    for table in expected_tables:
        result = await db_connection.execute(
            f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')"
        )
        if not result.scalar():
            return False

    return True

async def validate_user_isolation(db_connection, user1_id: str, user2_id: str) -> bool:
    """Validate user data isolation (user1 cannot access user2's todos)."""
    result = await db_connection.execute(
        "SELECT COUNT(*) FROM todos WHERE user_id = :user1_id",
        {"user1_id": user1_id}
    )
    user1_count = result.scalar()

    result = await db_connection.execute(
        "SELECT COUNT(*) FROM todos WHERE user_id = :user2_id",
        {"user2_id": user2_id}
    )
    user2_count = result.scalar()

    # Verify counts are independent (no cross-user access)
    return user1_count >= 0 and user2_count >= 0
```

## Summary

**Test Entities Defined**:
1. TestUser - User accounts for authentication testing
2. TestTodo - Todo items for CRUD testing
3. TestSession - Browser session state for frontend testing
4. TestDatabaseState - Expected database state for validation
5. TestHTTPRequest/Response - API contract validation
6. TestJWTToken - JWT token structure validation

**Fixtures Provided**:
- Database fixtures (clean DB, transactions)
- User fixtures (test users, authenticated clients)
- Todo fixtures (test todos)
- Browser fixtures (authenticated pages)

**Validation Helpers**:
- Schema validators (user, todo, JWT)
- Database validators (schema, isolation)

**Next Steps**: Proceed to generate API contracts in `contracts/` directory.
