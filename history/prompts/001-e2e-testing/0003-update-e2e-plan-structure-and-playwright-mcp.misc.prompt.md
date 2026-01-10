---
id: 0003
title: Update E2E Plan Structure and Playwright MCP
stage: misc
date: 2026-01-10
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-e2e-testing
branch: 001-e2e-testing
user: bilal-amir
command: /sp.plan
labels: ["plan-update", "playwright-mcp", "directory-structure", "documentation"]
links:
  spec: /specs/001-e2e-testing/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/001-e2e-testing/plan.md
  - /specs/001-e2e-testing/quickstart.md
tests:
  - None (documentation update only)
---

## Prompt

update the structure according to my @phase-2/ dir and remove the playright.config.ts in @specs/001-e2e-testing/plan.md  as playright mcp is already installed

## Response snapshot

Successfully updated E2E testing plan and quickstart guide to reflect actual project structure and Playwright MCP integration:

**Plan.md Updates:**
- Updated project structure to match actual phase-2/ directory layout
- Reflected existing directories: phase-2/backend/src/, phase-2/backend/tests/, phase-2/frontend/src/
- Marked test directories as "to be created" vs "existing"
- Removed playwright.config.ts reference (not needed with MCP)
- Updated structure decision to note Playwright MCP is already installed
- Clarified that shared fixtures live in phase-2/backend/tests/fixtures/ and phase-2/backend/tests/utils/

**Quickstart.md Updates:**
- Removed Playwright installation instructions (npm install @playwright/test, npx playwright install)
- Replaced with note: "Playwright MCP is already installed and configured"
- Removed all npx playwright test commands
- Replaced with notes about MCP integration for E2E test execution
- Updated debugging section to reflect MCP-based execution
- Updated CI/CD workflow to remove Playwright installation steps
- Updated troubleshooting section for MCP-based browser management
- Updated test reporting section to note MCP handles reports automatically

**Key Changes:**
1. Aligned directory structure with actual phase-2/ layout (backend/src/, backend/tests/, frontend/src/)
2. Removed all direct Playwright CLI commands (npx playwright)
3. Documented that Playwright MCP handles browser automation, debugging, and reporting
4. Maintained pytest-based backend testing approach (unchanged)
5. Clarified test organization: backend tests in phase-2/backend/tests/, frontend E2E in phase-2/frontend/tests/e2e/

## Outcome

- ✅ Impact: Plan and quickstart documentation now accurately reflect the actual project structure and Playwright MCP integration. Developers will no longer be confused by references to non-existent playwright.config.ts or unnecessary installation steps.
- 🧪 Tests: No tests affected (documentation update only). Test strategy remains unchanged: 3-layer architecture with MCP-based E2E execution.
- 📁 Files: Updated 2 files - plan.md (project structure section) and quickstart.md (installation, execution, debugging, CI/CD, troubleshooting, and reporting sections).
- 🔁 Next prompts: Ready to proceed with /sp.tasks to generate implementation tasks based on updated plan. No further plan updates needed.
- 🧠 Reflection: Update correctly addressed user's request to align documentation with actual codebase structure. Playwright MCP integration simplifies setup by eliminating manual browser installation and configuration. Documentation now accurately reflects that MCP handles E2E test execution, debugging, and reporting automatically.

## Evaluation notes (flywheel)

- Failure modes observed: None. Documentation updates completed successfully.
- Graders run and results (PASS/FAIL): No graders run (documentation update only).
- Prompt variant (if applicable): User-requested plan update to align with actual project structure.
- Next experiment (smallest change to try): Proceed to /sp.tasks to validate that updated plan generates correct implementation tasks for the actual directory structure.
