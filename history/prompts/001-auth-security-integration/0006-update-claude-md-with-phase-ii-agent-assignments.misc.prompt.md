---
id: 0006
title: Update CLAUDE.md with Phase II agent assignments
stage: misc
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-auth-security-integration
branch: 001-auth-security-integration
user: user
command: manual
labels: ["documentation", "agents", "phase-ii", "configuration", "project-setup"]
links:
  spec: specs/001-auth-security-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - (No tests - documentation update)
---

## Prompt

User requested update to CLAUDE.md file based on Phase II project requirements:

**Requirements**:
- Use authentication-security Agent for authentication
- Use nextjs-ui-architect Agent for frontend development (Next.js)
- Use neon-db-manager Agent for database design and operations
- Use fastapi-backend Agent for FastAPI development
- Use full-stack-debugger Agent for authentication, frontend, database, and FastAPI backend errors/issues
- Use e2e-integration-tester agent for full stack web app testing end to end

**Project Context**: Phase II Todo Full-Stack Web Application with Next.js 16+ frontend, FastAPI backend, Neon PostgreSQL database, and Better Auth authentication using JWT tokens.

**Better Auth JWT Flow**:
1. User logs in on Frontend → Better Auth creates session and issues JWT token
2. Frontend makes API call → Includes JWT token in Authorization: Bearer <token> header
3. Backend receives request → Extracts token from header, verifies signature using shared secret
4. Backend identifies user → Decodes token to get user ID, email, etc. and matches it with user ID in URL
5. Backend filters data → Returns only tasks belonging to that user

## Response snapshot

Added comprehensive "Phase II: Specialized Agent Assignments" section to CLAUDE.md with:

**Six Specialized Agents Documented**:
1. **authentication-security**: User signup/signin, Better Auth configuration, JWT verification, password hashing, authentication middleware
2. **nextjs-ui-architect**: Next.js 16+ pages, UI components, Better Auth integration, protected routes, API client with JWT injection
3. **neon-db-manager**: Database schemas, Alembic migrations, SQLModel models, query optimization, Neon PostgreSQL configuration
4. **fastapi-backend**: REST endpoints, Pydantic schemas, business logic, CRUD operations, authentication middleware, CORS configuration
5. **full-stack-debugger**: Authentication errors, JWT issues, frontend-backend communication, database errors, CORS issues, performance problems
6. **e2e-integration-tester**: Complete user journeys, authentication flow E2E, user isolation testing, frontend-backend integration, deployment validation

**Each Agent Section Includes**:
- "Use When" scenarios (specific triggers for agent invocation)
- Technology stack details
- Key responsibilities with file paths
- API contracts (for backend agent)
- Common debugging issues (for debugger agent)
- Testing scope (for E2E tester agent)

**Additional Content**:
- Agent Selection Guidelines (decision tree with 6 questions)
- Multi-Agent Collaboration examples (user registration, debugging authentication)
- Technology Constraints (must use/must not use)
- Success Criteria (8 checkpoints for Phase II completion)
- Better Auth JWT flow explanation (5-step process)

**Total Addition**: ~260 lines of comprehensive agent guidance

## Outcome

- ✅ Impact: Created comprehensive agent assignment guide for Phase II development. All 6 specialized agents now have clear responsibilities, use cases, and technology stacks documented. Developers and AI agents can now quickly determine which agent to use for any Phase II task.
- 🧪 Tests: No tests required (documentation update only)
- 📁 Files: Updated CLAUDE.md with Phase II agent assignments section (~260 lines added)
- 🔁 Next prompts: Ready to begin Phase II implementation using the documented agent assignments. Start with `/sp.implement` or invoke specific agents (e.g., authentication-security for auth setup, neon-db-manager for database schema).
- 🧠 Reflection: The agent assignment documentation provides clear decision trees and collaboration patterns. The Better Auth JWT flow is well-explained with the 5-step process. Multi-agent collaboration examples show how agents work together on complex tasks. Technology constraints ensure Phase II requirements are met.

## Evaluation notes (flywheel)

- Failure modes observed: None. Documentation successfully added to CLAUDE.md.
- Graders run and results (PASS/FAIL): Documentation completeness PASS, Agent responsibilities clearly defined PASS, Technology stack alignment PASS, Better Auth JWT flow documented PASS
- Prompt variant (if applicable): Standard documentation update workflow
- Next experiment (smallest change to try): Consider adding visual diagrams for Better Auth JWT flow and multi-agent collaboration patterns
