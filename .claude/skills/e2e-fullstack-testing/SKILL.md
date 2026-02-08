---
name: e2e-fullstack-testing
description: End-to-end testing for authentication, database, backend APIs, and frontend UI across the full application stack.
---

# E2E Full-Stack Testing Skill

## Scope
This skill is used to design, implement, and validate end-to-end tests covering:
- Authentication flows
- Database integration
- Backend API behavior
- Frontend pages, components, and layouts

This skill performs **testing only**.
It must NOT modify specs, business logic, or architecture.

---

## Testing Domains

### 1. Authentication Integration Testing
Validate complete auth lifecycle using Better Auth.

**Coverage**
- Signup flow
- Signin flow
- Password hashing & storage
- JWT issuance and validation
- Protected route access
- Logout & token invalidation

**Assertions**
- Passwords are never stored in plaintext
- JWT tokens are attached to authenticated requests
- Unauthorized requests return 401
- Authenticated users are correctly identified (user_id / subject)

---

### 2. Database Integration Testing
Ensure persistence layer behaves as specified.

**Coverage**
- Table creation
- Schema correctness
- Migrations execution
- Foreign keys & constraints
- User-scoped data isolation

**Assertions**
- Tables exist with correct columns & types
- Migrations are idempotent
- Data is persisted and retrieved correctly
- One user cannot access another user's records

---

### 3. Backend Implementation Testing
Validate backend behavior through real HTTP requests.

**Coverage**
- Route generation
- Request validation
- Response schemas
- Status codes
- DB connectivity

**Assertions**
- Endpoints match spec contracts
- Correct HTTP codes are returned
- Error cases handled gracefully
- Database reads/writes occur as expected

---

### 4. Frontend Implementation Testing
Validate UI behavior from the user's perspective.

**Coverage**
- Page rendering
- Navigation & redirects
- Auth-gated routes
- Component behavior
- Layout & styling integrity

**Assertions**
- Pages render without runtime errors
- Auth redirects behave correctly
- Forms submit expected payloads
- UI updates reflect backend state
- Responsive layout works across breakpoints

---

## Tools & Approach
- E2E framework: Playwright or Cypress
- Backend tests: pytest + TestClient (if applicable)
- Database: isolated test database or transactional rollback
- Frontend: real browser automation (no mocks for core flows)

---

## Best Practices
- Treat specs as contracts
- Test real integrations, not mocks
- One test = one user journey
- Clean test data after execution
- Keep tests deterministic and repeatable

---

## Example Test Flow (Auth → Dashboard)
```text
1. User signs up
2. Password is hashed and stored
3. User signs in
4. JWT is issued
5. JWT attached to API requests
6. Protected dashboard loads
7. Data fetched from backend
8. UI renders persisted data
```