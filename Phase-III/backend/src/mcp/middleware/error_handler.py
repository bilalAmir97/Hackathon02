"""MCP error handling middleware.

This module provides standardized error codes, error response models, and
error formatting utilities for MCP tool operations. All errors follow the
standard format: {"error": {"code": "ERROR_CODE", "message": "...", "details": {}}}
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MCPErrorCode(str, Enum):
    """Machine-readable error codes for MCP tool operations.

    These codes enable AI agents to handle errors programmatically and
    implement appropriate retry or fallback strategies.

    Attributes:
        TASK_NOT_FOUND: Task with specified ID does not exist or doesn't belong to user
        INVALID_INPUT: Input validation failed (details contain field errors)
        UNAUTHORIZED: Missing or invalid authentication token
        FORBIDDEN: User attempting to access another user's resource
        CONFLICT: Optimistic concurrency conflict (version mismatch)
        DATABASE_ERROR: Temporary database unavailability
        INTERNAL_ERROR: Unexpected server error
    """

    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    INVALID_INPUT = "INVALID_INPUT"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    CONFLICT = "CONFLICT"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class MCPError(BaseModel):
    """Error details following MCP standard format.

    Attributes:
        code: Machine-readable error code (uppercase snake_case)
        message: Human-readable error description
        details: Optional additional context (never exposes internal details)
    """

    code: MCPErrorCode = Field(description="Machine-readable error code")
    message: str = Field(description="Human-readable error description")
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional context for debugging"
    )


class MCPErrorResponse(BaseModel):
    """Standard MCP error response wrapper.

    All MCP tool errors are wrapped in this structure to ensure
    consistent error handling across all tools.

    Attributes:
        error: Error details with code, message, and optional details
    """

    error: MCPError = Field(description="Error details")


def format_mcp_error(
    code: MCPErrorCode,
    message: str,
    details: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Format error in standard MCP error response structure.

    This function creates a standardized error response that can be
    returned from MCP tools. The response follows the format:
    {"error": {"code": "ERROR_CODE", "message": "...", "details": {}}}

    Args:
        code: Machine-readable error code
        message: Human-readable error description
        details: Optional additional context (default: empty dict)

    Returns:
        dict: Formatted error response ready to return from MCP tool

    Example:
        >>> error = format_mcp_error(
        ...     MCPErrorCode.TASK_NOT_FOUND,
        ...     "Task with ID 123 not found",
        ...     {}
        ... )
        >>> error
        {'error': {'code': 'TASK_NOT_FOUND', 'message': '...', 'details': {}}}
    """
    error_response = MCPErrorResponse(
        error=MCPError(
            code=code,
            message=message,
            details=details or {}
        )
    )
    return error_response.model_dump()
