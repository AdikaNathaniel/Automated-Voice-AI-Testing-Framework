"""
Disambiguation Handling Service for NLU testing.

This service provides testing and validation for disambiguation
handling in conversational AI systems.

Key features:
- Clarification question generation
- User correction handling
- Implicit vs explicit disambiguation

Example:
    >>> service = DisambiguationHandlingService()
    >>> result = service.test_clarification_generation(test_cases, predictions)
    >>> print(f"Clarification accuracy: {result['accuracy']:.3f}")
"""

from typing import List, Dict, Any


class DisambiguationHandlingService:
    """
    Service for testing disambiguation handling in conversational systems.

    Provides test case generation and validation for clarification
    questions, user corrections, and disambiguation strategies.

    Example:
        >>> service = DisambiguationHandlingService()
        >>> cases = service.generate_clarification_test_cases()
        >>> print(f"Generated {len(cases)} test cases")
    """

    def __init__(self):
        """Initialize the disambiguation handling service."""
        pass

    def test_clarification_generation(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test clarification question generation.

        Evaluates the quality and appropriateness of generated
        clarification questions.

        Args:
            test_cases: Test cases requiring clarification
            predictions: Generated clarification questions

        Returns:
            Dictionary with clarification generation metrics

        Example:
            >>> result = service.test_clarification_generation(cases, preds)
            >>> print(f"Accuracy: {result['accuracy']:.3f}")
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_ambiguity_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            needs_clarification = case.get('needs_clarification', True)
            generated = pred.get('generated_clarification')

            ambiguity_type = case.get('ambiguity_type', 'unknown')
            if ambiguity_type not in by_type:
                by_type[ambiguity_type] = {'total': 0, 'correct': 0}

            by_type[ambiguity_type]['total'] += 1

            # Check if clarification was appropriately generated
            if needs_clarification and generated:
                # Check if it asks about the right thing
                expected_topic = case.get('expected_clarification_topic')
                if self._check_clarification(generated, expected_topic):
                    correct += 1
                    by_type[ambiguity_type]['correct'] += 1
            elif not needs_clarification and not generated:
                correct += 1
                by_type[ambiguity_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_ambiguity_type': by_type
        }

    def _check_clarification(
        self,
        generated: str,
        expected_topic: str
    ) -> bool:
        """Check if clarification asks about expected topic."""
        if not expected_topic:
            return bool(generated)
        return expected_topic.lower() in generated.lower()

    def generate_clarification_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for clarification generation.

        Returns:
            List of clarification test cases

        Example:
            >>> cases = service.generate_clarification_test_cases()
        """
        return [
            {
                'utterance': 'Play Jackson',
                'ambiguity_type': 'entity_ambiguity',
                'needs_clarification': True,
                'candidates': ['Michael Jackson', 'Janet Jackson', 'Jackson 5'],
                'expected_clarification_topic': 'which Jackson'
            },
            {
                'utterance': 'Call John',
                'ambiguity_type': 'entity_ambiguity',
                'needs_clarification': True,
                'candidates': ['John (Work)', 'John (Home)', 'John Doe'],
                'expected_clarification_topic': 'which John'
            },
            {
                'utterance': 'Book a flight',
                'ambiguity_type': 'missing_info',
                'needs_clarification': True,
                'missing': ['destination', 'date'],
                'expected_clarification_topic': 'destination'
            },
            {
                'utterance': 'Play Bohemian Rhapsody by Queen',
                'ambiguity_type': 'none',
                'needs_clarification': False
            }
        ]

    def test_correction_handling(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test user correction handling.

        Evaluates how well the system handles user corrections.

        Args:
            test_cases: Test cases with user corrections
            predictions: System responses to corrections

        Returns:
            Dictionary with correction handling metrics

        Example:
            >>> result = service.test_correction_handling(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_correction_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected_state = case.get('expected_corrected_state', {})
            actual_state = pred.get('corrected_state', {})

            correction_type = case.get('correction_type', 'unknown')
            if correction_type not in by_type:
                by_type[correction_type] = {'total': 0, 'correct': 0}

            by_type[correction_type]['total'] += 1

            if self._match_state(expected_state, actual_state):
                correct += 1
                by_type[correction_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_correction_type': by_type
        }

    def _match_state(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any]
    ) -> bool:
        """Check if states match."""
        for key in expected:
            if key not in actual:
                return False
            if expected[key] != actual[key]:
                return False
        return True

    def generate_correction_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for correction handling.

        Returns:
            List of correction handling test cases

        Example:
            >>> cases = service.generate_correction_test_cases()
        """
        return [
            {
                'dialog': [
                    'Book flight to Paris',
                    'No, I meant London'
                ],
                'correction_type': 'explicit_correction',
                'expected_corrected_state': {'destination': 'London'}
            },
            {
                'dialog': [
                    'Set alarm for 7am',
                    "That's wrong, I said 7pm"
                ],
                'correction_type': 'explicit_negation',
                'expected_corrected_state': {'time': '7pm'}
            },
            {
                'dialog': [
                    'Order a large pizza',
                    'Actually make it medium'
                ],
                'correction_type': 'soft_correction',
                'expected_corrected_state': {'size': 'medium'}
            },
            {
                'dialog': [
                    'Send message to Mom',
                    'I meant to Dad'
                ],
                'correction_type': 'implicit_correction',
                'expected_corrected_state': {'recipient': 'Dad'}
            }
        ]

    def test_disambiguation(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test implicit vs explicit disambiguation.

        Evaluates disambiguation strategies used by the system.

        Args:
            test_cases: Test cases with ambiguous input
            predictions: Disambiguation results

        Returns:
            Dictionary with disambiguation metrics

        Example:
            >>> result = service.test_disambiguation(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'implicit_rate': 0.0,
                'explicit_rate': 0.0
            }

        total = len(test_cases)
        correct = 0
        implicit_count = 0
        explicit_count = 0

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_resolution')
            actual = pred.get('resolution')
            strategy = pred.get('disambiguation_strategy')

            if strategy == 'implicit':
                implicit_count += 1
            elif strategy == 'explicit':
                explicit_count += 1

            if expected == actual:
                correct += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'implicit_count': implicit_count,
            'explicit_count': explicit_count,
            'implicit_rate': float(implicit_count / total) if total > 0 else 0.0,
            'explicit_rate': float(explicit_count / total) if total > 0 else 0.0
        }

    def generate_disambiguation_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for disambiguation testing.

        Returns:
            List of disambiguation test cases

        Example:
            >>> cases = service.generate_disambiguation_test_cases()
        """
        return [
            {
                'utterance': 'Turn on the light',
                'context': {'room': 'living room', 'lights': ['main', 'lamp']},
                'expected_strategy': 'implicit',
                'expected_resolution': 'main_light'
            },
            {
                'utterance': 'Call John',
                'context': {'contacts': ['John Smith', 'John Doe']},
                'expected_strategy': 'explicit',
                'expected_resolution': None,
                'expected_clarification': True
            },
            {
                'utterance': 'Play my favorite song',
                'context': {'user_history': {'top_song': 'Bohemian Rhapsody'}},
                'expected_strategy': 'implicit',
                'expected_resolution': 'Bohemian Rhapsody'
            },
            {
                'utterance': 'Navigate to the bank',
                'context': {'nearby': ['First National', 'City Bank']},
                'expected_strategy': 'explicit',
                'expected_clarification': True
            }
        ]

    def get_disambiguation_metrics(
        self,
        clarification_results: Dict[str, Any],
        correction_results: Dict[str, Any],
        disambiguation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive disambiguation handling metrics.

        Args:
            clarification_results: Results from clarification testing
            correction_results: Results from correction testing
            disambiguation_results: Results from disambiguation testing

        Returns:
            Dictionary with overall disambiguation metrics

        Example:
            >>> metrics = service.get_disambiguation_metrics(
            ...     clarif, correct, disamb
            ... )
        """
        # Calculate totals
        total_tests = (
            clarification_results.get('total', 0) +
            correction_results.get('total', 0) +
            disambiguation_results.get('total', 0)
        )

        total_correct = (
            clarification_results.get('correct', 0) +
            correction_results.get('correct', 0) +
            disambiguation_results.get('correct', 0)
        )

        overall_accuracy = (
            total_correct / total_tests
        ) if total_tests > 0 else 0.0

        return {
            'overall_accuracy': float(overall_accuracy),
            'total_tests': total_tests,
            'total_correct': total_correct,
            'clarification': {
                'accuracy': clarification_results.get('accuracy', 0.0),
                'total': clarification_results.get('total', 0)
            },
            'correction': {
                'accuracy': correction_results.get('accuracy', 0.0),
                'total': correction_results.get('total', 0)
            },
            'disambiguation': {
                'accuracy': disambiguation_results.get('accuracy', 0.0),
                'implicit_rate': disambiguation_results.get('implicit_rate', 0.0),
                'explicit_rate': disambiguation_results.get('explicit_rate', 0.0),
                'total': disambiguation_results.get('total', 0)
            },
            'quality_rating': (
                'excellent' if overall_accuracy > 0.9
                else 'good' if overall_accuracy > 0.8
                else 'fair' if overall_accuracy > 0.7
                else 'needs improvement'
            )
        }

