"""
RFC 7807 Problem Details exception handler for FastAPI.

Provides consistent error responses following RFC 7807 standard.
"""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("todo_api")


# Custom Exception Classes
class TaskNotFoundError(Exception):
    """Raised when a task is not found or doesn't belong to the user."""

    def __init__(self, task_id: str = None, user_id: str = None):
        self.task_id = task_id
        self.user_id = user_id
        message = "Task not found or does not belong to this user"
        if task_id:
            message = f"Task with ID {task_id} does not exist or does not belong to this user"
        super().__init__(message)


class ValidationError(Exception):
    """Raised when request validation fails."""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class DatabaseError(Exception):
    """Raised when database operations fail."""

    def __init__(self, detail: str = "Database operation failed"):
        self.detail = detail
        super().__init__(detail)


# RFC 7807 Problem Details Response Builder
def create_problem_detail(
    request: Request,
    error_type: str,
    title: str,
    status_code: int,
    detail: str,
) -> dict[str, Any]:
    """
    Create RFC 7807 Problem Details response.

    Args:
        request: FastAPI request object
        error_type: Error type identifier (e.g., "not-found")
        title: Short, human-readable summary
        status_code: HTTP status code
        detail: Specific explanation for this occurrence

    Returns:
        Dictionary with RFC 7807 fields
    """
    return {
        "type": f"https://api.example.com/errors/{error_type}",
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": str(request.url.path),
    }


# Exception Handlers
async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
    """
    Handle TaskNotFoundError exceptions.

    Returns 404 Not Found with RFC 7807 format.
    """
    problem_detail = create_problem_detail(
        request=request,
        error_type="not-found",
        title="Task Not Found",
        status_code=status.HTTP_404_NOT_FOUND,
        detail=str(exc),
    )

    # Log the error
    logger.warning(
        "Task not found",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "task_id": exc.task_id,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=problem_detail,
    )


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle ValidationError exceptions.

    Returns 422 Unprocessable Entity with RFC 7807 format.
    """
    problem_detail = create_problem_detail(
        request=request,
        error_type="validation-error",
        title="Validation Error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=exc.detail,
    )

    # Log the error
    logger.warning(
        "Validation error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "detail": exc.detail,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=problem_detail,
    )


async def database_error_handler(request: Request, exc: DatabaseError) -> JSONResponse:
    """
    Handle DatabaseError exceptions.

    Returns 503 Service Unavailable with RFC 7807 format.
    """
    problem_detail = create_problem_detail(
        request=request,
        error_type="service-unavailable",
        title="Service Unavailable",
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Database connection unavailable. Please try again later.",
    )

    # Log the error with full details (server-side only)
    logger.error(
        "Database error",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "error_detail": exc.detail,
            "path": request.url.path,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=problem_detail,
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle HTTPException for authentication errors.

    Returns consistent error format for 401 Unauthorized responses.
    """
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):
        # For 401 Unauthorized, return simple error format expected by tests
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.detail},
                headers=exc.headers,
            )
        # For other HTTP exceptions, return detail format
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers if hasattr(exc, "headers") else None,
        )

    # Not an HTTPException, fall through to generic handler
    return await generic_exception_handler(request, exc)


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all unhandled exceptions.

    Returns 500 Internal Server Error with RFC 7807 format.
    Does not expose internal error details to clients.
    """
    problem_detail = create_problem_detail(
        request=request,
        error_type="internal-error",
        title="Internal Server Error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred while processing your request",
    )

    # Log the full error details (server-side only)
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": getattr(request.state, "request_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
        },
        exc_info=True,  # Include stack trace in logs
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=problem_detail,
    )
