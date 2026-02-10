---
id: 0001
title: create-openai-agents-sdk-spec
stage: spec
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: 009-phase-iii-openai-agents-sdk
branch: 009-phase-iii-openai-agents-sdk
user: bilal-amir
command: /sp.specify
labels: ["phase-iii", "openai-agents-sdk", "mcp", "specification", "agent-orchestration"]
links:
  spec: /home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-phase-iii-openai-agents-sdk/spec.md
  - specs/009-phase-iii-openai-agents-sdk/checklists/requirements.md
tests:
  - None (specification phase)
---

## Prompt

Replace Mock Orchestration with OpenAI Agents SDK + MCP (Spec-2 Completion)

Target audience:
Claude Code acting as a senior AI backend engineer responsible for completing the agent layer by replacing mock intent detection with a real OpenAI Agents SDK runner integrated with MCP tools.

Focus:
Eliminate the mocked agent flow and implement a production-grade agent orchestration pipeline where the Runner invokes an Agent that exclusively uses MCP tools for task operations, persists conversation history, and returns structured tool-call transparency.

References (must be followed):
- MCP Server & Tooling: https://modelcontextprotocol.io/docs/develop/build-server
- OpenAI Agents SDK (sessions, MCP integration, guardrails, runner): https://openai.github.io/openai-agents-python/
- Groq model documentation: https://console.groq.com/docs/model/openai/gpt-oss-20b

Success criteria:
- Mock intent detection is fully removed from the codebase.
- AgentOrchestration uses Runner → Agent → MCP Adapter → Database flow.
- Agent successfully calls MCP tools (add_task, list_tasks, update_task, complete_task, delete_task).
- Tool calls are persisted in the database (JSON field or dedicated table).
- Chat endpoint returns structured tool_calls alongside assistant responses.
- Conversation history is injected into every agent run.
- Server remains fully stateless — database is the single source of truth.
- JWT identity enforced; agent operates only within authenticated user scope.
- Deterministic behavior configured (low temperature, structured instructions).
- System verified via real prompt tests (e.g., "Add a task to buy milk" triggers add_task).

Constraints:
- Must use OpenAI Agents SDK runner (no custom LLM wrappers).
- MCP Adapter is the single tool path — do NOT route through standalone MCP server.
- Agent is forbidden from directly mutating the database.
- All configuration via environment variables.
- Async execution required.
- Output format: Markdown spec consumable by Claude Code.

Agent rules (must be enforced in system prompt):
- ALWAYS use MCP tools for task operations.
- NEVER simulate tool usage.
- NEVER fabricate tasks.
- Database is the single source of truth.
- Confirm destructive actions before execution.
- Ask clarifying questions when task references are ambiguous.

Elite implementation requirements:
- Register MCP tools with strict schemas to minimize hallucinations.
- Persist assistant responses AND tool calls atomically.
- Implement structured logging for tool execution (tool name, inputs, outputs, latency).
- Add retry/backoff handling for model or tool failures.
- Gracefully handle Groq rate limits.

## Response snapshot

Created comprehensive specification for replacing mock intent detection with OpenAI Agents SDK integration:

**Branch Created**: 009-phase-iii-openai-agents-sdk

**Specification Structure**:
- 6 prioritized user stories (P1: core AI integration, P2: context/transparency, P3: reliability)
- 25 functional requirements covering agent runner, MCP tool integration, persistence, retry logic, and logging
- 10 measurable success criteria (95% intent accuracy, 100% tool call persistence, 5s response time)
- 4 key entities (Agent Configuration, Agent Runner, Tool Call Record, Retry Policy)
- Clear scope boundaries (13 in-scope items, 9 out-of-scope items)
- 10 assumptions and 9 dependencies documented
- 4 risks identified with mitigation strategies

**Quality Validation**: All checklist items passed - specification is complete, testable, and technology-agnostic.

**Key Architectural Flow**: Chat Endpoint → OpenAI Agents SDK Runner → Agent → MCP Adapter → Database

## Outcome

- ✅ Impact: Specification complete for replacing mock orchestration with production-grade OpenAI Agents SDK integration. Provides clear requirements for implementing real AI-powered natural language understanding while maintaining MCP tool architecture.
- 🧪 Tests: No tests created (specification phase). Test requirements defined in user stories with 18 acceptance scenarios.
- 📁 Files: Created spec.md (285 lines) and requirements.md checklist (validation passed)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or `/sp.clarify` if any requirements need refinement
- 🧠 Reflection: Specification successfully balances technical precision (25 FRs) with business clarity (no implementation details). All requirements are testable and measurable. Ready for planning phase.

## Evaluation notes (flywheel)

- Failure modes observed: None - specification completed successfully on first attempt
- Graders run and results (PASS/FAIL): Requirements checklist validation PASSED (14/14 items)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Proceed to planning phase with `/sp.plan` to design implementation approach
