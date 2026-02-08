-- Database Schema Contract for Phase 2 Todo Application
-- This file defines the expected database schema that E2E tests will validate against
-- Database: Neon PostgreSQL (Serverless)
-- Version: 1.0.0

-- ============================================================================
-- USERS TABLE
-- ============================================================================
-- Stores user authentication and profile information

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,  -- bcrypt hash format: $2b$12$...
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Constraints
ALTER TABLE users ADD CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$');
ALTER TABLE users ADD CONSTRAINT chk_password_hash_format CHECK (password_hash LIKE '$2b$%');

-- ============================================================================
-- TODOS TABLE
-- ============================================================================
-- Stores todo items with user ownership

CREATE TABLE IF NOT EXISTS todos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for todos table
CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed);
CREATE INDEX IF NOT EXISTS idx_todos_user_completed ON todos(user_id, completed);

-- Constraints
ALTER TABLE todos ADD CONSTRAINT chk_title_not_empty CHECK (LENGTH(TRIM(title)) > 0);

-- ============================================================================
-- TRIGGERS
-- ============================================================================
-- Automatically update updated_at timestamp on record modification

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- TEST DATA VALIDATION QUERIES
-- ============================================================================
-- These queries are used by E2E tests to validate database state

-- Verify user password is hashed (not plaintext)
-- Expected: All password_hash values start with $2b$ (bcrypt format)
-- SELECT id, email, password_hash FROM users WHERE password_hash NOT LIKE '$2b$%';

-- Verify user data isolation (user can only see their own todos)
-- Expected: Empty result when checking for cross-user access
-- SELECT * FROM todos WHERE user_id != :authenticated_user_id;

-- Verify todo ownership
-- Expected: All todos for a user have matching user_id
-- SELECT id, title, user_id FROM todos WHERE user_id = :user_id;

-- Verify cascade delete (deleting user deletes their todos)
-- Expected: No orphaned todos after user deletion
-- SELECT COUNT(*) FROM todos WHERE user_id NOT IN (SELECT id FROM users);

-- ============================================================================
-- SCHEMA VALIDATION RULES FOR E2E TESTS
-- ============================================================================

-- Rule 1: Users table must exist with required columns
-- Columns: id (UUID), email (VARCHAR), password_hash (VARCHAR), created_at, updated_at

-- Rule 2: Todos table must exist with required columns
-- Columns: id (UUID), title (VARCHAR), description (TEXT), completed (BOOLEAN),
--          user_id (UUID), created_at, updated_at

-- Rule 3: Foreign key constraint must exist
-- todos.user_id REFERENCES users.id ON DELETE CASCADE

-- Rule 4: Indexes must exist for performance
-- idx_users_email, idx_todos_user_id, idx_todos_completed, idx_todos_user_completed

-- Rule 5: Password hashing must be enforced
-- All password_hash values must match bcrypt format: $2b$12$...

-- Rule 6: Timestamps must be automatically managed
-- created_at set on INSERT, updated_at updated on UPDATE

-- Rule 7: Data integrity constraints
-- - Email must be unique
-- - Email must be valid format
-- - Title must not be empty
-- - user_id must reference valid user

-- ============================================================================
-- SAMPLE TEST DATA
-- ============================================================================
-- Used by E2E tests for validation scenarios

-- Test User 1
-- INSERT INTO users (id, email, password_hash) VALUES
-- ('550e8400-e29b-41d4-a716-446655440001', 'test1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS.W9S8Gy');

-- Test User 2
-- INSERT INTO users (id, email, password_hash) VALUES
-- ('550e8400-e29b-41d4-a716-446655440002', 'test2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS.W9S8Gy');

-- Test Todos for User 1
-- INSERT INTO todos (id, title, description, completed, user_id) VALUES
-- ('650e8400-e29b-41d4-a716-446655440001', 'Buy groceries', 'Milk, eggs, bread', false, '550e8400-e29b-41d4-a716-446655440001'),
-- ('650e8400-e29b-41d4-a716-446655440002', 'Finish project', 'Complete Phase 2 implementation', true, '550e8400-e29b-41d4-a716-446655440001');

-- Test Todos for User 2
-- INSERT INTO todos (id, title, description, completed, user_id) VALUES
-- ('650e8400-e29b-41d4-a716-446655440003', 'Read book', 'Clean Code by Robert Martin', false, '550e8400-e29b-41d4-a716-446655440002');
