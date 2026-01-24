"""
Custom report builder service (TASK-316).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from services.pdf_report_service import PDFReportMetadata, PDFReportService


class UnsupportedMetricError(ValueError):
    """Raised when a user selects an unsupported metric for a custom report."""


class UnsupportedFormatError(ValueError):
    """Raised when a requested output format is not supported."""


class InvalidDateRangeError(ValueError):
    """Raised when the supplied start/end dates are not valid."""


MetricsProvider = Callable[[Sequence[str], date, date], Dict[str, float]]


@dataclass(slots=True)
class CustomReportRequest:
    metrics: Sequence[str]
    start_date: date
    end_date: date
    format: str
    title: Optional[str] = None
    description: Optional[str] = None


@dataclass(slots=True)
class CustomReportResult:
    content: Optional[bytes]
    data: Optional[Dict[str, object]]
    content_type: str
    filename: str


class CustomReportBuilderService:
    """
    Builds ad-hoc reports using the selected metrics, time range, and format.
    """

    def __init__(
        self,
        *,
        metrics_provider: MetricsProvider,
        pdf_renderer: PDFReportService,
        allowed_metrics: Optional[Dict[str, str]] = None,
        supported_formats: Optional[Iterable[str]] = None,
    ) -> None:
        self._metrics_provider = metrics_provider
        self._pdf_renderer = pdf_renderer
        self._allowed_metrics = allowed_metrics or {
            "pass_rate": "Pass Rate",
            "defects": "Defects Found",
            "duration_ms": "Mean Duration (ms)",
        }
        self._supported_formats = set(supported_formats or {"pdf", "json"})

    def create_report(self, request: CustomReportRequest) -> CustomReportResult:
        self._validate_request(request)

        metrics = self._metrics_provider(
            metrics=list(request.metrics),
            start_date=request.start_date,
            end_date=request.end_date,
        )

        if request.format == "pdf":
            return self._build_pdf_report(request, metrics)
        if request.format == "json":
            return self._build_json_report(request, metrics)

        raise UnsupportedFormatError(f"Unsupported report format '{request.format}'")

    def _validate_request(self, request: CustomReportRequest) -> None:
        if not request.metrics:
            raise UnsupportedMetricError("At least one metric must be selected.")

        invalid_metrics = [metric for metric in request.metrics if metric not in self._allowed_metrics]
        if invalid_metrics:
            raise UnsupportedMetricError(
                f"Unsupported metrics selected: {', '.join(invalid_metrics)}"
            )

        if request.format not in self._supported_formats:
            raise UnsupportedFormatError(f"Unsupported report format '{request.format}'")

        if request.end_date < request.start_date:
            raise InvalidDateRangeError("end_date must be on or after start_date")

    def _build_pdf_report(
        self,
        request: CustomReportRequest,
        metrics: Dict[str, float],
    ) -> CustomReportResult:
        summary_text = self._build_summary_text(request=request, metrics=metrics)
        report_payload = {
            "period": {
                "start": request.start_date,
                "end": request.end_date,
            },
            "summary": summary_text,
            "trends": {},
            "key_risks": [],
            "recommendations": [],
            "selected_metrics": {
                key: metrics.get(key) for key in request.metrics
            },
        }

        metadata = PDFReportMetadata(
            title=request.title or "Custom Quality Report",
            author="Automated Testing Platform",
            subject=request.description or "Custom automation metrics report",
            generated_on=datetime.now(timezone.utc),
        )

        pdf_bytes = self._pdf_renderer.render_report(report_payload, metadata=metadata)
        filename = self._build_filename(request, suffix=".pdf")

        return CustomReportResult(
            content=pdf_bytes,
            data=None,
            content_type="application/pdf",
            filename=filename,
        )

    def _build_json_report(
        self,
        request: CustomReportRequest,
        metrics: Dict[str, float],
    ) -> CustomReportResult:
        payload = {
            "metrics": {metric: metrics.get(metric) for metric in request.metrics},
            "period": {
                "start": request.start_date,
                "end": request.end_date,
            },
            "title": request.title or "Custom Quality Report",
            "description": request.description,
        }

        filename = self._build_filename(request, suffix=".json")
        return CustomReportResult(
            content=None,
            data=payload,
            content_type="application/json",
            filename=filename,
        )

    def _build_summary_text(
        self,
        *,
        request: CustomReportRequest,
        metrics: Dict[str, float],
    ) -> str:
        segments: List[str] = [
            f"Custom report covering {request.start_date.isoformat()} to {request.end_date.isoformat()}."
        ]

        for metric in request.metrics:
            label = self._allowed_metrics.get(metric, metric)
            value = metrics.get(metric)
            if value is None:
                segments.append(f"{label}: no data.")
            else:
                segments.append(f"{label}: {value}")
        return " ".join(segments)

    @staticmethod
    def _build_filename(request: CustomReportRequest, *, suffix: str) -> str:
        return (
            f"custom-report-{request.start_date.isoformat()}--"
            f"{request.end_date.isoformat()}{suffix}"
        )
