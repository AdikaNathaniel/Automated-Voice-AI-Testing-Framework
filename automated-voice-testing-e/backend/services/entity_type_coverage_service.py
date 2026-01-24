"""
Entity Type Coverage Service for NLU testing.

This service provides testing and validation for various entity types
in NLU systems including date/time, duration, location, numeric,
custom, and composite entities.

Key features:
- Generate test cases for each entity type
- Validate entity extraction accuracy
- Support custom and composite entities

Example:
    >>> service = EntityTypeCoverageService()
    >>> result = service.test_datetime_entity(test_cases, predictions)
    >>> print(f"DateTime accuracy: {result['accuracy']:.3f}")
"""

from typing import List, Dict, Any, Optional

# Import extended entity mixin
from services.entity_type_extended import EntityTypeExtendedMixin


class EntityTypeCoverageService(EntityTypeExtendedMixin):
    """
    Service for testing entity type coverage in NLU systems.

    Provides test case generation and validation for various
    entity types including date/time, duration, location, and numeric.

    Example:
        >>> service = EntityTypeCoverageService()
        >>> cases = service.generate_datetime_test_cases()
        >>> print(f"Generated {len(cases)} test cases")
    """

    def __init__(self):
        """Initialize the entity type coverage service."""
        self._custom_entity_types: Dict[str, Dict[str, Any]] = {}

    def test_datetime_entity(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test date/time entity extraction accuracy.

        Args:
            test_cases: List of test cases with 'text' and 'expected' fields
            predictions: List of predictions with 'extracted' field

        Returns:
            Dictionary with datetime entity metrics

        Example:
            >>> result = service.test_datetime_entity(cases, predictions)
            >>> print(f"Accuracy: {result['accuracy']:.3f}")
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_format': {}
            }

        total = len(test_cases)
        correct = 0
        by_format = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected', {})
            extracted = pred.get('extracted', {})

            # Determine format type
            format_type = case.get('format', 'unknown')
            if format_type not in by_format:
                by_format[format_type] = {'total': 0, 'correct': 0}

            by_format[format_type]['total'] += 1

            # Compare datetime values
            if self._compare_datetime(expected, extracted):
                correct += 1
                by_format[format_type]['correct'] += 1

        # Calculate per-format accuracy
        for fmt in by_format:
            if by_format[fmt]['total'] > 0:
                by_format[fmt]['accuracy'] = (
                    by_format[fmt]['correct'] / by_format[fmt]['total']
                )
            else:
                by_format[fmt]['accuracy'] = 0.0

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_format': by_format
        }

    def _compare_datetime(
        self,
        expected: Dict[str, Any],
        extracted: Dict[str, Any]
    ) -> bool:
        """Compare datetime values."""
        # Compare year, month, day, hour, minute
        for key in ['year', 'month', 'day', 'hour', 'minute']:
            if key in expected:
                if expected.get(key) != extracted.get(key):
                    return False
        return True

    def generate_datetime_test_cases(
        self,
        formats: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for datetime entity extraction.

        Args:
            formats: Optional list of formats to generate

        Returns:
            List of test case dictionaries

        Example:
            >>> cases = service.generate_datetime_test_cases()
        """
        if formats is None:
            formats = [
                'absolute', 'relative', 'partial',
                'informal', 'iso8601'
            ]

        test_cases = []

        if 'absolute' in formats:
            test_cases.extend([
                {
                    'text': 'January 15, 2024',
                    'expected': {'year': 2024, 'month': 1, 'day': 15},
                    'format': 'absolute'
                },
                {
                    'text': '03/20/2024',
                    'expected': {'year': 2024, 'month': 3, 'day': 20},
                    'format': 'absolute'
                },
                {
                    'text': 'December 25th at 3pm',
                    'expected': {'month': 12, 'day': 25, 'hour': 15},
                    'format': 'absolute'
                }
            ])

        if 'relative' in formats:
            test_cases.extend([
                {
                    'text': 'tomorrow',
                    'expected': {'relative': 'tomorrow'},
                    'format': 'relative'
                },
                {
                    'text': 'next week',
                    'expected': {'relative': 'next_week'},
                    'format': 'relative'
                },
                {
                    'text': 'in 3 days',
                    'expected': {'relative': 'in_days', 'value': 3},
                    'format': 'relative'
                }
            ])

        if 'partial' in formats:
            test_cases.extend([
                {
                    'text': 'March',
                    'expected': {'month': 3},
                    'format': 'partial'
                },
                {
                    'text': '2024',
                    'expected': {'year': 2024},
                    'format': 'partial'
                }
            ])

        if 'informal' in formats:
            test_cases.extend([
                {
                    'text': 'this afternoon',
                    'expected': {'time_of_day': 'afternoon'},
                    'format': 'informal'
                },
                {
                    'text': 'tonight',
                    'expected': {'time_of_day': 'night'},
                    'format': 'informal'
                }
            ])

        if 'iso8601' in formats:
            test_cases.extend([
                {
                    'text': '2024-01-15T14:30:00',
                    'expected': {
                        'year': 2024, 'month': 1, 'day': 15,
                        'hour': 14, 'minute': 30
                    },
                    'format': 'iso8601'
                }
            ])

        return test_cases

    def test_duration_entity(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test duration entity extraction accuracy.

        Args:
            test_cases: Test cases with expected durations
            predictions: Extracted predictions

        Returns:
            Dictionary with duration entity metrics

        Example:
            >>> result = service.test_duration_entity(cases, predictions)
        """
        if not test_cases:
            return {'accuracy': 0.0, 'total': 0, 'correct': 0}

        total = len(test_cases)
        correct = 0

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected', {})
            extracted = pred.get('extracted', {})

            # Compare duration components
            if self._compare_duration(expected, extracted):
                correct += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct
        }

    def _compare_duration(
        self,
        expected: Dict[str, Any],
        extracted: Dict[str, Any]
    ) -> bool:
        """Compare duration values."""
        for unit in ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds']:
            if unit in expected:
                if expected.get(unit) != extracted.get(unit):
                    return False
        return True

    def generate_duration_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for duration entity extraction.

        Returns:
            List of duration test cases

        Example:
            >>> cases = service.generate_duration_test_cases()
        """
        return [
            {
                'text': '2 hours',
                'expected': {'hours': 2}
            },
            {
                'text': '30 minutes',
                'expected': {'minutes': 30}
            },
            {
                'text': '1 hour and 30 minutes',
                'expected': {'hours': 1, 'minutes': 30}
            },
            {
                'text': '3 days',
                'expected': {'days': 3}
            },
            {
                'text': '2 weeks',
                'expected': {'weeks': 2}
            },
            {
                'text': 'half an hour',
                'expected': {'minutes': 30}
            },
            {
                'text': 'a quarter of an hour',
                'expected': {'minutes': 15}
            }
        ]

    def test_numeric_entity(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test numeric entity extraction accuracy.

        Args:
            test_cases: Test cases with expected numeric values
            predictions: Extracted predictions

        Returns:
            Dictionary with numeric entity metrics

        Example:
            >>> result = service.test_numeric_entity(cases, predictions)
        """
        if not test_cases:
            return {'accuracy': 0.0, 'total': 0, 'correct': 0}

        total = len(test_cases)
        correct = 0

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected', {})
            extracted = pred.get('extracted', {})

            exp_value = expected.get('value')
            ext_value = extracted.get('value')

            # Handle numeric comparison
            try:
                if float(exp_value) == float(ext_value):
                    correct += 1
            except (TypeError, ValueError):
                if str(exp_value) == str(ext_value):
                    correct += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct
        }

    def generate_numeric_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for numeric entity extraction.

        Returns:
            List of numeric test cases

        Example:
            >>> cases = service.generate_numeric_test_cases()
        """
        return [
            {'text': 'five', 'expected': {'value': 5}},
            {'text': '42', 'expected': {'value': 42}},
            {'text': 'three hundred', 'expected': {'value': 300}},
            {'text': '1,000', 'expected': {'value': 1000}},
            {'text': '3.14', 'expected': {'value': 3.14}},
            {'text': 'a dozen', 'expected': {'value': 12}},
            {'text': 'half', 'expected': {'value': 0.5}},
            {'text': 'twenty-one', 'expected': {'value': 21}}
        ]


