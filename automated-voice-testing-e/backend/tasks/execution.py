"""
Execution Tasks

This module contains Celery tasks for executing scenario scripts.
Handles:
- Scenario execution (single and multi-turn)
- Voice input processing via Houndify
- Response capture and analysis
- Execution result recording
"""

import asyncio
import logging
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from api.database import SessionLocal
from celery import chord, group
from celery_app import celery
from models.scenario_script import ScenarioScript
from models.suite_run import SuiteRun
from services.multi_turn_execution_service import MultiTurnExecutionService
from sqlalchemy.orm import Session as SyncSession

logger = logging.getLogger(__name__)


@celery.task(name='tasks.execution.execute_scenario', bind=True)
def execute_scenario(
    self,
    script_id: str,
    language: str | None = None,
    config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Execute a scenario script using MultiTurnExecutionService.

    Runs the scenario with the specified language, executing all steps
    in sequence with conversation state management.

    Args:
        script_id: UUID of the scenario script to execute
        language: Language code for execution (optional, uses default)
        config: Additional execution configuration (optional)

    Returns:
        Dict containing:
            - execution_id: UUID of the execution record
            - script_id: UUID of the scenario script
            - status: Execution status (completed/failed/error)
            - result: Test result details
            - execution_time: Time taken to execute (seconds)

    Example:
        >>> result = execute_scenario.delay(script_id="uuid-here", language="en")
        >>> result.get()
        {'execution_id': 'uuid', 'status': 'completed', 'execution_time': 2.5}
    """
    if config is None or not config.get("suite_run_id"):
        raise ValueError("execute_scenario requires 'suite_run_id' in config")

    suite_run_id = config["suite_run_id"]
    default_language = config.get("language_code") or config.get("language") or "en-US"
    language_code = language or default_language

    try:
        script_uuid = UUID(script_id)
        suite_run_uuid = UUID(suite_run_id)
    except ValueError as exc:
        raise ValueError(f"Invalid UUID provided: {exc}") from exc

    execution_result: dict[str, Any] = {}

    async def _execute():
        nonlocal execution_result
        async with SessionLocal() as session:
            # Verify scenario exists
            scenario = await session.get(ScenarioScript, script_uuid)
            if not scenario:
                raise RuntimeError(f"Scenario script {script_uuid} not found")

            # Verify suite run exists
            suite_run = await session.get(SuiteRun, suite_run_uuid)
            if not suite_run:
                raise RuntimeError(f"Suite run {suite_run_uuid} not found")

            # Use MultiTurnExecutionService for all scenario executions
            service = MultiTurnExecutionService()

            execution = await service.execute_scenario(
                db=session,
                script_id=script_uuid,
                suite_run_id=suite_run_uuid,
                tenant_id=suite_run.tenant_id,
                language_codes=[language_code] if language_code else None,
            )

            execution_result = {
                'execution_id': str(execution.id),
                'script_id': script_id,
                'suite_run_id': suite_run_id,
                'language_code': language_code,
                'status': execution.status,
                'total_steps': execution.total_steps,
                'completed_steps': execution.current_step_order,
                'execution_time': execution.duration_seconds or 0,
            }

            await session.commit()

    asyncio.run(_execute())

    if not execution_result:
        raise RuntimeError("Scenario execution produced no results")

    # Trigger validation for completed executions
    exec_id = execution_result.get('execution_id')
    if exec_id and execution_result.get('status') == 'completed':
        try:
            from tasks.validation import validate_multi_turn_execution
            validate_multi_turn_execution.delay(execution_id=exec_id)
            logger.info(f"Validation triggered for execution {exec_id}")
        except ImportError:
            logger.debug(f"Validation task not available, skipping for execution {exec_id}")
        except Exception as exc:
            logger.warning(f"Failed to trigger validation for {exec_id}: {exc}")

    return execution_result


# Backward compatibility alias
@celery.task(name='tasks.execution.execute_test_case', bind=True)
def execute_test_case(
    self,
    test_case_id: str,
    language: str | None = None,
    config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Backward compatibility wrapper - calls execute_scenario."""
    return execute_scenario(test_case_id, language, config)


@celery.task(name='tasks.execution.execute_test_batch', bind=True)
def execute_test_batch(
    self,
    test_case_ids: list[str],
    language: str | list[str] | None = None,
    config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Execute a batch of test cases.

    Executes multiple test cases sequentially or in parallel depending
    on configuration.

    Args:
        test_case_ids: List of test case UUIDs to execute
        language: Language code for execution (optional)
        config: Execution configuration including parallel flag

    Returns:
        Dict containing:
            - batch_id: UUID of the batch execution
            - total: Total test cases in batch
            - completed: Number of completed executions
            - results: List of execution results
    """
    if not test_case_ids:
        raise ValueError("execute_test_batch requires at least one test_case_id")
    if config is None or not config.get("suite_run_id"):
        raise ValueError("execute_test_batch requires 'suite_run_id' in config")

    batch_id = str(uuid4())
    languages = _normalize_languages(language, config)
    total_executions = len(test_case_ids) * len(languages)

    # Ensure batch_id travels with each task config
    per_task_config = dict(config)
    per_task_config["batch_id"] = batch_id
    per_task_config["languages"] = languages
    completion_signature = per_task_config.pop("completion_task", None)
    suite_run_id = per_task_config.get("suite_run_id")

    run_inline = bool(config.get("run_inline"))
    if run_inline:
        inline_results = _run_inline_batch(test_case_ids, per_task_config, languages)
        return {
            'batch_id': batch_id,
            'total': total_executions,
            'scheduled': total_executions,
            'completed': len(inline_results),
            'task_ids': [],
            'results': inline_results,
            'mode': 'inline',
            'message': 'Batch execution completed inline'
        }

    signatures = []
    for test_case_id in test_case_ids:
        for language_code in languages:
            task_config = dict(per_task_config)
            task_config["language_code"] = language_code
            signatures.append(
                execute_test_case.s(
                    test_case_id,
                    language=language_code,
                    config=task_config
                )
            )

    if not signatures:
        raise RuntimeError("No tasks scheduled for batch execution")

    if not completion_signature:
        if not suite_run_id:
            raise ValueError("suite_run_id required to finalize batch execution")
        completion_signature = finalize_batch_execution.s(
            suite_run_id=suite_run_id,
            batch_id=batch_id
        )

    async_result = _schedule_batch(signatures, completion_signature)
    metadata_source = getattr(async_result, "parent", None) or async_result
    group_id = getattr(metadata_source, "id", None)
    task_ids = _extract_child_ids(metadata_source)

    return {
        'batch_id': batch_id,
        'total': total_executions,
        'scheduled': len(signatures),
        'completed': 0,
        'group_id': group_id,
        'task_ids': task_ids,
        'mode': 'async-chord' if completion_signature else 'async-group',
        'message': 'Batch execution scheduled'
    }


def _get_scenario(script_id):
    """
    Get scenario script from database.

    Args:
        script_id: UUID of scenario script

    Returns:
        ScenarioScript object or None if not found
    """
    async def _fetch():
        async with SessionLocal() as session:
            scenario = await session.get(ScenarioScript, script_id)
            if scenario:
                await session.expunge(scenario)
            return scenario

    try:
        return asyncio.run(_fetch())
    except Exception as exc:
        logger.error("Failed to fetch scenario %s: %s", script_id, exc)
        return None


def _run_inline_batch(
    test_case_ids: list[str],
    config: dict[str, Any],
    languages: list[str]
) -> list[dict[str, Any]]:
    """
    Execute the batch inline for immediate aggregation.
    """
    suite_run_id = config.get("suite_run_id")
    if not suite_run_id:
        raise ValueError("Inline batch execution requires 'suite_run_id'")

    try:
        suite_run_uuid = UUID(suite_run_id)
    except ValueError as exc:
        raise ValueError(f"Invalid suite_run_id: {exc}") from exc

    inline_results: list[dict[str, Any]] = []
    execution_languages = languages or [
        config.get("language_code") or config.get("language") or "en-US"
    ]

    async def _run_serial():
        async with SessionLocal() as session:
            # Load suite run to get tenant_id
            suite_run = await session.get(SuiteRun, suite_run_uuid)
            if not suite_run:
                raise RuntimeError(f"Suite run {suite_run_uuid} not found")

            service = MultiTurnExecutionService()

            for case_id in test_case_ids:
                for language_code in execution_languages:
                    execution = await service.execute_scenario(
                        db=session,
                        script_id=UUID(case_id),
                        suite_run_id=suite_run_uuid,
                        tenant_id=suite_run.tenant_id,
                        language_codes=[language_code] if language_code else None,
                    )
                    inline_results.append(_build_execution_payload(execution))

            await session.commit()
            await _update_suite_run_statistics_async(session, suite_run_uuid, inline_results)
            summary = _summarize_result_buckets(inline_results)
            await _maybe_finalize_suite_run_async(session, suite_run_uuid, summary)

    asyncio.run(_run_serial())
    return inline_results


def _build_execution_payload(execution) -> dict[str, Any]:
    """Normalize execution details into a serializable dictionary."""
    status = getattr(execution, "status", "completed")
    result_payload: dict[str, Any] = {}

    # Try to get result from execution_metadata (MultiTurnExecution)
    raw_result = getattr(execution, "execution_metadata", None)
    if isinstance(raw_result, dict):
        result_payload.update(raw_result)

    execution_time = getattr(execution, "duration_seconds", 0) or 0
    script_ref = getattr(execution, "script_id", None)
    language_code = getattr(execution, "language_code", None)
    error_message = getattr(execution, "error_details", None)

    if error_message and "error" not in result_payload:
        result_payload["error"] = error_message

    return {
        "execution_id": str(getattr(execution, "id", "")),
        "status": status,
        "result": result_payload,
        "execution_time": execution_time if isinstance(execution_time, (int, float)) else 0,
        "script_id": str(script_ref) if script_ref else None,
        "language_code": language_code,
    }


def _summarize_execution_status(executions: list[dict[str, Any]]) -> str:
    """Aggregate execution statuses into a single label."""
    status_values = {entry.get("status") for entry in executions if entry.get("status")}
    if not status_values:
        return "unknown"
    if len(status_values) == 1:
        return status_values.pop()
    return "mixed"


def _update_suite_run_statistics(
    db_session: SyncSession,
    suite_run_id: UUID,
    execution_results: list[dict[str, Any]]
) -> None:
    """
    Update SuiteRun counters (passed/failed/skipped) from inline executions.
    (Synchronous version for compatibility)
    """
    if not execution_results:
        return

    try:
        suite_run = db_session.get(SuiteRun, suite_run_id)
    except Exception as exc:
        logger.error("Unable to load SuiteRun %s: %s", suite_run_id, exc)
        return

    if not suite_run:
        logger.warning("SuiteRun %s not found for inline update", suite_run_id)
        return

    for result in execution_results:
        bucket = _bucket_status(result.get("status"))
        _increment_suite_run_bucket(suite_run, bucket)

    try:
        db_session.commit()
    except Exception as exc:
        db_session.rollback()
        logger.error("Failed to update SuiteRun %s counts: %s", suite_run_id, exc)


async def _update_suite_run_statistics_async(
    session,
    suite_run_id: UUID,
    execution_results: list[dict[str, Any]]
) -> None:
    """
    Update SuiteRun counters (passed/failed/skipped) from inline executions.
    (Async version)
    """
    if not execution_results:
        return

    try:
        suite_run = await session.get(SuiteRun, suite_run_id)
    except Exception as exc:
        logger.error("Unable to load SuiteRun %s: %s", suite_run_id, exc)
        return

    if not suite_run:
        logger.warning("SuiteRun %s not found for inline update", suite_run_id)
        return

    for result in execution_results:
        bucket = _bucket_status(result.get("status"))
        _increment_suite_run_bucket(suite_run, bucket)

    try:
        await session.commit()
    except Exception as exc:
        await session.rollback()
        logger.error("Failed to update SuiteRun %s counts: %s", suite_run_id, exc)


async def _maybe_finalize_suite_run_async(
    session,
    suite_run_id: UUID,
    summary: dict[str, int]
) -> None:
    """
    Mark the SuiteRun completed/failed if all executions are accounted for.
    (Async version)
    """
    try:
        suite_run = await session.get(SuiteRun, suite_run_id)
    except Exception as exc:
        logger.error("Unable to refresh SuiteRun %s for completion: %s", suite_run_id, exc)
        return

    if not suite_run or suite_run.status in {"completed", "failed"}:
        return

    total_recorded = (
        (suite_run.passed_tests or 0)
        + (suite_run.failed_tests or 0)
        + (suite_run.skipped_tests or 0)
    )
    if suite_run.total_tests and total_recorded < suite_run.total_tests:
        return

    if summary.get("failed"):
        suite_run.mark_as_failed()
    else:
        suite_run.mark_as_completed()

    try:
        await session.commit()

        # Trigger regression detection after suite completion
        try:
            from tasks.regression import detect_suite_regressions
            detect_suite_regressions.delay(
                suite_run_id=str(suite_run_id),
                tenant_id=str(suite_run.tenant_id) if suite_run.tenant_id else None,
            )
            logger.info(f"Regression detection triggered for suite run {suite_run_id}")
        except ImportError:
            logger.debug(f"Regression detection task not available, skipping for suite {suite_run_id}")
        except Exception as exc:
            logger.warning(f"Failed to trigger regression detection for {suite_run_id}: {exc}")

        # Trigger integrations (GitHub issues, Jira tickets, Slack notifications)
        if suite_run.tenant_id:
            try:
                from services.integration_orchestrator_service import trigger_integrations_after_suite_run
                integration_results = await trigger_integrations_after_suite_run(
                    db=session,
                    suite_run_id=suite_run_id,
                    tenant_id=suite_run.tenant_id,
                )
                logger.info(
                    f"Integrations triggered for suite run {suite_run_id}: "
                    f"{integration_results.get('github_issues_created', 0)} GitHub issues, "
                    f"{integration_results.get('jira_tickets_created', 0)} Jira tickets, "
                    f"Slack: {integration_results.get('slack_notification_sent', False)}"
                )
                if integration_results.get("errors"):
                    logger.warning(f"Integration errors for {suite_run_id}: {integration_results['errors']}")
            except Exception as exc:
                logger.warning(f"Failed to trigger integrations for {suite_run_id}: {exc}")

    except Exception as exc:
        await session.rollback()
        logger.error("Failed to mark SuiteRun %s complete: %s", suite_run_id, exc)


def _normalize_languages(
    language_value: str | list[str] | None,
    config: dict[str, Any]
) -> list[str]:
    """
    Normalize language inputs into a non-empty list of language codes.
    """

    languages = _coerce_language_list(language_value)
    if languages:
        return languages

    cfg_languages = _coerce_language_list(config.get("languages"))
    if cfg_languages:
        return cfg_languages

    cfg_language = config.get("language_code") or config.get("language")
    cfg_list = _coerce_language_list(cfg_language)
    if cfg_list:
        return cfg_list

    return ["en-US"]


def _coerce_language_list(value: Any) -> list[str]:
    """Convert a variety of inputs into a normalized list of language codes."""
    if not value:
        return []
    if isinstance(value, str):
        stripped = value.strip()
        return [stripped] if stripped else []
    if isinstance(value, (list, tuple, set)):
        normalized: list[str] = []
        for item in value:
            if not item:
                continue
            normalized_value = str(item).strip()
            if normalized_value:
                normalized.append(normalized_value)
        return normalized
    return []


def _schedule_batch(
    signatures: list[Any],
    completion_signature: Any | None = None
):
    """
    Schedule a Celery group or chord for the provided signatures.
    """
    if completion_signature:
        scheduled = chord(signatures, body=completion_signature)
        return scheduled.apply_async()
    execution_group = group(*signatures)
    return execution_group.apply_async()


def _extract_child_ids(result_holder: Any) -> list[str]:
    """Return child task IDs from a group/chord result."""
    children = getattr(result_holder, "children", None) or []
    task_ids: list[str] = []
    for child in children:
        child_id = getattr(child, "id", None)
        if child_id:
            task_ids.append(child_id)
    return task_ids


@celery.task(name='tasks.execution.finalize_batch_execution')
def finalize_batch_execution(
    results: list[dict[str, Any]] | None,
    suite_run_id: str,
    batch_id: str | None = None
) -> dict[str, Any]:
    """
    Celery callback to aggregate batch execution results and update SuiteRun counts.
    """
    if not suite_run_id:
        raise ValueError("finalize_batch_execution requires a suite_run_id")

    run_uuid = UUID(suite_run_id)
    flattened_results = _flatten_execution_results(results)

    summary = _summarize_result_buckets(flattened_results)
    status = _summarize_execution_status(flattened_results)

    async def _apply():
        async with SessionLocal() as session:
            await _update_suite_run_statistics_async(session, run_uuid, flattened_results)
            await _maybe_finalize_suite_run_async(session, run_uuid, summary)

    asyncio.run(_apply())

    return {
        "suite_run_id": suite_run_id,
        "batch_id": batch_id,
        "processed_executions": len(flattened_results),
        "summary": summary,
        "status": status,
    }


def _flatten_execution_results(results: list[Any] | None) -> list[dict[str, Any]]:
    """
    Expand batch results so each execution outcome is processed independently.
    """
    if not results:
        return []

    flattened: list[dict[str, Any]] = []
    for result in results:
        if not isinstance(result, dict):
            continue
        nested = result.get("executions")
        if isinstance(nested, list):
            for entry in nested:
                if isinstance(entry, dict):
                    flattened.append(entry)
        else:
            flattened.append(result)
    return flattened


def _summarize_result_buckets(execution_results: list[dict[str, Any]]) -> dict[str, int]:
    """
    Count how many executions ended up in each status bucket.
    """
    summary = {"passed": 0, "failed": 0, "skipped": 0}
    for result in execution_results:
        bucket = _bucket_status(result.get("status"))
        summary[bucket] += 1
    return summary


def _bucket_status(status: str | None) -> str:
    """
    Normalize execution status strings into logical buckets.
    """
    if not status:
        return "skipped"
    normalized = status.lower()
    if normalized in {"success", "passed", "completed"}:
        return "passed"
    if normalized in {"failed", "error"}:
        return "failed"
    if normalized in {"skipped", "deferred"}:
        return "skipped"
    return "passed"


def _increment_suite_run_bucket(suite_run: SuiteRun, bucket: str) -> None:
    """Increment the appropriate SuiteRun counter."""
    if bucket == "failed":
        suite_run.increment_failed()
    elif bucket == "skipped":
        suite_run.increment_skipped()
    else:
        suite_run.increment_passed()


def _maybe_finalize_suite_run(
    db_session: SyncSession,
    suite_run_id: UUID,
    summary: dict[str, int]
) -> None:
    """Mark the SuiteRun completed/failed if all executions are accounted for."""
    try:
        suite_run = db_session.get(SuiteRun, suite_run_id)
    except Exception as exc:
        logger.error("Unable to refresh SuiteRun %s for completion: %s", suite_run_id, exc)
        return

    if not suite_run or suite_run.status in {"completed", "failed"}:
        return

    total_recorded = (
        (suite_run.passed_tests or 0)
        + (suite_run.failed_tests or 0)
        + (suite_run.skipped_tests or 0)
    )
    if suite_run.total_tests and total_recorded < suite_run.total_tests:
        return

    if summary.get("failed"):
        suite_run.mark_as_failed()
    else:
        suite_run.mark_as_completed()

    try:
        db_session.commit()
    except Exception as exc:
        db_session.rollback()
        logger.error("Failed to mark SuiteRun %s complete: %s", suite_run_id, exc)


def _extract_error_detail(result: dict[str, Any]) -> str | None:
    """
    Pull an error detail string from a result payload if available.
    """
    if not isinstance(result, dict):
        return None
    if isinstance(result.get("error"), str):
        return result["error"]
    payload = result.get("result")
    if isinstance(payload, dict):
        error_value = payload.get("error") or payload.get("message")
        if isinstance(error_value, str):
            return error_value
    return None
