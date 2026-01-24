"""
Refresh token rotation and management with Redis

This module provides secure refresh token handling using Redis for storage
and blacklisting. Implements token rotation to minimize security risks from
token theft and provides TTL-based automatic cleanup.

Key Features:
    - Token storage in Redis with 7-day TTL
    - Token validation with blacklist checking
    - Token invalidation/blacklisting
    - Automatic token rotation with old token invalidation
    - User ID association with tokens

Functions:
    store_refresh_token(redis, token: str, user_id: UUID) -> None:
        Store refresh token in Redis with user association and TTL

    validate_refresh_token(redis, token: str) -> bool:
        Check if refresh token is valid (exists and not blacklisted)

    invalidate_refresh_token(redis, token: str) -> None:
        Invalidate/blacklist a refresh token

    rotate_refresh_token(redis, old_token: str, user_id: UUID) -> str:
        Rotate refresh token: invalidate old, create and store new

Security Notes:
    - Tokens automatically expire after 7 days
    - Old tokens are blacklisted during rotation to prevent reuse
    - One-time use pattern enforced: using a token for refresh invalidates it
    - All operations are async for high performance

Example:
    >>> from api.auth.refresh_token import (
    ...     store_refresh_token,
    ...     validate_refresh_token,
    ...     rotate_refresh_token
    ... )
    >>> from api.auth.jwt import create_refresh_token
    >>>
    >>> # After login, store the refresh token
    >>> refresh_token = create_refresh_token(user_id)
    >>> await store_refresh_token(redis, refresh_token, user_id)
    >>>
    >>> # On token refresh endpoint
    >>> if await validate_refresh_token(redis, old_token):
    ...     new_token = await rotate_refresh_token(redis, old_token, user_id)
    ...     return {"access_token": new_access, "refresh_token": new_token}
"""

import json
from uuid import UUID


# Token TTL settings
REFRESH_TOKEN_TTL_DAYS = 7
REFRESH_TOKEN_TTL_SECONDS = REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60  # 604800 seconds


async def store_refresh_token(redis, token: str, user_id: UUID) -> None:
    """
    Store a refresh token in Redis with user association and TTL.

    Creates a Redis entry for the refresh token that includes:
    - User ID for token-to-user mapping
    - Automatic expiration after 7 days
    - Timestamp of token creation

    Args:
        redis: Redis client instance (async)
        token: The refresh token string (JWT)
        user_id: UUID of the user this token belongs to

    Raises:
        ValueError: If token is empty or None
        ConnectionError: If Redis is unavailable

    Example:
        >>> user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        >>> token = "eyJhbGci...refresh_token"
        >>> await store_refresh_token(redis, token, user_id)

    Note:
        - Token is stored with 7-day TTL and automatically cleaned up
        - Multiple tokens can exist for the same user (multi-device support)
        - Token key format: "refresh_token:{token}"
        - Value is JSON with user_id and metadata
    """
    # Validate inputs
    if not token:
        raise ValueError("Token cannot be empty")

    # Create token data with user association
    token_data = {
        "user_id": str(user_id),
        "type": "refresh_token"
    }

    # Store in Redis with TTL
    key = f"refresh_token:{token}"
    await redis.setex(
        key,
        REFRESH_TOKEN_TTL_SECONDS,
        json.dumps(token_data)
    )


async def validate_refresh_token(redis, token: str) -> bool:
    """
    Validate that a refresh token is active and not blacklisted.

    Checks if the token exists in Redis and has not been invalidated.
    Returns False for expired, blacklisted, or non-existent tokens.

    Args:
        redis: Redis client instance (async)
        token: The refresh token string to validate

    Returns:
        bool: True if token is valid, False otherwise

    Example:
        >>> if await validate_refresh_token(redis, token):
        ...     print("Token is valid")
        ... else:
        ...     print("Token is invalid or expired")

    Note:
        - Returns False for empty tokens
        - Expired tokens are automatically removed by Redis TTL
        - Blacklisted tokens return False
        - Does not check JWT signature (that's done separately)
    """
    # Empty token is invalid
    if not token:
        return False

    # Check if token exists in Redis
    key = f"refresh_token:{token}"
    token_data = await redis.get(key)

    # If token doesn't exist, it's invalid (or expired)
    if token_data is None:
        return False

    # Check if token is blacklisted
    blacklist_key = f"blacklist:{token}"
    is_blacklisted = await redis.exists(blacklist_key)

    return not is_blacklisted


async def invalidate_refresh_token(redis, token: str) -> None:
    """
    Invalidate a refresh token by removing it from Redis.

    Permanently invalidates the token so it can no longer be used.
    This is called during logout or token rotation.

    Args:
        redis: Redis client instance (async)
        token: The refresh token string to invalidate

    Example:
        >>> # On logout
        >>> await invalidate_refresh_token(redis, refresh_token)
        >>>
        >>> # After rotation
        >>> await invalidate_refresh_token(redis, old_token)

    Note:
        - Silently succeeds if token doesn't exist
        - Removes token from Redis completely
        - For extra security, could add to blacklist with TTL
    """
    # Remove token from Redis
    key = f"refresh_token:{token}"
    await redis.delete(key)

    # Optionally add to blacklist for remaining TTL period
    # This prevents race conditions if someone tries to use token
    # between rotation and Redis deletion
    blacklist_key = f"blacklist:{token}"
    await redis.setex(
        blacklist_key,
        REFRESH_TOKEN_TTL_SECONDS,
        "1"
    )


async def rotate_refresh_token(redis, old_token: str, user_id: UUID) -> str:
    """
    Rotate a refresh token: invalidate old, generate and store new.

    This implements the refresh token rotation security pattern:
    1. Validates old token exists
    2. Invalidates/blacklists the old token
    3. Generates a new refresh token
    4. Stores the new token with TTL
    5. Returns the new token

    Args:
        redis: Redis client instance (async)
        old_token: The current refresh token to rotate
        user_id: UUID of the user (for new token)

    Returns:
        str: New refresh token

    Raises:
        ValueError: If old token is invalid

    Example:
        >>> # In token refresh endpoint
        >>> old_token = request_data.refresh_token
        >>> if await validate_refresh_token(redis, old_token):
        ...     new_refresh = await rotate_refresh_token(redis, old_token, user_id)
        ...     return {"refresh_token": new_refresh, ...}

    Security:
        - Old token is immediately invalidated to prevent reuse
        - New token has fresh 7-day TTL
        - Rotation prevents token theft from being useful long-term
        - Failed rotation attempts don't generate new tokens

    Note:
        - This function generates a new JWT token
        - Old token cannot be used again after rotation
        - Each refresh creates a new token (one-time use pattern)
    """
    # Import here to avoid circular dependency
    from api.auth.jwt import create_refresh_token

    # Validate old token exists (will be checked by caller, but double-check)
    is_valid = await validate_refresh_token(redis, old_token)
    if not is_valid:
        raise ValueError("Old refresh token is invalid or expired")

    # Invalidate old token
    await invalidate_refresh_token(redis, old_token)

    # Generate new refresh token
    new_token = create_refresh_token(user_id)

    # Store new token
    await store_refresh_token(redis, new_token, user_id)

    return new_token


# =============================================================================
# Export
# =============================================================================

__all__ = [
    'store_refresh_token',
    'validate_refresh_token',
    'invalidate_refresh_token',
    'rotate_refresh_token',
    'REFRESH_TOKEN_TTL_DAYS',
    'REFRESH_TOKEN_TTL_SECONDS',
]
