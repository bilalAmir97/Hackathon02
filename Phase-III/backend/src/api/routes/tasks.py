"""Task management API endpoints.

Provides RESTful endpoints for task CRUD operations with user-scoped
data access. All endpoints enforce ownership verification.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.dependencies import get_current_user
from src.domain.models import TaskStatus
from src.middleware.error_handler import DatabaseError, TaskNotFoundError, ValidationError
from src.schemas.task import PaginatedTaskResponse, TaskCreate, TaskResponse, TaskUpdate
from src.use_cases.task_operations import (
    count_tasks,
    create_task,
    delete_task,
    get_task_by_id,
    list_tasks,
    toggle_task_completion,
    update_task,
)

router = APIRouter(prefix="/api", tags=["tasks"])


@router.post(
    "/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user. Returns the created task with generated ID and timestamps. Requires valid JWT token.",
    response_description="Created task with all fields",
    responses={
        201: {
            "description": "Task created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "status": "pending",
                        "created_at": "2026-01-12T00:00:00Z",
                        "updated_at": "2026-01-12T00:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid input data",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body", "title"],
                                "msg": "field required",
                                "type": "value_error.missing",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
                    }
                }
            },
        },
    },
)
async def create_task_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user creating the task",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    task_data: TaskCreate = ...,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Create a new task for an authenticated user.

    Creates a new task with the provided title and optional description.
    The task is assigned a unique UUID and defaults to 'pending' status.
    Requires valid JWT token and enforces user isolation.

    Args:
        user_id: UUID of the user creating the task (path parameter)
        task_data: Task creation data (title, description)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        JSONResponse: Created task with Location header

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        ValidationError: If input validation fails (422)
        DatabaseError: If database operation fails (503)
    """
    # T050: Validate user_id match - User A cannot create tasks for User B
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # T051: Create task with user_id from authenticated user (not from request body)
        task = await create_task(session, user_id, task_data)

        # Convert to response schema
        task_response = TaskResponse.model_validate(task)

        # Create response with Location header
        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=task_response.model_dump(mode="json"),
            headers={
                "Location": f"/api/{user_id}/tasks/{task.id}",
            },
        )

        return response

    except DatabaseError:
        # Database errors are handled by exception handler
        raise
    except ValueError as e:
        # Validation errors from Pydantic
        raise ValidationError(str(e)) from e


@router.get(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
    description="Retrieve a specific task by its ID. Only returns tasks owned by the authenticated user. Requires valid JWT token.",
    response_description="Task details",
    responses={
        200: {
            "description": "Task retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "status": "pending",
                        "created_at": "2026-01-12T00:00:00Z",
                        "updated_at": "2026-01-12T00:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        404: {
            "description": "Task not found or does not belong to user",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/not-found",
                        "title": "Task Not Found",
                        "status": 404,
                        "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid UUID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "task_id"],
                                "msg": "value is not a valid uuid",
                                "type": "type_error.uuid",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
    },
)
async def get_task_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user requesting the task",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    task_id: UUID = Path(
        ...,
        description="UUID of the task to retrieve",
        example="123e4567-e89b-12d3-a456-426614174000",
    ),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Retrieve a task by ID with ownership verification.

    Retrieves a task only if it exists and belongs to the authenticated user.
    Returns 404 for both non-existent tasks and tasks belonging to other
    users (timing attack prevention). Requires valid JWT token.

    Args:
        user_id: UUID of the user requesting the task (path parameter)
        task_id: UUID of the task to retrieve (path parameter)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        TaskResponse: Task details

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        TaskNotFoundError: If task doesn't exist or doesn't belong to user (404)
        DatabaseError: If database operation fails (503)
    """
    # T052: Validate user_id match - User A cannot access User B's tasks
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # Retrieve task with ownership verification
        task = await get_task_by_id(session, user_id, task_id)

        # Convert to response schema
        return TaskResponse.model_validate(task)

    except TaskNotFoundError:
        # TaskNotFoundError is handled by exception handler
        raise
    except DatabaseError:
        # DatabaseError is handled by exception handler
        raise


@router.get(
    "/{user_id}/tasks",
    response_model=PaginatedTaskResponse,
    status_code=status.HTTP_200_OK,
    summary="List tasks for a user",
    description="Retrieve a paginated list of tasks for the authenticated user with optional status filtering. Results are ordered by creation date (newest first). Requires valid JWT token.",
    response_description="Paginated list of tasks with metadata",
    responses={
        200: {
            "description": "Tasks retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                                "title": "Buy groceries",
                                "description": "Milk, eggs, bread",
                                "status": "pending",
                                "created_at": "2026-01-12T00:00:00Z",
                                "updated_at": "2026-01-12T00:00:00Z",
                            }
                        ],
                        "total": 25,
                        "offset": 0,
                        "limit": 20,
                        "has_next": True,
                        "has_previous": False,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["query", "limit"],
                                "msg": "ensure this value is less than or equal to 100",
                                "type": "value_error.number.not_le",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks",
                    }
                }
            },
        },
    },
)
async def list_tasks_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user requesting tasks",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    status_filter: TaskStatus | None = Query(
        default=None,
        alias="status",
        description="Optional status filter (pending or completed)",
        example="pending",
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Starting position for pagination (min: 0)",
        example=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Maximum items per page (min: 1, max: 100)",
        example=20,
    ),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """List tasks for an authenticated user with optional filtering and pagination.

    Retrieves tasks belonging to the authenticated user with optional status
    filtering and pagination support. Results are ordered by created_at
    DESC (newest first). Requires valid JWT token.

    Args:
        user_id: UUID of the user requesting tasks (path parameter)
        status_filter: Optional status filter (query parameter)
        offset: Starting position for pagination (query parameter)
        limit: Maximum items per page (query parameter)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        PaginatedTaskResponse: Paginated list of tasks with metadata

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        ValidationError: If query parameters are invalid (422)
        DatabaseError: If database operation fails (503)
    """
    # T049: Validate user_id match - User A cannot list User B's tasks
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # List tasks with filtering and pagination
        tasks = await list_tasks(
            session=session,
            user_id=user_id,
            status=status_filter,
            offset=offset,
            limit=limit,
        )

        # Count total tasks matching the criteria
        total = await count_tasks(
            session=session,
            user_id=user_id,
            status=status_filter,
        )

        # Calculate pagination metadata
        has_next = (offset + limit) < total
        has_previous = offset > 0

        # Convert tasks to response schema
        task_responses = [TaskResponse.model_validate(task) for task in tasks]

        # Build paginated response
        paginated_response = PaginatedTaskResponse(
            items=task_responses,
            total=total,
            offset=offset,
            limit=limit,
            has_next=has_next,
            has_previous=has_previous,
        )

        return paginated_response

    except DatabaseError:
        # DatabaseError is handled by exception handler
        raise
    except ValueError as e:
        # Validation errors from query parameters
        raise ValidationError(str(e)) from e


@router.put(
    "/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Update an existing task. Supports partial updates - only provided fields will be updated. At least one field must be provided. Requires valid JWT token.",
    response_description="Updated task details",
    responses={
        200: {
            "description": "Task updated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Updated task title",
                        "description": "Updated description",
                        "status": "completed",
                        "created_at": "2026-01-12T00:00:00Z",
                        "updated_at": "2026-01-12T01:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        404: {
            "description": "Task not found or does not belong to user",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/not-found",
                        "title": "Task Not Found",
                        "status": 404,
                        "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid input data or no fields provided",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["body"],
                                "msg": "At least one field must be provided for update",
                                "type": "value_error",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
    },
)
async def update_task_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user updating the task",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    task_id: UUID = Path(
        ...,
        description="UUID of the task to update",
        example="123e4567-e89b-12d3-a456-426614174000",
    ),
    task_data: TaskUpdate = ...,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Update an existing task with ownership verification.

    Updates only the fields provided in the request body (partial update).
    At least one field must be provided. The updated_at timestamp is
    automatically updated. Requires valid JWT token.

    Args:
        user_id: UUID of the user updating the task (path parameter)
        task_id: UUID of the task to update (path parameter)
        task_data: Task update data (title, description, status)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        TaskResponse: Updated task details

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        TaskNotFoundError: If task doesn't exist or doesn't belong to user (404)
        ValidationError: If input validation fails (422)
        DatabaseError: If database operation fails (503)
    """
    # T052: Validate user_id match - User A cannot update User B's tasks
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # Update task via use case
        task = await update_task(session, user_id, task_id, task_data)

        # Convert to response schema
        return TaskResponse.model_validate(task)

    except TaskNotFoundError:
        # TaskNotFoundError is handled by exception handler
        raise
    except DatabaseError:
        # DatabaseError is handled by exception handler
        raise
    except ValueError as e:
        # Validation errors from Pydantic
        raise ValidationError(str(e)) from e


@router.delete(
    "/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task. This operation cannot be undone. Requires valid JWT token.",
    responses={
        204: {
            "description": "Task deleted successfully (no content)",
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        404: {
            "description": "Task not found or does not belong to user",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/not-found",
                        "title": "Task Not Found",
                        "status": 404,
                        "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid UUID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "task_id"],
                                "msg": "value is not a valid uuid",
                                "type": "type_error.uuid",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                    }
                }
            },
        },
    },
)
async def delete_task_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user deleting the task",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    task_id: UUID = Path(
        ...,
        description="UUID of the task to delete",
        example="123e4567-e89b-12d3-a456-426614174000",
    ),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Delete a task with ownership verification.

    Permanently deletes a task from the database. This operation cannot
    be undone. Returns 204 No Content on success. Requires valid JWT token.

    Args:
        user_id: UUID of the user deleting the task (path parameter)
        task_id: UUID of the task to delete (path parameter)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        None (204 No Content)

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        TaskNotFoundError: If task doesn't exist or doesn't belong to user (404)
        DatabaseError: If database operation fails (503)
    """
    # T052: Validate user_id match - User A cannot delete User B's tasks
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # Delete task via use case
        await delete_task(session, user_id, task_id)

        # Return 204 No Content (empty response body)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except TaskNotFoundError:
        # TaskNotFoundError is handled by exception handler
        raise
    except DatabaseError:
        # DatabaseError is handled by exception handler
        raise


@router.patch(
    "/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggle a task between pending and completed status. If pending, marks as completed. If completed, marks as pending. Requires valid JWT token.",
    response_description="Task with updated status",
    responses={
        200: {
            "description": "Task status toggled successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "status": "completed",
                        "created_at": "2026-01-12T00:00:00Z",
                        "updated_at": "2026-01-12T01:00:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized - invalid token or user_id mismatch",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Cannot access another user's resources",
                    }
                }
            },
        },
        404: {
            "description": "Task not found or does not belong to user",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/not-found",
                        "title": "Task Not Found",
                        "status": 404,
                        "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000/complete",
                    }
                }
            },
        },
        422: {
            "description": "Validation error - invalid UUID format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "loc": ["path", "task_id"],
                                "msg": "value is not a valid uuid",
                                "type": "type_error.uuid",
                            }
                        ]
                    }
                }
            },
        },
        503: {
            "description": "Service unavailable - database connection failed",
            "content": {
                "application/json": {
                    "example": {
                        "type": "https://api.example.com/errors/service-unavailable",
                        "title": "Service Unavailable",
                        "status": 503,
                        "detail": "Database connection unavailable. Please try again later.",
                        "instance": "/api/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000/complete",
                    }
                }
            },
        },
    },
)
async def toggle_task_completion_endpoint(
    user_id: UUID = Path(
        ...,
        description="UUID of the user toggling the task",
        example="550e8400-e29b-41d4-a716-446655440000",
    ),
    task_id: UUID = Path(
        ...,
        description="UUID of the task to toggle",
        example="123e4567-e89b-12d3-a456-426614174000",
    ),
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """Toggle task completion status with ownership verification.

    Toggles the task status between PENDING and COMPLETED. If the task
    is currently pending, it will be marked as completed. If completed,
    it will be marked as pending. The updated_at timestamp is automatically
    updated. Requires valid JWT token.

    Args:
        user_id: UUID of the user toggling the task (path parameter)
        task_id: UUID of the task to toggle (path parameter)
        current_user: Authenticated user claims from JWT token
        session: Database session (injected dependency)

    Returns:
        TaskResponse: Task with updated status

    Raises:
        HTTPException 401: If user_id doesn't match authenticated user
        TaskNotFoundError: If task doesn't exist or doesn't belong to user (404)
        DatabaseError: If database operation fails (503)
    """
    # T052: Validate user_id match - User A cannot toggle User B's tasks
    # Ensure both values are in string format for comparison
    token_user_id = str(current_user["user_id"])
    path_user_id = str(user_id)
    if token_user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cannot access another user's resources",
        )

    try:
        # Toggle task completion via use case
        task = await toggle_task_completion(session, user_id, task_id)

        # Convert to response schema
        return TaskResponse.model_validate(task)

    except TaskNotFoundError:
        # TaskNotFoundError is handled by exception handler
        raise
    except DatabaseError:
        # DatabaseError is handled by exception handler
        raise
