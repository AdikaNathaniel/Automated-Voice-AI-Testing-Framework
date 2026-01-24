"""
Custom report builder API endpoints (TASK-316).
"""

from __future__ import annotations

import base64
from datetime import date
from typing import Dict, Iterable, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from services.custom_report_builder import (
    CustomReportBuilderService,
    CustomReportRequest,
    CustomReportResult,
    InvalidDateRangeError,
    UnsupportedFormatError,
    UnsupportedMetricError,
)
from services.pdf_report_service import PDFReportService

router = APIRouter(prefix="/reports", tags=["Reports"])


class CustomReportPayload(BaseModel):
    metrics: Iterable[str] = Field(..., min_length=1, description="Metrics to include in the report.")
    start_date: date = Field(..., description="Start date for the reporting range (inclusive).")
    end_date: date = Field(..., description="End date for the reporting range (inclusive).")
    format: str = Field(..., description="Desired report format (pdf or json).")
    title: Optional[str] = Field(None, description="Optional report title.")
    description: Optional[str] = Field(None, description="Optional description or purpose of the report.")


class CustomReportResponse(BaseModel):
    filename: str
    content_type: str
    content: Optional[str] = None
    data: Optional[Dict[str, object]] = None


def get_custom_report_builder_service() -> Optional[CustomReportBuilderService]:
    """
    Provide a configured CustomReportBuilderService.

    Returns None when the system has not been configured for custom reporting.
    """
    metrics_provider = _build_metrics_provider()
    pdf_renderer = PDFReportService()

    return CustomReportBuilderService(
        metrics_provider=metrics_provider,
        pdf_renderer=pdf_renderer,
    )


def _build_metrics_provider():
    def _provider(metrics: Iterable[str], start_date: date, end_date: date) -> Dict[str, float]:
        """
        Placeholder metrics provider until analytics integration is completed.

        Returns zeros for requested metrics, enabling future wiring without
        blocking the API contract.
        """
        return {metric: 0.0 for metric in metrics}

    return _provider


@router.post(
    "/custom",
    response_model=CustomReportResponse,
    response_model_exclude_none=True,
)
def create_custom_report(
    payload: CustomReportPayload,
    builder: Optional[CustomReportBuilderService] = Depends(get_custom_report_builder_service),
) -> CustomReportResponse:
    if builder is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Custom report builder is not configured.",
        )

    request = CustomReportRequest(
        metrics=list(payload.metrics),
        start_date=payload.start_date,
        end_date=payload.end_date,
        format=payload.format.lower(),
        title=payload.title,
        description=payload.description,
    )

    try:
        result = builder.create_report(request)
    except (UnsupportedMetricError, UnsupportedFormatError, InvalidDateRangeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return _serialize_response(result)


def _serialize_response(result: CustomReportResult) -> CustomReportResponse:
    response_payload: Dict[str, object] = {
        "filename": result.filename,
        "content_type": result.content_type,
    }

    if result.content is not None:
        response_payload["content"] = base64.b64encode(result.content).decode("ascii")

    if result.data is not None:
        response_payload["data"] = result.data

    return CustomReportResponse(**response_payload)
