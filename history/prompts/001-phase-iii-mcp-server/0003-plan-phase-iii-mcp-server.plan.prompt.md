---
id: 0003
title: Plan Phase III MCP Server
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase-iii-mcp-server
branch: 001-phase-iii-mcp-server
user: bilal-amir
command: /sp.plan
labels: ["planning", "mcp-server", "phase-iii", "architecture", "design", "research"]
links:
  spec: specs/001-phase-iii-mcp-server/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-iii-mcp-server/plan.md
  - specs/001-phase-iii-mcp-server/research.md
  - specs/001-phase-iii-mcp-server/data-model.md
  - specs/001-phase-iii-mcp-server/quickstart.md
  - specs/001-phase-iii-mcp-server/contracts/mcp-tools.json
  - specs/001-phase-iii-mcp-server/contracts/error-codes.json
  - CLAUDE.md (updated with MCP SDK context)
tests:
  - N/A (planning phase - no tests run)
---

## Prompt

/sp.plan

Analyze & Review my existing codebase architecture including backend & frontend directory in Phase-III folder then generate a plan file. here is the plan details:

Spec-1 MCP Server & Tooling Layer

Objective:
Build a stateless MCP server using the Official MCP SDK that exposes task operations as reliable tools backed by Neon PostgreSQL.

Plan (Research → Foundation → Analysis → Synthesis):

- Research: Review Official MCP SDK server patterns, tool schema design, and stateless execution practices; document DB session and validation tradeoffs.
- Foundation: Initialize MCP server structure, configure environment variables, establish SQLModel + Neon connection, and define base tool schemas.
- Analysis: Implement core tools (add, list, update, complete, delete) with strict input validation, user_id ownership checks, and structured JSON responses.
- Synthesis: Add centralized error handling, execution logging, and ensure tools remain fully stateless with request-scoped DB sessions.
- Quality validation: Manually verify each tool against acceptance criteria, confirm persistence, deterministic outputs, and agent-readiness.

Decisions needing documentation:
- Tool schema strictness vs flexibility.
- DB session lifecycle strategy.
- Error response format.

Testing strategy:
- Functional tests per tool.
- Ownership enforcement verification.
- Persistence checks after server restart.

## Response snapshot

Generated comprehensive implementation plan for MCP Todo Server with complete Phase 0 (Research) and Phase 1 (Design & Contracts) execution:

**Phase 0 - Research Completed**:
- Researched Official MCP SDK integration patterns → Decision: Use Python MCP SDK with separate ASGI app
- Researched tool schema design → Decision: Pydantic v2 models with JSON Schema generation
- Researched stateless session management → Decision: Request-scoped async context managers
- Researched authentication context extraction → Decision: JWT token from Authorization header
- Researched error handling → Decision: Standardized error format with machine-readable codes

**Phase 1 - Design & Contracts Completed**:
- Generated data-model.md with Task entity version field extension for optimistic concurrency
- Generated contracts/mcp-tools.json with complete schemas for all 5 MCP tools
- Generated contracts/error-codes.json with 7 standardized error codes
- Generated quickstart.md with setup, testing, and troubleshooting instructions
- Updated agent context (CLAUDE.md) with MCP SDK and Phase-III backend knowledge

**Key Architectural Decisions**:
1. **Code Reuse Strategy**: Extend existing Phase-III backend, reuse domain models, use cases, and database infrastructure
2. **Stateless Architecture**: Request-scoped database sessions, no in-memory state retention
3. **User Isolation**: Extract user_id from JWT token in Authorization header (not tool parameter)
4. **Concurrency Control**: Optimistic locking with version field (increment on each update)
5. **Error Format**: Standardized JSON with code, message, and details fields

**Constitution Compliance**: All gates passed (Phase Governance, Stateless Services, Clean Architecture, Contract-First Design, TDD, Security, Observability)

**Project Structure**: New src/mcp/ module in Phase-III/backend with tools/, schemas/, and middleware/ subdirectories

## Outcome

- ✅ Impact: Created production-ready implementation plan for MCP server with complete research findings, data model extensions, tool contracts, and quickstart guide enabling immediate task decomposition and implementation
- 🧪 Tests: No tests run (planning phase focuses on architecture and design)
- 📁 Files: 6 files created (plan.md, research.md, data-model.md, quickstart.md, 2 contract files) + 1 updated (CLAUDE.md)
- 🔁 Next prompts: `/sp.tasks` to generate atomic task breakdown, then `/sp.implement` to execute implementation
- 🧠 Reflection: Planning successfully analyzed existing Phase-III codebase and designed MCP server integration that maximizes code reuse while maintaining clean architecture. Research phase resolved all technical unknowns (MCP SDK integration, session management, auth extraction, error handling). Design phase produced complete contracts and data model extensions. Ready for task decomposition with no blockers.

## Evaluation notes (flywheel)

- Failure modes observed: None - all research areas resolved, constitution gates passed, contracts generated successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (all 7 gates), Code Reuse Analysis - PASS (maximized existing infrastructure), Contract Completeness - PASS (all 5 tools with input/output schemas)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design execution
- Next experiment (smallest change to try): Execute /sp.tasks to validate that plan provides sufficient detail for atomic task generation
