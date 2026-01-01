# Data Model: Phase I Reorganization

Since this is a structural reorganization of files, the "data model" refers to the target directory structure.

## Entities

### Phase I Directory
- **Type**: Directory
- **Path**: `/Phase I/`
- **Purpose**: Root container for Phase I assets.

### Relocated Assets
The following entities are moved from the project root into `/Phase I/`:

| Original Path | Target Path | Type |
|---------------|-------------|------|
| `/src/` | `/Phase I/src/` | Directory |
| `/todo_app/` | `/Phase I/todo_app/` | Directory |
| `/tests/` | `/Phase I/tests/` | Directory |
| `/.gitignore` | `/Phase I/.gitignore` | File |
| `/README.md` | `/Phase I/README.md` | File |
| `/requirements.txt` | `/Phase I/requirements.txt` | File |

## Validation Rules
- **Existence**: Destination `Phase I/` must be created before moving files.
- **Completeness**: All 6 specified assets must be present in the new location.
- **Cleanliness**: The original paths in the root directory must be removed.
