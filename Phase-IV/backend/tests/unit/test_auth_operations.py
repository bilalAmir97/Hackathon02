"""Unit tests for authentication operations.

Tests password hashing and JWT token generation functions including:
- Password hashing with bcrypt
- Password verification
- JWT token generation with correct claims
- JWT token signature verification
- Token expiration handling
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
import pytest

# These imports will fail initially (TDD red phase) - implementation doesn't exist yet
from src.auth.password import hash_password, verify_password
from src.auth.token import create_access_token, decode_token, verify_token


class TestPasswordHashing:
    """Test password hashing and verification functions."""

    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        assert isinstance(hashed, str), "Hashed password must be a string"
        assert len(hashed) > 0, "Hashed password must not be empty"

    def test_hash_password_different_from_plaintext(self):
        """Test that hashed password is different from plaintext."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        assert hashed != password, "Hashed password must differ from plaintext"

    def test_hash_password_produces_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "SecurePass123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2, "Same password should produce different hashes due to salt"

    def test_hash_password_with_empty_string(self):
        """Test that hashing empty string works."""
        password = ""
        hashed = hash_password(password)

        assert isinstance(hashed, str), "Should return hash even for empty string"
        assert len(hashed) > 0, "Hash should not be empty"

    def test_hash_password_with_long_password(self):
        """Test that hashing very long password works."""
        password = "a" * 1000  # 1000 character password
        hashed = hash_password(password)

        assert isinstance(hashed, str), "Should handle long passwords"
        assert len(hashed) > 0, "Hash should not be empty"

    def test_hash_password_with_special_characters(self):
        """Test that hashing password with special characters works."""
        password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = hash_password(password)

        assert isinstance(hashed, str), "Should handle special characters"
        assert hashed != password, "Hash should differ from plaintext"

    def test_hash_password_with_unicode(self):
        """Test that hashing password with unicode characters works."""
        password = "パスワード123🔒"
        hashed = hash_password(password)

        assert isinstance(hashed, str), "Should handle unicode characters"
        assert hashed != password, "Hash should differ from plaintext"

    def test_verify_password_correct_password(self):
        """Test that verify_password returns True for correct password."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        result = verify_password(password, hashed)
        assert result is True, "Should return True for correct password"

    def test_verify_password_incorrect_password(self):
        """Test that verify_password returns False for incorrect password."""
        password = "SecurePass123!"
        wrong_password = "WrongPass123!"
        hashed = hash_password(password)

        result = verify_password(wrong_password, hashed)
        assert result is False, "Should return False for incorrect password"

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "SecurePass123!"
        wrong_case = "securepass123!"
        hashed = hash_password(password)

        result = verify_password(wrong_case, hashed)
        assert result is False, "Password verification should be case-sensitive"

    def test_verify_password_empty_string(self):
        """Test that verifying empty string against hash returns False."""
        password = "SecurePass123!"
        hashed = hash_password(password)

        result = verify_password("", hashed)
        assert result is False, "Empty string should not match non-empty password"

    def test_verify_password_with_invalid_hash(self):
        """Test that verify_password handles invalid hash gracefully."""
        password = "SecurePass123!"
        invalid_hash = "not-a-valid-bcrypt-hash"

        # Should either return False or raise an exception
        try:
            result = verify_password(password, invalid_hash)
            assert result is False, "Invalid hash should return False"
        except Exception:
            # It's acceptable to raise an exception for invalid hash
            pass


class TestJWTTokenGeneration:
    """Test JWT token generation and verification functions."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)

        assert isinstance(token, str), "Token must be a string"
        assert len(token) > 0, "Token must not be empty"

    def test_create_access_token_has_three_parts(self):
        """Test that JWT token has three parts separated by dots."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        parts = token.split(".")

        assert len(parts) == 3, "JWT token must have 3 parts (header.payload.signature)"

    def test_create_access_token_contains_user_id(self):
        """Test that token contains user_id claim."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert "user_id" in payload, "Token must contain user_id claim"
        assert payload["user_id"] == user_id, "user_id claim must match input"

    def test_create_access_token_contains_email(self):
        """Test that token contains email claim."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert "email" in payload, "Token must contain email claim"
        assert payload["email"] == email, "email claim must match input"

    def test_create_access_token_contains_sub_claim(self):
        """Test that token contains sub (subject) claim."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert "sub" in payload, "Token must contain sub claim"
        assert payload["sub"] == user_id, "sub claim should be user_id"

    def test_create_access_token_contains_iat_claim(self):
        """Test that token contains iat (issued at) claim."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert "iat" in payload, "Token must contain iat claim"
        assert isinstance(payload["iat"], int), "iat must be an integer timestamp"

    def test_create_access_token_contains_exp_claim(self):
        """Test that token contains exp (expiration) claim."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert "exp" in payload, "Token must contain exp claim"
        assert isinstance(payload["exp"], int), "exp must be an integer timestamp"

    def test_create_access_token_expiration_30_minutes(self):
        """Test that token expires in 30 minutes."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        iat = payload["iat"]
        exp = payload["exp"]
        duration = exp - iat

        # Should be 30 minutes (1800 seconds)
        assert duration == 1800, f"Token should expire in 30 minutes (1800s), got {duration}s"

    def test_create_access_token_iat_before_exp(self):
        """Test that issued_at is before expiration."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert payload["iat"] < payload["exp"], "iat must be before exp"

    def test_verify_token_valid_token(self):
        """Test that verify_token returns True for valid token."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        result = verify_token(token)

        assert result is True, "Should return True for valid token"

    def test_verify_token_invalid_signature(self):
        """Test that verify_token returns False for tampered token."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)

        # Tamper with the token by changing the last character
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        result = verify_token(tampered_token)
        assert result is False, "Should return False for tampered token"

    def test_verify_token_malformed_token(self):
        """Test that verify_token returns False for malformed token."""
        malformed_token = "not.a.valid.jwt.token"

        result = verify_token(malformed_token)
        assert result is False, "Should return False for malformed token"

    def test_verify_token_empty_string(self):
        """Test that verify_token returns False for empty string."""
        result = verify_token("")
        assert result is False, "Should return False for empty string"

    def test_decode_token_returns_dict(self):
        """Test that decode_token returns a dictionary."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = decode_token(token)

        assert isinstance(payload, dict), "Decoded payload must be a dictionary"

    def test_decode_token_invalid_token_raises_exception(self):
        """Test that decode_token raises exception for invalid token."""
        invalid_token = "not.a.valid.jwt"

        with pytest.raises(Exception):
            decode_token(invalid_token)

    def test_create_access_token_different_users_different_tokens(self):
        """Test that different users get different tokens."""
        user1_id = "550e8400-e29b-41d4-a716-446655440000"
        user2_id = "660e8400-e29b-41d4-a716-446655440001"
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        token1 = create_access_token(user_id=user1_id, email=email1)
        token2 = create_access_token(user_id=user2_id, email=email2)

        assert token1 != token2, "Different users should get different tokens"

    def test_create_access_token_same_user_different_tokens(self):
        """Test that same user gets different tokens at different times (due to iat)."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        token1 = create_access_token(user_id=user_id, email=email)
        # Small delay to ensure different iat
        import time
        time.sleep(1)
        token2 = create_access_token(user_id=user_id, email=email)

        assert token1 != token2, "Same user should get different tokens at different times"


class TestTokenExpiration:
    """Test JWT token expiration handling."""

    def test_verify_token_expired_token(self):
        """Test that verify_token returns False for expired token."""
        # Create a token that's already expired
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        # This test assumes create_access_token accepts expires_delta parameter
        # If not, we'll need to manually create an expired token
        expired_delta = timedelta(seconds=-1)  # Already expired

        try:
            token = create_access_token(
                user_id=user_id, email=email, expires_delta=expired_delta
            )
            result = verify_token(token)
            assert result is False, "Should return False for expired token"
        except TypeError:
            # If create_access_token doesn't support expires_delta, skip this test
            pytest.skip("create_access_token doesn't support custom expiration")

    def test_decode_token_expired_raises_exception(self):
        """Test that decode_token raises exception for expired token."""
        user_id = "550e8400-e29b-41d4-a716-446655440000"
        email = "test@example.com"

        expired_delta = timedelta(seconds=-1)

        try:
            token = create_access_token(
                user_id=user_id, email=email, expires_delta=expired_delta
            )

            with pytest.raises(jwt.ExpiredSignatureError):
                decode_token(token)
        except TypeError:
            pytest.skip("create_access_token doesn't support custom expiration")
