"""Password hashing and verification using bcrypt.

This module provides secure password hashing and verification functions using
the bcrypt algorithm with automatic salt generation. Bcrypt is designed to be
computationally expensive to resist brute-force attacks.

Security Features:
- Automatic salt generation (unique per password)
- Configurable cost factor (default: 12 rounds)
- Timing-safe comparison for verification
- Handles unicode and special characters

Example:
    >>> from src.auth.password import hash_password, verify_password
    >>>
    >>> # Hash a password
    >>> password = "SecurePass123!"
    >>> hashed = hash_password(password)
    >>>
    >>> # Verify password
    >>> is_valid = verify_password(password, hashed)
    >>> assert is_valid is True
"""

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with automatic salt generation.

    This function generates a unique salt for each password and produces a
    bcrypt hash that includes the salt, cost factor, and hash value. The same
    password will produce different hashes due to unique salts.

    Security Notes:
    - Uses bcrypt cost factor of 12 (2^12 = 4096 iterations)
    - Salt is automatically generated and embedded in the hash
    - Hash format: $2b$12$[22-char-salt][31-char-hash]
    - Safe for passwords up to 72 bytes (bcrypt limitation)

    Args:
        password: The plaintext password to hash (any string)

    Returns:
        str: The bcrypt hash string (60 characters, ASCII-safe)

    Example:
        >>> hash1 = hash_password("MyPassword123")
        >>> hash2 = hash_password("MyPassword123")
        >>> assert hash1 != hash2  # Different salts produce different hashes
        >>> assert len(hash1) == 60  # Standard bcrypt hash length
    """
    # Convert password string to bytes (bcrypt requires bytes)
    password_bytes = password.encode("utf-8")

    # Bcrypt has a 72-byte limit - truncate if necessary
    # This is a security tradeoff: longer passwords are truncated
    # but this prevents errors and is standard bcrypt behavior
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Generate salt and hash password (cost factor: 12)
    # bcrypt.gensalt() generates a random salt with default cost factor 12
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Convert hash bytes back to string for storage
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash using timing-safe comparison.

    This function checks if the provided password matches the stored hash.
    It uses constant-time comparison to prevent timing attacks.

    Security Notes:
    - Timing-safe comparison (prevents timing attacks)
    - Extracts salt from hash automatically
    - Returns False for invalid hash format (graceful degradation)
    - Case-sensitive password comparison

    Args:
        password: The plaintext password to verify
        hashed: The bcrypt hash to compare against

    Returns:
        bool: True if password matches hash, False otherwise

    Example:
        >>> password = "SecurePass123!"
        >>> hashed = hash_password(password)
        >>>
        >>> # Correct password
        >>> assert verify_password(password, hashed) is True
        >>>
        >>> # Wrong password
        >>> assert verify_password("WrongPass", hashed) is False
        >>>
        >>> # Case-sensitive
        >>> assert verify_password("securepass123!", hashed) is False
    """
    try:
        # Convert password and hash to bytes
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")

        # Bcrypt has a 72-byte limit - truncate if necessary
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]

        # Verify password using bcrypt's timing-safe comparison
        # bcrypt.checkpw extracts the salt from the hash automatically
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    except (ValueError, AttributeError):
        # Invalid hash format or encoding error
        # Return False instead of raising exception (graceful degradation)
        return False
