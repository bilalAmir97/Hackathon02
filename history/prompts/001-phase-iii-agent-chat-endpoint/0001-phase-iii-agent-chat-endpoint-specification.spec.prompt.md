---
id: 0001
title: Phase III Agent Chat Endpoint Specification
stage: spec
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: 001-phase-iii-agent-chat-endpoint
branch: 001-phase-iii-agent-chat-endpoint
user: bilal-amir
command: /sp.specify
labels: ["specification", "phase-iii", "agent", "chat-endpoint", "ai-orchestration", "mcp-tools", "openai-agents-sdk"]
links:
  spec: /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/spec.md
  - /home/bilal-amir/hackathon-02/specs/001-phase-iii-agent-chat-endpoint/checklists/requirements.md
tests:
  - none (specification phase)
---

## Prompt

AI Orchestration Layer — Agent + Chat Endpoint (Spec-2 — Phase-III Todo AI Chatbot)

Target audience:
Claude Code acting as a backend AI engineer building the agent orchestration layer that runs AI agents, registers MCP tools, and exposes a stateless chat endpoint.

Focus:
Implement an OpenAI Agents SDK–based agent runner that uses **MCP tools (not function tools)** for task operations, persists conversation & message history to Neon PostgreSQL, returns tool_call transparency, and exposes a single stateless chat endpoint `/api/{user_id}/chat`.

References (must be used)
- Official MCP server: https://modelcontextprotocol.io/docs/develop/build-server
- OpenAI Agents SDK (sessions, handoffs, dynamic instructions, guardrails, MCP integration): https://openai.github.io/openai-agents-python/
- Groq model (optional/high-throughput model): https://console.groq.com/docs/model/openai/gpt-oss-20b

Success criteria:
- Agent built with OpenAI Agents SDK and registered to call **MCP tools** (add_task, list_tasks, update_task, complete_task, delete_task).
- Chat endpoint `POST /api/{user_id}/chat` implements the stateless request cycle: store user message → fetch history → build messages → run agent → persist assistant response & tool_calls → return response with `tool_calls` array.
- Tool Call Transparency: every response includes structured `tool_calls` (tool name, inputs, outputs, status) for auditing and UI display.
- Conversation and messages persisted in DB (Conversation, Message models) and usable for resume/replay after restart.
- Agent uses MCP tools exclusively for data mutations; never directly mutate DB.
- JWT-based authentication enforced; `user_id` in path must match authenticated identity derived from token.
- Deterministic, guarded agent behavior (tool schemas, confirmation prompts, error handling, retry/backoff).

Constraints:
- Backend: Python FastAPI (existing Phase-II backend).
- AI framework: OpenAI Agents SDK (use MCP tool integration).
- Model: Prefer `openai/gpt-oss-20b` via Groq for high throughput; fall back to OpenAI-hosted models if unavailable. Document token/rate limits and plan for graceful degradation.
- MCP: Use Official MCP SDK tools implemented in Spec-1 (do not implement as function tools).
- DB: Neon Serverless PostgreSQL via SQLModel.
- Stateless: server holds no in-memory conversation state; DB is single source of truth.
- All configuration via environment variables; no hardcoded secrets.
- Output format: Markdown spec consumable by Claude Code.

Agent behavior & tooling rules:
- Intent → tool mapping: create/add → add_task, list/show → list_tasks, mark done → complete_task, delete → delete_task, rename/update → update_task.
- Always confirm destructive actions (delete, complete) with the user via the assistant before finalizing, unless message is explicit and confirmed.
- For ambiguous references (e.g., "delete the meeting task"), agent should call `list_tasks` (filtered) and ask user to pick one before delete_task.
- Tool inputs must be fully validated; tool response errors must be handled and presented to the user gracefully.
- Tool call responses must be deterministic JSON and included in final API response as `tool_calls`.

Elite implementation tips (must be included in spec execution):
1. Use **structured tool schemas** and strict typing to minimize hallucination surface; prefer explicit param names (user_id, task_id, title, description).
2. Seed agent instructions with a short deterministic system prompt that enforces "use MCP tools only" and a JSON-only output policy for tool-call steps.
3. Implement guardrails and dynamic instructions (session-level) using OpenAI Agents SDK features (sessions/handoffs) to control retries and tool usage.
4. Instrument exhaustive logging for tool calls (request id, user_id, tool inputs/outputs, timing) for auditability and debugging.
5. Respect Groq model limits: implement graceful rate-limit handling and fallback model selection to avoid service disruption.
6. Make tools idempotent where possible (e.g., create returns existing if duplicate) and design for safe retries.

API contract (concise)
- POST /api/{user_id}/chat
  - Request: `{ conversation_id?: int, message: string }` (JWT required)
  - Response: `{ conversation_id: int, response: string, tool_calls: [{tool, input, output, status}] }`

## Response snapshot

Created comprehensive specification for Phase III AI Orchestration Layer with agent chat endpoint. Generated feature branch `001-phase-iii-agent-chat-endpoint` and complete specification document.

**Key Deliverables**:
- 6 prioritized user stories (P1-P6) with independent test criteria
- 25 functional requirements covering stateless chat endpoint, MCP tool integration, conversation persistence, authentication, and agent behavior
- 10 measurable success criteria (technology-agnostic)
- Complete scope definition (12 in-scope, 12 out-of-scope items)
- Dependencies, assumptions, and risk mitigation strategies
- Specification quality checklist with validation results (all items pass)

**Validation Results**: All checklist items passed - no [NEEDS CLARIFICATION] markers, all requirements testable and unambiguous, success criteria measurable and technology-agnostic.

**Branch renamed** per user request to include "Phase-III" designation.

## Outcome

- ✅ Impact: Created complete, validated specification for AI agent orchestration layer with chat endpoint. Ready for planning phase.
- 🧪 Tests: Specification includes 6 user stories with detailed acceptance scenarios (Given-When-Then format) and 8 edge cases
- 📁 Files: Created spec.md (283 lines) and requirements.md checklist (validation passed)
- 🔁 Next prompts: `/sp.plan` to create architectural plan, or `/sp.clarify` if additional clarification needed
- 🧠 Reflection: Specification successfully balances technical detail with business focus. All requirements are testable without implementation details. User stories are properly prioritized and independently testable.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed without clarification needs
- Graders run and results (PASS/FAIL): Specification Quality Checklist - ALL PASS (Content Quality, Requirement Completeness, Feature Readiness)
- Prompt variant (if applicable): Standard /sp.specify workflow with quality validation
- Next experiment (smallest change to try): Proceed to planning phase to validate architectural decisions for OpenAI Agents SDK + MCP integration
