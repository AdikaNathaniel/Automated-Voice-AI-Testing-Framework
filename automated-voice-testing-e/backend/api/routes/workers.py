"""
Routes for worker health monitoring.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from api.schemas.worker import WorkerHealthResponse
from celery_app import celery
from services.worker_health_service import WorkerHealthService

router = APIRouter(prefix="/workers", tags=["Workers"])


def get_worker_health_service() -> WorkerHealthService:
    return WorkerHealthService(celery_app=celery)


@router.get("/health", response_model=WorkerHealthResponse)
def worker_health(service: WorkerHealthService = Depends(get_worker_health_service)) -> WorkerHealthResponse:
    report = service.check_health()
    return WorkerHealthResponse.from_report(report)
