"""
Real-time metrics aggregation service (TASK-222).

Provides helpers to synthesise an overview of active executions, queue depth,
and recent throughput for dashboard consumption.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.suite_run import SuiteRun
from models.defect import Defect
from models.edge_case import EdgeCase
from services.metrics_service import MetricsService
from services.queue_manager import get_queue_stats


class RealTimeMetricsService:
    """
    Service class for real-time metrics aggregation.

    Provides methods to aggregate active executions, queue depth,
    and throughput for dashboard consumption.

    Example:
        >>> service = RealTimeMetricsService()
        >>> metrics = await service.get_real_time_metrics(db)
    """

    def __init__(self):
        """Initialize the real-time metrics service."""
        self.default_window_minutes = 15
        self.default_max_runs = 5

    async def get_real_time_metrics(
        self,
        db: Optional[AsyncSession],
        *,
        window_minutes: int = 15,
        max_runs: int = 5
    ) -> Dict[str, Any]:
        """Aggregate real-time execution telemetry."""
        return await get_real_time_metrics(
            db, window_minutes=window_minutes, max_runs=max_runs
        )


async def get_real_time_metrics(
    db: Optional[AsyncSession],
    *,
    window_minutes: int = 15,
    max_runs: int = 5,
) -> Dict[str, Any]:
    """
    Aggregate real-time execution telemetry.

    Args:
        db: Async database session.
        window_minutes: Rolling window for throughput calculations.
        max_runs: Maximum number of active runs to return.

    Returns:
        Dictionary containing current runs, queue depth, and throughput payloads.
    """
    if window_minutes <= 0:
        raise ValueError("window_minutes must be greater than zero")
    if max_runs <= 0:
        raise ValueError("max_runs must be greater than zero")

    now = _utcnow()

    active_runs = await _fetch_active_suite_runs(db, limit=max_runs)
    serialized_runs = [_serialize_run(run) for run in active_runs]

    queue_depth = (
        await get_queue_stats(db)
        if db is not None
        else {
            "total": 0,
            "queued": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "average_priority": 0.0,
            "oldest_queued_seconds": None,
        }
    )

    throughput = await _calculate_throughput(
        db,
        now=now,
        window_minutes=window_minutes,
    )

    run_counts = await _aggregate_run_status_counts(db)
    issue_summary = await _fetch_defect_edge_counts(db, now=now)

    return {
        "current_runs": serialized_runs,
        "queue_depth": queue_depth,
        "throughput": throughput,
        "run_counts": run_counts,
        "issue_summary": issue_summary,
    }


async def _fetch_active_suite_runs(
    db: Optional[AsyncSession],
    *,
    limit: int,
) -> List[SuiteRun]:
    if db is None:
        return []

    stmt = (
        select(SuiteRun)
        .options(selectinload(SuiteRun.test_suite))
        .where(SuiteRun.status.in_(("running", "pending")))
        .order_by(SuiteRun.started_at.desc().nullslast(), SuiteRun.created_at.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def _calculate_throughput(
    db: Optional[AsyncSession],
    *,
    now: datetime,
    window_minutes: int,
) -> Dict[str, Any]:
    if db is None:
        # Without a DB session we cannot query metrics; fall back to zeros.
        return {
            "tests_per_minute": 0.0,
            "sample_size": 0,
            "window_minutes": window_minutes,
            "last_updated": _format_datetime(now),
        }

    metrics_service = MetricsService(db)
    start_time = now - timedelta(minutes=window_minutes)
    entries = await metrics_service.get_metrics(
        metric_type="validation_pass",
        start_time=start_time,
        end_time=now,
        granularity="raw",
        dimensions={"aggregation": "raw"},
    )

    sample_size = _count_entries(entries)
    tests_per_minute = round(sample_size / window_minutes, 2) if window_minutes else 0.0

    return {
        "tests_per_minute": tests_per_minute,
        "sample_size": sample_size,
        "window_minutes": window_minutes,
        "last_updated": _format_datetime(now),
    }


def _count_entries(entries: Iterable[Dict[str, Any]]) -> int:
    total = 0
    for entry in entries:
        total += int(entry.get("count", 0) or 0)
    return total


def _serialize_run(run: SuiteRun) -> Dict[str, Any]:
    total = int(run.total_tests or 0)
    passed = int(run.passed_tests or 0)
    failed = int(run.failed_tests or 0)
    skipped = int(run.skipped_tests or 0)
    completed = passed + failed + skipped
    progress_pct = round((completed / total) * 100, 2) if total > 0 else 0.0

    return {
        "id": str(run.id),
        "suite_id": str(run.suite_id) if getattr(run, "suite_id", None) else None,
        "suite_name": getattr(getattr(run, "test_suite", None), "name", None),
        "status": getattr(run, "status", None),
        "progress_pct": progress_pct,
        "total_tests": total,
        "passed_tests": passed,
        "failed_tests": failed,
        "skipped_tests": skipped,
        "started_at": _format_datetime(getattr(run, "started_at", None)),
        "completed_at": _format_datetime(getattr(run, "completed_at", None)),
    }


def _format_datetime(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _aggregate_run_status_counts(
    db: Optional[AsyncSession],
) -> Dict[str, int]:
    defaults = {
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    }
    if db is None:
        return defaults

    stmt = select(SuiteRun.status, func.count()).group_by(SuiteRun.status)
    result = await db.execute(stmt)
    counts = dict(defaults)
    for status, count in result.all():
        if status in counts:
            counts[status] = counts.get(status, 0) + int(count or 0)
    return counts


async def _fetch_defect_edge_counts(
    db: Optional[AsyncSession],
    *,
    now: datetime,
) -> Dict[str, int]:
    defaults = {
        "open_defects": 0,
        "critical_defects": 0,
        "edge_cases_active": 0,
        "edge_cases_new": 0,
    }
    if db is None:
        return defaults

    open_defects_stmt = select(func.count(Defect.id)).where(Defect.status != "resolved")
    critical_defects_stmt = select(func.count(Defect.id)).where(
        Defect.status != "resolved",
        func.lower(Defect.severity) == "critical",
    )
    active_edge_stmt = select(func.count(EdgeCase.id)).where(EdgeCase.status == "active")
    recent_window = now - timedelta(days=7)
    new_edge_stmt = select(func.count(EdgeCase.id)).where(EdgeCase.created_at >= recent_window)

    open_defects = (await db.execute(open_defects_stmt)).scalar() or 0
    critical_defects = (await db.execute(critical_defects_stmt)).scalar() or 0
    edge_cases_active = (await db.execute(active_edge_stmt)).scalar() or 0
    edge_cases_new = (await db.execute(new_edge_stmt)).scalar() or 0

    return {
        "open_defects": int(open_defects),
        "critical_defects": int(critical_defects),
        "edge_cases_active": int(edge_cases_active),
        "edge_cases_new": int(edge_cases_new),
    }
