"""Unit tests for JWT authentication middleware.

Tests JWT token verification, signature validation, expiration handling,
claims extraction, user existence validation, account status validation,
and password change timestamp validation.

These tests verify the middleware functions that will be implemented in:
- src/middleware/jwt_auth.py (verify_jwt_token function)
- src/dependencies.py (get_current_user dependency)
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt
import pytest
from sqlalchemy import select

from src.config import settings
from src.domain.models import User, UserStatus

# These imports will fail initially (TDD red phase) - implementation doesn't exist yet
from src.middleware.jwt_auth import verify_jwt_token


class TestJWTSignatureVerification:
    """Test JWT signature verification (T032)."""

    @pytest.mark.asyncio
    async def test_valid_signature_passes(self, test_db_session):
        """Test that JWT with valid signature passes verification.

        Verifies FR-007: System MUST verify JWT token signatures using BETTER_AUTH_SECRET.
        """
        # Create a test user in database
        user = User(
            id=uuid4(),
            email="validuser@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a valid JWT token with correct signature
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)

        assert result is not None, "Valid token should pass verification"
        assert result["user_id"] == str(user.id), "Should return correct user_id"
        assert result["email"] == user.email, "Should return correct email"

    @pytest.mark.asyncio
    async def test_invalid_signature_fails(self, test_db_session):
        """Test that JWT with invalid signature fails verification.

        Verifies FR-012: System MUST return 401 for invalid JWT signature.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="testuser@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token with WRONG secret (invalid signature)
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        wrong_secret = "wrong-secret-key-that-does-not-match"
        token = jwt.encode(payload, wrong_secret, algorithm="HS256")

        # Verify token fails validation
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception indicating invalid signature
        assert "signature" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_tampered_token_fails(self, test_db_session):
        """Test that tampered JWT token fails verification.

        Verifies that modifying any part of the token invalidates the signature.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="tampertest@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a valid token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Tamper with the token by changing the last character
        tampered_token = token[:-1] + ("a" if token[-1] != "a" else "b")

        # Verify tampered token fails validation
        with pytest.raises(Exception):
            await verify_jwt_token(tampered_token, test_db_session)


class TestTokenExpirationValidation:
    """Test JWT token expiration validation (T033)."""

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, test_db_session):
        """Test that expired JWT token is rejected.

        Verifies FR-008, FR-013: System MUST verify expiration and return 401 for expired tokens.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="expiredtest@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create an expired token (exp in the past)
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "exp": int((datetime.now(timezone.utc) - timedelta(minutes=30)).timestamp()),  # Expired 30 min ago
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify expired token is rejected
        with pytest.raises(jwt.ExpiredSignatureError):
            await verify_jwt_token(token, test_db_session)

    @pytest.mark.asyncio
    async def test_valid_unexpired_token_accepted(self, test_db_session):
        """Test that unexpired JWT token is accepted.

        Verifies that tokens within their validity period pass expiration check.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="validexpiry@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token that expires in 30 minutes (valid)
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Unexpired token should pass validation"

    @pytest.mark.asyncio
    async def test_token_expiring_soon_still_valid(self, test_db_session):
        """Test that token expiring in 1 second is still valid.

        Verifies that tokens are valid until the exact expiration moment.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="expiringsoon@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token that expires in 1 second
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(seconds=1)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token is still valid
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Token should be valid until expiration"


class TestClaimsExtraction:
    """Test JWT claims extraction (T034)."""

    @pytest.mark.asyncio
    async def test_user_id_extracted_correctly(self, test_db_session):
        """Test that user_id claim is extracted correctly.

        Verifies FR-009: System MUST extract user_id claim from validated tokens.
        """
        # Create a test user
        user_id = uuid4()
        user = User(
            id=user_id,
            email="claimstest@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()

        # Create token with user_id claim
        payload = {
            "sub": str(user_id),
            "user_id": str(user_id),
            "email": "claimstest@example.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify user_id is extracted correctly
        result = await verify_jwt_token(token, test_db_session)
        assert result["user_id"] == str(user_id), "user_id should be extracted correctly"

    @pytest.mark.asyncio
    async def test_email_extracted_correctly(self, test_db_session):
        """Test that email claim is extracted correctly.

        Verifies that email claim is available after token validation.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="emailtest@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create token with email claim
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": "emailtest@example.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify email is extracted correctly
        result = await verify_jwt_token(token, test_db_session)
        assert result["email"] == "emailtest@example.com", "email should be extracted correctly"

    @pytest.mark.asyncio
    async def test_iat_extracted_correctly(self, test_db_session):
        """Test that iat (issued at) claim is extracted correctly.

        Verifies that issued_at timestamp is available for password change validation.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="iattest@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create token with specific iat
        iat_timestamp = int(datetime.now(timezone.utc).timestamp())
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": "iattest@example.com",
            "iat": iat_timestamp,
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify iat is extracted correctly
        result = await verify_jwt_token(token, test_db_session)
        assert result["iat"] == iat_timestamp, "iat should be extracted correctly"

    @pytest.mark.asyncio
    async def test_missing_required_claims_rejected(self, test_db_session):
        """Test that token with missing required claims is rejected.

        Verifies FR-014: System MUST return 401 for malformed tokens.
        """
        # Create a test user
        user = User(
            id=uuid4(),
            email="missingclaims@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create token WITHOUT user_id claim (missing required claim)
        payload = {
            "sub": str(user.id),
            # "user_id": str(user.id),  # MISSING
            "email": "missingclaims@example.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token with missing claims is rejected
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception about missing claims
        assert "user_id" in str(exc_info.value).lower() or "claim" in str(exc_info.value).lower()


class TestUserExistenceValidation:
    """Test user existence validation (T035)."""

    @pytest.mark.asyncio
    async def test_nonexistent_user_id_rejected(self, test_db_session):
        """Test that token with non-existent user_id is rejected.

        Verifies FR-022: System MUST verify user_id exists in database and return 401 if not found.
        """
        # Create a token for a user that doesn't exist in database
        nonexistent_user_id = uuid4()
        payload = {
            "sub": str(nonexistent_user_id),
            "user_id": str(nonexistent_user_id),
            "email": "nonexistent@example.com",
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token is rejected due to non-existent user
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception about user not found
        error_msg = str(exc_info.value).lower()
        assert "user" in error_msg and ("not found" in error_msg or "does not exist" in error_msg)

    @pytest.mark.asyncio
    async def test_existing_user_id_accepted(self, test_db_session):
        """Test that token with existing user_id is accepted.

        Verifies that user existence check passes for valid users.
        """
        # Create a test user in database
        user = User(
            id=uuid4(),
            email="existinguser@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create token for existing user
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Token for existing user should pass validation"


class TestAccountStatusValidation:
    """Test account status validation (T036)."""

    @pytest.mark.asyncio
    async def test_disabled_account_rejected(self, test_db_session):
        """Test that token for disabled account is rejected.

        Verifies FR-021: System MUST verify account status and reject disabled accounts with 401.
        """
        # Create a disabled user
        user = User(
            id=uuid4(),
            email="disabled@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.DISABLED,  # Account is disabled
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a valid token for disabled user
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token is rejected due to disabled account
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception about account status
        error_msg = str(exc_info.value).lower()
        assert "disabled" in error_msg or "inactive" in error_msg or "status" in error_msg

    @pytest.mark.asyncio
    async def test_deleted_account_rejected(self, test_db_session):
        """Test that token for deleted account is rejected.

        Verifies FR-021: System MUST verify account status and reject deleted accounts with 401.
        """
        # Create a deleted user
        user = User(
            id=uuid4(),
            email="deleted@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.DELETED,  # Account is deleted
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a valid token for deleted user
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token is rejected due to deleted account
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception about account status
        error_msg = str(exc_info.value).lower()
        assert "deleted" in error_msg or "inactive" in error_msg or "status" in error_msg

    @pytest.mark.asyncio
    async def test_active_account_accepted(self, test_db_session):
        """Test that token for active account is accepted.

        Verifies that only active accounts can authenticate successfully.
        """
        # Create an active user
        user = User(
            id=uuid4(),
            email="active@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,  # Account is active
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a valid token for active user
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Token for active account should pass validation"


class TestPasswordChangeValidation:
    """Test password change timestamp validation (T037)."""

    @pytest.mark.asyncio
    async def test_token_issued_before_password_change_rejected(self, test_db_session):
        """Test that token issued before password change is rejected.

        Verifies FR-024: System MUST validate iat > password_changed_at and reject old tokens.
        """
        # Create a user with password_changed_at timestamp
        password_changed_at = datetime.now(timezone.utc) - timedelta(hours=1)
        user = User(
            id=uuid4(),
            email="passwordchanged@example.com",
            password_hash="$2b$12$newhashedpassword",
            status=UserStatus.ACTIVE,
            password_changed_at=password_changed_at,  # Password changed 1 hour ago
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token issued BEFORE password change (2 hours ago)
        old_iat = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp())
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": old_iat,  # Issued before password change
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token is rejected due to password change
        with pytest.raises(Exception) as exc_info:
            await verify_jwt_token(token, test_db_session)

        # Should raise an exception about password change
        error_msg = str(exc_info.value).lower()
        assert "password" in error_msg and ("changed" in error_msg or "invalidated" in error_msg)

    @pytest.mark.asyncio
    async def test_token_issued_after_password_change_accepted(self, test_db_session):
        """Test that token issued after password change is accepted.

        Verifies that new tokens issued after password change are valid.
        """
        # Create a user with password_changed_at timestamp
        password_changed_at = datetime.now(timezone.utc) - timedelta(hours=2)
        user = User(
            id=uuid4(),
            email="newtoken@example.com",
            password_hash="$2b$12$newhashedpassword",
            status=UserStatus.ACTIVE,
            password_changed_at=password_changed_at,  # Password changed 2 hours ago
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token issued AFTER password change (1 hour ago)
        new_iat = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": new_iat,  # Issued after password change
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Token issued after password change should be valid"

    @pytest.mark.asyncio
    async def test_token_for_user_without_password_change_accepted(self, test_db_session):
        """Test that token for user without password change is accepted.

        Verifies that users who haven't changed password (password_changed_at is NULL) can authenticate.
        """
        # Create a user WITHOUT password_changed_at (NULL)
        user = User(
            id=uuid4(),
            email="nopasswordchange@example.com",
            password_hash="$2b$12$hashedpassword",
            status=UserStatus.ACTIVE,
            password_changed_at=None,  # No password change yet
        )
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Create a token
        payload = {
            "sub": str(user.id),
            "user_id": str(user.id),
            "email": user.email,
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "exp": int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
        }
        token = jwt.encode(payload, settings.better_auth_secret, algorithm="HS256")

        # Verify token passes validation
        result = await verify_jwt_token(token, test_db_session)
        assert result is not None, "Token for user without password change should be valid"
