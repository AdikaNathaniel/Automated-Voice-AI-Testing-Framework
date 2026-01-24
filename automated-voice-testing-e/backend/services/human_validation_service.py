"""
Human validation service helpers for submitting validator decisions.
"""

from __future__ import annotations

import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.human_validation import HumanValidation
from models.validation_queue import ValidationQueue
from models.validation_result import ValidationResult
from models.validator_performance import ValidatorPerformance
from models.edge_case import EdgeCase
from services.validation_queue_service import ValidationQueueService
from services.edge_case_detection_service import EdgeCaseDetectionService

logger = logging.getLogger(__name__)


class HumanValidationService:
    """
    Handles submission of human validation decisions and related bookkeeping.
    """

    def __init__(
        self,
        queue_service: Optional[ValidationQueueService] = None,
        detection_service: Optional[EdgeCaseDetectionService] = None
    ) -> None:
        self.queue_service = queue_service or ValidationQueueService()
        self.detection_service = detection_service or EdgeCaseDetectionService()

    async def submit_decision(
        self,
        db: AsyncSession,
        queue_id: UUID,
        validator_id: UUID,
        validation_data: Any,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """
        Persist a human validation decision and update queue + performance metrics.
        """
        queue_item = await self._get_queue_item(db, queue_id, tenant_id=tenant_id)
        self._ensure_queue_claim(queue_item, validator_id)

        submitted_at = datetime.utcnow()
        human_validation = HumanValidation(
            validation_result_id=queue_item.validation_result_id,
            validator_id=validator_id,
            tenant_id=tenant_id,  # Add tenant_id from function parameter
            claimed_at=queue_item.claimed_at or submitted_at,
            submitted_at=submitted_at,
            validation_decision=validation_data.validation_decision,
            feedback=validation_data.feedback,
            time_spent_seconds=validation_data.time_spent_seconds,
            is_second_opinion=False,
        )
        db.add(human_validation)

        queue_item.status = "completed"

        await self._update_validator_performance(
            db=db,
            validator_id=validator_id,
            time_spent_seconds=validation_data.time_spent_seconds,
        )

        # Auto-create edge case if decision is "edge_case"
        edge_case_id = None
        edge_case_data = None
        if validation_data.validation_decision == "edge_case":
            edge_case = await self._create_edge_case_entry(
                db=db,
                queue_item=queue_item,
                validator_id=validator_id,
                feedback=validation_data.feedback,
                human_validation_id=human_validation.id,
            )
            edge_case_id = str(edge_case.id)
            # Capture data for notification before commit
            edge_case_data = {
                "id": str(edge_case.id),
                "title": edge_case.title,
                "category": edge_case.category,
                "severity": edge_case.severity,
                "scenario_name": edge_case.scenario_definition.get("scenario_name"),
                "description": validation_data.feedback,
            }

        # Auto-create defect if decision is "create_defect"
        # Note: For metrics, this counts as "fail" (see dashboard_service.py)
        defect_id = None
        if validation_data.validation_decision == "create_defect":
            defect = await self._create_defect_from_validation(
                db=db,
                queue_item=queue_item,
                feedback=validation_data.feedback,
                tenant_id=tenant_id,
            )
            defect_id = str(defect.id)

        await db.commit()
        await db.refresh(human_validation)

        # Send notification for edge case (after commit, non-blocking)
        if edge_case_data:
            await self._send_edge_case_notification(db, edge_case_data, tenant_id)

        result = {
            "queue_id": str(queue_id),
            "validator_id": str(validator_id),
            "decision": validation_data.validation_decision,
            "time_spent_seconds": validation_data.time_spent_seconds,
            "human_validation_id": str(human_validation.id),
        }

        if edge_case_id:
            result["edge_case_id"] = edge_case_id

        if defect_id:
            result["defect_id"] = defect_id

        return result

    async def _get_queue_item(
        self,
        db: AsyncSession,
        queue_id: UUID,
        tenant_id: Optional[UUID] = None,
    ) -> ValidationQueue:
        stmt = select(ValidationQueue).where(ValidationQueue.id == queue_id)
        if tenant_id:
            # Join with ValidationResult to filter by tenant_id
            stmt = stmt.join(
                ValidationResult,
                ValidationQueue.validation_result_id == ValidationResult.id
            ).where(
                ValidationResult.tenant_id == tenant_id
            )
        result = await db.execute(stmt)
        queue_item = result.scalar_one_or_none()
        if not queue_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Validation task not found",
            )
        return queue_item

    @staticmethod
    def _ensure_queue_claim(queue_item: ValidationQueue, validator_id: UUID) -> None:
        if queue_item.claimed_by != validator_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Validation task is not claimed by current user",
            )
        if queue_item.status != "claimed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Validation task is not currently claimed",
            )

    async def _update_validator_performance(
        self,
        db: AsyncSession,
        validator_id: UUID,
        time_spent_seconds: Optional[int],
    ) -> None:
        today = date.today()
        result = await db.execute(
            select(ValidatorPerformance).where(
                ValidatorPerformance.validator_id == validator_id,
                ValidatorPerformance.date == today,
            )
        )
        performance = result.scalar_one_or_none()
        if performance is None:
            performance = ValidatorPerformance(
                validator_id=validator_id,
                date=today,
                validations_completed=0,
                average_time_seconds=None,
            )
            db.add(performance)

        completed_before = performance.validations_completed or 0
        performance.validations_completed = completed_before + 1

        if time_spent_seconds is not None:
            new_time = Decimal(time_spent_seconds)
            if performance.average_time_seconds is None or completed_before == 0:
                performance.average_time_seconds = new_time
            else:
                total_time = Decimal(performance.average_time_seconds) * Decimal(completed_before)
                performance.average_time_seconds = (total_time + new_time) / Decimal(completed_before + 1)

    async def _create_edge_case_entry(
        self,
        db: AsyncSession,
        queue_item: ValidationQueue,
        validator_id: UUID,
        feedback: Optional[str],
        human_validation_id: UUID,
    ) -> EdgeCase:
        """
        Automatically create an edge case library entry from validation decision.

        Args:
            db: Database session
            queue_item: The validation queue item being validated
            validator_id: ID of the validator who marked it as edge case
            feedback: Optional feedback from validator
            human_validation_id: ID of the human validation record

        Returns:
            EdgeCase: Created edge case record
        """
        # Get validation result with relationships
        result = await db.execute(
            select(ValidationResult).where(
                ValidationResult.id == queue_item.validation_result_id
            )
        )
        validation_result = result.scalar_one()

        # Load relationships
        await db.refresh(validation_result, ["multi_turn_execution", "step_execution", "expected_outcome"])
        multi_turn_execution = validation_result.multi_turn_execution
        await db.refresh(multi_turn_execution, ["script"])
        scenario = multi_turn_execution.script

        # Get step execution data
        step_execution = validation_result.step_execution
        step_order = step_execution.step_order if step_execution else 0
        user_utterance = step_execution.user_utterance if step_execution else ""
        actual_response = step_execution.ai_response if step_execution else ""

        # Get expected criteria from expected outcome
        expected_command_kind = None
        expected_response_content = None
        expected_asr_confidence_min = None
        forbidden_phrases = None

        if validation_result.expected_outcome:
            expected_command_kind = getattr(validation_result.expected_outcome, 'expected_command_kind', None)
            expected_response_content = getattr(validation_result.expected_outcome, 'expected_response_content', None)
            expected_asr_confidence_min = getattr(validation_result.expected_outcome, 'expected_asr_confidence_min', None)
            forbidden_phrases = getattr(validation_result.expected_outcome, 'forbidden_phrases', None)

        # Get validation results
        command_kind_match = validation_result.command_kind_match_score
        houndify_passed = validation_result.houndify_passed
        llm_passed = validation_result.llm_passed
        final_decision = validation_result.final_decision

        # Get language code
        language_code = queue_item.language_code or validation_result.language_code or (multi_turn_execution.language_code if hasattr(multi_turn_execution, 'language_code') else None)

        # Auto-generate title
        title = f"Edge Case: {scenario.name} - Step {step_order}"

        # Build comprehensive scenario definition with actual validation criteria
        scenario_definition = {
            "scenario_id": str(scenario.id),
            "scenario_name": scenario.name,
            "scenario_description": scenario.description,
            "step_order": step_order,
            "user_utterance": user_utterance,
            "actual_response": actual_response,
            "language_code": language_code,
            # Validation criteria (what was expected)
            "expected_command_kind": expected_command_kind,
            "expected_response_content": expected_response_content,
            "expected_asr_confidence_min": expected_asr_confidence_min,
            "forbidden_phrases": forbidden_phrases,
            # Validation results (what happened)
            "command_kind_match_score": command_kind_match,
            "asr_confidence_score": validation_result.asr_confidence_score,
            "houndify_passed": houndify_passed,
            "llm_passed": llm_passed,
            "final_decision": final_decision,
            "review_status": validation_result.review_status,
            # References
            "validation_result_id": str(validation_result.id),
            "human_validation_id": str(human_validation_id),
            "multi_turn_execution_id": str(multi_turn_execution.id),
        }

        # Detect category and severity
        category = await self.detection_service.detect_category(validation_result)
        severity = self.detection_service.determine_severity(validation_result, category)

        # Generate tags
        tags = await self.detection_service.generate_tags(validation_result, db)

        # Create edge case
        edge_case = EdgeCase(
            title=title,
            description=feedback or f"Automatically created from human validation. Validator feedback: (none provided)",
            scenario_definition=scenario_definition,
            tags=tags,
            severity=severity,
            category=category,
            status="new",
            script_id=scenario.id,
            discovered_date=date.today(),
            discovered_by=validator_id,
            tenant_id=validation_result.tenant_id,  # Add tenant_id from validation result
            human_validation_id=human_validation_id,
            validation_result_id=validation_result.id,
            auto_created=True,
        )

        db.add(edge_case)
        # Don't commit here - let the caller handle transaction

        return edge_case

    async def _send_edge_case_notification(
        self,
        db: AsyncSession,
        edge_case_data: Dict[str, Any],
        tenant_id: Optional[UUID] = None,
    ) -> None:
        """
        Send Slack notification for newly created edge case.

        Uses tenant-specific notification config if tenant_id is provided,
        otherwise falls back to global settings.

        Notification is non-blocking - errors are logged but don't fail the flow.

        Args:
            db: Database session for looking up tenant config
            edge_case_data: Dictionary with edge case details for notification
            tenant_id: Optional tenant ID for tenant-specific notifications
        """
        try:
            from api.config import get_settings
            from services.notification_service import (
                get_notification_service,
                get_tenant_notification_service,
                should_send_notification,
            )

            settings = get_settings()

            edge_case_url = (
                f"{settings.FRONTEND_URL}/edge-cases/{edge_case_data['id']}"
            )

            # Try tenant-specific config first, fall back to global
            if tenant_id:
                notification_service, preferences = await get_tenant_notification_service(
                    db, tenant_id
                )
                # Check if tenant has edge case notifications enabled
                should_send, pref_channel = should_send_notification(
                    preferences,
                    "edgeCase",
                    severity=edge_case_data["severity"],
                )
                if not should_send:
                    logger.debug(
                        "Edge case notification disabled for tenant %s",
                        tenant_id,
                    )
                    return
                channel = pref_channel
            else:
                # Fall back to global config
                notification_service = get_notification_service()
                channel = settings.SLACK_EDGE_CASE_CHANNEL or settings.SLACK_ALERT_CHANNEL

            await notification_service.notify_edge_case_created(
                edge_case_id=edge_case_data["id"],
                title=edge_case_data["title"],
                category=edge_case_data["category"],
                severity=edge_case_data["severity"],
                edge_case_url=edge_case_url,
                scenario_name=edge_case_data.get("scenario_name"),
                description=edge_case_data.get("description"),
                channel=channel,
            )
        except Exception as exc:
            # Log but don't fail - notification is non-critical
            logger.warning(
                "Failed to send edge case notification for %s: %s",
                edge_case_data.get("id"),
                exc,
            )

    async def _create_defect_from_validation(
        self,
        db: AsyncSession,
        queue_item: ValidationQueue,
        feedback: Optional[str],
        tenant_id: Optional[UUID] = None,
    ):
        """
        Automatically create a defect from validation decision.

        Args:
            db: Database session
            queue_item: The validation queue item being validated
            feedback: Optional feedback from validator
            tenant_id: Tenant ID for multi-tenancy isolation

        Returns:
            Defect: Created defect record
        """
        from models.defect import Defect
        from models.multi_turn_execution import MultiTurnExecution
        from datetime import datetime, timezone

        # Get validation result with relationships
        result = await db.execute(
            select(ValidationResult).where(
                ValidationResult.id == queue_item.validation_result_id
            )
        )
        validation_result = result.scalar_one()

        # Load relationships
        await db.refresh(validation_result, ["multi_turn_execution"])
        multi_turn_execution = validation_result.multi_turn_execution
        await db.refresh(multi_turn_execution, ["script", "step_executions"])
        scenario = multi_turn_execution.script

        # Extract language code from step executions
        language_code = None
        if multi_turn_execution.step_executions:
            for step in multi_turn_execution.step_executions:
                audio_urls = getattr(step, "audio_data_urls", None)
                if audio_urls and isinstance(audio_urls, dict):
                    for lang_code in audio_urls.keys():
                        if isinstance(lang_code, str) and lang_code.strip():
                            language_code = lang_code.strip()
                            break
                if language_code:
                    break

        # Generate title
        title = f"Manual defect: {scenario.name}"
        if feedback:
            # Use first line of feedback as part of title if provided
            feedback_line = feedback.split('\n')[0][:50]
            title = f"Manual defect: {scenario.name} - {feedback_line}"

        # Build description
        description = feedback or "Defect created during human validation review."
        description += f"\n\nValidation Result ID: {validation_result.id}"

        # Create defect
        defect = Defect(
            tenant_id=tenant_id or validation_result.tenant_id,
            script_id=scenario.id,
            execution_id=multi_turn_execution.id,
            suite_run_id=multi_turn_execution.suite_run_id,
            severity="medium",  # Default severity, can be changed later
            category="uncategorized",  # Default category, can be changed later
            title=title,
            description=description,
            language_code=language_code,
            detected_at=datetime.now(timezone.utc),
            status="open",
        )

        db.add(defect)
        # Don't commit here - let the caller handle transaction

        return defect
