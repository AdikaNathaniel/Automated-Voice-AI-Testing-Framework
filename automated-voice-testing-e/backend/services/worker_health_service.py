"""
Worker health monitoring service.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

from celery import Celery


@dataclass(frozen=True)
class WorkerStatus:
    """Represents the status of an individual worker."""

    name: str
    status: str
    active_tasks: int
    max_concurrency: int
    queues: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class WorkerAlert:
    """Represents a health alert for worker monitoring."""

    level: str
    message: str


@dataclass(frozen=True)
class WorkerHealthReport:
    """Aggregate health report for Celery workers."""

    status: str
    total_workers: int
    total_online: int
    total_offline: int
    workers: List[WorkerStatus] = field(default_factory=list)
    alerts: List[WorkerAlert] = field(default_factory=list)


class WorkerHealthService:
    """Service that inspects Celery workers and reports their health."""

    def __init__(
        self,
        *,
        celery_app: Celery,
        inspector_factory: Optional[Callable[[], object]] = None,
    ) -> None:
        self._celery = celery_app
        self._inspector_factory = inspector_factory or (lambda: self._celery.control.inspect())

    def check_health(self) -> WorkerHealthReport:
        inspector = self._inspector_factory()
        if inspector is None:
            return self._empty_report(
                status="critical",
                alert_message="Unable to create Celery inspector (no workers reachable).",
            )

        ping_result = inspector.ping()
        if not ping_result:
            return self._empty_report(
                status="critical",
                alert_message="No Celery workers responded to ping.",
            )

        stats = inspector.stats() or {}
        active = inspector.active() or {}
        registered = inspector.registered() or {}

        workers: List[WorkerStatus] = []
        for worker_name, ping_data in sorted(ping_result.items()):
            worker_stats = stats.get(worker_name) or {}
            pool_info = worker_stats.get("pool") or {}

            max_concurrency = (
                pool_info.get("max-concurrency")
                or worker_stats.get("pool_max_concurrency")
                or 0
            )

            active_tasks = len(active.get(worker_name) or [])

            queues = tuple(worker_stats.get("queues") or ())
            if not queues and isinstance(registered, dict):
                queues = tuple(registered.get(worker_name) or ())

            workers.append(
                WorkerStatus(
                    name=worker_name,
                    status="online" if ping_data else "unknown",
                    active_tasks=active_tasks,
                    max_concurrency=int(max_concurrency),
                    queues=queues,
                )
            )

        total_workers = len(workers)
        status = "healthy" if total_workers else "degraded"

        return WorkerHealthReport(
            status=status,
            total_workers=total_workers,
            total_online=total_workers,
            total_offline=0,
            workers=workers,
            alerts=[],
        )

    def _empty_report(self, *, status: str, alert_message: str) -> WorkerHealthReport:
        return WorkerHealthReport(
            status=status,
            total_workers=0,
            total_online=0,
            total_offline=0,
            workers=[],
            alerts=[WorkerAlert(level=status, message=alert_message)],
        )
