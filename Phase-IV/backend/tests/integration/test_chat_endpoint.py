"""Integration tests for chat endpoint.

Tests the complete flow from HTTP request through agent orchestration to database.
Following TDD approach - these tests should fail until the endpoint is implemented.
"""

import pytest
from httpx import ASGITransport, AsyncClient
import json


@pytest.fixture
async def async_client():
    """Create async test client."""
    from src.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_chat_endpoint_task_creation_intent(async_client, test_user, test_token, test_db_session_with_user):
    """Test that chat endpoint detects task creation intent and calls add_task tool.

    This is the core US1 test: user says "Create a task to buy groceries"
    and the agent should call add_task tool.
    """
    # Arrange
    message = "Create a task to buy groceries"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    # Verify tool_calls array contains add_task
    assert "tool_calls" in data
    assert len(data["tool_calls"]) > 0

    # Find add_task call
    add_task_call = next(
        (call for call in data["tool_calls"] if call["tool_name"] == "add_task"),
        None
    )
    assert add_task_call is not None, "Should call add_task tool"
    assert "buy groceries" in add_task_call["input_parameters"]["title"].lower()


@pytest.mark.asyncio
async def test_chat_endpoint_persists_conversation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that conversation is persisted to database."""
    # Arrange
    message = "Hello"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # Verify conversation exists in database
    from src.database import AsyncSessionLocal
    from src.domain.models import Conversation
    from sqlmodel import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        assert conversation is not None
        assert conversation.user_id == test_user.id


@pytest.mark.asyncio
async def test_chat_endpoint_persists_messages(async_client, test_user, test_token, test_db_session_with_user):
    """Test that user and assistant messages are persisted."""
    # Arrange
    message = "Create a task"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    conversation_id = data["conversation_id"]

    # Verify messages exist in database
    from src.database import AsyncSessionLocal
    from src.domain.models import Message
    from sqlmodel import select

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        messages = result.scalars().all()

        # Should have at least user message and assistant response
        assert len(messages) >= 2

        # Verify user message
        user_msg = next((m for m in messages if m.role == "user"), None)
        assert user_msg is not None
        assert user_msg.content == message

        # Verify assistant message
        assistant_msg = next((m for m in messages if m.role == "assistant"), None)
        assert assistant_msg is not None


@pytest.mark.asyncio
async def test_chat_endpoint_resumes_conversation(async_client, test_user, test_token, test_db_session_with_user):
    """Test that conversation can be resumed with conversation_id."""
    # Arrange - Create initial conversation
    response1 = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Act - Resume conversation
    response2 = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Create a task",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response2.status_code == 200
    data = response2.json()
    assert data["conversation_id"] == conversation_id

    # Verify message count increased
    from src.database import AsyncSessionLocal
    from src.domain.models import Message
    from sqlmodel import select, func

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
        )
        message_count = result.scalar()
        assert message_count >= 4  # 2 from first exchange + 2 from second


@pytest.mark.asyncio
async def test_chat_endpoint_enforces_user_ownership(async_client, test_user, test_token, test_db_session_with_user):
    """Test that users cannot access other users' conversations."""
    # Arrange - Create conversation for test_user
    response1 = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    conversation_id = response1.json()["conversation_id"]

    # Create different user in database
    from src.domain.models import User, UserStatus
    from src.auth.password import hash_password
    from src.auth.token import create_access_token
    from src.database import AsyncSessionLocal
    from uuid import uuid4

    different_user_id = uuid4()
    different_token = create_access_token(user_id=str(different_user_id), email="other@example.com")

    async with AsyncSessionLocal() as session:
        different_user = User(
            id=different_user_id,
            email="other@example.com",
            password_hash=hash_password("password123"),
            status=UserStatus.ACTIVE
        )
        session.add(different_user)
        await session.commit()

    # Act - Try to access conversation with different user
    response2 = await async_client.post(
        f"/api/{different_user_id}/chat",
        json={
            "message": "Hello",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {different_token}"}
    )

    # Assert
    assert response2.status_code == 403, "Should reject access to other user's conversation"


@pytest.mark.asyncio
async def test_chat_endpoint_tool_call_transparency(async_client, test_user, test_token, test_db_session_with_user):
    """Test that tool calls are returned with full transparency."""
    # Arrange
    message = "Create a task to test tool transparency"

    # Act
    response = await async_client.post(
        f"/api/{test_user.id}/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {test_token}"}
    )

    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Verify tool_calls structure
    assert "tool_calls" in data
    if len(data["tool_calls"]) > 0:
        tool_call = data["tool_calls"][0]
        
        # Verify required fields
        assert "tool_name" in tool_call
        assert "input_parameters" in tool_call
        assert "output_result" in tool_call
        assert "execution_status" in tool_call
        assert "timestamp" in tool_call
