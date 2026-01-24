"""
Dashboard aggregation service with caching support.

Provides helpers to construct the executive dashboard response while caching
aggregated results for five minutes to reduce database load.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Optional

from sqlalchemy import select, func, case, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.redis_client import get_redis
from services.metrics_service import MetricsService
from models.multi_turn_execution import MultiTurnExecution, StepExecution
from models.validation_result import ValidationResult
from models.validation_queue import ValidationQueue
from models.human_validation import HumanValidation
from models.scenario_script import ScenarioScript
from models.defect import Defect
from models.test_suite import TestSuite
from models.suite_run import SuiteRun
from models.edge_case import EdgeCase

TIME_RANGE_WINDOWS = {
    "1h": timedelta(hours=1),
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}

_CACHE_PREFIX = "dashboard:snapshot"
_CACHE_TTL_SECONDS = 300  # 5 minutes


async def get_dashboard_snapshot(
    db: AsyncSession,
    *,
    time_range: str,
) -> Dict[str, Any]:
    """
    Return dashboard snapshot - caching disabled for fresh data.
    """
    # CACHING DISABLED - Always fetch fresh dashboard data
    # cache_key = _cache_key(time_range)
    # redis_gen = get_redis()
    # redis = await redis_gen.__anext__()
    #
    # try:
    #     cached_value = await redis.get(cache_key)
    #     if cached_value is not None:
    #         return json.loads(cached_value)

    snapshot = await _compute_dashboard_snapshot(db, time_range=time_range)

    # CACHING DISABLED
    #     await redis.set(
    #         cache_key,
    #         json.dumps(snapshot, default=str),
    #         ttl=_CACHE_TTL_SECONDS,
    #     )
    return snapshot
    # finally:
    #     try:
    #         await redis_gen.aclose()
    #     except StopAsyncIteration:
    #         pass


async def invalidate_dashboard_cache(time_range: Optional[str] = None) -> int:
    """
    Invalidate cached dashboard snapshots.

    Args:
        time_range: Specific time range to clear, or None for all ranges.

    Returns:
        Number of cache entries deleted.
    """
    ranges = [time_range] if time_range else list(TIME_RANGE_WINDOWS.keys())
    redis_gen = get_redis()
    redis = await redis_gen.__anext__()
    deleted = 0

    try:
        for range_key in ranges:
            if range_key not in TIME_RANGE_WINDOWS:
                continue
            deleted += await redis.delete(_cache_key(range_key))
        return deleted
    finally:
        try:
            await redis_gen.aclose()
        except StopAsyncIteration:
            pass


def _cache_key(time_range: str) -> str:
    return f"{_CACHE_PREFIX}:{time_range}"


# Average time in minutes for a human to validate one item
AVG_HUMAN_VALIDATION_TIME_MINUTES = 2.0


async def _calculate_human_agreement_rate(
    db: AsyncSession,
    start_time: datetime,
    end_time: datetime,
) -> Dict[str, Any]:
    """
    Calculate human agreement rate with COMBINED AI validation decisions.

    Compares AI's final_decision (pass/fail from combined deterministic+LLM)
    with human's validation_decision (pass/fail) to measure how often they agree.

    The final_decision represents the combined decision from both:
    - Deterministic validation (Houndify CommandKind, ASR, patterns)
    - LLM ensemble validation (Gemini + GPT + Claude)

    Args:
        db: Database session
        start_time: Start of time window
        end_time: End of time window

    Returns:
        Dictionary with agreement metrics:
        - agreement_rate_pct: Percentage of agreement (0-100)
        - total_human_reviews: Total human reviews in period
        - agreements: Number of times combined AI and human agreed
        - disagreements: Number of times combined AI and human disagreed
        - ai_overturned: Cases where human changed AI's decision
        - edge_cases_found: Cases where human marked as edge_case
        - uncertain_resolved: Cases where AI was uncertain and human decided
    """
    # Query human validations with the COMBINED AI decision (final_decision)
    stmt = (
        select(
            ValidationResult.final_decision,
            HumanValidation.validation_decision,
        )
        .join(
            HumanValidation,
            HumanValidation.validation_result_id == ValidationResult.id
        )
        .where(
            and_(
                HumanValidation.submitted_at.isnot(None),
                HumanValidation.validation_decision.isnot(None),
                HumanValidation.submitted_at >= start_time,
                HumanValidation.submitted_at < end_time,
            )
        )
    )

    result = await db.execute(stmt)
    rows = result.all()

    total_reviews = len(rows)
    agreements = 0
    disagreements = 0
    ai_overturned = 0
    edge_cases_found = 0
    uncertain_resolved = 0
    comparable_reviews = 0  # Reviews where combined AI made a definitive decision

    for ai_decision, human_decision in rows:
        # Track edge cases separately
        if human_decision == "edge_case":
            edge_cases_found += 1
            # If AI was confident but human found edge case, count as overturned
            if ai_decision in ("pass", "fail"):
                ai_overturned += 1
                comparable_reviews += 1
                disagreements += 1
            continue

        # Normalize "create_defect" to "fail" for metrics
        # (defect creation implies the test failed)
        if human_decision == "create_defect":
            human_decision = "fail"

        # Track uncertain resolutions (combined AI was uncertain, human decided)
        if ai_decision == "uncertain" or ai_decision is None:
            uncertain_resolved += 1
            continue

        # Compare combined AI vs human for definitive AI decisions
        if ai_decision in ("pass", "fail"):
            comparable_reviews += 1

            if human_decision == ai_decision:
                agreements += 1
            else:
                disagreements += 1
                ai_overturned += 1

    # Agreement rate only for cases where combined AI made a definitive decision
    agreement_rate = (agreements / comparable_reviews * 100.0) if comparable_reviews > 0 else 0.0

    return {
        "agreement_rate_pct": round(agreement_rate, 2),
        "total_human_reviews": total_reviews,
        "agreements": agreements,
        "disagreements": disagreements,
        "ai_overturned": ai_overturned,
        "edge_cases_found": edge_cases_found,
        "uncertain_resolved": uncertain_resolved,
    }


async def _compute_dashboard_snapshot(
    db: AsyncSession,
    *,
    time_range: str,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    window = TIME_RANGE_WINDOWS.get(time_range, TIME_RANGE_WINDOWS["24h"])
    start_time = now - window

    # Count scenario executions from multi_turn_executions
    # Count by status: completed, failed, in_progress, pending
    execution_stmt = select(
        func.count(MultiTurnExecution.id),
        func.sum(case((MultiTurnExecution.status == 'completed', 1), else_=0)),
        func.sum(case((MultiTurnExecution.status == 'failed', 1), else_=0)),
        func.sum(case((MultiTurnExecution.status == 'in_progress', 1), else_=0)),
        func.sum(case((MultiTurnExecution.status == 'pending', 1), else_=0)),
    ).where(
        MultiTurnExecution.created_at >= start_time,
        MultiTurnExecution.created_at < now
    )
    execution_result = await db.execute(execution_stmt)
    total_executions, completed, failed, in_progress, pending = execution_result.one()

    # Convert to int (handle None values)
    tests_executed = int(total_executions or 0)
    executions_completed = int(completed or 0)
    executions_failed = int(failed or 0)
    tests_pending = int(pending or 0)
    tests_running = int(in_progress or 0)

    # Count actual validation pass/fail by final_decision (not execution status)
    # This gives us the real pass/fail based on validation outcomes
    validation_decision_stmt = select(
        func.count(ValidationResult.id),
        func.sum(case((ValidationResult.final_decision == 'pass', 1), else_=0)),
        func.sum(case((ValidationResult.final_decision == 'fail', 1), else_=0)),
        func.sum(case((ValidationResult.final_decision == 'uncertain', 1), else_=0)),
    ).where(
        ValidationResult.created_at >= start_time,
        ValidationResult.created_at < now
    )
    validation_decision_result = await db.execute(validation_decision_stmt)
    total_validations_checked, validations_passed, validations_failed, validations_uncertain = validation_decision_result.one()

    # Use actual validation results for pass/fail counts
    tests_passed = int(validations_passed or 0)
    tests_failed = int(validations_failed or 0)
    tests_uncertain = int(validations_uncertain or 0)

    # Get metrics for performance data (response time, confidence, etc.)
    metrics = MetricsService(db)

    response_time_data = await metrics.get_metrics(
        metric_type="response_time",
        start_time=start_time,
        end_time=now,
        granularity="raw",
        dimensions={"aggregation": "raw"},
    )
    validation_confidence_data = await metrics.get_metrics(
        metric_type="validation_confidence",
        start_time=start_time,
        end_time=now,
        granularity="raw",
        dimensions={"aggregation": "raw"},
    )

    response_stats = _summarise_metrics(response_time_data)
    confidence_stats = _summarise_metrics(validation_confidence_data)

    avg_confidence = _calculate_average(confidence_stats)
    avg_response_seconds = _calculate_average(response_stats)

    # Fallback: Calculate avg response time from StepExecution if no TestMetric data
    if avg_response_seconds is None or response_stats.total_count == 0:
        step_response_stmt = select(func.avg(StepExecution.response_time_ms)).where(
            and_(
                StepExecution.executed_at >= start_time,
                StepExecution.executed_at < now,
                StepExecution.response_time_ms.isnot(None),
            )
        )
        step_response_result = await db.execute(step_response_stmt)
        avg_response_ms = step_response_result.scalar()
        if avg_response_ms is not None:
            avg_response_seconds = float(avg_response_ms) / 1000.0  # Convert ms to seconds

    # Count pending validation queue items
    pending_queue_stmt = select(func.count(ValidationQueue.id)).where(
        ValidationQueue.status == "pending"
    )
    pending_queue_result = await db.execute(pending_queue_stmt)
    pending_reviews = pending_queue_result.scalar() or 0

    # Calculate pass rate from actual executions
    total_completed = tests_passed + tests_failed
    pass_rate = (tests_passed / total_completed) if total_completed > 0 else None

    # Count actual validation results
    validation_count_stmt = select(func.count(ValidationResult.id)).where(
        ValidationResult.created_at >= start_time,
        ValidationResult.created_at < now
    )
    validation_count_result = await db.execute(validation_count_stmt)
    total_validation_results = validation_count_result.scalar() or 0

    # Count auto-approved validations (didn't need human review)
    auto_approved_stmt = select(func.count(ValidationResult.id)).where(
        and_(
            ValidationResult.created_at >= start_time,
            ValidationResult.created_at < now,
            ValidationResult.review_status == "auto_pass",
        )
    )
    auto_approved_result = await db.execute(auto_approved_stmt)
    auto_approved_count = auto_approved_result.scalar() or 0

    # Calculate human agreement rate
    human_agreement = await _calculate_human_agreement_rate(db, start_time, now)

    # Get scenario counts
    scenario_count_stmt = select(func.count(ScenarioScript.id))
    scenario_count_result = await db.execute(scenario_count_stmt)
    total_scenarios = scenario_count_result.scalar() or 0

    # Get test suite counts
    suite_count_stmt = select(func.count(TestSuite.id))
    suite_count_result = await db.execute(suite_count_stmt)
    total_suites = suite_count_result.scalar() or 0

    # Get suite run counts
    suite_run_count_stmt = select(
        func.count(SuiteRun.id),
        func.sum(case((SuiteRun.status == 'completed', 1), else_=0)),
        func.sum(case((SuiteRun.status == 'failed', 1), else_=0)),
        func.sum(case((SuiteRun.status == 'running', 1), else_=0)),
    ).where(
        SuiteRun.created_at >= start_time,
        SuiteRun.created_at < now
    )
    suite_run_result = await db.execute(suite_run_count_stmt)
    total_suite_runs, suite_runs_completed, suite_runs_failed, suite_runs_running = suite_run_result.one()
    total_suite_runs = int(total_suite_runs or 0)
    suite_runs_completed = int(suite_runs_completed or 0)
    suite_runs_failed = int(suite_runs_failed or 0)
    suite_runs_running = int(suite_runs_running or 0)

    # Get defect counts by severity and status
    defect_stmt = select(
        func.count(Defect.id).filter(Defect.status != 'resolved'),
        func.count(Defect.id).filter(and_(Defect.severity == 'critical', Defect.status != 'resolved')),
        func.count(Defect.id).filter(and_(Defect.severity == 'high', Defect.status != 'resolved')),
        func.count(Defect.id).filter(and_(Defect.severity == 'medium', Defect.status != 'resolved')),
        func.count(Defect.id).filter(and_(Defect.severity == 'low', Defect.status != 'resolved')),
    )
    defect_result = await db.execute(defect_stmt)
    open_defects, critical_defects, high_defects, medium_defects, low_defects = defect_result.one()

    # Get edge case counts
    edge_case_stmt = select(
        func.count(EdgeCase.id),
        func.count(EdgeCase.id).filter(EdgeCase.status == 'resolved'),
    )
    edge_case_result = await db.execute(edge_case_stmt)
    total_edge_cases, resolved_edge_cases = edge_case_result.one()

    # Calculate pass rate trend (daily pass rates for the time window)
    pass_rate_trend = _calculate_pass_rate_trend(
        tests_passed=tests_passed,
        tests_failed=tests_failed,
        window=window,
        now=now
    )

    # Detect regressions (placeholder - would query test history)
    regressions = {
        "total": 0,
        "recent": []
    }

    # Calculate validation accuracy trend (placeholder - would query validation history)
    validation_accuracy_trend = []

    return {
        "kpis": {
            "tests_executed": tests_executed,
            "system_health_pct": round((pass_rate or 1.0) * 100, 2),
            "issues_detected": max(tests_failed, 0),
            "avg_response_time_ms": round((avg_response_seconds or 0.0) * 1000, 2),
        },
        "real_time_execution": {
            "current_run_id": None,
            "progress_pct": round(_progress_percentage(tests_executed, tests_passed + tests_failed), 2),
            "tests_passed": tests_passed,  # Actual validation passes
            "tests_failed": tests_failed,  # Actual validation failures
            "under_review": tests_uncertain,  # Validations needing human review
            "queued": tests_pending,  # Executions pending
        },
        "validation_accuracy": {
            # Human agreement rate: measures how often AI decisions match human reviews
            "overall_accuracy_pct": human_agreement["agreement_rate_pct"],
            "total_validations": total_validation_results,
            "human_reviews": human_agreement["total_human_reviews"],
            "agreements": human_agreement["agreements"],
            "disagreements": human_agreement["disagreements"],
            "ai_overturned": human_agreement["ai_overturned"],
            # Time saved = auto-approved items × avg human validation time
            "time_saved_hours": round(
                auto_approved_count * AVG_HUMAN_VALIDATION_TIME_MINUTES / 60, 2
            ),
        },
        "validation_queue": {
            "pending_reviews": pending_reviews,
        },
        "language_coverage": [],
        "defects": {
            "open": int(open_defects or 0),
            "critical": int(critical_defects or 0),
            "high": int(high_defects or 0),
            "medium": int(medium_defects or 0),
            "low": int(low_defects or 0),
        },
        "defects_trend": [],
        "test_coverage": [],
        "cicd_status": {
            "pipelines": [],
            "incidents": 0,
        },
        "edge_cases": {
            "total": int(total_edge_cases or 0),
            "resolved": int(resolved_edge_cases or 0),
            "categories": [],
        },
        "scenarios": {
            "total": total_scenarios,
        },
        "test_suites": {
            "total": total_suites,
        },
        "suite_runs": {
            "total": total_suite_runs,
            "completed": suite_runs_completed,
            "failed": suite_runs_failed,
            "running": suite_runs_running,
        },
        "pass_rate_trend": pass_rate_trend,
        "regressions": regressions,
        "validation_accuracy_trend": validation_accuracy_trend,
        "updated_at": now.isoformat().replace("+00:00", "Z"),
    }


class _MetricSummary:
    """Holds aggregated metric totals."""

    __slots__ = ("total_value", "total_count")

    def __init__(self, total_value: float, total_count: int) -> None:
        self.total_value = total_value
        self.total_count = total_count


def _summarise_metrics(entries: Iterable[Dict[str, Any]]) -> _MetricSummary:
    total_value = 0.0
    total_count = 0
    for entry in entries:
        value = float(entry.get("metric_value") or 0.0)
        count = int(entry.get("count", 1) or 0)
        total_value += value * max(count, 1)
        total_count += max(count, 1)
    return _MetricSummary(total_value, total_count)


def _calculate_average(summary: _MetricSummary) -> Optional[float]:
    if summary.total_count == 0:
        return None
    return summary.total_value / summary.total_count


def _progress_percentage(executions: int, processed: int) -> float:
    if executions <= 0:
        return 0.0
    return min(max((processed / executions) * 100, 0.0), 100.0)


def _calculate_pass_rate_trend(
    *,
    tests_passed: int,
    tests_failed: int,
    window: timedelta,
    now: datetime
) -> list:
    """
    Calculate pass rate trend over the time window.

    For now, returns a simplified trend with data points showing the current pass rate.
    In a full implementation, this would query historical test run data grouped by day.
    """
    # Generate daily buckets for the time window
    total_tests = tests_passed + tests_failed
    current_pass_rate = (tests_passed / total_tests * 100.0) if total_tests > 0 else 0.0

    # For demonstration, create sample trend points
    # In production, this would query actual daily test results
    trend_points = []

    # Determine number of days in window
    days = int(window.total_seconds() / 86400)  # Convert to days
    days = max(1, min(days, 30))  # Between 1 and 30 days

    # Create daily data points (simplified - uses current pass rate as baseline)
    for i in range(days):
        date = now - timedelta(days=days - i - 1)

        # In real implementation, would query actual data for each day
        # For now, show current pass rate with slight variation
        trend_points.append({
            "date": date.isoformat().replace("+00:00", "Z"),
            "pass_rate_pct": round(current_pass_rate, 2),
            "tests_passed": tests_passed // days if days > 0 else tests_passed,
            "tests_failed": tests_failed // days if days > 0 else tests_failed,
            "total_tests": total_tests // days if days > 0 else total_tests,
        })

    return trend_points
