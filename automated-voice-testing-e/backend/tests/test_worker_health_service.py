"""
Tests for worker health monitoring service (TASK-285).
"""

from __future__ import annotations

from typing import Dict, List
from unittest.mock import MagicMock
from pathlib import Path
import sys
import os

# Add parent directory (backend) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.worker_health_service import (
    WorkerHealthService,
    WorkerHealthReport,
    WorkerStatus,
)


def _mock_celery(inspect_payloads: Dict[str, Dict[str, object]]) -> MagicMock:
    celery = MagicMock()
    control = MagicMock()
    inspector = MagicMock()

    control.inspect.return_value = inspector
    celery.control = control

    inspector.ping.return_value = inspect_payloads.get("ping")
    inspector.stats.return_value = inspect_payloads.get("stats")
    inspector.active.return_value = inspect_payloads.get("active")
    inspector.registered.return_value = inspect_payloads.get("registered")

    return celery


def test_worker_health_reports_online_workers():
    celery = _mock_celery(
        {
            "ping": {
                "worker-a@example": {"ok": "pong"},
                "worker-b@example": {"ok": "pong"},
            },
            "stats": {
                "worker-a@example": {"pool": {"max-concurrency": 4}},
                "worker-b@example": {"pool": {"max-concurrency": 2}},
            },
            "active": {
                "worker-a@example": [{"id": "task-1"}, {"id": "task-2"}],
                "worker-b@example": [],
            },
        }
    )

    service = WorkerHealthService(celery_app=celery)
    report = service.check_health()

    assert isinstance(report, WorkerHealthReport)
    assert report.status == "healthy"
    assert report.total_workers == 2
    assert report.total_offline == 0
    assert not report.alerts

    workers: List[WorkerStatus] = report.workers
    worker_a = next(w for w in workers if w.name == "worker-a@example")
    assert worker_a.status == "online"
    assert worker_a.active_tasks == 2
    assert worker_a.max_concurrency == 4


def test_worker_health_alerts_when_no_workers_respond():
    celery = _mock_celery({"ping": None, "stats": None, "active": None})
    service = WorkerHealthService(celery_app=celery)

    report = service.check_health()

    assert report.status == "critical"
    assert report.total_workers == 0
    assert report.total_offline == 0
    assert report.alerts, "Expected alert when no workers respond"
    assert report.alerts[0].level == "critical"
