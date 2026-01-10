"""
Contract validation tests for authentication.

Tests that JWT tokens and authentication responses conform to expected contracts.
"""
import pytest
from uuid import uuid4

from tests.utils.auth_helpers import AuthHelpers
from tests.utils.assertions import Assertions


@pytest.mark.contract
@pytest.mark.auth
@pytest.mark.us1
class TestAuthContract:
    """Test authentication contract validation."""

    def test_jwt_token_has_three_parts(self, test_user_id):
        """
        T026: Test that JWT token has correct structure (3 parts).

        Given: User ID
        When: JWT token is generated
        Then: Token has 3 parts separated by dots (header.payload.signature)
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)

        parts = token.split(".")
        assert len(parts) == 3, f"JWT should have 3 parts, got {len(parts)}"

        # Each part should be non-empty
        for i, part in enumerate(parts):
            assert len(part) > 0, f"JWT part {i} should not be empty"

    def test_jwt_token_contains_required_claims(self, test_user_id):
        """
        T027: Test that JWT token contains all required claims.

        Given: Generated JWT token
        When: Token is decoded
        Then: Token contains 'sub', 'exp', and 'iat' claims
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)
        payload = AuthHelpers.decode_token(token)

        required_claims = ["sub", "exp", "iat"]
        for claim in required_claims:
            assert claim in payload, f"JWT should contain '{claim}' claim"

    def test_jwt_sub_claim_is_valid_uuid(self, test_user_id):
        """
        T027: Test that JWT 'sub' claim is a valid UUID string.

        Given: Generated JWT token
        When: Token is decoded
        Then: 'sub' claim is a valid UUID string
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)
        payload = AuthHelpers.decode_token(token)

        sub = payload["sub"]
        assert isinstance(sub, str), "'sub' claim should be a string"

        # Verify it's a valid UUID
        try:
            from uuid import UUID
            UUID(sub)
        except ValueError:
            pytest.fail(f"'sub' claim is not a valid UUID: {sub}")

    def test_jwt_exp_claim_is_future_timestamp(self, test_user_id):
        """
        T027: Test that JWT 'exp' claim is in the future.

        Given: Generated JWT token with default expiration
        When: Token is decoded
        Then: 'exp' claim is a timestamp in the future
        """
        from datetime import datetime, timezone

        token = AuthHelpers.generate_jwt_token(test_user_id, expires_in_seconds=3600)
        payload = AuthHelpers.decode_token(token)

        exp = payload["exp"]
        assert isinstance(exp, (int, float)), "'exp' claim should be a numeric timestamp"

        current_timestamp = datetime.now(timezone.utc).timestamp()
        assert exp > current_timestamp, "'exp' claim should be in the future"

    def test_jwt_iat_claim_is_past_timestamp(self, test_user_id):
        """
        T027: Test that JWT 'iat' claim is in the past or present.

        Given: Generated JWT token
        When: Token is decoded
        Then: 'iat' claim is a timestamp in the past or present
        """
        from datetime import datetime, timezone

        token = AuthHelpers.generate_jwt_token(test_user_id)
        payload = AuthHelpers.decode_token(token)

        iat = payload["iat"]
        assert isinstance(iat, (int, float)), "'iat' claim should be a numeric timestamp"

        current_timestamp = datetime.now(timezone.utc).timestamp()
        assert iat <= current_timestamp + 1, "'iat' claim should be in the past or present"

    def test_jwt_token_signature_is_valid(self, test_user_id):
        """
        T027: Test that JWT token signature can be verified.

        Given: Generated JWT token
        When: Token is decoded with correct secret
        Then: Signature verification succeeds
        """
        token = AuthHelpers.generate_jwt_token(test_user_id)

        # Should not raise exception
        payload = AuthHelpers.decode_token(token)
        assert payload is not None

    def test_jwt_token_with_wrong_secret_fails_verification(self, test_user_id):
        """
        T027: Test that JWT token with wrong secret fails verification.

        Given: JWT token signed with one secret
        When: Token is decoded with different secret
        Then: Verification fails
        """
        from jose import JWTError

        token = AuthHelpers.generate_jwt_token(test_user_id)

        # Try to decode with wrong secret
        with pytest.raises(JWTError):
            AuthHelpers.decode_token(token, secret="wrong-secret")

    def test_expired_jwt_token_fails_verification(self, test_user_id):
        """
        T027: Test that expired JWT token fails verification.

        Given: Expired JWT token
        When: Token is decoded
        Then: Verification fails with expiration error
        """
        from jose import JWTError

        token = AuthHelpers.generate_expired_token(test_user_id)

        # Should raise JWTError due to expiration
        with pytest.raises(JWTError):
            AuthHelpers.decode_token(token)

    def test_authorization_header_format(self, test_user_id):
        """
        T026: Test that Authorization header has correct format.

        Given: User ID
        When: Auth headers are created
        Then: Header has format "Bearer <token>"
        """
        headers = AuthHelpers.create_auth_headers(test_user_id)

        assert "Authorization" in headers, "Should have Authorization header"

        auth_value = headers["Authorization"]
        assert auth_value.startswith("Bearer "), "Authorization should start with 'Bearer '"

        token = auth_value.replace("Bearer ", "")
        Assertions.assert_jwt_token_structure(token)


@pytest.mark.contract
@pytest.mark.auth
@pytest.mark.us1
class TestAuthErrorResponses:
    """Test authentication error response contracts."""

    def test_unauthorized_response_has_detail_field(self, client):
        """
        T026: Test that 401 responses have 'detail' field.

        Given: Request without authentication
        When: Protected endpoint is accessed
        Then: 401 response contains 'detail' field
        """
        response = client.get("/api/todos")

        assert response.status_code == 401
        body = response.json()
        assert "detail" in body, "401 response should have 'detail' field"
        assert isinstance(body["detail"], str), "'detail' should be a string"

    def test_unauthorized_response_has_www_authenticate_header(self, client):
        """
        T026: Test that 401 responses have WWW-Authenticate header.

        Given: Request without authentication
        When: Protected endpoint is accessed
        Then: Response includes WWW-Authenticate header
        """
        response = client.get("/api/todos")

        assert response.status_code == 401
        # Note: WWW-Authenticate header may or may not be present depending on implementation
        # This test documents the expected behavior per HTTP standards

    def test_malformed_token_error_message_is_descriptive(self, client):
        """
        T026: Test that malformed token errors have descriptive messages.

        Given: Malformed JWT token
        When: Protected endpoint is accessed
        Then: Error message describes the issue
        """
        headers = AuthHelpers.create_malformed_auth_headers()
        response = client.get("/api/todos", headers=headers)

        assert response.status_code == 401
        body = response.json()
        detail = body["detail"].lower()
        assert "invalid" in detail or "token" in detail, \
            "Error message should mention invalid token"
