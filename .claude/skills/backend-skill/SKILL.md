---
name: backend-skill
description: Generate backend routes, handle HTTP requests/responses, and connect reliably to databases (SQL & NoSQL) with best-practice patterns.
---

# Backend Skill

## Instructions

1. **Route & Endpoint Design**
   - Define resource-oriented routes (RESTful or RPC depending on use-case).
   - Use consistent naming and HTTP verbs: `GET /items`, `POST /items`, `GET /items/:id`, `PUT /items/:id`, `DELETE /items/:id`.
   - Support query parameters for filtering, sorting, and pagination (`?page=1&limit=20&sort=-createdAt`).

2. **Request Validation & Transformation**
   - Validate incoming payloads and query params (Zod, Joi, Yup).
   - Normalize and coerce types (dates, numbers, booleans) at the boundary.
   - Return clear 4xx responses for client errors with structured problem details.

3. **Business Logic & Controllers**
   - Keep controllers thin: validate → authorize → call service layer → return response.
   - Implement a service/repository separation: services contain business rules; repositories handle DB access.

4. **Database Connectivity**
   - Create a single database client/connection manager and reuse across requests.
   - Support transactional operations with explicit transaction scopes.
   - Use prepared statements / parameterized queries or an ORM (Prisma, TypeORM, Sequelize) to avoid injection.

5. **Error Handling & Responses**
   - Centralize error handling middleware that maps exceptions to HTTP status codes.
   - Log server errors and return a safe, generic message to clients.
   - Use consistent response envelope (status, data, errors, meta) for API consumers.

6. **Security & Operational Concerns**
   - Protect endpoints with auth middleware (JWT, sessions, Better Auth, OAuth).
   - Apply rate limiting, CORS, input sanitization, and CSRF protections where applicable.
   - Never leak sensitive data in errors or logs; store secrets in environment variables/secret manager.

7. **Observability & Testing**
   - Instrument request logging and distributed tracing for latency hotspots.
   - Add unit tests for services and integration tests for routes (supertest / Playwright / Postman).
   - Run migrations and schema checks in CI; include smoke tests after deploy.

8. **Standards & Documentation**
   - Keep OpenAPI/Swagger docs up-to-date; auto-generate from route schemas when possible.
   - Version your API (v1, v2) and support backward-compatible changes with clear deprecation paths.

## Best Practices
- Keep routes idempotent where appropriate (use `PUT` for full updates, `PATCH` for partial).
- Favor explicitness: return 404 for missing resources; 400 for bad input; 500 for server errors.
- Use pagination and limits to avoid excessive payloads.
- Use connection pooling and proper idle / max lifetime settings for DB clients.
- Prefer safe schema migrations (create-then-backfill-then-swap) for production changes.
- Structure repositories to allow easy switching of database engines (adapter pattern).
- Document error codes and validation rules in API docs.
