# API Documentation

**Version**: 1.0.0
**Base URL**: `http://localhost:8000`
**Feature**: 003-todo-backend-core

## Overview

This document provides complete API endpoint documentation for the Todo Backend Core service. The API follows REST principles and uses JSON for request/response payloads.

## Authentication

**Current Implementation**: User identification via UUID in URL path.

**Production Recommendation**: Implement JWT-based authentication with Bearer tokens. The user_id in the path should be validated against the authenticated user's token to prevent unauthorized access.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.yourdomain.com`

## Content Type

All requests and responses use `application/json` content type unless otherwise specified.

## Error Handling

All errors follow [RFC 7807 Problem Details](https://tools.ietf.org/html/rfc7807) format.

---

## Endpoints

### Health Check

#### GET /health

Check the health status of the API service.

**Request**:
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-01-12T10:30:45.123Z"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service is unhealthy (database connection failed)

---

## Task Management

All task endpoints are scoped to users. Each user can only access their own tasks.

### Create Task

#### POST /users/{user_id}/tasks

Create a new task for the specified user.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user creating the task

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | Yes | 1-200 chars | Task title |
| description | string | No | 0-2000 chars | Task description |

**Example Request**:
```bash
curl -X POST http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Response** (201 Created):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T00:00:00Z"
}
```

**Response Headers**:
- `Location`: `/users/{user_id}/tasks/{task_id}` - URL of the created task

**Status Codes**:
- `201 Created`: Task created successfully
- `422 Unprocessable Entity`: Validation error (invalid input)
- `503 Service Unavailable`: Database connection failed

**Error Examples**:

*Validation Error (422)*:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

*Service Unavailable (503)*:
```json
{
  "type": "https://api.example.com/errors/service-unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "Database connection unavailable. Please try again later.",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks"
}
```

---

### Get Task by ID

#### GET /users/{user_id}/tasks/{task_id}

Retrieve a specific task by its ID. Only returns tasks owned by the specified user.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user requesting the task
- `task_id` (UUID, required): UUID of the task to retrieve

**Example Request**:
```bash
curl http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T00:00:00Z"
}
```

**Status Codes**:
- `200 OK`: Task retrieved successfully
- `404 Not Found`: Task doesn't exist or doesn't belong to user
- `422 Unprocessable Entity`: Invalid UUID format
- `503 Service Unavailable`: Database connection failed

**Error Examples**:

*Not Found (404)*:
```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000"
}
```

---

### List Tasks

#### GET /users/{user_id}/tasks

Retrieve a paginated list of tasks for the specified user with optional status filtering.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user requesting tasks

**Query Parameters**:
| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| status | string | No | - | `pending` or `completed` | Filter by task status |
| offset | integer | No | 0 | >= 0 | Starting position for pagination |
| limit | integer | No | 20 | 1-100 | Maximum items per page |

**Example Requests**:
```bash
# List all tasks
curl http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks

# Filter by status
curl "http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks?status=pending"

# Pagination
curl "http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks?offset=20&limit=10"

# Combined filters
curl "http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks?status=completed&offset=0&limit=50"
```

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "created_at": "2026-01-12T00:00:00Z",
      "updated_at": "2026-01-12T00:00:00Z"
    }
  ],
  "total": 25,
  "offset": 0,
  "limit": 20,
  "has_next": true,
  "has_previous": false
}
```

**Response Schema**:
| Field | Type | Description |
|-------|------|-------------|
| items | array | List of task objects |
| total | integer | Total count of tasks matching the filter |
| offset | integer | Current offset position |
| limit | integer | Current limit value |
| has_next | boolean | Whether more results exist after current page |
| has_previous | boolean | Whether results exist before current page |

**Sorting**: Results are ordered by `created_at` DESC (newest first).

**Status Codes**:
- `200 OK`: Tasks retrieved successfully
- `422 Unprocessable Entity`: Invalid query parameters
- `503 Service Unavailable`: Database connection failed

---

### Update Task

#### PUT /users/{user_id}/tasks/{task_id}

Update an existing task. Supports partial updates - only provided fields will be updated.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user updating the task
- `task_id` (UUID, required): UUID of the task to update

**Request Body** (at least one field required):
```json
{
  "title": "Buy organic groceries",
  "description": "Organic milk, free-range eggs",
  "status": "completed"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| title | string | No | 1-200 chars | Updated task title |
| description | string | No | 0-2000 chars | Updated task description |
| status | string | No | `pending` or `completed` | Updated task status |

**Note**: At least one field must be provided for update.

**Example Request**:
```bash
curl -X PUT http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy organic groceries",
    "status": "completed"
  }'
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy organic groceries",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T01:00:00Z"
}
```

**Note**: The `updated_at` timestamp is automatically updated.

**Status Codes**:
- `200 OK`: Task updated successfully
- `404 Not Found`: Task doesn't exist or doesn't belong to user
- `422 Unprocessable Entity`: Validation error or no fields provided
- `503 Service Unavailable`: Database connection failed

---

### Delete Task

#### DELETE /users/{user_id}/tasks/{task_id}

Permanently delete a task. This operation cannot be undone.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user deleting the task
- `task_id` (UUID, required): UUID of the task to delete

**Example Request**:
```bash
curl -X DELETE http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000
```

**Response** (204 No Content):
Empty response body.

**Status Codes**:
- `204 No Content`: Task deleted successfully
- `404 Not Found`: Task doesn't exist or doesn't belong to user
- `422 Unprocessable Entity`: Invalid UUID format
- `503 Service Unavailable`: Database connection failed

---

### Toggle Task Completion

#### PATCH /users/{user_id}/tasks/{task_id}/complete

Toggle a task between pending and completed status.

**Path Parameters**:
- `user_id` (UUID, required): UUID of the user toggling the task
- `task_id` (UUID, required): UUID of the task to toggle

**Behavior**:
- If task status is `pending`, it will be changed to `completed`
- If task status is `completed`, it will be changed to `pending`

**Example Request**:
```bash
curl -X PATCH http://localhost:8000/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000/complete
```

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "completed",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T01:00:00Z"
}
```

**Note**: The `updated_at` timestamp is automatically updated.

**Status Codes**:
- `200 OK`: Task status toggled successfully
- `404 Not Found`: Task doesn't exist or doesn't belong to user
- `422 Unprocessable Entity`: Invalid UUID format
- `503 Service Unavailable`: Database connection failed

---

## Common Response Schemas

### Task Object

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "status": "pending",
  "created_at": "2026-01-12T00:00:00Z",
  "updated_at": "2026-01-12T00:00:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Unique task identifier |
| user_id | UUID | Owner's user identifier |
| title | string | Task title (1-200 chars) |
| description | string\|null | Task description (0-2000 chars) |
| status | string | Task status: `pending` or `completed` |
| created_at | ISO 8601 | Task creation timestamp (UTC) |
| updated_at | ISO 8601 | Last update timestamp (UTC) |

---

## Error Responses

All errors follow RFC 7807 Problem Details format.

### 404 Not Found

```json
{
  "type": "https://api.example.com/errors/not-found",
  "title": "Task Not Found",
  "status": 404,
  "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000"
}
```

### 422 Unprocessable Entity (Validation Error)

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

### 503 Service Unavailable

```json
{
  "type": "https://api.example.com/errors/service-unavailable",
  "title": "Service Unavailable",
  "status": 503,
  "detail": "Database connection unavailable. Please try again later.",
  "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks"
}
```

---

## HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT, PATCH requests |
| 201 | Created | Successful POST request |
| 204 | No Content | Successful DELETE request |
| 404 | Not Found | Resource doesn't exist or doesn't belong to user |
| 422 | Unprocessable Entity | Validation error |
| 503 | Service Unavailable | Database connection failed |

---

## Pagination

List endpoints support offset-based pagination:

**Parameters**:
- `offset`: Starting position (default: 0)
- `limit`: Maximum items per page (default: 20, max: 100)

**Response Metadata**:
- `total`: Total count of items matching the filter
- `has_next`: Boolean indicating if more results exist
- `has_previous`: Boolean indicating if previous results exist

**Example**:
```bash
# Page 1 (items 0-19)
curl "http://localhost:8000/users/{user_id}/tasks?offset=0&limit=20"

# Page 2 (items 20-39)
curl "http://localhost:8000/users/{user_id}/tasks?offset=20&limit=20"

# Page 3 (items 40-59)
curl "http://localhost:8000/users/{user_id}/tasks?offset=40&limit=20"
```

---

## Rate Limiting

**Current Implementation**: No rate limiting.

**Production Recommendation**: Implement rate limiting to prevent abuse:
- 100 requests per minute per user
- 1000 requests per hour per user
- Return `429 Too Many Requests` when limit exceeded

---

## CORS

**Current Implementation**: CORS is configured for development.

**Production Configuration**: Update CORS settings in `src/main.py` to allow only trusted origins.

---

## Versioning

**Current Version**: v1.0.0

**Strategy**: URL-based versioning (future: `/v1/users/{user_id}/tasks`)

---

## Interactive Documentation

FastAPI provides auto-generated interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Support

For issues or questions:
- Review specification: `/specs/003-todo-backend-core/spec.md`
- Check architecture plan: `/specs/003-todo-backend-core/plan.md`
- Review data model: `/specs/003-todo-backend-core/data-model.md`
