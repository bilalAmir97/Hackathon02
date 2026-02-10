---
id: 0003
title: Phase III Agent Chat Endpoint Plan
stage: plan
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-iii-agent-chat-endpoint
branch: 001-phase-iii-agent-chat-endpoint
user: bilal-amir
command: /sp.plan
labels: ["planning", "phase-iii", "agent-orchestration", "mcp-integration", "openai-agents-sdk", "groq", "architecture"]
links:
  spec: /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/plan.md
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/research.md
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/data-model.md
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/quickstart.md
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/contracts/chat-endpoint.openapi.yaml
tests:
  - none (planning phase - tests defined in plan for implementation)
---

## Prompt

Analyze and review my codebase including frontend and backend directories in Phase-III folder Spec-2 AI Orchestration Layer

Objective:
Implement a stateless AI agent with MCP tool integration and a production-ready chat endpoint that persists conversations and returns tool-call transparency.

Plan (Research → Foundation → Analysis → Synthesis):

- Research: Review OpenAI Agents SDK (sessions, guardrails, MCP integration) and Groq model limits; document tool-registration strategy and fallback model tradeoffs.
- Foundation: Create Conversation/Message schemas, configure env variables, set up Groq model (`openai/gpt-oss-20b`) with optional fallback, and prepare MCP tool adapter.
- Analysis: Implement `/api/{user_id}/chat` endpoint with stateless cycle (store → fetch history → run agent → persist response → return tool_calls); register MCP tools and enforce JWT identity checks.
- Synthesis: Add deterministic agent instructions, guardrails, structured logging for tool calls, confirmation responses, and centralized error handling with retry/backoff.
- Quality validation: Test tool-call correctness, conversation persistence after restart, ownership enforcement, rate-limit handling, and deterministic agent behavior.

Decisions needing documentation:
- Groq-only vs fallback model strategy.
- Tool transparency schema format.
- Guardrail strictness vs agent flexibility.

Testing strategy:
- Integration tests for intent → tool mapping.
- Persistence verification across sessions.
- Auth + user isolation tests.
- Rate-limit and failure recovery checks.

User specified: Use Groq `openai/gpt-oss-20b` model (200k tokens/min, 30 req/min, 1000 req/day), OpenAI Agents SDK with MCP tools (not function tools), and official MCP SDK documentation.

## Response snapshot

Created comprehensive implementation plan for Phase III AI Orchestration Layer with complete architecture, research findings, data models, API contracts, and quickstart guide.

**Planning Artifacts Created**:
1. **plan.md** (728 lines): Complete implementation plan with constitution compliance check, project structure, complexity tracking, Phase 0 research tasks, Phase 1 design specifications, and 4 ADRs
2. **research.md** (300+ lines): Technology research covering OpenAI Agents SDK MCP integration, Groq model configuration, stateless conversation architecture, agent guardrails, and tool transparency schema
3. **data-model.md** (400+ lines): Database schema for Conversation and Message models with SQLModel definitions, migration scripts, query patterns, and performance considerations
4. **contracts/chat-endpoint.openapi.yaml** (200+ lines): Complete OpenAPI 3.0 specification for chat endpoint with request/response schemas, error handling, and examples
5. **quickstart.md** (400+ lines): Comprehensive setup guide with environment configuration, database migration, testing examples, troubleshooting, and monitoring

**Key Architectural Decisions (ADRs)**:
- ADR-001: Groq as primary model with OpenAI fallback for reliability and cost optimization
- ADR-002: Database-persisted conversation history for stateless design
- ADR-003: MCP tools only policy for separation of concerns
- ADR-004: Tool call transparency schema for auditability and frontend display

**Constitution Compliance**: ALL GATES PASSED ✅
- Phase Governance: Phase III requirements, Basic Level only, no future-phase leakage
- Spec-Driven Development: Approved spec, plan before code, tasks next
- Stateless Services: No in-memory state, database-persisted conversations
- Clean Architecture: Existing structure maintained, new components fit into layers
- All other principles verified and compliant

**Technical Architecture**:
- Stateless request cycle: store → fetch → run → persist → return
- MCP adapter pattern for tool integration with user_id context injection
- Groq primary with automatic OpenAI fallback on rate limits
- PostgreSQL with JSONB for tool_calls transparency
- Multi-turn confirmation flows with explicit override capability

## Outcome

- ✅ Impact: Created production-ready implementation plan with complete architecture, research, data models, API contracts, and setup guide. Ready for task decomposition via `/sp.tasks`.
- 🧪 Tests: Defined comprehensive testing strategy (unit, integration, contract, E2E) in plan.md with specific test scenarios for each user story
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, quickstart.md, chat-endpoint.openapi.yaml) totaling 2000+ lines of documentation
- 🔁 Next prompts: `/sp.tasks` to generate atomic implementation tasks, then `/sp.implement` to execute tasks with TDD approach
- 🧠 Reflection: Planning phase successfully balanced technical depth with practical implementation guidance. All constitution gates passed. Research findings provide clear implementation patterns for OpenAI Agents SDK + MCP integration. Data model supports stateless architecture. API contract enables frontend integration. Quickstart guide ensures smooth developer onboarding.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning workflow completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): Constitution Check - ALL PASS (9/9 gates), Architecture Design - COMPLETE, Documentation - COMPREHENSIVE
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design artifacts
- Next experiment (smallest change to try): Execute `/sp.tasks` to validate if plan provides sufficient detail for atomic task generation, then implement first task to verify architecture decisions
