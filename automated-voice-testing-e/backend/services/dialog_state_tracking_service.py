"""
Dialog State Tracking Service for NLU testing.

This service provides testing and validation for dialog state
management in conversational AI systems.

Key features:
- State transition accuracy testing
- Context carryover validation
- State recovery after errors
- Session timeout handling

Example:
    >>> service = DialogStateTrackingService()
    >>> result = service.test_state_transitions(test_cases, predictions)
    >>> print(f"Transition accuracy: {result['accuracy']:.3f}")
"""

from typing import List, Dict, Any


class DialogStateTrackingService:
    """
    Service for testing dialog state tracking in conversational systems.

    Provides test case generation and validation for state transitions,
    context carryover, recovery, and timeout handling.

    Example:
        >>> service = DialogStateTrackingService()
        >>> cases = service.generate_transition_test_cases()
        >>> print(f"Generated {len(cases)} test cases")
    """

    def __init__(self):
        """Initialize the dialog state tracking service."""
        pass

    def test_state_transitions(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test state transition accuracy.

        Evaluates how accurately the system tracks dialog state changes.

        Args:
            test_cases: Test cases with expected state transitions
            predictions: Predicted state transitions

        Returns:
            Dictionary with state transition metrics

        Example:
            >>> result = service.test_state_transitions(cases, preds)
            >>> print(f"Accuracy: {result['accuracy']:.3f}")
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_transition_type': {}
            }

        total = len(test_cases)
        correct = 0
        by_type = {}

        for case, pred in zip(test_cases, predictions):
            expected_state = case.get('expected_state')
            predicted_state = pred.get('predicted_state')

            trans_type = case.get('transition_type', 'unknown')
            if trans_type not in by_type:
                by_type[trans_type] = {'total': 0, 'correct': 0}

            by_type[trans_type]['total'] += 1

            if self._match_state(expected_state, predicted_state):
                correct += 1
                by_type[trans_type]['correct'] += 1

        # Calculate per-type accuracy
        for ttype in by_type:
            if by_type[ttype]['total'] > 0:
                by_type[ttype]['accuracy'] = (
                    by_type[ttype]['correct'] / by_type[ttype]['total']
                )

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_transition_type': by_type
        }

    def _match_state(
        self,
        expected: Dict[str, Any],
        predicted: Dict[str, Any]
    ) -> bool:
        """Check if states match."""
        if not expected or not predicted:
            return expected == predicted

        for key in expected:
            if key not in predicted:
                return False
            if expected[key] != predicted[key]:
                return False
        return True

    def generate_transition_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for state transition testing.

        Returns:
            List of state transition test cases

        Example:
            >>> cases = service.generate_transition_test_cases()
        """
        return [
            {
                'utterance': 'I want to book a flight',
                'previous_state': {'intent': None, 'slots': {}},
                'expected_state': {
                    'intent': 'book_flight',
                    'slots': {}
                },
                'transition_type': 'intent_change'
            },
            {
                'utterance': 'to New York',
                'previous_state': {
                    'intent': 'book_flight',
                    'slots': {}
                },
                'expected_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'New York'}
                },
                'transition_type': 'slot_fill'
            },
            {
                'utterance': 'actually make that Boston',
                'previous_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'New York'}
                },
                'expected_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Boston'}
                },
                'transition_type': 'slot_update'
            },
            {
                'utterance': 'cancel that',
                'previous_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Boston'}
                },
                'expected_state': {
                    'intent': None,
                    'slots': {}
                },
                'transition_type': 'reset'
            }
        ]

    def test_context_carryover(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test context carryover between turns.

        Evaluates how well context is maintained across dialog turns.

        Args:
            test_cases: Test cases with expected context
            predictions: Predicted context values

        Returns:
            Dictionary with context carryover metrics

        Example:
            >>> result = service.test_context_carryover(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'partial_carryover': 0
            }

        total = len(test_cases)
        correct = 0
        partial = 0

        for case, pred in zip(test_cases, predictions):
            expected_context = case.get('expected_context', {})
            predicted_context = pred.get('predicted_context', {})

            # Count matching context items
            matches = sum(
                1 for k in expected_context
                if k in predicted_context and
                expected_context[k] == predicted_context[k]
            )

            if matches == len(expected_context) and len(expected_context) > 0:
                correct += 1
            elif matches > 0:
                partial += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'partial_carryover': partial,
            'carryover_rate': float(
                (correct + partial) / total
            ) if total > 0 else 0.0
        }

    def generate_context_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for context carryover testing.

        Returns:
            List of context carryover test cases

        Example:
            >>> cases = service.generate_context_test_cases()
        """
        return [
            {
                'dialog': [
                    'Book a flight to Paris',
                    'For next Monday'
                ],
                'expected_context': {
                    'destination': 'Paris',
                    'date': 'next Monday'
                }
            },
            {
                'dialog': [
                    'I need a hotel in London',
                    'for 3 nights',
                    'with breakfast included'
                ],
                'expected_context': {
                    'location': 'London',
                    'nights': 3,
                    'breakfast': True
                }
            },
            {
                'dialog': [
                    'Order a pizza',
                    'large size',
                    'with pepperoni',
                    'deliver to 123 Main St'
                ],
                'expected_context': {
                    'item': 'pizza',
                    'size': 'large',
                    'topping': 'pepperoni',
                    'address': '123 Main St'
                }
            }
        ]

    def test_state_recovery(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test state recovery after errors.

        Evaluates how well the system recovers dialog state after errors.

        Args:
            test_cases: Test cases with error scenarios
            predictions: Recovered state predictions

        Returns:
            Dictionary with state recovery metrics

        Example:
            >>> result = service.test_state_recovery(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'recovered': 0,
                'by_error_type': {}
            }

        total = len(test_cases)
        recovered = 0
        by_error = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_recovered_state')
            actual = pred.get('recovered_state')

            error_type = case.get('error_type', 'unknown')
            if error_type not in by_error:
                by_error[error_type] = {'total': 0, 'recovered': 0}

            by_error[error_type]['total'] += 1

            if self._match_state(expected, actual):
                recovered += 1
                by_error[error_type]['recovered'] += 1

        return {
            'accuracy': float(recovered / total) if total > 0 else 0.0,
            'total': total,
            'recovered': recovered,
            'by_error_type': by_error
        }

    def generate_recovery_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for state recovery testing.

        Returns:
            List of state recovery test cases

        Example:
            >>> cases = service.generate_recovery_test_cases()
        """
        return [
            {
                'dialog': ['Book flight to Paris', '???unclear???'],
                'error_type': 'asr_error',
                'pre_error_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                },
                'expected_recovered_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                }
            },
            {
                'dialog': ['Set timer', 'for... um... never mind'],
                'error_type': 'user_correction',
                'pre_error_state': {
                    'intent': 'set_timer',
                    'slots': {}
                },
                'expected_recovered_state': {
                    'intent': None,
                    'slots': {}
                }
            },
            {
                'dialog': ['Transfer $100', '[timeout]', 'hello?'],
                'error_type': 'timeout',
                'pre_error_state': {
                    'intent': 'transfer_money',
                    'slots': {'amount': 100}
                },
                'expected_recovered_state': {
                    'intent': 'transfer_money',
                    'slots': {'amount': 100}
                }
            }
        ]

    def test_session_timeout(
        self,
        test_cases: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Test session timeout handling.

        Evaluates how the system handles session timeouts.

        Args:
            test_cases: Test cases with timeout scenarios
            predictions: Post-timeout state predictions

        Returns:
            Dictionary with timeout handling metrics

        Example:
            >>> result = service.test_session_timeout(cases, preds)
        """
        if not test_cases:
            return {
                'accuracy': 0.0,
                'total': 0,
                'correct': 0,
                'by_timeout_duration': {}
            }

        total = len(test_cases)
        correct = 0
        by_duration = {}

        for case, pred in zip(test_cases, predictions):
            expected = case.get('expected_post_timeout_state')
            actual = pred.get('post_timeout_state')

            duration = case.get('timeout_duration', 'unknown')
            if duration not in by_duration:
                by_duration[duration] = {'total': 0, 'correct': 0}

            by_duration[duration]['total'] += 1

            if self._match_state(expected, actual):
                correct += 1
                by_duration[duration]['correct'] += 1

        return {
            'accuracy': float(correct / total) if total > 0 else 0.0,
            'total': total,
            'correct': correct,
            'by_timeout_duration': by_duration
        }

    def generate_timeout_test_cases(self) -> List[Dict[str, Any]]:
        """
        Generate test cases for session timeout testing.

        Returns:
            List of timeout test cases

        Example:
            >>> cases = service.generate_timeout_test_cases()
        """
        return [
            {
                'pre_timeout_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                },
                'timeout_duration': 'short',  # < 5 min
                'expected_post_timeout_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                }
            },
            {
                'pre_timeout_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                },
                'timeout_duration': 'medium',  # 5-30 min
                'expected_post_timeout_state': {
                    'intent': None,
                    'slots': {},
                    'context_preserved': True
                }
            },
            {
                'pre_timeout_state': {
                    'intent': 'book_flight',
                    'slots': {'destination': 'Paris'}
                },
                'timeout_duration': 'long',  # > 30 min
                'expected_post_timeout_state': {
                    'intent': None,
                    'slots': {}
                }
            }
        ]

    def get_state_tracking_metrics(
        self,
        transition_results: Dict[str, Any],
        carryover_results: Dict[str, Any],
        recovery_results: Dict[str, Any],
        timeout_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get comprehensive dialog state tracking metrics.

        Args:
            transition_results: Results from transition testing
            carryover_results: Results from carryover testing
            recovery_results: Results from recovery testing
            timeout_results: Results from timeout testing

        Returns:
            Dictionary with overall state tracking metrics

        Example:
            >>> metrics = service.get_state_tracking_metrics(
            ...     trans, carry, recov, timeout
            ... )
        """
        # Calculate totals
        total_tests = (
            transition_results.get('total', 0) +
            carryover_results.get('total', 0) +
            recovery_results.get('total', 0) +
            timeout_results.get('total', 0)
        )

        total_correct = (
            transition_results.get('correct', 0) +
            carryover_results.get('correct', 0) +
            recovery_results.get('recovered', 0) +
            timeout_results.get('correct', 0)
        )

        overall_accuracy = (
            total_correct / total_tests
        ) if total_tests > 0 else 0.0

        return {
            'overall_accuracy': float(overall_accuracy),
            'total_tests': total_tests,
            'total_correct': total_correct,
            'transition': {
                'accuracy': transition_results.get('accuracy', 0.0),
                'total': transition_results.get('total', 0)
            },
            'carryover': {
                'accuracy': carryover_results.get('accuracy', 0.0),
                'total': carryover_results.get('total', 0)
            },
            'recovery': {
                'accuracy': recovery_results.get('accuracy', 0.0),
                'total': recovery_results.get('total', 0)
            },
            'timeout': {
                'accuracy': timeout_results.get('accuracy', 0.0),
                'total': timeout_results.get('total', 0)
            },
            'quality_rating': (
                'excellent' if overall_accuracy > 0.9
                else 'good' if overall_accuracy > 0.8
                else 'fair' if overall_accuracy > 0.7
                else 'needs improvement'
            )
        }

