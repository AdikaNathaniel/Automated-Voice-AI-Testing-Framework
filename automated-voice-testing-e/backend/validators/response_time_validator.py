"""
ResponseTimeValidator for validating response time performance (TASK-122).

This module provides the ResponseTimeValidator class which validates voice AI
response times by comparing actual response times against expected thresholds
and calculating P95 (95th percentile) metrics.

Key Features:
- Threshold comparison (actual vs expected)
- P95 (95th percentile) calculation for multiple measurements
- Score calculation based on performance
- Support for single or multiple response time measurements
- Returns confidence scores (0.0 to 1.0)

Example:
    >>> from validators.response_time_validator import ResponseTimeValidator
    >>>
    >>> # Create validator
    >>> validator = ResponseTimeValidator()
    >>>
    >>> # Single response time
    >>> score = validator.validate(150, threshold=200)
    >>> print(score)  # 1.0 (within threshold)
    >>>
    >>> # Multiple response times (uses P95)
    >>> times = [100, 150, 180, 200, 250]
    >>> score = validator.validate(times, threshold=300)
    >>> print(score)  # High score (P95 is 250, within 300ms)
"""

from typing import Union, List
import logging

logger = logging.getLogger(__name__)


class ResponseTimeValidator:
    """
    Validator for response time performance with threshold and P95 support.

    This validator checks response time performance by:
    1. Comparing single response times against thresholds
    2. Calculating P95 (95th percentile) for multiple measurements
    3. Scoring based on how response time compares to threshold

    The validator returns a confidence score from 0.0 to 1.0, where:
    - 1.0 = excellent performance (well within threshold)
    - 0.0 = poor performance (far exceeding threshold)

    Example:
        >>> validator = ResponseTimeValidator()
        >>>
        >>> # Single measurement
        >>> score = validator.validate(150, threshold=200)
        >>> assert score == 1.0  # Fast response
        >>>
        >>> # Multiple measurements
        >>> times = [50, 100, 150, 200, 250]
        >>> score = validator.validate(times, threshold=300)
        >>> print(f"Performance score: {score:.2f}")
        >>>
        >>> # Calculate P95
        >>> p95 = validator.calculate_p95(times)
        >>> print(f"P95: {p95}ms")
    """

    def __init__(self):
        """
        Initialize ResponseTimeValidator.

        Example:
            >>> validator = ResponseTimeValidator()
            >>> assert validator is not None
        """
        logger.info("ResponseTimeValidator initialized")

    def check_threshold(
        self,
        actual: Union[int, float],
        threshold: Union[int, float]
    ) -> bool:
        """
        Check if response time is within threshold.

        Simple boolean check: actual <= threshold.

        Args:
            actual: Actual response time in milliseconds
            threshold: Expected maximum response time in milliseconds

        Returns:
            True if within threshold, False otherwise

        Example:
            >>> validator = ResponseTimeValidator()
            >>>
            >>> # Within threshold
            >>> validator.check_threshold(150, 200)
            True
            >>>
            >>> # At threshold
            >>> validator.check_threshold(200, 200)
            True
            >>>
            >>> # Exceeds threshold
            >>> validator.check_threshold(250, 200)
            False
        """
        within_threshold = actual <= threshold

        logger.debug(
            f"Threshold check: {actual}ms vs {threshold}ms = {within_threshold}"
        )

        return within_threshold

    def calculate_p95(self, response_times: List[Union[int, float]]) -> float:
        """
        Calculate P95 (95th percentile) of response times.

        P95 represents the response time below which 95% of measurements fall.
        This is a standard performance metric that helps identify outliers.

        Args:
            response_times: List of response times in milliseconds

        Returns:
            P95 value in milliseconds

        Raises:
            ValueError: If response_times is empty

        Example:
            >>> validator = ResponseTimeValidator()
            >>>
            >>> # Simple case
            >>> times = [100, 200, 300, 400, 500]
            >>> p95 = validator.calculate_p95(times)
            >>> print(p95)  # 500
            >>>
            >>> # Larger dataset
            >>> times = list(range(1, 101))  # 1 to 100
            >>> p95 = validator.calculate_p95(times)
            >>> print(f"P95: {p95}")  # Around 95
            >>>
            >>> # Unsorted values
            >>> times = [500, 100, 300, 200, 400]
            >>> p95 = validator.calculate_p95(times)
            >>> print(p95)  # 500 (automatically sorted)
        """
        if not response_times:
            raise ValueError("Cannot calculate P95 of empty list")

        # Sort the response times
        sorted_times = sorted(response_times)

        # Calculate P95 index
        # P95 means 95% of values are below this point
        n = len(sorted_times)

        if n == 1:
            p95_value = sorted_times[0]
        else:
            # Calculate the index for 95th percentile
            # Using nearest-rank method
            index = int(0.95 * n)

            # Ensure index is within bounds
            if index >= n:
                index = n - 1

            p95_value = sorted_times[index]

        logger.debug(
            f"P95 calculation: n={n}, index={int(0.95 * n)}, "
            f"P95={p95_value}ms"
        )

        return float(p95_value)

    def validate(
        self,
        actual: Union[int, float, List[Union[int, float]]],
        threshold: Union[int, float]
    ) -> float:
        """
        Validate response time performance against threshold.

        Behavior:
        - Single value: Direct comparison with threshold
        - Multiple values: Calculate P95 and compare with threshold

        Scoring:
        - If within threshold: Score based on how far below threshold
        - If exceeds threshold: Score based on how far above threshold

        Args:
            actual: Single response time or list of response times (ms)
            threshold: Expected maximum response time (ms)

        Returns:
            Confidence score from 0.0 to 1.0:
            - 1.0 = excellent (0ms or well within threshold)
            - 0.5 = at threshold
            - 0.0 = poor (far exceeding threshold)

        Example:
            >>> validator = ResponseTimeValidator()
            >>>
            >>> # Single time within threshold
            >>> score = validator.validate(150, 200)
            >>> assert score == 1.0
            >>>
            >>> # Single time exceeds threshold
            >>> score = validator.validate(250, 200)
            >>> assert score < 1.0
            >>>
            >>> # Multiple times
            >>> times = [100, 150, 180, 200, 220]
            >>> score = validator.validate(times, 250)
            >>> print(f"Performance: {score:.2f}")
        """
        logger.info(f"Validating response time: actual={actual}, threshold={threshold}")

        # Handle list of response times - use P95
        if isinstance(actual, list):
            if not actual:
                # Empty list - return neutral score
                logger.warning("Empty response times list - returning 0.5")
                return 0.5

            # Calculate P95 for multiple measurements
            actual_time = self.calculate_p95(actual)
            logger.info(f"Using P95 value: {actual_time}ms (from {len(actual)} measurements)")
        else:
            actual_time = float(actual)

        # Calculate score based on comparison to threshold
        if actual_time <= threshold:
            # Within threshold - perfect score
            if threshold == 0:
                # Special case: zero threshold
                if actual_time == 0:
                    return 1.0
                else:
                    return 0.0

            # Any time within or at threshold gets perfect score
            score = 1.0
        else:
            # Exceeds threshold - score degrades based on how much over
            # 1.0x threshold (just over) = 0.5
            # 1.5x threshold = 0.25
            # 2.0x+ threshold = 0.0

            excess_ratio = actual_time / threshold

            if excess_ratio <= 1.5:
                # Between 1x and 1.5x threshold: 0.5 to 0.25
                # Linear degradation
                score = 0.5 - (0.5 * (excess_ratio - 1.0))
            elif excess_ratio < 2.0:
                # Between 1.5x and 2x threshold: 0.25 to 0.0
                score = 0.25 - (0.5 * (excess_ratio - 1.5))
            else:
                # 2x+ threshold: very poor performance
                score = 0.0

            # Ensure score stays in valid range
            score = max(0.0, min(1.0, score))

        logger.info(
            f"Response time validation: {actual_time}ms vs {threshold}ms "
            f"threshold = score {score:.3f}"
        )

        return float(score)

    def __repr__(self) -> str:
        """
        String representation of ResponseTimeValidator.

        Returns:
            String identifier

        Example:
            >>> validator = ResponseTimeValidator()
            >>> print(validator)
            <ResponseTimeValidator()>
        """
        return "<ResponseTimeValidator()>"
