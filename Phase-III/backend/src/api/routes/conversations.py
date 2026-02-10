"""Conversation management endpoint routes.

Provides endpoints for listing conversations and fetching message history
to support conversation persistence and resumption.

API Endpoints:
    GET /api/{user_id}/conversations - List all user conversations
    GET /api/{user_id}/conversations/{id}/messages - Get conversation messages

Query Parameters:
    limit (int): Maximum items to return (default: 100, max: 100)
    offset (int): Pagination offset (default: 0)

Response Format:
    Conversations: {"conversations": [{"id": 1, "preview": "...", ...}]}
    Messages: {"conversation_id": 1, "messages": [{"id": 1, "role": "user", ...}]}

Authentication:
    Requires JWT token in Authorization header: Bearer <token>

Performance:
    - Conversations sorted by updated_at DESC for recency
    - Message history limited to 100 messages per request
    - Efficient indexing on user_id and conversation_id
"""

import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.database import get_session
from src.dependencies import get_current_user_id
from src.domain.models import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["conversations"])


@router.get(
    "/{user_id}/conversations",
    status_code=status.HTTP_200_OK,
    summary="List user conversations",
    description="Get list of all conversations for a user, sorted by most recent activity"
)
async def list_conversations(
    user_id: UUID = Path(..., description="User ID from JWT token"),
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(100, ge=1, le=100, description="Maximum conversations to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """List all conversations for a user.

    Returns conversations sorted by most recent activity (updated_at DESC).
    Each conversation includes a preview (first user message) and message count.

    Args:
        user_id: User ID from path (must match JWT token)
        session: Database session
        current_user_id: User ID from JWT token
        limit: Maximum conversations to return (default: 100)
        offset: Pagination offset (default: 0)

    Returns:
        JSON with conversations array containing:
        - id: Conversation ID
        - created_at: Creation timestamp
        - updated_at: Last activity timestamp
        - preview: First user message content
        - message_count: Number of messages in conversation

    Raises:
        HTTPException 403: If user_id doesn't match JWT token
    """
    # Validate user_id matches JWT token
    if user_id != current_user_id:
        logger.warning(
            f"User {current_user_id} attempted to access conversations for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access conversations for different user"
        )

    try:
        # Fetch conversations for user, sorted by most recent
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        conversations = result.scalars().all()

        # Build conversation list with previews
        conversation_list = []
        for conv in conversations:
            # Get first user message as preview
            first_msg_result = await session.execute(
                select(Message)
                .where(
                    Message.conversation_id == conv.id,
                    Message.role == 'user'
                )
                .order_by(Message.created_at)
                .limit(1)
            )
            first_msg = first_msg_result.scalar_one_or_none()

            # Get message count
            msg_count_result = await session.execute(
                select(Message)
                .where(Message.conversation_id == conv.id)
            )
            message_count = len(msg_count_result.scalars().all())

            conversation_list.append({
                "id": conv.id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "preview": first_msg.content if first_msg else "New conversation",
                "message_count": message_count
            })

        logger.info(
            f"Listed {len(conversation_list)} conversations for user {user_id}"
        )

        return {"conversations": conversation_list}

    except Exception as e:
        logger.error(
            f"Failed to list conversations for user {user_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch conversations"
        )


@router.get(
    "/{user_id}/conversations/{conversation_id}/messages",
    status_code=status.HTTP_200_OK,
    summary="Get conversation messages",
    description="Fetch message history for a specific conversation"
)
async def get_conversation_messages(
    user_id: UUID = Path(..., description="User ID from JWT token"),
    conversation_id: int = Path(..., description="Conversation ID"),
    session: AsyncSession = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(100, ge=1, le=100, description="Maximum messages to return"),
    offset: int = Query(0, ge=0, description="Pagination offset")
):
    """Get message history for a conversation.

    Returns all messages in chronological order with tool call transparency.

    Args:
        user_id: User ID from path (must match JWT token)
        conversation_id: Conversation ID
        session: Database session
        current_user_id: User ID from JWT token
        limit: Maximum messages to return (default: 100)
        offset: Pagination offset (default: 0)

    Returns:
        JSON with:
        - conversation_id: Conversation ID
        - messages: Array of messages with id, role, content, tool_calls, created_at

    Raises:
        HTTPException 403: If user_id doesn't match JWT token
        HTTPException 403: If conversation doesn't belong to user
        HTTPException 404: If conversation not found
    """
    # Validate user_id matches JWT token
    if user_id != current_user_id:
        logger.warning(
            f"User {current_user_id} attempted to access messages for user {user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access messages for different user"
        )

    try:
        # Verify conversation exists and belongs to user
        conv_result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = conv_result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found"
            )

        if conversation.user_id != user_id:
            logger.warning(
                f"User {user_id} attempted to access conversation {conversation_id} "
                f"belonging to user {conversation.user_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Conversation does not belong to user"
            )

        # Fetch messages for conversation
        msg_result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )
        messages = msg_result.scalars().all()

        # Format messages for response
        message_list = []
        for msg in messages:
            # Parse tool_calls if it's a JSON string
            tool_calls = None
            if msg.tool_calls:
                if isinstance(msg.tool_calls, str):
                    tool_calls = json.loads(msg.tool_calls)
                else:
                    tool_calls = msg.tool_calls

            message_list.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "tool_calls": tool_calls,
                "created_at": msg.created_at.isoformat()
            })

        logger.info(
            f"Fetched {len(message_list)} messages for conversation {conversation_id}"
        )

        return {
            "conversation_id": conversation_id,
            "messages": message_list
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        logger.error(
            f"Failed to fetch messages for conversation {conversation_id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch messages"
        )
