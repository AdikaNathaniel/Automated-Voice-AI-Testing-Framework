"""
OpenAI LLM Adapter for Ensemble Validation.

This module provides the OpenAI-specific implementation for
evaluating voice AI responses using GPT-4o or other OpenAI models.

Uses OpenAI's Structured Outputs feature for GUARANTEED JSON schema compliance.
See: https://platform.openai.com/docs/guides/structured-outputs
"""

import os
import logging
from typing import Any, Dict, Optional

from .base import BaseLLMAdapter, EVALUATION_JSON_SCHEMA

logger = logging.getLogger(__name__)


class OpenAIAdapter(BaseLLMAdapter):
    """
    OpenAI adapter for LLM ensemble validation.

    Uses the OpenAI API to evaluate voice AI responses with GPT-4o
    or other available models.

    Key Feature: Uses Structured Outputs (response_format with json_schema)
    to GUARANTEE the response matches our expected schema. The model will
    ALWAYS return valid JSON matching the schema - no parsing failures.
    """

    provider_name = "openai"
    default_model = "gpt-4o"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30
    ):
        """
        Initialize the OpenAI adapter.

        Args:
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
            model: Model name (default: gpt-4o)
            temperature: Sampling temperature (default: 0.0 for deterministic)
            max_tokens: Maximum tokens in response (default: 1024)
            timeout: Request timeout in seconds (default: 30)
        """
        super().__init__(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        self._async_client = None

    async def _initialize_client(self) -> None:
        """Initialize the OpenAI async client."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package is required for OpenAI adapter. "
                "Install it with: pip install openai"
            )

        api_key = self.api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key is required. "
                "Set OPENAI_API_KEY environment variable or pass api_key."
            )

        self._async_client = AsyncOpenAI(
            api_key=api_key,
            timeout=float(self.timeout)
        )
        self._client = self._async_client
        logger.debug(f"Initialized OpenAI client with model: {self.model}")

    async def _call_api(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make the API call to OpenAI with Structured Outputs.

        Uses response_format with json_schema to GUARANTEE the response
        matches our expected schema. This eliminates JSON parsing errors.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        if self._async_client is None:
            await self._initialize_client()

        # Use Structured Outputs for guaranteed schema compliance
        # See: https://platform.openai.com/docs/guides/structured-outputs
        response = await self._async_client.chat.completions.create(
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

        content = response.choices[0].message.content or ""

        return {
            'content': content,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'completion_tokens': (
                    response.usage.completion_tokens if response.usage else 0
                ),
                'total_tokens': response.usage.total_tokens if response.usage else 0,
            },
            'model': response.model,
            'finish_reason': response.choices[0].finish_reason,
        }

    async def _call_api_text(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make API call for plain text generation (no structured output).

        Unlike _call_api which uses Structured Outputs for JSON, this method
        returns plain text suitable for content generation tasks.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' key containing generated text
        """
        if self._async_client is None:
            await self._initialize_client()

        # Plain text generation - no response_format constraint
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
                'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                'completion_tokens': (
                    response.usage.completion_tokens if response.usage else 0
                ),
                'total_tokens': response.usage.total_tokens if response.usage else 0,
            },
            'model': response.model,
            'finish_reason': response.choices[0].finish_reason,
        }
