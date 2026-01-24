"""
Custom report builder service tests (TASK-316).
"""

from __future__ import annotations

from datetime import date
from typing import Dict
from unittest.mock import MagicMock

import pytest

from services.custom_report_builder import (
    CustomReportBuilderService,
    CustomReportRequest,
    UnsupportedFormatError,
    UnsupportedMetricError,
)


def _build_service(pdf_bytes: bytes = b"%PDF", metrics: Dict[str, float] | None = None) -> tuple[CustomReportBuilderService, MagicMock, MagicMock]:
    metrics_provider = MagicMock(return_value=metrics or {"pass_rate": 0.93, "defects": 4})
    pdf_renderer = MagicMock()
    pdf_renderer.render_report.return_value = pdf_bytes

    service = CustomReportBuilderService(
        metrics_provider=metrics_provider,
        pdf_renderer=pdf_renderer,
        allowed_metrics={
            "pass_rate": "Pass Rate",
            "defects": "Defects Found",
            "duration_ms": "Mean Duration (ms)",
        },
    )
    return service, metrics_provider, pdf_renderer


def test_create_pdf_report_renders_document() -> None:
    service, metrics_provider, pdf_renderer = _build_service()

    request = CustomReportRequest(
        metrics=["pass_rate", "defects"],
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 7),
        format="pdf",
        title="Weekly Custom Snapshot",
    )

    result = service.create_report(request)

    metrics_provider.assert_called_once_with(
        metrics=["pass_rate", "defects"],
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 7),
    )

    pdf_renderer.render_report.assert_called_once()
    rendered_payload, kwargs = pdf_renderer.render_report.call_args
    assert "summary" in rendered_payload[0]
    assert kwargs["metadata"].title == "Weekly Custom Snapshot"

    assert result.content == b"%PDF"
    assert result.content_type == "application/pdf"
    assert result.filename.startswith("custom-report-2024-01-01--2024-01-07")


def test_create_json_report_returns_serialized_metrics() -> None:
    service, metrics_provider, _ = _build_service(metrics={"pass_rate": 0.91})

    request = CustomReportRequest(
        metrics=["pass_rate"],
        start_date=date(2024, 2, 1),
        end_date=date(2024, 2, 5),
        format="json",
    )

    result = service.create_report(request)

    metrics_provider.assert_called_once()
    assert result.content is None
    assert result.data is not None
    assert result.data["metrics"] == {"pass_rate": 0.91}
    assert result.data["period"] == {
        "start": date(2024, 2, 1),
        "end": date(2024, 2, 5),
    }
    assert result.data["title"] == "Custom Quality Report"
    assert result.content_type == "application/json"
    assert result.filename.endswith(".json")


def test_invalid_metric_raises() -> None:
    service, _, _ = _build_service()

    request = CustomReportRequest(
        metrics=["unknown_metric"],
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 7),
        format="json",
    )

    with pytest.raises(UnsupportedMetricError):
        service.create_report(request)


def test_invalid_format_raises() -> None:
    service, _, _ = _build_service()

    request = CustomReportRequest(
        metrics=["pass_rate"],
        start_date=date(2024, 3, 1),
        end_date=date(2024, 3, 7),
        format="xml",
    )

    with pytest.raises(UnsupportedFormatError):
        service.create_report(request)
