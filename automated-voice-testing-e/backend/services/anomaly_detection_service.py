"""
Anomaly detection service for analytics (TASK-311).

Analyses trend data to surface significant deviations in pass rate,
response time, and defect backlog metrics.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List, Optional


@dataclass
class AnomalyAlert:
    """Represents a detected anomaly and supporting context."""

    metric: str
    severity: str
    message: str
    current_value: float | int
    baseline_value: Optional[float] = None
    change: Optional[float] = None
    change_pct: Optional[float] = None


class AnomalyDetectionService:
    """Detects anomalous behaviour across trend metrics."""

    def __init__(
        self,
        *,
        pass_rate_drop_threshold_pct: float = 10.0,
        response_time_increase_threshold_pct: float = 30.0,
        defect_backlog_threshold: int = 5,
    ) -> None:
        self.pass_rate_drop_threshold = pass_rate_drop_threshold_pct
        self.response_time_threshold = response_time_increase_threshold_pct
        self.defect_backlog_threshold = defect_backlog_threshold

    def detect_anomalies(
        self,
        *,
        pass_rate_trend: Iterable[dict],
        defect_trend: Iterable[dict],
        performance_trend: Iterable[dict],
    ) -> List[AnomalyAlert]:
        alerts: List[AnomalyAlert] = []
        alerts.extend(self._detect_pass_rate_drop(list(pass_rate_trend)))
        alerts.extend(self._detect_response_time_spike(list(performance_trend)))
        alerts.extend(self._detect_defect_backlog_spike(list(defect_trend)))
        alerts.sort(key=self._severity_sort_key)
        return alerts

    def _detect_pass_rate_drop(self, trend: List[dict]) -> List[AnomalyAlert]:
        if len(trend) < 2:
            return []

        latest = trend[-1]
        current = self._coerce_float(latest.get("pass_rate_pct"))
        if current is None:
            return []

        baseline_values = [
            value
            for entry in trend[:-1]
            if (value := self._coerce_float(entry.get("pass_rate_pct"))) is not None
        ]
        if not baseline_values:
            return []
        baseline = mean(baseline_values)
        drop = baseline - current
        if drop <= 0:
            return []

        severity = self._severity_from_delta(drop, self.pass_rate_drop_threshold)
        if severity is None:
            return []

        message = (
            f"Pass rate dropped by {drop:.1f} percentage points "
            f"(baseline {baseline:.1f}%, current {current:.1f}%)."
        )

        return [
            AnomalyAlert(
                metric="pass_rate",
                severity=severity,
                message=message,
                current_value=current,
                baseline_value=baseline,
                change=drop,
                change_pct=(drop / baseline) * 100 if baseline else None,
            )
        ]

    def _detect_response_time_spike(self, trend: List[dict]) -> List[AnomalyAlert]:
        if len(trend) < 2:
            return []

        latest = trend[-1]
        current = self._coerce_float(latest.get("avg_response_time_ms"))
        if current is None:
            return []
        previous_entry = trend[-2]
        baseline = self._coerce_float(previous_entry.get("avg_response_time_ms"))
        if baseline is None or baseline <= 0:
            return []

        increase_pct = ((current - baseline) / baseline) * 100
        if increase_pct <= 0:
            return []

        severity = self._severity_from_delta(increase_pct, self.response_time_threshold)
        if severity is None:
            return []

        message = (
            f"Response time increased by {increase_pct:.1f}% "
            f"(previous {baseline:.1f} ms, current {current:.1f} ms)."
        )

        return [
            AnomalyAlert(
                metric="response_time",
                severity=severity,
                message=message,
                current_value=current,
                baseline_value=baseline,
                change=current - baseline,
                change_pct=increase_pct,
            )
        ]

    def _detect_defect_backlog_spike(self, trend: List[dict]) -> List[AnomalyAlert]:
        if len(trend) < 2:
            return []

        latest = trend[-1]
        previous = trend[-2]
        current = self._coerce_int(latest.get("net_open"))
        baseline = self._coerce_int(previous.get("net_open"))
        if current is None or baseline is None:
            return []
        change = current - baseline
        if change <= 0:
            return []

        severity = self._severity_from_delta(change, self.defect_backlog_threshold)
        if severity is None:
            return []

        message = (
            f"Defect backlog increased by {change} "
            f"(baseline {baseline}, current {current})."
        )

        return [
            AnomalyAlert(
                metric="defect_backlog",
                severity=severity,
                message=message,
                current_value=current,
                baseline_value=float(baseline),
                change=float(change),
                change_pct=((change / baseline) * 100) if baseline else None,
            )
        ]

    @staticmethod
    def _severity_from_delta(delta: float, threshold: float) -> Optional[str]:
        if delta >= threshold * 2.0:
            return "critical"
        if delta >= threshold * 1.5:
            return "high"
        if delta >= threshold:
            return "moderate"
        return None

    @staticmethod
    def _severity_sort_key(alert: AnomalyAlert) -> tuple[int, str]:
        order = {"critical": 0, "high": 1, "moderate": 2}
        return (order.get(alert.severity, 3), alert.metric)

    @staticmethod
    def _coerce_float(value: object) -> Optional[float]:
        try:
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _coerce_int(value: object) -> Optional[int]:
        try:
            if value is None:
                return None
            return int(value)
        except (TypeError, ValueError):
            return None
