"""
Multi-turn Context Preservation Service for NLU testing.

This service provides testing and validation for context preservation
across multiple dialog turns in conversational AI systems.

Key features:
- Context window size testing
- Implicit reference resolution
- Topic switching detection
- Context reset scenarios

Example:
    >>> service = MultiTurnContextService()
    >>> result = service.test_context_window(test_cases, predictions)
    >>> print(f"Context retention: {result['accuracy']:.3f}")
"""

from typing import List, Dict, Any


class MultiTurnContextService:
    """
    Service for testing multi-turn context preservation.

    Provides test case generation and validation for context windows,
    implicit references, topic switching, and context resets.

    Example:
        >>> service = MultiTurnContextService()
        >>> cases = service.generate_implicit_test_cases()
        >>> print(f"Generated {len(cases)} test cases")
    """

    def __init__(self):
        """Initialize the multi-turn context service."""
        pass

    def test_context_window(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test context window size retention.

        Evaluates how well context is maintained across varying
        numbers of dialog turns.

        Args:
            test_cases: Test cases with varying context lengths
            predictions: Predicted context values

        Returns:
            Dictionary with context window metrics

        Example:
            >>> result = service.test_context_window(cases, preds)
            >>> print(f"Accuracy: {result['accuracy']:.3f}")
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_window_size': {}
            }

        total = len(test_cases)
        correct = 0
        by_size = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_context', {})
            predicted = pred.get('predicted_context', {})

            window_size = case.get('window_size', 0)
            if window_size not in by_size:
                by_size[window_size] = {'total': 0, 'correct': 0}

            by_size[window_size]['total'] += 1

            if self._match_context(expected, predicted):
                correct += 1
                by_size[window_size]['correct'] += 1

        # Calculate per-size accuracy
        for size in by_size:
            if by_size[size]['total'] > 0:
                by_size[size]['accuracy'] = (
                    by_size[size]['correct'] / by_size[size]['total']
                )

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_window_size': by_size
        }

    def _match_context(
        self,
        expected: Dict[str, Any],
        predicted: Dict[str, Any]
    ) -> bool:
        """Check if contexts match."""
        if not expected:
            return not predicted

        for key in expected:
            if key not in predicted:
                return False
            if expected[key] != predicted[key]:
                return False
        return True

    def test_implicit_reference(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test implicit reference resolution.

        Evaluates resolution of references that rely on context.

        Args:
            test_cases: Test cases with implicit references
            predictions: Resolved references

        Returns:
            Dictionary with implicit reference metrics

        Example:
            >>> result = service.test_implicit_reference(cases, preds)
        """
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
            expected = case.get('expected_resolution')
            actual = pred.get('resolved_reference')

            ref_type = case.get('reference_type', 'unknown')
            if ref_type not in by_type:
                by_type[ref_type] = {'total': 0, 'correct': 0}

            by_type[ref_type]['total'] += 1

            if expected == actual:
                correct += 1
                by_type[ref_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_reference_type': by_type
        }

    def generate_implicit_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for implicit reference testing.

        Returns:
            List of implicit reference test cases

        Example:
            >>> cases = service.generate_implicit_test_cases()
        """
        return [
            {
                'dialog': [
                    'Show me flights to Paris',
                    'What about the cheapest one?'
                ],
                'reference_type': 'superlative',
                'expected_resolution': 'cheapest flight to Paris'
            },
            {
                'dialog': [
                    'I want a pizza',
                    'Make it large'
                ],
                'reference_type': 'anaphora',
                'expected_resolution': 'large pizza'
            },
            {
                'dialog': [
                    'Book a table for 4',
                    'At the Italian place'
                ],
                'reference_type': 'ellipsis',
                'expected_resolution': 'table for 4 at Italian restaurant'
            },
            {
                'dialog': [
                    'What time does it open?'
                ],
                'context': {'entity': 'library'},
                'reference_type': 'context_dependent',
                'expected_resolution': 'library opening time'
            }
        ]

    def test_topic_switching(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test topic switching detection.

        Evaluates how well the system detects and handles topic changes.

        Args:
            test_cases: Test cases with topic switches
            predictions: Detected topic changes

        Returns:
            Dictionary with topic switching metrics

        Example:
            >>> result = service.test_topic_switching(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'detection_rate': 0.0
            }

        total = len(test_cases)
        correct = 0
        true_switches = 0
        detected_switches = 0

        for case, pred in zip(test_cases, predictions):
            has_switch = case.get('has_topic_switch', False)
            detected = pred.get('detected_switch', False)
            expected_topic = case.get('expected_new_topic')
            predicted_topic = pred.get('predicted_topic')

            if has_switch:
                true_switches += 1
                if detected:
                    detected_switches += 1
                    if expected_topic == predicted_topic:
                        correct += 1
            else:
                if not detected:
                    correct += 1

        detection_rate = (
            detected_switches / true_switches
        ) if true_switches > 0 else 0.0

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'detection_rate': float(detection_rate),
            'true_switches': true_switches,
            'detected_switches': detected_switches
        }

    def generate_topic_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for topic switching testing.

        Returns:
            List of topic switching test cases

        Example:
            >>> cases = service.generate_topic_test_cases()
        """
        return [
            {
                'dialog': [
                    'Book a flight to London',
                    "What's the weather like there?"
                ],
                'has_topic_switch': True,
                'expected_new_topic': 'weather'
            },
            {
                'dialog': [
                    'Order a pizza',
                    'With extra cheese',
                    'And mushrooms'
                ],
                'has_topic_switch': False,
                'current_topic': 'food_order'
            },
            {
                'dialog': [
                    'Set an alarm for 7am',
                    'Actually, remind me to call mom'
                ],
                'has_topic_switch': True,
                'expected_new_topic': 'reminder'
            },
            {
                'dialog': [
                    'Play some jazz music',
                    'By the way, turn off the lights'
                ],
                'has_topic_switch': True,
                'expected_new_topic': 'smart_home'
            }
        ]

    def test_context_reset(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test context reset scenarios.

        Evaluates how the system handles explicit and implicit resets.

        Args:
            test_cases: Test cases with reset scenarios
            predictions: Post-reset state predictions

        Returns:
            Dictionary with context reset metrics

        Example:
            >>> result = service.test_context_reset(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_reset_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected_state = case.get('expected_post_reset')
            actual_state = pred.get('post_reset_state')

            reset_type = case.get('reset_type', 'unknown')
            if reset_type not in by_type:
                by_type[reset_type] = {'total': 0, 'correct': 0}

            by_type[reset_type]['total'] += 1

            if self._match_context(expected_state, actual_state):
                correct += 1
                by_type[reset_type]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_reset_type': by_type
        }

    def generate_reset_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for context reset testing.

        Returns:
            List of context reset test cases

        Example:
            >>> cases = service.generate_reset_test_cases()
        """
        return [
            {
                'dialog': [
                    'Book a flight to Paris',
                    'Cancel',
                    'Start over'
                ],
                'reset_type': 'explicit',
                'expected_post_reset': {}
            },
            {
                'dialog': [
                    'Order a pizza',
                    'Never mind',
                    'I want Chinese instead'
                ],
                'reset_type': 'implicit_correction',
                'expected_post_reset': {'cuisine': 'Chinese'}
            },
            {
                'dialog': [
                    'Set timer for 10 minutes',
                    '[long pause]',
                    'Hello?'
                ],
                'reset_type': 'timeout',
                'expected_post_reset': {}
            },
            {
                'dialog': [
                    'Transfer $100 to John',
                    'Stop',
                    'Forget that'
                ],
                'reset_type': 'explicit_cancel',
                'expected_post_reset': {}
            }
        ]

    def get_context_metrics(
        self,
        window_results: Dict[str, Any],
        implicit_results: Dict[str, Any],
        switching_results: Dict[str, Any],
        reset_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive multi-turn context metrics.

        Args:
            window_results: Results from window testing
            implicit_results: Results from implicit reference testing
            switching_results: Results from topic switching testing
            reset_results: Results from reset testing

        Returns:
            Dictionary with overall context metrics

        Example:
            >>> metrics = service.get_context_metrics(
            ...     window, implicit, switching, reset
            ... )
        """
        # Calculate totals
        total_tests = (
            window_results.get('total', 0) +
            implicit_results.get('total', 0) +
            switching_results.get('total', 0) +
            reset_results.get('total', 0)
        )

        total_correct = (
            window_results.get('correct', 0) +
            implicit_results.get('correct', 0) +
            switching_results.get('correct', 0) +
            reset_results.get('correct', 0)
        )

        overall_accuracy = (
            total_correct / total_tests
        ) if total_tests > 0 else 0.0

        return {
            'overall_accuracy': float(overall_accuracy),
            'total_tests': total_tests,
            'total_correct': total_correct,
            'context_window': {
                'accuracy': window_results.get('accuracy', 0.0),
                'total': window_results.get('total', 0)
            },
            'implicit_reference': {
                'accuracy': implicit_results.get('accuracy', 0.0),
                'total': implicit_results.get('total', 0)
            },
            'topic_switching': {
                'accuracy': switching_results.get('accuracy', 0.0),
                'detection_rate': switching_results.get('detection_rate', 0.0),
                'total': switching_results.get('total', 0)
            },
            'context_reset': {
                'accuracy': reset_results.get('accuracy', 0.0),
                'total': reset_results.get('total', 0)
            },
            'quality_rating': (
                'excellent' if overall_accuracy > 0.9
                else 'good' if overall_accuracy > 0.8
                else 'fair' if overall_accuracy > 0.7
                else 'needs improvement'
            )
        }

