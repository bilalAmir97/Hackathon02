"""
Integration tests for JWT authentication middleware.

Tests User Story 1: Authentication Flow Validation
Validates JWT token verification, protected route enforcement, and authorization.
"""
import pytest
from uuid import uuid4

from tests.utils.auth_helpers import AuthHelpers
from tests.utils.assertions import Assertions


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.us1
class TestJWTAuthentication:
    """Test JWT authentication middleware behavior."""

    def test_valid_jwt_token_grants_access(self, client, test_user_id):
        """
        T019: Test that valid JWT token grants access to protected routes.

        Given: A valid JWT token with user_id in 'sub' claim
        When: Request is made to protected endpoint with Authorization header
        Then: Request succeeds and user_id is extracted correctly
        """
        # Create valid auth headers
        headers = AuthHelpers.create_auth_headers(test_user_id)

        # Access protected endpoint (list todos)
        response = client.get("/api/todos", headers=headers)

        # Should succeed (200 OK with empty list initially)
        Assertions.assert_http_status(response, 200)
        assert response.json() == []

    def test_missing_authorization_header_returns_401(self, client):
        """
        T025: Test that missing Authorization header returns 401.

        Given: No Authorization header provided
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        # Make request without auth headers
        response = client.get("/api/todos")

        # Should return 401
        Assertions.assert_http_status(response, 401)
        body = response.json()
        assert "detail" in body

    def test_malformed_jwt_token_returns_401(self, client):
        """
        T025: Test that malformed JWT token returns 401.

        Given: Malformed JWT token (not 3 parts)
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        headers = AuthHelpers.create_malformed_auth_headers()

        response = client.get("/api/todos", headers=headers)

        Assertions.assert_http_status(response, 401)
        Assertions.assert_error_response(response, 401, "Invalid token")

    def test_expired_jwt_token_returns_401(self, client, test_user_id):
        """
        T022: Test that expired JWT token returns 401.

        Given: Expired JWT token (exp claim in the past)
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        headers = AuthHelpers.create_expired_auth_headers(test_user_id)

        response = client.get("/api/todos", headers=headers)

        Assertions.assert_http_status(response, 401)
        Assertions.assert_error_response(response, 401, "Invalid token")

    def test_invalid_signature_returns_401(self, client, test_user_id):
        """
        T022: Test that JWT with invalid signature returns 401.

        Given: JWT token signed with wrong secret
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        headers = AuthHelpers.create_invalid_signature_headers(test_user_id)

        response = client.get("/api/todos", headers=headers)

        Assertions.assert_http_status(response, 401)
        Assertions.assert_error_response(response, 401, "Invalid token")

    def test_jwt_token_structure_validation(self, test_user_id):
        """
        T027: Test that generated JWT tokens have correct structure.

        Given: User ID
        When: JWT token is generated
        Then: Token has 3 parts (header.payload.signature)
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)

        Assertions.assert_jwt_token_structure(token)

        # Verify token can be decoded
        payload = AuthHelpers.decode_token(token)
        assert payload["sub"] == str(test_user_id)
        assert "exp" in payload
        assert "iat" in payload

    def test_jwt_token_contains_required_claims(self, test_user_id):
        """
        T027: Test that JWT token contains required claims (sub, exp, iat).

        Given: User ID
        When: JWT token is generated and decoded
        Then: Token contains 'sub', 'exp', and 'iat' claims
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)
        payload = AuthHelpers.decode_token(token)

        # Verify required claims
        assert "sub" in payload, "Token missing 'sub' claim"
        assert "exp" in payload, "Token missing 'exp' claim"
        assert "iat" in payload, "Token missing 'iat' claim"

        # Verify sub claim is valid UUID string
        assert payload["sub"] == str(test_user_id)

    def test_different_users_have_different_tokens(self, test_user_id, other_user_id):
        """
        T024: Test that different users get different JWT tokens.

        Given: Two different user IDs
        When: JWT tokens are generated for each
        Then: Tokens are different and contain correct user IDs
        """
        token1 = AuthHelpers.generate_jwt_token(test_user_id)
        token2 = AuthHelpers.generate_jwt_token(other_user_id)

        # Tokens should be different
        assert token1 != token2

        # Each token should contain correct user ID
        payload1 = AuthHelpers.decode_token(token1)
        payload2 = AuthHelpers.decode_token(token2)

        assert payload1["sub"] == str(test_user_id)
        assert payload2["sub"] == str(other_user_id)

    def test_protected_route_enforces_authorization(self, client, test_user_id, other_user_id):
        """
        T024: Test that protected routes enforce user authorization.

        Given: Two users with valid JWT tokens
        When: User A creates a todo and User B tries to access it
        Then: User B cannot access User A's todo (404 or 403)
        """
        # User A creates a todo
        user_a_headers = AuthHelpers.create_auth_headers(test_user_id)
        response = client.post(
            "/api/todos",
            json={"title": "User A's todo"},
            headers=user_a_headers,
        )
        Assertions.assert_http_status(response, 201)
        todo_id = response.json()["id"]

        # User B tries to access User A's todo
        user_b_headers = AuthHelpers.create_auth_headers(other_user_id)
        response = client.get(f"/api/todos/{todo_id}", headers=user_b_headers)

        # Should return 404 (not found for this user)
        Assertions.assert_http_status(response, 404)

    def test_all_protected_endpoints_require_auth(self, client):
        """
        T025: Test that all protected endpoints require authentication.

        Given: No authentication provided
        When: Requests are made to all protected endpoints
        Then: All return 401 Unauthorized
        """
        protected_endpoints = [
            ("GET", "/api/todos"),
            ("POST", "/api/todos"),
            ("GET", "/api/todos/00000000-0000-0000-0000-000000000000"),
            ("PUT", "/api/todos/00000000-0000-0000-0000-000000000000"),
            ("DELETE", "/api/todos/00000000-0000-0000-0000-000000000000"),
            ("POST", "/api/todos/00000000-0000-0000-0000-000000000000/toggle"),
        ]

        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)

            # All should return 401
            assert response.status_code == 401, \
                f"{method} {endpoint} should return 401, got {response.status_code}"


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.us1
class TestAuthenticationEdgeCases:
    """Test edge cases for authentication."""

    def test_bearer_prefix_case_insensitive(self, client, test_user_id):
        """
        Test that Bearer prefix is handled correctly.

        Given: Valid JWT token
        When: Authorization header uses 'Bearer' prefix
        Then: Request succeeds
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/todos", headers=headers)
        Assertions.assert_http_status(response, 200)

    def test_empty_authorization_header_returns_401(self, client):
        """
        Test that empty Authorization header returns 401.

        Given: Empty Authorization header
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        headers = {"Authorization": ""}

        response = client.get("/api/todos", headers=headers)
        Assertions.assert_http_status(response, 401)

    def test_authorization_without_bearer_prefix_returns_401(self, client, test_user_id):
        """
        Test that Authorization header without Bearer prefix returns 401.

        Given: JWT token without 'Bearer' prefix
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)
        headers = {"Authorization": token}  # Missing "Bearer " prefix

        response = client.get("/api/todos", headers=headers)
        Assertions.assert_http_status(response, 401)

    def test_jwt_token_with_missing_sub_claim_returns_401(self, client):
        """
        Test that JWT token without 'sub' claim returns 401.

        Given: JWT token missing 'sub' claim
        When: Request is made to protected endpoint
        Then: 401 Unauthorized is returned with appropriate error
        """
        import os
        from jose import jwt
        from datetime import datetime, timezone

        # Create token without 'sub' claim
        payload = {
            "exp": datetime.now(timezone.utc).timestamp() + 3600,
            "iat": datetime.now(timezone.utc).timestamp(),
        }
        token = jwt.encode(payload, os.getenv("BETTER_AUTH_SECRET"), algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/todos", headers=headers)
        Assertions.assert_http_status(response, 401)
        Assertions.assert_error_response(response, 401, "sub")
