"""Pydantic schemas for authentication request/response validation.

Defines data transfer objects (DTOs) for user registration, login,
and authentication responses including JWT tokens.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.domain.models import UserStatus


class RegisterRequest(BaseModel):
    """Schema for user registration request.

    Validates email format and password strength requirements.
    Password must be at least 8 characters long.

    Attributes:
        email: User email address (must be valid format and unique)
        password: User password (minimum 8 characters)
    """

    email: EmailStr = Field(
        ...,
        max_length=255,
        description="User email address (must be valid format and unique)",
        examples=["user@example.com", "john.doe@company.com"],
    )

    password: str = Field(
        ...,
        min_length=8,
        description="User password (minimum 8 characters)",
        examples=["SecurePass123!", "MyP@ssw0rd"],
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password meets security requirements.

        Ensures password is not empty or only whitespace and meets
        minimum length requirements.

        Args:
            v: Password string to validate

        Returns:
            Validated password string

        Raises:
            ValueError: If password is empty, only whitespace, or too short
        """
        # Check for whitespace-only password
        if not v or not v.strip():
            raise ValueError("Password cannot be empty or only whitespace")

        # Ensure minimum length (Field validation handles this, but explicit check)
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                },
                {
                    "email": "john.doe@company.com",
                    "password": "MyP@ssw0rd",
                },
            ]
        }
    }


class LoginRequest(BaseModel):
    """Schema for user login request.

    Validates email format. Password validation is performed during
    authentication, not at schema level.

    Attributes:
        email: User email address
        password: User password
    """

    email: EmailStr = Field(
        ...,
        max_length=255,
        description="User email address",
        examples=["user@example.com"],
    )

    password: str = Field(
        ...,
        description="User password",
        examples=["SecurePass123!"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePass123!",
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Schema for user data in API responses.

    Represents user information returned after registration or login.
    Excludes sensitive fields like password_hash.

    Attributes:
        id: Unique user identifier (UUID v4)
        email: User email address
        status: Account status (active, disabled, or deleted)
        created_at: Account creation timestamp (UTC)
    """

    id: UUID = Field(
        ...,
        description="Unique user identifier",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
    )

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"],
    )

    status: UserStatus = Field(
        ...,
        description="Account status: active, disabled, or deleted",
        examples=["active"],
    )

    created_at: datetime = Field(
        ...,
        description="Account creation timestamp (UTC)",
        examples=["2026-01-12T10:00:00Z"],
    )

    model_config = {
        "from_attributes": True,  # Enable ORM mode for SQLModel compatibility
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "status": "active",
                    "created_at": "2026-01-12T10:00:00Z",
                }
            ]
        },
    }


class AuthResponse(BaseModel):
    """Schema for authentication response.

    Returned after successful registration or login. Contains JWT token
    and user information.

    Attributes:
        token: JWT access token (valid for 30 minutes)
        user: User information (id, email, status, created_at)
    """

    token: str = Field(
        ...,
        description="JWT access token (valid for 30 minutes)",
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA1MDU2MDAwLCJleHAiOjE3MDUwNTc4MDB9.signature"
        ],
    )

    user: UserResponse = Field(
        ...,
        description="User information (id, email, status, created_at)",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwiaWF0IjoxNzA1MDU2MDAwLCJleHAiOjE3MDUwNTc4MDB9.signature",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "status": "active",
                        "created_at": "2026-01-12T10:00:00Z",
                    },
                }
            ]
        }
    }
