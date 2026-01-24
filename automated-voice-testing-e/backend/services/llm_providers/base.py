"""
Base LLM Adapter for Ensemble Validation.

This module defines the abstract base class for all LLM provider adapters,
ensuring a consistent interface for response evaluation.

Key Design Decisions:
- LLMs only provide individual scores (0-10) and reasoning
- Overall score and decision are calculated PROGRAMMATICALLY
- This reduces hallucination and ensures consistent scoring
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import logging

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


# =============================================================================
# Pydantic Models for Structured Output Validation
# =============================================================================

class EvaluationScores(BaseModel):
    """Individual evaluation scores from LLM (0-10 scale)."""
    relevance: float = Field(ge=0, le=10, description="How well response addresses request")
    correctness: float = Field(ge=0, le=10, description="Accuracy of information")
    completeness: float = Field(ge=0, le=10, description="How fully it answered")
    tone: float = Field(ge=0, le=10, description="Appropriateness for voice assistant")
    entity_accuracy: float = Field(ge=0, le=10, description="Accuracy of entities mentioned")

    @field_validator('*', mode='before')
    @classmethod
    def clamp_score(cls, v):
        """Ensure scores are within 0-10 range."""
        if isinstance(v, (int, float)):
            return max(0, min(10, float(v)))
        return v


class LLMEvaluationResponse(BaseModel):
    """
    Expected response structure from LLM judges.

    Note: LLM provides ONLY scores and reasoning.
    Overall score and decision are calculated programmatically.
    """
    scores: EvaluationScores
    reasoning: str = Field(max_length=500, description="Brief explanation")


# JSON Schema for providers that support strict structured output (OpenAI)
EVALUATION_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "scores": {
            "type": "object",
            "properties": {
                "relevance": {"type": "number", "minimum": 0, "maximum": 10},
                "correctness": {"type": "number", "minimum": 0, "maximum": 10},
                "completeness": {"type": "number", "minimum": 0, "maximum": 10},
                "tone": {"type": "number", "minimum": 0, "maximum": 10},
                "entity_accuracy": {"type": "number", "minimum": 0, "maximum": 10}
            },
            "required": ["relevance", "correctness", "completeness", "tone", "entity_accuracy"],
            "additionalProperties": False
        },
        "reasoning": {"type": "string", "maxLength": 500}
    },
    "required": ["scores", "reasoning"],
    "additionalProperties": False
}


# =============================================================================
# Evaluation Criteria and Thresholds (Programmatic)
# =============================================================================

EVALUATION_CRITERIA = {
    'relevance': 0.30,      # Does the response address the user's request?
    'correctness': 0.25,    # Is the information accurate?
    'completeness': 0.20,   # Did it answer fully or partially?
    'tone': 0.15,           # Is the response appropriate?
    'entity_accuracy': 0.10 # Are key entities mentioned/correct?
}

# Decision thresholds - applied programmatically, NOT by LLM
PASS_THRESHOLD = 7.0
FAIL_THRESHOLD = 4.0


def calculate_overall_score(scores: Dict[str, float]) -> float:
    """
    Calculate weighted overall score from individual scores.

    This is done PROGRAMMATICALLY to avoid LLM hallucination.

    Args:
        scores: Dictionary of individual scores (0-10)

    Returns:
        Weighted overall score (0-10)
    """
    total = 0.0
    for criterion, weight in EVALUATION_CRITERIA.items():
        score = scores.get(criterion, 0.0)
        # Clamp to valid range
        score = max(0, min(10, float(score)))
        total += score * weight
    return round(total, 2)


def determine_decision(overall_score: float) -> str:
    """
    Determine pass/fail/uncertain based on score thresholds.

    This is done PROGRAMMATICALLY to ensure consistency.

    Args:
        overall_score: Weighted overall score (0-10)

    Returns:
        Decision string: 'pass', 'fail', or 'uncertain'
    """
    if overall_score >= PASS_THRESHOLD:
        return 'pass'
    elif overall_score < FAIL_THRESHOLD:
        return 'fail'
    else:
        return 'uncertain'


# =============================================================================
# Result Dataclass
# =============================================================================

@dataclass
class EvaluationResult:
    """
    Result of an LLM evaluation of a voice AI response.

    Attributes:
        scores: Individual scores for each criterion (0-10)
        overall_score: Weighted overall score (CALCULATED, not from LLM)
        decision: Pass/fail/uncertain (CALCULATED, not from LLM)
        reasoning: Brief explanation from LLM
        raw_response: Full raw response from the LLM
        latency_ms: Response time in milliseconds
        provider: Name of the LLM provider
        model: Name of the model used
    """
    scores: Dict[str, float] = field(default_factory=dict)
    overall_score: float = 0.0
    decision: str = "uncertain"
    reasoning: str = ""
    raw_response: Optional[Dict[str, Any]] = None
    latency_ms: int = 0
    provider: str = ""
    model: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'scores': self.scores,
            'overall_score': self.overall_score,
            'decision': self.decision,
            'reasoning': self.reasoning,
            'raw_response': self.raw_response,
            'latency_ms': self.latency_ms,
            'provider': self.provider,
            'model': self.model,
        }


# =============================================================================
# Evaluation Prompt (No overall_score or decision requested!)
# =============================================================================

def get_evaluation_prompt(
    user_utterance: str,
    ai_response: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate the evaluation prompt for LLM judges.

    This focuses on BEHAVIORAL testing - evaluating whether the AI performed
    the correct action for the user's request, not whether it used exact words.

    IMPORTANT: The prompt only asks for individual scores and reasoning.
    Overall score and decision are calculated programmatically.

    Args:
        user_utterance: What the user said
        ai_response: What the voice AI responded (SpokenResponse)
        context: Additional context (conversation history, step order)

    Returns:
        Formatted evaluation prompt
    """
    # Build conversation history section for multi-turn context
    history_section = ""
    if context and context.get('conversation_history'):
        history = context['conversation_history']
        if history:
            history_lines = ["PREVIOUS CONVERSATION (for context only, do not evaluate):"]
            for i, turn in enumerate(history, 1):
                user_text = turn.get('user', '')
                ai_text = turn.get('ai', '')
                history_lines.append(f"  Turn {i}:")
                history_lines.append(f"    User: {user_text}")
                history_lines.append(f"    AI: {ai_text}")
            history_section = "\n" + "\n".join(history_lines) + "\n"

    # Build context section - only include step order for multi-turn awareness
    context_section = ""
    if context and context.get('step_order') is not None:
        context_section = f"\nCONTEXT: Step {context['step_order']} in multi-turn conversation"

    return f"""Evaluate this voice AI response for BEHAVIORAL correctness.
Focus on whether the AI performed the RIGHT ACTION for the user's request,
not whether it used exact words.
{history_section}
CURRENT TURN TO EVALUATE:
USER REQUEST: {user_utterance}
AI RESPONSE: {ai_response}{context_section}

Score each criterion from 0 to 10:

1. RELEVANCE: Does the response address the user's request?
   - 10: Perfectly addresses the request
   - 7-9: Mostly relevant, correct intent
   - 4-6: Partially relevant
   - 1-3: Mostly irrelevant
   - 0: Completely off-topic or wrong action

2. CORRECTNESS: Is the action/information accurate?
   - 10: Correct action, accurate information
   - 7-9: Right action, mostly correct details
   - 4-6: Partially correct
   - 1-3: Wrong action or mostly incorrect
   - 0: Completely wrong

3. COMPLETENESS: Did it fulfill the request?
   - 10: Fully completed the user's request
   - 7-9: Mostly complete
   - 4-6: Partially complete
   - 1-3: Very incomplete
   - 0: Did not address request

4. TONE: Is the response appropriate for a voice assistant?
   - 10: Natural, helpful, conversational
   - 7-9: Good tone
   - 4-6: Acceptable
   - 1-3: Awkward or inappropriate
   - 0: Completely inappropriate

5. ENTITY_ACCURACY: Are names, numbers, locations, times correct?
   - 10: All entities/details accurate
   - 7-9: Most correct
   - 4-6: Some incorrect
   - 1-3: Most wrong
   - 0: All wrong (or 10 if no entities to check)

Respond with JSON containing ONLY scores and reasoning:
{{
  "scores": {{
    "relevance": <0-10>,
    "correctness": <0-10>,
    "completeness": <0-10>,
    "tone": <0-10>,
    "entity_accuracy": <0-10>
  }},
  "reasoning": "<1-2 sentence explanation of the AI's behavioral performance>"
}}"""


# =============================================================================
# Base Adapter Class
# =============================================================================

class BaseLLMAdapter(ABC):
    """
    Abstract base class for LLM provider adapters.

    All LLM provider adapters must implement the evaluate method
    to ensure consistent behavior across providers.
    """

    provider_name: str = "base"
    default_model: str = ""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        timeout: int = 30
    ):
        """
        Initialize the adapter.

        Args:
            api_key: API key for the provider (uses env var if not provided)
            model: Model name to use (uses default if not provided)
            temperature: Sampling temperature (0.0 for deterministic)
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.model = model or self.default_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self._client = None

    @abstractmethod
    async def _initialize_client(self) -> None:
        """Initialize the provider-specific client."""
        pass

    @abstractmethod
    async def _call_api(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make the actual API call to the LLM provider.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' and 'usage' keys
        """
        pass

    async def evaluate(
        self,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> EvaluationResult:
        """
        Evaluate a voice AI response using this LLM provider.

        Args:
            user_utterance: What the user said
            ai_response: What the voice AI responded
            context: Additional context (conversation history, step order)
            system_prompt: Optional custom system prompt

        Returns:
            EvaluationResult with scores and decision
        """
        import time

        start_time = time.time()

        try:
            if self._client is None:
                await self._initialize_client()

            prompt = get_evaluation_prompt(
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context
            )

            default_system = (
                "You are an expert voice AI evaluator. "
                "Respond with valid JSON only. No markdown, no extra text."
            )

            response = await self._call_api(
                prompt=prompt,
                system_prompt=system_prompt or default_system
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Parse and validate the response
            result = self._parse_response(response['content'])
            result.latency_ms = latency_ms
            result.provider = self.provider_name
            result.model = self.model
            result.raw_response = response

            return result

        except Exception as e:
            logger.error(f"Error evaluating with {self.provider_name}: {e}")
            latency_ms = int((time.time() - start_time) * 1000)

            return EvaluationResult(
                scores={},
                overall_score=0.0,
                decision="uncertain",
                reasoning=f"Evaluation failed: {str(e)}",
                latency_ms=latency_ms,
                provider=self.provider_name,
                model=self.model,
                raw_response={'error': str(e)}
            )

    def _parse_response(self, content: str) -> EvaluationResult:
        """
        Parse the LLM response and calculate scores programmatically.

        The LLM provides only individual scores and reasoning.
        Overall score and decision are calculated here in code.

        Args:
            content: The raw text content from the LLM

        Returns:
            Parsed and validated EvaluationResult
        """
        import json

        try:
            # Clean up the content
            content = content.strip()

            # Handle markdown code blocks
            if content.startswith('```'):
                lines = content.split('\n')
                # Remove first and last lines (```json and ```)
                content = '\n'.join(lines[1:-1] if lines[-1] == '```' else lines[1:])
                content = content.strip()

            # Parse JSON
            data = json.loads(content)

            # Validate with Pydantic
            validated = LLMEvaluationResponse.model_validate(data)

            # Extract scores as dict
            scores = validated.scores.model_dump()

            # PROGRAMMATIC: Calculate overall score
            overall_score = calculate_overall_score(scores)

            # PROGRAMMATIC: Determine decision
            decision = determine_decision(overall_score)

            return EvaluationResult(
                scores=scores,
                overall_score=overall_score,
                decision=decision,
                reasoning=validated.reasoning
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw content: {content[:500]}")
            return EvaluationResult(
                scores={},
                overall_score=0.0,
                decision="uncertain",
                reasoning=f"Failed to parse JSON: {str(e)}"
            )

        except Exception as e:
            logger.warning(f"Failed to validate response: {e}")
            logger.debug(f"Raw content: {content[:500]}")
            return EvaluationResult(
                scores={},
                overall_score=0.0,
                decision="uncertain",
                reasoning=f"Validation failed: {str(e)}"
            )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate plain text content using this LLM provider.

        Unlike evaluate(), this method returns raw text without structured output.
        Used for content generation tasks like KB article creation.

        Args:
            prompt: The user prompt describing what to generate
            system_prompt: Optional system prompt for context
            max_tokens: Optional max tokens override (uses adapter default if not set)

        Returns:
            Generated text content

        Raises:
            Exception: If generation fails
        """
        if self._client is None:
            await self._initialize_client()

        default_system = (
            "You are a helpful assistant that generates clear, well-structured content."
        )

        # Temporarily override max_tokens if specified
        original_max_tokens = self.max_tokens
        if max_tokens is not None:
            self.max_tokens = max_tokens

        try:
            response = await self._call_api_text(
                prompt=prompt,
                system_prompt=system_prompt or default_system
            )
            return response.get('content', '')
        finally:
            # Restore original max_tokens
            self.max_tokens = original_max_tokens

    async def _call_api_text(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        Make API call for plain text generation (no structured output).

        Default implementation calls _call_api. Override in subclasses
        if the provider needs different handling for text vs structured output.

        Args:
            prompt: The user prompt to send
            system_prompt: The system prompt for context

        Returns:
            Dictionary with 'content' key containing generated text
        """
        # Default: use the same call as structured output
        # Subclasses should override if they need different handling
        return await self._call_api(prompt, system_prompt)
