"""
Pydantic schemas for real-time metrics responses (TASK-222).
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RealTimeSuiteRun(BaseModel):
    id: UUID
    suite_id: Optional[UUID] = None
    suite_name: Optional[str] = None
    status: str
    progress_pct: float = Field(ge=0.0, le=100.0)
    total_tests: int = Field(ge=0)
    passed_tests: int = Field(ge=0)
    failed_tests: int = Field(ge=0)
    skipped_tests: int = Field(ge=0)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Backward compatibility alias
RealTimeTestRun = RealTimeSuiteRun


class QueueDepth(BaseModel):
    total: int = Field(ge=0)
    queued: int = Field(ge=0)
    processing: int = Field(ge=0)
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)
    average_priority: float = Field(ge=0.0)
    oldest_queued_seconds: Optional[float] = None


class ThroughputMetrics(BaseModel):
    tests_per_minute: float = Field(ge=0.0)
    sample_size: int = Field(ge=0)
    window_minutes: int = Field(ge=1)
    last_updated: datetime


class RunCounts(BaseModel):
    pending: int = Field(ge=0)
    running: int = Field(ge=0)
    completed: int = Field(ge=0)
    failed: int = Field(ge=0)
    cancelled: int = Field(ge=0)


class IssueSummary(BaseModel):
    open_defects: int = Field(ge=0)
    critical_defects: int = Field(ge=0)
    edge_cases_active: int = Field(ge=0)
    edge_cases_new: int = Field(ge=0)


class RealTimeMetricsResponse(BaseModel):
    current_runs: List[RealTimeSuiteRun]
    queue_depth: QueueDepth
    throughput: ThroughputMetrics
    run_counts: RunCounts
    issue_summary: IssueSummary
