"""
Houndify Integration

This package contains the Houndify API client and related utilities for
voice AI interaction using SoundHound's Houndify platform.

Supports three client types:
- HoundifyClient: Real Houndify API client (requires credentials)
- MockHoundifyClient: Pattern-based mock with deterministic responses
- LLMMockClient: LLM-powered mock with dynamic responses (requires OpenAI API key)
"""

import logging
import os
from typing import Optional, Union

from .client import HoundifyClient
from .mock_client import MockHoundifyClient, MockHoundifyError
from .llm_mock_client import LLMMockClient

logger = logging.getLogger(__name__)

# Valid mock types
MOCK_TYPE_PATTERN = "pattern"  # Pattern-based MockHoundifyClient
MOCK_TYPE_LLM = "llm"          # LLM-powered LLMMockClient


def create_houndify_client(
    client_id: Optional[str] = None,
    client_key: Optional[str] = None,
    use_mock: Optional[bool] = None,
    mock_type: Optional[str] = None,
) -> Union[HoundifyClient, MockHoundifyClient, LLMMockClient]:
    """
    Factory function to create the appropriate Houndify client.

    This centralizes the logic for choosing between mock and real clients,
    ensuring consistent behavior across all services.

    Args:
        client_id: Houndify client ID (required for real client)
        client_key: Houndify client key (required for real client)
        use_mock: Override for mock setting. If None, reads from environment
                  variable USE_HOUNDIFY_MOCK or config setting.
        mock_type: Type of mock client to use when use_mock=True.
                   Options: "pattern" (default) or "llm".
                   Can also be set via HOUNDIFY_MOCK_TYPE env var.

    Returns:
        HoundifyClient, MockHoundifyClient, or LLMMockClient instance

    Raises:
        ValueError: If real client is requested but credentials are missing
        ValueError: If LLM mock is requested but OPENROUTER_API_KEY is not set

    Environment Variables:
        USE_HOUNDIFY_MOCK: Set to "true" to use mock client (default: true)
        HOUNDIFY_MOCK_TYPE: Set to "llm" for LLM-powered mock, "pattern" for
                            pattern-based mock (default: pattern)
        OPENROUTER_API_KEY: Required when HOUNDIFY_MOCK_TYPE=llm
        LLM_MOCK_MODEL: Model to use for LLM mock (default: openai/gpt-4o-mini)

    Example:
        # Auto-detect from environment
        client = create_houndify_client(
            client_id=settings.SOUNDHOUND_CLIENT_ID,
            client_key=settings.SOUNDHOUND_API_KEY
        )

        # Force LLM mock mode
        client = create_houndify_client(use_mock=True, mock_type="llm")
    """
    # Determine if mock should be used
    if use_mock is None:
        # Check environment variable first
        env_flag = os.getenv("USE_HOUNDIFY_MOCK", "").strip().lower()
        use_mock = env_flag in {"1", "true", "yes"}

        # If not set via env, try to load from config
        if not use_mock and not env_flag:
            try:
                from api.config import get_settings
                settings = get_settings()
                use_mock = getattr(settings, "USE_HOUNDIFY_MOCK", True)
            except Exception:
                # Default to mock if config unavailable
                use_mock = True

    if use_mock:
        # Determine mock type
        if mock_type is None:
            mock_type = os.getenv("HOUNDIFY_MOCK_TYPE", MOCK_TYPE_PATTERN).strip().lower()

        if mock_type == MOCK_TYPE_LLM:
            # Validate OpenRouter API key is available
            openrouter_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_key:
                logger.warning(
                    "[HOUNDIFY] OPENROUTER_API_KEY not set, falling back to pattern mock"
                )
                mock_type = MOCK_TYPE_PATTERN
            else:
                model = os.getenv("LLM_MOCK_MODEL", "openai/gpt-4o-mini")
                logger.info(f"[HOUNDIFY] Using LLMMockClient ({model} via OpenRouter)")
                return LLMMockClient(
                    api_key=openrouter_key,
                    model=model,
                )

        # Default to pattern-based mock
        logger.info("[HOUNDIFY] Using MockHoundifyClient (pattern-based)")
        return MockHoundifyClient(
            client_id=client_id,
            client_key=client_key,
        )

    # Validate credentials for real client
    if not client_id or not client_key:
        raise ValueError(
            "SOUNDHOUND_CLIENT_ID and SOUNDHOUND_API_KEY are required "
            "when USE_HOUNDIFY_MOCK is False"
        )

    logger.info("[HOUNDIFY] Using real HoundifyClient")
    return HoundifyClient(
        client_id=client_id,
        client_key=client_key,
    )


__all__ = [
    'HoundifyClient',
    'MockHoundifyClient',
    'LLMMockClient',
    'MockHoundifyError',
    'create_houndify_client',
    'MOCK_TYPE_PATTERN',
    'MOCK_TYPE_LLM',
]
