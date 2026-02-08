---
id: 0006
title: Database and Domain Models Implementation
stage: green
date: 2026-01-12
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-todo-backend-core
branch: 003-todo-backend-core
user: Bilal
command: Implement Phase 2 Database & Configuration + Domain Models
labels: ["database", "domain-models", "sqlmodel", "neon-postgresql", "pydantic", "async"]
links:
  spec: /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/specs/003-todo-backend-core/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/Phase-II/backend/src/config.py
  - /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/Phase-II/backend/src/database.py
  - /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/Phase-II/backend/src/domain/__init__.py
  - /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/Phase-II/backend/src/domain/models.py
  - /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/specs/003-todo-backend-core/tasks.md
tests:
  - Manual import verification tests passed
  - Ruff linting and formatting applied
---

## Prompt

Implement Phase 2 Database & Configuration + Domain Models for the Backend Core & Data Layer feature.

**Context**:
- Feature: 003-todo-backend-core (Phase II backend implementation)
- Backend Root: /mnt/d/Bilal/Bilal/Bilal_Data/Hackathon/hackathon-02/Phase-II/backend/
- Tech Stack: Python 3.13+, SQLModel, Neon Serverless PostgreSQL, asyncpg driver
- Database: Neon PostgreSQL with async operations

**Tasks to Complete** (T011-T020):

### Database & Configuration (T011-T014)

**T011**: Create Phase-II/backend/src/config.py with Settings class using pydantic-settings
- Use BaseSettings from pydantic-settings
- Environment variables: DATABASE_URL, DATABASE_POOL_SIZE (default: 10), DATABASE_MAX_OVERFLOW (default: 20), APP_ENV (default: "development"), LOG_LEVEL (default: "INFO"), API_HOST (default: "0.0.0.0"), API_PORT (default: 8000)
- Add model_config with env_file=".env", env_file_encoding="utf-8"

**T012**: Create Phase-II/backend/src/database.py with async engine, AsyncSession factory, get_session dependency
- Import: create_async_engine, AsyncSession, async_sessionmaker from sqlalchemy.ext.asyncio
- Create async engine with asyncpg driver: `postgresql+asyncpg://...`
- Create AsyncSession factory using async_sessionmaker
- Implement get_session() dependency for FastAPI (async generator that yields session)

**T013**: Configure connection pooling (pool_size=10, max_overflow=20) in database.py
- Add pool_size=10, max_overflow=20, pool_pre_ping=True to create_async_engine
- Add echo=True for development logging (conditional on APP_ENV)

**T014**: Add database health check function in database.py
- Implement async check_database_health() function
- Execute simple query: `SELECT 1`
- Return True if successful, False if connection fails
- Handle exceptions gracefully

### Domain Models (T015-T020)

**T015-T016** [P]: Create Phase-II/backend/src/domain/__init__.py and models.py with SQLModel base
- Import SQLModel, Field from sqlmodel
- Import UUID, uuid4, datetime, Enum

**T017**: Create User model in domain/models.py
- Table: user
- Fields: id (UUID, primary key, default_factory=uuid4), email (EmailStr, unique, indexed, max_length=255), created_at (datetime, default_factory=datetime.utcnow), updated_at (datetime, default_factory=datetime.utcnow)
- Use SQLModel with table=True

**T018**: Create Task model in domain/models.py
- Table: task
- Fields: id (UUID, primary key, default_factory=uuid4), user_id (UUID, foreign_key="user.id", indexed, nullable=False), title (str, min_length=1, max_length=200), description (str | None, default=None, max_length=2000), status (TaskStatus enum, default=TaskStatus.PENDING), created_at (datetime, default_factory=datetime.utcnow), updated_at (datetime, default_factory=datetime.utcnow)
- Use SQLModel with table=True

**T019**: Create TaskStatus enum in domain/models.py
- Enum values: PENDING = "pending", COMPLETED = "completed"
- Inherit from str and Enum

**T020**: Add table creation function in domain/models.py using SQLModel.metadata.create_all
- Implement async create_tables(engine) function
- Use SQLModel.metadata.create_all(bind=engine) with async context
- Import necessary async utilities

## Response snapshot

Successfully implemented all Database & Configuration and Domain Models tasks (T011-T020) for Phase 2 of the Backend Core feature.

### Implementation Details

**Configuration Module (config.py)**:
- Created Settings class using pydantic-settings BaseSettings
- Configured all required environment variables with validation
- Added Field constraints for database pool settings (ge=1, le=100)
- Pattern validation for APP_ENV and LOG_LEVEL
- Port validation (ge=1, le=65535)
- Loads from .env file with UTF-8 encoding

**Database Module (database.py)**:
- Created async engine with asyncpg driver for Neon PostgreSQL
- Configured connection pooling: pool_size=10, max_overflow=20, pool_pre_ping=True
- Added pool_recycle=3600 to prevent stale connections
- Implemented NullPool for test environment
- Created AsyncSession factory with proper configuration
- Implemented get_session() FastAPI dependency (async generator)
- Added check_database_health() function with graceful error handling
- Included init_db() and close_db() helper functions

**Domain Models (domain/models.py)**:
- Created TaskStatus enum (PENDING, COMPLETED) inheriting from str and Enum
- Implemented User model with UUID v4 identifiers
  - Fields: id, email (EmailStr with RFC 5322 validation), created_at, updated_at
  - Unique index on email, primary key on id
  - UTC timestamps using datetime.UTC
- Implemented Task model with full validation
  - Fields: id, user_id (FK to user.id), title (1-200 chars), description (optional, max 2000), status, timestamps
  - Foreign key constraint with index on user_id
  - Status defaults to PENDING
- Added create_tables() async function for table creation
- Comprehensive docstrings for all classes and functions

**Additional Work**:
- Installed email-validator dependency for EmailStr support
- Applied ruff formatting and linting (all issues resolved)
- Updated tasks.md to mark T011-T020 as complete
- Verified all modules import successfully

### Verification Results

All modules successfully tested:
- Config loads with correct defaults (pool_size=10, max_overflow=20)
- Database engine created with proper pooling configuration
- User model with 4 fields: id, email, created_at, updated_at
- Task model with 7 fields: id, user_id, title, description, status, created_at, updated_at
- TaskStatus enum with ['pending', 'completed'] values
- All helper functions available and working

## Outcome

- ✅ Impact: Phase 2 (Foundational) Database & Configuration + Domain Models complete. Foundation ready for user story implementation.
- 🧪 Tests: Manual import verification passed. No unit tests written yet (will be added in Phase 3 with TDD approach).
- 📁 Files: Created 4 new files (config.py, database.py, domain/__init__.py, domain/models.py), updated tasks.md
- 🔁 Next prompts: Implement Phase 3 (User Story 1) - Create and Retrieve Personal Tasks (T026-T045), starting with TDD tests
- 🧠 Reflection: Clean implementation following Neon serverless best practices. Used UUID v4 for security, proper connection pooling, and comprehensive validation. Ready for API layer implementation.

## Evaluation notes (flywheel)

- Failure modes observed: Initial missing email-validator dependency (resolved by adding to project dependencies)
- Graders run and results (PASS/FAIL): PASS - All imports successful, linting clean, models validated
- Prompt variant (if applicable): Standard implementation prompt with detailed task breakdown
- Next experiment (smallest change to try): Begin Phase 3 with TDD approach - write failing tests first before implementing use cases
