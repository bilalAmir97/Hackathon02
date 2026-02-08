# API Endpoints Reference

## Authentication Endpoints
- POST /api/auth/signup - Create new user account
- POST /api/auth/signin - Authenticate user and return JWT
- POST /api/auth/logout - Invalidate user session
- GET /api/auth/me - Get current user info (requires auth)

## Task Management Endpoints
- GET /api/tasks - Get user's tasks (requires auth)
- POST /api/tasks - Create new task (requires auth)
- PUT /api/tasks/{id} - Update task (requires auth)
- DELETE /api/tasks/{id} - Delete task (requires auth)

## Expected Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Optional message"
}
```

## Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```