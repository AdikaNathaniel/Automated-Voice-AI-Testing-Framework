"""
Anthropic LLM Adapter for Ensemble Validation.

This module provides the Anthropic-specific implementation for
evaluating voice AI responses using Claude Sonnet 4.5 or other Claude models.

Uses Anthropic's tool use feature to enforce structured JSON output.
"""

import os
import json
import logging
from typing import Any, Dict, Optional

from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)

# Tool definition for structured output via tool use
EVALUATION_TOOL = {
    "name": "submit_evaluation",
    "description": "Submit the evaluation scores and reasoning for the voice AI response",
    "input_schema": {
        "type": "object",
        "properties": {
            "scores": {
                "type": "object",
                "description": "Individual scores for each criterion (0-10)",
                "properties": {
                    "relevance": {
                        "type": "number",
                        "description": "How well the response addresses the request (0-10)"
                    },
                    "correctness": {
                        "type": "number",
                        "description": "Accuracy of information (0-10)"
                    },
                    "completeness": {
                        "type": "number",
                        "description": "How fully it answered (0-10)"
                    },
                    "tone": {
                        "type": "number",
                        "description": "Appropriateness for voice assistant (0-10)"
                    },
                    "entity_accuracy": {
                        "type": "number",
                        "description": "Accuracy of entities mentioned (0-10)"
                    }
                },
                "required": ["relevance", "correctness", "completeness", "tone", "entity_accuracy"]
            },
            "reasoning": {
                "type": "string",
                "description": "Brief 1-2 sentence explanation of the scores"
            }
        },
        "required": ["scores", "reasoning"]
    }
}


class AnthropicAdapter(BaseLLMAdapter):
    """
    Anthropic adapter for LLM ensemble validation.

    Uses the Anthropic API to evaluate voice AI responses with Claude Sonnet 4.5
    or other available models.

    Key Feature: Uses tool use (function calling) to ensure structured output.
    The model is forced to use the tool, guaranteeing the response structure.
    """

    provider_name = "anthropic"
    default_model = "claude-sonnet-4-5-20250929"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30
    ):
        """
        Initialize the Anthropic adapter.

        Args:
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
            model: Model name (default: claude-sonnet-4-5-20250929)
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
        """Initialize the Anthropic async client."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "anthropic package is required for Anthropic adapter. "
                "Install it with: pip install anthropic"
            )

        api_key = self.api_key or os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "Anthropic API key is required. "
                "Set ANTHROPIC_API_KEY environment variable or pass api_key."
            )

        self._async_client = AsyncAnthropic(
            api_key=api_key,
            timeout=float(self.timeout)
        )
        self._client = self._async_client
        logger.debug(f"Initialized Anthropic client with model: {self.model}")

    async def _call_api(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make the API call to Anthropic with tool use for structured output.

        Uses tool_choice="any" to force the model to use our evaluation tool,
        guaranteeing structured output that matches our schema.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        if self._async_client is None:
            await self._initialize_client()

        # Add instruction to use the tool
        enhanced_prompt = (
            f"{prompt}\n\n"
            "Use the submit_evaluation tool to provide your scores and reasoning."
        )

        response = await self._async_client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": enhanced_prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=[EVALUATION_TOOL],
            tool_choice={"type": "tool", "name": "submit_evaluation"}
        )

        # Extract the tool use result
        content = ""
        for block in response.content:
            if hasattr(block, 'type') and block.type == 'tool_use':
                # The tool input is our structured data
                content = json.dumps(block.input)
                break
            elif hasattr(block, 'text'):
                # Fallback to text if no tool use (shouldn't happen with tool_choice)
                content = block.text

        return {
            'content': content,
            'usage': {
                'input_tokens': response.usage.input_tokens if response.usage else 0,
                'output_tokens': response.usage.output_tokens if response.usage else 0,
                'total_tokens': (
                    (response.usage.input_tokens + response.usage.output_tokens)
                    if response.usage else 0
                ),
            },
            'model': response.model,
            'stop_reason': response.stop_reason,
        }

    async def _call_api_text(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make API call for plain text generation (no tool use).

        Unlike _call_api which uses tool use for JSON, this method
        returns plain text suitable for content generation tasks.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' key containing generated text
        """
        if self._async_client is None:
            await self._initialize_client()

        # Plain text generation - no tools
        response = await self._async_client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Extract text content
        content = ""
        for block in response.content:
            if hasattr(block, 'text'):
                content += block.text

        return {
            'content': content,
            'usage': {
                'input_tokens': response.usage.input_tokens if response.usage else 0,
                'output_tokens': response.usage.output_tokens if response.usage else 0,
                'total_tokens': (
                    (response.usage.input_tokens + response.usage.output_tokens)
                    if response.usage else 0
                ),
            },
            'model': response.model,
            'stop_reason': response.stop_reason,
        }
