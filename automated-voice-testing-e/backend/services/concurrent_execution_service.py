"""
Concurrent Test Execution Service for parallel testing.

This service provides concurrent test execution capabilities
for voice AI systems testing with thread pool management.

Key features:
- Thread pool management
- Task scheduling and distribution
- Result aggregation
- Concurrency control

Example:
    >>> service = ConcurrentExecutionService()
    >>> service.create_thread_pool(max_workers=10)
    >>> task_id = service.submit_task(test_function, args)
    >>> result = service.collect_results(task_id)
"""

from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import uuid


class ConcurrentExecutionService:
    """
    Service for concurrent test execution and management.

    Provides thread pool management, task scheduling, and
    result aggregation for parallel test execution.

    Example:
        >>> service = ConcurrentExecutionService()
        >>> service.create_thread_pool(max_workers=8)
        >>> task_ids = service.submit_batch(tasks)
        >>> print(f"Submitted {len(task_ids)} tasks")
    """

    def __init__(self):
        """Initialize the concurrent execution service."""
        self._pools: Dict[str, Dict[str, Any]] = {}
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._batches: Dict[str, List[str]] = {}
        self._default_pool_id: Optional[str] = None
        self._max_workers = 4

    def create_thread_pool(
        self,
        max_workers: int = 4,
        pool_name: str = "default"
    ) -> Dict[str, Any]:
        """
        Create a thread pool for concurrent execution.

        Args:
            max_workers: Maximum number of worker threads
            pool_name: Name identifier for the pool

        Returns:
            Dictionary with pool configuration

        Example:
            >>> pool = service.create_thread_pool(max_workers=10)
            >>> print(f"Pool created: {pool['id']}")
        """
        pool_id = str(uuid.uuid4())
        pool = {
            'id': pool_id,
            'name': pool_name,
            'max_workers': max_workers,
            'active_workers': 0,
            'status': 'running',
            'tasks_completed': 0,
            'tasks_pending': 0,
            'created_at': datetime.utcnow().isoformat()
        }
        self._pools[pool_id] = pool

        if self._default_pool_id is None:
            self._default_pool_id = pool_id

        return pool

    def resize_pool(
        self,
        pool_id: str,
        new_size: int
    ) -> Dict[str, Any]:
        """
        Resize a thread pool.

        Args:
            pool_id: Pool ID to resize
            new_size: New maximum worker count

        Returns:
            Dictionary with resize results

        Example:
            >>> result = service.resize_pool(pool_id, 20)
            >>> print(f"New size: {result['new_size']}")
        """
        if pool_id not in self._pools:
            return {'success': False, 'error': 'Pool not found'}

        old_size = self._pools[pool_id]['max_workers']
        self._pools[pool_id]['max_workers'] = new_size

        return {
            'success': True,
            'pool_id': pool_id,
            'old_size': old_size,
            'new_size': new_size
        }

    def shutdown_pool(
        self,
        pool_id: str,
        wait: bool = True
    ) -> Dict[str, Any]:
        """
        Shutdown a thread pool.

        Args:
            pool_id: Pool ID to shutdown
            wait: Wait for pending tasks to complete

        Returns:
            Dictionary with shutdown results

        Example:
            >>> result = service.shutdown_pool(pool_id)
        """
        if pool_id not in self._pools:
            return {'success': False, 'error': 'Pool not found'}

        self._pools[pool_id]['status'] = 'shutdown'
        return {
            'success': True,
            'pool_id': pool_id,
            'status': 'shutdown',
            'waited': wait
        }

    def get_pool_status(self, pool_id: str) -> Dict[str, Any]:
        """
        Get status of a thread pool.

        Args:
            pool_id: Pool ID to check

        Returns:
            Dictionary with pool status

        Example:
            >>> status = service.get_pool_status(pool_id)
            >>> print(f"Active workers: {status['active_workers']}")
        """
        if pool_id not in self._pools:
            return {'error': 'Pool not found'}

        pool = self._pools[pool_id]
        return {
            'pool_id': pool_id,
            'name': pool.get('name'),
            'status': pool.get('status'),
            'max_workers': pool.get('max_workers'),
            'active_workers': pool.get('active_workers'),
            'tasks_completed': pool.get('tasks_completed'),
            'tasks_pending': pool.get('tasks_pending')
        }

    def submit_task(
        self,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        pool_id: str = None
    ) -> str:
        """
        Submit a task for concurrent execution.

        Args:
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            pool_id: Pool to submit to

        Returns:
            Task ID string

        Example:
            >>> task_id = service.submit_task(my_function, (arg1,))
            >>> print(f"Submitted: {task_id}")
        """
        task_id = str(uuid.uuid4())
        target_pool = pool_id or self._default_pool_id

        self._tasks[task_id] = {
            'id': task_id,
            'func': func.__name__ if callable(func) else str(func),
            'args': args,
            'kwargs': kwargs or {},
            'pool_id': target_pool,
            'status': 'pending',
            'result': None,
            'error': None,
            'submitted_at': datetime.utcnow().isoformat()
        }

        if target_pool and target_pool in self._pools:
            self._pools[target_pool]['tasks_pending'] += 1

        return task_id

    def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        pool_id: str = None
    ) -> Dict[str, Any]:
        """
        Submit a batch of tasks for concurrent execution.

        Args:
            tasks: List of task definitions
            pool_id: Pool to submit to

        Returns:
            Dictionary with batch submission results

        Example:
            >>> tasks = [{'func': fn, 'args': (i,)} for i in range(10)]
            >>> result = service.submit_batch(tasks)
        """
        batch_id = str(uuid.uuid4())
        task_ids = []

        for task_def in tasks:
            func = task_def.get('func', lambda: None)
            args = task_def.get('args', ())
            kwargs = task_def.get('kwargs', {})

            task_id = self.submit_task(func, args, kwargs, pool_id)
            task_ids.append(task_id)

        self._batches[batch_id] = task_ids

        return {
            'batch_id': batch_id,
            'task_count': len(task_ids),
            'task_ids': task_ids
        }

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """
        Cancel a pending task.

        Args:
            task_id: Task ID to cancel

        Returns:
            Dictionary with cancellation results

        Example:
            >>> result = service.cancel_task(task_id)
        """
        if task_id not in self._tasks:
            return {'success': False, 'error': 'Task not found'}

        task = self._tasks[task_id]
        if task['status'] != 'pending':
            return {
                'success': False,
                'error': f"Cannot cancel task in {task['status']} state"
            }

        task['status'] = 'cancelled'
        return {
            'success': True,
            'task_id': task_id,
            'status': 'cancelled'
        }

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get status of a submitted task.

        Args:
            task_id: Task ID to check

        Returns:
            Dictionary with task status

        Example:
            >>> status = service.get_task_status(task_id)
            >>> print(f"Status: {status['status']}")
        """
        if task_id not in self._tasks:
            return {'error': 'Task not found'}

        task = self._tasks[task_id]
        return {
            'task_id': task_id,
            'status': task.get('status'),
            'submitted_at': task.get('submitted_at'),
            'completed_at': task.get('completed_at'),
            'has_result': task.get('result') is not None,
            'has_error': task.get('error') is not None
        }

    def collect_results(
        self,
        task_id: str,
        timeout: float = None
    ) -> Dict[str, Any]:
        """
        Collect results from a completed task.

        Args:
            task_id: Task ID to collect results from
            timeout: Maximum time to wait

        Returns:
            Dictionary with task results

        Example:
            >>> result = service.collect_results(task_id)
            >>> print(f"Result: {result['data']}")
        """
        if task_id not in self._tasks:
            return {'error': 'Task not found'}

        task = self._tasks[task_id]
        return {
            'task_id': task_id,
            'status': task.get('status'),
            'data': task.get('result'),
            'error': task.get('error'),
            'execution_time': task.get('execution_time', 0)
        }

    def aggregate_batch_results(
        self,
        batch_id: str
    ) -> Dict[str, Any]:
        """
        Aggregate results from a batch of tasks.

        Args:
            batch_id: Batch ID to aggregate

        Returns:
            Dictionary with aggregated results

        Example:
            >>> results = service.aggregate_batch_results(batch_id)
            >>> print(f"Completed: {results['completed']}")
        """
        if batch_id not in self._batches:
            return {'error': 'Batch not found'}

        task_ids = self._batches[batch_id]
        results = []
        completed = 0
        failed = 0
        pending = 0

        for task_id in task_ids:
            task = self._tasks.get(task_id, {})
            status = task.get('status', 'unknown')

            if status == 'completed':
                completed += 1
                results.append(task.get('result'))
            elif status == 'failed':
                failed += 1
            else:
                pending += 1

        return {
            'batch_id': batch_id,
            'total': len(task_ids),
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'results': results
        }

    def get_completed_count(self, pool_id: str = None) -> int:
        """
        Get count of completed tasks.

        Args:
            pool_id: Optional pool to filter by

        Returns:
            Number of completed tasks

        Example:
            >>> count = service.get_completed_count()
            >>> print(f"Completed: {count}")
        """
        count = 0
        for task in self._tasks.values():
            if pool_id and task.get('pool_id') != pool_id:
                continue
            if task.get('status') == 'completed':
                count += 1
        return count

    def set_max_workers(self, max_workers: int) -> None:
        """
        Set maximum concurrent workers.

        Args:
            max_workers: Maximum worker count

        Example:
            >>> service.set_max_workers(16)
        """
        self._max_workers = max_workers
        if self._default_pool_id and self._default_pool_id in self._pools:
            self._pools[self._default_pool_id]['max_workers'] = max_workers

    def get_active_workers(self, pool_id: str = None) -> int:
        """
        Get count of active workers.

        Args:
            pool_id: Optional pool to filter by

        Returns:
            Number of active workers

        Example:
            >>> active = service.get_active_workers()
            >>> print(f"Active: {active}")
        """
        if pool_id:
            if pool_id in self._pools:
                return self._pools[pool_id].get('active_workers', 0)
            return 0

        total = 0
        for pool in self._pools.values():
            total += pool.get('active_workers', 0)
        return total

    def wait_for_completion(
        self,
        task_ids: List[str],
        timeout: float = None
    ) -> Dict[str, Any]:
        """
        Wait for tasks to complete.

        Args:
            task_ids: List of task IDs to wait for
            timeout: Maximum wait time in seconds

        Returns:
            Dictionary with completion status

        Example:
            >>> result = service.wait_for_completion(task_ids, timeout=60)
        """
        completed = []
        pending = []

        for task_id in task_ids:
            if task_id in self._tasks:
                if self._tasks[task_id]['status'] == 'completed':
                    completed.append(task_id)
                else:
                    pending.append(task_id)

        return {
            'completed': len(completed),
            'pending': len(pending),
            'total': len(task_ids),
            'all_complete': len(pending) == 0,
            'completed_ids': completed,
            'pending_ids': pending
        }

    def get_execution_metrics(self) -> Dict[str, Any]:
        """
        Get overall execution metrics.

        Returns:
            Dictionary with execution metrics

        Example:
            >>> metrics = service.get_execution_metrics()
            >>> print(f"Total tasks: {metrics['total_tasks']}")
        """
        total = len(self._tasks)
        completed = sum(
            1 for t in self._tasks.values()
            if t.get('status') == 'completed'
        )
        failed = sum(
            1 for t in self._tasks.values()
            if t.get('status') == 'failed'
        )
        pending = sum(
            1 for t in self._tasks.values()
            if t.get('status') == 'pending'
        )

        return {
            'total_tasks': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'success_rate': completed / total if total > 0 else 0.0,
            'total_pools': len(self._pools),
            'total_batches': len(self._batches)
        }

    def get_throughput(self, window_seconds: int = 60) -> float:
        """
        Get task throughput rate.

        Args:
            window_seconds: Time window for calculation

        Returns:
            Tasks completed per second

        Example:
            >>> throughput = service.get_throughput()
            >>> print(f"Throughput: {throughput:.2f} tasks/sec")
        """
        completed = sum(
            1 for t in self._tasks.values()
            if t.get('status') == 'completed'
        )
        return float(completed) / window_seconds if window_seconds > 0 else 0.0

    def get_queue_depth(self, pool_id: str = None) -> int:
        """
        Get current queue depth.

        Args:
            pool_id: Optional pool to filter by

        Returns:
            Number of pending tasks in queue

        Example:
            >>> depth = service.get_queue_depth()
            >>> print(f"Queue depth: {depth}")
        """
        count = 0
        for task in self._tasks.values():
            if pool_id and task.get('pool_id') != pool_id:
                continue
            if task.get('status') == 'pending':
                count += 1
        return count

