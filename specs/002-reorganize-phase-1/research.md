# Research: Phase I Reorganization

## Unknowns & Decisions

### Decision 1: Directory Structure
- **Decision**: Create `Phase I/` at the project root and move `src/`, `todo_app/`, `tests/`, `.gitignore`, `README.md`, and `requirements.txt` into it.
- **Rationale**: Groups all initial phase assets together, clearing the root for future phases (Phase II+).
- **Alternatives considered**:
    - Renaming current root? (Not viable as the repo itself is the container).
    - Moving to `v1/`? (Less descriptive than `Phase I`).

### Decision 2: File Handling (Move vs Copy)
- **Decision**: Perform a physical move (copy then delete from original location).
- **Rationale**: User clarified in Session 2026-01-01 that the root should be clean and zero orphaned files should remain.
- **Alternatives considered**: Copy and keep backup (Rejected by user).

### Decision 3: Path and Environment Handling
- **Decision**: Ensure execution instructions in `Phase I/README.md` are followed relative to the `Phase I/` directory root.
- **Rationale**: The application's module structure (e.g., `src.cli.app_controller`) depends on the parent directory of `src` being in the Python path. Running commands from within `Phase I/` satisfies this.
- **Alternatives considered**: Updating all relative paths in code (Unnecessary if execution context is moved).

## Best Practices
- **Atomic Operations**: Move directories using system-native commands to preserve structure and metadata.
- **Verification**: Run tests immediately after the move to confirm structural integrity.
- **Git State**: Use `git mv` where possible to preserve history, otherwise `mv` followed by `git add/rm`.
