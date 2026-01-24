"""
Regression detection service (TASK-336).

This initial implementation focuses on identifying status regressions where a
scenario script previously passed in the baseline but now fails or is otherwise
not successful. Metric-based analysis will be layered on in subsequent steps.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence, List
from uuid import UUID


@dataclass(frozen=True)
class TestResultSnapshot:
    """
    Lightweight representation of a scenario script execution outcome.

    Attributes:
        script_id: Identifier of the scenario script.
        status: Outcome status (passed, failed, skipped, etc.).
        metrics: Optional numerical metrics recorded for the execution.
    """

    script_id: UUID
    status: str
    metrics: Mapping[str, Any] = field(default_factory=dict)
    __test__ = False  # Prevent pytest from collecting as a test case


@dataclass(frozen=True)
class MetricRule:
    """
    Configuration describing how to evaluate a metric for regressions.

    Attributes:
        direction: Whether higher values are better or lower values are better.
        absolute_tolerance: Minimum absolute change required to flag a regression.
        relative_tolerance: Minimum percentual change (0.05 => 5%) required.
    """

    direction: str  # "higher_is_better" or "lower_is_better"
    absolute_tolerance: Optional[float] = None
    relative_tolerance: Optional[float] = None


@dataclass(frozen=True)
class RegressionFinding:
    """Represents an individual regression that was detected."""

    script_id: UUID
    category: str  # e.g., "status", "metric"
    detail: Dict[str, Any]


@dataclass(frozen=True)
class RegressionSummary:
    """Aggregate counts for regression categories."""

    total_regressions: int
    status_regressions: int
    metric_regressions: int


@dataclass(frozen=True)
class RegressionDetectionReport:
    """Complete report for a regression detection pass."""

    findings: List[RegressionFinding]
    summary: RegressionSummary


class RegressionDetectionService:
    """Compares current test results against a baseline to flag regressions."""

    _SUCCESS_STATUSES = frozenset({"passed", "success"})

    def __init__(self, *, metric_rules: Optional[Mapping[str, MetricRule]] = None) -> None:
        self._metric_rules: Dict[str, MetricRule] = dict(metric_rules or {})

    def detect(
        self,
        *,
        current_results: Sequence[TestResultSnapshot],
        baseline_results: Sequence[TestResultSnapshot],
    ) -> RegressionDetectionReport:
        baseline_index: MutableMapping[UUID, TestResultSnapshot] = {
            snapshot.script_id: snapshot
            for snapshot in baseline_results
        }

        findings: List[RegressionFinding] = []
        status_regressions = 0
        metric_regressions = 0

        for current in current_results:
            baseline = baseline_index.get(current.script_id)
            if baseline is None:
                continue

            if self._is_status_regression(baseline.status, current.status):
                status_regressions += 1
                findings.append(
                    RegressionFinding(
                        script_id=current.script_id,
                        category="status",
                        detail={
                            "baseline_status": baseline.status,
                            "current_status": current.status,
                        },
                    )
                )

            metric_findings = self._detect_metric_regressions(baseline, current)
            metric_regressions += len(metric_findings)
            findings.extend(metric_findings)

        total = status_regressions + metric_regressions
        summary = RegressionSummary(
            total_regressions=total,
            status_regressions=status_regressions,
            metric_regressions=metric_regressions,
        )
        return RegressionDetectionReport(findings=findings, summary=summary)

    def _is_status_regression(self, baseline_status: str | None, current_status: str | None) -> bool:
        baseline_normalized = (baseline_status or "").strip().lower()
        current_normalized = (current_status or "").strip().lower()
        return (
            baseline_normalized in self._SUCCESS_STATUSES
            and current_normalized not in self._SUCCESS_STATUSES
        )

    def _detect_metric_regressions(
        self,
        baseline: TestResultSnapshot,
        current: TestResultSnapshot,
    ) -> List[RegressionFinding]:
        findings: List[RegressionFinding] = []

        if not self._metric_rules:
            return findings

        for metric_name, rule in self._metric_rules.items():
            baseline_value = self._coerce_float(baseline.metrics.get(metric_name))
            current_value = self._coerce_float(current.metrics.get(metric_name))
            if baseline_value is None or current_value is None:
                continue

            regression = self._is_metric_regression(
                metric_name=metric_name,
                baseline_value=baseline_value,
                current_value=current_value,
                rule=rule,
            )
            if not regression:
                continue

            change = current_value - baseline_value
            change_pct = None
            if baseline_value not in (0.0, 0):
                change_pct = (change / baseline_value) * 100

            findings.append(
                RegressionFinding(
                    script_id=current.script_id,
                    category="metric",
                    detail={
                        "metric": metric_name,
                        "baseline_value": baseline_value,
                        "current_value": current_value,
                        "change": change,
                        "change_pct": change_pct,
                    },
                )
            )

        return findings

    @staticmethod
    def _coerce_float(value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    def _is_metric_regression(
        self,
        *,
        metric_name: str,
        baseline_value: float,
        current_value: float,
        rule: MetricRule,
    ) -> bool:
        direction = rule.direction.lower()
        if direction not in {"higher_is_better", "lower_is_better"}:
            raise ValueError(f"Unsupported direction '{rule.direction}' for metric '{metric_name}'")

        if direction == "higher_is_better":
            drop = baseline_value - current_value
            if drop <= 0:
                return False
            return self._exceeds_threshold(drop, baseline_value, rule)

        # lower_is_better
        increase = current_value - baseline_value
        if increase <= 0:
            return False
        return self._exceeds_threshold(increase, baseline_value, rule)

    def _exceeds_threshold(
        self,
        change: float,
        baseline_value: float,
        rule: MetricRule,
    ) -> bool:
        if rule.absolute_tolerance is not None and change > rule.absolute_tolerance:
            return True

        if (
            rule.relative_tolerance is not None
            and baseline_value not in (0.0, 0)
            and (change / baseline_value) > rule.relative_tolerance
        ):
            return True

        if rule.absolute_tolerance is None and rule.relative_tolerance is None:
            return change > 0

        return False
