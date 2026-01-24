"""
Google LLM Adapter for Ensemble Validation.

This module provides the Google-specific implementation for
evaluating voice AI responses using Gemini 1.5 Pro or other Gemini models.

Uses Google's response_schema feature for structured JSON output.
"""

import os
import logging
from typing import Any, Dict, Optional

from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class GoogleAdapter(BaseLLMAdapter):
    """
    Google adapter for LLM ensemble validation.

    Uses the Google Generative AI API to evaluate voice AI responses
    with Gemini 1.5 Pro or other available models.

    Key Feature: Uses response_schema to enforce structured JSON output.
    """

    provider_name = "google"
    default_model = "gemini-1.5-pro"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30
    ):
        """
        Initialize the Google adapter.

        Args:
            api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)
            model: Model name (default: gemini-1.5-pro)
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
        self._generative_model = None

    async def _initialize_client(self) -> None:
        """Initialize the Google Generative AI client with structured output."""
        try:
            import google.generativeai as genai
            from google.generativeai.types import GenerationConfig
        except ImportError:
            raise ImportError(
                "google-generativeai package is required for Google adapter. "
                "Install it with: pip install google-generativeai"
            )

        api_key = self.api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "Google API key is required. "
                "Set GOOGLE_API_KEY environment variable or pass api_key."
            )

        genai.configure(api_key=api_key)

        # Define the response schema for structured output
        # Gemini uses a different schema format
        response_schema = {
            "type": "object",
            "properties": {
                "scores": {
                    "type": "object",
                    "properties": {
                        "relevance": {"type": "number"},
                        "correctness": {"type": "number"},
                        "completeness": {"type": "number"},
                        "tone": {"type": "number"},
                        "entity_accuracy": {"type": "number"}
                    },
                    "required": [
                        "relevance", "correctness", "completeness",
                        "tone", "entity_accuracy"
                    ]
                },
                "reasoning": {"type": "string"}
            },
            "required": ["scores", "reasoning"]
        }

        # Configure generation settings with structured output
        generation_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            response_mime_type="application/json",
            response_schema=response_schema,
        )

        self._generative_model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
        )
        self._client = self._generative_model
        logger.debug(f"Initialized Google client with model: {self.model}")

    async def _call_api(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make the API call to Google Generative AI with structured output.

        Uses response_schema to enforce JSON structure compliance.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        if self._generative_model is None:
            await self._initialize_client()

        # Combine system prompt with user prompt for Gemini
        full_prompt = f"{system_prompt}\n\n{prompt}"

        # Use generate_content_async for async operation
        response = await self._generative_model.generate_content_async(
            full_prompt,
            request_options={"timeout": self.timeout}
        )

        content = response.text if response.text else ""

        # Extract token counts if available
        usage_metadata = getattr(response, 'usage_metadata', None)

        return {
            'content': content,
            'usage': {
                'prompt_tokens': (
                    usage_metadata.prompt_token_count
                    if usage_metadata else 0
                ),
                'completion_tokens': (
                    usage_metadata.candidates_token_count
                    if usage_metadata else 0
                ),
                'total_tokens': (
                    usage_metadata.total_token_count
                    if usage_metadata else 0
                ),
            },
            'model': self.model,
            'finish_reason': (
                response.candidates[0].finish_reason.name
                if response.candidates else 'unknown'
            ),
        }

    async def _call_api_text(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make API call for plain text generation (no schema constraint).

        Unlike _call_api which uses response_schema for JSON, this method
        returns plain text suitable for content generation tasks.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' key containing generated text
        """
        try:
            import google.generativeai as genai
            from google.generativeai.types import GenerationConfig
        except ImportError:
            raise ImportError(
                "google-generativeai package is required for Google adapter. "
                "Install it with: pip install google-generativeai"
            )

        api_key = self.api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError(
                "Google API key is required. "
                "Set GOOGLE_API_KEY environment variable or pass api_key."
            )

        genai.configure(api_key=api_key)

        # Plain text generation config - no response_schema
        generation_config = GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )

        text_model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
        )

        # Combine system prompt with user prompt for Gemini
        full_prompt = f"{system_prompt}\n\n{prompt}"

        response = await text_model.generate_content_async(
            full_prompt,
            request_options={"timeout": self.timeout}
        )

        content = response.text if response.text else ""
        usage_metadata = getattr(response, 'usage_metadata', None)

        return {
            'content': content,
            'usage': {
                'prompt_tokens': (
                    usage_metadata.prompt_token_count
                    if usage_metadata else 0
                ),
                'completion_tokens': (
                    usage_metadata.candidates_token_count
                    if usage_metadata else 0
                ),
                'total_tokens': (
                    usage_metadata.total_token_count
                    if usage_metadata else 0
                ),
            },
            'model': self.model,
            'finish_reason': (
                response.candidates[0].finish_reason.name
                if response.candidates else 'unknown'
            ),
        }
