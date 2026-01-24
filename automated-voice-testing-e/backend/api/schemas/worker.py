"""
Pydantic schemas for worker health endpoints.
"""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from services.worker_health_service import WorkerAlert, WorkerHealthReport, WorkerStatus


class WorkerAlertSchema(BaseModel):
    level: str
    message: str

    @classmethod
    def from_domain(cls, alert: WorkerAlert) -> "WorkerAlertSchema":
        return cls(level=alert.level, message=alert.message)


class WorkerStatusSchema(BaseModel):
    name: str
    status: str
    active_tasks: int
    max_concurrency: int
    queues: List[str] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, status: WorkerStatus) -> "WorkerStatusSchema":
        return cls(
            name=status.name,
            status=status.status,
            active_tasks=status.active_tasks,
            max_concurrency=status.max_concurrency,
            queues=list(status.queues),
        )


class WorkerTotalsSchema(BaseModel):
    workers: int
    online: int
    offline: int


class WorkerHealthResponse(BaseModel):
    status: str
    totals: WorkerTotalsSchema
    workers: List[WorkerStatusSchema]
    alerts: List[WorkerAlertSchema] = Field(default_factory=list)

    @classmethod
    def from_report(cls, report: WorkerHealthReport) -> "WorkerHealthResponse":
        return cls(
            status=report.status,
            totals=WorkerTotalsSchema(
                workers=report.total_workers,
                online=report.total_online,
                offline=report.total_offline,
            ),
            workers=[WorkerStatusSchema.from_domain(w) for w in report.workers],
            alerts=[WorkerAlertSchema.from_domain(alert) for alert in report.alerts],
        )
