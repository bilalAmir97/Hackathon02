---
id: "0001"
title: Phase 2 Web App Spec
stage: spec
date: "2026-01-07"
surface: agent
model: claude-sonnet-4-5-20250929
feature: "003-phase-2-web-app"
branch: "003-phase-2-web-app"
user: "human"
command: "/sp.specify"
labels: ["full-stack","todo-app","web-app"]
links:
  spec: "specs/003-phase-2-web-app/spec.md"
  ticket: null
  adr: null
  pr: null
files:
  - "specs/003-phase-2-web-app/spec.md"
  - "specs/003-phase-2-web-app/checklists/requirements.md"
tests: []
---

## Prompt

PHASE: Phase 2 — Web Application (Frontend + Backend + Database + Auth)

SCOPE (STRICT):
This specification applies ONLY to /phase-2/**
No files outside /phase-2 may be referenced or modified.

OBJECTIVE:
Define the complete, contract-level specification for a full-stack Todo web application consisting of:

Next.js frontend

FastAPI backend

PostgreSQL database (Neon)

Better Auth JWT-based authentication

This spec is binding. All later plans, tasks, and implementations MUST conform exactly.

================================
SYSTEM ARCHITECTURE

Frontend:

Framework: Next.js (App Router)

Styling: Tailwind CSS

Auth: Better Auth (JWT issued on client)

API Access: REST over HTTPS with Authorization header

Backend:

Framework: FastAPI

ORM: SQLModel

Auth: JWT verification middleware (Better Auth compatible)

API Style: REST (JSON)

Database:

PostgreSQL (Neon)

One database per environment

User-scoped data isolation enforced at query level

================================
FUNCTIONAL REQUIREMENTS

Authentication:

Users authenticate via Better Auth on the frontend.

Frontend MUST attach Authorization: Bearer <JWT> to every API request.

Backend MUST reject unauthenticated requests with HTTP 401.

Backend MUST extract user identity from JWT and scope all data to that user.

Todo Entity:
Each Todo item MUST contain:

id (UUID, primary key)

user_id (string, from JWT subject)

title (string, required)

description (string, optional)

completed (boolean, default false)

created_at (timestamp)

updated_at (timestamp)

REST API Endpoints (Backend):

GET /todos → list user todos

POST /todos → create todo

GET /todos/{id} → get single todo

PUT /todos/{id} → update title/description/completed

PATCH /todos/{id}/toggle → toggle completion

DELETE /todos/{id} → delete todo

All endpoints:

Require valid JWT

Operate ONLY on the authenticated user's data

Return JSON responses

Use proper HTTP status codes

Frontend Features:

Login / logout using Better Auth.

View list of todos.

Create new todo.

Edit existing todo.

Delete todo.

Toggle completion state.

Responsive UI (desktop + mobile).

Loading and error states for all API interactions.

================================
NON-FUNCTIONAL REQUIREMENTS

Security:

No unauthenticated access to data

No cross-user data leakage

JWT secret via environment variable only

Code Quality:

Clear separation of frontend and backend

Reusable frontend components

Backend routes grouped logically

No business logic in frontend beyond UI concerns

================================
CONSTRAINTS

No GraphQL

No WebSockets

No background jobs

No AI features in this phase

No schema changes without spec update (not allowed)

================================
DELIVERABLES

Fully specified API contract

Fully specified UI behavior

Fully specified data model

END OF PHASE 2 SPECIFICATION

## Response snapshot

Created feature specification for Phase 2 full-stack Todo web application (branch: 003-phase-2-web-app). Defined 5 user stories covering authentication (P1), CRUD operations (P1/P2), and mobile responsiveness (P3). Specified 13 functional requirements and 7 success criteria with measurable outcomes. No [NEEDS CLARIFICATION] markers required. All quality checklist items passed. Ready for `/sp.plan`.

## Outcome

- ✅ Impact: Created binding specification for Phase 2 web application covering Next.js frontend, FastAPI backend, Neon PostgreSQL, and Better Auth JWT authentication
- 🧪 Tests: None (specification phase)
- 📁 Files: 2 files created (spec.md, checklists/requirements.md)
- 🔁 Next prompts: `/sp.plan` to create architecture design
- 🧠 Reflection: Feature scope clearly defined with no ambiguities requiring clarification. User stories prioritized independently testable.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): All 16 quality checklist items PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
