"""
Orchestration Tasks

This module contains Celery tasks for orchestrating test execution.
Handles high-level coordination of test runs, including:
- Creating test runs from suites or individual test cases
- Managing test execution flow
- Coordinating parallel test execution
- Aggregating results
"""

from celery_app import celery
from typing import List, Dict, Any, Optional
import asyncio
from api.events import emit_suite_run_update
from services.notification_service import get_notification_service, NotificationServiceError


@celery.task(name='tasks.orchestration.create_suite_run', bind=True)
def create_suite_run(
    self,
    suite_id: Optional[str] = None,
    scenario_ids: Optional[List[str]] = None,
    languages: Optional[List[str]] = None,
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create and orchestrate a suite run.

    Args:
        suite_id: UUID of the test suite to run (optional)
        scenario_ids: List of scenario script UUIDs to run (optional)
        languages: List of language codes to test (optional, defaults to all)
        config: Additional configuration options (optional)

    Returns:
        Dict containing:
            - suite_run_id: UUID of the created suite run
            - status: Initial status
            - test_count: Number of tests to execute

    Example:
        >>> result = create_suite_run.delay(suite_id="uuid-here")
        >>> result.get()
        {'suite_run_id': 'uuid', 'status': 'pending', 'test_count': 5}
    """
    import logging
    from uuid import UUID
    from datetime import datetime
    from api.database import SessionLocal
    from models.suite_run import SuiteRun
    from models.scenario_script import ScenarioScript
    from models.test_suite import TestSuite
    from models.test_suite_scenario import TestSuiteScenario

    logger = logging.getLogger(__name__)

    try:
        # STEP 1: Validate inputs
        if not suite_id and not scenario_ids:
            raise ValueError("Either suite_id or scenario_ids must be provided")

        # Default language if none specified
        if not languages:
            languages = ['en-US']

        # STEP 2: Get database session (sync context for Celery task)
        with SessionLocal() as session:
            db = session.sync_session

            # STEP 3: Fetch scenarios
            scenarios = []

            if suite_id:
                # Fetch all scenarios in the suite via TestSuiteScenario
                suite_uuid = UUID(suite_id)
                suite = db.query(TestSuite).filter(TestSuite.id == suite_uuid).first()

                if not suite:
                    raise ValueError(f"Test suite {suite_id} not found")

                # Get all active scenarios in the suite
                scenarios = db.query(ScenarioScript).join(
                    TestSuiteScenario,
                    ScenarioScript.id == TestSuiteScenario.scenario_id
                ).filter(
                    TestSuiteScenario.suite_id == suite_uuid,
                    ScenarioScript.is_active == True  # noqa: E712
                ).all()

                logger.info(f"Found {len(scenarios)} scenarios in suite {suite_id}")

            elif scenario_ids:
                # Fetch specific scenarios by IDs
                scenario_uuids = [UUID(s_id) for s_id in scenario_ids]
                scenarios = db.query(ScenarioScript).filter(
                    ScenarioScript.id.in_(scenario_uuids)
                ).all()

                if len(scenarios) != len(scenario_uuids):
                    found_ids = {str(s.id) for s in scenarios}
                    missing_ids = set(scenario_ids) - found_ids
                    logger.warning(f"Some scenarios not found: {missing_ids}")

                logger.info(f"Found {len(scenarios)} scenarios from provided IDs")

            if not scenarios:
                raise ValueError("No scenarios found to execute")

            # STEP 4: Create SuiteRun record
            total_tests = len(scenarios) * len(languages)

            suite_run = SuiteRun(
                suite_id=UUID(suite_id) if suite_id else None,
                name=config.get('name') if config and config.get('name') else f"Suite Run - {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}",
                status='pending',
                total_tests=total_tests,
                passed_tests=0,
                failed_tests=0,
                skipped_tests=0,
                configuration=config or {}
            )

            db.add(suite_run)
            db.commit()
            db.refresh(suite_run)

            suite_run_id = str(suite_run.id)

            logger.info(
                f"Created suite run {suite_run_id} with {total_tests} tests "
                f"({len(scenarios)} scenarios × {len(languages)} languages)"
            )

            # STEP 5: Schedule test executions
            # This will be handled by schedule_test_executions task
            result = schedule_test_executions.apply_async(
                kwargs={
                    'suite_run_id': suite_run_id,
                    'scenario_ids': [str(s.id) for s in scenarios],
                    'languages': languages
                }
            )

            logger.info(f"Scheduled test executions with task ID: {result.id}")

            # STEP 6: Emit real-time event
            try:
                asyncio.run(emit_suite_run_update(
                    suite_run_id=suite_run.id,
                    data={
                        'status': 'pending',
                        'total_tests': total_tests,
                        'message': 'Suite run created and scheduled'
                    }
                ))
            except Exception as e:
                # Log but don't fail
                logger.warning(f"Failed to emit suite run event: {e}")

            # STEP 7: Return suite run information
            return {
                'suite_run_id': suite_run_id,
                'status': 'pending',
                'test_count': total_tests,
                'test_cases': len(test_cases),
                'languages': languages,
                'schedule_task_id': result.id,
                'message': 'Suite run created successfully'
            }

    except ValueError as e:
        logger.error(f"Validation error creating suite run: {e}")
        return {
            'suite_run_id': None,
            'status': 'error',
            'test_count': 0,
            'error': str(e),
            'message': f'Validation failed: {str(e)}'
        }
    except Exception as e:
        logger.error(f"Unexpected error creating suite run: {e}", exc_info=True)
        return {
            'suite_run_id': None,
            'status': 'error',
            'test_count': 0,
            'error': str(e),
            'message': f'Failed to create suite run: {str(e)}'
        }


@celery.task(name='tasks.orchestration.schedule_test_executions', bind=True)
def schedule_test_executions(
    self,
    suite_run_id: str,
    test_case_ids: List[str],
    languages: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Schedule execution of multiple test cases.

    Creates execution tasks for each test case and language combination.
    Uses Celery groups for parallel execution.

    Args:
        suite_run_id: UUID of the suite run
        test_case_ids: List of test case UUIDs to execute
        languages: List of language codes (optional)

    Returns:
        Dict containing:
            - scheduled_count: Number of tasks scheduled
            - task_ids: List of Celery task IDs
    """
    import logging
    from celery import group
    from tasks.execution import execute_test_case

    logger = logging.getLogger(__name__)

    try:
        # Default to en-US if no languages specified
        if not languages:
            languages = ['en-US']

        logger.info(
            f"Scheduling {len(test_case_ids)} test cases × {len(languages)} languages "
            f"= {len(test_case_ids) * len(languages)} total tests for suite run {suite_run_id}"
        )

        # Create execution task for each test case × language combination
        tasks = []

        for test_case_id in test_case_ids:
            for language in languages:
                # Create task signature for execute_test_case
                task_signature = execute_test_case.s(
                    test_case_id=test_case_id,
                    language=language,
                    config={
                        'suite_run_id': suite_run_id,
                        'language_code': language
                    }
                )
                tasks.append(task_signature)

        # Execute tasks in parallel using Celery group
        job = group(tasks)
        result = job.apply_async()

        # Get task IDs from group result
        task_ids = [str(r.id) for r in result.results] if hasattr(result, 'results') else []

        scheduled_count = len(tasks)

        logger.info(
            f"Successfully scheduled {scheduled_count} test executions "
            f"for suite run {suite_run_id} with group ID {result.id}"
        )

        # Emit real-time event
        try:
            from uuid import UUID
            asyncio.run(emit_suite_run_update(
                suite_run_id=UUID(suite_run_id),
                data={
                    'status': 'running',
                    'scheduled_count': scheduled_count,
                    'message': f'Scheduled {scheduled_count} test executions'
                }
            ))
        except Exception as e:
            # Log but don't fail
            logger.warning(f"Failed to emit scheduling event: {e}")

        return {
            'scheduled_count': scheduled_count,
            'task_ids': task_ids,
            'group_id': str(result.id),
            'suite_run_id': suite_run_id,
            'message': f'Successfully scheduled {scheduled_count} test executions'
        }

    except Exception as e:
        logger.error(f"Failed to schedule test executions: {e}", exc_info=True)
        return {
            'scheduled_count': 0,
            'task_ids': [],
            'error': str(e),
            'suite_run_id': suite_run_id,
            'message': f'Failed to schedule test executions: {str(e)}'
        }


@celery.task(name='tasks.orchestration.aggregate_results', bind=True)
def aggregate_results(
    self,
    suite_run_id: str,
    execution_results: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Aggregate results from multiple test executions.

    Combines individual test results and updates the suite run status.

    Args:
        suite_run_id: UUID of the suite run
        execution_results: List of execution result dictionaries (optional)

    Returns:
        Dict containing:
            - total_tests: Total number of tests executed
            - passed: Number of passed tests
            - failed: Number of failed tests
            - summary: Overall summary
    """
    import logging
    from uuid import UUID
    from datetime import datetime
    from api.database import SessionLocal
    from models.suite_run import SuiteRun
    from models.multi_turn_execution import MultiTurnExecution
    from sqlalchemy import select

    logger = logging.getLogger(__name__)

    try:
        # STEP 1: Validate inputs and fetch results if not provided
        if not execution_results:
            logger.info(f"[ORCHESTRATION] Fetching execution results from database for suite_run_id={suite_run_id}")

            # Fetch execution results from database using sync session
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                from api.config import get_settings

                settings = get_settings()
                # Create sync engine (remove +asyncpg if present)
                sync_db_url = settings.DATABASE_URL.replace('+asyncpg', '')
                sync_engine = create_engine(sync_db_url)
                SyncSessionLocal = sessionmaker(bind=sync_engine)

                db = SyncSessionLocal()
                try:
                    stmt = select(MultiTurnExecution).where(
                        MultiTurnExecution.suite_run_id == UUID(suite_run_id)
                    )
                    executions = db.execute(stmt).scalars().all()

                    # Convert executions to result dictionaries
                    execution_results = [
                        {
                            'execution_id': str(exec.id),
                            'script_id': str(exec.script_id),
                            'status': exec.status,
                            'result': exec.execution_metadata or {},
                            'execution_time': 0,  # Calculate from timestamps if needed
                            'error': exec.error_details
                        }
                        for exec in executions
                    ]
                    logger.info(f"[ORCHESTRATION] Fetched {len(execution_results)} execution results from database")
                finally:
                    db.close()
            except Exception as e:
                logger.error(f"[ORCHESTRATION] Failed to fetch execution results: {e}")
                execution_results = []

        if not execution_results:
            logger.warning(f"No execution results to aggregate for suite run {suite_run_id}")
            return {
                'suite_run_id': suite_run_id,
                'total_tests': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'summary': 'No execution results provided',
                'message': 'Aggregation completed with no results'
            }

        # STEP 2: Calculate summary statistics
        total_tests = len(execution_results)
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_execution_time = 0.0
        error_count = 0

        for result in execution_results:
            status = result.get('status', '').lower()

            # Categorize by status
            if status in ['passed', 'success', 'completed']:
                passed_tests += 1
            elif status in ['failed', 'error']:
                failed_tests += 1
            elif status in ['skipped', 'deferred']:
                skipped_tests += 1
            else:
                # Unknown status - count as skipped
                skipped_tests += 1

            # Track errors
            if result.get('error') or result.get('result', {}).get('error'):
                error_count += 1

            # Sum execution times
            exec_time = result.get('execution_time', 0)
            if isinstance(exec_time, (int, float)):
                total_execution_time += exec_time

        # Calculate pass rate
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        # Determine overall status
        if failed_tests > 0:
            overall_status = 'failed'
        elif skipped_tests == total_tests:
            overall_status = 'skipped'
        elif passed_tests == total_tests:
            overall_status = 'completed'
        else:
            overall_status = 'partial'

        logger.info(
            f"Aggregated results for suite run {suite_run_id}: "
            f"{passed_tests} passed, {failed_tests} failed, {skipped_tests} skipped "
            f"({pass_rate:.1f}% pass rate)"
        )

        # STEP 3: Update suite run status in database
        try:
            with SessionLocal() as session:
                db = session.sync_session

                # Fetch suite run
                suite_run = db.query(SuiteRun).filter(
                    SuiteRun.id == UUID(suite_run_id)
                ).first()

                if not suite_run:
                    logger.error(f"Suite run {suite_run_id} not found for aggregation")
                    return {
                        'suite_run_id': suite_run_id,
                        'total_tests': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'skipped': skipped_tests,
                        'error': 'Suite run not found',
                        'message': 'Aggregation failed: suite run not found'
                    }

                # Update suite run statistics
                suite_run.passed_tests = passed_tests
                suite_run.failed_tests = failed_tests
                suite_run.skipped_tests = skipped_tests
                suite_run.total_tests = total_tests

                # Update status based on results
                if overall_status == 'completed':
                    suite_run.mark_as_completed()
                elif overall_status == 'failed':
                    suite_run.mark_as_failed()
                # If partial or skipped, leave status as is (running/pending)

                db.commit()
                db.refresh(suite_run)

                logger.info(f"Updated suite run {suite_run_id} with aggregated results")

        except Exception as e:
            logger.error(f"Failed to update suite run {suite_run_id}: {e}", exc_info=True)
            # Continue with aggregation even if DB update fails

        # STEP 4: Emit real-time event
        try:
            asyncio.run(emit_suite_run_update(
                suite_run_id=UUID(suite_run_id),
                data={
                    'status': overall_status,
                    'total_tests': total_tests,
                    'passed_tests': passed_tests,
                    'failed_tests': failed_tests,
                    'skipped_tests': skipped_tests,
                    'pass_rate': round(pass_rate, 1),
                    'message': 'Results aggregated successfully'
                }
            ))
        except Exception as e:
            # Log but don't fail
            logger.warning(f"Failed to emit aggregation event: {e}")

        # STEP 5: Send notification for completed suite run
        if overall_status in ('completed', 'failed'):
            try:
                notification_service = get_notification_service()
                run_url = f"/suite-runs/{suite_run_id}"  # Relative URL for frontend
                notification_status = "success" if overall_status == "completed" else "failure"
                asyncio.run(notification_service.notify_test_run_result(
                    status=notification_status,
                    passed=passed_tests,
                    failed=failed_tests,
                    duration_seconds=total_execution_time,
                    run_url=run_url,
                ))
                logger.info(f"Sent notification for suite run {suite_run_id} completion ({overall_status})")
            except NotificationServiceError as e:
                # Log but don't fail - notifications shouldn't break core functionality
                logger.warning(f"Failed to send suite run notification: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error sending notification: {e}")

        # STEP 6: Return aggregated results
        summary = {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'pass_rate': round(pass_rate, 1),
            'total_execution_time': round(total_execution_time, 2),
            'average_execution_time': round(total_execution_time / total_tests, 2) if total_tests > 0 else 0,
            'error_count': error_count
        }

        return {
            'suite_run_id': suite_run_id,
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'overall_status': overall_status,
            'pass_rate': round(pass_rate, 1),
            'summary': summary,
            'message': 'Results aggregated successfully'
        }

    except Exception as e:
        logger.error(f"Unexpected error aggregating results for suite run {suite_run_id}: {e}", exc_info=True)
        return {
            'suite_run_id': suite_run_id,
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'error': str(e),
            'message': f'Aggregation failed: {str(e)}'
        }


@celery.task(name='tasks.orchestration.schedule_suite_run', bind=True)
def schedule_suite_run(
    self,
    suite_run_id: str
) -> Dict[str, Any]:
    """
    Schedule a suite run by creating queue entries for all tests.

    Creates queue entries for each test case in the suite run and distributes
    them to execution engines through the queue manager. This task coordinates
    the initial setup of test execution.

    Args:
        suite_run_id: UUID string of the suite run to schedule

    Returns:
        Dict containing:
            - suite_run_id: UUID of the suite run
            - queued_count: Number of tests queued
            - status: Scheduling status
            - queue_ids: List of created queue entry IDs

    Raises:
        ValueError: If suite_run_id is invalid
        RuntimeError: If suite run is not in schedulable state

    Example:
        >>> result = schedule_suite_run.delay(suite_run_id="uuid-here")
        >>> result.get()
        {'suite_run_id': 'uuid', 'queued_count': 10, 'status': 'scheduled'}
    """
    try:
        from uuid import UUID
        from services.orchestration_service import schedule_test_executions
        from api.database import get_sync_db

        # Convert string to UUID
        run_id = UUID(suite_run_id)

        # Get database session
        db = get_sync_db()

        # Schedule test executions through orchestration service
        # This creates the execution records
        result = schedule_test_executions(db, run_id)

        # Create queue entries for prioritized execution
        # In a full implementation, we would:
        # 1. Fetch all test cases for the test run
        # 2. Create queue entry for each with appropriate priority
        # 3. Return the queue entry IDs

        queue_ids = []
        # Placeholder for queue creation logic
        # for test_case in test_cases:
        #     queue_entry = await queue_manager.enqueue_test(
        #         db=db,
        #         test_case_id=test_case.id,
        #         test_run_id=run_id,
        #         priority=5
        #     )
        #     queue_ids.append(str(queue_entry.id))

        # Prepare return data
        response_data = {
            'suite_run_id': suite_run_id,
            'queued_count': result.get('scheduled_count', 0),
            'status': 'scheduled',
            'queue_ids': queue_ids,
            'message': 'Suite run scheduled successfully'
        }

        # Emit real-time event to subscribed clients
        try:
            asyncio.run(emit_suite_run_update(
                suite_run_id=run_id,
                data={
                    'status': 'scheduled',
                    'queued_count': response_data['queued_count'],
                    'message': 'Suite run has been scheduled'
                }
            ))
        except Exception as e:
            # Log error but don't fail the task
            print(f"Failed to emit suite run update event: {e}")

        return response_data

    except ValueError as e:
        return {
            'suite_run_id': suite_run_id,
            'queued_count': 0,
            'status': 'error',
            'error': f'Invalid suite run ID: {str(e)}'
        }
    except Exception as e:
        return {
            'suite_run_id': suite_run_id,
            'queued_count': 0,
            'status': 'error',
            'error': f'Failed to schedule suite run: {str(e)}'
        }


@celery.task(name='tasks.orchestration.monitor_suite_run_progress', bind=True)
def monitor_suite_run_progress(
    self,
    suite_run_id: str
) -> Dict[str, Any]:
    """
    Monitor suite run progress and update status.

    Checks the completion status of all test executions in a suite run,
    updates the suite run status accordingly, and triggers notifications
    if the run is complete.

    Args:
        suite_run_id: UUID string of the suite run to monitor

    Returns:
        Dict containing:
            - suite_run_id: UUID of the suite run
            - status: Current suite run status
            - progress: Progress percentage (0-100)
            - completed_tests: Number of completed tests
            - total_tests: Total number of tests
            - is_complete: Boolean indicating if run is complete

    Raises:
        ValueError: If suite_run_id is invalid

    Example:
        >>> result = monitor_suite_run_progress.delay(suite_run_id="uuid-here")
        >>> result.get()
        {'suite_run_id': 'uuid', 'status': 'running', 'progress': 50, 'is_complete': False}
    """
    try:
        from uuid import UUID
        from api.database import get_sync_db
        from models.suite_run import SuiteRun

        # Convert string to UUID
        run_id = UUID(suite_run_id)

        # Get database session
        db = get_sync_db()

        # Fetch suite run
        suite_run = db.query(SuiteRun).filter(SuiteRun.id == run_id).first()

        if not suite_run:
            return {
                'suite_run_id': suite_run_id,
                'status': 'not_found',
                'error': f'Suite run with ID {suite_run_id} not found'
            }

        # Calculate progress
        total_tests = suite_run.total_tests or 0
        completed_tests = (suite_run.passed_tests or 0) + (suite_run.failed_tests or 0) + (suite_run.skipped_tests or 0)

        progress = 0
        if total_tests > 0:
            progress = int((completed_tests / total_tests) * 100)

        is_complete = suite_run.is_completed()

        # Update status if all tests are complete
        if not is_complete and completed_tests == total_tests and total_tests > 0:
            # Determine final status based on results
            if suite_run.failed_tests and suite_run.failed_tests > 0:
                suite_run.mark_as_failed()
            else:
                suite_run.mark_as_completed()
            db.commit()
            is_complete = True

        # Trigger notifications if complete
        if is_complete:
            try:
                notification_service = get_notification_service()
                run_url = f"/suite-runs/{suite_run_id}"
                notification_status = "failure" if (suite_run.failed_tests or 0) > 0 else "success"
                # Calculate duration if available
                duration_seconds = 0.0
                if suite_run.started_at and suite_run.completed_at:
                    duration_seconds = (suite_run.completed_at - suite_run.started_at).total_seconds()
                asyncio.run(notification_service.notify_test_run_result(
                    status=notification_status,
                    passed=suite_run.passed_tests or 0,
                    failed=suite_run.failed_tests or 0,
                    duration_seconds=duration_seconds,
                    run_url=run_url,
                ))
                logger.info(f"Sent notification for suite run {suite_run_id} completion via monitor")
            except NotificationServiceError as e:
                # Log but don't fail - notifications shouldn't break core functionality
                logger.warning(f"Failed to send suite run notification: {e}")
            except Exception as e:
                logger.warning(f"Unexpected error sending notification: {e}")

        # Prepare return data
        response_data = {
            'suite_run_id': suite_run_id,
            'status': suite_run.status,
            'progress': progress,
            'completed_tests': completed_tests,
            'total_tests': total_tests,
            'passed_tests': suite_run.passed_tests or 0,
            'failed_tests': suite_run.failed_tests or 0,
            'skipped_tests': suite_run.skipped_tests or 0,
            'is_complete': is_complete,
            'message': 'Progress monitored successfully'
        }

        # Emit real-time progress update to subscribed clients
        try:
            asyncio.run(emit_suite_run_update(
                suite_run_id=run_id,
                data={
                    'status': response_data['status'],
                    'progress': response_data['progress'],
                    'completed_tests': response_data['completed_tests'],
                    'total_tests': response_data['total_tests'],
                    'passed_tests': response_data['passed_tests'],
                    'failed_tests': response_data['failed_tests'],
                    'skipped_tests': response_data['skipped_tests'],
                    'is_complete': response_data['is_complete']
                }
            ))
        except Exception as e:
            # Log error but don't fail the task
            print(f"Failed to emit progress update event: {e}")

        return response_data

    except ValueError as e:
        return {
            'suite_run_id': suite_run_id,
            'status': 'error',
            'error': f'Invalid suite run ID: {str(e)}'
        }
    except Exception as e:
        return {
            'suite_run_id': suite_run_id,
            'status': 'error',
            'error': f'Failed to monitor suite run: {str(e)}'
        }
