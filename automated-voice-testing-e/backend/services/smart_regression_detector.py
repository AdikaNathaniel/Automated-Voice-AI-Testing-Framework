"""
Smart Regression Detector Service

Handles regression detection with LLM non-determinism awareness:
- Tier 1: Deterministic metrics (strict gating) - command_kind_match, asr_confidence, etc.
- Tier 2: LLM final ensemble verdict (advisory, wide tolerances) - pass/fail only, NOT individual scores
- Tier 3: Suite-level aggregates (trend analysis)

This service integrates regression detection into suite execution, automatically
detecting and recording regressions after test runs complete.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.multi_turn_execution import MultiTurnExecution
from models.regression_baseline import RegressionBaseline
from services.regression_tracking_service import RegressionTrackingService

logger = logging.getLogger(__name__)


@dataclass
class RegressionFinding:
    """Represents a detected regression."""
    script_id: UUID
    category: str  # 'status', 'metric', or 'llm'
    detail: Dict[str, Any]
    severity: str = 'medium'


class SmartRegressionDetector:
    """
    Detects regressions with intelligent handling of LLM non-determinism.

    Key principles:
    - Deterministic metrics (command_kind_match, asr_confidence) use strict comparison
    - LLM final verdict (pass/fail) tracked with advisory status only
    - Individual LLM evaluator scores (relevance, correctness, tone) are IGNORED
    """

    # Metrics that are deterministic and suitable for strict regression gating
    DETERMINISTIC_METRICS = {
        'command_kind_match',
        'asr_confidence',
        'execution_success',
        'response_time_ms',
        'steps_completed',
    }

    # Success statuses for pass/fail determination
    SUCCESS_STATUSES = frozenset({'passed', 'success', 'completed'})

    def __init__(self, db: AsyncSession):
        """Initialize the detector with database session."""
        self.db = db
        self.tracking_service = RegressionTrackingService(db)

    async def detect_suite_regressions(
        self,
        suite_run_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> List[RegressionFinding]:
        """
        Detect regressions for all scenarios in a suite run.

        Args:
            suite_run_id: UUID of the completed suite run
            tenant_id: Optional tenant ID for scoping

        Returns:
            List of detected regressions
        """
        findings: List[RegressionFinding] = []

        # Get all executions for this suite run with tenant isolation
        stmt = select(MultiTurnExecution).where(
            MultiTurnExecution.suite_run_id == suite_run_id
        )

        # CRITICAL: Enforce tenant isolation if tenant_id is provided
        if tenant_id is not None:
            stmt = stmt.where(MultiTurnExecution.tenant_id == tenant_id)

        result = await self.db.execute(stmt)
        executions = result.scalars().all()

        logger.info(f"Analyzing {len(executions)} executions for regressions in suite {suite_run_id}")

        for execution in executions:
            # Get baseline for this scenario with tenant isolation
            baseline = await self._get_active_baseline(
                script_id=execution.script_id,
                tenant_id=execution.tenant_id  # Use execution's tenant_id for consistency
            )

            if not baseline:
                logger.debug(f"No baseline found for script {execution.script_id}, skipping")
                continue

            # Detect regressions for this execution
            execution_findings = await self._detect_execution_regressions(
                execution,
                baseline,
            )
            findings.extend(execution_findings)

            # Record or update regressions
            for finding in execution_findings:
                await self.tracking_service.record_regression(
                    finding=finding,
                    tenant_id=execution.tenant_id,  # Use execution's tenant_id
                    baseline_version=baseline.version,
                )

            # Auto-resolve if test is now passing
            if execution.status in self.SUCCESS_STATUSES:
                await self.tracking_service.auto_resolve_passing_tests(
                    script_id=execution.script_id
                )

        await self.db.commit()
        logger.info(f"Detected {len(findings)} regressions in suite {suite_run_id}")

        return findings

    async def _get_active_baseline(
        self,
        script_id: UUID,
        tenant_id: Optional[UUID] = None
    ) -> Optional[RegressionBaseline]:
        """
        Get the active baseline for a scenario script with tenant isolation.

        Args:
            script_id: UUID of the scenario script
            tenant_id: Optional tenant ID for multi-tenant isolation

        Returns:
            Active baseline or None if not found
        """
        stmt = (
            select(RegressionBaseline)
            .where(RegressionBaseline.script_id == script_id)
            .where(RegressionBaseline.is_active == True)
        )

        # CRITICAL: Enforce tenant isolation if tenant_id is provided
        if tenant_id is not None:
            stmt = stmt.where(RegressionBaseline.tenant_id == tenant_id)

        stmt = stmt.order_by(RegressionBaseline.version.desc())

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _detect_execution_regressions(
        self,
        execution: MultiTurnExecution,
        baseline: RegressionBaseline,
    ) -> List[RegressionFinding]:
        """
        Detect regressions for a single execution against its baseline.

        Tier 1: Check deterministic metrics (strict)
        Tier 2: Check LLM final verdict (advisory)
        """
        findings: List[RegressionFinding] = []

        # Extract metrics from execution
        current_metrics = self._extract_metrics(execution)
        baseline_metrics = baseline.snapshot_data.get('metrics', {}) if baseline.snapshot_data else {}

        # Tier 1: Status regression (deterministic)
        status_finding = self._check_status_regression(
            baseline_status=baseline.snapshot_data.get('status') if baseline.snapshot_data else None,
            current_status=execution.status,
            script_id=execution.script_id,
        )
        if status_finding:
            findings.append(status_finding)

        # Tier 1: Deterministic metric regressions (strict gating)
        metric_findings = self._check_deterministic_metrics(
            baseline_metrics=baseline_metrics,
            current_metrics=current_metrics,
            script_id=execution.script_id,
        )
        findings.extend(metric_findings)

        # Tier 2: LLM final verdict regression (advisory only)
        llm_finding = self._check_llm_verdict_regression(
            baseline_metrics=baseline_metrics,
            current_metrics=current_metrics,
            script_id=execution.script_id,
        )
        if llm_finding:
            findings.append(llm_finding)

        return findings

    def _extract_metrics(self, execution: MultiTurnExecution) -> Dict[str, Any]:
        """
        Extract relevant metrics from execution.

        IMPORTANT: Only extracts:
        - Deterministic metrics (command_kind_match, asr_confidence, etc.)
        - Final LLM ensemble verdict (pass/fail)
        - Does NOT extract individual LLM evaluator scores
        """
        metrics: Dict[str, Any] = {}

        if not execution.execution_metadata:
            return metrics

        metadata = execution.execution_metadata

        # Extract deterministic metrics
        for metric_name in self.DETERMINISTIC_METRICS:
            if metric_name in metadata:
                metrics[metric_name] = metadata[metric_name]

        # Extract LLM final verdict ONLY (not individual evaluator scores)
        # Look for ensemble result or final validation decision
        if 'llm_validation_result' in metadata:
            llm_result = metadata['llm_validation_result']
            if isinstance(llm_result, dict):
                # Only use final verdict/decision
                if 'final_verdict' in llm_result:
                    metrics['llm_final_verdict'] = llm_result['final_verdict']
                elif 'decision' in llm_result:
                    metrics['llm_final_verdict'] = llm_result['decision']

        # Extract step-level metrics (deterministic only)
        if 'steps' in metadata and isinstance(metadata['steps'], list):
            total_steps = len(metadata['steps'])
            completed_steps = sum(1 for step in metadata['steps'] if step.get('status') == 'completed')
            metrics['steps_completed'] = completed_steps / total_steps if total_steps > 0 else 0

        return metrics

    def _check_status_regression(
        self,
        baseline_status: Optional[str],
        current_status: str,
        script_id: UUID,
    ) -> Optional[RegressionFinding]:
        """
        Check for status regression (pass → fail).

        This is Tier 1: Deterministic, strict gating.
        """
        baseline_normalized = (baseline_status or '').strip().lower()
        current_normalized = (current_status or '').strip().lower()

        # Regression: baseline passed, current did not pass
        if (baseline_normalized in self.SUCCESS_STATUSES and
            current_normalized not in self.SUCCESS_STATUSES):
            return RegressionFinding(
                script_id=script_id,
                category='status',
                detail={
                    'baseline_status': baseline_status,
                    'current_status': current_status,
                    'message': f'Test status regressed from {baseline_status} to {current_status}',
                },
                severity='high',  # Status regressions are always high severity
            )

        return None

    def _check_deterministic_metrics(
        self,
        baseline_metrics: Dict[str, Any],
        current_metrics: Dict[str, Any],
        script_id: UUID,
    ) -> List[RegressionFinding]:
        """
        Check for regressions in deterministic metrics.

        This is Tier 1: Strict gating with tight tolerances.
        """
        findings: List[RegressionFinding] = []

        for metric_name in self.DETERMINISTIC_METRICS:
            if metric_name not in baseline_metrics or metric_name not in current_metrics:
                continue

            baseline_value = baseline_metrics[metric_name]
            current_value = current_metrics[metric_name]

            # Skip non-numeric metrics
            if not isinstance(baseline_value, (int, float)) or not isinstance(current_value, (int, float)):
                continue

            # Check for degradation (lower is worse for most metrics)
            # Use 5% tolerance for deterministic metrics
            tolerance = 0.05
            threshold = baseline_value * (1 - tolerance)

            if current_value < threshold:
                change_pct = ((current_value - baseline_value) / baseline_value * 100) if baseline_value != 0 else 0

                findings.append(RegressionFinding(
                    script_id=script_id,
                    category='metric',
                    detail={
                        'metric': metric_name,
                        'baseline_value': baseline_value,
                        'current_value': current_value,
                        'change': current_value - baseline_value,
                        'change_pct': change_pct,
                        'message': f'{metric_name} degraded by {abs(change_pct):.1f}%',
                    },
                    severity=self._determine_metric_severity(change_pct),
                ))

        return findings

    def _check_llm_verdict_regression(
        self,
        baseline_metrics: Dict[str, Any],
        current_metrics: Dict[str, Any],
        script_id: UUID,
    ) -> Optional[RegressionFinding]:
        """
        Check for LLM final verdict regression.

        This is Tier 2: Advisory only, NOT strict gating.
        Only looks at final ensemble verdict (pass/fail), NOT individual evaluator scores.
        """
        baseline_verdict = baseline_metrics.get('llm_final_verdict')
        current_verdict = current_metrics.get('llm_final_verdict')

        if not baseline_verdict or not current_verdict:
            return None

        baseline_normalized = str(baseline_verdict).strip().lower()
        current_normalized = str(current_verdict).strip().lower()

        # Check if verdict changed from pass to fail
        if (baseline_normalized in {'pass', 'passed', 'success'} and
            current_normalized in {'fail', 'failed', 'uncertain'}):
            return RegressionFinding(
                script_id=script_id,
                category='llm',
                detail={
                    'baseline_verdict': baseline_verdict,
                    'current_verdict': current_verdict,
                    'message': f'LLM verdict changed from {baseline_verdict} to {current_verdict} (advisory)',
                },
                severity='medium',  # LLM verdicts are advisory, not high severity
            )

        return None

    def _determine_metric_severity(self, change_pct: float) -> str:
        """Determine severity based on magnitude of metric degradation."""
        abs_change = abs(change_pct)

        if abs_change > 20:
            return 'high'
        elif abs_change > 10:
            return 'medium'
        else:
            return 'low'
