"""
Auto-scaling Validation Service for infrastructure scaling.

This service provides auto-scaling testing and validation
for Celery workers, database connections, and queue management.

Key features:
- Celery worker auto-scaling
- Database connection pool scaling
- Queue depth-based scaling triggers
- Cool-down period validation

Example:
    >>> service = AutoScalingService()
    >>> service.set_worker_limits(min_workers=2, max_workers=10)
    >>> service.scale_workers(target=5)
    >>> status = service.get_scaling_status()
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import time


class AutoScalingService:
    """
    Service for auto-scaling validation and testing.

    Provides scaling management for workers, database pools,
    and queue-based triggers with cool-down validation.

    Example:
        >>> service = AutoScalingService()
        >>> service.set_scaling_thresholds(scale_up=100, scale_down=10)
        >>> event = service.trigger_scale_event('scale_up')
    """

    def __init__(self):
        """Initialize the auto-scaling service."""
        self._worker_count: int = 1
        self._worker_limits: Dict[str, int] = {'min': 1, 'max': 10}
        self._pool_size: int = 5
        self._pool_limits: Dict[str, int] = {'min': 5, 'max': 50}
        self._scaling_thresholds: Dict[str, int] = {
            'scale_up': 100,
            'scale_down': 10
        }
        self._cool_down_seconds: int = 300
        self._last_scale_time: Optional[float] = None
        self._scaling_history: List[Dict[str, Any]] = []

    # Celery Worker Scaling Methods

    def scale_workers(
        self,
        target: int
    ) -> Dict[str, Any]:
        """
        Scale workers to target count.

        Args:
            target: Target worker count

        Returns:
            Dictionary with scaling result

        Example:
            >>> result = service.scale_workers(5)
        """
        # Check cool-down
        if not self.check_cool_down()['can_scale']:
            return {
                'success': False,
                'reason': 'Cool-down period active',
                'worker_count': self._worker_count
            }

        # Apply limits
        min_workers = self._worker_limits['min']
        max_workers = self._worker_limits['max']
        actual_target = max(min_workers, min(max_workers, target))

        previous = self._worker_count
        self._worker_count = actual_target
        self._last_scale_time = time.time()

        # Record event
        event = {
            'type': 'worker_scale',
            'previous': previous,
            'target': actual_target,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._scaling_history.append(event)

        return {
            'success': True,
            'previous_count': previous,
            'new_count': actual_target,
            'requested': target
        }

    def get_worker_count(self) -> Dict[str, Any]:
        """
        Get current worker count.

        Returns:
            Dictionary with worker info

        Example:
            >>> count = service.get_worker_count()
        """
        return {
            'worker_count': self._worker_count,
            'min_workers': self._worker_limits['min'],
            'max_workers': self._worker_limits['max']
        }

    def set_worker_limits(
        self,
        min_workers: int = 1,
        max_workers: int = 10
    ) -> Dict[str, Any]:
        """
        Set worker scaling limits.

        Args:
            min_workers: Minimum worker count
            max_workers: Maximum worker count

        Returns:
            Dictionary with limits

        Example:
            >>> service.set_worker_limits(min_workers=2, max_workers=20)
        """
        self._worker_limits = {
            'min': min_workers,
            'max': max_workers
        }
        return {
            'min_workers': min_workers,
            'max_workers': max_workers,
            'updated_at': datetime.utcnow().isoformat()
        }

    # Database Pool Scaling Methods

    def scale_db_pool(
        self,
        target: int
    ) -> Dict[str, Any]:
        """
        Scale database connection pool.

        Args:
            target: Target pool size

        Returns:
            Dictionary with scaling result

        Example:
            >>> result = service.scale_db_pool(20)
        """
        # Check cool-down
        if not self.check_cool_down()['can_scale']:
            return {
                'success': False,
                'reason': 'Cool-down period active',
                'pool_size': self._pool_size
            }

        # Apply limits
        min_pool = self._pool_limits['min']
        max_pool = self._pool_limits['max']
        actual_target = max(min_pool, min(max_pool, target))

        previous = self._pool_size
        self._pool_size = actual_target
        self._last_scale_time = time.time()

        # Record event
        event = {
            'type': 'pool_scale',
            'previous': previous,
            'target': actual_target,
            'timestamp': datetime.utcnow().isoformat()
        }
        self._scaling_history.append(event)

        return {
            'success': True,
            'previous_size': previous,
            'new_size': actual_target,
            'requested': target
        }

    def get_pool_size(self) -> Dict[str, Any]:
        """
        Get current pool size.

        Returns:
            Dictionary with pool info

        Example:
            >>> size = service.get_pool_size()
        """
        return {
            'pool_size': self._pool_size,
            'min_pool': self._pool_limits['min'],
            'max_pool': self._pool_limits['max']
        }

    def set_pool_limits(
        self,
        min_pool: int = 5,
        max_pool: int = 50
    ) -> Dict[str, Any]:
        """
        Set pool scaling limits.

        Args:
            min_pool: Minimum pool size
            max_pool: Maximum pool size

        Returns:
            Dictionary with limits

        Example:
            >>> service.set_pool_limits(min_pool=10, max_pool=100)
        """
        self._pool_limits = {
            'min': min_pool,
            'max': max_pool
        }
        return {
            'min_pool': min_pool,
            'max_pool': max_pool,
            'updated_at': datetime.utcnow().isoformat()
        }

    # Queue-based Scaling Methods

    def check_queue_depth(
        self,
        queue_name: str = 'default',
        current_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Check queue depth against thresholds.

        Args:
            queue_name: Name of queue
            current_depth: Current queue depth

        Returns:
            Dictionary with queue analysis

        Example:
            >>> result = service.check_queue_depth('tasks', 150)
        """
        scale_up = self._scaling_thresholds['scale_up']
        scale_down = self._scaling_thresholds['scale_down']

        if current_depth >= scale_up:
            action = 'scale_up'
        elif current_depth <= scale_down:
            action = 'scale_down'
        else:
            action = 'maintain'

        return {
            'queue_name': queue_name,
            'current_depth': current_depth,
            'scale_up_threshold': scale_up,
            'scale_down_threshold': scale_down,
            'recommended_action': action
        }

    def set_scaling_thresholds(
        self,
        scale_up: int = 100,
        scale_down: int = 10
    ) -> Dict[str, Any]:
        """
        Set queue depth scaling thresholds.

        Args:
            scale_up: Threshold for scaling up
            scale_down: Threshold for scaling down

        Returns:
            Dictionary with thresholds

        Example:
            >>> service.set_scaling_thresholds(scale_up=200, scale_down=20)
        """
        self._scaling_thresholds = {
            'scale_up': scale_up,
            'scale_down': scale_down
        }
        return {
            'scale_up': scale_up,
            'scale_down': scale_down,
            'updated_at': datetime.utcnow().isoformat()
        }

    def trigger_scale_event(
        self,
        event_type: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Trigger a scaling event.

        Args:
            event_type: Type of event (scale_up, scale_down)
            reason: Optional reason

        Returns:
            Dictionary with event info

        Example:
            >>> event = service.trigger_scale_event('scale_up', 'High queue depth')
        """
        # Check cool-down
        if not self.check_cool_down()['can_scale']:
            return {
                'triggered': False,
                'reason': 'Cool-down period active'
            }

        event = {
            'type': event_type,
            'reason': reason or f'Manual {event_type}',
            'timestamp': datetime.utcnow().isoformat()
        }
        self._scaling_history.append(event)
        self._last_scale_time = time.time()

        return {
            'triggered': True,
            'event': event
        }

    # Cool-down Validation Methods

    def set_cool_down(
        self,
        seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Set cool-down period.

        Args:
            seconds: Cool-down duration in seconds

        Returns:
            Dictionary with cool-down config

        Example:
            >>> service.set_cool_down(600)  # 10 minutes
        """
        self._cool_down_seconds = seconds
        return {
            'cool_down_seconds': seconds,
            'updated_at': datetime.utcnow().isoformat()
        }

    def check_cool_down(self) -> Dict[str, Any]:
        """
        Check if cool-down period is active.

        Returns:
            Dictionary with cool-down status

        Example:
            >>> status = service.check_cool_down()
        """
        if self._last_scale_time is None:
            return {
                'can_scale': True,
                'cool_down_active': False,
                'remaining_seconds': 0
            }

        elapsed = time.time() - self._last_scale_time
        remaining = max(0, self._cool_down_seconds - elapsed)

        return {
            'can_scale': remaining == 0,
            'cool_down_active': remaining > 0,
            'remaining_seconds': int(remaining),
            'cool_down_seconds': self._cool_down_seconds
        }

    def get_last_scale_time(self) -> Dict[str, Any]:
        """
        Get last scaling event time.

        Returns:
            Dictionary with last scale info

        Example:
            >>> last = service.get_last_scale_time()
        """
        if self._last_scale_time is None:
            return {
                'last_scale_time': None,
                'never_scaled': True
            }

        return {
            'last_scale_time': self._last_scale_time,
            'last_scale_iso': datetime.fromtimestamp(self._last_scale_time).isoformat(),
            'seconds_ago': int(time.time() - self._last_scale_time)
        }

    # Reporting Methods

    def get_scaling_history(
        self,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get scaling event history.

        Args:
            limit: Maximum results

        Returns:
            List of scaling events

        Example:
            >>> history = service.get_scaling_history()
        """
        return self._scaling_history[-limit:]

    def get_scaling_status(self) -> Dict[str, Any]:
        """
        Get current scaling status.

        Returns:
            Dictionary with scaling status

        Example:
            >>> status = service.get_scaling_status()
        """
        return {
            'workers': self.get_worker_count(),
            'pool': self.get_pool_size(),
            'thresholds': self._scaling_thresholds,
            'cool_down': self.check_cool_down(),
            'event_count': len(self._scaling_history)
        }
