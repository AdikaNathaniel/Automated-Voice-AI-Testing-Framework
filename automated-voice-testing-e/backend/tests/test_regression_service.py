"""
Regression service unit tests (TODO §4.2 regression dashboards).

These tests focus on the list_regressions helper, ensuring it pipes current
results through the detection logic and emits a summary/items payload the API
can return.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest

from services import regression_service
from services.regression_detection_service import TestResultSnapshot


def _snapshot(status: str, *, metrics: dict | None = None) -> TestResultSnapshot:
    return TestResultSnapshot(
        script_id=uuid4(),
        status=status,
        metrics=metrics or {},
    )


@pytest.mark.asyncio
async def test_list_regressions_returns_detection_report(monkeypatch: pytest.MonkeyPatch):
    suite_id = uuid4()
    baseline = _snapshot("passed", metrics={"intent_confidence": 0.95})
    current = TestResultSnapshot(
        script_id=baseline.script_id,
        status="failed",
        metrics={"intent_confidence": 0.70},
    )

    candidate = regression_service.RegressionCandidate(
        snapshot=current,
        detected_at=datetime(2025, 1, 1, 12, 0, tzinfo=timezone.utc),
    )

    async def fake_fetch_current(db, *, filters, pagination):
        assert filters == {"suite_id": suite_id}
        assert "skip" in pagination and "limit" in pagination
        return {baseline.script_id: candidate}

    async def fake_fetch_baselines(db, script_ids):
        assert list(script_ids) == [baseline.script_id]
        return {baseline.script_id: baseline}

    monkeypatch.setattr(regression_service, "_fetch_current_snapshots", fake_fetch_current)
    monkeypatch.setattr(regression_service, "_fetch_baselines", fake_fetch_baselines)

    result = await regression_service.list_regressions(
        db=SimpleNamespace(),
        filters={"suite_id": suite_id},
        pagination={"skip": 0, "limit": 50},
    )

    assert result["summary"]["total_regressions"] == 2
    assert result["summary"]["status_regressions"] == 1
    assert result["summary"]["metric_regressions"] == 1
    assert len(result["items"]) == 2
    categories = {item["category"] for item in result["items"]}
    assert categories == {"status", "metric"}
    status_finding = next(item for item in result["items"] if item["category"] == "status")
    assert status_finding["regression_detected_at"] == "2025-01-01T12:00:00Z"


@pytest.mark.asyncio
async def test_list_regressions_returns_empty_when_no_snapshots(monkeypatch: pytest.MonkeyPatch):
    async def fake_fetch_current(*_args, **_kwargs):
        return {}

    async def fake_fetch_baselines(*_args, **_kwargs):
        raise AssertionError("should not fetch baselines when no current data")

    monkeypatch.setattr(regression_service, "_fetch_current_snapshots", fake_fetch_current)
    monkeypatch.setattr(regression_service, "_fetch_baselines", fake_fetch_baselines)

    result = await regression_service.list_regressions(
        db=SimpleNamespace(),
        filters={},
        pagination={"skip": 0, "limit": 25},
    )

    assert result["summary"] == {
        "total_regressions": 0,
        "status_regressions": 0,
        "metric_regressions": 0,
    }
    assert result["items"] == []


@pytest.mark.asyncio
async def test_get_regression_comparison_returns_differences(monkeypatch: pytest.MonkeyPatch):
    script_id = uuid4()
    baseline_snapshot = TestResultSnapshot(
        script_id=script_id,
        status="passed",
        metrics={"pass_rate": 0.95, "latency_ms": 110},
    )
    current_snapshot = TestResultSnapshot(
        script_id=script_id,
        status="failed",
        metrics={"pass_rate": 0.82, "latency_ms": 145},
    )

    async def fake_load(db, script_id):
        return baseline_snapshot if script_id == baseline_snapshot.script_id else None

    monkeypatch.setattr(
        regression_service,
        "_load_single_baseline",
        fake_load,
    )

    candidate = regression_service.RegressionCandidate(
        snapshot=current_snapshot,
        detected_at=datetime(2025, 1, 4, 12, 0, tzinfo=timezone.utc),
    )
    async def fake_fetch_latest(db, script_id):
        return candidate if script_id == baseline_snapshot.script_id else None

    monkeypatch.setattr(
        regression_service,
        "_fetch_latest_execution_snapshot",
        fake_fetch_latest,
    )

    result = await regression_service.get_regression_comparison(
        db=SimpleNamespace(),
        script_id=script_id,
    )

    assert result["script_id"] == str(script_id)
    assert result["baseline"]["status"] == "passed"
    assert result["current"]["status"] == "failed"
    metrics = result["differences"]
    assert any(entry["metric"] == "pass_rate" for entry in metrics)
    pass_rate_diff = next(entry for entry in metrics if entry["metric"] == "pass_rate")
    assert pass_rate_diff["baseline_value"] == pytest.approx(0.95)
    assert pass_rate_diff["current_value"] == pytest.approx(0.82)
    assert pass_rate_diff["delta"] == pytest.approx(-0.13)
    assert pass_rate_diff["delta_pct"] == pytest.approx(-13.684, rel=1e-3)


@pytest.mark.asyncio
async def test_get_regression_comparison_requires_baseline(monkeypatch: pytest.MonkeyPatch):
    script_id = uuid4()
    async def fake_load_none(db, script_id):
        return None

    monkeypatch.setattr(
        regression_service,
        "_load_single_baseline",
        fake_load_none,
    )
    async def fake_fetch_candidate(db, script_id):
        return regression_service.RegressionCandidate(
            snapshot=_snapshot("passed"), detected_at=None
        )

    monkeypatch.setattr(
        regression_service,
        "_fetch_latest_execution_snapshot",
        fake_fetch_candidate,
    )

    with pytest.raises(ValueError):
        await regression_service.get_regression_comparison(
            db=SimpleNamespace(),
            script_id=script_id,
        )


@pytest.mark.asyncio
async def test_list_regressions_flags_metric_regressions(monkeypatch: pytest.MonkeyPatch):
    suite_id = uuid4()
    baseline = TestResultSnapshot(
        script_id=uuid4(),
        status="passed",
        metrics={"intent_accuracy": 0.95},
    )
    current = TestResultSnapshot(
        script_id=baseline.script_id,
        status="passed",
        metrics={"intent_accuracy": 0.75},
    )
    candidate = regression_service.RegressionCandidate(snapshot=current, detected_at=None)

    async def fake_fetch_current(db, *, filters, pagination):
        assert filters == {"suite_id": suite_id}
        return {baseline.script_id: candidate}

    async def fake_fetch_baselines(db, script_ids):
        return {baseline.script_id: baseline}

    monkeypatch.setattr(regression_service, "_fetch_current_snapshots", fake_fetch_current)
    monkeypatch.setattr(regression_service, "_fetch_baselines", fake_fetch_baselines)

    result = await regression_service.list_regressions(
        db=SimpleNamespace(),
        filters={"suite_id": suite_id},
        pagination={"skip": 0, "limit": 10},
    )

    assert result["summary"]["metric_regressions"] == 1
    assert result["summary"]["status_regressions"] == 0
    assert result["summary"]["total_regressions"] == 1
    finding = result["items"][0]
    assert finding["category"] == "metric"
    assert finding["detail"]["metric"] == "intent_accuracy"


@pytest.mark.asyncio
async def test_list_regressions_filters_by_category(monkeypatch: pytest.MonkeyPatch):
    baseline = _snapshot("passed")
    current_status = TestResultSnapshot(script_id=baseline.script_id, status="failed", metrics={})
    status_candidate = regression_service.RegressionCandidate(snapshot=current_status, detected_at=None)

    async def fake_fetch_current(db, *, filters, pagination):
        return {baseline.script_id: status_candidate}

    async def fake_fetch_baselines(db, script_ids):
        return {baseline.script_id: baseline}

    monkeypatch.setattr(regression_service, "_fetch_current_snapshots", fake_fetch_current)
    monkeypatch.setattr(regression_service, "_fetch_baselines", fake_fetch_baselines)

    result = await regression_service.list_regressions(
        db=SimpleNamespace(),
        filters={"status": "metric"},
        pagination={"skip": 0, "limit": 5},
    )

    assert result["items"] == []
