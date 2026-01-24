"""
Executive report generation tests (TASK-313).
"""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List

import pytest

from services.report_generator_service import ReportGeneratorService


class StubDataSources:
    def __init__(self) -> None:
        self.execution_summary = {
            "total_executions": 320,
            "pass_rate": 0.92,
            "defects_found": 14,
            "mean_response_time_ms": 850,
        }
        self.trend_snapshot = {
            "pass_rate": [
                {"period_start": "2024-01-01", "value": 0.95},
                {"period_start": "2024-01-07", "value": 0.92},
            ],
            "defects": [
                {"period_start": "2024-01-01", "open": 8},
                {"period_start": "2024-01-07", "open": 12},
            ],
        }
        self.risk_findings = [
            {
                "name": "Checkout flow",
                "probability": 0.78,
                "risk_level": "high",
            }
        ]

    def get_execution_summary(self, start: date, end: date) -> Dict[str, Any]:
        self.last_summary_range = (start, end)
        return self.execution_summary

    def get_trend_snapshot(self, start: date, end: date) -> Dict[str, Any]:
        self.last_trend_range = (start, end)
        return self.trend_snapshot

    def get_top_risks(self, limit: int) -> List[Dict[str, Any]]:
        self.last_risk_limit = limit
        return self.risk_findings[:limit]


@pytest.fixture()
def data_sources() -> StubDataSources:
    return StubDataSources()


@pytest.fixture()
def report_service(data_sources: StubDataSources) -> ReportGeneratorService:
    return ReportGeneratorService(
        execution_summary_provider=data_sources.get_execution_summary,
        trend_provider=data_sources.get_trend_snapshot,
        risk_provider=data_sources.get_top_risks,
    )


def test_weekly_report_includes_summary_and_sections(
    report_service: ReportGeneratorService,
    data_sources: StubDataSources,
) -> None:
    report = report_service.generate_weekly_report(
        reference_date=date(2024, 1, 8)
    )

    assert data_sources.last_summary_range == (
        date(2024, 1, 1),
        date(2024, 1, 7),
    )
    assert "summary" in report
    assert "Total executions: 320" in report["summary"]
    assert "Pass rate: 92.0%" in report["summary"]

    trends = report["trends"]
    assert trends["pass_rate"]["current"] == pytest.approx(0.92, rel=1e-6)
    assert trends["pass_rate"]["delta"] == pytest.approx(-0.03, rel=1e-6)
    assert "key_risks" in report
    assert report["key_risks"][0]["name"] == "Checkout flow"
    assert any("Checkout flow" in rec for rec in report["recommendations"])
    assert any("pass rate" in rec.lower() for rec in report["recommendations"])


def test_monthly_report_covers_full_period_and_limits_risks(
    data_sources: StubDataSources,
) -> None:
    service = ReportGeneratorService(
        execution_summary_provider=data_sources.get_execution_summary,
        trend_provider=data_sources.get_trend_snapshot,
        risk_provider=data_sources.get_top_risks,
        risk_limit=1,
    )

    report = service.generate_monthly_report(reference_date=date(2024, 2, 1))

    assert data_sources.last_summary_range == (
        date(2024, 1, 2),
        date(2024, 1, 31),
    )
    assert data_sources.last_risk_limit == 1
    assert report["period"]["start"] == date(2024, 1, 2)
    assert report["period"]["end"] == date(2024, 1, 31)
    assert len(report["key_risks"]) == 1
    assert report["recommendations"], "Monthly report should include recommendations"
