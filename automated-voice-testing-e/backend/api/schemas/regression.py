"""
Regression-related API schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaselineApprovalRequest(BaseModel):
    """Payload required to approve a regression baseline."""

    status: str = Field(
        ...,
        description="Outcome status captured for the approved baseline.",
        examples=["passed", "failed"],
    )
    metrics: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional metric snapshot to associate with the baseline.",
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional reviewer note stored alongside the baseline approval.",
    )


class RegressionSummary(BaseModel):
    """Summary statistics for regression findings."""

    total_regressions: int = Field(0, description="Total number of regressions found")
    status_regressions: int = Field(0, description="Count of status-based regressions")
    metric_regressions: int = Field(0, description="Count of metric-based regressions")


class RegressionFindingItem(BaseModel):
    """A single regression finding."""

    script_id: str = Field(..., description="Scenario script UUID")
    category: str = Field(..., description="Regression category (status or metric)")
    detail: Dict[str, Any] = Field(default_factory=dict, description="Detailed regression info")
    regression_detected_at: Optional[str] = Field(
        None, description="ISO timestamp when regression was detected"
    )


class RegressionsListResponse(BaseModel):
    """Schema for regression list API response."""

    summary: RegressionSummary = Field(..., description="Regression summary statistics")
    items: List[RegressionFindingItem] = Field(
        default_factory=list, description="List of detected regressions"
    )


class BaselineApprovalResponse(BaseModel):
    """Schema for baseline approval API response."""

    script_id: str = Field(..., description="Scenario script UUID")
    status: str = Field(..., description="Baseline status")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Baseline metrics")
    version: int = Field(..., description="Baseline version number")
    approved_at: Optional[str] = Field(None, description="ISO timestamp of approval")
    approved_by: Optional[str] = Field(None, description="User ID who approved")
    note: Optional[str] = Field(None, description="Approval note")


class RegressionMetricValue(BaseModel):
    """Metric value with optional threshold and unit."""

    value: Optional[float] = Field(None, description="Metric value")
    threshold: Optional[float] = Field(None, description="Threshold for regression detection")
    unit: Optional[str] = Field(None, description="Unit of measurement")


class RegressionSnapshot(BaseModel):
    """Snapshot of a test result for comparison."""

    status: str = Field(..., description="Test status")
    metrics: Dict[str, RegressionMetricValue] = Field(
        default_factory=dict, description="Captured metrics"
    )
    media_uri: Optional[str] = Field(None, description="Optional media URI")


class RegressionDifference(BaseModel):
    """Difference between baseline and current metric values."""

    metric: str = Field(..., description="Metric name")
    baseline_value: Optional[float] = Field(None, description="Baseline metric value")
    current_value: Optional[float] = Field(None, description="Current metric value")
    delta: Optional[float] = Field(None, description="Absolute difference")
    delta_pct: Optional[float] = Field(None, description="Percentage difference")


class RegressionComparisonResponse(BaseModel):
    """Schema for regression comparison API response."""

    script_id: str = Field(..., description="Scenario script UUID")
    baseline: RegressionSnapshot = Field(..., description="Baseline snapshot data")
    current: RegressionSnapshot = Field(..., description="Current execution data")
    differences: List[RegressionDifference] = Field(
        default_factory=list, description="List of metric differences"
    )


class BaselineHistoryEntry(BaseModel):
    """A historical baseline version."""

    version: int = Field(..., description="Version number")
    status: str = Field(..., description="Status at this version")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Metrics at this version")
    approved_at: Optional[str] = Field(None, description="ISO timestamp of approval")
    approved_by: Optional[str] = Field(None, description="User ID who approved")
    note: Optional[str] = Field(None, description="Note for this version")


class ValidationSummary(BaseModel):
    """Summary of validation results across all steps."""

    total_steps: int = Field(0, description="Total number of steps")
    passed_steps: int = Field(0, description="Number of steps that passed validation")
    failed_steps: int = Field(0, description="Number of steps that failed validation")
    all_passed: bool = Field(False, description="Whether all steps passed")


class StepDetail(BaseModel):
    """Detail of a single step execution for review."""

    step_order: int = Field(..., description="Order of the step in the scenario")
    validation_passed: Optional[bool] = Field(None, description="Whether validation passed")
    user_utterance: Optional[str] = Field(None, description="User's utterance/transcription")
    ai_response: Optional[str] = Field(None, description="AI's response (truncated)")
    validation_details: Optional[Dict[str, Any]] = Field(None, description="Detailed validation results")
    confidence_score: Optional[float] = Field(None, description="Recognition confidence score")


class PendingBaselineSnapshot(BaseModel):
    """A pending baseline from the latest execution, awaiting approval."""

    status: Optional[str] = Field(None, description="Execution status")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Validation metrics (averages)")
    detected_at: Optional[str] = Field(None, description="ISO timestamp when detected")
    proposed_by: Optional[str] = Field(None, description="User ID who proposed (if available)")
    execution_id: Optional[str] = Field(None, description="ID of the source execution")
    validation_summary: Optional[ValidationSummary] = Field(None, description="Summary of validation results")
    step_details: Optional[List[StepDetail]] = Field(None, description="Details of each step for review")


class BaselineHistoryResponse(BaseModel):
    """Schema for baseline history API response."""

    script_id: str = Field(..., description="Scenario script UUID")
    history: List[BaselineHistoryEntry] = Field(
        default_factory=list, description="History of baseline versions (newest first)"
    )
    pending: Optional[PendingBaselineSnapshot] = Field(
        None, description="Pending baseline from latest execution (if newer than last approval)"
    )


# ============================================================================
# Persistent Regression Tracking Schemas
# ============================================================================


class RegressionRecordResponse(BaseModel):
    """Schema for a persistent regression record."""

    id: str = Field(..., description="Regression UUID")
    tenant_id: Optional[str] = Field(None, description="Tenant UUID")
    script_id: str = Field(..., description="Scenario script UUID")
    script_name: Optional[str] = Field(None, description="Scenario script name")
    category: str = Field(..., description="Regression category: status, metric, llm")
    severity: str = Field(..., description="Severity: low, medium, high, critical")
    status: str = Field(..., description="Status: active, resolved, ignored, investigating")
    baseline_version: Optional[int] = Field(None, description="Baseline version number")
    detection_date: str = Field(..., description="ISO timestamp when first detected")
    resolution_date: Optional[str] = Field(None, description="ISO timestamp when resolved")
    last_seen_date: str = Field(..., description="ISO timestamp of most recent occurrence")
    occurrence_count: int = Field(..., description="Number of times detected")
    details: Dict[str, Any] = Field(default_factory=dict, description="Regression details")
    linked_defect_id: Optional[str] = Field(None, description="Linked defect UUID")
    resolved_by: Optional[str] = Field(None, description="User UUID who resolved")
    resolution_note: Optional[str] = Field(None, description="Resolution explanation")
    created_at: str = Field(..., description="ISO timestamp of record creation")
    updated_at: str = Field(..., description="ISO timestamp of last update")


class RegressionListResponse(BaseModel):
    """Schema for list of persistent regression records."""

    total: int = Field(..., description="Total number of regressions")
    active: int = Field(..., description="Number of active regressions")
    resolved: int = Field(..., description="Number of resolved regressions")
    items: List[RegressionRecordResponse] = Field(
        default_factory=list, description="List of regression records"
    )


class RegressionResolveRequest(BaseModel):
    """Schema for resolving a regression."""

    note: Optional[str] = Field(None, description="Note explaining resolution")


class RegressionCreateDefectRequest(BaseModel):
    """Schema for creating a defect from a regression."""

    severity: Optional[str] = Field("high", description="Defect severity override")
    additional_notes: Optional[str] = Field(None, description="Additional context for defect")


class RegressionCreateDefectResponse(BaseModel):
    """Schema for defect created from regression."""

    defect_id: str = Field(..., description="Created defect UUID")
    regression_id: str = Field(..., description="Source regression UUID")
    message: str = Field(..., description="Success message")
