"""
LLM Ensemble Validation Mixin

This module provides the ValidationLLMMixin class which implements
LLM ensemble validation for voice AI responses.

Key Features:
- Three-stage LLM pipeline validation (Dual Evaluators + Curator)
- Support for houndify, llm_ensemble, and hybrid validation modes
- Integration with OpenRouter API for multi-model evaluation
- Consensus-based scoring with configurable thresholds

Example:
    >>> from services.validation_llm import ValidationLLMMixin
    >>>
    >>> class MyValidator(ValidationLLMMixin):
    ...     pass
    >>>
    >>> validator = MyValidator()
    >>> result = await validator._run_llm_pipeline_validation(
    ...     user_utterance="What's the weather?",
    ...     ai_response="It's sunny and 75 degrees"
    ... )
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, TYPE_CHECKING

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from services.llm_pipeline_service import PipelineResult


class ValidationLLMMixin:
    """
    Mixin providing LLM ensemble validation methods.

    This mixin adds LLM-based validation capabilities to ValidationService,
    implementing the three-stage pipeline:
    1. Dual Evaluators (Gemini + GPT)
    2. Curator (Claude) for tie-breaking
    3. Decision (pass/fail/needs_review)
    """

    def _is_llm_validation_enabled(self) -> bool:
        """
        Check if LLM ensemble validation is enabled.

        Returns:
            True if enabled (via environment variable)

        Example:
            >>> if self._is_llm_validation_enabled():
            ...     result = await self._run_llm_pipeline_validation(...)
        """
        enabled = os.getenv('ENABLE_LLM_ENSEMBLE_VALIDATION', 'false').lower()
        return enabled in ('true', '1', 'yes')

    def _get_default_validation_mode(self) -> str:
        """
        Get the default validation mode from environment.

        Returns:
            Validation mode: 'houndify', 'llm_ensemble', or 'hybrid'

        Example:
            >>> mode = self._get_default_validation_mode()
            >>> print(mode)  # 'hybrid'
        """
        return os.getenv('DEFAULT_VALIDATION_MODE', 'hybrid')

    async def _run_llm_pipeline_validation(
        self,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> "PipelineResult":
        """
        Run the three-stage LLM validation pipeline.

        This method orchestrates the dual evaluators (Gemini + GPT) and
        curator (Claude) to evaluate the AI response behaviorally.

        Args:
            user_utterance: What the user said
            ai_response: What the voice AI responded
            context: Additional context (conversation history, step order)

        Returns:
            PipelineResult with scores, decision, and confidence

        Example:
            >>> result = await self._run_llm_pipeline_validation(
            ...     user_utterance="Navigate to coffee shop",
            ...     ai_response="Navigating to Starbucks, 2 miles away",
            ...     context={"step_order": 1}
            ... )
            >>> print(result.final_decision)  # 'pass'
        """
        try:
            from services.llm_pipeline_service import LLMPipelineService

            service = LLMPipelineService()
            result = await service.evaluate(
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context,
            )

            logger.info(
                f"LLM pipeline validation complete: "
                f"decision={result.final_decision}, "
                f"score={result.final_score:.2f}, "
                f"confidence={result.confidence}, "
                f"type={result.consensus_type}"
            )

            return result

        except Exception as e:
            logger.error(
                f"LLM pipeline validation failed: {e}",
                exc_info=True
            )
            # Return a failed result for safety
            from services.llm_pipeline_service import PipelineResult
            return PipelineResult(
                final_score=0.0,
                final_decision="needs_review",
                confidence="low",
                consensus_type="error",
                evaluator_a_reasoning=f"Pipeline error: {str(e)}",
                evaluator_b_reasoning="",
            )

    def _build_llm_context(
        self,
        expected_command_kind: Optional[str] = None,
        expected_entities: Optional[Dict[str, Any]] = None,
        houndify_data: Optional[Dict[str, Any]] = None,
        transcript: Optional[str] = None,
        scenario_name: Optional[str] = None,
        step_order: Optional[int] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """
        Build context dictionary for LLM evaluation.

        Combines all available validation context into a single
        dictionary for the LLM evaluators. Includes conversation
        history for multi-turn scenarios.

        Args:
            expected_command_kind: Expected CommandKind from Houndify
            expected_entities: Expected entities from ExpectedOutcome
            houndify_data: Full Houndify response data
            transcript: Actual transcript from execution
            scenario_name: Name of the scenario being tested
            step_order: Step number in multi-turn scenario (1-indexed)
            conversation_history: Previous turns for context (not evaluated)
                Each entry: {"user": "...", "ai": "..."}

        Returns:
            Context dictionary for LLM evaluators

        Example:
            >>> context = self._build_llm_context(
            ...     expected_command_kind="RestaurantReservationCommand",
            ...     step_order=3,
            ...     conversation_history=[
            ...         {"user": "Make a reservation", "ai": "For how many people?"},
            ...         {"user": "4 people", "ai": "What date and time?"},
            ...     ]
            ... )
        """
        context: Dict[str, Any] = {}

        if expected_command_kind:
            context['expected_command_kind'] = expected_command_kind

        if expected_entities:
            context['expected_entities'] = expected_entities

        if houndify_data:
            # Extract relevant parts of Houndify response
            context['houndify_response'] = {
                'command_kind': self._extract_command_kind(houndify_data)
                if hasattr(self, '_extract_command_kind') else None,
                'asr_confidence': self._extract_asr_confidence(houndify_data)
                if hasattr(self, '_extract_asr_confidence') else None,
            }

        if transcript:
            context['actual_transcript'] = transcript

        if scenario_name:
            context['scenario_name'] = scenario_name

        if step_order is not None:
            context['step_order'] = step_order

        # Include conversation history for multi-turn context
        # This helps LLM understand references like "yes", "confirm that", etc.
        if conversation_history:
            context['conversation_history'] = conversation_history

        return context

    def _compute_combined_decision(
        self,
        houndify_passed: Optional[bool],
        llm_decision: str,
        llm_score: float,
        validation_mode: str,
    ) -> str:
        """
        Compute the final combined decision from Houndify and LLM results.

        Decision logic varies by validation mode:
        - houndify: Use Houndify result only
        - llm_ensemble: Use LLM result only
        - hybrid: Combine both (agreement required)

        Args:
            houndify_passed: Whether Houndify validation passed
            llm_decision: LLM's decision (pass/fail/needs_review)
            llm_score: LLM's final score (0.0-1.0)
            validation_mode: 'houndify', 'llm_ensemble', or 'hybrid'

        Returns:
            Final decision: 'pass', 'fail', or 'uncertain'

        Example:
            >>> decision = self._compute_combined_decision(
            ...     houndify_passed=True,
            ...     llm_decision="pass",
            ...     llm_score=0.85,
            ...     validation_mode="hybrid"
            ... )
            >>> print(decision)  # 'pass'
        """
        if validation_mode == 'houndify':
            # Houndify only
            if houndify_passed is None:
                return 'uncertain'
            return 'pass' if houndify_passed else 'fail'

        if validation_mode == 'llm_ensemble':
            # LLM only
            if llm_decision == 'needs_review':
                return 'uncertain'
            return llm_decision

        # Hybrid mode - combine both
        llm_passed = llm_decision == 'pass'

        # If LLM is uncertain, needs human review
        if llm_decision == 'needs_review':
            return 'uncertain'

        # If Houndify didn't run, use LLM decision
        if houndify_passed is None:
            return llm_decision

        # Both ran - check agreement
        if houndify_passed and llm_passed:
            return 'pass'
        elif not houndify_passed and not llm_passed:
            return 'fail'
        else:
            # Disagreement - needs human review
            logger.info(
                f"Houndify/LLM disagreement: houndify={houndify_passed}, "
                f"llm={llm_decision}, flagging for review"
            )
            return 'uncertain'

    def _compute_review_status(
        self,
        final_decision: str,
        llm_confidence: str,
    ) -> str:
        """
        Compute the review status from final decision and confidence.

        Args:
            final_decision: 'pass', 'fail', or 'uncertain'
            llm_confidence: 'high', 'medium', or 'low'

        Returns:
            Review status: 'auto_pass', 'auto_fail', or 'needs_review'

        Example:
            >>> status = self._compute_review_status(
            ...     final_decision='pass',
            ...     llm_confidence='high'
            ... )
            >>> print(status)  # 'auto_pass'
        """
        if final_decision == 'uncertain':
            return 'needs_review'

        # Low confidence always needs review
        if llm_confidence == 'low':
            return 'needs_review'

        if final_decision == 'pass':
            return 'auto_pass'
        elif final_decision == 'fail':
            return 'auto_fail'
        else:
            return 'needs_review'
