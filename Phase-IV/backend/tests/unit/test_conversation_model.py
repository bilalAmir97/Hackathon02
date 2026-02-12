"""Unit tests for Conversation model.

Tests the Conversation model's validation, relationships, and business rules.
Following TDD approach - these tests should fail until the model is implemented.
"""

import pytest
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


def test_conversation_creation(session):
    """Test creating a conversation with required fields."""
    from src.domain.models.conversation import Conversation
    
    # Arrange
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    
    # Act
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    
    # Assert
    assert conversation.id is not None
    assert conversation.user_id == user_id
    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)


def test_conversation_requires_user_id(session):
    """Test that conversation requires user_id."""
    from src.domain.models.conversation import Conversation
    
    # Act & Assert
    with pytest.raises(Exception):  # Should raise validation error
        conversation = Conversation()
        session.add(conversation)
        session.commit()


def test_conversation_timestamps_auto_set(session):
    """Test that timestamps are automatically set on creation."""
    from src.domain.models.conversation import Conversation
    
    # Arrange
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    before_creation = datetime.utcnow()
    
    # Act
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    after_creation = datetime.utcnow()
    
    # Assert
    assert before_creation <= conversation.created_at <= after_creation
    assert before_creation <= conversation.updated_at <= after_creation
    assert conversation.created_at == conversation.updated_at


def test_conversation_user_id_indexed(session):
    """Test that user_id has an index for efficient queries."""
    from src.domain.models.conversation import Conversation
    
    # This test verifies the index exists in the model definition
    # The actual index creation is tested in migration tests
    assert hasattr(Conversation, 'user_id')
    field = Conversation.__fields__['user_id']
    assert field.field_info.extra.get('index') is True


def test_conversation_table_name():
    """Test that conversation uses correct table name."""
    from src.domain.models.conversation import Conversation
    
    assert Conversation.__tablename__ == "conversations"


def test_conversation_has_messages_relationship():
    """Test that conversation has relationship to messages."""
    from src.domain.models.conversation import Conversation
    
    # Verify the relationship is defined
    assert hasattr(Conversation, 'messages')
