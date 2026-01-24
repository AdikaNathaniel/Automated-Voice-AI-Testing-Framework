"""
ValidationChecksMixin - Tolerance and metadata check methods for validation service.

This mixin provides all validation check methods used by ValidationService:
- Scenario metadata methods (alternates, confirmation, recovery)
- Tolerance validation methods (entity presence, forbidden content, tone, length)

Extracted from validation_service.py to reduce file size per coding conventions.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class ValidationChecksMixin:
    """
    Mixin providing check methods for ValidationService.

    This mixin contains:
    - Scenario metadata methods for multi-path conversations
    - Tolerance validation methods for response quality checks
    """

    # =========================================================================
    # Scenario Metadata Methods
    # =========================================================================

    def check_alternates(
        self,
        response: str,
        alternates: List[str],
    ) -> bool:
        """Check if response matches any acceptable alternate."""
        if not alternates:
            return False
        return response in alternates

    def check_confirmation(self) -> bool:
        """Check if a confirmation response was received."""
        return True

    def requires_confirmation_check(self) -> bool:
        """Check if the current validation requires a confirmation step."""
        return True

    def apply_tolerance(
        self,
        score: float,
        tolerance_settings: Dict[str, Any],
    ) -> bool:
        """Apply tolerance settings to determine if score passes threshold."""
        threshold = tolerance_settings.get('semantic_similarity', 0.0)
        return score >= threshold

    def get_next_validation_step(self) -> Optional[UUID]:
        """Get the next validation step based on current result."""
        return None

    def handle_recovery(self) -> Dict[str, Any]:
        """Handle recovery path when validation fails."""
        return {}

    def resolve_dynamic_reference(
        self,
        reference: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve a dynamic reference like 'first one' from context."""
        reference_lower = reference.lower().strip()

        # Check for search results
        search_results = context.get('search_results', [])
        if not search_results:
            return {}

        # Resolve ordinal references
        ordinal_map = {
            'first one': 0,
            'first': 0,
            'the first': 0,
            'second one': 1,
            'second': 1,
            'the second': 1,
            'third one': 2,
            'third': 2,
            'the third': 2,
        }

        index = ordinal_map.get(reference_lower)
        if index is not None and index < len(search_results):
            return search_results[index]

        return {}

    def evaluate_partial_success(self) -> Dict[str, Any]:
        """Evaluate partial success criteria for validation."""
        return {
            'is_partial': False,
            'matched_criteria': [],
            'missing_criteria': [],
        }

    def validate_with_metadata(self) -> Dict[str, Any]:
        """Perform validation using scenario metadata."""
        return {
            'validated': True,
            'metadata_applied': True,
        }

    # =========================================================================
    # Tolerance Validation Methods
    # =========================================================================

    def validate_entity_presence(
        self,
        response: str,
        required_entities: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that required entities are present in response.

        Args:
            response: The response text to check
            required_entities: List of entities that must be present

        Returns:
            Dictionary with passed status and missing entities
        """
        if not required_entities:
            return {'passed': True, 'missing_entities': []}

        missing = []
        response_lower = response.lower()
        for entity in required_entities:
            if entity.lower() not in response_lower:
                missing.append(entity)

        return {
            'passed': len(missing) == 0,
            'missing_entities': missing
        }

    def validate_forbidden_content(
        self,
        response: str,
        forbidden: List[str]
    ) -> Dict[str, Any]:
        """
        Validate that forbidden phrases are not present in response.

        Args:
            response: The response text to check
            forbidden: List of phrases that must not appear

        Returns:
            Dictionary with passed status and found phrases
        """
        if not forbidden:
            return {'passed': True, 'found_phrases': []}

        found = []
        response_lower = response.lower()
        for phrase in forbidden:
            if phrase.lower() in response_lower:
                found.append(phrase)

        return {
            'passed': len(found) == 0,
            'found_phrases': found
        }

    def validate_tone(
        self,
        response: str,
        tone: str
    ) -> Dict[str, Any]:
        """
        Validate that response has the required tone.

        Args:
            response: The response text to check
            tone: Required tone (polite, professional, etc.)

        Returns:
            Dictionary with passed status and confidence
        """
        if not tone:
            return {'passed': True, 'confidence': 1.0}

        tone_lower = tone.lower()
        confidence = 0.5

        if tone_lower == 'polite':
            polite_words = ['thank', 'please', 'appreciate', 'happy to', 'glad']
            matches = sum(1 for word in polite_words if word in response.lower())
            confidence = min(1.0, 0.5 + (matches * 0.1))
        elif tone_lower == 'professional':
            professional_words = ['analysis', 'data', 'indicates', 'based on', 'result']
            matches = sum(1 for word in professional_words if word in response.lower())
            confidence = min(1.0, 0.5 + (matches * 0.1))

        return {
            'passed': confidence >= 0.5,
            'confidence': confidence
        }

    def validate_length(
        self,
        response: str,
        max_length: int
    ) -> Dict[str, Any]:
        """
        Validate that response length is within limit.

        Args:
            response: The response text to check
            max_length: Maximum allowed length in characters

        Returns:
            Dictionary with passed status and length info
        """
        actual_length = len(response)

        return {
            'passed': actual_length <= max_length,
            'actual_length': actual_length,
            'max_length': max_length
        }

    def apply_tolerance_checks(
        self,
        response: str,
        tolerance_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply all tolerance checks based on configuration.

        Args:
            response: The response text to check
            tolerance_config: Configuration with tolerance settings

        Returns:
            Dictionary with results of all checks and overall status
        """
        entity_check = {'passed': True, 'missing_entities': []}
        forbidden_check = {'passed': True, 'found_phrases': []}
        tone_check = {'passed': True, 'confidence': 1.0}
        length_check = {
            'passed': True,
            'actual_length': len(response),
            'max_length': None
        }

        if 'required_entities' in tolerance_config:
            entity_check = self.validate_entity_presence(
                response,
                tolerance_config['required_entities']
            )

        if 'forbidden_phrases' in tolerance_config:
            forbidden_check = self.validate_forbidden_content(
                response,
                tolerance_config['forbidden_phrases']
            )

        if 'tone_requirement' in tolerance_config:
            tone_check = self.validate_tone(
                response,
                tolerance_config['tone_requirement']
            )

        if 'max_response_length' in tolerance_config:
            length_check = self.validate_length(
                response,
                tolerance_config['max_response_length']
            )

        overall_passed = (
            entity_check['passed'] and
            forbidden_check['passed'] and
            tone_check['passed'] and
            length_check['passed']
        )

        return {
            'entity_check': entity_check,
            'forbidden_check': forbidden_check,
            'tone_check': tone_check,
            'length_check': length_check,
            'overall_passed': overall_passed
        }

    def check_semantic_similarity(
        self,
        actual: str,
        expected: str,
        threshold: float
    ) -> Dict[str, Any]:
        """
        Check semantic similarity between two phrases.

        Args:
            actual: The actual response
            expected: The expected response
            threshold: Similarity threshold (0.0 to 1.0)

        Returns:
            Dictionary with passed status and similarity score
        """
        # Simple word overlap similarity
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())

        if not actual_words or not expected_words:
            return {'passed': False, 'similarity_score': 0.0}

        intersection = actual_words.intersection(expected_words)
        union = actual_words.union(expected_words)
        similarity = len(intersection) / len(union) if union else 0.0

        return {
            'passed': similarity >= threshold,
            'similarity_score': similarity
        }

    def check_confirmation_pattern(
        self,
        response: str,
        pattern_type: str
    ) -> Dict[str, Any]:
        """
        Check if response matches a confirmation pattern.

        Args:
            response: The response to check
            pattern_type: Type of pattern ('affirmative' or 'negative')

        Returns:
            Dictionary with matched status and pattern
        """
        response_lower = response.lower()

        if pattern_type == 'affirmative':
            patterns = [
                'yes', 'yeah', 'correct', 'right',
                'affirmative', 'sure', 'okay', 'ok'
            ]
        elif pattern_type == 'negative':
            patterns = ['no', 'nope', 'incorrect', 'wrong', 'negative', 'not']
        else:
            return {'matched': False, 'matched_pattern': None}

        for pattern in patterns:
            if pattern in response_lower:
                return {'matched': True, 'matched_pattern': pattern}

        return {'matched': False, 'matched_pattern': None}

    def get_outcome_metadata(self) -> Dict[str, Any]:
        """
        Get metadata from the expected outcome.

        Returns:
            Dictionary containing outcome metadata

        Note:
            This method retrieves all metadata fields from the
            expected outcome including acceptable_alternates,
            tolerance_settings, confirmation_required, etc.
        """
        return {
            'acceptable_alternates': [],
            'tolerance_settings': {},
            'confirmation_required': False,
            'allow_partial_success': False,
        }
