"""
Load Testing Service for performance and scalability testing.

This service provides load testing infrastructure for voice AI systems,
including concurrent user simulation, ramp patterns, and metrics collection.

Key features:
- Load generation configuration
- Concurrent user simulation
- Ramp-up and ramp-down patterns
- Real-time metrics collection

Example:
    >>> service = LoadTestingService()
    >>> config = service.create_load_config(users=100, duration=300)
    >>> test_id = service.start_load_test(config)
    >>> metrics = service.collect_metrics(test_id)
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

# Import metrics mixin
from services.load_testing_metrics import LoadTestingMetricsMixin


class LoadTestingService(LoadTestingMetricsMixin):
    """
    Service for load testing and performance benchmarking.

    Provides infrastructure for generating load, simulating concurrent
    users, and collecting performance metrics.

    This class inherits from:
    - LoadTestingMetricsMixin: Execution and metrics methods

    Example:
        >>> service = LoadTestingService()
        >>> config = service.create_load_config(users=50, duration=600)
        >>> print(f"Config created: {config['id']}")
    """

    def __init__(self):
        """Initialize the load testing service."""
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._tests: Dict[str, Dict[str, Any]] = {}
        self._scenarios: Dict[str, Dict[str, Any]] = {}
        self._ramp_patterns: Dict[str, str] = {
            'linear': 'Linear increase/decrease',
            'step': 'Step-wise increase/decrease',
            'exponential': 'Exponential curve'
        }

    def create_load_config(
        self,
        users: int,
        duration: int,
        spawn_rate: float = 1.0,
        host: str = "http://localhost:8000"
    ) -> Dict[str, Any]:
        """Create a load test configuration."""
        config_id = str(uuid.uuid4())
        config = {
            'id': config_id,
            'users': users,
            'duration': duration,
            'spawn_rate': spawn_rate,
            'host': host,
            'ramp_up': None,
            'ramp_down': None,
            'created_at': datetime.utcnow().isoformat()
        }
        self._configs[config_id] = config
        return config

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a load test configuration."""
        errors = []

        if config.get('users', 0) <= 0:
            errors.append("Users must be greater than 0")
        if config.get('duration', 0) <= 0:
            errors.append("Duration must be greater than 0")
        if config.get('spawn_rate', 0) <= 0:
            errors.append("Spawn rate must be greater than 0")
        if not config.get('host'):
            errors.append("Host URL is required")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'config_id': config.get('id')
        }

    def configure_users(
        self,
        config_id: str,
        user_distribution: Dict[str, float]
    ) -> Dict[str, Any]:
        """Configure user distribution for load test."""
        if config_id not in self._configs:
            return {'success': False, 'error': 'Config not found'}

        self._configs[config_id]['user_distribution'] = user_distribution
        return {
            'success': True,
            'config_id': config_id,
            'distribution': user_distribution
        }

    def spawn_users(
        self,
        test_id: str,
        count: int
    ) -> Dict[str, Any]:
        """Spawn additional users during test."""
        if test_id not in self._tests:
            return {'success': False, 'error': 'Test not found'}

        current = self._tests[test_id].get('active_users', 0)
        self._tests[test_id]['active_users'] = current + count

        return {
            'success': True,
            'spawned': count,
            'active_users': self._tests[test_id]['active_users']
        }

    def get_active_users(self, test_id: str) -> Dict[str, Any]:
        """Get number of active users."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        return {
            'test_id': test_id,
            'active_users': self._tests[test_id].get('active_users', 0)
        }

    def configure_ramp_up(
        self,
        config_id: str,
        duration: int,
        pattern: str = 'linear'
    ) -> Dict[str, Any]:
        """Configure ramp-up for load test."""
        if config_id not in self._configs:
            return {'success': False, 'error': 'Config not found'}

        if pattern not in self._ramp_patterns:
            return {'success': False, 'error': 'Invalid pattern'}

        self._configs[config_id]['ramp_up'] = {
            'duration': duration,
            'pattern': pattern
        }

        return {
            'success': True,
            'config_id': config_id,
            'ramp_up': self._configs[config_id]['ramp_up']
        }

    def configure_ramp_down(
        self,
        config_id: str,
        duration: int,
        pattern: str = 'linear'
    ) -> Dict[str, Any]:
        """Configure ramp-down for load test."""
        if config_id not in self._configs:
            return {'success': False, 'error': 'Config not found'}

        if pattern not in self._ramp_patterns:
            return {'success': False, 'error': 'Invalid pattern'}

        self._configs[config_id]['ramp_down'] = {
            'duration': duration,
            'pattern': pattern
        }

        return {
            'success': True,
            'config_id': config_id,
            'ramp_down': self._configs[config_id]['ramp_down']
        }

    def calculate_user_schedule(
        self,
        config_id: str,
        time_points: List[int]
    ) -> Dict[str, Any]:
        """Calculate user schedule at given time points."""
        if config_id not in self._configs:
            return {'error': 'Config not found'}

        config = self._configs[config_id]
        target_users = config.get('users', 0)
        schedule = []

        for time_point in time_points:
            users_at_point = min(time_point * config.get('spawn_rate', 1), target_users)
            schedule.append({
                'time': time_point,
                'users': int(users_at_point)
            })

        return {
            'config_id': config_id,
            'schedule': schedule
        }

    def get_ramp_patterns(self) -> Dict[str, str]:
        """Get available ramp patterns."""
        return self._ramp_patterns.copy()

    def define_scenario(
        self,
        name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Define a load test scenario."""
        scenario_id = str(uuid.uuid4())
        self._scenarios[scenario_id] = {
            'id': scenario_id,
            'name': name,
            'description': description,
            'tasks': [],
            'created_at': datetime.utcnow().isoformat()
        }
        return self._scenarios[scenario_id]

    def add_task_to_scenario(
        self,
        scenario_id: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add a task to a scenario."""
        if scenario_id not in self._scenarios:
            return {'success': False, 'error': 'Scenario not found'}

        self._scenarios[scenario_id]['tasks'].append(task)
        return {
            'success': True,
            'scenario_id': scenario_id,
            'task_count': len(self._scenarios[scenario_id]['tasks'])
        }

    def get_scenario(self, scenario_id: str) -> Dict[str, Any]:
        """Get a scenario by ID."""
        if scenario_id not in self._scenarios:
            return {'error': 'Scenario not found'}

        return self._scenarios[scenario_id]

    def create_test(
        self,
        name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a new load test."""
        test_id = str(uuid.uuid4())
        test = {
            'id': test_id,
            'name': name,
            'description': description,
            'status': 'created',
            'config': {
                'users': 1,
                'duration_seconds': 60
            },
            'created_at': datetime.utcnow().isoformat()
        }
        self._tests[test_id] = test
        return test

    def set_duration(
        self,
        test_id: str,
        duration_seconds: int
    ) -> Dict[str, Any]:
        """Set test duration."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        if 'config' not in self._tests[test_id]:
            self._tests[test_id]['config'] = {}
        self._tests[test_id]['config']['duration_seconds'] = duration_seconds

        return {
            'test_id': test_id,
            'duration_seconds': duration_seconds,
            'configured': True
        }

    def get_config(self, test_id: str) -> Dict[str, Any]:
        """Get test configuration."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        return {
            'test_id': test_id,
            'config': self._tests[test_id].get('config', {})
        }

    def start_sessions(
        self,
        test_id: str,
        count: int
    ) -> Dict[str, Any]:
        """Start concurrent sessions."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        current = self._tests[test_id].get('active_users', 0)
        self._tests[test_id]['active_users'] = current + count

        return {
            'test_id': test_id,
            'started': count,
            'active_users': self._tests[test_id]['active_users']
        }

    def get_active_sessions(self, test_id: str) -> Dict[str, Any]:
        """Get active session count."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        return {
            'test_id': test_id,
            'active_sessions': self._tests[test_id].get('active_users', 0)
        }

    def stop_sessions(
        self,
        test_id: str,
        count: Optional[int] = None
    ) -> Dict[str, Any]:
        """Stop concurrent sessions."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        current = self._tests[test_id].get('active_users', 0)
        if count is None:
            count = current

        stopped = min(count, current)
        self._tests[test_id]['active_users'] = current - stopped

        return {
            'test_id': test_id,
            'stopped': stopped,
            'active_users': self._tests[test_id]['active_users']
        }

    def set_ramp_up(
        self,
        test_id: str,
        users: int,
        duration_seconds: int
    ) -> Dict[str, Any]:
        """Set ramp-up configuration."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        if 'config' not in self._tests[test_id]:
            self._tests[test_id]['config'] = {}

        self._tests[test_id]['config']['ramp_up_users'] = users
        self._tests[test_id]['config']['ramp_up_seconds'] = duration_seconds

        return {
            'test_id': test_id,
            'ramp_up_users': users,
            'ramp_up_seconds': duration_seconds,
            'configured': True
        }

    def set_ramp_down(
        self,
        test_id: str,
        duration_seconds: int
    ) -> Dict[str, Any]:
        """Set ramp-down configuration."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        if 'config' not in self._tests[test_id]:
            self._tests[test_id]['config'] = {}

        self._tests[test_id]['config']['ramp_down_seconds'] = duration_seconds

        return {
            'test_id': test_id,
            'ramp_down_seconds': duration_seconds,
            'configured': True
        }

    def get_ramp_schedule(self, test_id: str) -> Dict[str, Any]:
        """Get ramp schedule for test."""
        if test_id not in self._tests:
            return {'error': 'Test not found'}

        config = self._tests[test_id].get('config', {})

        return {
            'test_id': test_id,
            'ramp_up_users': config.get('ramp_up_users', 1),
            'ramp_up_seconds': config.get('ramp_up_seconds', 10),
            'ramp_down_seconds': config.get('ramp_down_seconds', 10),
            'duration_seconds': config.get('duration_seconds', 60)
        }
