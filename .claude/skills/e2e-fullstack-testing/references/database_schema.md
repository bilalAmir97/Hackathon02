# Database Schema Reference

## Users Table
- id (UUID, Primary Key)
- email (VARCHAR, Unique, Not Null)
- password_hash (VARCHAR, Not Null)
- created_at (TIMESTAMP, Not Null)
- updated_at (TIMESTAMP, Not Null)

## Tasks Table
- id (UUID, Primary Key)
- user_id (UUID, Foreign Key to Users.id)
- title (VARCHAR, Not Null)
- description (TEXT)
- status (VARCHAR, Default: 'pending')
- created_at (TIMESTAMP, Not Null)
- updated_at (TIMESTAMP, Not Null)

## Indexes
- users_email_idx: UNIQUE INDEX ON users(email)
- tasks_user_id_idx: INDEX ON tasks(user_id)