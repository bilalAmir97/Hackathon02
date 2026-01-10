"""
JWT token generator and authentication helpers for testing.

Provides utilities for generating valid/invalid JWT tokens and auth headers.
"""
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional
from uuid import UUID

from jose import jwt


def get_test_auth_secret() -> str:
    """Get JWT secret for testing."""
    return os.getenv("BETTER_AUTH_SECRET", "test-secret-key-for-testing-only")


class AuthHelpers:
    """Helper class for authentication testing."""

    @staticmethod
    def generate_jwt_token(
        user_id: UUID,
        expires_in_seconds: int = 3600,
        secret: Optional[str] = None,
    ) -> str:
        """
        Generate a valid JWT token for testing.

        Args:
            user_id: User UUID to encode in token
            expires_in_seconds: Token expiration time in seconds
            secret: JWT secret (uses test secret if not provided)

        Returns:
            Encoded JWT token string
        """
        secret = secret or get_test_auth_secret()
        exp_timestamp = datetime.now(timezone.utc).timestamp() + expires_in_seconds

        payload = {
            "sub": str(user_id),
            "exp": exp_timestamp,
            "iat": datetime.now(timezone.utc).timestamp(),
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    def generate_expired_token(user_id: UUID, secret: Optional[str] = None) -> str:
        """
        Generate an expired JWT token for testing.

        Args:
            user_id: User UUID to encode in token
            secret: JWT secret (uses test secret if not provided)

        Returns:
            Expired JWT token string
        """
        secret = secret or get_test_auth_secret()
        exp_timestamp = datetime.now(timezone.utc).timestamp() - 3600  # Expired 1 hour ago

        payload = {
            "sub": str(user_id),
            "exp": exp_timestamp,
            "iat": datetime.now(timezone.utc).timestamp() - 7200,
        }

        return jwt.encode(payload, secret, algorithm="HS256")

    @staticmethod
    def generate_malformed_token() -> str:
        """
        Generate a malformed JWT token for testing.

        Returns:
            Invalid JWT token string
        """
        return "malformed.jwt.token"

    @staticmethod
    def generate_invalid_signature_token(user_id: UUID) -> str:
        """
        Generate a JWT token with invalid signature.

        Args:
            user_id: User UUID to encode in token

        Returns:
            JWT token with invalid signature
        """
        wrong_secret = "wrong-secret-key"
        return AuthHelpers.generate_jwt_token(user_id, secret=wrong_secret)

    @staticmethod
    def create_auth_headers(user_id: UUID, expires_in_seconds: int = 3600) -> Dict[str, str]:
        """
        Create Authorization headers with valid JWT token.

        Args:
            user_id: User UUID
            expires_in_seconds: Token expiration time

        Returns:
            Dictionary with Authorization header
        """
        token = AuthHelpers.generate_jwt_token(user_id, expires_in_seconds)
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def create_expired_auth_headers(user_id: UUID) -> Dict[str, str]:
        """
        Create Authorization headers with expired JWT token.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with Authorization header (expired token)
        """
        token = AuthHelpers.generate_expired_token(user_id)
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def create_malformed_auth_headers() -> Dict[str, str]:
        """
        Create Authorization headers with malformed JWT token.

        Returns:
            Dictionary with Authorization header (malformed token)
        """
        token = AuthHelpers.generate_malformed_token()
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def create_invalid_signature_headers(user_id: UUID) -> Dict[str, str]:
        """
        Create Authorization headers with invalid signature.

        Args:
            user_id: User UUID

        Returns:
            Dictionary with Authorization header (invalid signature)
        """
        token = AuthHelpers.generate_invalid_signature_token(user_id)
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def decode_token(token: str, secret: Optional[str] = None) -> Dict:
        """
        Decode JWT token for validation.

        Args:
            token: JWT token string
            secret: JWT secret (uses test secret if not provided)

        Returns:
            Decoded token payload

        Raises:
            JWTError: If token is invalid
        """
        secret = secret or get_test_auth_secret()
        return jwt.decode(token, secret, algorithms=["HS256"])


# Pytest fixtures for convenience
import pytest


@pytest.fixture
def auth_headers(test_user_id):
    """Generate valid auth headers for test user."""
    return AuthHelpers.create_auth_headers(test_user_id)


@pytest.fixture
def other_auth_headers(other_user_id):
    """Generate valid auth headers for other user."""
    return AuthHelpers.create_auth_headers(other_user_id)


@pytest.fixture
def expired_auth_headers(test_user_id):
    """Generate expired auth headers."""
    return AuthHelpers.create_expired_auth_headers(test_user_id)


@pytest.fixture
def malformed_auth_headers():
    """Generate malformed auth headers."""
    return AuthHelpers.create_malformed_auth_headers()


@pytest.fixture
def invalid_signature_headers(test_user_id):
    """Generate auth headers with invalid signature."""
    return AuthHelpers.create_invalid_signature_headers(test_user_id)
