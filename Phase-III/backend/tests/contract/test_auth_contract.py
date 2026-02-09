"""Contract tests for authentication endpoints.

Tests API contract compliance for user registration and login including:
- POST /api/auth/register (201 Created)
- POST /api/auth/login (200 OK)
- Request/response schema validation
- Error response formats (400, 401, 409)
"""

from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_register_success():
    """Test successful user registration returns 201 with correct response format."""
    register_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    # Assert response body matches AuthResponse schema
    data = response.json()
    assert "token" in data, "Missing 'token' field"
    assert "user" in data, "Missing 'user' field"

    # Assert token is a non-empty string
    assert isinstance(data["token"], str), "Token must be a string"
    assert len(data["token"]) > 0, "Token must not be empty"

    # Assert user object has required fields
    user = data["user"]
    assert "id" in user, "Missing 'id' field in user"
    assert "email" in user, "Missing 'email' field in user"
    assert "status" in user, "Missing 'status' field in user"
    assert "created_at" in user, "Missing 'created_at' field in user"

    # Assert field values
    assert user["email"] == register_data["email"]
    assert user["status"] == "active"  # Default status

    # Assert id is valid UUID
    try:
        UUID(user["id"])
    except ValueError:
        pytest.fail(f"Invalid UUID format for id: {user['id']}")


@pytest.mark.asyncio
async def test_register_missing_email():
    """Test registration without email returns 422."""
    register_data = {
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_register_missing_password():
    """Test registration without password returns 422."""
    register_data = {
        "email": "test@example.com",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_register_invalid_email_format():
    """Test registration with invalid email format returns 400."""
    register_data = {
        "email": "not-an-email",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code (400 for invalid email format)
    assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_register_weak_password():
    """Test registration with password less than 8 characters returns 400."""
    register_data = {
        "email": "test@example.com",
        "password": "short",  # Less than 8 characters
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code (400 for weak password)
    assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_register_duplicate_email():
    """Test registration with existing email returns 409."""
    register_data = {
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # First registration should succeed
        response1 = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert response1.status_code == 201, "First registration should succeed"

        # Second registration with same email should fail
        response2 = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Assert status code
    assert response2.status_code == 409, f"Expected 409, got {response2.status_code}"

    # Assert error response format
    data = response2.json()
    assert "error" in data, "Missing 'error' field in error response"
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_login_success():
    """Test successful user login returns 200 with correct response format."""
    # First, register a user
    register_data = {
        "email": "loginuser@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"

        # Now login with same credentials
        login_data = {
            "email": "loginuser@example.com",
            "password": "SecurePass123!",
        }

        response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Assert status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Assert response body matches AuthResponse schema
    data = response.json()
    assert "token" in data, "Missing 'token' field"
    assert "user" in data, "Missing 'user' field"

    # Assert token is a non-empty string
    assert isinstance(data["token"], str), "Token must be a string"
    assert len(data["token"]) > 0, "Token must not be empty"

    # Assert user object has required fields
    user = data["user"]
    assert "id" in user, "Missing 'id' field in user"
    assert "email" in user, "Missing 'email' field in user"
    assert "status" in user, "Missing 'status' field in user"
    assert "created_at" in user, "Missing 'created_at' field in user"

    # Assert field values
    assert user["email"] == login_data["email"]
    assert user["status"] == "active"


@pytest.mark.asyncio
async def test_login_missing_email():
    """Test login without email returns 422."""
    login_data = {
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_login_missing_password():
    """Test login without password returns 422."""
    login_data = {
        "email": "test@example.com",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Assert status code
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials returns 401."""
    # First, register a user
    register_data = {
        "email": "validuser@example.com",
        "password": "CorrectPass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"

        # Try to login with wrong password
        login_data = {
            "email": "validuser@example.com",
            "password": "WrongPassword123!",
        }

        response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Assert status code
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "error" in data, "Missing 'error' field in error response"
    assert "detail" in data, "Missing 'detail' field in error response"


@pytest.mark.asyncio
async def test_login_nonexistent_user():
    """Test login with non-existent email returns 401."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "SomePassword123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Assert status code
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Assert error response format
    data = response.json()
    assert "error" in data, "Missing 'error' field in error response"
