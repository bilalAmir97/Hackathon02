# API Contracts: Frontend Application & Full-Stack Integration

## Authentication API Contracts

### POST /api/auth/register
**Description**: Register a new user account
**Request**:
- Headers: `Content-Type: application/json`
- Body: `{ "email": string, "password": string }`
**Response**:
- Success (201): `{ "token": string, "user": { "id": string, "email": string } }`
- Error (400): `{ "error": "Invalid input", "code": "INVALID_INPUT" }`
- Error (409): `{ "error": "Email already registered", "code": "EMAIL_EXISTS" }`

### POST /api/auth/login
**Description**: Authenticate user and return JWT token
**Request**:
- Headers: `Content-Type: application/json`
- Body: `{ "email": string, "password": string }`
**Response**:
- Success (200): `{ "token": string, "user": { "id": string, "email": string } }`
- Error (400): `{ "error": "Invalid input", "code": "INVALID_INPUT" }`
- Error (401): `{ "error": "Invalid credentials", "code": "INVALID_CREDENTIALS" }`

## Task Management API Contracts

### GET /api/{user_id}/tasks
**Description**: Retrieve all tasks for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
**Response**:
- Success (200): `{ "tasks": [TaskResponse] }`
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`

### POST /api/{user_id}/tasks
**Description**: Create a new task for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
**Body**: `{ "title": string, "description": string, "completed": boolean }`
**Response**:
- Success (201): `{ "task": TaskResponse }`
- Error (400): `{ "error": "Invalid input", "code": "INVALID_INPUT" }`
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`

### GET /api/{user_id}/tasks/{id}
**Description**: Retrieve a specific task for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
- Path: `id` (task ID)
**Response**:
- Success (200): `{ "task": TaskResponse }`
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`
- Error (404): `{ "error": "Task not found", "code": "TASK_NOT_FOUND" }`

### PUT /api/{user_id}/tasks/{id}
**Description**: Update an existing task for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
- Path: `id` (task ID)
**Body**: `{ "title": string, "description": string, "completed": boolean }`
**Response**:
- Success (200): `{ "task": TaskResponse }`
- Error (400): `{ "error": "Invalid input", "code": "INVALID_INPUT" }`
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`
- Error (404): `{ "error": "Task not found", "code": "TASK_NOT_FOUND" }`

### DELETE /api/{user_id}/tasks/{id}
**Description**: Delete a task for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
- Path: `id` (task ID)
**Response**:
- Success (204): No content
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`
- Error (404): `{ "error": "Task not found", "code": "TASK_NOT_FOUND" }`

### PATCH /api/{user_id}/tasks/{id}/complete
**Description**: Toggle completion status of a task for the authenticated user
**Headers**: `Authorization: Bearer <token>`
**Parameters**:
- Path: `user_id` (must match authenticated user ID)
- Path: `id` (task ID)
**Body**: `{ "completed": boolean }`
**Response**:
- Success (200): `{ "task": TaskResponse }`
- Error (400): `{ "error": "Invalid input", "code": "INVALID_INPUT" }`
- Error (401): `{ "error": "Unauthorized", "code": "UNAUTHORIZED" }`
- Error (403): `{ "error": "Access denied", "code": "ACCESS_DENIED" }`
- Error (404): `{ "error": "Task not found", "code": "TASK_NOT_FOUND" }`

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| INVALID_INPUT | 400 | Request body validation failed |
| UNAUTHORIZED | 401 | Missing or invalid JWT token |
| ACCESS_DENIED | 403 | User attempting to access another user's resources |
| TASK_NOT_FOUND | 404 | Requested task does not exist |
| EMAIL_EXISTS | 409 | Email already registered during registration |

## Common Response Headers
- `Content-Type: application/json`
- `Cache-Control: no-cache` (for authenticated requests)