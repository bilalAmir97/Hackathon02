---
id: 0005
title: Apply Remediation Edits
stage: misc
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-phase-iii-mcp-server
branch: 001-todo
user: bilal-amir
command: continuation
labels: ["remediation", "tdd-compliance", "constitution-fixes", "analysis-followup"]
links:
  spec: specs/001-phase-iii-mcp-server/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-iii-mcp-server/tasks.md
  - specs/001-phase-iii-mcp-server/spec.md
  - specs/001-phase-iii-mcp-server/plan.md
tests:
  - N/A (remediation phase - no tests run)
---

## Prompt

apply all the recommendations

(Context: User approved applying all three remediation edits identified during `/sp.analyze` session to resolve critical constitution violations and gaps)

## Response snapshot

Applied all three approved remediation edits to resolve critical issues identified during cross-artifact consistency analysis:

**Remediation 1 - TDD Compliance (Critical Issue C1/C2)**:
- Added Phase 2.5 "Test Infrastructure Setup" with 2 foundational test tasks (T015a-T015b)
- Added test-first implementation sections for all 5 user stories
- Inserted 15 test tasks before implementation tasks:
  - US1 (add_task): T015c-T015e (contract test, integration test, verify failure)
  - US2 (list_tasks): T023a-T023c (contract test, integration test, verify failure)
  - US3 (complete_task): T031a-T031c (contract test, integration test, verify failure)
  - US4 (update_task): T041a-T041c (contract test, integration test, verify failure)
  - US5 (delete_task): T062a-T062c (contract test, integration test, verify failure)
- Total: 17 new test tasks added to tasks.md
- All test tasks marked with "⚠️ CRITICAL: Write tests FIRST, verify they FAIL, then implement"
- Follows constitution Section IV mandate: "Tests written → User approved → Tests fail → Then implement"

**Remediation 2 - Conversation History Clarification (Critical Issue G1)**:
- Added to spec.md Out of Scope section: "Conversation/chat history and message persistence (handled by OpenAI ChatKit frontend - MCP server only provides stateless tools)"
- Clarifies that Phase III constitution requirement for "Database-persisted conversation history" is handled by frontend, not MCP server
- MCP server remains stateless and tool-focused per architecture

**Remediation 3 - Coverage Target Consistency (High Issue H3)**:
- Updated plan.md Test-Driven Development section
- Changed coverage target from absolute "80%+ for new MCP tool code" to conditional "80%+ for new MCP tool code (if tests are implemented per constitution Section IV)"
- Added note: "Test tasks are optional per feature specification but recommended for production readiness"
- Resolves inconsistency between plan claiming 80% coverage and tasks excluding all tests

**Constitution Compliance Status After Remediation**:
- Section IV (TDD): ✅ NOW COMPLIANT - Test tasks added before implementation tasks
- Section III (Phase Governance): ✅ NOW COMPLIANT - Conversation history scope clarified
- All other gates: ✅ PASS (unchanged)

## Outcome

- ✅ Impact: Resolved 2 CRITICAL constitution violations and 1 HIGH-severity inconsistency, bringing feature specification into full constitution compliance with 17 new test tasks enabling TDD workflow
- 🧪 Tests: No tests run (remediation edits only - tests will be executed during implementation phase)
- 📁 Files: 3 files modified (tasks.md with 17 test tasks, spec.md with conversation history clarification, plan.md with conditional coverage target)
- 🔁 Next prompts: `/sp.implement` to begin executing tasks with test-first approach, or `/sp.analyze` to re-validate consistency after remediation
- 🧠 Reflection: Remediation successfully addressed all critical issues identified during analysis. TDD compliance now enforced through explicit test tasks with "write tests first, verify failure" checkpoints. Conversation history scope clarified to prevent confusion about Phase III requirements. Coverage target made realistic given optional test implementation. Feature specification now ready for implementation with no constitution blockers.

## Evaluation notes (flywheel)

- Failure modes observed: None - all three remediation edits applied successfully without conflicts or errors
- Graders run and results (PASS/FAIL): Constitution Section IV compliance - PASS (test tasks added), Phase Governance compliance - PASS (conversation history clarified), Coverage target consistency - PASS (conditional wording added)
- Prompt variant (if applicable): Standard remediation workflow following `/sp.analyze` findings
- Next experiment (smallest change to try): Execute Phase 2.5 test infrastructure tasks (T015a-T015b) to validate test framework setup before implementing user stories
