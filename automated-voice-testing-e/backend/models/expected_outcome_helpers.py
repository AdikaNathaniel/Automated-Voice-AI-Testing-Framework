"""
ExpectedOutcome Helpers Mixin for validation and tolerance methods.

This mixin provides helper methods for ExpectedOutcome:
- Acceptable alternates methods
- Confirmation methods
- Tolerance methods
- Multi-path support methods

Extracted from expected_outcome.py to maintain 500-line limit per file.

Example:
    >>> class ExpectedOutcome(Base, BaseModel, ExpectedOutcomeHelpersMixin):
    ...     pass
"""

from typing import Dict, Any, Optional
from uuid import UUID


class ExpectedOutcomeHelpersMixin:
    """
    Mixin providing validation and tolerance helper methods.

    This mixin contains:
    - Acceptable alternates methods
    - Confirmation methods
    - Tolerance configuration methods
    - Validation check methods
    - Multi-path support methods
    """

    # =========================================================================
    # Acceptable Alternates Methods
    # =========================================================================

    def add_acceptable_alternate(self, alternate: str) -> None:
        """
        Add an acceptable alternate response.

        Args:
            alternate: Alternative acceptable response text
        """
        if self.acceptable_alternates is None:
            self.acceptable_alternates = []
        if alternate not in self.acceptable_alternates:
            self.acceptable_alternates.append(alternate)

    def remove_acceptable_alternate(self, alternate: str) -> None:
        """
        Remove an acceptable alternate response.

        Args:
            alternate: Alternative response to remove
        """
        if self.acceptable_alternates and alternate in self.acceptable_alternates:
            self.acceptable_alternates.remove(alternate)

    def has_acceptable_alternates(self) -> bool:
        """
        Check if this outcome has acceptable alternates.

        Returns:
            True if alternates exist, False otherwise
        """
        return bool(self.acceptable_alternates and len(self.acceptable_alternates) > 0)

    def matches_alternate(self, response: str) -> bool:
        """
        Check if response matches any acceptable alternate.

        Args:
            response: The response to check

        Returns:
            True if response matches an alternate
        """
        if not self.acceptable_alternates:
            return False
        return response in self.acceptable_alternates

    # =========================================================================
    # Confirmation Methods
    # =========================================================================

    def requires_confirmation(self) -> bool:
        """
        Check if this outcome requires confirmation.

        Returns:
            True if confirmation is required
        """
        return bool(self.confirmation_required)

    # =========================================================================
    # Tolerance Methods
    # =========================================================================

    def set_semantic_tolerance(self, threshold: float) -> None:
        """
        Set semantic similarity tolerance threshold.

        Args:
            threshold: Similarity threshold (0.0 to 1.0)
        """
        if self.tolerance_settings is None:
            self.tolerance_settings = {}
        self.tolerance_settings['semantic_similarity'] = threshold

    def set_entity_tolerance(self, entity: str, tolerance: Dict[str, Any]) -> None:
        """
        Set tolerance for a specific entity.

        Args:
            entity: Entity name
            tolerance: Tolerance settings for the entity
        """
        if self.tolerance_settings is None:
            self.tolerance_settings = {}
        if 'entities' not in self.tolerance_settings:
            self.tolerance_settings['entities'] = {}
        self.tolerance_settings['entities'][entity] = tolerance

    def get_tolerance(self, key: str) -> Optional[Any]:
        """
        Get a tolerance setting value.

        Args:
            key: Tolerance setting key

        Returns:
            Tolerance value or None if not set
        """
        if self.tolerance_settings:
            return self.tolerance_settings.get(key)
        return None

    def get_tolerance_config(self) -> Dict[str, Any]:
        """
        Get the complete tolerance configuration.

        Returns:
            Dictionary with all tolerance settings
        """
        config = {}
        if self.tolerance_config:
            config.update(self.tolerance_config)
        if self.required_entities:
            config['required_entities'] = self.required_entities
        if self.forbidden_phrases:
            config['forbidden_phrases'] = self.forbidden_phrases
        if self.tone_requirement:
            config['tone_requirement'] = self.tone_requirement
        if self.max_response_length:
            config['max_response_length'] = self.max_response_length
        return config

    def check_entity_requirements(self, response: str) -> Dict[str, Any]:
        """
        Check if response contains required entities.

        Args:
            response: The response text to check

        Returns:
            Dictionary with passed status and missing entities
        """
        if not self.required_entities:
            return {'passed': True, 'missing_entities': []}

        missing = []
        response_lower = response.lower()
        for entity in self.required_entities:
            if entity.lower() not in response_lower:
                missing.append(entity)

        return {
            'passed': len(missing) == 0,
            'missing_entities': missing
        }

    def check_forbidden_phrases(self, response: str) -> Dict[str, Any]:
        """
        Check if response contains any forbidden phrases.

        Args:
            response: The response text to check

        Returns:
            Dictionary with passed status and found phrases
        """
        if not self.forbidden_phrases:
            return {'passed': True, 'found_phrases': []}

        found = []
        response_lower = response.lower()
        for phrase in self.forbidden_phrases:
            if phrase.lower() in response_lower:
                found.append(phrase)

        return {
            'passed': len(found) == 0,
            'found_phrases': found
        }

    def check_tone_requirement(self, response: str) -> Dict[str, Any]:
        """
        Check if response meets tone requirement.

        Args:
            response: The response text to check

        Returns:
            Dictionary with passed status and confidence
        """
        if not self.tone_requirement:
            return {'passed': True, 'confidence': 1.0}

        # Simple heuristic-based tone checking
        tone = self.tone_requirement.lower()
        confidence = 0.5  # Default confidence

        if tone == 'polite':
            polite_words = ['thank', 'please', 'appreciate', 'happy to', 'glad']
            matches = sum(1 for word in polite_words if word in response.lower())
            confidence = min(1.0, 0.5 + (matches * 0.1))
        elif tone == 'professional':
            professional_words = ['analysis', 'data', 'indicates', 'based on', 'result']
            matches = sum(1 for word in professional_words if word in response.lower())
            confidence = min(1.0, 0.5 + (matches * 0.1))

        return {
            'passed': confidence >= 0.5,
            'confidence': confidence
        }

    def check_response_length(self, response: str) -> Dict[str, Any]:
        """
        Check if response length is within limit.

        Args:
            response: The response text to check

        Returns:
            Dictionary with passed status and length info
        """
        actual_length = len(response)

        if not self.max_response_length:
            return {
                'passed': True,
                'actual_length': actual_length,
                'max_length': None
            }

        return {
            'passed': actual_length <= self.max_response_length,
            'actual_length': actual_length,
            'max_length': self.max_response_length
        }

    # =========================================================================
    # Multi-Path Methods
    # =========================================================================

    def get_next_step(self, success: bool) -> Optional[UUID]:
        """
        Get the next step based on validation result.

        Args:
            success: Whether validation succeeded

        Returns:
            UUID of next step or None
        """
        if success:
            return self.next_step_on_success
        return self.next_step_on_failure
