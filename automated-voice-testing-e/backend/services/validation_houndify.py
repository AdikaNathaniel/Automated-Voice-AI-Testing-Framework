"""
Houndify Validation Mixin

This module provides the ValidationHoundifyMixin class which implements
validation logic specific to Houndify voice AI responses.

Key Features:
- CommandKind matching validation
- ASR confidence score extraction and validation
- Response content validation
- NativeData schema validation

Example:
    >>> from services.validation_houndify import ValidationHoundifyMixin
    >>>
    >>> class MyValidator(ValidationHoundifyMixin):
    ...     pass
    >>>
    >>> validator = MyValidator()
    >>> score = validator._calculate_command_kind_match_score(
    ...     actual_command_kind="WeatherCommand",
    ...     expected_command_kind="WeatherCommand"
    ... )
    >>> print(score)  # 1.0
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from validators.entity_validator import EntityValidator

logger = logging.getLogger(__name__)

# Shared entity validator instance
_entity_validator = EntityValidator(default_tolerance=0.01)


class ValidationHoundifyMixin:
    """
    Mixin providing Houndify-specific validation methods.

    This mixin is designed to be used with ValidationService to add
    Houndify-specific validation capabilities.
    """

    def _extract_houndify_data(
        self,
        execution_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Extract Houndify response data from execution context.

        Args:
            execution_context: Execution context containing houndify_response

        Returns:
            Houndify response data or None if not found

        Example:
            >>> context = {"houndify_response": {"AllResults": [...]}}
            >>> data = self._extract_houndify_data(context)
            >>> print(data["AllResults"])
        """
        houndify_response = execution_context.get("houndify_response")
        if not houndify_response:
            logger.warning("No houndify_response found in execution context")
            return None

        return houndify_response

    def _extract_command_kind(
        self,
        houndify_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extract CommandKind from Houndify response.

        Args:
            houndify_data: Houndify response data

        Returns:
            CommandKind string or None if not found

        Example:
            >>> data = {"AllResults": [{"CommandKind": "WeatherCommand"}]}
            >>> command_kind = self._extract_command_kind(data)
            >>> print(command_kind)  # "WeatherCommand"
        """
        all_results = houndify_data.get("AllResults", [])
        if not all_results or len(all_results) == 0:
            logger.warning("No AllResults found in Houndify response")
            return None

        first_result = all_results[0]
        command_kind = first_result.get("CommandKind")

        if not command_kind:
            logger.warning("No CommandKind found in first result")
            return None

        logger.debug(f"Extracted CommandKind: {command_kind}")
        return command_kind

    def _extract_asr_confidence(
        self,
        houndify_data: Dict[str, Any]
    ) -> Optional[float]:
        """
        Extract ASR confidence score from Houndify response.

        Args:
            houndify_data: Houndify response data

        Returns:
            ASR confidence score (0.0 to 1.0) or None if not found

        Example:
            >>> data = {"AllResults": [{"ASRConfidence": 0.95}]}
            >>> confidence = self._extract_asr_confidence(data)
            >>> print(confidence)  # 0.95
        """
        all_results = houndify_data.get("AllResults", [])
        if not all_results or len(all_results) == 0:
            logger.warning("No AllResults found in Houndify response")
            return None

        first_result = all_results[0]
        asr_confidence = first_result.get("ASRConfidence")

        if asr_confidence is None:
            logger.warning("No ASRConfidence found in first result")
            return None

        logger.debug(f"Extracted ASRConfidence: {asr_confidence}")
        return float(asr_confidence)

    def _extract_spoken_response(
        self,
        houndify_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extract the AI's spoken response from Houndify response.

        This is what the voice AI actually said back to the user.

        Args:
            houndify_data: Houndify response data

        Returns:
            SpokenResponse text or None if not found

        Example:
            >>> data = {"AllResults": [{"SpokenResponse": "The weather is sunny"}]}
            >>> response = self._extract_spoken_response(data)
            >>> print(response)  # "The weather is sunny"
        """
        all_results = houndify_data.get("AllResults", [])
        if not all_results or len(all_results) == 0:
            logger.warning("No AllResults found in Houndify response")
            return None

        first_result = all_results[0]

        # Try SpokenResponse first, then WrittenResponse as fallback
        spoken = first_result.get("SpokenResponse")
        if spoken:
            logger.debug(f"Extracted SpokenResponse: {spoken[:100]}...")
            return spoken

        written = first_result.get("WrittenResponse")
        if written:
            logger.debug(f"Extracted WrittenResponse as fallback: {written[:100]}...")
            return written

        logger.warning("No SpokenResponse or WrittenResponse found")
        return None

    def _calculate_command_kind_match_score(
        self,
        actual_command_kind: Optional[str],
        expected_command_kind: Optional[str]
    ) -> Optional[float]:
        """
        Calculate CommandKind match score.

        Args:
            actual_command_kind: Actual CommandKind from Houndify
            expected_command_kind: Expected CommandKind

        Returns:
            1.0 if matches, 0.0 if mismatch, None if no expectation defined.

        Example:
            >>> score = self._calculate_command_kind_match_score(
            ...     "WeatherCommand",
            ...     "WeatherCommand"
            ... )
            >>> print(score)  # 1.0
        """
        # If no expected CommandKind, return None (nothing to compare)
        if expected_command_kind is None:
            logger.debug("No expected CommandKind defined, returning None")
            return None

        # If no actual CommandKind, it's a mismatch
        if actual_command_kind is None:
            logger.warning("No actual CommandKind, returning 0.0")
            return 0.0

        # Compare CommandKinds
        match = actual_command_kind == expected_command_kind
        score = 1.0 if match else 0.0

        logger.info(
            f"CommandKind match: actual={actual_command_kind}, "
            f"expected={expected_command_kind}, score={score}"
        )

        return score

    def _validate_asr_confidence(
        self,
        asr_confidence: Optional[float],
        min_confidence: Optional[float]
    ) -> float:
        """
        Validate ASR confidence meets minimum threshold.

        Args:
            asr_confidence: Actual ASR confidence from Houndify
            min_confidence: Minimum required confidence

        Returns:
            ASR confidence score if above threshold, 0.0 otherwise.
            Returns actual confidence if min_confidence is None.

        Example:
            >>> score = self._validate_asr_confidence(0.95, 0.80)
            >>> print(score)  # 0.95
        """
        # If no ASR confidence available, return 0.0
        if asr_confidence is None:
            logger.warning("No ASR confidence available, returning 0.0")
            return 0.0

        # If no minimum threshold, return actual confidence
        if min_confidence is None:
            logger.debug(f"No min confidence threshold, returning {asr_confidence}")
            return asr_confidence

        # Check if confidence meets threshold
        meets_threshold = asr_confidence >= min_confidence
        score = asr_confidence if meets_threshold else 0.0

        logger.info(
            f"ASR confidence validation: actual={asr_confidence}, "
            f"min={min_confidence}, score={score}"
        )

        return score

    def _validate_response_content(
        self,
        ai_response: Optional[str],
        expected_response_content: Optional[Dict[str, Any]],
        forbidden_phrases: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Validate AI response against expected content patterns.

        This is a deterministic check that validates the AI's SpokenResponse
        against patterns defined in ExpectedOutcome.expected_response_content.

        Supported patterns:
        - contains: List of strings that MUST appear (case-insensitive)
        - not_contains: List of strings that must NOT appear (case-insensitive)
        - regex: List of regex patterns that must match
        - regex_not_match: List of regex patterns that must NOT match

        Args:
            ai_response: The AI's spoken response from Houndify
            expected_response_content: Dict with pattern definitions, or None
            forbidden_phrases: Additional forbidden phrases from ExpectedOutcome

        Returns:
            Dict with:
            - passed: bool - Whether all checks passed
            - errors: List[str] - List of validation errors
            - details: Dict - Detailed results for each check type

        Example:
            >>> result = self._validate_response_content(
            ...     ai_response="It's sunny and 72 degrees in Seattle",
            ...     expected_response_content={
            ...         "contains": ["sunny", "degrees"],
            ...         "not_contains": ["error", "sorry"]
            ...     }
            ... )
            >>> print(result['passed'])  # True
        """
        result = {
            'passed': True,
            'errors': [],
            'details': {
                'contains': {'passed': True, 'matched': [], 'missing': []},
                'not_contains': {'passed': True, 'found': []},
                'regex': {'passed': True, 'matched': [], 'failed': []},
                'regex_not_match': {'passed': True, 'found': []},
                'forbidden_phrases': {'passed': True, 'found': []},
            }
        }

        # If no expected content defined, auto-pass
        if not expected_response_content:
            logger.debug("No expected_response_content defined, auto-passing")
            return result

        # If expected_response_content is empty dict, auto-pass
        if isinstance(expected_response_content, dict) and not expected_response_content:
            logger.debug("Empty expected_response_content, auto-passing")
            return result

        # If no AI response to check against, fail if patterns expected
        if not ai_response or not ai_response.strip():
            result['passed'] = False
            result['errors'].append("No AI response to validate")
            logger.warning("No AI response provided for content validation")
            return result

        response_lower = ai_response.lower()

        # Check 'contains' patterns
        contains_patterns = expected_response_content.get('contains', [])
        if contains_patterns and isinstance(contains_patterns, list):
            for pattern in contains_patterns:
                if not pattern:
                    continue
                pattern_lower = str(pattern).lower()
                if pattern_lower in response_lower:
                    result['details']['contains']['matched'].append(pattern)
                else:
                    result['details']['contains']['missing'].append(pattern)
                    result['details']['contains']['passed'] = False
                    result['passed'] = False
                    result['errors'].append(f"Missing required phrase: '{pattern}'")

        # Check 'not_contains' patterns
        not_contains = expected_response_content.get('not_contains', [])
        if not_contains and isinstance(not_contains, list):
            for pattern in not_contains:
                if not pattern:
                    continue
                pattern_lower = str(pattern).lower()
                if pattern_lower in response_lower:
                    result['details']['not_contains']['found'].append(pattern)
                    result['details']['not_contains']['passed'] = False
                    result['passed'] = False
                    result['errors'].append(f"Found forbidden phrase: '{pattern}'")

        # Check 'regex' patterns (must match)
        regex_patterns = expected_response_content.get('regex', [])
        if regex_patterns and isinstance(regex_patterns, list):
            for pattern in regex_patterns:
                if not pattern:
                    continue
                try:
                    if re.search(pattern, ai_response, re.IGNORECASE):
                        result['details']['regex']['matched'].append(pattern)
                    else:
                        result['details']['regex']['failed'].append(pattern)
                        result['details']['regex']['passed'] = False
                        result['passed'] = False
                        result['errors'].append(f"Regex pattern not matched: '{pattern}'")
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern}': {e}")
                    result['errors'].append(f"Invalid regex pattern: '{pattern}'")

        # Check 'regex_not_match' patterns (must NOT match)
        regex_not_match = expected_response_content.get('regex_not_match', [])
        if regex_not_match and isinstance(regex_not_match, list):
            for pattern in regex_not_match:
                if not pattern:
                    continue
                try:
                    if re.search(pattern, ai_response, re.IGNORECASE):
                        result['details']['regex_not_match']['found'].append(pattern)
                        result['details']['regex_not_match']['passed'] = False
                        result['passed'] = False
                        result['errors'].append(
                            f"Response matched forbidden regex: '{pattern}'"
                        )
                except re.error as e:
                    logger.warning(f"Invalid regex pattern '{pattern}': {e}")

        # Check forbidden_phrases from ExpectedOutcome
        if forbidden_phrases and isinstance(forbidden_phrases, list):
            for phrase in forbidden_phrases:
                if not phrase:
                    continue
                phrase_lower = str(phrase).lower()
                if phrase_lower in response_lower:
                    result['details']['forbidden_phrases']['found'].append(phrase)
                    result['details']['forbidden_phrases']['passed'] = False
                    result['passed'] = False
                    result['errors'].append(f"Found forbidden phrase: '{phrase}'")

        logger.info(
            f"Response content validation: passed={result['passed']}, "
            f"errors={len(result['errors'])}"
        )

        return result

    def _validate_entities(
        self,
        actual_entities: Optional[Dict[str, Any]],
        expected_entities: Optional[Dict[str, Any]],
        tolerance: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Validate actual entities against expected entities.

        Uses EntityValidator to compare entities with:
        - Presence checking (all expected entities must be present)
        - Value matching with type-aware comparison
        - Numeric tolerance for approximate matching
        - Case-insensitive string comparison

        Args:
            actual_entities: Actual entities extracted from Houndify response
            expected_entities: Expected entities from ExpectedOutcome.entities
            tolerance: Optional numeric tolerance for value matching

        Returns:
            Dict with:
            - passed: bool - Whether entity validation passed (score >= 1.0)
            - score: float - Entity match score (0.0 to 1.0)
            - errors: List[str] - List of validation errors
            - details: Dict with expected, actual, matched, missing info

        Example:
            >>> result = self._validate_entities(
            ...     actual_entities={"location": "Seattle", "temp": 72},
            ...     expected_entities={"location": "Seattle", "temp": 72}
            ... )
            >>> print(result['passed'])  # True
            >>> print(result['score'])   # 1.0
        """
        result = {
            'passed': True,
            'score': 1.0,
            'errors': [],
            'details': {
                'expected': expected_entities,
                'actual': actual_entities,
                'matched': [],
                'missing': [],
                'mismatched': [],
            }
        }

        # If no expected entities, auto-pass
        if not expected_entities:
            logger.debug("No expected entities defined, auto-passing")
            return result

        # If expected entities but no actual entities, fail
        if not actual_entities:
            result['passed'] = False
            result['score'] = 0.0
            result['errors'].append("No actual entities to validate against expected")
            result['details']['missing'] = list(expected_entities.keys())
            logger.warning("No actual entities provided for validation")
            return result

        # Use EntityValidator for smart comparison
        score = _entity_validator.validate(
            actual=actual_entities,
            expected=expected_entities,
            tolerance=tolerance
        )

        # Build detailed results
        for key, expected_value in expected_entities.items():
            if key not in actual_entities:
                result['details']['missing'].append(key)
                result['errors'].append(f"Missing entity: '{key}'")
            else:
                actual_value = actual_entities[key]
                if _entity_validator.match_value(actual_value, expected_value, tolerance):
                    result['details']['matched'].append(key)
                else:
                    result['details']['mismatched'].append({
                        'key': key,
                        'expected': expected_value,
                        'actual': actual_value
                    })
                    result['errors'].append(
                        f"Entity mismatch for '{key}': "
                        f"expected '{expected_value}', got '{actual_value}'"
                    )

        result['score'] = score
        # Pass only if all expected entities match (score == 1.0)
        result['passed'] = score >= 1.0

        logger.info(
            f"Entity validation: passed={result['passed']}, score={score:.3f}, "
            f"matched={len(result['details']['matched'])}, "
            f"missing={len(result['details']['missing'])}, "
            f"mismatched={len(result['details']['mismatched'])}"
        )

        return result
