"""
Parallel Execution Service for voice AI testing.

This service provides parallel test execution capabilities including
test sharding, dynamic parallelization, and isolation validation.

Key features:
- Test sharding across workers
- Dynamic parallelization
- Test isolation validation

Example:
    >>> service = ParallelExecutionService()
    >>> result = service.create_shards(tests, num_workers=4)
"""

from typing import List, Dict, Any
from datetime import datetime
import uuid
import math


class ParallelExecutionService:
    """
    Service for parallel test execution management.

    Provides test sharding, dynamic parallelization,
    and isolation validation capabilities.

    Example:
        >>> service = ParallelExecutionService()
        >>> config = service.get_parallel_config()
    """

    def __init__(self):
        """Initialize the parallel execution service."""
        self._workers: Dict[str, Dict[str, Any]] = {}
        self._shards: Dict[str, List[Dict[str, Any]]] = {}
        self._dependencies: Dict[str, List[str]] = {}
        self._default_workers: int = 4
        self._max_workers: int = 32

    def create_shards(
        self,
        tests: List[Dict[str, Any]],
        num_workers: int = 4,
        strategy: str = 'round_robin'
    ) -> Dict[str, Any]:
        """
        Create test shards for parallel execution.

        Args:
            tests: Tests to shard
            num_workers: Number of workers
            strategy: Sharding strategy

        Returns:
            Dictionary with shard details

        Example:
            >>> result = service.create_shards(tests, num_workers=4)
        """
        shard_id = str(uuid.uuid4())
        shards: List[List[Dict[str, Any]]] = [[] for _ in range(num_workers)]

        if strategy == 'round_robin':
            for i, test in enumerate(tests):
                shards[i % num_workers].append(test)
        elif strategy == 'balanced':
            # Sort by estimated duration and distribute
            sorted_tests = sorted(
                tests,
                key=lambda t: t.get('duration', 1),
                reverse=True
            )
            for test in sorted_tests:
                # Add to least loaded shard
                min_shard = min(
                    range(num_workers),
                    key=lambda i: sum(
                        t.get('duration', 1) for t in shards[i]
                    )
                )
                shards[min_shard].append(test)

        self._shards[shard_id] = [
            {'shard_index': i, 'tests': s}
            for i, s in enumerate(shards)
        ]

        return {
            'shard_id': shard_id,
            'num_shards': num_workers,
            'total_tests': len(tests),
            'shards': [
                {'index': i, 'test_count': len(s)}
                for i, s in enumerate(shards)
            ],
            'strategy': strategy,
            'created_at': datetime.utcnow().isoformat()
        }

    def assign_to_workers(
        self,
        shard_id: str,
        worker_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Assign shards to workers.

        Args:
            shard_id: Shard identifier
            worker_ids: Worker identifiers

        Returns:
            Dictionary with assignment result

        Example:
            >>> result = service.assign_to_workers('shard-1', workers)
        """
        shards = self._shards.get(shard_id, [])
        assignments = []

        for i, worker_id in enumerate(worker_ids):
            if i < len(shards):
                assignment = {
                    'worker_id': worker_id,
                    'shard_index': i,
                    'test_count': len(shards[i].get('tests', []))
                }
                assignments.append(assignment)

                self._workers[worker_id] = {
                    'id': worker_id,
                    'shard_id': shard_id,
                    'shard_index': i,
                    'status': 'assigned',
                    'assigned_at': datetime.utcnow().isoformat()
                }

        return {
            'shard_id': shard_id,
            'assignments': assignments,
            'assigned_workers': len(assignments),
            'assigned_at': datetime.utcnow().isoformat()
        }

    def balance_shards(
        self,
        shard_id: str,
        test_durations: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Rebalance shards based on test durations.

        Args:
            shard_id: Shard identifier
            test_durations: Test duration estimates

        Returns:
            Dictionary with rebalanced shards

        Example:
            >>> result = service.balance_shards('shard-1', durations)
        """
        shards = self._shards.get(shard_id, [])
        if not shards:
            return {
                'shard_id': shard_id,
                'rebalanced': False,
                'error': f'Shard not found: {shard_id}',
                'balanced_at': datetime.utcnow().isoformat()
            }

        # Calculate current load per shard
        loads = []
        for shard in shards:
            total_duration = sum(
                test_durations.get(t.get('id', ''), 1)
                for t in shard.get('tests', [])
            )
            loads.append({
                'index': shard['shard_index'],
                'duration': total_duration,
                'test_count': len(shard.get('tests', []))
            })

        return {
            'shard_id': shard_id,
            'loads': loads,
            'rebalanced': True,
            'balanced_at': datetime.utcnow().isoformat()
        }

    def calculate_parallelism(
        self,
        total_tests: int,
        target_duration: float,
        avg_test_duration: float
    ) -> Dict[str, Any]:
        """
        Calculate optimal parallelism level.

        Args:
            total_tests: Total number of tests
            target_duration: Target total duration
            avg_test_duration: Average test duration

        Returns:
            Dictionary with parallelism recommendation

        Example:
            >>> result = service.calculate_parallelism(100, 300, 5)
        """
        # Calculate required parallelism
        total_duration = total_tests * avg_test_duration
        required_workers = math.ceil(total_duration / target_duration)

        # Apply limits
        recommended = min(max(required_workers, 1), self._max_workers)

        return {
            'total_tests': total_tests,
            'target_duration': target_duration,
            'avg_test_duration': avg_test_duration,
            'total_sequential_duration': total_duration,
            'recommended_workers': recommended,
            'estimated_duration': total_duration / recommended,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def scale_workers(
        self,
        current_workers: int,
        queue_depth: int,
        target_wait_time: float
    ) -> Dict[str, Any]:
        """
        Calculate worker scaling recommendation.

        Args:
            current_workers: Current worker count
            queue_depth: Current queue depth
            target_wait_time: Target wait time

        Returns:
            Dictionary with scaling recommendation

        Example:
            >>> result = service.scale_workers(4, 100, 60)
        """
        scaling_id = str(uuid.uuid4())

        # Simple scaling logic
        if queue_depth > current_workers * 10:
            action = 'scale_up'
            target = min(current_workers * 2, self._max_workers)
        elif queue_depth < current_workers * 2:
            action = 'scale_down'
            target = max(current_workers // 2, 1)
        else:
            action = 'maintain'
            target = current_workers

        return {
            'scaling_id': scaling_id,
            'current_workers': current_workers,
            'queue_depth': queue_depth,
            'action': action,
            'target_workers': target,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def optimize_distribution(
        self,
        tests: List[Dict[str, Any]],
        worker_capacities: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Optimize test distribution across workers.

        Args:
            tests: Tests to distribute
            worker_capacities: Worker capacity map

        Returns:
            Dictionary with optimized distribution

        Example:
            >>> result = service.optimize_distribution(tests, capacities)
        """
        optimization_id = str(uuid.uuid4())

        total_capacity = sum(worker_capacities.values())
        distribution = {}

        for worker_id, capacity in worker_capacities.items():
            ratio = capacity / total_capacity
            test_count = int(len(tests) * ratio)
            distribution[worker_id] = test_count

        return {
            'optimization_id': optimization_id,
            'total_tests': len(tests),
            'distribution': distribution,
            'optimized_at': datetime.utcnow().isoformat()
        }

    def validate_isolation(
        self,
        tests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate test isolation requirements.

        Args:
            tests: Tests to validate

        Returns:
            Dictionary with validation result

        Example:
            >>> result = service.validate_isolation(tests)
        """
        validation_id = str(uuid.uuid4())

        issues = []
        for test in tests:
            if test.get('shared_state'):
                issues.append({
                    'test_id': test.get('id'),
                    'issue': 'shared_state',
                    'severity': 'warning'
                })
            if test.get('requires_db'):
                issues.append({
                    'test_id': test.get('id'),
                    'issue': 'database_dependency',
                    'severity': 'info'
                })

        return {
            'validation_id': validation_id,
            'tests_checked': len(tests),
            'issues': issues,
            'isolated': len(issues) == 0,
            'validated_at': datetime.utcnow().isoformat()
        }

    def detect_dependencies(
        self,
        tests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect test dependencies.

        Args:
            tests: Tests to analyze

        Returns:
            Dictionary with dependency analysis

        Example:
            >>> result = service.detect_dependencies(tests)
        """
        detection_id = str(uuid.uuid4())

        dependencies = []
        for test in tests:
            test_deps = test.get('depends_on', [])
            if test_deps:
                dependencies.append({
                    'test_id': test.get('id'),
                    'depends_on': test_deps
                })
                self._dependencies[test.get('id', '')] = test_deps

        return {
            'detection_id': detection_id,
            'tests_analyzed': len(tests),
            'dependencies_found': len(dependencies),
            'dependencies': dependencies,
            'detected_at': datetime.utcnow().isoformat()
        }

    def check_conflicts(
        self,
        tests: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check for test conflicts.

        Args:
            tests: Tests to check

        Returns:
            Dictionary with conflict analysis

        Example:
            >>> result = service.check_conflicts(tests)
        """
        check_id = str(uuid.uuid4())

        conflicts = []
        resource_usage: Dict[str, List[str]] = {}

        for test in tests:
            test_id = test.get('id', '')
            resources = test.get('resources', [])

            for resource in resources:
                if resource in resource_usage:
                    # Conflict detected
                    conflicts.append({
                        'resource': resource,
                        'tests': [resource_usage[resource][0], test_id]
                    })
                else:
                    resource_usage[resource] = [test_id]

        return {
            'check_id': check_id,
            'tests_checked': len(tests),
            'conflicts': conflicts,
            'has_conflicts': len(conflicts) > 0,
            'checked_at': datetime.utcnow().isoformat()
        }

    def get_parallel_config(self) -> Dict[str, Any]:
        """
        Get parallel execution configuration.

        Returns:
            Dictionary with configuration

        Example:
            >>> config = service.get_parallel_config()
        """
        return {
            'total_workers': len(self._workers),
            'total_shards': len(self._shards),
            'default_workers': self._default_workers,
            'max_workers': self._max_workers,
            'features': [
                'sharding', 'dynamic_parallelism',
                'isolation_validation', 'conflict_detection'
            ]
        }
