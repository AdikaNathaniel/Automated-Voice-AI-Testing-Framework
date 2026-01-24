"""
Execution Scheduler Service

Manages test execution scheduling including:
- Scheduling test executions via Celery tasks
- Retrieving executions for a suite run
- Attaching validation metadata to executions
"""

import logging
from uuid import UUID
from typing import Optional, List, Dict, Any, NamedTuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from models.suite_run import SuiteRun
from models.scenario_script import ScenarioScript
from models.test_suite_scenario import TestSuiteScenario
from models.multi_turn_execution import MultiTurnExecution
from models.validation_result import ValidationResult
from models.validation_queue import ValidationQueue
from models.human_validation import HumanValidation
from celery_app import celery

logger = logging.getLogger(__name__)


class ExecutionConfig(NamedTuple):
    """Configuration for a single execution task."""
    script_id: UUID
    language_code: str


class ExecutionSchedulerService:
    """
    Service for scheduling and managing test executions.

    Handles scheduling Celery tasks for test execution and
    retrieving execution results with validation metadata.
    """

    async def schedule_test_executions(
        self,
        db: AsyncSession,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Schedule test executions for a suite run.

        Creates Celery tasks for each test case in the suite run,
        enabling parallel execution of tests.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run
            tenant_id: UUID of the tenant (optional)

        Returns:
            Dict containing:
                - suite_run_id: UUID of the suite run
                - scheduled_count: Number of tasks scheduled
                - task_ids: List of Celery task IDs

        Raises:
            ValueError: If suite_run_id is invalid
            RuntimeError: If suite run is not in pending status
        """
        logger.info(
            f"[SCHEDULER] Scheduling test executions - "
            f"suite_run_id={suite_run_id}, tenant_id={tenant_id}"
        )

        suite_run = await db.get(SuiteRun, suite_run_id)
        if not suite_run:
            logger.error(f"[SCHEDULER] Suite run not found: {suite_run_id}")
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if tenant_id and suite_run.tenant_id not in (None, tenant_id):
            logger.error(
                f"[SCHEDULER] Tenant mismatch - "
                f"suite_run.tenant_id={suite_run.tenant_id}, requested={tenant_id}"
            )
            raise ValueError(f"Suite run with ID {suite_run_id} not found")

        if suite_run.status != "pending":
            logger.error(
                f"[SCHEDULER] Invalid suite run status - "
                f"current={suite_run.status}, expected='pending'"
            )
            raise RuntimeError(
                f"Suite run status is {suite_run.status}, expected 'pending'"
            )

        logger.info(f"[SCHEDULER] Suite run validated - id={suite_run_id}, status={suite_run.status}")

        metadata = self._get_run_metadata(suite_run)
        execution_overrides = metadata.get("executions")

        if execution_overrides:
            logger.info(f"[SCHEDULER] Using execution overrides - count={len(execution_overrides)}")
            execution_configs = await self._prepare_execution_configs(
                db=db,
                suite_run=suite_run,
                override_configs=execution_overrides,
            )
        else:
            logger.info(f"[SCHEDULER] Creating execution configs from suite")
            execution_configs = await self._create_execution_configs_from_suite(
                db=db,
                suite_run=suite_run,
            )

        if not execution_configs:
            logger.error(f"[SCHEDULER] No executable scenarios found for suite_run_id={suite_run_id}")
            raise ValueError("No executable scenarios found for scheduling")

        logger.info(f"[SCHEDULER] Created {len(execution_configs)} execution configs")

        # Update suite run with total count
        suite_run.total_tests = len(execution_configs)

        logger.info(f"[SCHEDULER] Scheduling Celery tasks for {len(execution_configs)} executions")
        task_ids = await self._schedule_celery_tasks(
            suite_run_id, execution_configs
        )
        logger.info(f"[SCHEDULER] Scheduled {len(task_ids)} Celery tasks")

        suite_run.status = "running"
        suite_run.started_at = datetime.utcnow()
        await db.commit()
        logger.info(f"[SCHEDULER] Suite run status updated to 'running' - id={suite_run_id}")

        # Schedule aggregate_results task to run after executions complete
        # Use countdown of 60 seconds to allow voice tests to complete
        logger.info(f"[SCHEDULER] Scheduling aggregate_results task with 60s countdown")
        celery.send_task(
            'tasks.orchestration.aggregate_results',
            args=[str(suite_run_id), []],  # Pass empty list for execution_results - will be populated by monitor task
            countdown=60
        )

        result = {
            'suite_run_id': str(suite_run_id),
            'scheduled_count': len(task_ids),
            'task_ids': task_ids
        }
        logger.info(
            f"[SCHEDULER] Scheduling complete - "
            f"suite_run_id={suite_run_id}, scheduled_count={len(task_ids)}"
        )
        return result

    async def get_suite_run_executions(
        self,
        db: AsyncSession,
        *,
        suite_run_id: UUID,
        status_filter: Optional[str] = None,
    ) -> list[MultiTurnExecution]:
        """
        Retrieve executions for a given suite run with optional status filter.

        Eagerly loads step_executions for audio URLs and validation data.

        Args:
            db: Database session
            suite_run_id: UUID of the suite run
            status_filter: Optional status to filter by

        Returns:
            List of MultiTurnExecution instances with step_executions loaded
        """
        stmt = (
            select(MultiTurnExecution)
            .options(
                selectinload(MultiTurnExecution.step_executions),
                selectinload(MultiTurnExecution.script),
            )
            .where(MultiTurnExecution.suite_run_id == suite_run_id)
        )

        if status_filter:
            stmt = stmt.where(MultiTurnExecution.status == status_filter)

        stmt = stmt.order_by(MultiTurnExecution.created_at.asc())

        result = await db.execute(stmt)
        executions = list(result.scalars().all())

        if not executions:
            return []

        await self.attach_validation_metadata(db, executions)

        return executions

    async def attach_validation_metadata(
        self,
        db: AsyncSession,
        executions: List[MultiTurnExecution],
    ) -> None:
        """
        Attach validation metadata to executions.

        Args:
            db: Database session
            executions: List of executions to hydrate
        """
        execution_ids = [
            execution.id for execution in executions
            if getattr(execution, "id", None)
        ]
        if not execution_ids:
            return

        stmt = (
            select(ValidationResult)
            .options(
                selectinload(ValidationResult.queue_items),
                selectinload(ValidationResult.human_validations),
            )
            .where(ValidationResult.multi_turn_execution_id.in_(execution_ids))
        )
        result = await db.execute(stmt)
        validation_results = list(result.scalars().all())

        validation_map: Dict[UUID, ValidationResult] = {
            vr.multi_turn_execution_id: vr
            for vr in validation_results
            if getattr(vr, "multi_turn_execution_id", None)
        }

        for execution in executions:
            validation = validation_map.get(getattr(execution, "id"))
            if not validation:
                continue

            # Set validation_result - this enables the computed properties
            # pending_validation_queue_item and latest_human_validation
            # which are @property methods on MultiTurnExecution
            setattr(execution, "validation_result", validation)

    async def hydrate_run_language_metadata(
        self,
        db: AsyncSession,
        runs: List[SuiteRun],
    ) -> None:
        """
        Hydrate suite runs with language metadata from executions.

        Args:
            db: Database session
            runs: List of suite runs to hydrate
        """
        # Language is now stored in SuiteRun.trigger_metadata, not in MultiTurnExecution
        # This function is no longer needed as language is extracted from trigger_metadata
        # in the serialization code. Keeping as no-op for backwards compatibility.
        for run in runs:
            metadata = getattr(run, "trigger_metadata", None) or {}
            if not metadata:
                # Try to derive from languages array if present
                languages = metadata.get("languages", [])
                if languages and isinstance(languages, list) and len(languages) > 0:
                    setattr(run, "_derived_language_code", languages[0])
                else:
                    setattr(run, "_derived_language_code", metadata.get("language_code"))

    def resolve_run_languages(self, suite_run: SuiteRun) -> List[str]:
        """
        Determine which languages to execute for the given suite run.

        Args:
            suite_run: The suite run to resolve languages for

        Returns:
            List of language codes
        """
        metadata = getattr(suite_run, "trigger_metadata", {}) or {}
        configured = metadata.get("languages")

        if not configured:
            return ["en-US"]

        if isinstance(configured, str):
            cleaned = configured.strip()
            return [cleaned] if cleaned else ["en-US"]

        languages: List[str] = []
        for entry in configured:
            if not entry:
                continue
            value = str(entry).strip()
            if value:
                languages.append(value)

        return languages or ["en-US"]

    def _get_run_metadata(self, suite_run: SuiteRun) -> Dict[str, Any]:
        """Extract metadata from suite run."""
        metadata = getattr(suite_run, "trigger_metadata", None)
        if isinstance(metadata, dict):
            return dict(metadata)
        return {}

    async def _create_execution_configs_from_suite(
        self,
        db: AsyncSession,
        suite_run: SuiteRun,
    ) -> List[ExecutionConfig]:
        """Create execution configs from suite run suite."""
        if not suite_run.suite_id:
            return []

        from sqlalchemy import and_

        # Check if specific scenario_ids were provided in trigger_metadata
        metadata = self._get_run_metadata(suite_run)
        scenario_ids_str = metadata.get("scenario_ids")

        if scenario_ids_str:
            # Run only specific scenarios
            logger.info(f"[SCHEDULER] Running specific scenarios: {scenario_ids_str}")
            scenario_ids = [UUID(s_id) for s_id in scenario_ids_str]
            result = await db.execute(
                select(ScenarioScript).filter(
                    and_(
                        ScenarioScript.id.in_(scenario_ids),
                        ScenarioScript.is_active == True
                    )
                )
            )
        else:
            # Run all scenarios in the suite via TestSuiteScenario
            logger.info(f"[SCHEDULER] Running all scenarios in suite {suite_run.suite_id}")
            result = await db.execute(
                select(ScenarioScript)
                .join(
                    TestSuiteScenario,
                    ScenarioScript.id == TestSuiteScenario.scenario_id
                )
                .where(
                    and_(
                        TestSuiteScenario.suite_id == suite_run.suite_id,
                        ScenarioScript.is_active == True
                    )
                )
            )

        scenarios = list(result.scalars().all())

        if not scenarios:
            raise ValueError("No scenarios found for suite run")

        languages = self.resolve_run_languages(suite_run)

        configs: List[ExecutionConfig] = []
        for scenario in scenarios:
            for language_code in languages:
                configs.append(ExecutionConfig(
                    script_id=scenario.id,
                    language_code=language_code,
                ))

        return configs

    async def _prepare_execution_configs(
        self,
        db: AsyncSession,
        *,
        suite_run: SuiteRun,
        override_configs: List[Dict[str, Any]],
    ) -> List[ExecutionConfig]:
        """Prepare execution configs from override configuration."""
        if not override_configs:
            return []

        parsed_configs: List[Dict[str, Any]] = []
        scenario_ids: List[UUID] = []

        for config in override_configs:
            raw_scenario_id = config.get("scenario_id")
            if not raw_scenario_id:
                continue
            scenario_uuid = UUID(str(raw_scenario_id))
            scenario_ids.append(scenario_uuid)
            parsed_configs.append({
                "scenario_id": scenario_uuid,
                "language_code": (
                    config.get("language_code") or config.get("languageCode")
                ),
            })

        if not parsed_configs:
            return []

        result = await db.execute(
            select(ScenarioScript).where(ScenarioScript.id.in_(scenario_ids))
        )
        scenario_map = {scenario.id: scenario for scenario in result.scalars().all()}

        configs: List[ExecutionConfig] = []
        for config in parsed_configs:
            scenario = scenario_map.get(config["scenario_id"])
            if not scenario:
                raise ValueError(
                    f"Scenario {config['scenario_id']} not found for overrides"
                )

            languages = (
                [config["language_code"]] if config["language_code"]
                else self.resolve_run_languages(suite_run)
            )
            for language in languages:
                configs.append(ExecutionConfig(
                    script_id=scenario.id,
                    language_code=language,
                ))

        return configs

    async def _schedule_celery_tasks(
        self,
        suite_run_id: UUID,
        execution_configs: List[ExecutionConfig],
    ) -> List[str]:
        """Schedule Celery tasks for executions."""
        execute_scenario = self._get_execute_scenario()
        task_ids = []

        for config in execution_configs:
            task_config = {
                'suite_run_id': str(suite_run_id),
                'language_code': config.language_code,
            }
            task = execute_scenario.delay(
                str(config.script_id),
                language=config.language_code,
                config=task_config
            )
            task_ids.append(task.id)

        return task_ids

    def _get_execute_scenario(self):
        """Lazy import to avoid Celery initialization in tests."""
        from tasks.execution import execute_scenario
        return execute_scenario

    def _select_pending_queue_item(
        self,
        queue_items: List[ValidationQueue],
    ) -> Optional[ValidationQueue]:
        """Select pending queue item from list."""
        if not queue_items:
            return None

        prioritized = sorted(
            queue_items,
            key=lambda item: (
                0 if item.status == "pending" else (
                    1 if item.status == "claimed" else 2
                ),
                getattr(item, "created_at", None) or datetime.min,
            ),
        )

        for item in prioritized:
            if item.status in {"pending", "claimed"}:
                return item
        return None

    def _select_latest_human_validation(
        self,
        human_validations: List[HumanValidation],
    ) -> Optional[HumanValidation]:
        """Select latest human validation from list."""
        if not human_validations:
            return None

        submitted = [
            hv for hv in human_validations
            if getattr(hv, "submitted_at", None)
        ]
        if submitted:
            submitted.sort(key=lambda hv: getattr(hv, "submitted_at"))
            return submitted[-1]

        claimed = [
            hv for hv in human_validations
            if getattr(hv, "claimed_at", None)
        ]
        if claimed:
            claimed.sort(key=lambda hv: getattr(hv, "claimed_at"))
            return claimed[-1]

        return human_validations[-1]
