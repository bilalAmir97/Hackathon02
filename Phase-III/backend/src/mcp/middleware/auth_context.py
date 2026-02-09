"""MCP authentication context extraction.

This module provides utilities for extracting and verifying user_id from
JWT tokens in MCP request headers. Integrates with existing Phase-III
authentication infrastructure.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.token import decode_token
from src.config import settings
from src.database import AsyncSessionLocal
from src.mcp.middleware.error_handler import MCPErrorCode, format_mcp_error


def extract_user_id(headers: dict[str, str]) -> UUID:
    """Extract and verify user_id from JWT token in Authorization header.

    This function extracts the JWT token from the Authorization header,
    verifies its signature and claims, and returns the authenticated user_id.
    Reuses existing Phase-III JWT verification logic for consistency.

    Args:
        headers: HTTP headers dict from MCP request context

    Returns:
        UUID: Authenticated user identifier

    Raises:
        Exception: If authentication fails (wrapped in format_mcp_error)

    Example:
        >>> headers = {"authorization": "Bearer eyJhbGc..."}
        >>> user_id = extract_user_id(headers)
        >>> print(user_id)
        UUID('550e8400-e29b-41d4-a716-446655440000')
    """
    auth_header = headers.get("authorization")

    if not auth_header:
        raise Exception(
            format_mcp_error(
                MCPErrorCode.UNAUTHORIZED,
                "Missing authentication credentials",
                {}
            )
        )

    if not auth_header.startswith("Bearer "):
        raise Exception(
            format_mcp_error(
                MCPErrorCode.UNAUTHORIZED,
                "Invalid Authorization header format",
                {}
            )
        )

    token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        # Reuse existing JWT verification logic
        payload = decode_token(token)
        user_id = UUID(payload["user_id"])
        return user_id
    except Exception as e:
        raise Exception(
            format_mcp_error(
                MCPErrorCode.UNAUTHORIZED,
                f"Invalid token: {str(e)}",
                {}
            )
        )


@asynccontextmanager
async def get_mcp_session() -> AsyncGenerator[AsyncSession, None]:
    """Create request-scoped database session for MCP tools.

    This context manager ensures stateless execution by creating a new
    database session for each tool invocation and automatically cleaning
    up resources. Sessions are committed on success and rolled back on error.

    Yields:
        AsyncSession: Database session for tool execution

    Example:
        >>> async with get_mcp_session() as session:
        ...     task = await create_task(session, user_id, title, description)
        ...     # Session automatically committed and closed
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
