"""
Context Manager Service (TASK-117)

This module provides the ContextManager for managing multi-turn conversation contexts.
It stores conversation state in Redis with automatic expiration to support:
- Multi-turn voice conversations
- Conversation history tracking
- Context-aware test execution
- Automatic cleanup via TTL

Key Features:
- Store conversation context in Redis
- Retrieve context by conversation ID
- Clear context manually
- Automatic expiration after 30 minutes
- JSON serialization for complex context data
- Async operations for non-blocking I/O

Example:
    >>> from services.context_manager import ContextManager
    >>> from uuid import uuid4
    >>>
    >>> manager = ContextManager()
    >>>
    >>> # Store conversation context
    >>> conversation_id = uuid4()
    >>> context = {
    ...     "turn": 2,
    ...     "last_intent": "booking",
    ...     "user_id": "user123",
    ...     "state": "awaiting_confirmation"
    ... }
    >>> await manager.store_context(conversation_id, context)
    >>>
    >>> # Retrieve context
    >>> retrieved = await manager.get_context(conversation_id)
    >>> print(retrieved["turn"])  # 2
    >>>
    >>> # Clear context
    >>> await manager.clear_context(conversation_id)
"""

import logging
import json
from typing import Optional, Dict, Any
from uuid import UUID

logger = logging.getLogger(__name__)


# Context TTL: 30 minutes (1800 seconds)
CONTEXT_TTL_SECONDS = 30 * 60  # 1800 seconds


class ContextManager:
    """
    Manager for multi-turn conversation contexts stored in Redis.

    This service handles storage, retrieval, and cleanup of conversation
    contexts for multi-turn voice AI testing. Contexts are automatically
    expired after 30 minutes to prevent stale data accumulation.

    Attributes:
        redis_client: Redis client instance for storage operations
        ttl: Time-to-live in seconds (default: 1800 = 30 minutes)

    Example:
        >>> manager = ContextManager()
        >>>
        >>> # Store context for a conversation
        >>> conv_id = uuid4()
        >>> context = {"turn": 1, "intent": "greeting"}
        >>> await manager.store_context(conv_id, context)
        >>>
        >>> # Retrieve context
        >>> ctx = await manager.get_context(conv_id)
        >>> print(ctx["turn"])  # 1
        >>>
        >>> # Clear context
        >>> await manager.clear_context(conv_id)
    """

    def __init__(self, redis_client: Optional[Any] = None, ttl: int = CONTEXT_TTL_SECONDS):
        """
        Initialize the ContextManager.

        Args:
            redis_client: Optional Redis client instance (for testing)
            ttl: Time-to-live for context in seconds (default: 1800)

        Example:
            >>> # Use default Redis client
            >>> manager = ContextManager()
            >>>
            >>> # Use custom Redis client for testing
            >>> mock_redis = Mock()
            >>> manager = ContextManager(redis_client=mock_redis)
            >>>
            >>> # Use custom TTL (1 hour)
            >>> manager = ContextManager(ttl=3600)
        """
        self.redis_client = redis_client
        self.ttl = ttl
        logger.info(f"ContextManager initialized with TTL={ttl} seconds")

    async def store_context(self, conversation_id: UUID, context: Dict[str, Any]) -> None:
        """
        Store conversation context in Redis with TTL.

        Stores the provided context dictionary in Redis, serialized as JSON.
        The context will automatically expire after the configured TTL (default: 30 minutes).

        Args:
            conversation_id: UUID of the conversation
            context: Dictionary containing conversation context data

        Raises:
            ValueError: If conversation_id is invalid or context is not a dict
            Exception: If Redis storage fails

        Example:
            >>> conv_id = uuid4()
            >>> context = {
            ...     "turn": 3,
            ...     "last_intent": "booking",
            ...     "user_id": "user123",
            ...     "entities": {"date": "2024-01-15", "time": "14:00"}
            ... }
            >>> await manager.store_context(conv_id, context)

        Note:
            - Context is JSON-serialized before storage
            - TTL is set to 30 minutes (1800 seconds) by default
            - Overwrites existing context for the same conversation_id
        """
        if not isinstance(conversation_id, UUID):
            raise ValueError("conversation_id must be a UUID")

        if not isinstance(context, dict):
            raise ValueError("context must be a dictionary")

        logger.info(f"Storing context for conversation: {conversation_id}")

        # Generate Redis key
        key = self._get_redis_key(conversation_id)

        # Serialize context to JSON
        serialized_context = json.dumps(context)

        # Get or create Redis client
        if self.redis_client is None:
            # This will be used in production
            try:
                from api.redis_client import RedisClient, get_settings
                settings = get_settings()
                self.redis_client = RedisClient(
                    redis_url=settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                await self.redis_client.connect()
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        # Store in Redis with TTL
        await self.redis_client.set(key, serialized_context, ttl=self.ttl)

        logger.debug(f"Context stored: {key} (TTL={self.ttl}s)")

    async def get_context(self, conversation_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Retrieve conversation context from Redis.

        Fetches the context for the specified conversation ID from Redis
        and deserializes it from JSON. Returns None if the context doesn't
        exist or has expired.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Dictionary containing conversation context, or None if not found

        Raises:
            ValueError: If conversation_id is invalid

        Example:
            >>> conv_id = uuid4()
            >>> context = await manager.get_context(conv_id)
            >>> if context is not None:
            ...     print(f"Turn: {context['turn']}")
            ... else:
            ...     print("No context found (new conversation)")

        Note:
            - Returns None for expired or non-existent contexts
            - Does not extend TTL on retrieval
            - JSON-deserializes the stored context
        """
        if not isinstance(conversation_id, UUID):
            raise ValueError("conversation_id must be a UUID")

        logger.info(f"Retrieving context for conversation: {conversation_id}")

        # Generate Redis key
        key = self._get_redis_key(conversation_id)

        # Get or create Redis client
        if self.redis_client is None:
            try:
                from api.redis_client import RedisClient, get_settings
                settings = get_settings()
                self.redis_client = RedisClient(
                    redis_url=settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                await self.redis_client.connect()
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        # Retrieve from Redis
        serialized_context = await self.redis_client.get(key)

        if serialized_context is None:
            logger.debug(f"No context found for: {key}")
            return None

        # Deserialize from JSON
        try:
            context = json.loads(serialized_context)
            logger.debug(f"Context retrieved: {key}")
            return context
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize context from Redis: {e}")
            # Clear corrupted data
            await self.redis_client.delete(key)
            return None

    async def clear_context(self, conversation_id: UUID) -> bool:
        """
        Clear conversation context from Redis.

        Manually removes the context for the specified conversation ID.
        Useful for explicitly ending conversations or cleaning up after tests.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            True if context was deleted, False if it didn't exist

        Raises:
            ValueError: If conversation_id is invalid

        Example:
            >>> conv_id = uuid4()
            >>> # ... conversation happens ...
            >>> # Clear context when conversation ends
            >>> was_deleted = await manager.clear_context(conv_id)
            >>> if was_deleted:
            ...     print("Context cleared successfully")

        Note:
            - Returns False if context was already expired or didn't exist
            - Operation is idempotent (safe to call multiple times)
            - Does not raise exception if context doesn't exist
        """
        if not isinstance(conversation_id, UUID):
            raise ValueError("conversation_id must be a UUID")

        logger.info(f"Clearing context for conversation: {conversation_id}")

        # Generate Redis key
        key = self._get_redis_key(conversation_id)

        # Get or create Redis client
        if self.redis_client is None:
            try:
                from api.redis_client import RedisClient, get_settings
                settings = get_settings()
                self.redis_client = RedisClient(
                    redis_url=settings.REDIS_URL,
                    max_connections=settings.REDIS_MAX_CONNECTIONS
                )
                await self.redis_client.connect()
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise

        # Delete from Redis
        deleted = await self.redis_client.delete(key)

        if deleted:
            logger.debug(f"Context cleared: {key}")
        else:
            logger.debug(f"No context to clear: {key}")

        return deleted

    def _get_redis_key(self, conversation_id: UUID) -> str:
        """
        Generate Redis key for conversation context.

        Creates a namespaced key for storing conversation context in Redis.

        Args:
            conversation_id: UUID of the conversation

        Returns:
            Redis key string

        Example:
            >>> key = manager._get_redis_key(uuid4())
            >>> print(key)  # "context:conversation:12345678-1234-5678-1234-567812345678"
        """
        return f"context:conversation:{str(conversation_id)}"
