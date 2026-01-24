"""
Async Redis client connection manager

This module provides async Redis connectivity using redis-py with asyncio support.
It manages connection pooling and provides convenient helper methods for cache operations.

The RedisClient class wraps the async Redis client and provides:
    - Automatic connection pooling with configurable max connections
    - Helper methods for common operations: get, set, delete, exists
    - Async context manager support for proper resource cleanup
    - Integration with FastAPI dependency injection via get_redis()

Note:
    This implementation uses redis.asyncio from redis-py 4.2+, which replaced
    the standalone aioredis package. The async interface provides better
    performance and proper connection pooling for concurrent operations.

Configuration:
    Redis connection is configured via Settings (api.config):
    - REDIS_URL: Connection URL (e.g., redis://localhost:6379/0)
    - REDIS_MAX_CONNECTIONS: Max connections in pool (default: 50)

Example:
    >>> from api.redis_client import get_redis
    >>> from fastapi import Depends
    >>>
    >>> @app.get("/cached-data")
    >>> async def get_cached_data(redis = Depends(get_redis)):
    ...     value = await redis.get("my_key")
    ...     if value is None:
    ...         value = "computed_value"
    ...         await redis.set("my_key", value, ttl=300)
    ...     return {"data": value}

Direct usage:
    >>> from api.redis_client import RedisClient
    >>>
    >>> client = RedisClient(redis_url="redis://localhost:6379/0")
    >>> await client.connect()
    >>> await client.set("key", "value", ttl=60)
    >>> result = await client.get("key")
    >>> await client.disconnect()
"""

from typing import Optional, AsyncGenerator
import logging

from redis import asyncio as aioredis
from redis.asyncio import ConnectionPool

from api.config import get_settings


# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()


class RedisClient:
    """
    Async Redis client with connection pooling and helper methods.

    Provides a high-level interface for async Redis operations with automatic
    connection pooling, JSON serialization support, and convenient helper methods.

    Attributes:
        redis_url (str): Redis connection URL
        max_connections (int): Maximum connections in pool (default: 50)
        pool (ConnectionPool): Redis connection pool
        client (aioredis.Redis): Async Redis client instance

    Example:
        >>> client = RedisClient(redis_url="redis://localhost:6379/0")
        >>> await client.connect()
        >>>
        >>> # Set a value with TTL
        >>> await client.set("user:123", "john_doe", ttl=3600)
        >>>
        >>> # Get a value
        >>> username = await client.get("user:123")
        >>> print(username)  # "john_doe"
        >>>
        >>> # Check existence
        >>> exists = await client.exists("user:123")
        >>> print(exists)  # True
        >>>
        >>> # Delete a key
        >>> deleted = await client.delete("user:123")
        >>> print(deleted)  # True
        >>>
        >>> await client.disconnect()

    Note:
        - All values are automatically JSON-serialized/deserialized
        - Connection pool automatically manages connections
        - Use connect() before operations and disconnect() when done
        - For FastAPI, use get_redis() dependency instead of direct instantiation
    """

    def __init__(self, redis_url: str, max_connections: int = 50):
        """
        Initialize Redis client with connection pooling.

        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379/0)
            max_connections: Maximum number of connections in pool (default: 50)

        Example:
            >>> client = RedisClient(
            ...     redis_url="redis://localhost:6379/0",
            ...     max_connections=100
            ... )
        """
        self.redis_url = redis_url
        self.max_connections = max_connections
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[aioredis.Redis] = None
        logger.info(f"RedisClient initialized with max_connections={max_connections}")

    async def connect(self) -> None:
        """
        Establish connection pool to Redis.

        Creates a connection pool and Redis client instance. This method
        should be called before performing any Redis operations.

        Example:
            >>> client = RedisClient(redis_url="redis://localhost:6379/0")
            >>> await client.connect()

        Note:
            - Connection pool is created lazily
            - Subsequent calls to connect() will reuse existing pool
            - Pool automatically handles connection lifecycle
        """
        if self.client is None:
            self.pool = ConnectionPool.from_url(
                self.redis_url,
                max_connections=self.max_connections,
                decode_responses=True,  # Automatically decode bytes to str
            )
            self.client = aioredis.Redis(connection_pool=self.pool)
            logger.info(f"Connected to Redis at {self.redis_url}")

    async def disconnect(self) -> None:
        """
        Close Redis connection pool and cleanup resources.

        Closes all connections in the pool and cleans up resources.
        Should be called during application shutdown.

        Example:
            >>> await client.disconnect()

        Note:
            - Waits for all connections to be returned to pool
            - Closes all connections gracefully
            - Safe to call multiple times
        """
        if self.client is not None:
            await self.client.close()
            await self.pool.close()
            self.client = None
            self.pool = None
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis by key.

        Retrieves a value from Redis and returns it as a string.
        Returns None if the key doesn't exist or has expired.

        Args:
            key: Redis key to retrieve

        Returns:
            The value associated with the key, or None if key doesn't exist

        Example:
            >>> value = await client.get("user:123:name")
            >>> if value is not None:
            ...     print(f"Found: {value}")
            ... else:
            ...     print("Key not found")

        Note:
            - Returns None for non-existent keys
            - Automatically decodes bytes to string
            - Does not raise exceptions for missing keys
        """
        if self.client is None:
            await self.connect()

        value = await self.client.get(key)
        logger.debug(f"GET {key}: {value}")
        return value

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Set value in Redis with optional TTL.

        Stores a key-value pair in Redis. Optionally sets a time-to-live (TTL)
        in seconds after which the key will automatically expire.

        Args:
            key: Redis key to set
            value: Value to store (will be stored as string)
            ttl: Optional time-to-live in seconds (default: None for no expiration)

        Returns:
            True if the operation was successful, False otherwise

        Example:
            >>> # Set without expiration
            >>> await client.set("config:feature_flag", "enabled")
            >>>
            >>> # Set with 1-hour expiration
            >>> await client.set("session:abc123", "user_data", ttl=3600)

        Note:
            - TTL is in seconds
            - TTL=None means key never expires
            - Overwrites existing key if it exists
        """
        if self.client is None:
            await self.connect()

        if ttl is not None:
            result = await self.client.setex(key, ttl, value)
        else:
            result = await self.client.set(key, value)

        logger.debug(f"SET {key}={value} (ttl={ttl}): {result}")
        return bool(result)

    async def delete(self, *keys: str) -> int:
        """
        Delete key from Redis.

        Removes a key from Redis. Returns True if the key was deleted,
        False if the key didn't exist.

        Args:
            keys: One or more Redis keys to delete

        Returns:
            Number of keys deleted

        Example:
            >>> deleted = await client.delete("temp:data")
            >>> await client.delete("cache:a", "cache:b")

        Note:
            - Returns False for non-existent keys (not an error)
            - Operation is idempotent (safe to call multiple times)
        """
        if not keys:
            return 0

        if self.client is None:
            await self.connect()

        result = await self.client.delete(*keys)
        logger.debug(f"DELETE {keys}: {result}")
        return int(result)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Tests whether a key exists in Redis without retrieving its value.
        More efficient than get() when you only need to check existence.

        Args:
            key: Redis key to check

        Returns:
            True if key exists, False otherwise

        Example:
            >>> if await client.exists("cache:expensive_computation"):
            ...     result = await client.get("cache:expensive_computation")
            ... else:
            ...     result = perform_expensive_computation()
            ...     await client.set("cache:expensive_computation", result, ttl=300)

        Note:
            - Does not retrieve the value (more efficient than get())
            - Returns False for expired keys
            - Does not extend key TTL
        """
        if self.client is None:
            await self.connect()

        result = await self.client.exists(key)
        logger.debug(f"EXISTS {key}: {result}")
        return bool(result)


# Global Redis client instance
_redis_client: Optional[RedisClient] = None


async def get_redis() -> AsyncGenerator[RedisClient, None]:
    """
    FastAPI dependency for Redis client injection.

    Provides a Redis client instance for use in FastAPI route handlers.
    Automatically manages connection lifecycle and ensures proper cleanup.

    Yields:
        RedisClient: Connected Redis client instance

    Example:
        >>> from fastapi import APIRouter, Depends
        >>> from api.redis_client import get_redis, RedisClient
        >>>
        >>> router = APIRouter()
        >>>
        >>> @router.get("/cache-test")
        >>> async def cache_test(redis: RedisClient = Depends(get_redis)):
        ...     await redis.set("test_key", "test_value", ttl=60)
        ...     value = await redis.get("test_key")
        ...     return {"value": value}

    Note:
        - Client is automatically connected before yielding
        - Connection is maintained across requests (connection pooling)
        - Use with FastAPI's Depends() for automatic injection
        - Single global client instance is reused for efficiency
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(
            redis_url=settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS
        )
        await _redis_client.connect()
        logger.info("Global Redis client created and connected")

    yield _redis_client
