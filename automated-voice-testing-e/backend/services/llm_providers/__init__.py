"""
LLM Provider Adapters for Ensemble Validation.

This module provides provider-agnostic adapters for various LLM services
used in ensemble validation. Each adapter implements the same interface
for evaluating voice AI responses.

Supported providers:
- OpenRouter (unified access to 400+ models) - RECOMMENDED
- OpenAI (GPT-4o)
- Anthropic (Claude 3.5 Sonnet)
- Google (Gemini 1.5 Pro)

For ensemble validation, use OpenRouter with the factory functions:
- create_evaluator_a(): Google Gemini for primary evaluation
- create_evaluator_b(): OpenAI GPT for secondary evaluation
- create_curator(): Anthropic Claude for tie-breaking

API Key Resolution:
1. Explicit api_key parameter
2. Database configuration (LLMProviderConfig)
3. Environment variable (OPENROUTER_API_KEY, OPENAI_API_KEY, etc.)
"""

import logging
from typing import Optional, Any, Dict
from uuid import UUID

from sqlalchemy.orm import Session

from .base import BaseLLMAdapter, EvaluationResult
from .openai_adapter import OpenAIAdapter
from .anthropic_adapter import AnthropicAdapter
from .google_adapter import GoogleAdapter
from .openrouter_adapter import (
    OpenRouterAdapter,
    create_evaluator_a,
    create_evaluator_b,
    create_curator,
)

logger = logging.getLogger(__name__)

__all__ = [
    # Base classes
    'BaseLLMAdapter',
    'EvaluationResult',
    # Direct provider adapters
    'OpenAIAdapter',
    'AnthropicAdapter',
    'GoogleAdapter',
    # OpenRouter (unified access)
    'OpenRouterAdapter',
    # Ensemble factory functions
    'create_evaluator_a',
    'create_evaluator_b',
    'create_curator',
    # Legacy factory functions
    'get_adapter',
    'get_adapter_with_db_config',
]


def get_adapter(provider: str, **kwargs: Any) -> BaseLLMAdapter:
    """
    Factory function to get the appropriate adapter for a provider.

    This version creates an adapter that will use environment variables
    for API keys. For database-configured keys, use get_adapter_with_db_config.

    Args:
        provider: The LLM provider name (openai, anthropic, google, openrouter)
        **kwargs: Additional arguments to pass to the adapter

    Returns:
        An instance of the appropriate adapter

    Raises:
        ValueError: If the provider is not supported
    """
    adapters = {
        'openai': OpenAIAdapter,
        'anthropic': AnthropicAdapter,
        'google': GoogleAdapter,
        'openrouter': OpenRouterAdapter,
    }

    provider_lower = provider.lower()
    if provider_lower not in adapters:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {list(adapters.keys())}"
        )

    return adapters[provider_lower](**kwargs)


def get_adapter_with_db_config(
    provider: str,
    db: Session,
    tenant_id: Optional[UUID] = None,
    **kwargs: Any
) -> BaseLLMAdapter:
    """
    Get an adapter with configuration loaded from the database.

    This function first tries to load API key and settings from the database
    (LLMProviderConfig), then falls back to environment variables if not found.

    Args:
        provider: The LLM provider name (openai, anthropic, google)
        db: SQLAlchemy session for database access
        tenant_id: Optional tenant ID for multi-tenant isolation
        **kwargs: Additional arguments (override database config)

    Returns:
        An instance of the appropriate adapter configured with DB settings

    Raises:
        ValueError: If the provider is not supported
    """
    from services.llm_provider_config_service import LLMProviderConfigService

    adapters = {
        'openai': OpenAIAdapter,
        'anthropic': AnthropicAdapter,
        'google': GoogleAdapter,
    }

    provider_lower = provider.lower()
    if provider_lower not in adapters:
        raise ValueError(
            f"Unsupported provider: {provider}. "
            f"Supported providers: {list(adapters.keys())}"
        )

    # Try to get config from database
    service = LLMProviderConfigService(db)
    config = service.get_active_config(provider_lower, tenant_id)

    adapter_kwargs: Dict[str, Any] = {}

    if config:
        # Use database configuration
        api_key = config.get_api_key()
        if api_key:
            adapter_kwargs['api_key'] = api_key

        if config.default_model:
            adapter_kwargs['model'] = config.default_model

        adapter_kwargs['temperature'] = config.temperature
        adapter_kwargs['max_tokens'] = int(config.max_tokens)
        adapter_kwargs['timeout'] = int(config.timeout_seconds)

        logger.debug(
            f"Using database config for {provider}: "
            f"model={config.default_model}, display_name={config.display_name}"
        )
    else:
        logger.debug(
            f"No database config for {provider}, using environment variables"
        )

    # Override with any explicit kwargs
    adapter_kwargs.update(kwargs)

    return adapters[provider_lower](**adapter_kwargs)


async def get_adapter_with_db_config_async(
    provider: str,
    db_session,  # AsyncSession
    tenant_id: Optional[UUID] = None,
    **kwargs: Any
) -> BaseLLMAdapter:
    """
    Async version of get_adapter_with_db_config.

    Args:
        provider: The LLM provider name (openai, anthropic, google)
        db_session: Async SQLAlchemy session
        tenant_id: Optional tenant ID for multi-tenant isolation
        **kwargs: Additional arguments (override database config)

    Returns:
        An instance of the appropriate adapter configured with DB settings
    """
    def _sync_get_adapter(sync_session):
        return get_adapter_with_db_config(
            provider=provider,
            db=sync_session,
            tenant_id=tenant_id,
            **kwargs
        )

    return await db_session.run_sync(_sync_get_adapter)
