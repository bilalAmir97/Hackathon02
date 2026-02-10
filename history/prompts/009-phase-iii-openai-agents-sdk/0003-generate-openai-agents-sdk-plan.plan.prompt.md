---
id: 0003
title: generate-openai-agents-sdk-plan
stage: plan
date: 2026-02-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: 009-phase-iii-openai-agents-sdk
branch: 009-phase-iii-openai-agents-sdk
user: bilal-amir
command: /sp.plan
labels: ["planning", "openai-agents-sdk", "phase-iii", "architecture", "design"]
links:
  spec: /home/bilal-amir/hackathon-02/specs/009-phase-iii-openai-agents-sdk/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/009-phase-iii-openai-agents-sdk/plan.md
tests:
  - None (planning phase)
---

## Prompt

/sp.plan

Analyze and review my codebase including the backend and frontend directories of Phase-III and Also Analyze @OpenAIAgents_SampleCode then, generate plan file

## Response snapshot

Generated comprehensive implementation plan for replacing mock orchestration with OpenAI Agents SDK integration.

**Plan Structure**:
- Technical Context: Python 3.13+, FastAPI, OpenAI Agents SDK, Groq/OpenAI providers
- Constitution Check: All 9 principles validated (✅ passed)
- Project Structure: Phase-III backend with agent modules
- Phase 0 Research: 5 research tasks (OpenAI Agents SDK, Groq integration, tool extraction, retry logic, history management)
- Phase 1 Design: 7 design components (RunnerFactory, RetryPolicy, HistoryManager, contracts, orchestration flow, config, logging)
- Phase 2 Implementation: 10 sequential steps with dependencies

**Key Architectural Decisions**:
1. Runner → Agent → MCP Adapter → Database flow
2. Groq primary (openai/gpt-oss-20b) + OpenAI fallback (gpt-4o-mini)
3. Temperature 0.1, max tokens 500, timeout 30s
4. Exponential backoff: 100ms initial, 5s max, 2x multiplier
5. Conversation history: 20 messages (message-based truncation)
6. Structured logging for all agent invocations and tool executions

**Files to Create**:
- src/agent/runner_factory.py - Factory for Runner instances
- src/agent/retry_policy.py - Exponential backoff logic
- src/agent/history_manager.py - Conversation truncation

**Files to Modify**:
- src/agent/agent_factory.py - Use RunnerFactory
- src/agent/instructions.py - Remove detect_intent()
- src/use_cases/agent_orchestration.py - Replace mock with real agent
- src/config.py - Update temperature to 0.1, max_tokens to 500
- .env.example - Document agent configuration

**Implementation Sequence**: Bottom-up approach (utilities → core integration → orchestration → cleanup)

## Outcome

- ✅ Impact: Comprehensive implementation plan created with 10 sequential steps, clear dependencies, and detailed design specifications. Plan provides complete roadmap for replacing mock intent detection with production-grade OpenAI Agents SDK integration.
- 🧪 Tests: Test strategy defined for each module (unit, integration, contract tests). TDD approach specified with tests before implementation.
- 📁 Files: Created plan.md (838 lines) with technical context, constitution check, research tasks, design specifications, and implementation sequence
- 🔁 Next prompts: `/sp.tasks` to generate atomic implementation tasks from this plan
- 🧠 Reflection: Plan successfully integrates OpenAI Agents SDK sample code pattern with existing codebase structure. All constitution principles validated. Clear separation of concerns with RunnerFactory, RetryPolicy, and HistoryManager utilities. Implementation sequence follows bottom-up approach for testability.

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generation completed successfully
- Graders run and results (PASS/FAIL): Constitution check PASSED (9/9 principles validated)
- Prompt variant (if applicable): Standard /sp.plan workflow with codebase analysis
- Next experiment (smallest change to try): Proceed to task generation with `/sp.tasks`
