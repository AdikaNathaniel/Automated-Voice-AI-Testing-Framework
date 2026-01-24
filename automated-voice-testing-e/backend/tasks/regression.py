"""
Celery tasks for automatic regression suite execution and detection.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from celery_app import celery
from api.config import get_settings
from api.database import SessionLocal
from services.regression_suite_executor import RegressionSuiteExecutor
from services.smart_regression_detector import SmartRegressionDetector

logger = logging.getLogger(__name__)


async def _execute_regression_suite(
    *,
    settings: Any,
    trigger: str,
    metadata: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    async with SessionLocal() as session:
        executor = RegressionSuiteExecutor(db=session, settings=settings)
        return await executor.execute(trigger=trigger, metadata=metadata or {})


@celery.task(name="tasks.regression.run_regression_suite", bind=True)
def run_regression_suite(self, trigger: str = "scheduled", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Celery task that executes the regression suite with the provided trigger context.
    """
    settings = get_settings()

    if not getattr(settings, "ENABLE_AUTO_REGRESSION", False):
        return {"status": "disabled", "reason": "automation disabled"}

    try:
        result = asyncio.run(
            _execute_regression_suite(
                settings=settings,
                trigger=trigger,
                metadata=metadata,
            )
        )
        result.setdefault("trigger", trigger)
        return result
    except Exception as exc:  # pragma: no cover - defensive
        return {"status": "error", "reason": str(exc), "trigger": trigger}


@celery.task(name="tasks.regression.detect_suite_regressions", bind=True)
def detect_suite_regressions(
    self,
    suite_run_id: str,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detect and record regressions for a completed suite run.

    This task is automatically triggered when a suite run completes.
    It compares test results against baselines and records any regressions found.

    Args:
        suite_run_id: UUID of the completed suite run
        tenant_id: Optional tenant ID for scoping

    Returns:
        Dict containing:
            - suite_run_id: UUID of the suite run
            - regressions_detected: Number of regressions found
            - status: 'success' or 'error'
    """
    try:
        suite_run_uuid = UUID(suite_run_id)
        tenant_uuid = UUID(tenant_id) if tenant_id else None
    except ValueError as exc:
        logger.error(f"Invalid UUID provided: {exc}")
        return {
            "suite_run_id": suite_run_id,
            "status": "error",
            "reason": f"Invalid UUID: {exc}",
        }

    async def _detect():
        async with SessionLocal() as session:
            detector = SmartRegressionDetector(db=session)
            findings = await detector.detect_suite_regressions(
                suite_run_id=suite_run_uuid,
                tenant_id=tenant_uuid,
            )
            return findings

    try:
        findings = asyncio.run(_detect())

        logger.info(
            f"Regression detection completed for suite {suite_run_id}: "
            f"{len(findings)} regressions detected"
        )

        return {
            "suite_run_id": suite_run_id,
            "regressions_detected": len(findings),
            "status": "success",
            "findings": [
                {
                    "script_id": str(f.script_id),
                    "category": f.category,
                    "severity": f.severity,
                }
                for f in findings
            ],
        }
    except Exception as exc:
        logger.error(f"Failed to detect regressions for suite {suite_run_id}: {exc}")
        return {
            "suite_run_id": suite_run_id,
            "status": "error",
            "reason": str(exc),
        }
