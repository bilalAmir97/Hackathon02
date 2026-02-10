"""Chat endpoint routes.

Provides the conversational AI interface for task management through
natural language interactions with tool call transparency.
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.chat_schemas import ChatRequest, ChatResponse
from src.database import get_session
from src.dependencies import get_current_user_id
from src.use_cases.agent_orchestration import AgentOrchestration

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Chat with AI agent",
    description="Send a message to the AI agent for conversational task management"
)
async def chat(
    user_id: UUID = Path(..., description="User ID from JWT token"),
    request: ChatRequest = ...,
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
) -> ChatResponse:
    """Chat endpoint for conversational AI task management.
    
    This endpoint provides a stateless conversational interface where users
    can manage their tasks through natural language. The agent uses MCP tools
    to perform operations and returns full tool call transparency.
    
    Args:
        user_id: User ID from path (must match JWT token)
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user_id: User ID from JWT token
        
    Returns:
        ChatResponse with conversation_id, response, and tool_calls
        
    Raises:
        HTTPException 403: If user_id doesn't match JWT token
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 500: If agent orchestration fails
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

    try:
        # Process message through agent orchestration
        orchestration = AgentOrchestration()
        result = await orchestration.process_message(
            session=session,
            user_id=user_id,
            message=request.message,
            conversation_id=request.conversation_id
        )

        logger.info(
            f"Chat processed for user {user_id}, "
            f"conversation {result['conversation_id']}, "
            f"tool_calls: {len(result['tool_calls'])}"
        )

        return ChatResponse(**result)

    except PermissionError as e:
        logger.warning(f"Permission denied for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Chat endpoint error for user {user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )
