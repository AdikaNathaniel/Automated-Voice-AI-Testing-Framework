"""
Executive report generator service (TASK-313).
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Callable, Dict, Iterable, List, Optional, Tuple


SummaryProvider = Callable[[date, date], Dict[str, float]]
TrendProvider = Callable[[date, date], Dict[str, Iterable[Dict[str, float]]]]
RiskProvider = Callable[[int], List[Dict[str, float]]]


class ReportGeneratorService:
    """
    Builds executive reports combining metrics, trend, and risk insights.
    """

    def __init__(
        self,
        *,
        execution_summary_provider: SummaryProvider,
        trend_provider: TrendProvider,
        risk_provider: RiskProvider,
        risk_limit: int = 5,
    ) -> None:
        self._execution_summary_provider = execution_summary_provider
        self._trend_provider = trend_provider
        self._risk_provider = risk_provider
        self._risk_limit = risk_limit

    def generate_weekly_report(self, reference_date: date) -> Dict[str, object]:
        """
        Produce a weekly report covering the seven days ending before reference_date.
        """
        return self._assemble_report(label="Week", reference_date=reference_date, days=7)

    def generate_monthly_report(self, reference_date: date) -> Dict[str, object]:
        """
        Produce a monthly report covering the previous 30 days.
        """
        return self._assemble_report(label="Month", reference_date=reference_date, days=30)

    def _assemble_report(
        self,
        *,
        label: str,
        reference_date: date,
        days: int,
    ) -> Dict[str, object]:
        start, end = self._period_range(reference_date, days=days)
        summary = self._execution_summary_provider(start, end)
        raw_trends = self._trend_provider(start, end)
        trend_summary = self._build_trend_block(raw_trends)
        risks = self._risk_provider(self._risk_limit)
        recommendations = self._build_recommendations(summary, trend_summary, risks)

        return {
            "period": {"start": start, "end": end},
            "summary": self._build_summary_block(label, start, end, summary),
            "trends": trend_summary,
            "key_risks": risks,
            "recommendations": recommendations,
        }

    @staticmethod
    def _period_range(reference: date, *, days: int) -> Tuple[date, date]:
        end = reference - timedelta(days=1)
        start = end - timedelta(days=days - 1)
        return start, end

    @staticmethod
    def _build_summary_block(
        label: str,
        start: date,
        end: date,
        summary: Dict[str, float],
    ) -> str:
        pass_rate_pct = summary.get("pass_rate", 0.0) * 100.0
        return (
            f"{label} of {start.isoformat()} to {end.isoformat()} — "
            f"Total executions: {int(summary.get('total_executions', 0))}; "
            f"Pass rate: {pass_rate_pct:.1f}%; "
            f"Defects found: {int(summary.get('defects_found', 0))}; "
            f"Mean response time: {summary.get('mean_response_time_ms', 0):.0f} ms"
        )

    def _build_trend_block(self, trends: Dict[str, Iterable[Dict[str, float]]]) -> Dict[str, Dict[str, object]]:
        summary: Dict[str, Dict[str, float]] = {}
        for key, series in trends.items():
            series_list = list(series)
            if not series_list:
                continue
            current_entry = series_list[-1]
            previous_entry = series_list[-2] if len(series_list) > 1 else None
            value_key = self._resolve_value_key(current_entry)
            if value_key is None:
                continue

            current_value = float(current_entry[value_key])
            delta = None
            if previous_entry and value_key in previous_entry:
                delta = current_value - float(previous_entry[value_key])

            summary[key] = {
                "current": current_value,
                "delta": delta,
                "history": series_list,
            }
        return summary

    @staticmethod
    def _build_recommendations(
        summary: Dict[str, float],
        trends: Dict[str, Dict[str, object]],
        risks: List[Dict[str, float]],
    ) -> List[str]:
        recommendations: List[str] = []

        pass_rate = summary.get("pass_rate", 0.0)
        if pass_rate < 0.9:
            recommendations.append(
                f"Improve pass rate, currently at {pass_rate * 100:.1f}% by addressing failing scenarios."
            )

        defects_found = summary.get("defects_found", 0)
        if defects_found:
            recommendations.append(
                f"Review root causes for the {int(defects_found)} defects detected this period."
            )

        response_time = summary.get("mean_response_time_ms", 0)
        if response_time and response_time > 900:
            recommendations.append(
                f"Investigate performance regressions; mean response time reached {response_time:.0f} ms."
            )

        pass_rate_trend = trends.get("pass_rate")
        if pass_rate_trend and pass_rate_trend.get("delta") is not None and pass_rate_trend["delta"] < 0:
            recommendations.append(
                f"Reverse the declining pass rate trend (down {abs(pass_rate_trend['delta']):.2f})."
            )

        defects_trend = trends.get("defects")
        if defects_trend and defects_trend.get("delta") is not None and defects_trend["delta"] > 0:
            recommendations.append(
                f"Contain defect backlog growth; open issues increased by {defects_trend['delta']:.0f}."
            )

        for risk in risks:
            if risk.get("risk_level") == "high":
                probability = risk.get("probability")
                probability_pct = f"{probability * 100:.0f}%" if isinstance(probability, (float, int)) else "N/A"
                recommendations.append(
                    f"Prioritise mitigation for high-risk area '{risk.get('name')}' (likelihood {probability_pct})."
                )

        if not recommendations:
            recommendations.append("Continue current strategy; no critical issues detected this period.")

        return recommendations

    @staticmethod
    def _resolve_value_key(entry: Dict[str, float]) -> Optional[str]:
        for key, value in entry.items():
            if key == "period_start":
                continue
            if isinstance(value, (int, float)):
                return key
        return None
