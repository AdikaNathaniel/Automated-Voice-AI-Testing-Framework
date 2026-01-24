"""
Password hashing and verification utilities

This module provides secure password hashing and verification using
passlib with the bcrypt algorithm. Bcrypt is a password hashing function
designed to be slow and computationally expensive, making it resistant
to brute-force attacks.

Functions:
    hash_password(password: str) -> str:
        Hash a plain text password using bcrypt

    verify_password(plain_password: str, hashed_password: str) -> bool:
        Verify a plain text password against a hashed password

Example:
    >>> from api.auth.password import hash_password, verify_password
    >>>
    >>> # Hash a password during user registration
    >>> user_password = "MySecurePassword123!"
    >>> hashed = hash_password(user_password)
    >>>
    >>> # Verify password during login
    >>> login_attempt = "MySecurePassword123!"
    >>> if verify_password(login_attempt, hashed):
    ...     print("Login successful!")
    ... else:
    ...     print("Invalid password")
"""

from passlib.context import CryptContext


# Configure password hashing context with bcrypt
# Bcrypt is recommended for password hashing due to its adaptive nature
# and resistance to GPU-based attacks
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Number of rounds (higher = slower/more secure)
)


def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt algorithm.

    This function takes a plain text password and returns a bcrypt hash.
    Each time this function is called with the same password, it produces
    a different hash due to the random salt that bcrypt generates.

    Args:
        password (str): The plain text password to hash

    Returns:
        str: The bcrypt hashed password (60 characters long)

    Example:
        >>> hashed = hash_password("MyPassword123")
        >>> print(len(hashed))
        60
        >>> print(hashed[:4])
        $2b$

    Note:
        The returned hash includes the algorithm identifier, cost factor,
        salt, and the actual hash, all encoded in a single string.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    This function compares a plain text password with a previously hashed
    password to determine if they match. It uses constant-time comparison
    to prevent timing attacks.

    Args:
        plain_password (str): The plain text password to verify
        hashed_password (str): The hashed password to verify against

    Returns:
        bool: True if the password matches, False otherwise

    Example:
        >>> hashed = hash_password("MyPassword123")
        >>> verify_password("MyPassword123", hashed)
        True
        >>> verify_password("WrongPassword", hashed)
        False

    Note:
        This function is safe to use in timing-sensitive contexts as it
        performs constant-time string comparison.
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # If verification fails for any reason (invalid hash format, etc.)
        # return False instead of raising an exception
        return False
