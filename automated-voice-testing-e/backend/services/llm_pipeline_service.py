"""
LLM Pipeline Validation Service.

Three-stage LLM validation pipeline for voice AI testing:
1. Dual Evaluators (Gemini + GPT) - Independent parallel evaluation
2. Curator (Claude) - Tie-breaking when evaluators disagree
3. Decision - Pass/Fail/Human Review based on consensus

This focuses on **behavioral testing** - assessing whether the agent
performed the correct action, not whether it used exact words.

See: backend/services/llm_providers/LLM_VALIDATION_DESIGN.md
"""

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from services.llm_providers import (
    create_evaluator_a,
    create_evaluator_b,
    create_curator,
    EvaluationResult,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration from Environment
# =============================================================================

def get_consensus_threshold() -> float:
    """Get consensus threshold from environment."""
    return float(os.getenv('LLM_CONSENSUS_THRESHOLD', '0.15'))


def get_extreme_disagreement_threshold() -> float:
    """Get extreme disagreement threshold from environment."""
    return float(os.getenv('LLM_EXTREME_DISAGREEMENT_THRESHOLD', '0.40'))


def get_pass_threshold() -> float:
    """Get pass threshold from environment."""
    return float(os.getenv('LLM_PASS_THRESHOLD', '0.80'))


# =============================================================================
# Pipeline Result
# =============================================================================

@dataclass
class PipelineResult:
    """
    Result of the three-stage LLM validation pipeline.

    Attributes:
        final_score: Final score after consensus logic (0.0-1.0)
        final_decision: 'pass', 'fail', or 'needs_review'
        confidence: Confidence level ('high', 'medium', 'low')
        evaluator_a_score: Score from Evaluator A (Gemini)
        evaluator_b_score: Score from Evaluator B (GPT)
        evaluator_a_scores: Individual criterion scores from Evaluator A
        evaluator_b_scores: Individual criterion scores from Evaluator B
        evaluator_a_reasoning: Reasoning from Evaluator A
        evaluator_b_reasoning: Reasoning from Evaluator B
        curator_decision: Curator's tie-breaking decision (if called)
        curator_reasoning: Curator's reasoning (if called)
        score_difference: Absolute difference between evaluator scores
        consensus_type: 'high_consensus', 'curator_resolved', 'human_review'
    """
    final_score: float = 0.0
    final_decision: str = "needs_review"
    confidence: str = "low"
    evaluator_a_score: float = 0.0
    evaluator_b_score: float = 0.0
    evaluator_a_scores: Optional[Dict[str, float]] = None
    evaluator_b_scores: Optional[Dict[str, float]] = None
    evaluator_a_reasoning: str = ""
    evaluator_b_reasoning: str = ""
    curator_decision: Optional[str] = None
    curator_reasoning: Optional[str] = None
    score_difference: float = 0.0
    consensus_type: str = "unknown"
    latency_ms: int = 0
    evaluator_a_latency_ms: int = 0
    evaluator_b_latency_ms: int = 0
    curator_latency_ms: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'final_score': self.final_score,
            'final_decision': self.final_decision,
            'confidence': self.confidence,
            'evaluator_a_score': self.evaluator_a_score,
            'evaluator_b_score': self.evaluator_b_score,
            'evaluator_a_scores': self.evaluator_a_scores,
            'evaluator_b_scores': self.evaluator_b_scores,
            'evaluator_a_reasoning': self.evaluator_a_reasoning,
            'evaluator_b_reasoning': self.evaluator_b_reasoning,
            'curator_decision': self.curator_decision,
            'curator_reasoning': self.curator_reasoning,
            'score_difference': self.score_difference,
            'consensus_type': self.consensus_type,
            'latency_ms': self.latency_ms,
            'evaluator_a_latency_ms': self.evaluator_a_latency_ms,
            'evaluator_b_latency_ms': self.evaluator_b_latency_ms,
            'curator_latency_ms': self.curator_latency_ms,
        }


# =============================================================================
# Pipeline Service
# =============================================================================

class LLMPipelineService:
    """
    Three-stage LLM validation pipeline service.

    Stage 1: Dual Evaluators
        - Evaluator A (Gemini) and B (GPT) run in parallel
        - Each provides a score (0.0-1.0) and reasoning

    Stage 2: Curator (conditional)
        - Only called when evaluators disagree beyond consensus threshold
        - Reviews both evaluations and makes tie-breaking decision
        - Not called for extreme disagreement (goes to human review)

    Stage 3: Decision
        - High consensus: Average the scores
        - Curator resolved: Use curator's decision
        - Extreme disagreement: Flag for human review
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        consensus_threshold: Optional[float] = None,
        extreme_disagreement_threshold: Optional[float] = None,
        pass_threshold: Optional[float] = None,
    ):
        """
        Initialize the pipeline service.

        Args:
            api_key: OpenRouter API key (uses env var if not provided)
            consensus_threshold: Max score diff for high consensus
            extreme_disagreement_threshold: Score diff triggering human review
            pass_threshold: Minimum score to pass
        """
        self.api_key = api_key
        self.consensus_threshold = (
            consensus_threshold or get_consensus_threshold()
        )
        self.extreme_disagreement_threshold = (
            extreme_disagreement_threshold or get_extreme_disagreement_threshold()
        )
        self.pass_threshold = pass_threshold or get_pass_threshold()

        # Lazy-loaded adapters
        self._evaluator_a = None
        self._evaluator_b = None
        self._curator = None

    def _get_evaluator_a(self):
        """Get or create Evaluator A adapter."""
        if self._evaluator_a is None:
            self._evaluator_a = create_evaluator_a(self.api_key)
        return self._evaluator_a

    def _get_evaluator_b(self):
        """Get or create Evaluator B adapter."""
        if self._evaluator_b is None:
            self._evaluator_b = create_evaluator_b(self.api_key)
        return self._evaluator_b

    def _get_curator(self):
        """Get or create Curator adapter."""
        if self._curator is None:
            self._curator = create_curator(self.api_key)
        return self._curator

    async def evaluate(
        self,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> PipelineResult:
        """
        Run the three-stage evaluation pipeline.

        Args:
            user_utterance: What the user said
            ai_response: What the voice AI responded
            context: Additional context (conversation history, step order)

        Returns:
            PipelineResult with scores, decision, and confidence
        """
        import time
        start_time = time.time()

        # Stage 1: Dual Evaluators (parallel)
        eval_a, eval_b = await self._run_dual_evaluators(
            user_utterance=user_utterance,
            ai_response=ai_response,
            context=context,
        )

        # Normalize scores to 0-1 range (evaluators return 0-10)
        score_a = eval_a.overall_score / 10.0
        score_b = eval_b.overall_score / 10.0
        score_diff = abs(score_a - score_b)

        # Stage 2 & 3: Consensus logic
        result = await self._apply_consensus_logic(
            score_a=score_a,
            score_b=score_b,
            score_diff=score_diff,
            eval_a=eval_a,
            eval_b=eval_b,
            user_utterance=user_utterance,
            ai_response=ai_response,
            context=context,
        )

        # Set latencies
        result.evaluator_a_latency_ms = eval_a.latency_ms
        result.evaluator_b_latency_ms = eval_b.latency_ms
        result.latency_ms = int((time.time() - start_time) * 1000)

        logger.info(
            f"Pipeline complete: {result.final_decision} "
            f"(score={result.final_score:.2f}, confidence={result.confidence}, "
            f"type={result.consensus_type})"
        )

        return result

    async def _run_dual_evaluators(
        self,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]],
    ) -> tuple[EvaluationResult, EvaluationResult]:
        """
        Stage 1: Run both evaluators in parallel.

        Returns:
            Tuple of (evaluator_a_result, evaluator_b_result)
        """
        evaluator_a = self._get_evaluator_a()
        evaluator_b = self._get_evaluator_b()

        # Run in parallel
        results = await asyncio.gather(
            evaluator_a.evaluate(
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context,
            ),
            evaluator_b.evaluate(
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context,
            ),
            return_exceptions=True,
        )

        # Handle errors
        eval_a, eval_b = results

        if isinstance(eval_a, Exception):
            logger.error(f"Evaluator A failed: {eval_a}")
            eval_a = EvaluationResult(
                scores={},
                overall_score=0.0,
                decision="uncertain",
                reasoning=f"Evaluator A failed: {str(eval_a)}",
            )

        if isinstance(eval_b, Exception):
            logger.error(f"Evaluator B failed: {eval_b}")
            eval_b = EvaluationResult(
                scores={},
                overall_score=0.0,
                decision="uncertain",
                reasoning=f"Evaluator B failed: {str(eval_b)}",
            )

        return eval_a, eval_b

    async def _apply_consensus_logic(
        self,
        score_a: float,
        score_b: float,
        score_diff: float,
        eval_a: EvaluationResult,
        eval_b: EvaluationResult,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]],
    ) -> PipelineResult:
        """
        Stage 2 & 3: Apply consensus logic and determine decision.

        Logic:
        - score_diff <= consensus_threshold → High consensus, average scores
        - consensus_threshold < score_diff < extreme_threshold → Curator decides
        - score_diff >= extreme_threshold → Human review required
        """
        # Log evaluator scores for debugging
        logger.info(
            f"Evaluator scores: A={score_a:.2f}, B={score_b:.2f}, diff={score_diff:.2f} "
            f"(consensus_threshold={self.consensus_threshold}, extreme_threshold={self.extreme_disagreement_threshold})"
        )

        result = PipelineResult(
            evaluator_a_score=score_a,
            evaluator_b_score=score_b,
            evaluator_a_scores=eval_a.scores if eval_a.scores else None,
            evaluator_b_scores=eval_b.scores if eval_b.scores else None,
            evaluator_a_reasoning=eval_a.reasoning,
            evaluator_b_reasoning=eval_b.reasoning,
            score_difference=score_diff,
        )

        if score_diff <= self.consensus_threshold:
            # HIGH CONSENSUS: Average the scores
            logger.info(f"✓ High consensus detected (diff={score_diff:.2f} <= {self.consensus_threshold}) - averaging scores")
            final_score = (score_a + score_b) / 2
            result.final_score = round(final_score, 4)
            result.confidence = "high"
            result.consensus_type = "high_consensus"
            result.final_decision = self._score_to_decision(final_score)

        elif score_diff < self.extreme_disagreement_threshold:
            # CURATOR NEEDED: Call curator for tie-breaking
            logger.info(f"⚖️  Moderate disagreement detected (diff={score_diff:.2f}) - calling curator for tie-breaking")
            curator_result = await self._call_curator(
                score_a=score_a,
                score_b=score_b,
                eval_a=eval_a,
                eval_b=eval_b,
                user_utterance=user_utterance,
                ai_response=ai_response,
                context=context,
            )
            result.curator_decision = curator_result.decision
            result.curator_reasoning = curator_result.reasoning
            result.curator_latency_ms = curator_result.latency_ms
            logger.info(f"⚖️  Curator decision: {curator_result.decision} (score={curator_result.overall_score}/10)")

            # Use curator's score (normalized)
            final_score = curator_result.overall_score / 10.0
            result.final_score = round(final_score, 4)
            result.confidence = "medium"
            result.consensus_type = "curator_resolved"
            result.final_decision = self._score_to_decision(final_score)

        else:
            # EXTREME DISAGREEMENT: Human review required
            logger.warning(
                f"⚠️  EXTREME disagreement detected (diff={score_diff:.2f} >= {self.extreme_disagreement_threshold}) - "
                f"flagging for human review (curator NOT called due to extreme disagreement)"
            )
            result.final_score = round((score_a + score_b) / 2, 4)
            result.confidence = "low"
            result.consensus_type = "human_review"
            result.final_decision = "needs_review"

        return result

    async def _call_curator(
        self,
        score_a: float,
        score_b: float,
        eval_a: EvaluationResult,
        eval_b: EvaluationResult,
        user_utterance: str,
        ai_response: str,
        context: Optional[Dict[str, Any]],
    ) -> EvaluationResult:
        """
        Call the curator LLM for tie-breaking.

        The curator receives both evaluations and must determine
        which one is more accurate.
        """
        curator = self._get_curator()

        # Build curator context with both evaluations
        curator_context = {
            **(context or {}),
            'evaluator_a': {
                'score': score_a,
                'reasoning': eval_a.reasoning,
                'scores': eval_a.scores,
            },
            'evaluator_b': {
                'score': score_b,
                'reasoning': eval_b.reasoning,
                'scores': eval_b.scores,
            },
            'score_difference': abs(score_a - score_b),
        }

        # Custom system prompt for curator
        curator_system = (
            "You are a senior QA expert reviewing conflicting evaluations. "
            "Two evaluators assessed a voice AI response and disagreed. "
            "Review both evaluations and provide your own independent assessment. "
            "Focus on which evaluation more accurately captures the AI's performance. "
            "Respond with valid JSON only. No markdown, no extra text."
        )

        return await curator.evaluate(
            user_utterance=user_utterance,
            ai_response=ai_response,
            context=curator_context,
            system_prompt=curator_system,
        )

    def _score_to_decision(self, score: float) -> str:
        """
        Convert a score to a decision.

        Args:
            score: Score between 0.0 and 1.0

        Returns:
            'pass' if score >= pass_threshold, else 'fail'
        """
        if score >= self.pass_threshold:
            return "pass"
        return "fail"


# =============================================================================
# Convenience Functions
# =============================================================================

async def run_llm_pipeline(
    user_utterance: str,
    ai_response: str,
    context: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None,
) -> PipelineResult:
    """
    Run the LLM validation pipeline with default configuration.

    This is a convenience function for simple usage.

    Args:
        user_utterance: What the user said
        ai_response: What the voice AI responded
        context: Additional context (conversation history, step order)
        api_key: OpenRouter API key (uses env var if not provided)

    Returns:
        PipelineResult with scores and decision
    """
    service = LLMPipelineService(api_key=api_key)
    return await service.evaluate(
        user_utterance=user_utterance,
        ai_response=ai_response,
        context=context,
    )
