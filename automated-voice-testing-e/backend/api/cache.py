"""
Cache decorator and invalidation helpers

This module provides a decorator for caching function results in Redis
with configurable TTL, key prefixes, and cache invalidation utilities.

The @cache decorator automatically caches async function results in Redis,
using function name and arguments to generate unique cache keys. It supports:
    - Configurable TTL (time-to-live) for automatic expiration
    - Custom key prefixes for namespace organization
    - Automatic serialization/deserialization of results
    - Cache invalidation helpers for manual cache clearing

Configuration:
    Default cache TTL is configured via Settings.CACHE_TTL (api.config).
    Can be overridden per-function using the ttl parameter.

Example:
    >>> from api.cache import cache, invalidate_cache
    >>>
    >>> @cache(ttl=300, key_prefix="products")
    >>> async def get_product(product_id: int):
    ...     # Expensive database or API call
    ...     return fetch_product_from_db(product_id)
    >>>
    >>> # First call executes function and caches result
    >>> product = await get_product(123)
    >>>
    >>> # Subsequent calls return cached result (fast!)
    >>> product = await get_product(123)
    >>>
    >>> # Manually invalidate cache when product is updated
    >>> await invalidate_cache("products:get_product:123")

Cache Key Format:
    Cache keys are generated in the format:
    {key_prefix}:{function_name}:{args_hash}

    Where:
    - key_prefix: Custom prefix or "cache" (default)
    - function_name: Name of the decorated function
    - args_hash: Hash of function arguments (args + kwargs)

    Example keys:
    - cache:get_user:abc123
    - products:list_products:page=1_limit=10
    - api:expensive_calculation:x=5_y=10

Invalidation:
    Use invalidate_cache(key) to delete a specific cache entry.
    Use clear_cache(pattern) to delete multiple entries matching a pattern.
"""

from typing import Optional, Callable, Any, TypeVar
from functools import wraps
import hashlib
import json
import logging

from api.redis_client import get_redis
from api.config import get_settings


# Configure logging
logger = logging.getLogger(__name__)

# Get application settings
settings = get_settings()

# Type variable for generic function signatures
F = TypeVar('F', bound=Callable[..., Any])


def _generate_cache_key(
    func_name: str,
    args: tuple,
    kwargs: dict,
    key_prefix: str = "cache"
) -> str:
    """
    Generate a unique cache key from function name and arguments.

    Creates a deterministic cache key by hashing the function arguments.
    The key format is: {prefix}:{function_name}:{args_hash}

    Args:
        func_name: Name of the function being cached
        args: Positional arguments passed to function
        kwargs: Keyword arguments passed to function
        key_prefix: Prefix for the cache key (default: "cache")

    Returns:
        Unique cache key string

    Example:
        >>> key = _generate_cache_key("get_user", (123,), {}, "users")
        >>> print(key)
        users:get_user:a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
    """
    # Create a deterministic string from args and kwargs
    args_str = json.dumps({
        "args": args,
        "kwargs": kwargs
    }, sort_keys=True, default=str)

    # Generate hash of arguments
    args_hash = hashlib.sha256(args_str.encode()).hexdigest()[:16]

    # Format: prefix:function_name:args_hash
    cache_key = f"{key_prefix}:{func_name}:{args_hash}"

    logger.debug(f"Generated cache key: {cache_key}")
    return cache_key


def cache(
    func: Optional[F] = None,
    *,
    ttl: Optional[int] = None,
    key_prefix: str = "cache"
) -> F:
    """
    Decorator to cache async function results in Redis.

    Caches the return value of async functions in Redis with an optional TTL.
    On subsequent calls with the same arguments, returns the cached value
    instead of executing the function.

    Args:
        func: The function to decorate (provided automatically when used without parentheses)
        ttl: Time-to-live in seconds (default: settings.CACHE_TTL or 300)
        key_prefix: Prefix for cache keys (default: "cache")

    Returns:
        Decorated function that caches results

    Example:
        >>> # Using with default settings
        >>> @cache
        >>> async def get_user(user_id: int):
        ...     return fetch_user_from_db(user_id)
        >>>
        >>> # Using with custom TTL and prefix
        >>> @cache(ttl=600, key_prefix="products")
        >>> async def get_product(product_id: int):
        ...     return fetch_product_from_db(product_id)
        >>>
        >>> # Call the cached function
        >>> user = await get_user(123)  # First call: executes function
        >>> user = await get_user(123)  # Second call: returns cached result

    Note:
        - Only works with async functions
        - Return values must be JSON-serializable
        - Different arguments generate different cache keys
        - TTL of None means no expiration (cache forever)
        - Use invalidate_cache() to manually clear cached values
    """

    def decorator(fn: F) -> F:
        # Get the actual TTL to use
        cache_ttl = ttl if ttl is not None else getattr(settings, 'CACHE_TTL', 300)

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function and arguments
            cache_key = _generate_cache_key(
                func_name=fn.__name__,
                args=args,
                kwargs=kwargs,
                key_prefix=key_prefix
            )

            # Try to get cached value using async context manager
            redis_gen = get_redis()
            redis = await redis_gen.__anext__()

            try:
                cached_value = await redis.get(cache_key)

                if cached_value is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    # Deserialize and return cached value
                    return json.loads(cached_value)

                # Cache miss - execute function
                logger.debug(f"Cache miss for {cache_key}")
                result = await fn(*args, **kwargs)

                # Serialize and cache the result
                serialized_result = json.dumps(result, default=str)
                await redis.set(cache_key, serialized_result, ttl=cache_ttl)

                logger.debug(f"Cached result for {cache_key} (ttl={cache_ttl})")
                return result

            except Exception as e:
                logger.error(f"Cache error for {cache_key}: {e}")
                # On cache error, execute function without caching
                return await fn(*args, **kwargs)

        return wrapper

    # Support both @cache and @cache(ttl=300) syntax
    if func is None:
        # Called with parameters: @cache(ttl=300)
        return decorator
    else:
        # Called without parameters: @cache
        return decorator(func)


async def invalidate_cache(key: str) -> bool:
    """
    Invalidate a specific cache entry by key.

    Deletes a single cache entry from Redis. Useful when you need to
    manually clear cache after data updates.

    Args:
        key: The cache key to invalidate

    Returns:
        True if key was deleted, False if key didn't exist

    Example:
        >>> # After updating a user
        >>> await invalidate_cache("cache:get_user:123")
        True
        >>>
        >>> # Using with custom prefix
        >>> await invalidate_cache("products:get_product:456")
        True

    Note:
        - Returns False if key doesn't exist (not an error)
        - Safe to call even if key is already expired
        - Use clear_cache() to delete multiple keys at once
    """
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()

    try:
        result = await redis.delete(key)
        logger.info(f"Invalidated cache key: {key}")
        return result
    except Exception as e:
        logger.error(f"Error invalidating cache key {key}: {e}")
        return False


async def clear_cache(pattern: str = "cache:*") -> int:
    """
    Clear multiple cache entries matching a pattern.

    Deletes all cache keys matching the specified pattern. Useful for
    bulk cache invalidation or clearing entire namespaces.

    Args:
        pattern: Redis key pattern to match (default: "cache:*")
                Supports wildcards: * (any chars), ? (single char)

    Returns:
        Number of keys deleted

    Example:
        >>> # Clear all cache entries
        >>> count = await clear_cache("cache:*")
        >>> print(f"Cleared {count} cache entries")
        >>>
        >>> # Clear specific prefix
        >>> await clear_cache("products:*")
        >>>
        >>> # Clear specific function cache
        >>> await clear_cache("cache:get_user:*")

    Note:
        - Be careful with patterns - they can delete many keys
        - Pattern matching uses Redis SCAN for efficiency
        - Returns 0 if no keys match the pattern
        - Use invalidate_cache() for single key deletion

    Warning:
        Using "*" pattern will delete ALL keys in Redis database.
        Always use appropriate prefixes to limit scope.
    """
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()

    try:
        # Use the Redis client's connection to scan for keys
        deleted_count = 0

        # Use SCAN to find matching keys (more efficient than KEYS)
        # Note: redis.asyncio doesn't expose scan_iter directly, so we'll
        # use the underlying client
        if hasattr(redis, 'client') and redis.client is not None:
            # Get all keys matching pattern using KEYS
            # In production, consider using SCAN for better performance
            keys = []
            cursor = 0
            while True:
                # Use SCAN command for production safety
                cursor, partial_keys = await redis.client.scan(
                    cursor, match=pattern, count=100
                )
                keys.extend(partial_keys)
                if cursor == 0:
                    break

            # Delete all matching keys
            if keys:
                deleted_count = await redis.client.delete(*keys)
                logger.info(f"Cleared {deleted_count} cache entries matching '{pattern}'")
        else:
            logger.warning("Redis client not available for pattern scanning")

        return deleted_count

    except Exception as e:
        logger.error(f"Error clearing cache with pattern '{pattern}': {e}")
        return 0
