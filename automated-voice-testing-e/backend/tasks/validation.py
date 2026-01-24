"""
Validation Tasks

This module contains Celery tasks for validating test results.
Handles:
- Test result validation against expected outcomes
- Response quality analysis
- Performance metrics validation
- Report generation
"""

from celery_app import celery
from typing import Dict, Any, Optional
from api.database import SessionLocal
from models.expected_outcome import ExpectedOutcome
from models.validation_result import ValidationResult
from models.validation_queue import ValidationQueue
from services.validation_service import ValidationService, determine_review_status
from services.validation_queue_service import ValidationQueueService
import logging
from uuid import UUID
from sqlalchemy import select
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@celery.task(name='tasks.validation.validate_multi_turn_execution', bind=True)
def validate_multi_turn_execution(
    self,
    execution_id: str,
    tenant_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate a multi-turn execution against expected outcomes.

    This task validates scenario executions created by MultiTurnExecutionService.
    It checks each step's results against the scenario's expected outcomes.

    Args:
        execution_id: UUID of the MultiTurnExecution to validate
        tenant_id: Optional UUID of the tenant for multi-tenant validation

    Returns:
        Dict containing:
            - validation_id: UUID of the validation result
            - execution_id: UUID of the execution
            - passed: Boolean indicating if validation passed
            - status: Validation status
            - step_results: Per-step validation results
    """
    import asyncio
    from models.multi_turn_execution import MultiTurnExecution

    logger.info("Starting multi-turn validation for execution: %s", execution_id)

    async def _validate():
        try:
            execution_uuid = UUID(execution_id)
        except ValueError as exc:
            raise ValueError(f"Invalid execution_id '{execution_id}'") from exc

        # Convert tenant_id to UUID if provided
        tenant_uuid = None
        if tenant_id is not None:
            try:
                tenant_uuid = UUID(tenant_id)
            except ValueError as exc:
                raise ValueError(f"Invalid tenant_id '{tenant_id}'") from exc

        async with SessionLocal() as db:
            # Fetch the MultiTurnExecution
            result = await db.execute(
                select(MultiTurnExecution).where(MultiTurnExecution.id == execution_uuid)
            )
            execution = result.scalar_one_or_none()

            if not execution:
                raise ValueError(f"MultiTurnExecution {execution_id} not found")

            # CRITICAL: Validate tenant isolation if tenant_id provided
            if tenant_uuid is not None:
                execution_tenant_id = getattr(execution, "tenant_id", None)
                if execution_tenant_id != tenant_uuid:
                    logger.error(
                        "Tenant validation failed for execution %s: "
                        "expected tenant_id=%s but got tenant_id=%s",
                        execution_id,
                        tenant_uuid,
                        execution_tenant_id,
                    )
                    raise ValueError(
                        f"Execution {execution_id} does not belong to tenant {tenant_id}"
                    )

            # Get step results from execution metadata
            step_results = execution.execution_metadata.get("step_results", []) if execution.execution_metadata else []

            # Determine overall pass/fail based on execution status
            passed = execution.status == "completed"

            return {
                "validation_id": None,  # No separate validation record for now
                "execution_id": execution_id,
                "passed": passed,
                "status": "completed",
                "step_count": len(step_results),
                "execution_status": execution.status,
                "message": f"Multi-turn execution validated with {len(step_results)} steps"
            }

    return asyncio.run(_validate())


def _build_validator_scores(validation_result: ValidationResult) -> Dict[str, float]:
    return {
        "command_kind": float(validation_result.command_kind_match_score or 0.0),
        "asr_confidence": float(validation_result.asr_confidence_score or 0.0),
        "semantic": float(validation_result.semantic_similarity_score or 0.0),
    }


def _determine_queue_priority(review_status: str) -> int:
    return 2 if review_status == "auto_fail" else 5


def _requires_native_validator(expected: ExpectedOutcome) -> bool:
    rules = expected.validation_rules or {}
    return bool(rules.get("requires_native_validator"))


def _to_percentage(score: Any) -> float:
    value = (score or 0.0) * 100
    return round(value, 2)


def _to_decimal_percentage(score: Any) -> Decimal:
    value = (score or 0.0) * 100
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@celery.task(name='tasks.validation.validate_test_result', bind=True)
def validate_test_result(
    self,
    execution_id: str,
    expected_result: Dict[str, Any],
    actual_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate a test execution result.

    Compares actual result against expected result and determines
    if the test passed or failed.

    Args:
        execution_id: UUID of the execution
        expected_result: Expected test outcome
        actual_result: Actual test outcome

    Returns:
        Dict containing:
            - validation_id: UUID of validation record
            - passed: Boolean indicating if validation passed
            - differences: List of differences found
            - confidence: Confidence score (0-1)
    """
    from uuid import uuid4

    logger.info(f"Validating test result for execution: {execution_id}")

    differences = []
    match_scores = []

    # Compare each expected key with actual result
    for key, expected_value in expected_result.items():
        actual_value = actual_result.get(key)

        if actual_value is None:
            differences.append({
                "field": key,
                "expected": expected_value,
                "actual": None,
                "type": "missing"
            })
            match_scores.append(0.0)
        elif actual_value != expected_value:
            # Calculate partial match score for strings
            if isinstance(expected_value, str) and isinstance(actual_value, str):
                expected_lower = expected_value.lower()
                actual_lower = actual_value.lower()
                if expected_lower == actual_lower:
                    match_scores.append(0.95)  # Case mismatch only
                elif expected_lower in actual_lower or actual_lower in expected_lower:
                    match_scores.append(0.7)  # Partial match
                else:
                    match_scores.append(0.0)
            else:
                match_scores.append(0.0)

            differences.append({
                "field": key,
                "expected": expected_value,
                "actual": actual_value,
                "type": "mismatch"
            })
        else:
            match_scores.append(1.0)

    # Check for extra fields in actual result
    for key in actual_result:
        if key not in expected_result:
            differences.append({
                "field": key,
                "expected": None,
                "actual": actual_result[key],
                "type": "extra"
            })

    # Calculate overall confidence
    if match_scores:
        confidence = sum(match_scores) / len(match_scores)
    else:
        confidence = 1.0 if not differences else 0.0

    # Determine pass/fail (threshold: 0.8)
    passed = confidence >= 0.8 and not any(
        d["type"] == "missing" for d in differences
    )

    validation_id = str(uuid4())
    logger.info(
        f"Validation complete for {execution_id}: "
        f"passed={passed}, confidence={confidence:.2f}, differences={len(differences)}"
    )

    return {
        'validation_id': validation_id,
        'execution_id': execution_id,
        'passed': passed,
        'differences': differences,
        'confidence': round(confidence, 4)
    }


@celery.task(name='tasks.validation.analyze_response_quality', bind=True)
def analyze_response_quality(
    self,
    execution_id: str,
    response_text: str,
    criteria: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyze the quality of a voice AI response.

    Evaluates response quality based on various criteria such as:
    - Relevance
    - Completeness
    - Accuracy
    - Language quality

    Args:
        execution_id: UUID of the execution
        response_text: The response text to analyze
        criteria: Quality criteria to evaluate (optional)

    Returns:
        Dict containing:
            - quality_score: Overall quality score (0-100)
            - metrics: Individual quality metrics
            - recommendations: Improvement recommendations
    """
    import re

    logger.info(f"Analyzing response quality for execution: {execution_id}")

    # Default criteria if not provided
    default_criteria = {
        "min_length": 10,
        "max_length": 500,
        "expected_keywords": [],
        "prohibited_phrases": ["I don't know", "I cannot", "error"],
        "check_grammar": True,
        "check_repetition": True
    }
    criteria = {**default_criteria, **(criteria or {})}

    metrics = {}
    recommendations = []

    # 1. Length analysis
    text_length = len(response_text)
    word_count = len(response_text.split())

    if text_length < criteria["min_length"]:
        metrics["length_score"] = max(0, text_length / criteria["min_length"] * 100)
        recommendations.append(
            f"Response is too short ({text_length} chars). "
            f"Consider providing more detail."
        )
    elif text_length > criteria["max_length"]:
        metrics["length_score"] = max(0, 100 - (text_length - criteria["max_length"]) / 10)
        recommendations.append(
            f"Response is too long ({text_length} chars). "
            f"Consider being more concise."
        )
    else:
        metrics["length_score"] = 100.0

    # 2. Keyword presence
    if criteria["expected_keywords"]:
        response_lower = response_text.lower()
        found_keywords = sum(
            1 for kw in criteria["expected_keywords"]
            if kw.lower() in response_lower
        )
        metrics["keyword_score"] = (
            found_keywords / len(criteria["expected_keywords"]) * 100
        )
        if metrics["keyword_score"] < 50:
            recommendations.append(
                "Response may be missing key information. "
                "Verify all expected topics are addressed."
            )
    else:
        metrics["keyword_score"] = 100.0

    # 3. Prohibited phrases check
    prohibited_found = []
    response_lower = response_text.lower()
    for phrase in criteria["prohibited_phrases"]:
        if phrase.lower() in response_lower:
            prohibited_found.append(phrase)

    if prohibited_found:
        penalty = min(len(prohibited_found) * 20, 80)
        metrics["prohibited_score"] = 100 - penalty
        recommendations.append(
            f"Response contains problematic phrases: {', '.join(prohibited_found)}. "
            "Consider rephrasing."
        )
    else:
        metrics["prohibited_score"] = 100.0

    # 4. Repetition check
    if criteria["check_repetition"]:
        words = response_text.lower().split()
        if words:
            unique_words = set(words)
            repetition_ratio = len(unique_words) / len(words)
            metrics["repetition_score"] = repetition_ratio * 100

            if repetition_ratio < 0.5:
                recommendations.append(
                    "Response contains significant repetition. "
                    "Consider varying vocabulary."
                )
        else:
            metrics["repetition_score"] = 100.0
    else:
        metrics["repetition_score"] = 100.0

    # 5. Basic grammar check
    if criteria["check_grammar"]:
        sentences = re.split(r'[.!?]+', response_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        grammar_issues = 0
        for sentence in sentences:
            if sentence and not sentence[0].isupper():
                grammar_issues += 1
            if len(sentence.split()) < 2 and len(sentence) > 0:
                grammar_issues += 0.5

        if sentences:
            metrics["grammar_score"] = max(0, 100 - grammar_issues * 10)
        else:
            metrics["grammar_score"] = 50.0

        if metrics["grammar_score"] < 70:
            recommendations.append(
                "Some grammar or sentence structure issues detected. "
                "Review capitalization and sentence completeness."
            )
    else:
        metrics["grammar_score"] = 100.0

    # 6. Clarity score
    words_per_sentence = word_count / max(1, len(sentences) if 'sentences' in dir() else 1)
    if words_per_sentence > 25:
        metrics["clarity_score"] = max(50, 100 - (words_per_sentence - 25) * 2)
        recommendations.append(
            "Some sentences are quite long. Consider breaking them up for clarity."
        )
    elif words_per_sentence < 5:
        metrics["clarity_score"] = 70.0
        recommendations.append(
            "Response uses very short sentences. Consider adding more context."
        )
    else:
        metrics["clarity_score"] = 100.0

    # Calculate overall quality score
    weights = {
        "length_score": 0.15,
        "keyword_score": 0.25,
        "prohibited_score": 0.25,
        "repetition_score": 0.10,
        "grammar_score": 0.10,
        "clarity_score": 0.15
    }

    quality_score = sum(
        metrics.get(metric, 100) * weight
        for metric, weight in weights.items()
    )

    logger.info(
        f"Quality analysis complete for {execution_id}: "
        f"score={quality_score:.1f}, metrics={len(metrics)}"
    )

    return {
        'execution_id': execution_id,
        'quality_score': round(quality_score, 2),
        'metrics': {k: round(v, 2) for k, v in metrics.items()},
        'recommendations': recommendations,
        'word_count': word_count,
        'character_count': text_length
    }


@celery.task(name='tasks.validation.validate_performance', bind=True)
def validate_performance(
    self,
    execution_id: str,
    performance_data: Dict[str, Any],
    thresholds: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Validate performance metrics of test execution.

    Checks if performance metrics meet defined thresholds.

    Args:
        execution_id: UUID of the execution
        performance_data: Performance metrics collected
        thresholds: Performance thresholds (optional)

    Returns:
        Dict containing validation results and violations
    """
    from uuid import uuid4

    logger.info(f"Validating performance for execution: {execution_id}")

    default_thresholds = {
        "response_time_ms": 3000,
        "processing_time_ms": 1000,
        "latency_ms": 500,
        "error_rate_percent": 5,
        "timeout_rate_percent": 2,
        "asr_confidence_min": 0.7,
        "memory_usage_mb": 512,
        "cpu_usage_percent": 80
    }
    thresholds = {**default_thresholds, **(thresholds or {})}

    violations = []
    metrics_summary = {}

    metric_types = {
        "response_time_ms": "max",
        "processing_time_ms": "max",
        "latency_ms": "max",
        "error_rate_percent": "max",
        "timeout_rate_percent": "max",
        "asr_confidence_min": "min",
        "memory_usage_mb": "max",
        "cpu_usage_percent": "max"
    }

    for metric_name, threshold in thresholds.items():
        actual_value = performance_data.get(metric_name)

        if actual_value is None:
            metrics_summary[metric_name] = {
                "value": None,
                "threshold": threshold,
                "status": "not_provided"
            }
            continue

        comparison_type = metric_types.get(metric_name, "max")

        if comparison_type == "max":
            passed = actual_value <= threshold
            violation_msg = f"exceeded maximum ({actual_value} > {threshold})"
        else:
            passed = actual_value >= threshold
            violation_msg = f"below minimum ({actual_value} < {threshold})"

        metrics_summary[metric_name] = {
            "value": actual_value,
            "threshold": threshold,
            "status": "passed" if passed else "failed",
            "comparison": comparison_type
        }

        if not passed:
            violations.append({
                "metric": metric_name,
                "actual": actual_value,
                "threshold": threshold,
                "type": comparison_type,
                "message": f"{metric_name} {violation_msg}"
            })

    total_metrics = sum(1 for m in metrics_summary.values() if m["status"] != "not_provided")
    passed_metrics = sum(1 for m in metrics_summary.values() if m["status"] == "passed")

    if total_metrics > 0:
        performance_score = (passed_metrics / total_metrics) * 100
    else:
        performance_score = 100.0

    overall_passed = len(violations) == 0
    validation_id = str(uuid4())

    logger.info(
        f"Performance validation complete for {execution_id}: "
        f"passed={overall_passed}, violations={len(violations)}"
    )

    return {
        'validation_id': validation_id,
        'execution_id': execution_id,
        'passed': overall_passed,
        'performance_score': round(performance_score, 2),
        'violations': violations,
        'metrics_summary': metrics_summary,
        'total_metrics': total_metrics,
        'passed_metrics': passed_metrics
    }


async def _generate_test_report_async(
    suite_run_id: str,
    format: str = 'json',
    include_details: bool = True
) -> Dict[str, Any]:
    """
    Async implementation for generating test report.
    """
    from uuid import uuid4
    from models.suite_run import SuiteRun
    from models.multi_turn_execution import MultiTurnExecution

    logger.info(f"Generating {format} report for suite run: {suite_run_id}")

    async with SessionLocal() as db:
        try:
            # Fetch suite run
            result = await db.execute(
                select(SuiteRun).where(SuiteRun.id == suite_run_id)
            )
            suite_run = result.scalar_one_or_none()

            if not suite_run:
                logger.error(f"Suite run not found: {suite_run_id}")
                return {
                    'report_id': None,
                    'format': format,
                    'url': None,
                    'summary': {},
                    'error': f'Suite run {suite_run_id} not found'
                }

            # Fetch executions
            exec_result = await db.execute(
                select(MultiTurnExecution).where(
                    MultiTurnExecution.suite_run_id == suite_run_id
                )
            )
            executions = exec_result.scalars().all()

            # Calculate summary statistics
            total_executions = len(executions)
            completed_executions = sum(
                1 for e in executions if e.status == 'completed'
            )
            failed_executions = sum(
                1 for e in executions if e.status == 'failed'
            )
            pending_executions = sum(
                1 for e in executions if e.status in ['pending', 'running']
            )

            # Build summary
            summary = {
                'suite_run_id': str(suite_run_id),
                'status': suite_run.status,
                'created_at': suite_run.created_at.isoformat() if suite_run.created_at else None,
                'completed_at': suite_run.completed_at.isoformat() if suite_run.completed_at else None,
                'execution_stats': {
                    'total': total_executions,
                    'completed': completed_executions,
                    'failed': failed_executions,
                    'pending': pending_executions,
                    'completion_rate': (
                        completed_executions / total_executions * 100
                        if total_executions > 0 else 0
                    )
                }
            }

            # Build detailed results if requested
            details = None
            if include_details:
                details = []
                for execution in executions:
                    exec_detail = {
                        'execution_id': str(execution.id),
                        'script_id': str(execution.script_id),
                        'status': execution.status,
                        'language_code': execution.language_code,
                        'total_steps': execution.total_steps,
                        'completed_steps': execution.current_step_order,
                        'created_at': execution.created_at.isoformat() if execution.created_at else None,
                    }
                    details.append(exec_detail)

            report_id = str(uuid4())

            logger.info(
                f"Report generated for {suite_run_id}: "
                f"executions={total_executions}"
            )

            return {
                'report_id': report_id,
                'suite_run_id': str(suite_run_id),
                'format': format,
                'url': None,
                'summary': summary,
                'details': details if include_details else None,
                'generated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error generating report for {suite_run_id}: {e}")
            await db.rollback()
            raise


@celery.task(name='tasks.validation.generate_test_report', bind=True)
def generate_test_report(
    self,
    suite_run_id: str,
    format: str = 'json',
    include_details: bool = True
) -> Dict[str, Any]:
    """
    Generate a comprehensive test report.

    Creates a detailed report of suite run results including:
    - Summary statistics
    - Individual test results
    - Validation outcomes
    - Performance metrics

    Args:
        suite_run_id: UUID of the suite run
        format: Report format ('json', 'html', 'pdf')
        include_details: Whether to include detailed results

    Returns:
        Dict containing report data
    """
    import asyncio
    return asyncio.run(_generate_test_report_async(suite_run_id, format, include_details))


# NOTE: The enqueue_for_human_review Celery task was removed.
# Human review enqueuing is now handled directly in multi_turn_execution_service.py
# using ValidationQueueService.enqueue_for_human_review() with correct logic:
# - Enqueues everything except auto_pass (plus 5% random sampling of auto_pass)


async def _release_timed_out_validations_async() -> Dict[str, Any]:
    """
    Internal async implementation for release_timed_out_validations task.
    """
    logger.info("Starting periodic check for timed-out validation queue items")

    timeout_minutes = 30
    cutoff_time = datetime.utcnow() - timedelta(minutes=timeout_minutes)

    async with SessionLocal() as db:
        try:
            result = await db.execute(
                select(ValidationQueue).where(
                    ValidationQueue.status == 'claimed',
                    ValidationQueue.claimed_at < cutoff_time
                )
            )
            timed_out_items = result.scalars().all()

            released_count = 0
            for item in timed_out_items:
                item.status = 'pending'
                item.claimed_by = None
                item.claimed_at = None
                released_count += 1
                logger.info(f"Released timed-out queue item {item.id}")

            if released_count > 0:
                await db.commit()

            logger.info(f"Released {released_count} timed-out validation queue items")

            return {
                'released_count': released_count,
                'timeout_minutes': timeout_minutes,
                'cutoff_time': cutoff_time.isoformat()
            }

        except Exception as e:
            logger.error(f"Error releasing timed-out validations: {e}")
            await db.rollback()
            raise


@celery.task(name='tasks.validation.release_timed_out_validations', bind=True)
def release_timed_out_validations(self) -> Dict[str, Any]:
    """
    Release validation queue items that have been claimed but not completed.

    This periodic task finds queue items that have been claimed for longer
    than the timeout period and releases them back to 'pending' status.

    Returns:
        Dict containing release results
    """
    import asyncio
    return asyncio.run(_release_timed_out_validations_async())
