"""
LoadTestingMetricsMixin - Execution and metrics methods for load testing service.

This mixin provides test execution and metrics collection methods:
- Load test lifecycle (start, stop, pause)
- Metrics collection and reporting
- Real-time statistics

Extracted from load_testing_service.py to reduce file size per coding conventions.
"""

from typing import Dict, Any
from datetime import datetime


class LoadTestingMetricsMixin:
    """
    Mixin providing execution and metrics methods for LoadTestingService.

    This mixin contains:
    - Load test execution methods (start, stop, pause)
    - Metrics collection methods
    - Real-time statistics and reporting
    """

    def start_load_test(self, config: Dict[str, Any]) -> str:
        """Start a load test with given configuration."""
        import uuid
        test_id = str(uuid.uuid4())
        self._tests[test_id] = {
            'id': test_id,
            'config': config,
            'status': 'running',
            'active_users': 0,
            'started_at': datetime.utcnow().isoformat(),
            'metrics': {
                'requests': 0,
                'failures': 0,
                'response_times': []
            }
        }
        return test_id

    def stop_load_test(self, test_id: str) -> Dict[str, Any]:
        """Stop a running load test."""
        if test_id not in self._tests:
            return {'success': False, 'error': 'Test not found'}

        self._tests[test_id]['status'] = 'stopped'
        self._tests[test_id]['stopped_at'] = datetime.utcnow().isoformat()

        return {
            'success': True,
            'test_id': test_id,
            'status': 'stopped'
        }

    def get_test_status(self, test_id: str) -> Dict[str, Any]:
        """Get current status of a load test."""
        if test_id not in self._tests:
            return {'status': 'not_found', 'error': 'Test not found'}

        test = self._tests[test_id]
        return {
            'test_id': test_id,
            'status': test.get('status', 'unknown'),
            'active_users': test.get('active_users', 0),
            'started_at': test.get('started_at'),
            'stopped_at': test.get('stopped_at')
        }

    def pause_load_test(self, test_id: str) -> Dict[str, Any]:
        """Pause a running load test."""
        if test_id not in self._tests:
            return {'success': False, 'error': 'Test not found'}

        self._tests[test_id]['status'] = 'paused'
        return {
            'success': True,
            'test_id': test_id,
            'status': 'paused'
        }

    def collect_metrics(self, test_id: str) -> Dict[str, Any]:
        """Collect metrics from a load test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        test = self._tests[test_id]
        metrics = test.get('metrics', {})
        response_times = metrics.get('response_times', [])

        avg_response = (
            sum(response_times) / len(response_times)
        ) if response_times else 0.0

        return {
            'test_id': test_id,
            'total_requests': metrics.get('requests', 0),
            'total_failures': metrics.get('failures', 0),
            'avg_response_time': avg_response,
            'min_response_time': min(response_times) if response_times else 0,
            'max_response_time': max(response_times) if response_times else 0,
            'active_users': test.get('active_users', 0)
        }

    def get_real_time_stats(self, test_id: str) -> Dict[str, Any]:
        """Get real-time statistics from a running test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        test = self._tests[test_id]
        metrics = test.get('metrics', {})

        return {
            'test_id': test_id,
            'current_users': test.get('active_users', 0),
            'requests_per_second': metrics.get('rps', 0.0),
            'failures_per_second': metrics.get('fps', 0.0),
            'avg_response_time': metrics.get('avg_rt', 0.0),
            'p50_response_time': metrics.get('p50', 0.0),
            'p95_response_time': metrics.get('p95', 0.0),
            'p99_response_time': metrics.get('p99', 0.0)
        }

    def generate_load_report(self, test_id: str) -> Dict[str, Any]:
        """Generate comprehensive report for a load test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        test = self._tests[test_id]
        metrics = self.collect_metrics(test_id)

        return {
            'test_id': test_id,
            'config': test.get('config', {}),
            'summary': {
                'total_requests': metrics.get('total_requests', 0),
                'total_failures': metrics.get('total_failures', 0),
                'avg_response_time': metrics.get('avg_response_time', 0),
                'peak_users': test.get('active_users', 0)
            },
            'started_at': test.get('started_at'),
            'stopped_at': test.get('stopped_at'),
            'status': test.get('status')
        }

    def start_test(self, test_id: str) -> Dict[str, Any]:
        """Start the load test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        self._tests[test_id]['status'] = 'running'
        self._tests[test_id]['started_at'] = datetime.utcnow().isoformat()

        return {
            'test_id': test_id,
            'status': 'running',
            'started_at': self._tests[test_id]['started_at']
        }

    def stop_test(self, test_id: str) -> Dict[str, Any]:
        """Stop the load test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        self._tests[test_id]['status'] = 'stopped'
        self._tests[test_id]['stopped_at'] = datetime.utcnow().isoformat()

        return {
            'test_id': test_id,
            'status': 'stopped',
            'stopped_at': self._tests[test_id]['stopped_at']
        }

    def get_status(self, test_id: str) -> Dict[str, Any]:
        """Get test status."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        test = self._tests[test_id]
        return {
            'test_id': test_id,
            'name': test.get('name'),
            'status': test.get('status'),
            'active_users': test.get('active_users', 0)
        }

    def get_metrics(self, test_id: str) -> Dict[str, Any]:
        """Get test metrics."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        metrics = self._tests[test_id].get('metrics', {})

        return {
            'test_id': test_id,
            'requests': metrics.get('requests', 0),
            'failures': metrics.get('failures', 0),
            'collected_at': datetime.utcnow().isoformat()
        }

    def get_throughput(self, test_id: str) -> Dict[str, Any]:
        """Get throughput metrics."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        test = self._tests[test_id]
        metrics = test.get('metrics', {})
        requests = metrics.get('requests', 0)

        elapsed = 0
        if test.get('started_at'):
            start = datetime.fromisoformat(test['started_at'])
            end = datetime.utcnow()
            elapsed = (end - start).total_seconds()

        rps = requests / elapsed if elapsed > 0 else 0

        return {
            'test_id': test_id,
            'requests': requests,
            'elapsed_seconds': elapsed,
            'requests_per_second': rps
        }

    def get_error_rate(self, test_id: str) -> Dict[str, Any]:
        """Get error rate metrics."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        metrics = self._tests[test_id].get('metrics', {})
        requests = metrics.get('requests', 0)
        failures = metrics.get('failures', 0)

        rate = failures / requests if requests > 0 else 0

        return {
            'test_id': test_id,
            'total_requests': requests,
            'total_failures': failures,
            'error_rate': rate
        }

    def get_resource_usage(self, test_id: str) -> Dict[str, Any]:
        """Get resource usage metrics."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        return {
            'test_id': test_id,
            'cpu_percent': 0.0,
            'memory_mb': 0.0,
            'active_connections': self._tests[test_id].get('active_users', 0),
            'measured_at': datetime.utcnow().isoformat()
        }
