"""Contract tests for chat endpoint.

Tests that the chat endpoint complies with the OpenAPI specification.
Following TDD approach - these tests should fail until the endpoint is implemented.
"""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


@pytest.fixture
def client():
    """Create test client."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers with valid JWT."""
    from src.auth.token import create_access_token
    user_id = str(uuid4())
    token = create_access_token(user_id=user_id, email="test@example.com")
    return {
        "Authorization": f"Bearer {token}",
        "user_id": user_id
    }


def test_chat_endpoint_exists(client, auth_headers):
    """Test that POST /api/{user_id}/chat endpoint exists."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    assert response.status_code != 404, "Chat endpoint should exist"


def test_chat_endpoint_requires_authentication(client):
    """Test that chat endpoint requires JWT authentication."""
    user_id = str(uuid4())
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"}
    )
    
    # Assert
    assert response.status_code == 401, "Should require authentication"


def test_chat_endpoint_accepts_message(client, auth_headers):
    """Test that chat endpoint accepts message in request body."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Create a task to buy groceries"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    assert response.status_code in [200, 201], f"Should accept valid message, got {response.status_code}"


def test_chat_endpoint_returns_conversation_id(client, auth_headers):
    """Test that response includes conversation_id."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    if response.status_code == 200:
        data = response.json()
        assert "conversation_id" in data, "Response should include conversation_id"
        assert isinstance(data["conversation_id"], int)


def test_chat_endpoint_returns_response_message(client, auth_headers):
    """Test that response includes agent's response message."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    if response.status_code == 200:
        data = response.json()
        assert "response" in data, "Response should include agent response"
        assert isinstance(data["response"], str)


def test_chat_endpoint_returns_tool_calls_array(client, auth_headers):
    """Test that response includes tool_calls array."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Create a task to buy groceries"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    if response.status_code == 200:
        data = response.json()
        assert "tool_calls" in data, "Response should include tool_calls"
        assert isinstance(data["tool_calls"], list)


def test_chat_endpoint_accepts_optional_conversation_id(client, auth_headers):
    """Test that endpoint accepts optional conversation_id to resume conversation."""
    user_id = auth_headers["user_id"]
    
    # Act - First message
    response1 = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    if response1.status_code == 200:
        conversation_id = response1.json()["conversation_id"]
        
        # Act - Resume conversation
        response2 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Create a task",
                "conversation_id": conversation_id
            },
            headers={"Authorization": auth_headers["Authorization"]}
        )
        
        # Assert
        assert response2.status_code == 200
        assert response2.json()["conversation_id"] == conversation_id


def test_chat_endpoint_validates_user_id_match(client, auth_headers):
    """Test that endpoint validates user_id in path matches JWT token."""
    different_user_id = str(uuid4())
    
    # Act
    response = client.post(
        f"/api/{different_user_id}/chat",
        json={"message": "Hello"},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    assert response.status_code == 403, "Should reject mismatched user_id"


def test_chat_endpoint_requires_message_field(client, auth_headers):
    """Test that endpoint requires message field in request."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    assert response.status_code == 422, "Should require message field"


def test_chat_endpoint_rejects_empty_message(client, auth_headers):
    """Test that endpoint rejects empty message."""
    user_id = auth_headers["user_id"]
    
    # Act
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": ""},
        headers={"Authorization": auth_headers["Authorization"]}
    )
    
    # Assert
    assert response.status_code == 422, "Should reject empty message"
