"""
JWT token generation and validation utilities

This module provides JWT (JSON Web Token) functionality for authentication,
including access token and refresh token generation, and token decoding/validation.

Uses python-jose library for JWT operations with HS256 algorithm (HMAC with SHA-256).

Functions:
    create_access_token(user_id: UUID, expires_delta: timedelta) -> str:
        Create a short-lived access token for API authentication

    create_refresh_token(user_id: UUID) -> str:
        Create a long-lived refresh token for obtaining new access tokens

    decode_token(token: str) -> dict:
        Decode and validate a JWT token, returning its payload

Example:
    >>> from uuid import uuid4
    >>> from datetime import timedelta
    >>> from api.auth.jwt import create_access_token, decode_token
    >>>
    >>> # Create token during login
    >>> user_id = uuid4()
    >>> token = create_access_token(user_id=user_id, expires_delta=timedelta(minutes=15))
    >>>
    >>> # Validate token on protected endpoints
    >>> payload = decode_token(token)
    >>> user_id_from_token = payload['sub']
"""

from datetime import datetime, timedelta
from typing import Dict, Any
from uuid import UUID, uuid4

from jose import jwt, JWTError

from api.config import get_settings


# JWT configuration derived from application settings.
settings = get_settings()
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM

# Token expiration windows (configurable for pilot environments).
ACCESS_TOKEN_EXPIRE_MINUTES = settings.JWT_EXPIRATION_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.JWT_REFRESH_EXPIRATION_DAYS


def create_access_token(user_id: UUID, expires_delta: timedelta) -> str:
    """
    Create a JWT access token for API authentication.

    Access tokens are short-lived tokens used to authenticate API requests.
    They typically expire after 15-30 minutes to limit the window of
    opportunity if a token is compromised.

    Args:
        user_id (UUID): The unique identifier of the user
        expires_delta (timedelta): How long until the token expires

    Returns:
        str: A JWT access token (3 parts: header.payload.signature)

    Example:
        >>> from uuid import uuid4
        >>> from datetime import timedelta
        >>> user_id = uuid4()
        >>> token = create_access_token(user_id, timedelta(minutes=15))
        >>> print(len(token.split('.')))
        3

    Note:
        The token payload includes:
        - sub: Subject (user_id)
        - exp: Expiration timestamp
        - iat: Issued at timestamp
        - type: Token type ('access')
    """
    # Calculate expiration time
    expire = datetime.utcnow() + expires_delta

    # Create token payload
    payload: Dict[str, Any] = {
        "sub": str(user_id),          # Subject (user identifier)
        "exp": expire,                 # Expiration time
        "iat": datetime.utcnow(),      # Issued at time
        "type": "access"               # Token type
    }

    # Encode and sign the token
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(user_id: UUID) -> str:
    """
    Create a JWT refresh token for obtaining new access tokens.

    Refresh tokens are long-lived tokens used to obtain new access tokens
    without requiring the user to log in again. They typically expire after
    7-30 days and should be stored securely.

    Args:
        user_id (UUID): The unique identifier of the user

    Returns:
        str: A JWT refresh token (3 parts: header.payload.signature)

    Example:
        >>> from uuid import uuid4
        >>> user_id = uuid4()
        >>> refresh_token = create_refresh_token(user_id)
        >>> # Store refresh_token securely (e.g., in httpOnly cookie)

    Note:
        The token payload includes:
        - sub: Subject (user_id)
        - exp: Expiration timestamp (7 days by default)
        - iat: Issued at timestamp
        - type: Token type ('refresh')

    Security:
        Refresh tokens should be:
        - Stored in httpOnly cookies (not localStorage)
        - Transmitted only over HTTPS
        - Rotated on each use (optional but recommended)
    """
    # Calculate expiration time (longer than access tokens)
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    # Create token payload
    payload: Dict[str, Any] = {
        "sub": str(user_id),          # Subject (user identifier)
        "exp": expire,                 # Expiration time
        "iat": datetime.utcnow(),      # Issued at time
        "type": "refresh",             # Token type
        "jti": str(uuid4())            # JWT ID (unique identifier)
    }

    # Encode and sign the token
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    This function decodes a JWT token, validates its signature, and checks
    that it hasn't expired. If the token is invalid or expired, an exception
    is raised.

    Args:
        token (str): The JWT token to decode

    Returns:
        dict: The decoded token payload containing claims like:
            - sub: Subject (user_id)
            - exp: Expiration timestamp
            - iat: Issued at timestamp
            - type: Token type ('access' or 'refresh')

    Raises:
        JWTError: If the token is invalid, expired, or tampered with

    Example:
        >>> token = create_access_token(uuid4(), timedelta(minutes=15))
        >>> payload = decode_token(token)
        >>> user_id = payload['sub']
        >>> token_type = payload['type']

    Security:
        This function:
        - Validates the token signature (prevents tampering)
        - Checks token expiration automatically
        - Uses constant-time comparison for signature validation

    Note:
        Always use try-except when calling this function to handle
        invalid or expired tokens gracefully.
    """
    # Validate token format before attempting to decode
    if not token or not token.strip():
        raise JWTError("Invalid token format: token is empty")

    # Check if token has the basic JWT structure (3 parts separated by dots)
    token_parts = token.split('.')
    if len(token_parts) != 3:
        raise JWTError("Invalid token format: token must have 3 parts separated by dots")

    try:
        # Decode and validate the token
        # jwt.decode automatically validates:
        # - Signature (using SECRET_KEY)
        # - Expiration (exp claim)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except JWTError as e:
        # Token is invalid, expired, or tampered with
        # Re-raise the exception to be handled by the caller
        raise e
    except Exception as e:
        # Catch any other exceptions (e.g., UnicodeDecodeError from invalid base64)
        # and convert them to JWTError
        raise JWTError(f"Invalid token format: {str(e)}")
