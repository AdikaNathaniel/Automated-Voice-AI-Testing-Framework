"""
Entity Resolution Testing Service for NLU testing.

This service provides testing and validation for entity resolution
in NLU systems including coreference, relative references, and
list entity disambiguation.

Key features:
- Coreference resolution testing ("it", "that", "there")
- Relative reference resolution ("next week", "tomorrow")
- List entity disambiguation

Example:
    >>> service = EntityResolutionService()
    >>> result = service.test_coreference_resolution(test_cases, predictions)
    >>> print(f"Resolution accuracy: {result['accuracy']:.3f}")
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta


class EntityResolutionService:
    """
    Service for testing entity resolution in NLU systems.

    Provides test case generation and validation for coreference
    resolution, relative references, and list disambiguation.

    Example:
        >>> service = EntityResolutionService()
        >>> cases = service.generate_coreference_test_cases()
        >>> print(f"Generated {len(cases)} test cases")
    """

    def __init__(self):
        """Initialize the entity resolution service."""
        pass

    def test_coreference_resolution(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test coreference resolution accuracy.

        Evaluates how well the system resolves pronouns and demonstratives
        to their antecedents.

        Args:
            test_cases: Test cases with context and expected resolution
            predictions: Predicted resolutions

        Returns:
            Dictionary with coreference resolution metrics

        Example:
            >>> result = service.test_coreference_resolution(cases, preds)
            >>> print(f"Accuracy: {result['accuracy']:.3f}")
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_pronoun_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_resolution')
            resolved = pred.get('resolved_entity')

            # Track by pronoun type
            pronoun_type = case.get('pronoun_type', 'unknown')
            if pronoun_type not in by_type:
                by_type[pronoun_type] = {'total': 0, 'correct': 0}

            by_type[pronoun_type]['total'] += 1

            if self._match_resolution(expected, resolved):
                correct += 1
                by_type[pronoun_type]['correct'] += 1

        # Calculate per-type accuracy
        for ptype in by_type:
            if by_type[ptype]['total'] > 0:
                by_type[ptype]['accuracy'] = (
                    by_type[ptype]['correct'] / by_type[ptype]['total']
                )
            else:
                by_type[ptype]['accuracy'] = 0.0

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_pronoun_type': by_type
        }

    def _match_resolution(
        self,
        expected: Any,
        resolved: Any
    ) -> bool:
        """Check if resolution matches expected."""
        if isinstance(expected, dict) and isinstance(resolved, dict):
            for key in expected:
                if key not in resolved:
                    return False
                if expected[key] != resolved[key]:
                    return False
            return True
        return str(expected).lower() == str(resolved).lower()

    def generate_coreference_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for coreference resolution.

        Returns:
            List of coreference test cases

        Example:
            >>> cases = service.generate_coreference_test_cases()
        """
        return [
            {
                'context': 'I want to book a flight to Paris.',
                'utterance': 'How much does it cost?',
                'pronoun': 'it',
                'pronoun_type': 'pronoun_it',
                'expected_resolution': {'entity': 'flight to Paris'}
            },
            {
                'context': 'Show me the red shirt.',
                'utterance': 'Add that to my cart.',
                'pronoun': 'that',
                'pronoun_type': 'demonstrative',
                'expected_resolution': {'entity': 'red shirt'}
            },
            {
                'context': 'I was looking at the Grand Hotel.',
                'utterance': 'Is there a pool?',
                'pronoun': 'there',
                'pronoun_type': 'location',
                'expected_resolution': {'entity': 'Grand Hotel'}
            },
            {
                'context': 'My order number is 12345.',
                'utterance': 'Can you cancel it?',
                'pronoun': 'it',
                'pronoun_type': 'pronoun_it',
                'expected_resolution': {'entity': 'order 12345'}
            },
            {
                'context': 'I need to talk to John.',
                'utterance': 'What is his phone number?',
                'pronoun': 'his',
                'pronoun_type': 'possessive',
                'expected_resolution': {'entity': 'John'}
            }
        ]

    def test_relative_reference(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Test relative reference resolution accuracy.

        Evaluates how well the system resolves temporal expressions.

        Args:
            test_cases: Test cases with relative expressions
            predictions: Resolved datetime values
            reference_date: Reference date for resolution

        Returns:
            Dictionary with relative reference metrics

        Example:
            >>> result = service.test_relative_reference(cases, preds)
        """
        if reference_date is None:
            reference_date = datetime.now()

        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_reference_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_datetime')
            resolved = pred.get('resolved_datetime')

            ref_type = case.get('reference_type', 'unknown')
            if ref_type not in by_type:
                by_type[ref_type] = {'total': 0, 'correct': 0}

            by_type[ref_type]['total'] += 1

            if self._match_datetime(expected, resolved):
                correct += 1
                by_type[ref_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_reference_type': by_type
        }

    def _match_datetime(
        self,
        expected: Dict[str, Any],
        resolved: Dict[str, Any]
    ) -> bool:
        """Check if datetime values match."""
        if not expected or not resolved:
            return expected == resolved

        for key in ['year', 'month', 'day', 'hour', 'minute']:
            if key in expected:
                if expected.get(key) != resolved.get(key):
                    return False
        return True

    def generate_relative_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for relative reference resolution.

        Returns:
            List of relative reference test cases

        Example:
            >>> cases = service.generate_relative_test_cases()
        """
        return [
            {
                'text': 'tomorrow',
                'reference_type': 'relative_day',
                'expected_datetime': {'offset_days': 1}
            },
            {
                'text': 'next week',
                'reference_type': 'relative_week',
                'expected_datetime': {'offset_weeks': 1}
            },
            {
                'text': 'yesterday',
                'reference_type': 'relative_day',
                'expected_datetime': {'offset_days': -1}
            },
            {
                'text': 'in 3 hours',
                'reference_type': 'relative_hours',
                'expected_datetime': {'offset_hours': 3}
            },
            {
                'text': 'this afternoon',
                'reference_type': 'time_of_day',
                'expected_datetime': {'time_of_day': 'afternoon'}
            },
            {
                'text': 'next Monday',
                'reference_type': 'relative_weekday',
                'expected_datetime': {'weekday': 0, 'next': True}
            },
            {
                'text': 'the day after tomorrow',
                'reference_type': 'relative_day',
                'expected_datetime': {'offset_days': 2}
            }
        ]

    def resolve_relative_datetime(
        self,
        expression: str,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Resolve a relative datetime expression to absolute values.

        Args:
            expression: Relative datetime expression
            reference_date: Reference date for resolution

        Returns:
            Dictionary with resolved datetime components

        Example:
            >>> result = service.resolve_relative_datetime("tomorrow")
        """
        if reference_date is None:
            reference_date = datetime.now()

        expression_lower = expression.lower().strip()

        # Simple resolution rules
        if expression_lower == 'tomorrow':
            resolved = reference_date + timedelta(days=1)
        elif expression_lower == 'yesterday':
            resolved = reference_date - timedelta(days=1)
        elif expression_lower == 'today':
            resolved = reference_date
        elif expression_lower == 'next week':
            resolved = reference_date + timedelta(weeks=1)
        elif expression_lower == 'last week':
            resolved = reference_date - timedelta(weeks=1)
        elif 'in' in expression_lower and 'hour' in expression_lower:
            # Extract number
            import re
            match = re.search(r'(\d+)', expression_lower)
            hours = int(match.group(1)) if match else 1
            resolved = reference_date + timedelta(hours=hours)
        elif 'in' in expression_lower and 'day' in expression_lower:
            import re
            match = re.search(r'(\d+)', expression_lower)
            days = int(match.group(1)) if match else 1
            resolved = reference_date + timedelta(days=days)
        else:
            resolved = reference_date

        return {
            'year': resolved.year,
            'month': resolved.month,
            'day': resolved.day,
            'hour': resolved.hour,
            'minute': resolved.minute,
            'expression': expression
        }

    def test_list_disambiguation(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test list entity disambiguation accuracy.

        Evaluates how well the system disambiguates between similar
        list entities.

        Args:
            test_cases: Test cases with ambiguous entities
            predictions: Disambiguated predictions

        Returns:
            Dictionary with disambiguation metrics

        Example:
            >>> result = service.test_list_disambiguation(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'ambiguity_resolved': 0
            }

        total = len(test_cases)
        correct = 0
        ambiguity_resolved = 0

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_entity')
            resolved = pred.get('resolved_entity')
            candidates = case.get('candidates', [])

            if expected == resolved:
                correct += 1
                if len(candidates) > 1:
                    ambiguity_resolved += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'ambiguity_resolved': ambiguity_resolved,
            'disambiguation_rate': float(
                ambiguity_resolved / total
            ) if total > 0 else 0.0
        }

    def generate_list_disambiguation_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for list entity disambiguation.

        Returns:
            List of disambiguation test cases

        Example:
            >>> cases = service.generate_list_disambiguation_cases()
        """
        return [
            {
                'text': 'Play songs by Jackson',
                'candidates': [
                    'Michael Jackson',
                    'Janet Jackson',
                    'Jackson 5'
                ],
                'context': 'User previously played Thriller',
                'expected_entity': 'Michael Jackson'
            },
            {
                'text': 'Call John',
                'candidates': [
                    'John Smith (Work)',
                    'John Smith (Home)',
                    'John Doe'
                ],
                'context': 'Currently during work hours',
                'expected_entity': 'John Smith (Work)'
            },
            {
                'text': 'Navigate to the bank',
                'candidates': [
                    'First National Bank',
                    'City Bank',
                    'River Bank Park'
                ],
                'context': 'User needs to deposit money',
                'expected_entity': 'First National Bank'
            },
            {
                'text': 'Order the usual',
                'candidates': [
                    'Large pepperoni pizza',
                    'Medium cheese pizza',
                    'Caesar salad'
                ],
                'context': 'User order history shows large pepperoni',
                'expected_entity': 'Large pepperoni pizza'
            }
        ]

    def get_resolution_metrics(
        self,
        coreference_results: Dict[str, Any],
        relative_results: Dict[str, Any],
        disambiguation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive entity resolution metrics.

        Args:
            coreference_results: Results from coreference testing
            relative_results: Results from relative reference testing
            disambiguation_results: Results from disambiguation testing

        Returns:
            Dictionary with overall resolution metrics

        Example:
            >>> metrics = service.get_resolution_metrics(
            ...     coref_results, rel_results, disamb_results
            ... )
        """
        # Calculate totals
        total_tests = (
            coreference_results.get('total', 0) +
            relative_results.get('total', 0) +
            disambiguation_results.get('total', 0)
        )

        total_correct = (
            coreference_results.get('correct', 0) +
            relative_results.get('correct', 0) +
            disambiguation_results.get('correct', 0)
        )

        overall_accuracy = (
            total_correct / total_tests
        ) if total_tests > 0 else 0.0

        return {
            'overall_accuracy': float(overall_accuracy),
            'total_tests': total_tests,
            'total_correct': total_correct,
            'coreference': {
                'accuracy': coreference_results.get('accuracy', 0.0),
                'total': coreference_results.get('total', 0),
                'correct': coreference_results.get('correct', 0)
            },
            'relative_reference': {
                'accuracy': relative_results.get('accuracy', 0.0),
                'total': relative_results.get('total', 0),
                'correct': relative_results.get('correct', 0)
            },
            'disambiguation': {
                'accuracy': disambiguation_results.get('accuracy', 0.0),
                'total': disambiguation_results.get('total', 0),
                'correct': disambiguation_results.get('correct', 0)
            },
            'quality_rating': (
                'excellent' if overall_accuracy > 0.9
                else 'good' if overall_accuracy > 0.8
                else 'fair' if overall_accuracy > 0.7
                else 'needs improvement'
            )
        }

