"""
ConfidenceScorer for aggregating validation scores (TASK-124).

This module provides the ConfidenceScorer class which aggregates scores from
multiple validators using weighted averaging and returns a confidence score
as a percentage (0-100%).

Key Features:
- Weighted average of all validator scores
- Default weights for common validators
- Custom weight configuration
- Score conversion from 0-1 to 0-100%
- Handles missing validator scores gracefully

Example:
    >>> from validators.confidence_scorer import ConfidenceScorer
    >>>
    >>> # Create scorer with default weights
    >>> scorer = ConfidenceScorer()
    >>>
    >>> # Calculate confidence from validator scores
    >>> scores = {
    ...     'intent': 0.9,
    ...     'entity': 0.85,
    ...     'semantic': 0.8,
    ...     'response_time': 1.0
    ... }
    >>> confidence = scorer.calculate(scores)
    >>> print(f"Confidence: {confidence}%")  # ~87.5%
    >>>
    >>> # Use custom weights
    >>> scorer.set_weights({
    ...     'intent': 0.4,
    ...     'entity': 0.3,
    ...     'semantic': 0.2,
    ...     'response_time': 0.1
    ... })
    >>> confidence = scorer.calculate(scores)
    >>> print(f"Confidence: {confidence}%")
"""

from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """
    Aggregator for validation scores with weighted averaging.

    This scorer combines multiple validator scores (each in 0-1 range) into
    a single confidence score (0-100%) using weighted averaging.

    Default weights are balanced across validators:
    - Intent matching: 30%
    - Entity extraction: 30%
    - Semantic similarity: 25%
    - Response time: 15%

    These can be customized based on use case requirements.

    Attributes:
        weights: Dictionary mapping validator names to their weights

    Example:
        >>> scorer = ConfidenceScorer()
        >>>
        >>> # Calculate with default weights
        >>> scores = {
        ...     'intent': 0.9,
        ...     'entity': 0.8,
        ...     'semantic': 0.85,
        ...     'response_time': 1.0
        ... }
        >>> confidence = scorer.calculate(scores)
        >>> print(f"Overall confidence: {confidence:.1f}%")
        >>>
        >>> # Customize weights for specific use case
        >>> scorer.set_weights({
        ...     'intent': 0.5,      # Intent is most important
        ...     'entity': 0.3,      # Entities moderately important
        ...     'semantic': 0.15,   # Semantic less important
        ...     'response_time': 0.05  # Performance least important
        ... })
        >>> confidence = scorer.calculate(scores)
    """

    # Default weights for validators
    DEFAULT_WEIGHTS = {
        'intent': 0.30,           # Intent matching - 30%
        'entity': 0.30,           # Entity extraction - 30%
        'semantic': 0.25,         # Semantic similarity - 25%
        'response_time': 0.15     # Response time - 15%
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize ConfidenceScorer.

        Args:
            weights: Optional custom weights dictionary.
                    Keys are validator names, values are weights (should sum to 1.0)
                    If not provided, uses DEFAULT_WEIGHTS

        Example:
            >>> # Use default weights
            >>> scorer = ConfidenceScorer()
            >>>
            >>> # Use custom weights
            >>> custom_weights = {
            ...     'intent': 0.5,
            ...     'entity': 0.3,
            ...     'semantic': 0.2
            ... }
            >>> scorer = ConfidenceScorer(weights=custom_weights)
        """
        if weights is None:
            self.weights = self.DEFAULT_WEIGHTS.copy()
            logger.info("Initialized with default weights")
        else:
            self.weights = self._normalize_weights(weights)
            logger.info(f"Initialized with custom weights: {self.weights}")

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize weights to ensure they sum to 1.0.

        This handles cases where weights don't sum exactly to 1.0 due to
        rounding or user input. Also ensures all weights are non-negative.

        Args:
            weights: Dictionary of weights to normalize

        Returns:
            Normalized weights dictionary

        Example:
            >>> scorer = ConfidenceScorer()
            >>> weights = {'a': 2.0, 'b': 3.0}  # Sum = 5.0
            >>> normalized = scorer._normalize_weights(weights)
            >>> print(normalized)  # {'a': 0.4, 'b': 0.6}
        """
        # Ensure all weights are non-negative
        clean_weights = {k: max(0.0, v) for k, v in weights.items()}

        # Calculate sum
        total = sum(clean_weights.values())

        if total == 0:
            logger.warning("All weights are zero, using equal weights")
            n = len(clean_weights)
            return {k: 1.0 / n for k in clean_weights.keys()}

        # Normalize to sum to 1.0
        normalized = {k: v / total for k, v in clean_weights.items()}

        logger.debug(f"Normalized weights: {normalized} (original sum: {total})")

        return normalized

    def get_weights(self) -> Dict[str, float]:
        """
        Get current validator weights.

        Returns:
            Dictionary of validator weights

        Example:
            >>> scorer = ConfidenceScorer()
            >>> weights = scorer.get_weights()
            >>> print(weights)
            >>> # {'intent': 0.3, 'entity': 0.3, 'semantic': 0.25, 'response_time': 0.15}
        """
        return self.weights.copy()

    def set_weights(self, weights: Dict[str, float]) -> None:
        """
        Set custom validator weights.

        Weights will be normalized to sum to 1.0 if they don't already.
        Negative weights will be set to 0.

        Args:
            weights: Dictionary mapping validator names to weights

        Example:
            >>> scorer = ConfidenceScorer()
            >>>
            >>> # Prioritize intent matching
            >>> scorer.set_weights({
            ...     'intent': 0.6,
            ...     'entity': 0.2,
            ...     'semantic': 0.15,
            ...     'response_time': 0.05
            ... })
            >>>
            >>> # Weights that don't sum to 1.0 will be normalized
            >>> scorer.set_weights({
            ...     'intent': 3,
            ...     'entity': 2,
            ...     'semantic': 1
            ... })
            >>> weights = scorer.get_weights()
            >>> # Will be normalized to: {'intent': 0.5, 'entity': 0.33, 'semantic': 0.17}
        """
        self.weights = self._normalize_weights(weights)
        logger.info(f"Weights updated: {self.weights}")

    def calculate(self, scores: Optional[Dict[str, float]]) -> float:
        """
        Calculate overall confidence score from validator scores.

        This method:
        1. Takes validator scores (each 0-1 range)
        2. Applies weights to each score
        3. Calculates weighted average
        4. Converts to percentage (0-100%)

        Only validators present in both scores and weights are included.
        Missing validators are ignored (their weight is redistributed).

        Args:
            scores: Dictionary mapping validator names to scores (0-1 range)
                   Example: {'intent': 0.9, 'entity': 0.8}

        Returns:
            Confidence score as percentage (0-100%)

        Example:
            >>> scorer = ConfidenceScorer()
            >>>
            >>> # All validators present
            >>> scores = {
            ...     'intent': 0.9,
            ...     'entity': 0.85,
            ...     'semantic': 0.8,
            ...     'response_time': 1.0
            ... }
            >>> confidence = scorer.calculate(scores)
            >>> print(f"{confidence}%")  # ~87.5%
            >>>
            >>> # Some validators missing
            >>> partial_scores = {
            ...     'intent': 1.0,
            ...     'entity': 0.8
            ... }
            >>> confidence = scorer.calculate(partial_scores)
            >>> print(f"{confidence}%")  # ~90% (weighted avg of available)
            >>>
            >>> # Perfect scores
            >>> perfect = {k: 1.0 for k in scorer.get_weights()}
            >>> confidence = scorer.calculate(perfect)
            >>> print(f"{confidence}%")  # 100%
        """
        if scores is None or not scores:
            logger.warning("No scores provided, returning 0.0")
            return 0.0

        logger.info(f"Calculating confidence from {len(scores)} validator scores")

        # Find validators present in both scores and weights
        available_validators = set(scores.keys()) & set(self.weights.keys())

        if not available_validators:
            logger.warning(
                "No matching validators between scores and weights, "
                "returning 0.0"
            )
            return 0.0

        # Calculate weighted sum and total weight
        weighted_sum = 0.0
        total_weight = 0.0

        for validator in available_validators:
            score = scores[validator]
            weight = self.weights[validator]

            # Clamp score to valid range [0, 1]
            score = max(0.0, min(1.0, score))

            weighted_sum += score * weight
            total_weight += weight

            logger.debug(
                f"Validator '{validator}': score={score:.3f}, "
                f"weight={weight:.3f}, contribution={score * weight:.3f}"
            )

        # Calculate weighted average
        if total_weight == 0:
            logger.warning("Total weight is 0, returning 0.0")
            return 0.0

        weighted_average = weighted_sum / total_weight

        # Convert from 0-1 to 0-100%
        confidence_percentage = weighted_average * 100.0

        logger.info(
            f"Confidence calculated: {confidence_percentage:.2f}% "
            f"(from {len(available_validators)} validators)"
        )

        return float(confidence_percentage)

    def __repr__(self) -> str:
        """
        String representation of ConfidenceScorer.

        Returns:
            String showing number of weights configured

        Example:
            >>> scorer = ConfidenceScorer()
            >>> print(scorer)
            <ConfidenceScorer(weights=4)>
        """
        return f"<ConfidenceScorer(weights={len(self.weights)})>"
