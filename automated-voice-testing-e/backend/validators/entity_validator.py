"""
EntityValidator for validating extracted entities (TASK-121).

This module provides the EntityValidator class which validates entity extraction
from voice AI responses by checking that all expected entities are present and
their values match (with tolerance for numeric values).

Key Features:
- Check all expected entities are present
- Value matching with type-aware comparison
- Numeric tolerance for approximate matching
- Case-insensitive string comparison
- Returns confidence scores (0.0 to 1.0)

Example:
    >>> from validators.entity_validator import EntityValidator
    >>>
    >>> # Create validator
    >>> validator = EntityValidator()
    >>>
    >>> # Validate entities
    >>> actual = {"action": "navigate", "destination": "home"}
    >>> expected = {"action": "navigate", "destination": "home"}
    >>> score = validator.validate(actual, expected)
    >>> print(score)  # 1.0
    >>>
    >>> # With numeric tolerance
    >>> actual = {"temperature": 72.5, "unit": "fahrenheit"}
    >>> expected = {"temperature": 72, "unit": "fahrenheit"}
    >>> score = validator.validate(actual, expected, tolerance=1.0)
    >>> print(score)  # 1.0
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class EntityValidator:
    """
    Validator for entity extraction with presence and value matching.

    This validator checks that:
    1. All expected entities are present in the actual entities
    2. Entity values match (with tolerance for numeric values)

    The validator returns a confidence score from 0.0 to 1.0, where:
    - 1.0 = all entities present and values match
    - 0.0 = no entities match or missing entities
    - 0.0-1.0 = partial match (percentage of matching entities)

    Attributes:
        default_tolerance: Default numeric tolerance (0.01 or 1%)

    Example:
        >>> validator = EntityValidator()
        >>>
        >>> # All entities match
        >>> actual = {"action": "play", "media": "music"}
        >>> expected = {"action": "play", "media": "music"}
        >>> score = validator.validate(actual, expected)
        >>> assert score == 1.0
        >>>
        >>> # Partial match
        >>> actual = {"action": "play", "media": "video"}
        >>> expected = {"action": "play", "media": "music"}
        >>> score = validator.validate(actual, expected)
        >>> print(f"Match score: {score}")  # 0.5 (1 out of 2 entities match)
        >>>
        >>> # Missing entity
        >>> actual = {"action": "play"}
        >>> expected = {"action": "play", "media": "music"}
        >>> score = validator.validate(actual, expected)
        >>> print(f"Match score: {score}")  # 0.5 (1 present, 1 missing)
    """

    def __init__(self, default_tolerance: float = 0.01):
        """
        Initialize EntityValidator.

        Args:
            default_tolerance: Default tolerance for numeric matching
                             Default is 0.01 (1% tolerance)

        Example:
            >>> # Use default tolerance
            >>> validator = EntityValidator()
            >>>
            >>> # Use custom default tolerance
            >>> strict_validator = EntityValidator(default_tolerance=0.001)
        """
        self.default_tolerance = default_tolerance
        logger.info(f"EntityValidator initialized with tolerance={default_tolerance}")

    def check_all_present(
        self,
        actual: Optional[Dict[str, Any]],
        expected: Optional[Dict[str, Any]]
    ) -> bool:
        """
        Check if all expected entities are present in actual entities.

        Only checks for presence of keys, not values. Returns True if all
        expected entity keys are in the actual entities dictionary.

        Args:
            actual: Actual entities extracted from voice response
            expected: Expected entities to check for

        Returns:
            True if all expected entities are present, False otherwise

        Example:
            >>> validator = EntityValidator()
            >>>
            >>> # All present
            >>> actual = {"action": "play", "media": "music", "artist": "Beatles"}
            >>> expected = {"action": "play", "media": "music"}
            >>> validator.check_all_present(actual, expected)
            True
            >>>
            >>> # Missing entity
            >>> actual = {"action": "play"}
            >>> expected = {"action": "play", "media": "music"}
            >>> validator.check_all_present(actual, expected)
            False
            >>>
            >>> # No expected entities
            >>> validator.check_all_present({"a": 1}, {})
            True
        """
        # Handle None values
        if expected is None or not expected:
            # No expected entities means all present
            return True

        if actual is None:
            actual = {}

        # Check if all expected keys are in actual
        expected_keys = set(expected.keys())
        actual_keys = set(actual.keys())

        all_present = expected_keys.issubset(actual_keys)

        logger.debug(
            f"Check all present: expected={list(expected_keys)}, "
            f"actual={list(actual_keys)}, result={all_present}"
        )

        return all_present

    def match_value(
        self,
        actual: Any,
        expected: Any,
        tolerance: Optional[float] = None
    ) -> bool:
        """
        Check if two values match with type-aware comparison.

        Comparison rules:
        - Strings: Case-insensitive, whitespace-normalized
        - Numbers: Exact match or within tolerance
        - Booleans: Exact match
        - None: None matches None only
        - Lists/Dicts: Equality comparison (deep)

        Args:
            actual: Actual value from voice response
            expected: Expected value to compare against
            tolerance: Optional numeric tolerance (absolute difference)
                      If not provided, uses default_tolerance

        Returns:
            True if values match, False otherwise

        Example:
            >>> validator = EntityValidator()
            >>>
            >>> # String matching (case insensitive)
            >>> validator.match_value("Home", "home")
            True
            >>>
            >>> # Numeric exact match
            >>> validator.match_value(42, 42)
            True
            >>>
            >>> # Numeric with tolerance
            >>> validator.match_value(42.1, 42, tolerance=0.2)
            True
            >>>
            >>> # Boolean
            >>> validator.match_value(True, True)
            True
            >>>
            >>> # None
            >>> validator.match_value(None, None)
            True
        """
        # Use provided tolerance or default
        use_tolerance = tolerance if tolerance is not None else self.default_tolerance

        # Handle None values
        if actual is None and expected is None:
            return True
        if actual is None or expected is None:
            return False

        # String matching - case insensitive with whitespace normalization
        if isinstance(expected, str) and isinstance(actual, str):
            actual_normalized = actual.strip().lower()
            expected_normalized = expected.strip().lower()
            is_match = actual_normalized == expected_normalized

            logger.debug(
                f"String match: '{actual}' vs '{expected}' = {is_match}"
            )
            return is_match

        # Numeric matching - exact or within tolerance
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            # Check if values are within tolerance
            difference = abs(float(actual) - float(expected))
            is_match = difference <= use_tolerance

            logger.debug(
                f"Numeric match: {actual} vs {expected} "
                f"(diff={difference:.4f}, tolerance={use_tolerance}) = {is_match}"
            )
            return is_match

        # Boolean matching - exact
        if isinstance(expected, bool) and isinstance(actual, bool):
            is_match = actual == expected
            logger.debug(f"Boolean match: {actual} vs {expected} = {is_match}")
            return is_match

        # List/Dict/Other - equality comparison
        try:
            is_match = actual == expected
            logger.debug(
                f"Generic match: {type(actual).__name__} "
                f"{actual} vs {expected} = {is_match}"
            )
            return is_match
        except Exception as e:
            logger.warning(f"Failed to compare values: {e}")
            return False

    def validate(
        self,
        actual: Optional[Dict[str, Any]],
        expected: Optional[Dict[str, Any]],
        tolerance: Optional[float] = None
    ) -> float:
        """
        Validate entity extraction with presence and value matching.

        This method calculates a confidence score based on:
        1. Percentage of expected entities that are present
        2. Percentage of present entities whose values match

        Final score = (matched_entities / total_expected_entities)

        Args:
            actual: Actual entities extracted from voice response
            expected: Expected entities to compare against
            tolerance: Optional numeric tolerance for value matching

        Returns:
            Confidence score from 0.0 to 1.0:
            - 1.0 = all entities present and all values match
            - 0.0 = no entities match or all missing
            - 0.0-1.0 = partial match

        Example:
            >>> validator = EntityValidator()
            >>>
            >>> # Perfect match
            >>> actual = {"action": "play", "media": "music"}
            >>> expected = {"action": "play", "media": "music"}
            >>> score = validator.validate(actual, expected)
            >>> assert score == 1.0
            >>>
            >>> # Partial match (1 of 2 values match)
            >>> actual = {"action": "play", "media": "video"}
            >>> expected = {"action": "play", "media": "music"}
            >>> score = validator.validate(actual, expected)
            >>> assert score == 0.5
            >>>
            >>> # Missing entity (1 present, 1 missing)
            >>> actual = {"action": "play"}
            >>> expected = {"action": "play", "media": "music"}
            >>> score = validator.validate(actual, expected)
            >>> assert score == 0.5
            >>>
            >>> # With numeric tolerance
            >>> actual = {"temp": 72.5}
            >>> expected = {"temp": 72}
            >>> score = validator.validate(actual, expected, tolerance=1.0)
            >>> assert score == 1.0
        """
        # Use provided tolerance or default
        use_tolerance = tolerance if tolerance is not None else self.default_tolerance

        logger.info(
            f"Validating entities: actual={actual}, expected={expected}, "
            f"tolerance={use_tolerance}"
        )

        # Handle None and empty dictionaries
        if expected is None or not expected:
            # No expected entities means perfect match
            logger.debug("No expected entities - returning 1.0")
            return 1.0

        if actual is None:
            actual = {}

        # If both empty, perfect match
        if not actual and not expected:
            logger.debug("Both empty - returning 1.0")
            return 1.0

        # Count total expected entities
        total_expected = len(expected)
        if total_expected == 0:
            return 1.0

        # Count matching entities
        matched_count = 0

        for key, expected_value in expected.items():
            if key in actual:
                actual_value = actual[key]

                # Check if values match
                if self.match_value(actual_value, expected_value, use_tolerance):
                    matched_count += 1
                    logger.debug(f"Entity '{key}' matches: {actual_value} == {expected_value}")
                else:
                    logger.debug(
                        f"Entity '{key}' present but value mismatch: "
                        f"{actual_value} != {expected_value}"
                    )
            else:
                logger.debug(f"Entity '{key}' missing from actual entities")

        # Calculate score as percentage of matched entities
        score = matched_count / total_expected

        logger.info(
            f"Entity validation complete: {matched_count}/{total_expected} "
            f"entities matched (score={score:.3f})"
        )

        return float(score)

    def __repr__(self) -> str:
        """
        String representation of EntityValidator.

        Returns:
            String showing default tolerance

        Example:
            >>> validator = EntityValidator(default_tolerance=0.1)
            >>> print(validator)
            <EntityValidator(tolerance=0.1)>
        """
        return f"<EntityValidator(tolerance={self.default_tolerance})>"
