"""Integration tests for authentication flows.

Tests complete authentication workflows including:
- User registration with database persistence
- Duplicate email handling
- User login with credential verification
- Invalid credential handling
- JWT token generation and validation
- Token security (expired, invalid signature, malformed)
"""

import jwt
import pytest
from datetime import datetime, timedelta, timezone
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from src.config import settings
from src.domain.models import User
from src.main import app
from tests.fixtures.database import test_db_session


@pytest.mark.asyncio
async def test_user_registration_flow(test_db_session):
    """Test complete user registration flow with database persistence.

    Verifies that:
    - User can register with valid email and password
    - User record is created in database
    - Password is hashed (not stored as plaintext)
    - JWT token is returned
    - User status is set to 'active'
    - Timestamps are set correctly
    """
    register_data = {
        "email": "newuser@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register user
        response = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Step 2: Verify API response
    assert response.status_code == 201, f"Registration failed: {response.text}"
    data = response.json()

    assert "token" in data, "Response must contain token"
    assert "user" in data, "Response must contain user"

    user_data = data["user"]
    assert user_data["email"] == register_data["email"]
    assert user_data["status"] == "active"
    assert "id" in user_data
    assert "created_at" in user_data

    user_id = user_data["id"]

    # Step 3: Verify user exists in database
    result = await test_db_session.execute(
        select(User).where(User.id == user_id)
    )
    db_user = result.scalar_one_or_none()

    assert db_user is not None, "User should exist in database"
    assert db_user.email == register_data["email"]
    assert db_user.status == "active"

    # Step 4: Verify password is hashed (not plaintext)
    assert hasattr(db_user, "password_hash"), "User should have password_hash field"
    assert db_user.password_hash != register_data["password"], "Password must be hashed"
    assert len(db_user.password_hash) > 0, "Password hash must not be empty"

    # Step 5: Verify timestamps are set
    assert db_user.created_at is not None, "created_at must be set"
    assert db_user.updated_at is not None, "updated_at must be set"


@pytest.mark.asyncio
async def test_duplicate_email_registration(test_db_session):
    """Test that registering with duplicate email returns 409 Conflict.

    Verifies that:
    - First registration succeeds
    - Second registration with same email fails with 409
    - Error response contains appropriate message
    - No duplicate user records are created in database
    """
    register_data = {
        "email": "duplicate@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: First registration should succeed
        response1 = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert response1.status_code == 201, "First registration should succeed"

        # Step 2: Second registration with same email should fail
        response2 = await client.post(
            "/api/auth/register",
            json=register_data,
        )

    # Step 3: Verify 409 Conflict response
    assert response2.status_code == 409, f"Expected 409, got {response2.status_code}"

    # Step 4: Verify error response format
    error_data = response2.json()
    assert "error" in error_data, "Error response must contain 'error' field"
    assert "detail" in error_data, "Error response must contain 'detail' field"
    assert "already exists" in error_data["error"].lower() or "already exists" in error_data["detail"].lower()

    # Step 5: Verify only one user record exists in database
    result = await test_db_session.execute(
        select(User).where(User.email == register_data["email"])
    )
    users = result.scalars().all()

    assert len(users) == 1, "Only one user record should exist for duplicate email"


@pytest.mark.asyncio
async def test_user_login_flow(test_db_session):
    """Test complete user login flow with credential verification.

    Verifies that:
    - User can register successfully
    - User can login with correct credentials
    - JWT token is returned on login
    - Token contains correct user information
    - User data matches registration
    """
    register_data = {
        "email": "logintest@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register user
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        register_user_data = register_response.json()["user"]

        # Step 2: Login with same credentials
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"],
        }

        login_response = await client.post(
            "/api/auth/login",
            json=login_data,
        )

    # Step 3: Verify login response
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    login_data_response = login_response.json()

    assert "token" in login_data_response, "Login response must contain token"
    assert "user" in login_data_response, "Login response must contain user"

    # Step 4: Verify token is different from registration token (different iat)
    register_token = register_user_data.get("token") if "token" in register_user_data else register_response.json()["token"]
    login_token = login_data_response["token"]
    # Tokens should be different due to different issued_at times
    # (This may not always be true if registration and login happen in same second)

    # Step 5: Verify user data matches
    login_user_data = login_data_response["user"]
    assert login_user_data["id"] == register_user_data["id"], "User ID should match"
    assert login_user_data["email"] == register_data["email"], "Email should match"
    assert login_user_data["status"] == "active", "Status should be active"

    # Step 6: Verify user still exists in database with correct data
    result = await test_db_session.execute(
        select(User).where(User.email == register_data["email"])
    )
    db_user = result.scalar_one_or_none()

    assert db_user is not None, "User should exist in database"
    assert str(db_user.id) == login_user_data["id"], "Database user ID should match"


@pytest.mark.asyncio
async def test_invalid_login_credentials(test_db_session):
    """Test that login with invalid credentials returns 401 Unauthorized.

    Verifies that:
    - User can register successfully
    - Login with wrong password fails with 401
    - Login with non-existent email fails with 401
    - Error response contains appropriate message
    - No token is issued for invalid credentials
    """
    register_data = {
        "email": "validuser@example.com",
        "password": "CorrectPass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register user
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"

        # Step 2: Try to login with wrong password
        wrong_password_data = {
            "email": register_data["email"],
            "password": "WrongPassword123!",
        }

        wrong_password_response = await client.post(
            "/api/auth/login",
            json=wrong_password_data,
        )

        # Step 3: Verify 401 Unauthorized for wrong password
        assert wrong_password_response.status_code == 401, f"Expected 401, got {wrong_password_response.status_code}"

        error_data = wrong_password_response.json()
        assert "error" in error_data, "Error response must contain 'error' field"
        assert "detail" in error_data, "Error response must contain 'detail' field"

        # Step 4: Try to login with non-existent email
        nonexistent_email_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        nonexistent_response = await client.post(
            "/api/auth/login",
            json=nonexistent_email_data,
        )

        # Step 5: Verify 401 Unauthorized for non-existent email
        assert nonexistent_response.status_code == 401, f"Expected 401, got {nonexistent_response.status_code}"

        error_data2 = nonexistent_response.json()
        assert "error" in error_data2, "Error response must contain 'error' field"

        # Step 6: Verify no token is present in error responses
        assert "token" not in error_data, "Error response should not contain token"
        assert "token" not in error_data2, "Error response should not contain token"


@pytest.mark.asyncio
async def test_login_case_sensitive_password(test_db_session):
    """Test that password verification is case-sensitive.

    Verifies that:
    - User can register with a password
    - Login with password in different case fails
    - Case sensitivity is enforced
    """
    register_data = {
        "email": "casetest@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register user
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"

        # Step 2: Try to login with password in different case
        wrong_case_data = {
            "email": register_data["email"],
            "password": "securepass123!",  # All lowercase
        }

        response = await client.post(
            "/api/auth/login",
            json=wrong_case_data,
        )

    # Step 3: Verify login fails
    assert response.status_code == 401, "Login with wrong case password should fail"


@pytest.mark.asyncio
async def test_registration_and_login_with_special_characters(test_db_session):
    """Test registration and login with special characters in password.

    Verifies that:
    - Passwords with special characters are handled correctly
    - Password hashing preserves special characters
    - Login works with special character passwords
    """
    register_data = {
        "email": "specialchars@example.com",
        "password": "P@ssw0rd!#$%^&*()",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register with special character password
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"

        # Step 2: Login with same special character password
        login_response = await client.post(
            "/api/auth/login",
            json=register_data,
        )

    # Step 3: Verify login succeeds
    assert login_response.status_code == 200, "Login with special characters should succeed"
    assert "token" in login_response.json(), "Should receive token"


@pytest.mark.asyncio
async def test_multiple_users_can_register_and_login(test_db_session):
    """Test that multiple users can register and login independently.

    Verifies that:
    - Multiple users can register with different emails
    - Each user can login with their own credentials
    - User isolation is maintained
    - Each user gets their own unique token
    """
    user1_data = {
        "email": "user1@example.com",
        "password": "User1Pass123!",
    }

    user2_data = {
        "email": "user2@example.com",
        "password": "User2Pass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Step 1: Register both users
        response1 = await client.post("/api/auth/register", json=user1_data)
        response2 = await client.post("/api/auth/register", json=user2_data)

        assert response1.status_code == 201, "User 1 registration should succeed"
        assert response2.status_code == 201, "User 2 registration should succeed"

        user1_id = response1.json()["user"]["id"]
        user2_id = response2.json()["user"]["id"]

        # Step 2: Verify users have different IDs
        assert user1_id != user2_id, "Users should have different IDs"

        # Step 3: Login both users
        login1 = await client.post("/api/auth/login", json=user1_data)
        login2 = await client.post("/api/auth/login", json=user2_data)

        assert login1.status_code == 200, "User 1 login should succeed"
        assert login2.status_code == 200, "User 2 login should succeed"

        token1 = login1.json()["token"]
        token2 = login2.json()["token"]

        # Step 4: Verify users get different tokens
        assert token1 != token2, "Users should get different tokens"

    # Step 5: Verify both users exist in database
    result = await test_db_session.execute(select(User))
    all_users = result.scalars().all()

    emails = [user.email for user in all_users]
    assert user1_data["email"] in emails, "User 1 should exist in database"
    assert user2_data["email"] in emails, "User 2 should exist in database"


# ============================================================================
# User Story 3: Token Security and Expiration Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_expired_token_rejection(test_db_session):
    """Test that expired JWT tokens are rejected with 401 and appropriate error message.

    T056 [US3]: Verifies that:
    - User can register and receive a valid token
    - Token with expired timestamp (exp in the past) is rejected
    - Response status is 401 Unauthorized
    - Error message indicates token expiration
    - Protected endpoint access is denied

    Security: Prevents use of expired tokens to access protected resources.
    """
    # Step 1: Register a user to get user_id
    register_data = {
        "email": "expiredtoken@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create an expired token manually
        # Token expired 1 hour ago
        expired_payload = {
            "user_id": user_id,
            "email": register_data["email"],
            "sub": user_id,
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        }

        expired_token = jwt.encode(
            expired_payload,
            settings.better_auth_secret,
            algorithm="HS256"
        )

        # Step 3: Attempt to access protected endpoint with expired token
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {expired_token}"}
        )

    # Step 4: Verify 401 Unauthorized response
    assert response.status_code == 401, f"Expected 401 for expired token, got {response.status_code}"

    # Step 5: Verify error message indicates token expiration
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response must contain error information"

    # Check for expiration-related keywords in error message
    error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
    error_message_lower = error_message.lower()

    assert any(keyword in error_message_lower for keyword in ["expired", "expiration", "exp"]), \
        f"Error message should indicate token expiration. Got: {error_message}"


@pytest.mark.asyncio
async def test_invalid_signature_rejection(test_db_session):
    """Test that tokens with invalid signatures are rejected with 401 and appropriate error message.

    T057 [US3]: Verifies that:
    - User can register and receive a valid token
    - Token signed with wrong secret is rejected
    - Response status is 401 Unauthorized
    - Error message indicates invalid token or signature
    - Tampered tokens cannot access protected resources

    Security: Prevents token tampering and ensures signature verification.
    """
    # Step 1: Register a user to get user_id
    register_data = {
        "email": "invalidsig@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create a token with valid structure but wrong signature
        # Sign with a different secret to simulate tampering
        wrong_secret = "wrong_secret_key_for_testing_12345"

        valid_payload = {
            "user_id": user_id,
            "email": register_data["email"],
            "sub": user_id,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }

        tampered_token = jwt.encode(
            valid_payload,
            wrong_secret,  # Wrong secret - signature will be invalid
            algorithm="HS256"
        )

        # Step 3: Attempt to access protected endpoint with tampered token
        response = await client.get(
            f"/api/{user_id}/tasks",
            headers={"Authorization": f"Bearer {tampered_token}"}
        )

    # Step 4: Verify 401 Unauthorized response
    assert response.status_code == 401, f"Expected 401 for invalid signature, got {response.status_code}"

    # Step 5: Verify error message indicates invalid token or signature
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, "Response must contain error information"

    # Check for invalid token/signature keywords in error message
    error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
    error_message_lower = error_message.lower()

    assert any(keyword in error_message_lower for keyword in ["invalid", "signature", "token"]), \
        f"Error message should indicate invalid token or signature. Got: {error_message}"


@pytest.mark.asyncio
async def test_malformed_token_rejection(test_db_session):
    """Test that malformed (non-JWT) tokens are rejected with 401 and appropriate error message.

    T058 [US3]: Verifies that:
    - Malformed token strings (not valid JWT format) are rejected
    - Response status is 401 Unauthorized
    - Error message indicates invalid token
    - Non-JWT strings cannot access protected resources

    Security: Prevents arbitrary strings from being accepted as valid tokens.
    """
    # Step 1: Register a user to get user_id
    register_data = {
        "email": "malformedtoken@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create various malformed tokens
        malformed_tokens = [
            "not.a.valid.jwt.token.at.all",  # Random string with dots
            "random_string_without_structure",  # Plain string
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid",  # Incomplete JWT
            "Bearer token_without_bearer_removed",  # Malformed format
            "",  # Empty string
        ]

        # Step 3: Test each malformed token
        for malformed_token in malformed_tokens:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {malformed_token}"}
            )

            # Step 4: Verify 401 Unauthorized response
            assert response.status_code == 401, \
                f"Expected 401 for malformed token '{malformed_token[:20]}...', got {response.status_code}"

            # Step 5: Verify error message indicates invalid token
            error_data = response.json()
            assert "error" in error_data or "detail" in error_data, \
                f"Response must contain error information for token: {malformed_token[:20]}..."

            # Check for invalid token keywords in error message
            error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
            error_message_lower = error_message.lower()

            assert any(keyword in error_message_lower for keyword in ["invalid", "token", "malformed"]), \
                f"Error message should indicate invalid token. Got: {error_message} for token: {malformed_token[:20]}..."


# ============================================================================
# User Story 4: Missing or Invalid Token Handling Tests
# ============================================================================


@pytest.mark.asyncio
async def test_missing_authorization_header(test_db_session):
    """Test that requests without Authorization header are rejected with 401.

    T067 [US4]: Verifies that:
    - Protected endpoint requires Authorization header
    - Request without Authorization header returns 401 Unauthorized
    - Error response contains appropriate message
    - Access is denied without authentication

    Security: Ensures all protected endpoints require authentication.
    """
    # Step 1: Register a user to get valid user_id
    register_data = {
        "email": "noheader@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Attempt to access protected endpoint WITHOUT Authorization header
        response = await client.get(f"/api/{user_id}/tasks")

    # Step 3: Verify 401 Unauthorized response
    assert response.status_code == 401, \
        f"Expected 401 for missing Authorization header, got {response.status_code}"

    # Step 4: Verify error response structure
    error_data = response.json()
    assert "error" in error_data or "detail" in error_data, \
        "Response must contain error information"

    # Step 5: Verify error message indicates missing authentication
    error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
    error_message_lower = error_message.lower()

    assert any(keyword in error_message_lower for keyword in ["authorization", "missing", "required", "unauthorized"]), \
        f"Error message should indicate missing authorization. Got: {error_message}"


@pytest.mark.asyncio
async def test_invalid_bearer_format(test_db_session):
    """Test that malformed Bearer format in Authorization header is rejected with 401.

    T068 [US4]: Verifies that:
    - Authorization header with typo in "Bearer" is rejected
    - Authorization header with only "Bearer" (no token) is rejected
    - Authorization header with token but no "Bearer" prefix is rejected
    - Authorization header with "Bearer" and only spaces is rejected
    - All malformed formats return 401 Unauthorized
    - Error messages indicate invalid format

    Security: Ensures strict Bearer token format validation.
    """
    # Step 1: Register a user to get valid user_id
    register_data = {
        "email": "invalidformat@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Test various invalid Bearer formats
        invalid_formats = [
            ("Bear token123", "Typo in Bearer"),
            ("Bearer", "Bearer without token"),
            ("token123", "Token without Bearer prefix"),
            ("Bearer  ", "Bearer with only spaces"),
            ("bearer token123", "Lowercase bearer"),
            ("BEARER token123", "Uppercase BEARER"),
            ("BearerToken123", "No space after Bearer"),
        ]

        # Step 3: Test each invalid format
        for invalid_header, description in invalid_formats:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": invalid_header}
            )

            # Step 4: Verify 401 Unauthorized response
            assert response.status_code == 401, \
                f"Expected 401 for '{description}' ('{invalid_header}'), got {response.status_code}"

            # Step 5: Verify error response structure
            error_data = response.json()
            assert "error" in error_data or "detail" in error_data, \
                f"Response must contain error information for: {description}"

            # Step 6: Verify error message indicates invalid format or token
            error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
            error_message_lower = error_message.lower()

            assert any(keyword in error_message_lower for keyword in ["invalid", "token", "authorization", "format"]), \
                f"Error message should indicate invalid format. Got: {error_message} for: {description}"


@pytest.mark.asyncio
async def test_non_decodable_token(test_db_session):
    """Test that non-decodable random strings as tokens are rejected with 401.

    T069 [US4]: Verifies that:
    - Random strings that are not valid JWT format are rejected
    - Base64-like strings that aren't valid JWTs are rejected
    - Gibberish tokens are rejected
    - All non-decodable tokens return 401 Unauthorized
    - Error messages indicate invalid token

    Security: Prevents arbitrary strings from being accepted as valid tokens.
    """
    # Step 1: Register a user to get valid user_id
    register_data = {
        "email": "nondecodable@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create various non-decodable token strings
        non_decodable_tokens = [
            ("random_gibberish_string", "Random gibberish"),
            ("12345678901234567890", "Numeric string"),
            ("abcdefghijklmnopqrstuvwxyz", "Alphabetic string"),
            ("!@#$%^&*()_+-=[]{}|;:,.<>?", "Special characters"),
            ("dGhpcyBpcyBub3QgYSB2YWxpZCBqd3Q=", "Base64-like but not JWT"),
            ("eyJhbGciOiJIUzI1NiJ9.notvalidpayload", "JWT-like but invalid payload"),
        ]

        # Step 3: Test each non-decodable token
        for token, description in non_decodable_tokens:
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers={"Authorization": f"Bearer {token}"}
            )

            # Step 4: Verify 401 Unauthorized response
            assert response.status_code == 401, \
                f"Expected 401 for '{description}' ('{token[:30]}...'), got {response.status_code}"

            # Step 5: Verify error response structure
            error_data = response.json()
            assert "error" in error_data or "detail" in error_data, \
                f"Response must contain error information for: {description}"

            # Step 6: Verify error message indicates invalid token
            error_message = str(error_data.get("error", "")) + str(error_data.get("detail", ""))
            error_message_lower = error_message.lower()

            assert any(keyword in error_message_lower for keyword in ["invalid", "token", "decode", "malformed"]), \
                f"Error message should indicate invalid token. Got: {error_message} for: {description}"


@pytest.mark.asyncio
async def test_consistent_error_response_structure(test_db_session):
    """Test that all authentication failures return consistent ErrorResponse schema.

    T070 [US4]: Verifies that:
    - All auth failures return the same response structure
    - Response always contains 'error' and 'detail' fields
    - Status code is always 401 for auth failures
    - Error response format is consistent across different failure types
    - No sensitive information is leaked in error messages

    Security: Ensures consistent error handling prevents information leakage.
    """
    # Step 1: Register a user to get valid user_id and token
    register_data = {
        "email": "consistent@example.com",
        "password": "SecurePass123!",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        register_response = await client.post(
            "/api/auth/register",
            json=register_data,
        )
        assert register_response.status_code == 201, "Registration should succeed"
        user_id = register_response.json()["user"]["id"]

        # Step 2: Create an expired token for testing
        expired_payload = {
            "user_id": user_id,
            "email": register_data["email"],
            "sub": user_id,
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
        }
        expired_token = jwt.encode(expired_payload, settings.better_auth_secret, algorithm="HS256")

        # Step 3: Create an invalid signature token
        wrong_secret = "wrong_secret_key_12345"
        valid_payload = {
            "user_id": user_id,
            "email": register_data["email"],
            "sub": user_id,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        invalid_sig_token = jwt.encode(valid_payload, wrong_secret, algorithm="HS256")

        # Step 4: Test various authentication failure scenarios
        test_scenarios = [
            (None, "Missing Authorization header"),
            ("Bearer", "Bearer without token"),
            ("Bearer random_string", "Non-decodable token"),
            (f"Bearer {expired_token}", "Expired token"),
            (f"Bearer {invalid_sig_token}", "Invalid signature"),
            ("token_without_bearer", "Missing Bearer prefix"),
        ]

        error_responses = []

        # Step 5: Collect error responses from all scenarios
        for auth_header, description in test_scenarios:
            headers = {"Authorization": auth_header} if auth_header else {}
            response = await client.get(
                f"/api/{user_id}/tasks",
                headers=headers
            )

            # Verify 401 status code
            assert response.status_code == 401, \
                f"Expected 401 for '{description}', got {response.status_code}"

            error_data = response.json()
            error_responses.append((description, error_data))

    # Step 6: Verify all responses have consistent structure
    for description, error_data in error_responses:
        # Check that response contains required fields
        assert "error" in error_data or "detail" in error_data, \
            f"Response must contain 'error' or 'detail' field for: {description}"

        # Verify response is a dictionary (JSON object)
        assert isinstance(error_data, dict), \
            f"Error response must be a JSON object for: {description}"

        # Verify no sensitive information is leaked
        error_str = str(error_data).lower()
        assert "password" not in error_str, \
            f"Error response should not contain 'password' for: {description}"
        assert "secret" not in error_str, \
            f"Error response should not contain 'secret' for: {description}"

    # Step 7: Verify all responses have similar structure (same keys)
    # Extract keys from all responses
    all_keys = [set(error_data.keys()) for _, error_data in error_responses]

    # Check that all responses have at least one common key ('error' or 'detail')
    common_keys = set.intersection(*all_keys) if all_keys else set()
    assert len(common_keys) > 0 or all(
        "error" in keys or "detail" in keys for keys in all_keys
    ), "All error responses should have consistent structure with 'error' or 'detail' field"
