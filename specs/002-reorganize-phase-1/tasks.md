# Tasks: Phase I Reorganization

**Input**: Design documents from `/specs/002-reorganize-phase-1/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Existing tests in `tests/` will be used to validate the reorganization.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `Phase I/src/`, `Phase I/tests/`
- Paths shown below assume moving from repository root to `Phase I/` directory.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create `Phase I` directory at the project root

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Move `src/` directory to `Phase I/src/`
- [X] T003 Move `todo_app/` directory to `Phase I/todo_app/`
- [X] T004 Move `tests/` directory to `Phase I/tests/`
- [X] T005 [P] Move `.gitignore` to `Phase I/.gitignore`
- [X] T006 [P] Move `README.md` to `Phase I/README.md`
- [X] T007 [P] Move `requirements.txt` to `Phase I/requirements.txt`

**Checkpoint**: Foundation ready - structural move complete.

---

## Phase 3: User Story 1 - Consolidate Phase I Assets (Priority: P1) 🎯 MVP

**Goal**: Group all Phase I related files and directories into a single parent folder.

**Independent Test**: Verify all 6 specified assets are in `Phase I/` and removed from root.

### Implementation for User Story 1

- [X] T008 [US1] Remove original `src/` directory from project root
- [X] T009 [US1] Remove original `todo_app/` directory from project root
- [X] T010 [US1] Remove original `tests/` directory from project root
- [X] T011 [US1] Remove original `.gitignore` file from project root
- [X] T012 [US1] Remove original `README.md` file from project root
- [X] T013 [US1] Remove original `requirements.txt` file from project root

**Checkpoint**: At this point, the root is clean and User Story 1 is complete.

---

## Phase 4: User Story 2 - Maintain Project Functionality (Priority: P1)

**Goal**: Ensure that moving files does not break the core functionality.

**Independent Test**: Run tests from the `Phase I/` directory using `python -m pytest tests/`.

### Implementation for User Story 2

- [X] T014 [US2] Run all tests from `Phase I/` directory and verify they pass
- [X] T015 [US2] Verify application launch via `python -m src.cli.app_controller` from `Phase I/`

**Checkpoint**: User Story 2 complete - functionality verified.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verification and documentation

- [X] T016 Validate `Phase I/quickstart.md` steps manually
- [ ] T017 Update main project `README.md` (if one exists/required) to point to `Phase I/` (Optional/Deferred)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 (Phase 4)**: Depends on Phase 3.
- **Polish (Phase 5)**: Depends on Phase 4.

### Parallel Opportunities

- Tasks T005, T006, T007 can run in parallel.
- Cleanup tasks T008-T013 can be performed in parallel after verification of the move.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Create directory.
2. Complete Phase 2: Move files.
3. Complete Phase 3: Root cleanup.
4. **STOP and VALIDATE**: Verify root is clean and `Phase I/` is populated.

### Incremental Delivery

1. Physical move + Verification (Phase 1 & 2)
2. Root cleanup (Phase 3)
3. Final smoke test (Phase 4)
