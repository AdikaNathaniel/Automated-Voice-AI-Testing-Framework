"""
DynamicReferenceService for resolving contextual references.

This service handles resolution of dynamic references like:
- "the first one", "second result", "last option"
- "yes, that one", "confirm selection"
- Numeric references like "number 2", "option 3"
"""

import re
from typing import Any, Dict

import logging

logger = logging.getLogger(__name__)


class DynamicReferenceService:
    """
    Service for resolving dynamic contextual references.

    Handles ordinal, confirmation, and numeric reference patterns
    against a context of search results or current selections.
    """

    # Ordinal word to number mapping
    ORDINAL_MAP = {
        'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
        'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
        'last': -1
    }

    # Cardinal word to number mapping
    CARDINAL_MAP = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
    }

    # Confirmation patterns
    CONFIRMATION_PATTERNS = [
        r'\byes\b.*\bthat\s+one\b',
        r'\bconfirm\s+selection\b',
        r'\bthat\'s?\s+(the\s+)?one\b',
        r'\byes\b.*\bcorrect\b',
        r'\bconfirm\b'
    ]

    def __init__(self) -> None:
        """Initialize the dynamic reference service."""
        self._context: Dict[str, Any] = {}
        logger.info("DynamicReferenceService initialized")

    def set_context(self, context: Dict[str, Any]) -> None:
        """
        Set or update the context for reference resolution.

        Args:
            context: Dictionary with search_results, current_selection, etc.
        """
        self._context.update(context)
        logger.debug(f"Context updated: {list(context.keys())}")

    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context.

        Returns:
            Current context dictionary
        """
        return self._context

    def clear_context(self) -> None:
        """Clear the current context."""
        self._context = {}
        logger.debug("Context cleared")

    def resolve_reference(self, reference: str) -> Dict[str, Any]:
        """
        Resolve a dynamic reference to a concrete entity.

        Args:
            reference: The reference text (e.g., "the first one")

        Returns:
            Dictionary with resolved status, entity, and metadata
        """
        # Detect the pattern type
        pattern = self.detect_pattern(reference)

        if pattern['type'] == 'ordinal':
            return self._resolve_ordinal(pattern['value'])
        elif pattern['type'] == 'numeric':
            return self._resolve_ordinal(pattern['value'])
        elif pattern['type'] == 'confirmation':
            return self._resolve_confirmation()
        else:
            return {
                'resolved': False,
                'error': f'Unrecognized reference pattern: {reference}'
            }

    def detect_pattern(self, reference: str) -> Dict[str, Any]:
        """
        Detect the pattern type in a reference.

        Args:
            reference: The reference text

        Returns:
            Dictionary with pattern type and value
        """
        ref_lower = reference.lower()

        # Check for ordinal patterns
        for word, value in self.ORDINAL_MAP.items():
            if word in ref_lower:
                return {'type': 'ordinal', 'value': value}

        # Check for numeric patterns (number X, option X)
        numeric_match = re.search(r'\b(number|option)\s*(\d+)\b', ref_lower)
        if numeric_match:
            return {'type': 'numeric', 'value': int(numeric_match.group(2))}

        # Check for word-based numeric patterns (number one, option two)
        for word, value in self.CARDINAL_MAP.items():
            word_match = re.search(rf'\b(number|option)\s+{word}\b', ref_lower)
            if word_match:
                return {'type': 'numeric', 'value': value}

        # Check for confirmation patterns
        for pattern in self.CONFIRMATION_PATTERNS:
            if re.search(pattern, ref_lower):
                return {'type': 'confirmation', 'value': None}

        return {'type': 'unknown', 'value': None}

    def validate_selection(
        self,
        reference: str,
        selected_entity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that the selected entity matches the reference.

        Args:
            reference: The reference text
            selected_entity: The entity that was selected by the system

        Returns:
            Dictionary with validity status and details
        """
        # Resolve what the reference should point to
        resolved = self.resolve_reference(reference)

        if not resolved.get('resolved'):
            return {
                'valid': False,
                'error': resolved.get('error', 'Could not resolve reference')
            }

        expected_entity = resolved['entity']

        # Compare entities (allow partial match)
        if self._entities_match(expected_entity, selected_entity):
            return {'valid': True}
        else:
            return {
                'valid': False,
                'expected': expected_entity,
                'actual': selected_entity
            }

    def _resolve_ordinal(self, ordinal_value: int) -> Dict[str, Any]:
        """
        Resolve an ordinal reference to an entity.

        Args:
            ordinal_value: The ordinal position (1-based, -1 for last)

        Returns:
            Resolution result
        """
        search_results = self._context.get('search_results', [])

        if not search_results:
            return {
                'resolved': False,
                'error': 'No search results in context'
            }

        # Handle "last" reference
        if ordinal_value == -1:
            index = len(search_results) - 1
        else:
            index = ordinal_value - 1  # Convert to 0-based

        # Check bounds
        if index < 0 or index >= len(search_results):
            return {
                'resolved': False,
                'error': f'Index {ordinal_value} out of range (1-{len(search_results)})'
            }

        return {
            'resolved': True,
            'entity': search_results[index],
            'index': index
        }

    def _resolve_confirmation(self) -> Dict[str, Any]:
        """
        Resolve a confirmation reference to the current selection.

        Returns:
            Resolution result
        """
        current_selection = self._context.get('current_selection')

        if not current_selection:
            return {
                'resolved': False,
                'error': 'No current selection to confirm'
            }

        return {
            'resolved': True,
            'confirmed': True,
            'entity': current_selection
        }

    def _entities_match(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> bool:
        """
        Check if two entities match (allowing partial match).

        Args:
            expected: Expected entity
            actual: Actual entity

        Returns:
            True if entities match
        """
        # Check if all keys in actual exist in expected with same values
        for key, value in actual.items():
            if key in expected and expected[key] != value:
                return False

        # If actual has a 'name' or 'id', it must match
        if 'name' in actual and 'name' in expected:
            if actual['name'] != expected['name']:
                return False

        if 'id' in actual and 'id' in expected:
            if actual['id'] != expected['id']:
                return False

        return True


# Singleton instance
dynamic_reference_service = DynamicReferenceService()
