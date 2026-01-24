"""
Celery worker auto-scaling service.

This service monitors Celery queue depth and adjusts worker concurrency to
match demand. Scaling decisions are expressed as `AutoScalingDecision`
instances so callers can inspect what action (if any) was taken.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable, Optional, Protocol

from celery import Celery


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class QueueMetrics:
    """Simple container for queue depth and active worker counts."""

    queue_depth: int
    active_workers: int


@dataclass(frozen=True)
class AutoScalingDecision:
    """Represents the result of a scaling evaluation."""

    queue_depth: int
    active_workers: int
    target_workers: int
    scaled: bool
    scale_direction: Optional[str]


class MetricsProvider(Protocol):
    """Protocol describing a metrics provider."""

    def get_metrics(self) -> QueueMetrics:
        """Return the latest queue metrics."""
        ...


class CeleryMetricsProvider:
    """
    Fetch queue metrics from Celery using the inspection API.
    """

    def __init__(
        self,
        celery_app: Celery,
        queue_name: str = "default",
    ) -> None:
        self._celery = celery_app
        self._queue_name = queue_name

    def get_metrics(self) -> QueueMetrics:
        inspector = None
        try:
            inspector = self._celery.control.inspect()
        except Exception:  # pragma: no cover - defensive safeguard
            LOGGER.exception("Failed to create Celery inspector")

        queue_depth = self._queue_depth(inspector)
        active_workers = self._active_worker_count(inspector)

        return QueueMetrics(
            queue_depth=max(queue_depth, 0),
            active_workers=max(active_workers, 0),
        )

    def _queue_depth(self, inspector) -> int:
        if inspector is None:
            return 0

        depth = 0
        for attr in ("reserved", "scheduled"):
            try:
                task_map = getattr(inspector, attr)() or {}
            except Exception:  # pragma: no cover - inspection may fail per worker
                LOGGER.debug("Celery inspector.%s call failed", attr, exc_info=True)
                continue
            depth += self._count_tasks(task_map)

        return depth

    def _count_tasks(self, task_map) -> int:
        total = 0
        for tasks in task_map.values():
            for task in tasks:
                queue = self._extract_queue_name(task)
                if self._queue_name is None or queue == self._queue_name:
                    total += 1
        return total

    def _extract_queue_name(self, task) -> str:
        if isinstance(task, dict):
            delivery_info = task.get("delivery_info") or {}
            queue = delivery_info.get("routing_key") or delivery_info.get("queue")
            if queue:
                return queue

            request = task.get("request")
            if isinstance(request, dict):
                return self._extract_queue_name(request)

        return self._queue_name

    def _active_worker_count(self, inspector) -> int:
        if inspector is None:
            return 0

        try:
            stats = inspector.stats() or {}
        except Exception:  # pragma: no cover - inspection may fail per worker
            LOGGER.debug("Celery inspector.stats call failed", exc_info=True)
            return 0

        total = 0
        for info in stats.values():
            pool = info.get("pool") or {}

            max_concurrency = pool.get("max-concurrency") or info.get("pool_max_concurrency")
            if isinstance(max_concurrency, (int, float)):
                total += int(max_concurrency)
                continue

            processes = pool.get("processes")
            if isinstance(processes, list):
                total += len(processes)

        if total == 0 and stats:
            total = len(stats)

        return total


class CeleryWorkerAutoScaler:
    """
    Monitor queue metrics and adjust Celery worker concurrency.
    """

    def __init__(
        self,
        *,
        celery_app: Celery,
        metrics_provider: Optional[MetricsProvider] = None,
        min_workers: int = 1,
        max_workers: int = 10,
        target_tasks_per_worker: int = 10,
        scale_down_queue_threshold: int = 0,
        cooldown_seconds: int = 30,
        queue_name: str = "default",
        enabled: bool = True,
        time_provider: Callable[[], datetime] | None = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        if min_workers < 0:
            raise ValueError("min_workers cannot be negative")
        if max_workers < 1:
            raise ValueError("max_workers must be at least 1")
        if max_workers < min_workers:
            raise ValueError("max_workers must be >= min_workers")
        if target_tasks_per_worker <= 0:
            raise ValueError("target_tasks_per_worker must be > 0")
        if cooldown_seconds < 0:
            raise ValueError("cooldown_seconds cannot be negative")

        self._celery = celery_app
        self._min_workers = min_workers
        self._max_workers = max_workers
        self._target_tasks_per_worker = target_tasks_per_worker
        self._scale_down_queue_threshold = max(scale_down_queue_threshold, 0)
        self._cooldown_seconds = cooldown_seconds
        self._enabled = enabled
        self._time_provider = time_provider or datetime.utcnow
        self._logger = logger or LOGGER

        if metrics_provider is not None:
            self._metrics_provider = metrics_provider
        else:
            self._metrics_provider = CeleryMetricsProvider(
                celery_app=celery_app,
                queue_name=queue_name,
            )

        self._last_scale_at: Optional[datetime] = None

    def evaluate_and_scale(self) -> AutoScalingDecision:
        metrics = self._metrics_provider.get_metrics()
        queue_depth = max(metrics.queue_depth, 0)
        active_workers = max(metrics.active_workers, 0)

        target_workers = self._determine_target_workers(queue_depth)
        target_workers = min(max(target_workers, self._min_workers), self._max_workers)

        scaled = False
        direction: Optional[str] = None

        if not self._enabled:
            return AutoScalingDecision(queue_depth, active_workers, target_workers, scaled, direction)

        if not self._cooldown_elapsed():
            return AutoScalingDecision(queue_depth, active_workers, target_workers, scaled, direction)

        delta = target_workers - active_workers

        try:
            if delta > 0:
                self._celery.control.pool_grow(delta)
                scaled = True
                direction = "grow"
            elif delta < 0:
                self._celery.control.pool_shrink(-delta)
                scaled = True
                direction = "shrink"

            if scaled:
                self._last_scale_at = self._time_provider()
        except Exception:  # pragma: no cover - Celery may raise on control operations
            self._logger.exception("Failed to adjust Celery pool size by %s", delta)

        return AutoScalingDecision(queue_depth, active_workers, target_workers, scaled, direction)

    def _determine_target_workers(self, queue_depth: int) -> int:
        if queue_depth <= self._scale_down_queue_threshold:
            return self._min_workers

        return math.ceil(queue_depth / self._target_tasks_per_worker)

    def _cooldown_elapsed(self) -> bool:
        if self._cooldown_seconds == 0:
            return True

        if self._last_scale_at is None:
            return True

        now = self._time_provider()
        return now - self._last_scale_at >= timedelta(seconds=self._cooldown_seconds)
