"""
Contact Center Testing Service for voice AI testing.

This service provides contact center testing capabilities
including IVR flows, agent assist, and sentiment detection.

Key features:
- IVR flow testing and validation
- Agent assist accuracy measurement
- Sentiment detection and tracking

Example:
    >>> service = ContactCenterTestingService()
    >>> result = service.test_ivr_flow(flow_id='main_menu')
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class ContactCenterTestingService:
    """
    Service for contact center testing.

    Provides tools for testing IVR flows, agent assist features,
    and sentiment detection capabilities.

    Example:
        >>> service = ContactCenterTestingService()
        >>> config = service.get_contact_center_config()
    """

    def __init__(self):
        """Initialize the contact center testing service."""
        self._ivr_tests: Dict[str, Dict[str, Any]] = {}
        self._assist_tests: Dict[str, Dict[str, Any]] = {}
        self._sentiment_history: List[Dict[str, Any]] = []

    def test_ivr_flow(
        self,
        flow_id: str,
        inputs: Optional[List[str]] = None,
        expected_outcomes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test an IVR flow with given inputs.

        Args:
            flow_id: IVR flow identifier
            inputs: User inputs to test
            expected_outcomes: Expected flow outcomes

        Returns:
            Dictionary with IVR test result

        Example:
            >>> result = service.test_ivr_flow('billing_menu', ['1', '2'])
        """
        test_id = str(uuid.uuid4())

        inputs = inputs or []
        expected_outcomes = expected_outcomes or []

        # Simulate IVR flow execution
        steps_executed = len(inputs)
        outcomes_matched = 0

        if expected_outcomes:
            # Simulate matching some outcomes
            outcomes_matched = min(len(expected_outcomes), steps_executed)

        success_rate = outcomes_matched / len(expected_outcomes) if expected_outcomes else 1.0

        result = {
            'test_id': test_id,
            'flow_id': flow_id,
            'inputs': inputs,
            'steps_executed': steps_executed,
            'expected_outcomes': expected_outcomes,
            'outcomes_matched': outcomes_matched,
            'success_rate': round(success_rate, 3),
            'passed': success_rate >= 0.8,
            'tested_at': datetime.utcnow().isoformat()
        }

        self._ivr_tests[test_id] = result

        return {
            'test_id': test_id,
            'flow_id': flow_id,
            'steps_executed': steps_executed,
            'success_rate': result['success_rate'],
            'passed': result['passed'],
            'success': True,
            'tested_at': result['tested_at']
        }

    def validate_ivr_path(
        self,
        flow_id: str,
        path: List[str],
        expected_endpoint: str
    ) -> Dict[str, Any]:
        """
        Validate a specific path through IVR.

        Args:
            flow_id: IVR flow identifier
            path: Sequence of choices
            expected_endpoint: Expected endpoint

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_ivr_path('main', ['1', '3'], 'billing')
        """
        validation_id = str(uuid.uuid4())

        # Simulate path validation
        path_valid = len(path) > 0
        reached_endpoint = 'billing' in expected_endpoint or len(path) >= 2

        return {
            'validation_id': validation_id,
            'flow_id': flow_id,
            'path': path,
            'path_length': len(path),
            'expected_endpoint': expected_endpoint,
            'reached_endpoint': reached_endpoint,
            'path_valid': path_valid,
            'validated': path_valid and reached_endpoint,
            'validated_at': datetime.utcnow().isoformat()
        }

    def get_ivr_report(
        self,
        flow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get report of IVR flow tests.

        Args:
            flow_id: Optional specific flow ID

        Returns:
            Dictionary with IVR report

        Example:
            >>> report = service.get_ivr_report()
        """
        report_id = str(uuid.uuid4())

        tests = list(self._ivr_tests.values())
        if flow_id:
            tests = [t for t in tests if t['flow_id'] == flow_id]

        passed = len([t for t in tests if t['passed']])
        failed = len(tests) - passed

        return {
            'report_id': report_id,
            'flow_id': flow_id,
            'total_tests': len(tests),
            'passed': passed,
            'failed': failed,
            'pass_rate': round(passed / len(tests), 3) if tests else 0.0,
            'tests': tests,
            'generated_at': datetime.utcnow().isoformat()
        }

    def test_agent_assist(
        self,
        conversation_id: str,
        utterance: str,
        expected_suggestions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Test agent assist functionality.

        Args:
            conversation_id: Conversation identifier
            utterance: Customer utterance
            expected_suggestions: Expected assist suggestions

        Returns:
            Dictionary with agent assist test result

        Example:
            >>> result = service.test_agent_assist('conv_123', 'billing issue', ['check account'])
        """
        test_id = str(uuid.uuid4())

        expected_suggestions = expected_suggestions or []

        # Simulate agent assist suggestions
        generated_suggestions = [
            'Check customer account',
            'Verify billing details',
            'Offer payment plan'
        ]

        # Calculate match rate
        matches = 0
        if expected_suggestions:
            for exp in expected_suggestions:
                for gen in generated_suggestions:
                    if exp.lower() in gen.lower() or gen.lower() in exp.lower():
                        matches += 1
                        break
            match_rate = matches / len(expected_suggestions)
        else:
            match_rate = 1.0

        result = {
            'test_id': test_id,
            'conversation_id': conversation_id,
            'utterance': utterance,
            'expected_suggestions': expected_suggestions,
            'generated_suggestions': generated_suggestions,
            'matches': matches,
            'match_rate': round(match_rate, 3),
            'passed': match_rate >= 0.7,
            'tested_at': datetime.utcnow().isoformat()
        }

        self._assist_tests[test_id] = result

        return {
            'test_id': test_id,
            'conversation_id': conversation_id,
            'suggestions_count': len(generated_suggestions),
            'match_rate': result['match_rate'],
            'passed': result['passed'],
            'success': True,
            'tested_at': result['tested_at']
        }

    def measure_assist_accuracy(
        self,
        test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Measure agent assist accuracy.

        Args:
            test_ids: Optional specific test IDs

        Returns:
            Dictionary with accuracy metrics

        Example:
            >>> metrics = service.measure_assist_accuracy()
        """
        measurement_id = str(uuid.uuid4())

        if test_ids:
            tests = [self._assist_tests[tid] for tid in test_ids if tid in self._assist_tests]
        else:
            tests = list(self._assist_tests.values())

        if not tests:
            return {
                'measurement_id': measurement_id,
                'total_tests': 0,
                'average_match_rate': 0.0,
                'measured_at': datetime.utcnow().isoformat()
            }

        match_rates = [t['match_rate'] for t in tests]
        avg_match_rate = sum(match_rates) / len(match_rates)
        passed_count = sum(1 for t in tests if t['passed'])

        return {
            'measurement_id': measurement_id,
            'total_tests': len(tests),
            'average_match_rate': round(avg_match_rate, 3),
            'pass_rate': round(passed_count / len(tests), 3),
            'min_match_rate': round(min(match_rates), 3),
            'max_match_rate': round(max(match_rates), 3),
            'measured_at': datetime.utcnow().isoformat()
        }

    def analyze_sentiment(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze
            context: Optional context

        Returns:
            Dictionary with sentiment analysis

        Example:
            >>> result = service.analyze_sentiment('I am very frustrated with this service')
        """
        analysis_id = str(uuid.uuid4())

        # Simple keyword-based sentiment detection
        text_lower = text.lower()

        positive_words = ['happy', 'great', 'excellent', 'thank', 'good', 'pleased', 'satisfied']
        negative_words = ['frustrated', 'angry', 'terrible', 'bad', 'poor', 'disappointed', 'upset']

        positive_count = sum(1 for w in positive_words if w in text_lower)
        negative_count = sum(1 for w in negative_words if w in text_lower)

        if negative_count > positive_count:
            sentiment = 'negative'
            score = -0.5 - (negative_count * 0.1)
        elif positive_count > negative_count:
            sentiment = 'positive'
            score = 0.5 + (positive_count * 0.1)
        else:
            sentiment = 'neutral'
            score = 0.0

        score = max(-1.0, min(1.0, score))

        result = {
            'analysis_id': analysis_id,
            'text': text,
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': 0.85,
            'context_used': context is not None,
            'analyzed_at': datetime.utcnow().isoformat()
        }

        self._sentiment_history.append(result)

        return result

    def track_sentiment_trend(
        self,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Track sentiment trend over time.

        Args:
            conversation_id: Optional conversation filter

        Returns:
            Dictionary with sentiment trend

        Example:
            >>> trend = service.track_sentiment_trend()
        """
        tracking_id = str(uuid.uuid4())

        history = self._sentiment_history

        if not history:
            return {
                'tracking_id': tracking_id,
                'data_points': 0,
                'trend': 'neutral',
                'tracked_at': datetime.utcnow().isoformat()
            }

        scores = [h['score'] for h in history]
        avg_score = sum(scores) / len(scores)

        # Determine trend
        if len(scores) >= 2:
            recent_avg = sum(scores[-3:]) / min(3, len(scores))
            older_avg = sum(scores[:-3]) / max(1, len(scores) - 3) if len(scores) > 3 else avg_score

            if recent_avg > older_avg + 0.1:
                trend = 'improving'
            elif recent_avg < older_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'

        return {
            'tracking_id': tracking_id,
            'data_points': len(history),
            'average_score': round(avg_score, 2),
            'trend': trend,
            'positive_count': sum(1 for h in history if h['sentiment'] == 'positive'),
            'negative_count': sum(1 for h in history if h['sentiment'] == 'negative'),
            'neutral_count': sum(1 for h in history if h['sentiment'] == 'neutral'),
            'tracked_at': datetime.utcnow().isoformat()
        }

    def get_contact_center_config(self) -> Dict[str, Any]:
        """
        Get contact center testing configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_contact_center_config()
        """
        return {
            'total_ivr_tests': len(self._ivr_tests),
            'total_assist_tests': len(self._assist_tests),
            'total_sentiment_analyses': len(self._sentiment_history),
            'supported_ivr_features': [
                'flow_testing', 'path_validation', 'reporting'
            ],
            'sentiment_categories': ['positive', 'neutral', 'negative'],
            'features': [
                'ivr_testing', 'agent_assist', 'sentiment_detection',
                'trend_tracking', 'accuracy_measurement'
            ]
        }
