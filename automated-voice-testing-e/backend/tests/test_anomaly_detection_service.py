"""
Anomaly detection service tests.

Validates detection of significant metric deviations for alerting.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from services.anomaly_detection_service import AnomalyDetectionService


def _build_pass_rate_trend(values: list[float]) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "period_start": (base + timedelta(days=index)).isoformat(),
            "pass_rate_pct": value,
            "change_pct": None if index == 0 else value - values[index - 1],
            "direction": "down" if index and value < values[index - 1] else "flat",
            "total_executions": 100,
        }
        for index, value in enumerate(values)
    ]


def _build_performance_trend(values: list[float]) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "period_start": (base + timedelta(days=index)).isoformat(),
            "avg_response_time_ms": value,
            "change_ms": None if index == 0 else value - values[index - 1],
            "direction": "up" if index and value > values[index - 1] else "flat",
            "sample_size": 100,
        }
        for index, value in enumerate(values)
    ]


def _build_defect_trend(values: list[int]) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "period_start": (base + timedelta(days=index)).isoformat(),
            "detected": 3,
            "resolved": 2,
            "net_open": value,
            "change_open": None if index == 0 else value - values[index - 1],
            "direction": "up" if index and value > values[index - 1] else "flat",
        }
        for index, value in enumerate(values)
    ]


@pytest.fixture()
def detection_service() -> AnomalyDetectionService:
    return AnomalyDetectionService(
        pass_rate_drop_threshold_pct=8.0,
        response_time_increase_threshold_pct=30.0,
        defect_backlog_threshold=5,
    )


def test_detects_significant_pass_rate_drop(detection_service: AnomalyDetectionService):
    pass_rates = _build_pass_rate_trend([98.0, 97.5, 96.8, 83.0])

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=pass_rates,
        defect_trend=[],
        performance_trend=[],
    )

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.metric == "pass_rate"
    assert alert.severity == "high"
    assert alert.change == pytest.approx(14.433, rel=1e-3)
    assert alert.current_value == pytest.approx(83.0)
    assert alert.baseline_value == pytest.approx(97.433, rel=1e-3)


def test_detects_response_time_spike(detection_service: AnomalyDetectionService):
    trend = _build_performance_trend([950.0, 980.0, 1010.0, 1350.0])

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=[],
        defect_trend=[],
        performance_trend=trend,
    )

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.metric == "response_time"
    assert alert.severity == "moderate"
    assert alert.change_pct == pytest.approx(33.663, rel=1e-3)
    assert alert.current_value == pytest.approx(1350.0)


def test_detects_defect_backlog_surge(detection_service: AnomalyDetectionService):
    defects = _build_defect_trend([4, 5, 7, 15])

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=[],
        defect_trend=defects,
        performance_trend=[],
    )

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.metric == "defect_backlog"
    assert alert.severity == "high"
    assert alert.current_value == 15
    assert alert.change == 8


def test_returns_no_alerts_when_within_thresholds(detection_service: AnomalyDetectionService):
    pass_rates = _build_pass_rate_trend([97.0, 96.5, 95.9, 92.5])  # drop < threshold
    performance = _build_performance_trend([1000.0, 1100.0, 1150.0])  # +15%
    defects = _build_defect_trend([4, 6, 8])  # +2 per day

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=pass_rates,
        defect_trend=defects,
        performance_trend=performance,
    )

    assert alerts == []


def test_pass_rate_detection_ignores_missing_values(detection_service: AnomalyDetectionService):
    pass_rates = _build_pass_rate_trend([98.0, 96.5, 94.0, 72.0])
    pass_rates[1]["pass_rate_pct"] = None

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=pass_rates,
        defect_trend=[],
        performance_trend=[],
    )

    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.metric == "pass_rate"
    assert alert.severity == "critical"
    assert alert.change == pytest.approx(24.0, rel=1e-3)
    assert alert.baseline_value == pytest.approx(96.0, rel=1e-3)


def test_anomalies_sorted_by_severity(detection_service: AnomalyDetectionService):
    pass_rates = _build_pass_rate_trend([97.0, 95.5, 92.0, 83.0])  # moderate drop
    performance = _build_performance_trend([900.0, 930.0, 950.0, 1650.0])  # critical spike
    defects = _build_defect_trend([3, 4, 7, 16])  # high increase

    alerts = detection_service.detect_anomalies(
        pass_rate_trend=pass_rates,
        defect_trend=defects,
        performance_trend=performance,
    )

    severities = [alert.severity for alert in alerts]
    assert severities == ["critical", "high", "moderate"]
