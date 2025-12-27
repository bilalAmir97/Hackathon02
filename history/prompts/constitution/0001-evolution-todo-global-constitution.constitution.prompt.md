---
id: 0001
title: Evolution Todo Global Constitution
stage: constitution
date: 2025-12-27
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: system
command: /sp.constitution
labels: ["constitution", "governance", "principles", "spec-driven-development", "phase-governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution document)
---

## Prompt

Create a single global constitution for the entire "Evolution of Todo" project
covering Phase I through Phase V.

This constitution must define:

1. Spec-Driven Development as mandatory
   - No agent may write code without approved specs and tasks
   - All work must follow: Constitution → Specs → Plan → Tasks → Implement

2. Agent Behavior Rules
   - No manual coding by humans
   - No feature invention
   - No deviation from approved specifications
   - Refinement must occur at spec level, not code level

3. Phase Governance
   - Each phase is strictly scoped by its specification
   - Future-phase features must never leak into earlier phases
   - Architecture may evolve only through updated specs and plans

4. Technology Constraints
   - Python for backend
   - Next.js for frontend (later phases)
   - FastAPI, SQLModel, Neon DB
   - OpenAI Agents SDK, MCP
   - Docker, Kubernetes, Kafka, Dapr (later phases)

5. Quality Principles
   - Clean architecture
   - Stateless services where required
   - Clear separation of concerns

## Response snapshot

Created comprehensive global constitution (version 1.0.0) for the "Evolution of Todo"
project covering all five phases. The constitution establishes:

**Core Principles (9 total)**:
- I. Spec-Driven Development Mandate (NON-NEGOTIABLE)
- II. Agent Behavior Rules (NON-NEGOTIABLE)
- III. Phase Governance (NON-NEGOTIABLE)
- IV. Test-Driven Development (NON-NEGOTIABLE)
- V. Clean Architecture (NON-NEGOTIABLE)
- VI. Stateless Services (Required for Phase IV and V)
- VII. Contract-First Design
- VIII. Observability & Monitoring
- IX. Security & Compliance

**Additional Sections**:
- Technology Constraints: Fixed stack for backend, frontend, AI, and infrastructure
- Development Workflow: 7-step process from constitution review through PR merge
- Governance: Amendment process, compliance reviews, complexity justification

**Key Features**:
- Each principle includes rationale and enforcement mechanisms
- Phase boundaries clearly defined (I through V)
- All technology decisions locked down with substitution policy
- Quality gates defined for every PR
- Comprehensive documentation requirements
- Sync Impact Report included in constitution file header

**Compliance**:
- Reviewed spec-template.md, plan-template.md, tasks-template.md for alignment
- All templates align with constitution principles
- No template updates required

## Outcome

- ✅ Impact: Global constitution established for entire 5-phase project lifecycle
- 🧪 Tests: N/A (governance document)
- 📁 Files: Created/updated .specify/memory/constitution.md
- 🔁 Next prompts: `/sp.specify` for Phase I feature specification
- 🧠 Reflection: Constitution provides strong governance framework that prevents
  scope creep, enforces phase boundaries, and establishes clear agent behavior
  rules. All mandatory workflows (spec → plan → tasks → implement) are now
  codified with enforcement mechanisms.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, version
  properly set, principles comprehensive and enforceable
- Prompt variant (if applicable): N/A (initial version)
- Next experiment (smallest change to try): Monitor first feature spec creation
  to validate constitution principles are practical and sufficient
