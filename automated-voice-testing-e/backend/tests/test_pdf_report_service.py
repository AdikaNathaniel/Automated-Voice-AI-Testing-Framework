"""
PDF report generation tests (TASK-314).
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict

import pytest

from services.pdf_report_service import PDFReportMetadata, PDFReportService


@pytest.fixture()
def weekly_report() -> Dict[str, Any]:
    return {
        "period": {"start": date(2024, 1, 1), "end": date(2024, 1, 7)},
        "summary": (
            "Week of 2024-01-01 to 2024-01-07 — Total executions: 320; "
            "Pass rate: 92.0%; Defects found: 14; Mean response time: 850 ms"
        ),
        "trends": {
            "pass_rate": {
                "current": 0.92,
                "delta": -0.03,
                "history": [
                    {"period_start": "2023-12-31", "value": 0.95},
                    {"period_start": "2024-01-07", "value": 0.92},
                ],
            },
            "defects": {
                "current": 12,
                "delta": 4,
                "history": [
                    {"period_start": "2023-12-31", "open": 8},
                    {"period_start": "2024-01-07", "open": 12},
                ],
            },
        },
        "key_risks": [
            {"name": "Checkout flow", "probability": 0.78, "risk_level": "high"},
            {"name": "Payment gateway", "probability": 0.42, "risk_level": "medium"},
        ],
        "recommendations": [
            "Improve pass rate, currently at 92.0% by addressing failing scenarios.",
            "Contain defect backlog growth; open issues increased by 4.",
        ],
    }


def test_generate_pdf_contains_summary_sections_and_risks(
    weekly_report: Dict[str, Any],
) -> None:
    service = PDFReportService()

    pdf_bytes = service.render_report(
        weekly_report,
        metadata=PDFReportMetadata(
            title="QA Weekly Health Report",
            author="Automation Platform",
            generated_on=datetime(2024, 1, 8, 9, 30),
        ),
    )

    assert pdf_bytes.startswith(b"%PDF"), "Rendered document must be a PDF file"
    assert len(pdf_bytes) > 500, "Rendered PDF should contain body content"
    assert b"Executive Summary" in pdf_bytes
    assert b"Week of 2024-01-01 to 2024-01-07" in pdf_bytes
    assert b"Checkout flow" in pdf_bytes
    assert b"Improve pass rate" in pdf_bytes


def test_pdf_metadata_is_embedded_in_document_info(
    weekly_report: Dict[str, Any],
) -> None:
    metadata = PDFReportMetadata(
        title="Automation Executive Report",
        author="QA Insights Team",
        subject="Weekly QA Performance",
        generated_on=datetime(2024, 1, 8, 17, 45),
    )
    service = PDFReportService()

    pdf_bytes = service.render_report(weekly_report, metadata=metadata)

    # ReportLab stores metadata in the info dictionary as /Title, /Author, etc.
    assert b"/Title (Automation Executive Report)" in pdf_bytes
    assert b"/Author (QA Insights Team)" in pdf_bytes
    assert b"/Subject (Weekly QA Performance)" in pdf_bytes
    assert b"Generated on: 2024-01-08 17:45" in pdf_bytes
