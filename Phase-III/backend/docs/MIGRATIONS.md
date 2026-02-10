# Database Migration Strategy

**Feature**: 003-todo-backend-core
**Date**: 2026-01-12
**Status**: Active

## Overview

This document outlines the database migration strategy for the Todo Backend Core service. It covers schema management, migration approaches, and best practices for evolving the database schema over time.

## Current Approach

### SQLModel Metadata (Development)

**Current Implementation**: The application uses `SQLModel.metadata.create_all()` for automatic table creation during development.

**Location**: `src/main.py` - startup event handler

**Behavior**:
- Tables are created automatically on application startup
- Existing tables are not modified (idempotent)
- No migration history tracking
- Suitable for development and testing only

**Advantages**:
- Simple setup for development
- No migration files to manage
- Fast iteration during development

**Limitations**:
- No schema versioning
- No rollback capability
- Cannot handle complex schema changes (column renames, data migrations)
- Not suitable for production

## Recommended Production Approach

### Alembic Migrations

For production deployments, we recommend using **Alembic** for database migrations.

### Why Alembic?

- **Version Control**: Track schema changes over time
- **Rollback Support**: Revert to previous schema versions
- **Team Collaboration**: Share migrations via git
- **Complex Migrations**: Handle data transformations, column renames, etc.
- **Production Safety**: Review migrations before applying
- **SQLAlchemy Integration**: Works seamlessly with SQLModel

## Setup Instructions

### 1. Install Alembic

```bash
cd Phase-II/backend
uv add alembic
```

### 2. Initialize Alembic

```bash
uv run alembic init alembic
```

This creates:
```
Phase-II/backend/
├── alembic/
│   ├── versions/          # Migration files
│   ├── env.py            # Alembic environment configuration
│   ├── script.py.mako    # Migration template
│   └── README
└── alembic.ini           # Alembic configuration
```

### 3. Configure Alembic

**Edit `alembic.ini`**:
```ini
# Update database URL (or use environment variable)
sqlalchemy.url = postgresql+asyncpg://user:password@host:5432/database

# Or use environment variable (recommended)
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

**Edit `alembic/env.py`**:
```python
from src.config import settings
from src.domain.models import SQLModel

# Set target metadata
target_metadata = SQLModel.metadata

# Use async engine
config.set_main_option("sqlalchemy.url", settings.database_url)
```

### 4. Create Initial Migration

```bash
# Generate migration from current models
uv run alembic revision --autogenerate -m "Initial schema"

# Review the generated migration in alembic/versions/
# Edit if necessary to ensure correctness
```

### 5. Apply Migration

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Or apply specific version
uv run alembic upgrade <revision_id>
```

## Migration Workflow

### Development Workflow

1. **Make Model Changes**: Update SQLModel classes in `src/domain/models.py`
2. **Generate Migration**: `uv run alembic revision --autogenerate -m "Description"`
3. **Review Migration**: Check generated file in `alembic/versions/`
4. **Test Migration**: Apply to development database
5. **Commit Migration**: Add migration file to git
6. **Share with Team**: Push to repository

### Production Deployment Workflow

1. **Review Migrations**: Ensure all migrations are reviewed and tested
2. **Backup Database**: Create database backup before applying migrations
3. **Apply Migrations**: Run `alembic upgrade head` during deployment
4. **Verify Schema**: Check that schema matches expected state
5. **Monitor Application**: Watch for errors after deployment

## Common Migration Operations

### Add New Column

```bash
# Generate migration
uv run alembic revision --autogenerate -m "Add priority column to tasks"

# Review generated migration
# Apply migration
uv run alembic upgrade head
```

### Rename Column

```python
# Manual migration required (autogenerate sees this as drop + add)
def upgrade():
    op.alter_column('task', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('task', 'new_name', new_column_name='old_name')
```

### Add Index

```python
def upgrade():
    op.create_index('idx_task_user_status', 'task', ['user_id', 'status'])

def downgrade():
    op.drop_index('idx_task_user_status', table_name='task')
```

### Data Migration

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new column
    op.add_column('task', sa.Column('priority', sa.String(20), nullable=True))

    # Migrate data
    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE task SET priority = 'medium' WHERE priority IS NULL")
    )

    # Make column non-nullable
    op.alter_column('task', 'priority', nullable=False)

def downgrade():
    op.drop_column('task', 'priority')
```

## Migration Best Practices

### 1. Always Review Autogenerated Migrations

Alembic's autogenerate is helpful but not perfect. Always review:
- Column renames (detected as drop + add)
- Index changes
- Data type changes
- Constraint modifications

### 2. Test Migrations Before Production

```bash
# Test on development database
uv run alembic upgrade head

# Test rollback
uv run alembic downgrade -1

# Test upgrade again
uv run alembic upgrade head
```

### 3. Write Reversible Migrations

Always implement both `upgrade()` and `downgrade()`:
```python
def upgrade():
    op.add_column('task', sa.Column('priority', sa.String(20)))

def downgrade():
    op.drop_column('task', 'priority')
```

### 4. Use Transactions

Migrations run in transactions by default. For operations that can't run in transactions:
```python
# At top of migration file
revision = 'abc123'
down_revision = 'xyz789'

# Disable transaction for this migration
def upgrade():
    # Use op.execute() with autocommit for operations like CREATE INDEX CONCURRENTLY
    pass
```

### 5. Handle Data Carefully

For data migrations:
- Backup data before migration
- Test with production-like data volumes
- Consider downtime requirements
- Use batch operations for large tables

### 6. Version Control

- Commit migrations to git
- Never modify applied migrations
- Create new migration to fix issues
- Keep migration history linear

## Rollback Strategy

### Rollback Last Migration

```bash
uv run alembic downgrade -1
```

### Rollback to Specific Version

```bash
uv run alembic downgrade <revision_id>
```

### Rollback All Migrations

```bash
uv run alembic downgrade base
```

### Emergency Rollback

If migration fails in production:
1. Restore database from backup
2. Rollback application deployment
3. Fix migration locally
4. Test thoroughly
5. Redeploy

## Migration History

### View Current Version

```bash
uv run alembic current
```

### View Migration History

```bash
uv run alembic history
```

### View Pending Migrations

```bash
uv run alembic heads
```

## CI/CD Integration

### Pre-deployment Check

```bash
# Check for pending migrations
uv run alembic check

# Or compare current vs target
uv run alembic current
uv run alembic heads
```

### Automated Migration

```bash
# In deployment script
uv run alembic upgrade head
```

### Health Check

After deployment, verify schema version:
```bash
uv run alembic current
```

## Alternative: Manual SQL Scripts

For teams preferring manual control:

### Approach

1. Write SQL migration scripts manually
2. Store in `migrations/` directory
3. Track applied migrations in database table
4. Apply via custom migration runner

### Example Structure

```
Phase-II/backend/migrations/
├── 001_initial_schema.sql
├── 002_add_priority_column.sql
└── 003_add_indexes.sql
```

### Pros
- Full control over SQL
- No framework dependency
- Easy to review

### Cons
- Manual tracking required
- No autogenerate
- More maintenance

## Current Schema

### Tables

**user**:
- `id` (UUID, PK)
- `email` (VARCHAR, UNIQUE, NOT NULL)
- `created_at` (TIMESTAMP, NOT NULL)
- `updated_at` (TIMESTAMP, NOT NULL)

**task**:
- `id` (UUID, PK)
- `user_id` (UUID, FK → user.id, NOT NULL)
- `title` (VARCHAR(200), NOT NULL)
- `description` (VARCHAR(2000), NULL)
- `status` (VARCHAR(20), NOT NULL) - enum: 'pending', 'completed'
- `created_at` (TIMESTAMP, NOT NULL)
- `updated_at` (TIMESTAMP, NOT NULL)

### Indexes

- `task.user_id` (for user-scoped queries)
- `task.user_id, task.status` (for filtered queries)
- `task.user_id, task.created_at DESC` (for sorted pagination)

## Future Considerations

### Schema Evolution

Potential future migrations:
- Add `priority` field (low, medium, high)
- Add `due_date` field
- Add `tags` table (many-to-many)
- Add `archived` status
- Add soft delete support
- Add `completed_at` timestamp

### Performance Optimizations

- Add composite indexes for common queries
- Partition large tables by date
- Add materialized views for analytics

### Multi-tenancy

If scaling to multi-tenant:
- Add `tenant_id` to all tables
- Add row-level security policies
- Update all indexes to include `tenant_id`

## Troubleshooting

### Migration Fails

```bash
# Check current state
uv run alembic current

# Check for conflicts
uv run alembic heads

# Force stamp version (use with caution)
uv run alembic stamp head
```

### Schema Drift

If manual changes were made to database:
```bash
# Generate migration to sync
uv run alembic revision --autogenerate -m "Sync schema"

# Review carefully before applying
```

### Multiple Heads

If branches exist in migration history:
```bash
# Merge branches
uv run alembic merge -m "Merge migration branches" <rev1> <rev2>
```

## Resources

- **Alembic Documentation**: https://alembic.sqlalchemy.org
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

## Support

For migration issues:
- Review this document
- Check Alembic documentation
- Consult with database administrator
- Test in development environment first
