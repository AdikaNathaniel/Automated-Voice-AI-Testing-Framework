"""
Entity Type Extended Mixin for location, custom, and composite entities.

This mixin provides extended entity testing methods for EntityTypeCoverageService:
- Location entity testing
- Custom entity testing and registration
- Composite entity testing
- Coverage metrics

Extracted from entity_type_coverage_service.py to maintain 500-line limit per file.

Example:
    >>> class EntityTypeCoverageService(EntityTypeExtendedMixin):
    ...     pass
"""

from typing import List, Dict, Any, Optional, Callable


class EntityTypeExtendedMixin:
    """
    Mixin providing extended entity testing methods.

    This mixin contains:
    - Location entity methods
    - Custom entity methods
    - Composite entity methods
    - Coverage metrics methods
    """

    def test_location_entity(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test location entity extraction accuracy.

        Args:
            test_cases: Test cases with expected locations
            predictions: Extracted predictions

        Returns:
            Dictionary with location entity metrics

        Example:
            >>> result = service.test_location_entity(cases, predictions)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected', {})
            extracted = pred.get('extracted', {})

            loc_type = case.get('location_type', 'unknown')
            if loc_type not in by_type:
                by_type[loc_type] = {'total': 0, 'correct': 0}

            by_type[loc_type]['total'] += 1

            if self._compare_location(expected, extracted):
                correct += 1
                by_type[loc_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_type': by_type
        }

    def _compare_location(
        self,
        expected: Dict[str, Any],
        extracted: Dict[str, Any]
    ) -> bool:
        """Compare location values."""
        for key in ['city', 'state', 'country', 'street', 'zip']:
            if key in expected:
                exp_val = str(expected.get(key, '')).lower()
                ext_val = str(extracted.get(key, '')).lower()
                if exp_val != ext_val:
                    return False
        return True

    def generate_location_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for location entity extraction.

        Returns:
            List of location test cases

        Example:
            >>> cases = service.generate_location_test_cases()
        """
        return [
            {
                'text': 'New York City',
                'expected': {'city': 'New York City'},
                'location_type': 'city'
            },
            {
                'text': 'California',
                'expected': {'state': 'California'},
                'location_type': 'state'
            },
            {
                'text': '123 Main Street',
                'expected': {'street': '123 Main Street'},
                'location_type': 'address'
            },
            {
                'text': 'Paris, France',
                'expected': {'city': 'Paris', 'country': 'France'},
                'location_type': 'city_country'
            },
            {
                'text': '90210',
                'expected': {'zip': '90210'},
                'location_type': 'zip'
            }
        ]

    def test_custom_entity(
        self,
        entity_type: str,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test custom entity extraction accuracy.

        Args:
            entity_type: Name of the custom entity type
            test_cases: Test cases for this entity type
            predictions: Extracted predictions

        Returns:
            Dictionary with custom entity metrics

        Example:
            >>> result = service.test_custom_entity('product', cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'entity_type': entity_type
            }

        total = len(test_cases)
        correct = 0

        # Get custom validator if registered
        validator = None
        if entity_type in self._custom_entity_types:
            validator = self._custom_entity_types[entity_type].get('validator')

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected')
            extracted = pred.get('extracted')

            if validator:
                if validator(expected, extracted):
                    correct += 1
            elif expected == extracted:
                correct += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'entity_type': entity_type
        }

    def register_custom_entity_type(
        self,
        entity_type: str,
        validator: Optional[Callable] = None,
        normalizer: Optional[Callable] = None,
        examples: Optional[List[str]] = None
    ) -> None:
        """
        Register a custom entity type for testing.

        Args:
            entity_type: Name of the entity type
            validator: Optional validation function
            normalizer: Optional normalization function
            examples: Optional list of example values

        Example:
            >>> service.register_custom_entity_type(
            ...     'product_id',
            ...     validator=lambda e, p: e == p.upper()
            ... )
        """
        self._custom_entity_types[entity_type] = {
            'validator': validator,
            'normalizer': normalizer,
            'examples': examples or []
        }

    def test_composite_entity(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test composite entity extraction accuracy.

        Composite entities combine multiple sub-entities.

        Args:
            test_cases: Test cases with composite entities
            predictions: Extracted predictions

        Returns:
            Dictionary with composite entity metrics

        Example:
            >>> result = service.test_composite_entity(cases, predictions)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'partial_matches': 0
            }

        total = len(test_cases)
        correct = 0
        partial = 0

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected', {})
            extracted = pred.get('extracted', {})

            # Count matching sub-entities
            exp_keys = set(expected.keys())
            ext_keys = set(extracted.keys())

            common_keys = exp_keys & ext_keys
            matching = sum(
                1 for k in common_keys
                if expected[k] == extracted[k]
            )

            if matching == len(exp_keys) and len(exp_keys) > 0:
                correct += 1
            elif matching > 0:
                partial += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'partial_matches': partial,
            'partial_match_rate': float(
                (correct + partial) / total
            ) if total > 0 else 0.0
        }

    def generate_composite_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for composite entity extraction.

        Returns:
            List of composite entity test cases

        Example:
            >>> cases = service.generate_composite_test_cases()
        """
        return [
            {
                'text': 'Flight from New York to Los Angeles on January 15',
                'expected': {
                    'origin': 'New York',
                    'destination': 'Los Angeles',
                    'date': {'month': 1, 'day': 15}
                }
            },
            {
                'text': 'Book a room for 2 adults from March 1 to March 5',
                'expected': {
                    'guests': 2,
                    'check_in': {'month': 3, 'day': 1},
                    'check_out': {'month': 3, 'day': 5}
                }
            },
            {
                'text': 'Order 3 pizzas to 123 Main St at 7pm',
                'expected': {
                    'quantity': 3,
                    'item': 'pizza',
                    'address': '123 Main St',
                    'time': {'hour': 19}
                }
            }
        ]

    def get_entity_coverage_metrics(
        self,
        test_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get comprehensive entity coverage metrics.

        Args:
            test_results: Dictionary of test results by entity type

        Returns:
            Dictionary with overall coverage metrics

        Example:
            >>> metrics = service.get_entity_coverage_metrics(results)
            >>> print(f"Overall accuracy: {metrics['overall_accuracy']:.3f}")
        """
        if not test_results:
            return {
                'overall_accuracy': 0.0,
                'entity_types_tested': 0,
                'total_tests': 0,
                'total_correct': 0,
                'per_type': {}
            }

        total_tests = 0
        total_correct = 0
        per_type = {}

        for entity_type, results in test_results.items():
            tests = results.get('total', 0)
            correct = results.get('correct', 0)

            total_tests += tests
            total_correct += correct

            per_type[entity_type] = {
                'accuracy': results.get('accuracy', 0.0),
                'total': tests,
                'correct': correct
            }

        overall_accuracy = (
            total_correct / total_tests
        ) if total_tests > 0 else 0.0

        # Calculate coverage score
        entity_types_tested = len(test_results)
        coverage_score = min(1.0, entity_types_tested / 6)  # 6 main types

        return {
            'overall_accuracy': float(overall_accuracy),
            'entity_types_tested': entity_types_tested,
            'total_tests': total_tests,
            'total_correct': total_correct,
            'per_type': per_type,
            'coverage_score': float(coverage_score),
            'quality_rating': (
                'excellent' if overall_accuracy > 0.9 and coverage_score > 0.8
                else 'good' if overall_accuracy > 0.8 and coverage_score > 0.6
                else 'fair' if overall_accuracy > 0.7 and coverage_score > 0.4
                else 'needs improvement'
            )
        }
