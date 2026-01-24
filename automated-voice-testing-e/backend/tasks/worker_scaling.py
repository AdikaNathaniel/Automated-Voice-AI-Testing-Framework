"""
Celery tasks responsible for auto-scaling worker concurrency.
"""

from __future__ import annotations

from celery_app import celery
from api.config import get_settings
from services.worker_scaling_service import CeleryWorkerAutoScaler


@celery.task(name="tasks.worker_scaling.auto_scale_workers", bind=True)
def auto_scale_workers(self):
    """
    Periodic task that evaluates queue depth and scales workers accordingly.

    Returns a dictionary describing the scaling decision so the scheduler
    can inspect outcomes in monitoring/logging.
    """
    settings = get_settings()

    if not getattr(settings, "ENABLE_AUTO_SCALING", False):
        return {"status": "disabled"}

    scaler = CeleryWorkerAutoScaler(
        celery_app=celery,
        min_workers=settings.MIN_WORKERS,
        max_workers=settings.MAX_WORKERS,
        target_tasks_per_worker=settings.AUTO_SCALING_TARGET_TASKS_PER_WORKER,
        scale_down_queue_threshold=settings.AUTO_SCALING_SCALE_DOWN_THRESHOLD,
        cooldown_seconds=settings.AUTO_SCALING_COOLDOWN_SECONDS,
        queue_name=settings.AUTO_SCALING_QUEUE_NAME,
    )

    decision = scaler.evaluate_and_scale()

    return {
        "queue_depth": decision.queue_depth,
        "active_workers": decision.active_workers,
        "target_workers": decision.target_workers,
        "scaled": decision.scaled,
        "direction": decision.scale_direction,
    }
