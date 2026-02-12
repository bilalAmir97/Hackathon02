"""Unit tests for Message model.

Tests the Message model's validation, relationships, and business rules.
Following TDD approach - these tests should fail until the model is implemented.
"""

import pytest
import json
from datetime import datetime
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="conversation")
def conversation_fixture(session):
    """Create a test conversation."""
    from src.domain.models.conversation import Conversation
    
    conversation = Conversation(user_id="550e8400-e29b-41d4-a716-446655440000")
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def test_message_creation_user_role(session, conversation):
    """Test creating a user message."""
    from src.domain.models.message import Message
    
    # Arrange
    content = "Create a task to buy groceries"
    
    # Act
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    
    # Assert
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.role == "user"
    assert message.content == content
    assert message.tool_calls is None
    assert isinstance(message.created_at, datetime)


def test_message_creation_assistant_role(session, conversation):
    """Test creating an assistant message with tool calls."""
    from src.domain.models.message import Message
    
    # Arrange
    content = "I'll create that task for you."
    tool_calls = json.dumps([{
        "tool_name": "add_task",
        "input_parameters": {"title": "Buy groceries"},
        "output_result": {"id": 123, "status": "pending"},
        "execution_status": "success",
        "error_message": None,
        "timestamp": "2026-02-09T18:30:00Z"
    }])
    
    # Act
    message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    
    # Assert
    assert message.id is not None
    assert message.role == "assistant"
    assert message.content == content
    assert message.tool_calls is not None
    assert isinstance(json.loads(message.tool_calls), list)


def test_message_requires_conversation_id(session):
    """Test that message requires conversation_id."""
    from src.domain.models.message import Message
    
    # Act & Assert
    with pytest.raises(Exception):  # Should raise validation error
        message = Message(role="user", content="Test")
        session.add(message)
        session.commit()


def test_message_requires_role(session, conversation):
    """Test that message requires role."""
    from src.domain.models.message import Message
    
    # Act & Assert
    with pytest.raises(Exception):  # Should raise validation error
        message = Message(conversation_id=conversation.id, content="Test")
        session.add(message)
        session.commit()


def test_message_requires_content(session, conversation):
    """Test that message requires content."""
    from src.domain.models.message import Message
    
    # Act & Assert
    with pytest.raises(Exception):  # Should raise validation error
        message = Message(conversation_id=conversation.id, role="user")
        session.add(message)
        session.commit()


def test_message_role_validation(session, conversation):
    """Test that role must be 'user' or 'assistant'."""
    from src.domain.models.message import Message
    
    # Act & Assert
    with pytest.raises(Exception):  # Should raise validation error
        message = Message(
            conversation_id=conversation.id,
            role="invalid_role",
            content="Test"
        )
        session.add(message)
        session.commit()


def test_message_timestamp_auto_set(session, conversation):
    """Test that created_at is automatically set."""
    from src.domain.models.message import Message
    
    # Arrange
    before_creation = datetime.utcnow()
    
    # Act
    message = Message(
        conversation_id=conversation.id,
        role="user",
        content="Test message"
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    after_creation = datetime.utcnow()
    
    # Assert
    assert before_creation <= message.created_at <= after_creation


def test_message_table_name():
    """Test that message uses correct table name."""
    from src.domain.models.message import Message
    
    assert Message.__tablename__ == "messages"


def test_message_has_conversation_relationship():
    """Test that message has relationship to conversation."""
    from src.domain.models.message import Message
    
    # Verify the relationship is defined
    assert hasattr(Message, 'conversation')


def test_message_conversation_id_indexed():
    """Test that conversation_id has an index for efficient queries."""
    from src.domain.models.message import Message
    
    # This test verifies the index exists in the model definition
    assert hasattr(Message, 'conversation_id')
    field = Message.__fields__['conversation_id']
    assert field.field_info.extra.get('index') is True
