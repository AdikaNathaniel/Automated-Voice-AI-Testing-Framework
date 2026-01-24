"""
OpenRouter LLM Adapter for Ensemble Validation.

This module provides the OpenRouter-specific implementation for
accessing multiple LLM providers (OpenAI, Anthropic, Google, etc.)
through a unified API.

OpenRouter provides an OpenAI-compatible API that routes to 400+ models.
See: https://openrouter.ai/docs
"""

import os
import logging
from typing import Any, Dict, Optional

from .base import BaseLLMAdapter, EVALUATION_JSON_SCHEMA

logger = logging.getLogger(__name__)


class OpenRouterAdapter(BaseLLMAdapter):
    """
    OpenRouter adapter for LLM ensemble validation.

    Uses the OpenRouter API (OpenAI-compatible) to access multiple
    LLM providers through a single endpoint. Supports:
    - Google models (Gemini)
    - OpenAI models (GPT)
    - Anthropic models (Claude)
    - And 400+ other models

    Key Features:
    - Unified API for all providers
    - Automatic fallback handling
    - Cost tracking per request
    """

    provider_name = "openrouter"
    default_model = "google/gemini-2.5-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30,
        base_url: Optional[str] = None,
    ):
        """
        Initialize the OpenRouter adapter.

        Args:
            api_key: OpenRouter API key (uses OPENROUTER_API_KEY env var if not provided)
            model: Model ID (e.g., 'google/gemini-2.5-flash')
            temperature: Sampling temperature (default: 0.0 for deterministic)
            max_tokens: Maximum tokens in response (default: 1024)
            timeout: Request timeout in seconds (default: 30)
            base_url: OpenRouter API base URL (default: https://openrouter.ai/api/v1)
        """
        super().__init__(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        self.base_url = base_url or os.getenv(
            'OPENROUTER_BASE_URL',
            'https://openrouter.ai/api/v1'
        )
        self._async_client = None

    async def _initialize_client(self) -> None:
        """Initialize the OpenAI-compatible async client for OpenRouter."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package is required for OpenRouter adapter. "
                "Install it with: pip install openai"
            )

        api_key = self.api_key or os.getenv('OPENROUTER_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenRouter API key is required. "
                "Set OPENROUTER_API_KEY environment variable or pass api_key."
            )

        self._async_client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
            timeout=float(self.timeout),
            default_headers={
                "HTTP-Referer": os.getenv('APP_URL', 'http://localhost:8000'),
                "X-Title": os.getenv('APP_NAME', 'Voice AI Testing Framework'),
            }
        )
        self._client = self._async_client
        logger.debug(
            f"Initialized OpenRouter client with model: {self.model}, "
            f"base_url: {self.base_url}"
        )

    async def _call_api(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make the API call to OpenRouter.

        OpenRouter is OpenAI-compatible, so we use the same API format.
        Note: Not all models support structured outputs, so we use JSON mode
        where available and fall back to regular completion.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        if self._async_client is None:
            await self._initialize_client()

        # Determine if model supports structured output
        # OpenAI models support it, others may not
        supports_structured = self._supports_structured_output()

        try:
            if supports_structured:
                response = await self._call_with_structured_output(
                    prompt, system_prompt
                )
            else:
                response = await self._call_with_json_mode(prompt, system_prompt)

            content = response.choices[0].message.content or ""

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    'completion_tokens': (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                    'total_tokens': (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise

    async def _call_with_structured_output(
        self,
        prompt: str,
        system_prompt: str
    ):
        """Call API with structured output (OpenAI models only)."""
        return await self._async_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "evaluation_response",
                    "strict": True,
                    "schema": EVALUATION_JSON_SCHEMA
                }
            }
        )

    async def _call_with_json_mode(self, prompt: str, system_prompt: str):
        """Call API with JSON mode (more widely supported)."""
        # Add JSON instruction to system prompt for non-OpenAI models
        enhanced_system = (
            f"{system_prompt}\n\n"
            "IMPORTANT: Respond with valid JSON only. No markdown, no extra text."
        )

        return await self._async_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": enhanced_system},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def _supports_structured_output(self) -> bool:
        """
        Check if the model supports structured output.

        Currently only OpenAI models fully support json_schema response format.
        """
        openai_prefixes = ('openai/', 'gpt-')
        return self.model.lower().startswith(openai_prefixes)

    async def _call_api_text(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make API call for plain text generation (no JSON mode).

        This override ensures that text generation (like KB articles) gets
        pure markdown without JSON wrapping.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' key containing generated text
        """
        if self._async_client is None:
            await self._initialize_client()

        try:
            # Call API with regular completion (NO JSON mode enforcement)
            response = await self._async_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            content = response.choices[0].message.content or ""

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': (
                        response.usage.prompt_tokens if response.usage else 0
                    ),
                    'completion_tokens': (
                        response.usage.completion_tokens if response.usage else 0
                    ),
                    'total_tokens': (
                        response.usage.total_tokens if response.usage else 0
                    ),
                },
                'model': response.model,
                'finish_reason': response.choices[0].finish_reason,
            }

        except Exception as e:
            logger.error(f"OpenRouter text generation error: {e}")
            raise


# Factory functions for common configurations

def create_evaluator_a(api_key: Optional[str] = None) -> OpenRouterAdapter:
    """
    Create Evaluator A adapter with configured model.

    Uses LLM_EVALUATOR_A_MODEL from environment or default.
    Default: google/gemini-2.5-flash (fast, cost-effective reasoning model)
    """
    model = os.getenv('LLM_EVALUATOR_A_MODEL', 'google/gemini-2.5-flash')
    return OpenRouterAdapter(
        api_key=api_key,
        model=model,
        temperature=float(os.getenv('LLM_TEMPERATURE', '0.0')),
        max_tokens=int(os.getenv('LLM_MAX_TOKENS', '1024')),
        timeout=int(os.getenv('LLM_TIMEOUT', '30')),
    )


def create_evaluator_b(api_key: Optional[str] = None) -> OpenRouterAdapter:
    """
    Create Evaluator B adapter with configured model.

    Uses LLM_EVALUATOR_B_MODEL from environment or default.
    Default: openai/gpt-4.1-mini (fast, cost-effective OpenAI model)
    """
    model = os.getenv('LLM_EVALUATOR_B_MODEL', 'openai/gpt-4.1-mini')
    return OpenRouterAdapter(
        api_key=api_key,
        model=model,
        temperature=float(os.getenv('LLM_TEMPERATURE', '0.0')),
        max_tokens=int(os.getenv('LLM_MAX_TOKENS', '1024')),
        timeout=int(os.getenv('LLM_TIMEOUT', '30')),
    )


def create_curator(api_key: Optional[str] = None) -> OpenRouterAdapter:
    """
    Create Curator adapter with configured model.

    Uses LLM_CURATOR_MODEL from environment or default.
    Default: anthropic/claude-sonnet-4.5 (balanced reasoning for tie-breaking)
    """
    model = os.getenv('LLM_CURATOR_MODEL', 'anthropic/claude-sonnet-4.5')
    return OpenRouterAdapter(
        api_key=api_key,
        model=model,
        temperature=float(os.getenv('LLM_TEMPERATURE', '0.0')),
        max_tokens=int(os.getenv('LLM_MAX_TOKENS', '1024')),
        timeout=int(os.getenv('LLM_TIMEOUT', '30')),
    )
