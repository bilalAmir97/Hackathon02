# Authentication Data Model

## User Entity
The User entity represents registered users in the system with authentication and authorization capabilities.

### Fields
- `id` (UUID): Unique identifier for the user
- `email` (String, 255): User's email address (unique, required)
- `password_hash` (String): Hashed password using bcrypt
- `status` (Enum): Account status (active, inactive, suspended)
- `password_changed_at` (DateTime): Timestamp of last password change
- `created_at` (DateTime): Account creation timestamp
- `updated_at` (DateTime): Last update timestamp

### Validation Rules
- Email must be valid and unique
- Password must meet complexity requirements
- Status transitions follow predefined rules
- Created_at is immutable after creation

### Relationships
- One-to-many with user-owned resources (todos, etc.)

## JWT Token Claims
The JWT token contains the following claims for authentication and authorization:

### Required Claims
- `sub` (Subject): User ID as string
- `user_id` (String): User ID for authorization checks
- `email` (String): User's email address
- `iat` (Issued At): Token issuance timestamp
- `exp` (Expiration): Token expiration timestamp

### Token Properties
- Algorithm: HS256 (HMAC with SHA-256)
- Lifetime: 30 minutes from issuance
- Secret: Shared BETTER_AUTH_SECRET between frontend and backend
- Storage: httpOnly cookies (recommended) or Authorization header

## Security Considerations
- Passwords must be hashed using bcrypt with cost factor 12
- JWT tokens must be validated for signature and expiration
- User isolation requires validation that JWT user_id matches path user_id
- Account status must be checked on each request
- Password change invalidates all active sessions