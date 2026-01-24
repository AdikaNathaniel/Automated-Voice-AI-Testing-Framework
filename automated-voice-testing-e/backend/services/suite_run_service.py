"""
Suite Run Service

Manages suite run lifecycle including creation, listing, cancellation, and retry.
This service handles the CRUD operations for suite runs while delegating
execution scheduling to ExecutionSchedulerService.
"""

from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.suite_run import SuiteRun
from models.test_suite import TestSuite
from models.test_suite_scenario import TestSuiteScenario
from models.scenario_script import ScenarioScript
from models.multi_turn_execution import MultiTurnExecution


class SuiteRunService:
    """
    Service for managing suite run lifecycle operations.

    Handles creating, listing, canceling, and retrying suite runs.
    Works with ExecutionSchedulerService for scheduling test executions.
    """

    async def create_suite_run(
        self,
        db: AsyncSession,
        suite_id: Optional[UUID] = None,
        scenario_ids: Optional[List[UUID]] = None,
        languages: Optional[List[str]] = None,
        trigger_type: str = "manual",
        trigger_metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[UUID] = None,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Create a new suite run.

        Creates a suite run from either a test suite or a list of scenario IDs.
        At least one of suite_id or scenario_ids must be provided.

        Args:
            db: Database session
            suite_id: UUID of the test suite to run (optional)
            scenario_ids: List of scenario UUIDs to run (optional)
            languages: List of language codes to test (optional)
            trigger_type: Type of trigger ('manual', 'scheduled', 'api', 'webhook')
            trigger_metadata: Additional metadata about the trigger (optional)
            created_by: UUID of the user who created the suite run (optional)
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: The created suite run instance

        Raises:
            ValueError: If neither suite_id nor scenario_ids is provided
            ValueError: If suite_id is invalid
            ValueError: If scenario_ids contains invalid IDs
        """
        if not suite_id and not scenario_ids:
            raise ValueError("Either suite_id or scenario_ids must be provided")

        scenarios_to_run = await self._get_scenarios_to_run(
            db, suite_id, scenario_ids, tenant_id
        )

        if not scenarios_to_run:
            raise ValueError("No scenarios found to execute")

        metadata = dict(trigger_metadata) if trigger_metadata else {}
        if languages:
            metadata["languages"] = list(languages)

        # Save scenario_ids to metadata so scheduler knows which specific scenarios to run
        if scenario_ids:
            metadata["scenario_ids"] = [str(s_id) for s_id in scenario_ids]

        suite_run = SuiteRun(
            suite_id=suite_id,
            created_by=created_by,
            tenant_id=tenant_id,
            status="pending",
            total_tests=len(scenarios_to_run),
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            trigger_type=trigger_type,
            trigger_metadata=metadata if metadata else None
        )

        db.add(suite_run)
        await db.commit()
        await db.refresh(suite_run)

        return suite_run

    async def list_suite_runs(
        self,
        db: AsyncSession,
        *,
        suite_id: Optional[UUID] = None,
        status_filter: Optional[str] = None,
        created_by: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
        language_code: Optional[str] = None,
        tenant_id: Optional[UUID] = None,
    ) -> tuple[list[SuiteRun], int]:
        """
        Retrieve paginated suite runs with optional filtering.

        Args:
            db: Database session
            suite_id: Filter by test suite UUID
            status_filter: Filter by status
            created_by: Filter by creator
            start_date: Filter by start date
            end_date: Filter by end date
            skip: Number of records to skip
            limit: Maximum records to return
            language_code: Filter by language code
            tenant_id: Filter by tenant

        Returns:
            Tuple of (list of suite runs, total count)
        """
        stmt = select(SuiteRun).order_by(SuiteRun.created_at.desc())
        count_stmt = select(func.count()).select_from(SuiteRun)

        stmt, count_stmt = self._apply_filters(
            stmt, count_stmt, tenant_id, suite_id, status_filter,
            created_by, start_date, end_date, language_code
        )

        stmt = stmt.offset(skip).limit(limit)

        total_result = await db.execute(count_stmt)
        total = int(total_result.scalar_one() or 0)

        result = await db.execute(stmt)
        runs = list(result.scalars().all())

        return runs, total

    async def cancel_suite_run(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Cancel a running suite run.

        Stops all pending/running test executions and marks the suite run
        as canceled.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run to cancel
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: The updated suite run instance

        Raises:
            ValueError: If suite_run_id is invalid
            RuntimeError: If suite run is not in a cancelable state
        """
        suite_run = await db.get(SuiteRun, suite_run_id)
        if not suite_run:
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if tenant_id and suite_run.tenant_id not in (None, tenant_id):
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if suite_run.status not in ["pending", "running"]:
            raise RuntimeError(
                f"Cannot cancel suite run with status '{suite_run.status}'. "
                f"Only 'pending' or 'running' suite runs can be canceled."
            )

        await self._cancel_executions(db, suite_run_id)

        suite_run.mark_as_cancelled()

        await db.commit()
        await db.refresh(suite_run)

        return suite_run

    async def retry_failed_tests(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> SuiteRun:
        """
        Retry failed tests from a suite run.

        Creates a new suite run containing only the tests that failed
        in the original run.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run with failed tests
            tenant_id: UUID of the tenant (optional)

        Returns:
            SuiteRun: A new suite run instance for retrying failed tests

        Raises:
            ValueError: If suite_run_id is invalid
            ValueError: If suite run has no failed tests
        """
        original_run = await db.get(SuiteRun, suite_run_id)
        if not original_run:
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if tenant_id and original_run.tenant_id not in (None, tenant_id):
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if not original_run.failed_tests or original_run.failed_tests <= 0:
            raise ValueError("Suite run has no failed tests to retry")

        failed_executions = await self._get_failed_executions(db, suite_run_id)
        if not failed_executions:
            raise ValueError("No failed executions found to retry")

        execution_payload, retry_scenario_ids = self._build_retry_payload(
            failed_executions
        )

        if not execution_payload:
            raise ValueError("Unable to determine executions to retry")

        retry_metadata = {
            "original_suite_run_id": str(suite_run_id),
            "retry_source_execution_ids": [
                str(exec.id) for exec in failed_executions
            ],
            "executions": execution_payload,
        }

        new_run = await self.create_suite_run(
            db=db,
            suite_id=original_run.suite_id,
            scenario_ids=retry_scenario_ids,
            trigger_type="retry",
            trigger_metadata=retry_metadata,
            created_by=original_run.created_by,
            tenant_id=original_run.tenant_id,
        )

        new_run.total_tests = len(execution_payload)
        await db.commit()
        await db.refresh(new_run)

        return new_run

    async def _get_scenarios_to_run(
        self,
        db: AsyncSession,
        suite_id: Optional[UUID],
        scenario_ids: Optional[List[UUID]],
        tenant_id: Optional[UUID],
    ) -> List[ScenarioScript]:
        """
        Get scenarios from suite or by IDs.

        Priority order:
        1. If scenario_ids provided, return only those specific scenarios
        2. If only suite_id provided, return all active scenarios from suite
        3. If neither provided, return empty list

        This ensures that when a user clicks "Run Test" on a single scenario,
        only that scenario is executed (not the entire suite).
        """
        # Priority 1: Specific scenario IDs (e.g., running a single scenario)
        if scenario_ids:
            query = select(ScenarioScript).filter(ScenarioScript.id.in_(scenario_ids))
            if tenant_id:
                query = query.where(ScenarioScript.tenant_id == tenant_id)

            result = await db.execute(query)
            scenarios = list(result.scalars().all())

            if len(scenarios) != len(scenario_ids):
                raise ValueError("One or more scenario IDs are invalid")

            return scenarios

        # Priority 2: Entire suite (e.g., running all scenarios in a suite)
        elif suite_id:
            suite = await db.get(TestSuite, suite_id)
            if not suite:
                raise ValueError(f"Test suite with ID {suite_id} not found")

            suite_tenant = getattr(suite, "tenant_id", None)
            if tenant_id and suite_tenant not in (None, tenant_id):
                raise ValueError("Test suite not accessible for this tenant")

            # Get scenarios linked to suite through TestSuiteScenario
            query = (
                select(ScenarioScript)
                .join(
                    TestSuiteScenario,
                    ScenarioScript.id == TestSuiteScenario.scenario_id
                )
                .where(
                    and_(
                        TestSuiteScenario.suite_id == suite_id,
                        ScenarioScript.is_active == True
                    )
                )
            )
            if tenant_id:
                query = query.where(ScenarioScript.tenant_id == tenant_id)

            result = await db.execute(query)
            return list(result.scalars().all())

        return []

    def _apply_filters(
        self,
        stmt,
        count_stmt,
        tenant_id: Optional[UUID],
        suite_id: Optional[UUID],
        status_filter: Optional[str],
        created_by: Optional[UUID],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        language_code: Optional[str],
    ):
        """Apply filters to query statements."""
        if tenant_id:
            stmt = stmt.where(SuiteRun.tenant_id == tenant_id)
            count_stmt = count_stmt.where(SuiteRun.tenant_id == tenant_id)

        if suite_id:
            stmt = stmt.where(SuiteRun.suite_id == suite_id)
            count_stmt = count_stmt.where(SuiteRun.suite_id == suite_id)

        if status_filter:
            stmt = stmt.where(SuiteRun.status == status_filter)
            count_stmt = count_stmt.where(SuiteRun.status == status_filter)

        if created_by:
            stmt = stmt.where(SuiteRun.created_by == created_by)
            count_stmt = count_stmt.where(SuiteRun.created_by == created_by)

        if start_date:
            stmt = stmt.where(SuiteRun.created_at >= start_date)
            count_stmt = count_stmt.where(SuiteRun.created_at >= start_date)

        if end_date:
            stmt = stmt.where(SuiteRun.created_at <= end_date)
            count_stmt = count_stmt.where(SuiteRun.created_at <= end_date)

        if language_code:
            # Filter by language in trigger_metadata (JSONB contains check)
            # The language is stored in trigger_metadata.languages array or trigger_metadata.language_code
            from sqlalchemy import or_, cast
            from sqlalchemy.dialects.postgresql import JSONB

            # Check if language_code is in the languages array or matches language_code field
            language_filter = or_(
                SuiteRun.trigger_metadata['languages'].astext.contains(language_code),
                SuiteRun.trigger_metadata['language_code'].astext == language_code,
            )
            stmt = stmt.where(language_filter)
            count_stmt = count_stmt.where(language_filter)

        return stmt, count_stmt

    async def _cancel_executions(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
    ) -> None:
        """Cancel all executions for a suite run."""
        result = await db.execute(
            select(MultiTurnExecution).where(
                MultiTurnExecution.suite_run_id == suite_run_id
            )
        )
        executions = list(result.scalars().all())

        for execution in executions:
            task_id = self._get_celery_task_id(execution)
            if task_id:
                self._revoke_celery_task(task_id)

            if getattr(execution, "status", None) in {"pending", "running"}:
                execution.status = "skipped"
                execution.completed_at = datetime.utcnow()

    def _get_celery_task_id(self, execution: MultiTurnExecution) -> Optional[str]:
        """Extract Celery task ID from execution."""
        task_id = None
        if hasattr(execution, "get_context"):
            try:
                task_id = execution.get_context("celery_task_id")
            except Exception:
                task_id = None

        if not task_id:
            context = getattr(execution, "context", None)
            if isinstance(context, dict):
                task_id = context.get("celery_task_id")

        return task_id

    def _revoke_celery_task(self, task_id: str) -> None:
        """Revoke a Celery task."""
        try:
            from tasks.execution import execute_scenario
            async_result = execute_scenario.AsyncResult(task_id)
            async_result.revoke(terminate=True)
        except Exception:
            pass

    async def _get_failed_executions(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
    ) -> List[MultiTurnExecution]:
        """Get failed executions for a suite run."""
        result = await db.execute(
            select(MultiTurnExecution).where(
                MultiTurnExecution.suite_run_id == suite_run_id,
                MultiTurnExecution.status == "failed"
            )
        )
        return list(result.scalars().all())

    def _build_retry_payload(
        self,
        failed_executions: List[MultiTurnExecution],
    ) -> tuple[List[Dict[str, Any]], List[UUID]]:
        """Build payload for retrying failed executions."""
        execution_payload: List[Dict[str, Any]] = []
        retry_scenario_ids: List[UUID] = []

        for execution in failed_executions:
            scenario_id = getattr(execution, "script_id", None)
            if not scenario_id:
                continue

            language = self._extract_language(execution)

            execution_payload.append({
                "scenario_id": str(scenario_id),
                "language_code": language,
            })

            if scenario_id not in retry_scenario_ids:
                retry_scenario_ids.append(scenario_id)

        return execution_payload, retry_scenario_ids

    def _extract_language(self, execution: MultiTurnExecution) -> Optional[str]:
        """Extract language code from execution."""
        language = getattr(execution, "language_code", None)

        if not language and hasattr(execution, "get_context"):
            try:
                language = execution.get_context("language_code")
            except Exception:
                language = None

        if not language:
            context = getattr(execution, "context", None)
            if isinstance(context, dict):
                language = (
                    context.get("language_code")
                    or context.get("languageCode")
                    or context.get("language")
                )

        return language
