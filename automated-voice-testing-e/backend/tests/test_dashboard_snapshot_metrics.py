"""
Tests for dashboard snapshot aggregation logic (TODO §4.1).
"""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "supersecretkey1234")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from services import dashboard_service


class MetricsStub:
    """Stub MetricsService collecting calls and returning canned responses."""

    def __init__(self, db: Any, *, responses: Dict[str, List[Dict[str, Any]]], calls: List[Dict[str, Any]]):
        self.responses = responses
        self.calls = calls
        self.db = db

    async def get_metrics(
        self,
        *,
        metric_type: str,
        start_time: datetime,
        end_time: datetime,
        granularity: str,
        dimensions: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        self.calls.append(
            {
                "metric_type": metric_type,
                "start_time": start_time,
                "end_time": end_time,
                "granularity": granularity,
            }
        )
        return list(self.responses.get(metric_type, []))


def _patch_datetime(monkeypatch: pytest.MonkeyPatch, fixed_now: datetime) -> None:
    class _FixedDateTime(datetime):  # type: ignore[misc]
        @classmethod
        def now(cls, tz=None):
            if tz:
                return fixed_now.astimezone(tz)
            return fixed_now

    monkeypatch.setattr(dashboard_service, "datetime", _FixedDateTime)


@pytest.mark.asyncio
async def test_compute_dashboard_snapshot_aggregates_kpis(monkeypatch: pytest.MonkeyPatch):
    fixed_now = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    responses = {
        "execution_time": [
            {"metric_value": 1.0, "count": 1},
            {"metric_value": 1.0, "count": 2},
        ],
        "response_time": [
            {"metric_value": 2.0, "count": 1},
        ],
        "validation_confidence": [
            {"metric_value": 0.9, "count": 5},
        ],
        "validation_pass": [
            {"metric_value": 0.8, "count": 5},
        ],
    }
    calls: List[Dict[str, Any]] = []

    monkeypatch.setattr(
        dashboard_service,
        "MetricsService",
        lambda db: MetricsStub(db, responses=responses, calls=calls),
    )

    snapshot = await dashboard_service._compute_dashboard_snapshot(db=object(), time_range="24h")

    assert snapshot["kpis"]["tests_executed"] == 3
    assert snapshot["kpis"]["system_health_pct"] == 80.0
    assert snapshot["kpis"]["issues_detected"] == 1
    assert snapshot["kpis"]["avg_response_time_ms"] == 2000.0

    assert snapshot["real_time_execution"]["tests_passed"] == 4
    assert snapshot["real_time_execution"]["tests_failed"] == 1
    assert snapshot["real_time_execution"]["progress_pct"] == 100.0

    assert snapshot["validation_accuracy"]["overall_accuracy_pct"] == 80.0
    assert snapshot["validation_accuracy"]["total_validations"] == 5
    assert snapshot["validation_accuracy"]["time_saved_hours"] == 0.08

    assert snapshot["language_coverage"] == []
    assert snapshot["defects"]["open"] == 0
    assert snapshot["updated_at"] == fixed_now.isoformat().replace("+00:00", "Z")


@pytest.mark.asyncio
async def test_dashboard_snapshot_uses_time_range_windows(monkeypatch: pytest.MonkeyPatch):
    fixed_now = datetime(2024, 6, 1, 9, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    responses: Dict[str, List[Dict[str, Any]]] = {
        "execution_time": [],
        "response_time": [],
        "validation_confidence": [],
        "validation_pass": [],
    }
    calls: List[Dict[str, Any]] = []

    monkeypatch.setattr(
        dashboard_service,
        "MetricsService",
        lambda db: MetricsStub(db, responses=responses, calls=calls),
    )

    await dashboard_service._compute_dashboard_snapshot(db=object(), time_range="1h")

    assert len(calls) == 4
    expected_start = fixed_now - timedelta(hours=1)
    for call in calls:
        assert call["start_time"] == expected_start
        assert call["end_time"] == fixed_now
        assert call["granularity"] == "raw"


@pytest.mark.asyncio
async def test_dashboard_snapshot_includes_frontend_sections(monkeypatch: pytest.MonkeyPatch):
    fixed_now = datetime(2025, 1, 1, 0, 0, tzinfo=timezone.utc)
    _patch_datetime(monkeypatch, fixed_now)

    responses: Dict[str, List[Dict[str, Any]]] = {
        "execution_time": [],
        "response_time": [],
        "validation_confidence": [],
        "validation_pass": [],
    }
    calls: List[Dict[str, Any]] = []

    monkeypatch.setattr(
        dashboard_service,
        "MetricsService",
        lambda db: MetricsStub(db, responses=responses, calls=calls),
    )

    snapshot = await dashboard_service._compute_dashboard_snapshot(db=object(), time_range="24h")

    assert snapshot["defects_trend"] == []
    assert snapshot["test_coverage"] == []
    assert snapshot["cicd_status"] == {"pipelines": [], "incidents": 0}
    assert snapshot["edge_cases"] == {
        "total": 0,
        "resolved": 0,
        "categories": [],
    }
