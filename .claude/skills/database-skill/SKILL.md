---
name: database-skill
description: Design schemas, create tables, and implement reliable migrations for relational and NoSQL databases.
---

# Database Skill

## Instructions

1. **Schema Design**
   - Model entities and relationships (1–1, 1–N, N–M) before creating tables.
   - Define primary keys, foreign keys, unique constraints, and meaningful indexes.
   - Consider normalization level (3NF by default) and justified denormalization for read performance.

2. **Migrations**
   - Use a migration tool (Prisma Migrate, Knex, Flyway, Liquibase, Alembic).
   - Make migrations atomic and idempotent when possible.
   - Include `up` and `down` (or reversible) migration steps for safe rollbacks.
   - Run migrations in CI/CD and gate them with tests.

3. **Data Types & Constraints**
   - Choose precise column types (e.g., `timestamp with time zone`, `decimal(p,s)`).
   - Enforce data integrity with `NOT NULL`, `CHECK`, and `FOREIGN KEY` constraints.
   - Use length limits and enumerated types where appropriate.

4. **Indexes & Performance**
   - Add indexes for frequent query predicates and join keys.
   - Avoid over-indexing—monitor write amplification and storage cost.
   - Use partial, composite, or covering indexes to optimize targeted queries.

5. **Migrations for Production**
   - Use rolling, zero-downtime migration patterns (create-then-backfill-then-swap).
   - Avoid destructive operations on large tables; use safe migration patterns (new column → backfill → drop old).
   - Schedule heavy migrations during low-traffic windows and monitor metrics.

6. **Testing & Validation**
   - Write automated tests for migrations (apply, seed, rollback).
   - Validate schema with sample data and query performance checks.
   - Include data migration scripts with idempotency checks.

7. **Backups & Versioning**
   - Maintain regular backups and test restore procedures.
   - Store migration files in version control and tag releases with migration versions.

## Best Practices
- Use clear, consistent naming conventions: `snake_case`, plural table names (project-specific decision).
- Keep migrations small and focused—one logical change per migration file.
- Store secrets (DB credentials) securely in environment variables or secret manager.
- Record schema changes in changelogs and review in PRs.
- Add descriptive comments to complex columns or constraints.
- Prefer explicitness over implicit conversions; be conservative with automatic cascades.
- Apply principle of least privilege for DB users and roles.

## Example Structure

### SQL — Basic schema
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(254) NOT NULL UNIQUE,
  full_name VARCHAR(200),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE projects (
  id BIGSERIAL PRIMARY KEY,
  owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);