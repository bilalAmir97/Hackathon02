---
id: "0003"
title: "Create Phase-II Better Auth JWT Integrator Skill"
stage: "misc"
date: "2026-01-06"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "002-reorganize-phase-1"
user: "local_user"
command: "/sp.skill.create"
labels: ["skill-creation","authentication","jwt","better-auth","phase-2"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
 - ".claude/skills/phase-ii-better-auth-jwt-integrator/SKILL.md"
 - ".claude/skills/phase-ii-better-auth-jwt-integrator/references/"
tests:
 - "null"
---

## Prompt

Skill: Phase-II Better Auth JWT Integrator
Phase: Phase II
Type: implementation (work-only)
Scope: Configure Better Auth on frontend to issue JWT and implement backend JWT verification using shared secret BETTER_AUTH_SECRET.
Acceptance Criteria:

Frontend attaches Authorization: Bearer <token> to API calls.

Backend middleware decodes and authorizes requests.
Artifacts to modify: /phase-2/frontend/auth/, /phase-2/backend/middleware/, environment example files.
Constraints: Implement per spec; do not change authentication requirements in specs.

## Response snapshot

Created Phase-II Better Auth JWT Integrator skill with:
- SKILL.md: Complete workflow for JWT authentication between Better Auth (frontend) and FastAPI (backend)
- Environment configuration: BETTER_AUTH_SECRET setup in frontend (.env.local) and backend (.env)
- Frontend patterns: Better Auth client with jwtPlugin, API client that attaches Authorization header
- Backend patterns: JWT verification middleware using python-jose, CurrentUser dependency
- Protected endpoint examples: Task CRUD endpoints with user isolation
- References to existing auth-security.md patterns

## Outcome

- Impact: New skill available for implementing JWT authentication flow in Phase II
- Files: 2 files created under .claude/skills/phase-ii-better-auth-jwt-integrator/
- Next prompts: Use this skill when implementing authentication for Phase II frontend/backend
- Reflection: Followed existing Phase II skill patterns; integrated with fastapi-backend-builder auth-security reference

## Evaluation notes (flywheel)

- Graders run and results (PASS/FAIL): "PASS - Skill structure follows project conventions, integrates with existing auth patterns"
