"""
Unit tests for Celery worker auto-scaling service.

These tests define the expected behaviour for TASK-283:
 - Scaling up when queue depth is high
 - Scaling down when queue depth is low
 - Respecting min/max worker limits and cooldown windows
 - Supporting disabled auto-scaling without invoking Celery control APIs
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, List
from unittest.mock import MagicMock


import sys
import os

# Add parent directory (backend) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.worker_scaling_service import (
    AutoScalingDecision,
    CeleryWorkerAutoScaler,
    QueueMetrics,
)


class MetricsSequence:
    """
    Helper provider that returns a sequence of QueueMetrics for successive calls.
    """

    def __init__(self, metrics: Iterable[QueueMetrics]) -> None:
        self._metrics: List[QueueMetrics] = list(metrics)
        self._index = 0

    def get_metrics(self) -> QueueMetrics:
        if self._index >= len(self._metrics):
            raise AssertionError("MetricsSequence exhausted")
        item = self._metrics[self._index]
        self._index += 1
        return item


def _make_celery_mock() -> MagicMock:
    celery_app = MagicMock()
    celery_app.control = MagicMock()
    celery_app.control.pool_grow = MagicMock()
    celery_app.control.pool_shrink = MagicMock()
    return celery_app


def test_scale_up_when_queue_exceeds_capacity():
    celery_app = _make_celery_mock()
    metrics = MetricsSequence([
        QueueMetrics(queue_depth=40, active_workers=2),
    ])

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery_app,
        metrics_provider=metrics,
        min_workers=1,
        max_workers=10,
        target_tasks_per_worker=10,
        scale_down_queue_threshold=0,
        cooldown_seconds=0,
    )

    decision = scaler.evaluate_and_scale()

    celery_app.control.pool_grow.assert_called_once_with(2)
    celery_app.control.pool_shrink.assert_not_called()
    assert isinstance(decision, AutoScalingDecision)
    assert decision.queue_depth == 40
    assert decision.target_workers == 4
    assert decision.scaled is True
    assert decision.scale_direction == "grow"


def test_scale_down_when_queue_is_empty():
    celery_app = _make_celery_mock()
    metrics = MetricsSequence([
        QueueMetrics(queue_depth=0, active_workers=5),
    ])

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery_app,
        metrics_provider=metrics,
        min_workers=1,
        max_workers=10,
        target_tasks_per_worker=10,
        scale_down_queue_threshold=0,
        cooldown_seconds=0,
    )

    decision = scaler.evaluate_and_scale()

    celery_app.control.pool_grow.assert_not_called()
    celery_app.control.pool_shrink.assert_called_once_with(4)
    assert decision.target_workers == 1
    assert decision.scaled is True
    assert decision.scale_direction == "shrink"


def test_respects_max_worker_limit():
    celery_app = _make_celery_mock()
    metrics = MetricsSequence([
        QueueMetrics(queue_depth=150, active_workers=5),
    ])

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery_app,
        metrics_provider=metrics,
        min_workers=1,
        max_workers=12,
        target_tasks_per_worker=10,
        scale_down_queue_threshold=0,
        cooldown_seconds=0,
    )

    decision = scaler.evaluate_and_scale()

    # Target would be ceil(150 / 10) = 15, but max is 12 so delta = 7
    celery_app.control.pool_grow.assert_called_once_with(7)
    assert decision.target_workers == 12


def test_honours_cooldown_window():
    celery_app = _make_celery_mock()

    metrics = MetricsSequence([
        QueueMetrics(queue_depth=50, active_workers=2),
        QueueMetrics(queue_depth=5, active_workers=5),
    ])

    now = datetime.utcnow()
    times = [now, now + timedelta(seconds=10)]

    def time_provider():
        if not times:
            raise AssertionError("time_provider exhausted")
        return times.pop(0)

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery_app,
        metrics_provider=metrics,
        min_workers=1,
        max_workers=10,
        target_tasks_per_worker=10,
        scale_down_queue_threshold=0,
        cooldown_seconds=30,
        time_provider=time_provider,
    )

    first_decision = scaler.evaluate_and_scale()
    assert first_decision.scaled is True
    celery_app.control.pool_grow.assert_called_once_with(3)

    # Second call occurs within cooldown window; should not scale down yet
    second_decision = scaler.evaluate_and_scale()
    celery_app.control.pool_shrink.assert_not_called()
    assert second_decision.scaled is False
    assert second_decision.target_workers == 1  # Desired target, but action deferred


def test_disabled_auto_scaling_skips_actions():
    celery_app = _make_celery_mock()
    metrics = MetricsSequence([
        QueueMetrics(queue_depth=100, active_workers=1),
    ])

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery_app,
        metrics_provider=metrics,
        min_workers=1,
        max_workers=5,
        target_tasks_per_worker=10,
        scale_down_queue_threshold=0,
        cooldown_seconds=0,
        enabled=False,
    )

    decision = scaler.evaluate_and_scale()

    celery_app.control.pool_grow.assert_not_called()
    celery_app.control.pool_shrink.assert_not_called()
    assert decision.scaled is False
    assert decision.scale_direction is None
