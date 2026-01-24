"""
IntentValidator for matching intents with exact and fuzzy matching (TASK-120).

This module provides the IntentValidator class which validates voice AI
intent recognition by comparing actual intents with expected intents using
both exact matching and fuzzy matching with configurable thresholds.

Key Features:
- Exact match validation (case-insensitive, whitespace-normalized)
- Fuzzy match validation using sequence matching
- Configurable similarity threshold
- Returns confidence scores (0.0 to 1.0)

Example:
    >>> from validators.intent_validator import IntentValidator
    >>>
    >>> # Create validator
    >>> validator = IntentValidator()
    >>>
    >>> # Exact match
    >>> score = validator.validate("navigate_home", "navigate_home")
    >>> print(score)  # 1.0
    >>>
    >>> # Fuzzy match
    >>> score = validator.validate("navigate_home", "navigate_house", threshold=0.7)
    >>> print(score)  # ~0.85
    >>>
    >>> # No match
    >>> score = validator.validate("play_music", "navigate_home")
    >>> print(score)  # ~0.0
"""

from typing import Optional
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class IntentValidator:
    """
    Validator for intent matching with exact and fuzzy match support.

    This validator compares actual voice AI intents with expected intents
    using two matching strategies:
    1. Exact match: Case-insensitive, whitespace-normalized string equality
    2. Fuzzy match: Sequence similarity using difflib.SequenceMatcher

    The validator returns a confidence score from 0.0 to 1.0, where:
    - 1.0 = perfect match
    - 0.0 = no similarity

    Attributes:
        default_threshold: Default fuzzy match threshold (0.75)

    Example:
        >>> validator = IntentValidator()
        >>>
        >>> # Test exact match
        >>> score = validator.validate("play_music", "play_music")
        >>> assert score == 1.0
        >>>
        >>> # Test fuzzy match
        >>> score = validator.validate("play_music", "play_songs")
        >>> print(f"Similarity: {score:.2f}")
        >>>
        >>> # Test with custom threshold
        >>> score = validator.validate(
        ...     "navigate_home",
        ...     "navigate_house",
        ...     threshold=0.8
        ... )
    """

    def __init__(self, default_threshold: float = 0.75):
        """
        Initialize IntentValidator.

        Args:
            default_threshold: Default threshold for fuzzy matching (0.0-1.0)
                             Default is 0.75 (75% similarity required)

        Example:
            >>> # Use default threshold
            >>> validator = IntentValidator()
            >>>
            >>> # Use custom default threshold
            >>> strict_validator = IntentValidator(default_threshold=0.9)
        """
        self.default_threshold = default_threshold
        logger.info(f"IntentValidator initialized with threshold={default_threshold}")

    def exact_match(self, actual: Optional[str], expected: Optional[str]) -> bool:
        """
        Check if two intents match exactly.

        Performs case-insensitive comparison with whitespace normalization.
        None values are handled: None == None is True, None == string is False.

        Args:
            actual: Actual intent from voice AI response
            expected: Expected intent to compare against

        Returns:
            True if intents match exactly, False otherwise

        Example:
            >>> validator = IntentValidator()
            >>>
            >>> # Exact match
            >>> validator.exact_match("navigate_home", "navigate_home")
            True
            >>>
            >>> # Case insensitive
            >>> validator.exact_match("Navigate_Home", "navigate_home")
            True
            >>>
            >>> # Handles whitespace
            >>> validator.exact_match("  navigate_home  ", "navigate_home")
            True
            >>>
            >>> # Different intents
            >>> validator.exact_match("play_music", "navigate_home")
            False
        """
        # Handle None values
        if actual is None and expected is None:
            return True
        if actual is None or expected is None:
            return False

        # Normalize and compare
        actual_normalized = str(actual).strip().lower()
        expected_normalized = str(expected).strip().lower()

        is_match = actual_normalized == expected_normalized

        logger.debug(
            f"Exact match: '{actual}' vs '{expected}' = {is_match}"
        )

        return is_match

    def fuzzy_match(self, actual: Optional[str], expected: Optional[str]) -> float:
        """
        Calculate fuzzy similarity score between two intents.

        Uses difflib.SequenceMatcher to calculate similarity ratio based on
        longest contiguous matching subsequence. This handles typos, minor
        variations, and similar words well.

        Args:
            actual: Actual intent from voice AI response
            expected: Expected intent to compare against

        Returns:
            Similarity score from 0.0 to 1.0
            - 1.0 = identical strings
            - 0.0 = completely different

        Example:
            >>> validator = IntentValidator()
            >>>
            >>> # Identical strings
            >>> score = validator.fuzzy_match("navigate_home", "navigate_home")
            >>> print(score)  # 1.0
            >>>
            >>> # Similar strings
            >>> score = validator.fuzzy_match("navigate_home", "navigate_house")
            >>> print(f"{score:.2f}")  # ~0.85
            >>>
            >>> # Typo handling
            >>> score = validator.fuzzy_match("navgate_home", "navigate_home")
            >>> print(f"{score:.2f}")  # ~0.92
            >>>
            >>> # Very different
            >>> score = validator.fuzzy_match("play_music", "navigate_home")
            >>> print(f"{score:.2f}")  # ~0.23
        """
        # Handle None values
        if actual is None and expected is None:
            return 1.0
        if actual is None or expected is None:
            return 0.0

        # Normalize strings
        actual_normalized = str(actual).strip().lower()
        expected_normalized = str(expected).strip().lower()

        # Handle empty strings
        if not actual_normalized and not expected_normalized:
            return 1.0
        if not actual_normalized or not expected_normalized:
            return 0.0

        # Calculate similarity using SequenceMatcher
        matcher = SequenceMatcher(None, actual_normalized, expected_normalized)
        similarity = matcher.ratio()

        logger.debug(
            f"Fuzzy match: '{actual}' vs '{expected}' = {similarity:.3f}"
        )

        return float(similarity)

    def validate(
        self,
        actual: Optional[str],
        expected: Optional[str],
        threshold: Optional[float] = None
    ) -> float:
        """
        Validate intent matching with exact and fuzzy matching.

        This is the main validation method that:
        1. First checks for exact match → returns 1.0
        2. Then performs fuzzy match → returns similarity score
        3. Compares against threshold if provided

        Args:
            actual: Actual intent from voice AI response
            expected: Expected intent to compare against
            threshold: Optional custom threshold (uses default if not provided)

        Returns:
            Confidence score from 0.0 to 1.0:
            - 1.0 = exact match or perfect fuzzy match
            - 0.0 = no similarity
            - 0.0-1.0 = partial similarity (fuzzy match score)

        Example:
            >>> validator = IntentValidator()
            >>>
            >>> # Exact match
            >>> score = validator.validate("play_music", "play_music")
            >>> assert score == 1.0
            >>>
            >>> # Fuzzy match
            >>> score = validator.validate("play_music", "play_songs")
            >>> print(f"Match score: {score:.2f}")
            >>>
            >>> # With custom threshold
            >>> score = validator.validate(
            ...     "navigate_home",
            ...     "navigate_house",
            ...     threshold=0.8
            ... )
            >>> if score >= 0.8:
            ...     print("Meets threshold")
            >>>
            >>> # No match
            >>> score = validator.validate("completely", "different")
            >>> assert score < 0.5
        """
        # Use provided threshold or default
        use_threshold = threshold if threshold is not None else self.default_threshold

        logger.info(
            f"Validating intent: actual='{actual}', expected='{expected}', "
            f"threshold={use_threshold}"
        )

        # Handle None values
        if actual is None and expected is None:
            logger.debug("Both intents are None - returning 1.0")
            return 1.0
        if actual is None or expected is None:
            logger.debug("One intent is None - returning 0.0")
            return 0.0

        # Check exact match first
        if self.exact_match(actual, expected):
            logger.info("Exact match found - returning 1.0")
            return 1.0

        # Perform fuzzy matching
        similarity_score = self.fuzzy_match(actual, expected)

        logger.info(
            f"Fuzzy match score: {similarity_score:.3f} "
            f"(threshold: {use_threshold})"
        )

        return similarity_score

    def __repr__(self) -> str:
        """
        String representation of IntentValidator.

        Returns:
            String showing default threshold

        Example:
            >>> validator = IntentValidator(default_threshold=0.8)
            >>> print(validator)
            <IntentValidator(threshold=0.8)>
        """
        return f"<IntentValidator(threshold={self.default_threshold})>"
