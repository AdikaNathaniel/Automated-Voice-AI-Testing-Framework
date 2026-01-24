"""
Regression API service helpers (TASK-338).

Provides orchestration around regression reporting and baseline approval.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Optional
from uuid import UUID

logger = logging.getLogger(__name__)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.multi_turn_execution import MultiTurnExecution
from models.scenario_script import ScenarioScript
from services.baseline_management_service import BaselineManagementService
from services.regression_detection_service import (
    MetricRule,
    RegressionDetectionService,
    RegressionFinding,
    RegressionSummary,
    TestResultSnapshot,
)


@dataclass
class RegressionCandidate:
    """Captured execution snapshot plus metadata needed for the response."""

    snapshot: TestResultSnapshot
    detected_at: Optional[datetime] = None


async def list_regressions(
    db: AsyncSession,
    *,
    filters: Mapping[str, object],
    pagination: Mapping[str, int],
) -> Dict[str, Any]:
    """
    Return a paginated regression report derived from the latest executions.
    """
    candidates = await _fetch_current_snapshots(
        db,
        filters=filters,
        pagination=pagination,
    )

    if not candidates:
        return {
            "summary": _serialize_summary(None),
            "items": [],
        }

    baselines = await _fetch_baselines(db, script_ids=candidates.keys())
    if not baselines:
        return {
            "summary": _serialize_summary(None),
            "items": [],
        }

    detector = RegressionDetectionService(metric_rules=DEFAULT_METRIC_RULES)
    report = detector.detect(
        current_results=[candidate.snapshot for candidate in candidates.values()],
        baseline_results=list(baselines.values()),
    )

    status_filter = filters.get("status")
    findings = _filter_findings(report.findings, category=status_filter)

    items = [
        {
            "script_id": str(finding.script_id),
            "category": finding.category,
            "detail": finding.detail,
            "regression_detected_at": _format_timestamp(
                candidates.get(finding.script_id).detected_at
                if finding.script_id in candidates
                else None
            ),
        }
        for finding in findings
    ]

    return {
        "summary": _serialize_summary(report.summary),
        "items": items,
    }


async def approve_baseline(
    db: AsyncSession,
    *,
    script_id: UUID,
    snapshot_data: Mapping[str, Any],
    approved_by: Optional[UUID],
    note: Optional[str],
) -> Dict[str, Any]:
    """
    Approve a regression baseline for a scenario script.
    """
    status = (snapshot_data.get("status") or "").strip()
    if not status:
        raise ValueError("Baseline status is required.")

    metrics = snapshot_data.get("metrics") or {}
    if not isinstance(metrics, Mapping):
        raise ValueError("Baseline metrics must be a mapping if provided.")

    def _approve(sync_session) -> Dict[str, Any]:
        service = BaselineManagementService(sync_session)
        snapshot = TestResultSnapshot(
            script_id=script_id,
            status=status,
            metrics=dict(metrics),
        )
        record = service.approve_baseline(
            snapshot=snapshot,
            approved_by=approved_by,
            note=note,
        )

        approved_at = record.approved_at
        approved_at_iso = (
            approved_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            if approved_at
            else None
        )

        return {
            "script_id": str(record.snapshot.script_id),
            "status": record.snapshot.status,
            "metrics": dict(record.snapshot.metrics),
            "version": record.version,
            "approved_at": approved_at_iso,
            "approved_by": str(record.approved_by) if record.approved_by else None,
            "note": record.note,
        }

    return await db.run_sync(_approve)


async def get_regression_comparison(
    db: AsyncSession,
    *,
    script_id: UUID,
) -> Dict[str, Any]:
    """
    Compare the latest execution against the approved baseline for a scenario script.
    """
    baseline = await _load_single_baseline(db, script_id=script_id)
    if baseline is None:
        raise ValueError("No baseline available for this scenario script.")

    current = await _fetch_latest_execution_snapshot(db, script_id=script_id)
    if current is None:
        raise ValueError("No recent execution found for comparison.")

    differences = _compute_metric_differences(
        baseline.metrics,
        current.snapshot.metrics,
    )

    return {
        "script_id": str(script_id),
        "baseline": _serialize_snapshot(baseline),
        "current": _serialize_snapshot(current.snapshot),
        "differences": differences,
    }


async def get_baseline_history(
    db: AsyncSession,
    *,
    script_id: UUID,
) -> Dict[str, Any]:
    """
    Retrieve the baseline version history for a scenario script.

    Also returns a 'pending' baseline if there's a more recent execution
    than the last approved baseline (or if no baseline exists yet).
    """
    logger.debug(f"get_baseline_history called for script_id={script_id}")

    def _load(session) -> list:
        service = BaselineManagementService(session)
        records = service.get_baseline_history(script_id)
        return [
            {
                "version": r.version,
                "status": r.status,
                "metrics": dict(r.metrics),
                "approved_at": _format_timestamp(r.approved_at),
                "approved_by": str(r.approved_by) if r.approved_by else None,
                "note": r.note,
            }
            for r in records
        ]

    history = await db.run_sync(_load)
    logger.debug(f"Baseline history count: {len(history)}")

    # Get the latest execution to check if there's a pending baseline
    latest_execution = await _fetch_latest_execution_snapshot(db, script_id=script_id)
    logger.debug(f"Latest execution found: {latest_execution is not None}")

    pending = None
    if latest_execution:
        # Check if there's no baseline yet, or if latest execution is newer
        should_show_pending = True

        if history:
            # There's an existing baseline - check if the latest execution is newer
            last_approved_at = history[0].get("approved_at")
            if last_approved_at and latest_execution.detected_at:
                # Compare timestamps
                try:
                    approved_dt = datetime.fromisoformat(
                        last_approved_at.replace("Z", "+00:00")
                    )
                    if latest_execution.detected_at <= approved_dt:
                        # Execution is older than or equal to last approval
                        should_show_pending = False
                except (ValueError, TypeError):
                    pass

        if should_show_pending:
            # Build rich pending data with validation results
            pending = await _build_pending_baseline_data(
                db,
                execution_snapshot=latest_execution,
            )
            logger.debug(f"Setting pending baseline with status: {pending['status']}")
        else:
            logger.debug("Not showing pending - execution is older than last approval")

    logger.debug(f"Returning response - pending: {pending is not None}, history count: {len(history)}")
    return {
        "script_id": str(script_id),
        "history": history,
        "pending": pending,
    }


async def _fetch_current_snapshots(
    db: AsyncSession,
    *,
    filters: Mapping[str, object],
    pagination: Mapping[str, int],
) -> Dict[UUID, RegressionCandidate]:
    stmt = (
        select(MultiTurnExecution)
        .join(ScenarioScript, MultiTurnExecution.script_id == ScenarioScript.id)
        .where(MultiTurnExecution.script_id.isnot(None))
        .order_by(
            MultiTurnExecution.completed_at.desc().nullslast(),
            MultiTurnExecution.created_at.desc(),
        )
    )

    suite_id = filters.get("suite_id")
    if suite_id:
        stmt = stmt.where(ScenarioScript.suite_id == suite_id)

    stmt = stmt.offset(int(pagination.get("skip", 0)))
    stmt = stmt.limit(int(pagination.get("limit", 50)))

    result = await db.execute(stmt)
    executions = list(result.scalars().all())

    candidates: Dict[UUID, RegressionCandidate] = {}
    for execution in executions:
        script_id = execution.script_id
        if script_id is None or script_id in candidates:
            continue

        snapshot = TestResultSnapshot(
            script_id=script_id,
            status=(execution.status or "unknown"),
            metrics=_extract_numeric_metrics(execution),
        )
        detected_at = (
            execution.completed_at
            or execution.updated_at
            or execution.started_at
            or execution.created_at
        )
        candidates[script_id] = RegressionCandidate(
            snapshot=snapshot,
            detected_at=detected_at,
        )

    return candidates


async def _fetch_baselines(
    db: AsyncSession,
    *,
    script_ids: Iterable[UUID],
) -> Dict[UUID, TestResultSnapshot]:
    ids = list(script_ids)
    if not ids:
        return {}

    def _load(session) -> Dict[UUID, TestResultSnapshot]:
        service = BaselineManagementService(session)
        records: Dict[UUID, TestResultSnapshot] = {}
        for script_id in ids:
            record = service.get_baseline(script_id)
            if record:
                records[script_id] = record.snapshot
        return records

    return await db.run_sync(_load)


async def _load_single_baseline(
    db: AsyncSession,
    *,
    script_id: UUID,
) -> Optional[TestResultSnapshot]:
    def _load(session) -> Optional[TestResultSnapshot]:
        service = BaselineManagementService(session)
        record = service.get_baseline(script_id)
        return record.snapshot if record else None

    return await db.run_sync(_load)


async def _fetch_latest_execution_snapshot(
    db: AsyncSession,
    *,
    script_id: UUID,
) -> Optional[RegressionCandidate]:
    logger.debug(f"_fetch_latest_execution_snapshot for script_id={script_id}")
    stmt = (
        select(MultiTurnExecution)
        .where(MultiTurnExecution.script_id == script_id)
        .order_by(
            MultiTurnExecution.completed_at.desc().nullslast(),
            MultiTurnExecution.created_at.desc(),
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()
    logger.debug(f"Query returned execution: {execution.id if execution else None}")
    if execution is None:
        return None

    snapshot = TestResultSnapshot(
        script_id=script_id,
        status=execution.status or "unknown",
        metrics=_extract_numeric_metrics(execution),
    )
    detected_at = (
        execution.completed_at
        or execution.updated_at
        or execution.started_at
        or execution.created_at
    )
    return RegressionCandidate(snapshot=snapshot, detected_at=detected_at)


async def _build_pending_baseline_data(
    db: AsyncSession,
    *,
    execution_snapshot: RegressionCandidate,
) -> Dict[str, Any]:
    """
    Build rich pending baseline data including validation results and step summaries.
    """
    from sqlalchemy.orm import selectinload

    # Fetch the execution with step_executions loaded
    stmt = (
        select(MultiTurnExecution)
        .where(MultiTurnExecution.script_id == execution_snapshot.snapshot.script_id)
        .options(selectinload(MultiTurnExecution.step_executions))
        .order_by(
            MultiTurnExecution.completed_at.desc().nullslast(),
            MultiTurnExecution.created_at.desc(),
        )
        .limit(1)
    )
    result = await db.execute(stmt)
    execution = result.scalar_one_or_none()

    # Basic pending data
    pending: Dict[str, Any] = {
        "status": execution_snapshot.snapshot.status,
        "metrics": {},
        "detected_at": _format_timestamp(execution_snapshot.detected_at),
        "proposed_by": None,
    }

    if not execution:
        return pending

    # Add execution ID for reference
    pending["execution_id"] = str(execution.id)

    # Build validation summary from step executions
    steps = execution.step_executions or []
    if steps:
        total_steps = len(steps)
        passed_steps = sum(1 for s in steps if s.validation_passed is True)
        failed_steps = sum(1 for s in steps if s.validation_passed is False)

        pending["validation_summary"] = {
            "total_steps": total_steps,
            "passed_steps": passed_steps,
            "failed_steps": failed_steps,
            "all_passed": execution.all_steps_passed,
        }

        # Extract validation metrics (accuracy scores, confidence, etc.)
        validation_metrics: Dict[str, Any] = {}
        confidence_scores = []
        for step in steps:
            if step.confidence_score is not None:
                confidence_scores.append(step.confidence_score)

            # Extract from validation_details if available
            if step.validation_details and isinstance(step.validation_details, dict):
                for key, value in step.validation_details.items():
                    if isinstance(value, (int, float)):
                        if key not in validation_metrics:
                            validation_metrics[key] = []
                        validation_metrics[key].append(value)

        # Average confidence score
        if confidence_scores:
            validation_metrics["avg_confidence"] = sum(confidence_scores) / len(confidence_scores)

        # Average other metrics
        for key, values in list(validation_metrics.items()):
            if isinstance(values, list) and values:
                validation_metrics[key] = sum(values) / len(values)

        pending["metrics"] = validation_metrics

        # Include step details with AI responses for review
        step_details = []
        for step in steps[:10]:  # Limit to first 10 steps
            step_info: Dict[str, Any] = {
                "step_order": step.step_order,
                "validation_passed": step.validation_passed,
                "user_utterance": step.transcription or step.user_utterance,
            }
            if step.ai_response:
                step_info["ai_response"] = step.ai_response[:500]  # Truncate long responses
            if step.validation_details:
                step_info["validation_details"] = step.validation_details
            if step.confidence_score is not None:
                step_info["confidence_score"] = step.confidence_score

            step_details.append(step_info)

        pending["step_details"] = step_details

    return pending


def _extract_numeric_metrics(execution: MultiTurnExecution) -> Dict[str, float]:
    metrics: Dict[str, float] = {}

    def _ingest(source: Any) -> None:
        if not isinstance(source, Mapping):
            return
        for key, value in source.items():
            if isinstance(value, (int, float)):
                metrics[str(key)] = float(value)

    # Extract metrics from conversation_state if available
    _ingest(execution.conversation_state or {})

    return metrics


def _format_timestamp(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.isoformat().replace("+00:00", "Z")


def _serialize_summary(summary: Optional[RegressionSummary]) -> Dict[str, int]:
    if summary is None:
        return {
            "total_regressions": 0,
            "status_regressions": 0,
            "metric_regressions": 0,
        }
    return {
        "total_regressions": summary.total_regressions,
        "status_regressions": summary.status_regressions,
        "metric_regressions": summary.metric_regressions,
    }


def _filter_findings(
    findings: Iterable[RegressionFinding],
    *,
    category: Optional[str],
) -> Iterable[RegressionFinding]:
    normalized = (category or "").strip().lower()
    if normalized not in {"status", "metric"}:
        return findings
    return [finding for finding in findings if finding.category == normalized]


def _serialize_snapshot(snapshot: TestResultSnapshot) -> Dict[str, Any]:
    return {
        "status": snapshot.status,
        "metrics": {
            key: {"value": _coerce_float(value), "threshold": None, "unit": None}
            for key, value in snapshot.metrics.items()
            if _coerce_float(value) is not None
        },
        "media_uri": None,
    }


def _compute_metric_differences(
    baseline_metrics: Mapping[str, Any],
    current_metrics: Mapping[str, Any],
) -> list[dict[str, Any]]:
    keys = set(baseline_metrics.keys()) | set(current_metrics.keys())
    differences: list[dict[str, Any]] = []

    for key in sorted(keys):
        baseline_value = _coerce_float(baseline_metrics.get(key))
        current_value = _coerce_float(current_metrics.get(key))

        if baseline_value is None and current_value is None:
            continue

        delta = None
        delta_pct = None
        if baseline_value is not None and current_value is not None:
            delta = current_value - baseline_value
            if baseline_value not in (0.0, 0):
                delta_pct = (delta / baseline_value) * 100

        differences.append(
            {
                "metric": key,
                "baseline_value": baseline_value,
                "current_value": current_value,
                "delta": delta,
                "delta_pct": delta_pct,
            }
        )

    return differences


def _coerce_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
DEFAULT_METRIC_RULES: Dict[str, MetricRule] = {
    "intent_accuracy": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
    "intent_confidence": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
    "entity_accuracy": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
    "entity_precision": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
    "entity_recall": MetricRule(direction="higher_is_better", relative_tolerance=0.05),
}
