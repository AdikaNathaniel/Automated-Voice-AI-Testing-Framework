"""
Tests for regression detection service (TASK-336, subtask 1).

These initial tests cover status-based regressions and summary aggregation. The
implementation should flag cases where a test previously passed but now fails,
while ignoring neutral or improving outcomes.
"""

from __future__ import annotations

from uuid import uuid4

import pytest

from services.regression_detection_service import (
    MetricRule,
    RegressionDetectionService,
    RegressionSummary,
    TestResultSnapshot,
)


def make_snapshot(*, status: str, metrics: dict | None = None):
    return TestResultSnapshot(
        script_id=uuid4(),
        status=status,
        metrics=metrics or {},
    )


def test_status_regressions_are_flagged():
    script_id = uuid4()
    baseline = [
        TestResultSnapshot(script_id=script_id, status="passed", metrics={"pass_rate": 1.0})
    ]
    current = [
        TestResultSnapshot(script_id=script_id, status="failed", metrics={"pass_rate": 0.0})
    ]

    service = RegressionDetectionService()
    report = service.detect(current_results=current, baseline_results=baseline)

    assert report.summary == RegressionSummary(
        total_regressions=1,
        status_regressions=1,
        metric_regressions=0,
    )
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert finding.script_id == script_id
    assert finding.category == "status"
    assert finding.detail["baseline_status"] == "passed"
    assert finding.detail["current_status"] == "failed"


def test_improvements_do_not_count_as_regressions():
    baseline = [
        make_snapshot(status="failed"),
        make_snapshot(status="skipped"),
    ]
    current = [
        TestResultSnapshot(script_id=baseline[0].script_id, status="passed", metrics={}),
        TestResultSnapshot(script_id=baseline[1].script_id, status="passed", metrics={}),
    ]

    service = RegressionDetectionService()
    report = service.detect(current_results=current, baseline_results=baseline)

    assert report.summary.total_regressions == 0
    assert report.findings == []


def test_metric_regression_detects_drop_for_higher_is_better_metric():
    script_id = uuid4()
    baseline = [
        TestResultSnapshot(
            script_id=script_id,
            status="passed",
            metrics={"pass_rate": 0.95},
        )
    ]
    current = [
        TestResultSnapshot(
            script_id=script_id,
            status="passed",
            metrics={"pass_rate": 0.85},
        )
    ]

    service = RegressionDetectionService(
        metric_rules={
            "pass_rate": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
        }
    )
    report = service.detect(current_results=current, baseline_results=baseline)

    assert report.summary.metric_regressions == 1
    assert report.summary.total_regressions == 1
    finding = report.findings[0]
    assert finding.category == "metric"
    assert finding.detail["metric"] == "pass_rate"
    assert finding.detail["baseline_value"] == 0.95
    assert finding.detail["current_value"] == 0.85
    assert finding.detail["change"] == pytest.approx(-0.10, rel=1e-3)
    assert finding.detail["change_pct"] == pytest.approx(-10.526, rel=1e-3)


def test_metric_regression_detects_increase_for_lower_is_better_metric():
    script_id = uuid4()
    baseline = [
        TestResultSnapshot(
            script_id=script_id,
            status="passed",
            metrics={"response_time_ms": 120.0},
        )
    ]
    current = [
        TestResultSnapshot(
            script_id=script_id,
            status="passed",
            metrics={"response_time_ms": 156.0},
        )
    ]

    service = RegressionDetectionService(
        metric_rules={
            "response_time_ms": MetricRule(
                direction="lower_is_better",
                relative_tolerance=0.2,
            ),
        }
    )
    report = service.detect(current_results=current, baseline_results=baseline)

    assert report.summary.metric_regressions == 1
    assert report.findings[0].detail["metric"] == "response_time_ms"
    assert report.findings[0].detail["change"] == pytest.approx(36.0)
    assert report.findings[0].detail["change_pct"] == pytest.approx(30.0)
