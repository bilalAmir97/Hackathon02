# API Contracts: Frontend Premium UI & Full-Stack Integration

## Overview

This document defines the API contracts that the frontend application will consume. These are the existing backend API endpoints that the frontend will interact with for authentication and task management functionality.

## Authentication Endpoints

### POST /api/auth/register
Register a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-string",
    "email": "user@example.com"
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "Email already exists",
  "details": "A user with this email already exists"
}
```

### POST /api/auth/login
Authenticate a user and return JWT token.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK)**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user-uuid-string",
    "email": "user@example.com"
  }
}
```

**Response (401 Unauthorized)**:
```json
{
  "error": "Invalid credentials",
  "details": "Email or password is incorrect"
}
```

## Task Management Endpoints

### GET /api/{user_id}/tasks
Retrieve all tasks for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": "task-uuid-string",
      "userId": "user-uuid-string",
      "title": "Complete project proposal",
      "description": "Finish the project proposal document",
      "completed": false,
      "createdAt": "2024-01-15T10:30:00Z",
      "updatedAt": "2024-01-15T10:30:00Z"
    },
    {
      "id": "task-uuid-string-2",
      "userId": "user-uuid-string",
      "title": "Review code changes",
      "description": "Review pull requests from team members",
      "completed": true,
      "createdAt": "2024-01-15T09:15:00Z",
      "updatedAt": "2024-01-15T14:22:00Z"
    }
  ]
}
```

**Response (401 Unauthorized)**:
```json
{
  "error": "Unauthorized",
  "details": "Invalid or expired JWT token"
}
```

### POST /api/{user_id}/tasks
Create a new task for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Task description (optional)"
}
```

**Response (201 Created)**:
```json
{
  "task": {
    "id": "new-task-uuid-string",
    "userId": "user-uuid-string",
    "title": "New task title",
    "description": "Task description (optional)",
    "completed": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

**Response (400 Bad Request)**:
```json
{
  "error": "Validation error",
  "details": "Title is required and must be between 1 and 255 characters"
}
```

### GET /api/{user_id}/tasks/{id}
Retrieve a specific task for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token
- `id`: Task identifier

**Response (200 OK)**:
```json
{
  "task": {
    "id": "task-uuid-string",
    "userId": "user-uuid-string",
    "title": "Complete project proposal",
    "description": "Finish the project proposal document",
    "completed": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T10:30:00Z"
  }
}
```

### PUT /api/{user_id}/tasks/{id}
Update an existing task for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token
- `id`: Task identifier

**Request Body**:
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": false
}
```

**Response (200 OK)**:
```json
{
  "task": {
    "id": "task-uuid-string",
    "userId": "user-uuid-string",
    "title": "Updated task title",
    "description": "Updated task description",
    "completed": false,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T11:45:00Z"
  }
}
```

### DELETE /api/{user_id}/tasks/{id}
Delete a specific task for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token
- `id`: Task identifier

**Response (204 No Content)**:
```
[Empty response body]
```

### PATCH /api/{user_id}/tasks/{id}/complete
Toggle the completion status of a task for the authenticated user.

**Headers**:
```
Authorization: Bearer {jwt_token}
```

**Path Parameters**:
- `user_id`: User identifier extracted from JWT token
- `id`: Task identifier

**Response (200 OK)**:
```json
{
  "task": {
    "id": "task-uuid-string",
    "userId": "user-uuid-string",
    "title": "Complete project proposal",
    "description": "Finish the project proposal document",
    "completed": true,
    "createdAt": "2024-01-15T10:30:00Z",
    "updatedAt": "2024-01-15T12:30:00Z"
  }
}
```

## Error Response Format

All error responses follow this standard format:

```json
{
  "error": "Error message",
  "details": "Detailed error description",
  "timestamp": "2024-01-15T10:30:00Z",
  "path": "/api/user-uuid/tasks",
  "method": "GET"
}
```

## Authentication Flow

1. User submits credentials to `/api/auth/login` or `/api/auth/register`
2. Backend responds with JWT token
3. Frontend stores JWT token in httpOnly cookie
4. For subsequent API calls, backend verifies JWT token and extracts user_id
5. Backend ensures user can only access their own resources

## Security Considerations

- All API endpoints require valid JWT token in Authorization header
- User isolation enforced by backend - users can only access their own tasks
- JWT tokens should be stored securely using httpOnly cookies
- Token expiration handled automatically by auth system
- Sensitive operations require valid authentication

## Rate Limiting

All endpoints are subject to rate limiting:
- Anonymous endpoints: 100 requests per hour per IP
- Authenticated endpoints: 1000 requests per hour per user

## Versioning

This is version 1.0 of the API contract. All endpoints are currently at v1 level.