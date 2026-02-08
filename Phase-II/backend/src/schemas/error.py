"""Pydantic schemas for error responses.

Defines RFC 7807 Problem Details format for consistent error responses.
"""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """RFC 7807 Problem Details error response schema.

    Provides a standardized format for API error responses following
    RFC 7807 specification.

    Attributes:
        type: URI reference identifying the problem type
        title: Short, human-readable summary of the problem
        status: HTTP status code
        detail: Human-readable explanation specific to this occurrence
        instance: URI reference identifying the specific occurrence
    """

    type: str = Field(
        ...,
        description="URI reference identifying the problem type",
        examples=["https://api.example.com/errors/not-found"],
    )

    title: str = Field(
        ...,
        description="Short, human-readable summary of the problem",
        examples=["Task Not Found"],
    )

    status: int = Field(
        ...,
        description="HTTP status code",
        examples=[404],
        ge=100,
        le=599,
    )

    detail: str = Field(
        ...,
        description="Human-readable explanation specific to this occurrence",
        examples=[
            "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user"
        ],
    )

    instance: str = Field(
        ...,
        description="URI reference identifying the specific occurrence",
        examples=[
            "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000"
        ],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "type": "https://api.example.com/errors/not-found",
                    "title": "Task Not Found",
                    "status": 404,
                    "detail": "Task with ID 123e4567-e89b-12d3-a456-426614174000 does not exist or does not belong to this user",
                    "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks/123e4567-e89b-12d3-a456-426614174000",
                },
                {
                    "type": "https://api.example.com/errors/validation-error",
                    "title": "Validation Error",
                    "status": 422,
                    "detail": "Title cannot be empty or only whitespace",
                    "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks",
                },
                {
                    "type": "https://api.example.com/errors/service-unavailable",
                    "title": "Service Unavailable",
                    "status": 503,
                    "detail": "Database connection unavailable. Please try again later.",
                    "instance": "/users/550e8400-e29b-41d4-a716-446655440000/tasks",
                },
            ]
        }
    }
