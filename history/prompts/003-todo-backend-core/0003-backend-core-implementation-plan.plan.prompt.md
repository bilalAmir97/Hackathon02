---
id: 0003
title: backend-core-implementation-plan
stage: plan
date: 2026-01-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-backend-core
branch: 003-todo-backend-core
user: user
command: /sp.plan
labels: ["planning", "architecture", "fastapi", "sqlmodel", "neon-postgresql", "rest-api", "phase-ii", "backend", "design"]
links:
  spec: specs/003-todo-backend-core/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-todo-backend-core/plan.md
  - specs/003-todo-backend-core/research.md
  - specs/003-todo-backend-core/data-model.md
  - specs/003-todo-backend-core/quickstart.md
  - specs/003-todo-backend-core/contracts/openapi.yaml
  - specs/003-todo-backend-core/contracts/errors.json
  - specs/003-todo-backend-core/contracts/schemas/user.json
  - specs/003-todo-backend-core/contracts/schemas/task.json
  - specs/003-todo-backend-core/contracts/schemas/pagination.json
tests:
  - N/A - planning phase (no tests run)
---

## Prompt

```text
/sp.plan

Spec-1 Backend Core & Data Layer

Objective:
Implement a persistent FastAPI backend for Phase-II, scoped for multi-user task management and prepared for JWT enforcement in Spec-2.

Project structure (mandatory first step):
- Create Phase-II/
- Inside Phase-II/, create backend/ and frontend/
- All Spec-1 work lives in Phase-II/backend/

Plan (Research → Foundation → Analysis → Synthesis):

Research
- Review FastAPI async patterns, SQLModel async sessions, Neon PostgreSQL setup.
- Note key tradeoffs (async engine, migrations, session lifecycle).

Foundation
1. Initialize backend project (env config, app factory).
2. Configure Neon PostgreSQL connection via environment variables.
3. Set up SQLModel base, async engine, and session dependency.
4. Define models: User (id, email) and Task (id, title, completed, owner_id, timestamps).
5. Establish table creation / migration strategy.

Analysis
6. Define request/response schemas.
7. Implement REST endpoints: GET, POST, GET by id, PUT, DELETE, PATCH complete.
8. Enforce user-scoped queries (owner_id == user_id).
9. Enforce ownership checks on update/delete.
10. Add standardized API error handling.

Synthesis
11. Add minimal tests validating CRUD, user isolation, and ownership enforcement.
12. Document architecture sketch, key decisions, and testing strategy.
13. Document JWT middleware insertion points for Spec-2.

Constraints:
- No authentication logic in this spec.
- Async-only FastAPI + SQLModel.
- Environment-based configuration only.

Acceptance check:
- All endpoints work with persistent DB.
- User isolation enforced at query and mutation level.
- Backend ready for JWT verification integration.
```

## Response snapshot

Created comprehensive implementation plan for Backend Core & Data Layer feature (003-todo-backend-core) following Phase 0 (Research) and Phase 1 (Design & Contracts) workflow.

**Phase 0: Research (Completed)**

Documented 8 key technology decisions in `research.md`:
1. FastAPI async patterns with AsyncSession
2. SQLModel with SQLAlchemy async engine and connection pooling
3. Neon Serverless PostgreSQL with asyncpg driver
4. UUID v4 for all identifiers (user_id, task_id)
5. RFC 7807 Problem Details for error responses
6. Structured JSON logging with context fields
7. Offset/limit pagination with metadata (total, has_next, has_previous)
8. User-scoped data access at application layer

All technology tradeoffs documented with rationale, alternatives considered, and best practices.

**Phase 1: Design & Contracts (Completed)**

Created comprehensive design artifacts:

1. **data-model.md**: Complete entity definitions
   - 2 entities (User, Task) with UUID v4 identifiers
   - 1 relationship (User → Task, one-to-many with cascade delete)
   - 5 database indexes (1 unique, 4 performance)
   - Validation rules, state transitions, query patterns
   - SQL DDL for schema creation

2. **contracts/openapi.yaml**: Complete OpenAPI 3.0 specification
   - 6 REST endpoints (1 health check + 5 task CRUD operations)
   - Request/response schemas with validation
   - RFC 7807 error responses
   - Path parameters, query parameters, pagination

3. **contracts/errors.json**: RFC 7807 error schemas
   - ProblemDetail base schema
   - Specific error types (400, 404, 422, 500, 503)
   - Example error responses

4. **contracts/schemas/**: JSON Schema definitions
   - user.json (User entity schema)
   - task.json (Task entity schema)
   - pagination.json (Paginated response schema)

5. **quickstart.md**: Local development setup guide
   - Prerequisites and installation steps
   - Neon PostgreSQL configuration
   - Environment variable setup
   - Running the application and tests
   - API usage examples with curl commands
   - Troubleshooting guide

**Implementation Plan (plan.md)**

Comprehensive plan with:
- Constitution compliance check (all 12 principles satisfied)
- Project structure (Phase-II/backend/ with clean architecture layers)
- Architecture overview (request flow, error handling, design patterns)
- Security considerations (user isolation, input validation, SQL injection prevention)
- Performance optimization (indexing strategy, connection pooling, pagination)
- Testing strategy (test pyramid, coverage targets, test database approach)
- Deployment readiness (environment variables, health checks)
- Future integration points (JWT authentication middleware)
- Monitoring & observability (structured JSON logging)

**Key Design Decisions**:
- Clean architecture with 4 layers (API, Interface Adapters, Use Cases, Domain, Infrastructure)
- Dependency injection for database sessions
- Middleware for structured logging and error handling
- User isolation enforced at query level (always filter by user_id)
- Stateless backend ready for JWT integration
- Two-state task model (pending/completed) sufficient for Phase II

## Outcome

- ✅ Impact: Complete implementation plan with research, data model, API contracts, and quickstart guide. All technology decisions documented with rationale. Architecture designed following clean architecture principles with user isolation, async patterns, and production-ready observability. Ready for task decomposition and implementation.
- 🧪 Tests: N/A - planning phase (test strategy documented, no tests run yet)
- 📁 Files: Created 9 files (plan.md, research.md, data-model.md, quickstart.md, openapi.yaml, errors.json, 3 JSON schemas)
- 🔁 Next prompts: /sp.tasks to generate atomic, testable implementation tasks from this plan
- 🧠 Reflection: Comprehensive planning session successfully completed Phase 0 (Research) and Phase 1 (Design & Contracts). All technology decisions made with clear rationale and alternatives considered. Data model designed with UUID v4 identifiers, proper indexing, and validation rules. Complete API contract defined following OpenAPI 3.0 and RFC 7807 standards. Architecture follows clean architecture principles with clear layer separation. User isolation pattern designed to prevent cross-user data access. Stateless backend design ready for JWT authentication integration in future spec. All constitution principles satisfied without violations. Plan is implementation-ready with no unknowns remaining.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all artifacts generated
- Graders run and results (PASS/FAIL): Constitution check - PASS (all 12 principles satisfied, no violations)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null
