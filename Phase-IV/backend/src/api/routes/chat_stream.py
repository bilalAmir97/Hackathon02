"""Streaming chat endpoint routes.

Provides streaming responses for the conversational AI interface with
token-by-token rendering and real-time tool call transparency.

API Endpoints:
    POST /api/{user_id}/chat/stream - Stream chat response with NDJSON format

Response Format (NDJSON):
    {"type": "token", "content": "word"}
    {"type": "tool_call", "data": {...}}
    {"type": "done", "conversation_id": 1, "message_id": 123}
    {"type": "error", "message": "...", "code": "..."}

Authentication:
    Requires JWT token in Authorization header: Bearer <token>

Rate Limiting:
    TODO: Implement rate limiting to prevent abuse (max 60 requests/minute per user)
"""

import json
import logging
from typing import AsyncGenerator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat_schemas import ChatRequest
from src.database import get_session
from src.dependencies import get_current_user_id
from src.use_cases.agent_orchestration import AgentOrchestration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


async def generate_stream(
    orchestration: AgentOrchestration,
    session: AsyncSession,
    user_id: UUID,
    message: str,
    conversation_id: int | None
) -> AsyncGenerator[str, None]:
    """Generate streaming response chunks in NDJSON format.

    Yields:
        NDJSON chunks with types: token, tool_call, done, error
    """
    try:
        # Stream response from agent orchestration
        async for chunk in orchestration.stream_message(
            session=session,
            user_id=user_id,
            message=message,
            conversation_id=conversation_id
        ):
            # Yield chunk as NDJSON (newline-delimited JSON)
            yield json.dumps(chunk) + "\n"

    except PermissionError as e:
        # Yield error chunk for permission issues
        error_chunk = {
            "type": "error",
            "message": str(e),
            "code": "PERMISSION_DENIED"
        }
        yield json.dumps(error_chunk) + "\n"

    except Exception as e:
        # Yield error chunk for unexpected errors
        logger.error(f"Streaming error for user {user_id}: {str(e)}", exc_info=True)
        error_chunk = {
            "type": "error",
            "message": "Failed to process message",
            "code": "INTERNAL_ERROR"
        }
        yield json.dumps(error_chunk) + "\n"


@router.post(
    "/{user_id}/chat/stream",
    status_code=status.HTTP_200_OK,
    summary="Stream chat with AI agent",
    description="Send a message and receive streaming response with token-by-token rendering"
)
async def chat_stream(
    user_id: UUID = Path(..., description="User ID from JWT token"),
    request: ChatRequest = ...,
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
) -> StreamingResponse:
    """Streaming chat endpoint for conversational AI task management.

    This endpoint provides token-by-token streaming responses, allowing the
    frontend to display the AI's response as it's being generated. Tool calls
    are also streamed in real-time for transparency.

    Args:
        user_id: User ID from path (must match JWT token)
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user_id: User ID from JWT token

    Returns:
        StreamingResponse with NDJSON chunks (application/x-ndjson)

    Raises:
        HTTPException 403: If user_id doesn't match JWT token
    """
    # Validate user_id matches JWT token
    if user_id != current_user_id:
        logger.warning(
            f"User {current_user_id} attempted to access chat for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access chat for different user"
        )

    logger.info(
        f"Starting streaming chat for user {user_id}, "
        f"conversation {request.conversation_id}"
    )

    # Create orchestration instance
    orchestration = AgentOrchestration()

    # Return streaming response
    return StreamingResponse(
        generate_stream(
            orchestration=orchestration,
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        ),
        media_type="application/x-ndjson",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff",
            "Connection": "keep-alive"
        }
    )
