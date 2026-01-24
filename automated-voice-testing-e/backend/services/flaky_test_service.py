"""
Flaky Test Detection Service for voice AI testing.

This service provides flaky test management capabilities including
automatic identification, quarantine management, and metrics tracking.

Key features:
- Automatic flaky test identification
- Quarantine flaky tests
- Flakiness metrics

Example:
    >>> service = FlakyTestService()
    >>> result = service.identify_flaky_tests(test_results)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


class FlakyTestService:
    """
    Service for flaky test detection and management.

    Provides automatic identification, quarantine management,
    and flakiness metrics capabilities.

    Example:
        >>> service = FlakyTestService()
        >>> config = service.get_flaky_config()
    """

    def __init__(self):
        """Initialize the flaky test service."""
        self._quarantined: Dict[str, Dict[str, Any]] = {}
        self._test_history: Dict[str, List[Dict[str, Any]]] = {}
        self._flakiness_scores: Dict[str, float] = {}
        self._flakiness_threshold: float = 0.1

    def identify_flaky_tests(
        self,
        test_results: List[Dict[str, Any]],
        lookback_runs: int = 10
    ) -> Dict[str, Any]:
        """
        Identify flaky tests from results.

        Args:
            test_results: Recent test results
            lookback_runs: Number of runs to analyze

        Returns:
            Dictionary with flaky test identification

        Example:
            >>> result = service.identify_flaky_tests(results)
        """
        identification_id = str(uuid.uuid4())

        flaky_tests = []
        for test in test_results:
            test_id = test.get('id', '')
            history = self._test_history.get(test_id, [])

            if len(history) >= 2:
                # Check for inconsistent results
                results = [h.get('passed') for h in history[-lookback_runs:]]
                if True in results and False in results:
                    pass_rate = results.count(True) / len(results)
                    if 0.1 < pass_rate < 0.9:
                        flaky_tests.append({
                            'test_id': test_id,
                            'pass_rate': pass_rate,
                            'flakiness': 1 - abs(pass_rate - 0.5) * 2
                        })

        return {
            'identification_id': identification_id,
            'flaky_tests': flaky_tests,
            'total_identified': len(flaky_tests),
            'tests_analyzed': len(test_results),
            'identified_at': datetime.utcnow().isoformat()
        }

    def analyze_test_history(
        self,
        test_id: str,
        num_runs: int = 20
    ) -> Dict[str, Any]:
        """
        Analyze test execution history.

        Args:
            test_id: Test identifier
            num_runs: Number of runs to analyze

        Returns:
            Dictionary with history analysis

        Example:
            >>> result = service.analyze_test_history('test-1')
        """
        analysis_id = str(uuid.uuid4())

        history = self._test_history.get(test_id, [])[-num_runs:]

        if not history:
            return {
                'analysis_id': analysis_id,
                'test_id': test_id,
                'has_history': False,
                'analyzed_at': datetime.utcnow().isoformat()
            }

        passes = sum(1 for h in history if h.get('passed'))
        failures = len(history) - passes

        return {
            'analysis_id': analysis_id,
            'test_id': test_id,
            'total_runs': len(history),
            'passes': passes,
            'failures': failures,
            'pass_rate': passes / len(history) if history else 0,
            'has_history': True,
            'analyzed_at': datetime.utcnow().isoformat()
        }

    def calculate_flakiness_score(
        self,
        test_id: str,
        results: List[bool]
    ) -> Dict[str, Any]:
        """
        Calculate flakiness score for a test.

        Args:
            test_id: Test identifier
            results: List of pass/fail results

        Returns:
            Dictionary with flakiness score

        Example:
            >>> result = service.calculate_flakiness_score('test-1', results)
        """
        if not results:
            return {
                'test_id': test_id,
                'score': 0.0,
                'is_flaky': False,
                'calculated_at': datetime.utcnow().isoformat()
            }

        pass_rate = sum(results) / len(results)
        # Flakiness is highest when pass rate is around 50%
        score = 1 - abs(pass_rate - 0.5) * 2

        self._flakiness_scores[test_id] = score

        return {
            'test_id': test_id,
            'score': score,
            'pass_rate': pass_rate,
            'is_flaky': score > self._flakiness_threshold,
            'threshold': self._flakiness_threshold,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def quarantine_test(
        self,
        test_id: str,
        reason: str,
        auto_release_after: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Quarantine a flaky test.

        Args:
            test_id: Test identifier
            reason: Quarantine reason
            auto_release_after: Days until auto-release

        Returns:
            Dictionary with quarantine result

        Example:
            >>> result = service.quarantine_test('test-1', 'Too flaky')
        """
        quarantine_id = str(uuid.uuid4())

        self._quarantined[test_id] = {
            'quarantine_id': quarantine_id,
            'test_id': test_id,
            'reason': reason,
            'auto_release_after': auto_release_after,
            'quarantined_at': datetime.utcnow().isoformat()
        }

        return {
            'quarantine_id': quarantine_id,
            'test_id': test_id,
            'reason': reason,
            'status': 'quarantined',
            'quarantined_at': datetime.utcnow().isoformat()
        }

    def release_from_quarantine(
        self,
        test_id: str,
        reason: str = 'Manual release'
    ) -> Dict[str, Any]:
        """
        Release a test from quarantine.

        Args:
            test_id: Test identifier
            reason: Release reason

        Returns:
            Dictionary with release result

        Example:
            >>> result = service.release_from_quarantine('test-1')
        """
        if test_id in self._quarantined:
            del self._quarantined[test_id]
            return {
                'test_id': test_id,
                'reason': reason,
                'status': 'released',
                'released_at': datetime.utcnow().isoformat()
            }

        return {
            'test_id': test_id,
            'status': 'not_quarantined',
            'error': f'Test not in quarantine: {test_id}',
            'released_at': datetime.utcnow().isoformat()
        }

    def list_quarantined_tests(
        self,
        include_scores: bool = False
    ) -> Dict[str, Any]:
        """
        List all quarantined tests.

        Args:
            include_scores: Include flakiness scores

        Returns:
            Dictionary with quarantined tests list

        Example:
            >>> result = service.list_quarantined_tests()
        """
        tests = []
        for test_id, data in self._quarantined.items():
            test_info = {
                'test_id': test_id,
                'reason': data['reason'],
                'quarantined_at': data['quarantined_at']
            }
            if include_scores:
                test_info['flakiness_score'] = self._flakiness_scores.get(
                    test_id, 0.0
                )
            tests.append(test_info)

        return {
            'quarantined_tests': tests,
            'total_quarantined': len(tests),
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_flakiness_metrics(
        self,
        test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get flakiness metrics for tests.

        Args:
            test_ids: Specific test IDs

        Returns:
            Dictionary with flakiness metrics

        Example:
            >>> result = service.get_flakiness_metrics()
        """
        if test_ids:
            scores = {
                tid: self._flakiness_scores.get(tid, 0.0)
                for tid in test_ids
            }
        else:
            scores = dict(self._flakiness_scores)

        flaky_count = sum(
            1 for s in scores.values()
            if s > self._flakiness_threshold
        )

        return {
            'scores': scores,
            'total_tests': len(scores),
            'flaky_count': flaky_count,
            'flaky_percentage': (
                flaky_count / len(scores) * 100 if scores else 0
            ),
            'threshold': self._flakiness_threshold,
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def get_flakiness_trends(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get flakiness trends over time.

        Args:
            period_days: Period in days

        Returns:
            Dictionary with trend data

        Example:
            >>> result = service.get_flakiness_trends()
        """
        trend_id = str(uuid.uuid4())

        # Simulated trend data
        return {
            'trend_id': trend_id,
            'period_days': period_days,
            'current_flaky_count': len([
                s for s in self._flakiness_scores.values()
                if s > self._flakiness_threshold
            ]),
            'total_quarantined': len(self._quarantined),
            'trend': 'stable',
            'retrieved_at': datetime.utcnow().isoformat()
        }

    def generate_flakiness_report(
        self,
        include_details: bool = True
    ) -> Dict[str, Any]:
        """
        Generate flakiness report.

        Args:
            include_details: Include test details

        Returns:
            Dictionary with report data

        Example:
            >>> result = service.generate_flakiness_report()
        """
        report_id = str(uuid.uuid4())

        flaky_tests = [
            {'test_id': tid, 'score': score}
            for tid, score in self._flakiness_scores.items()
            if score > self._flakiness_threshold
        ]

        report = {
            'report_id': report_id,
            'total_tests_tracked': len(self._flakiness_scores),
            'flaky_tests_count': len(flaky_tests),
            'quarantined_count': len(self._quarantined),
            'generated_at': datetime.utcnow().isoformat()
        }

        if include_details:
            report['flaky_tests'] = flaky_tests
            report['quarantined_tests'] = list(self._quarantined.keys())

        return report

    def get_flaky_config(self) -> Dict[str, Any]:
        """
        Get flaky test configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_flaky_config()
        """
        return {
            'total_tracked': len(self._flakiness_scores),
            'total_quarantined': len(self._quarantined),
            'flakiness_threshold': self._flakiness_threshold,
            'features': [
                'auto_identification', 'quarantine',
                'metrics', 'trend_analysis'
            ]
        }
