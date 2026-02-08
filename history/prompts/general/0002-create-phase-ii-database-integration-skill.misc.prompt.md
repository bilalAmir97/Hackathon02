---
id: "0002"
title: "Create Phase-II Database Integration Skill"
stage: "misc"
date: "2026-01-06"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "none"
branch: "002-reorganize-phase-1"
user: "local_user"
command: "/sp.skill.create"
labels: ["skill-creation","database","phase-2","sqlmodel","neon"]
links:
  spec: "null"
  ticket: "null"
  adr: "null"
  pr: "null"
files:
 - ".claude/skills/phase-2-database-integration/SKILL.md"
 - ".claude/skills/phase-2-database-integration/references/sqlmodel-patterns.md"
 - ".claude/skills/phase-2-database-integration/references/neon-setup.md"
 - ".claude/skills/phase-2-database-integration/references/alembic-migrations.md"
tests:
 - "null"
---

## Prompt

Skill: Phase-II Database Integration (Neon + SQLModel)
Phase: Phase II
Type: implementation (work-only)
Scope: Implement SQLModel models, migrations, and Neon connection logic. Ensure indexes and schema per /specs/database/schema.md.
Acceptance Criteria:

Models in /phase-2/backend/models.py match schema.

Migration scripts and README instructions included.
Artifacts to modify: /phase-2/backend/models.py, /phase-2/backend/migrations/**, /phase-2/backend/README-db.md
Constraints: Follow database spec exactly; do not alter spec files.

## Response snapshot

Created Phase-II Database Integration skill with:
- SKILL.md: Main skill file with workflow, quick start, and schema reference
- references/sqlmodel-patterns.md: SQLModel model definitions, relationships, field types, indexes
- references/neon-setup.md: Neon PostgreSQL connection, SSL, pooling configuration
- references/alembic-migrations.md: Alembic initialization, migration creation, best practices

## Outcome

- Impact: New skill available for implementing Phase II database layer
- Files: 4 skill files created under .claude/skills/phase-2-database-integration/
- Next prompts: Use this skill when implementing Phase II backend database components
- Reflection: Followed skill-creator pattern; created comprehensive reference files for database integration

## Evaluation notes (flywheel)

- Graders run and results (PASS/FAIL): "PASS - Skill structure follows project conventions"
