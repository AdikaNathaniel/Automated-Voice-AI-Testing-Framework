"""
Tests for the real-time metrics service (TASK-222).

Validates that real-time aggregation combines active runs, queue statistics,
and throughput calculations.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import os
import pytest

# Minimal environment so settings-dependent imports succeed.
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from services import real_time_metrics_service


@pytest.mark.asyncio
async def test_get_real_time_metrics_combines_sources(monkeypatch: pytest.MonkeyPatch):
    now = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    monkeypatch.setattr(real_time_metrics_service, "_utcnow", lambda: now)

    active_runs = [
        SimpleNamespace(id=uuid4(),
            suite_id=uuid4(),
            status="running",
            started_at=now - timedelta(minutes=5),
            completed_at=None,
            total_tests=10,
            passed_tests=4,
            failed_tests=1,
            skipped_tests=0,
            test_suite=SimpleNamespace(name="Smoke Suite"),
        )
    ]
    fetch_runs = AsyncMock(return_value=active_runs)
    monkeypatch.setattr(
        real_time_metrics_service,
        "_fetch_active_test_runs",
        fetch_runs,
    )

    queue_stats = {
        "total": 12,
        "queued": 5,
        "processing": 3,
        "completed": 3,
        "failed": 1,
        "average_priority": 6.5,
        "oldest_queued_seconds": 42.0,
    }
    queue_mock = AsyncMock(return_value=queue_stats)
    monkeypatch.setattr(
        real_time_metrics_service,
        "get_queue_stats",
        queue_mock,
    )

    metrics_entries = [
        {"timestamp": now - timedelta(minutes=3), "metric_value": 1.0, "count": 1},
        {"timestamp": now - timedelta(minutes=1), "metric_value": 0.0, "count": 1},
    ]
    metrics_spy = AsyncMock(return_value=metrics_entries)

    run_counts = {
        "pending": 2,
        "running": 3,
        "completed": 5,
        "failed": 1,
        "cancelled": 0,
    }
    run_counts_mock = AsyncMock(return_value=run_counts)
    monkeypatch.setattr(
        real_time_metrics_service,
        "_aggregate_run_status_counts",
        run_counts_mock,
    )

    issue_summary = {
        "open_defects": 4,
        "critical_defects": 1,
        "edge_cases_active": 7,
        "edge_cases_new": 2,
    }
    issue_mock = AsyncMock(return_value=issue_summary)
    monkeypatch.setattr(
        real_time_metrics_service,
        "_fetch_defect_edge_counts",
        issue_mock,
    )

    class FakeMetricsService:
        def __init__(self, db):
            self.db = db

        async def get_metrics(self, **kwargs):
            return await metrics_spy(**kwargs)

    monkeypatch.setattr(
        real_time_metrics_service,
        "MetricsService",
        FakeMetricsService,
    )

    db_sentinel = object()
    result = await real_time_metrics_service.get_real_time_metrics(
        db=db_sentinel,
        window_minutes=10,
        max_runs=5,
    )

    assert fetch_runs.await_count == 1
    fetch_args = fetch_runs.await_args
    assert fetch_args.args[0] is db_sentinel
    assert fetch_args.kwargs["limit"] == 5
    queue_mock.assert_awaited_once()
    run_counts_mock.assert_awaited_once()
    issue_mock.assert_awaited_once()
    assert "now" in issue_mock.await_args.kwargs
    metrics_spy.assert_awaited_once()
    metrics_kwargs = metrics_spy.await_args.kwargs
    assert metrics_kwargs["metric_type"] == "validation_pass"
    assert metrics_kwargs["granularity"] == "raw"
    assert metrics_kwargs["dimensions"] == {"aggregation": "raw"}
    assert metrics_kwargs["end_time"] == now
    assert metrics_kwargs["start_time"] == now - timedelta(minutes=10)

    assert result["queue_depth"] == queue_stats
    assert result["throughput"]["window_minutes"] == 10
    assert result["throughput"]["sample_size"] == 2
    assert result["throughput"]["tests_per_minute"] == pytest.approx(0.2)
    assert result["throughput"]["last_updated"] == now.isoformat().replace("+00:00", "Z")

    assert len(result["current_runs"]) == 1
    current = result["current_runs"][0]
    assert current["status"] == "running"
    assert current["suite_name"] == "Smoke Suite"
    assert current["progress_pct"] == pytest.approx(50.0)
    assert current["total_tests"] == 10
    assert current["passed_tests"] == 4
    assert current["failed_tests"] == 1
    assert current["skipped_tests"] == 0
    assert current["started_at"] == (now - timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    assert result["run_counts"] == run_counts
    assert result["issue_summary"] == issue_summary


@pytest.mark.asyncio
async def test_real_time_metrics_defaults_without_db(monkeypatch: pytest.MonkeyPatch):
    queue_stub = AsyncMock()
    monkeypatch.setattr(real_time_metrics_service, "get_queue_stats", queue_stub)
    run_counts_mock = AsyncMock(return_value={
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    })
    monkeypatch.setattr(
        real_time_metrics_service,
        "_aggregate_run_status_counts",
        run_counts_mock,
    )
    issue_mock = AsyncMock(return_value={
        "open_defects": 0,
        "critical_defects": 0,
        "edge_cases_active": 0,
        "edge_cases_new": 0,
    })
    monkeypatch.setattr(
        real_time_metrics_service,
        "_fetch_defect_edge_counts",
        issue_mock,
    )

    result = await real_time_metrics_service.get_real_time_metrics(
        db=None,
        window_minutes=15,
        max_runs=5,
    )

    queue_stub.assert_not_called()
    run_counts_mock.assert_awaited_once_with(None)
    issue_mock.assert_awaited_once()

    assert result["current_runs"] == []
    assert result["queue_depth"]["total"] == 0
    assert result["run_counts"] == {
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
        "cancelled": 0,
    }
    assert result["issue_summary"] == {
        "open_defects": 0,
        "critical_defects": 0,
        "edge_cases_active": 0,
        "edge_cases_new": 0,
    }
