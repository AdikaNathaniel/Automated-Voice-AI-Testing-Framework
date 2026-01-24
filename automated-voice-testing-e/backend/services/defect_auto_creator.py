"""
Automatic defect creation helper for repeated validation failures (TASK-241).

This module provides the `DefectAutoCreator` class which tracks consecutive
automatic validation failures for each scenario script and raises a defect once
the configured streak threshold is reached.

Updated to use script_id (ScenarioScript) instead of test_case_id (TestCase).

The failure threshold is configurable via the 3-tier settings hierarchy:
1. Organization-specific setting (pattern_analysis_configs.defect_auto_creation_threshold)
2. Global default (pattern_analysis_configs with tenant_id=NULL)
3. .env default (DEFECT_AUTO_CREATION_THRESHOLD, defaults to 3)

Example usage with configurable threshold:
    from services.settings_manager import SettingsManager
    from services.defect_auto_creator import DefectAutoCreator, get_defect_threshold

    # Get threshold from settings
    threshold = await get_defect_threshold(db, tenant_id)

    # Create DefectAutoCreator with configurable threshold
    defect_creator = DefectAutoCreator(
        create_defect=create_defect_func,
        failure_threshold=threshold,
        categorizer=categorizer
    )
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Optional, Tuple, TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DefectAutoCreator:
    """
    Track repeated validation failures and create defects automatically.

    Args:
        create_defect: Coroutine function responsible for persisting the defect.
            It must accept a single keyword argument `data` containing the payload.
        failure_threshold: Number of consecutive automatic failures required
            before a defect is created.
        clock: Optional callable returning the current time (UTC). Primarily
            used to stabilise timestamps in unit tests.
        redis_client: Optional Redis client for persistent streak storage.
            If not provided, uses in-memory storage (not recommended for production).
    """

    # Redis key prefix for failure streaks
    REDIS_KEY_PREFIX = "defect_auto_creator:streak:"

    def __init__(
        self,
        *,
        create_defect: Callable[..., Awaitable[Any]],
        failure_threshold: int = 3,
        clock: Optional[Callable[[], datetime]] = None,
        categorizer: Optional[Any] = None,
        redis_client: Optional[Any] = None,
    ) -> None:
        if failure_threshold <= 0:
            raise ValueError("failure_threshold must be positive")
        if create_defect is None:
            raise ValueError("create_defect callable is required")

        self._create_defect = create_defect
        self._failure_threshold = failure_threshold
        self._clock = clock or _utc_now
        self._categorizer = categorizer
        self._redis_client = redis_client
        # CRITICAL: Key by (tenant_id, script_id) tuple for proper multi-tenant isolation
        # Used as fallback when Redis is not available
        self._failure_streaks: Dict[Tuple[Optional[UUID], UUID], int] = {}

    def _get_redis_key(self, tenant_id: Optional[UUID], script_id: UUID) -> str:
        """Generate Redis key for failure streak."""
        tenant_str = str(tenant_id) if tenant_id else "global"
        return f"{self.REDIS_KEY_PREFIX}{tenant_str}:{script_id}"

    async def _get_streak(self, tenant_id: Optional[UUID], script_id: UUID) -> int:
        """Get current failure streak from Redis or memory."""
        streak_key = (tenant_id, script_id)

        if self._redis_client:
            try:
                redis_key = self._get_redis_key(tenant_id, script_id)
                value = await self._redis_client.get(redis_key)
                if value:
                    return int(value)
                return 0
            except Exception as e:
                logger.warning(f"Redis get failed, using memory fallback: {e}")
                return self._failure_streaks.get(streak_key, 0)
        else:
            return self._failure_streaks.get(streak_key, 0)

    async def _set_streak(self, tenant_id: Optional[UUID], script_id: UUID, value: int) -> None:
        """Set failure streak in Redis or memory. Streaks expire after 7 days."""
        streak_key = (tenant_id, script_id)

        if self._redis_client:
            try:
                redis_key = self._get_redis_key(tenant_id, script_id)
                if value == 0:
                    await self._redis_client.delete(redis_key)
                else:
                    # Expire after 7 days - if no failures in 7 days, reset streak
                    await self._redis_client.set(redis_key, str(value), ttl=7 * 24 * 3600)
            except Exception as e:
                logger.warning(f"Redis set failed, using memory fallback: {e}")
                if value == 0:
                    self._failure_streaks.pop(streak_key, None)
                else:
                    self._failure_streaks[streak_key] = value
        else:
            if value == 0:
                self._failure_streaks.pop(streak_key, None)
            else:
                self._failure_streaks[streak_key] = value

    async def record_validation_outcome(
        self,
        *,
        execution: Any,
        validation_result: Any,
        review_status: str,
    ) -> Optional[Any]:
        """
        Record a validation outcome and auto-create a defect if threshold reached.

        CRITICAL: Failure streaks are now keyed by (tenant_id, script_id) to ensure
        proper multi-tenant isolation and prevent cross-tenant failure counts.

        Uses Redis for persistent streak storage across server restarts and workers.
        """
        script_id = self._resolve_script_id(execution)
        if script_id is None:
            logger.warning("Cannot record validation outcome: script_id not found")
            return None

        # CRITICAL: Get tenant_id for multi-tenant isolation
        tenant_id = self._resolve_tenant_id(execution)

        if review_status != "auto_fail":
            # Reset streak on any non-failure status.
            await self._set_streak(tenant_id, script_id, 0)
            logger.debug(f"Reset failure streak for script {script_id} (status: {review_status})")
            return None

        # Increment streak
        current_streak = await self._get_streak(tenant_id, script_id)
        new_streak = current_streak + 1
        await self._set_streak(tenant_id, script_id, new_streak)

        logger.info(
            f"Failure streak for script {script_id}: {new_streak}/{self._failure_threshold} "
            f"(review_status: {review_status})"
        )

        if new_streak < self._failure_threshold:
            return None

        # Threshold reached; reset counter before creating the defect.
        logger.info(f"Defect threshold reached for script {script_id} after {new_streak} consecutive failures")
        await self._set_streak(tenant_id, script_id, 0)

        payload = self._build_defect_payload(
            execution=execution,
            validation_result=validation_result,
            script_id=script_id,
            failure_count=new_streak,
            tenant_id=tenant_id,
        )
        return await self._create_defect(data=payload)

    def _resolve_script_id(self, execution: Any) -> Optional[UUID]:
        """Resolve the script_id from a MultiTurnExecution or similar."""
        direct = getattr(execution, "script_id", None)
        if isinstance(direct, UUID):
            return direct

        # Fall back to audio params stored in execution context.
        if hasattr(execution, "get_audio_param"):
            raw = execution.get_audio_param("script_id")
            if raw:
                try:
                    return UUID(str(raw))
                except (ValueError, TypeError):
                    pass
        return None

    def _resolve_tenant_id(self, execution: Any) -> Optional[UUID]:
        """
        Resolve the tenant_id from a MultiTurnExecution or similar.

        CRITICAL: This ensures proper multi-tenant isolation in failure streak tracking.
        """
        direct = getattr(execution, "tenant_id", None)
        if isinstance(direct, UUID):
            return direct

        # Fall back to execution context if available
        if hasattr(execution, "get_audio_param"):
            raw = execution.get_audio_param("tenant_id")
            if raw:
                try:
                    return UUID(str(raw))
                except (ValueError, TypeError):
                    pass
        return None

    def _resolve_language_code(self, execution: Any) -> Optional[str]:
        """
        Resolve language code from execution.

        Tries multiple sources:
        1. Direct language_code attribute
        2. get_audio_param method
        3. Step executions' audio_data_urls keys (e.g., {"en-US": "http://..."})
        """
        # Try direct attribute
        language = getattr(execution, "language_code", None)
        if isinstance(language, str) and language.strip():
            return language.strip()

        # Try get_audio_param method
        if hasattr(execution, "get_audio_param"):
            raw = execution.get_audio_param("language_code")
            if isinstance(raw, str) and raw.strip():
                return raw.strip()

        # Try to extract from step_executions audio_data_urls
        step_executions = getattr(execution, "step_executions", None)
        if step_executions:
            for step in step_executions:
                audio_urls = getattr(step, "audio_data_urls", None)
                if audio_urls and isinstance(audio_urls, dict):
                    # Return first language code found
                    for lang_code in audio_urls.keys():
                        if isinstance(lang_code, str) and lang_code.strip():
                            return lang_code.strip()

        return None

    def _build_defect_payload(
        self,
        *,
        execution: Any,
        validation_result: Any,
        script_id: UUID,
        failure_count: int,
        tenant_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        detected_at = self._ensure_timezone(self._clock())
        accuracy = self._format_score(getattr(validation_result, "accuracy_score", None))
        confidence = self._format_score(getattr(validation_result, "confidence_score", None))
        category = self._categorize(execution=execution, validation_result=validation_result)

        # Get scenario name if available
        # Try multiple ways to get the scenario name:
        # 1. Direct attribute (if set by caller)
        # 2. Via script relationship (execution.script.name)
        # 3. Fall back to script_id
        scenario_name = getattr(execution, "script_name", None)
        if not scenario_name:
            # Try to get from relationship
            script = getattr(execution, "script", None)
            if script:
                scenario_name = getattr(script, "name", None)
        if not scenario_name:
            scenario_name = str(script_id)

        description = (
            f"Automatic defect detected after {failure_count} consecutive auto_fail results.\n"
            f"- Accuracy: {accuracy}\n"
            f"- Confidence: {confidence}\n"
        )

        payload: Dict[str, Any] = {
            "script_id": script_id,
            "execution_id": getattr(execution, "id", None),
            "tenant_id": tenant_id,
            "severity": "high",
            "category": category,
            "title": f"Repeated failure detected for scenario: {scenario_name}",
            "description": description,
            "language_code": self._resolve_language_code(execution),
            "detected_at": detected_at,
            "status": "open",
        }
        return payload

    def _categorize(self, *, execution: Any, validation_result: Any) -> str:
        if self._categorizer is None:
            return "uncategorized"
        try:
            category = self._categorizer.categorize(
                execution=execution,
                validation_result=validation_result,
            )
        except Exception:  # pragma: no cover - defensive guard
            return "uncategorized"
        if not isinstance(category, str) or not category.strip():
            return "uncategorized"
        return category.strip()

    @staticmethod
    def _ensure_timezone(value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _format_score(value: Any) -> str:
        if isinstance(value, (int, float)):
            return f"{float(value) * 100:.1f}%"
        return "unknown"


async def get_defect_threshold(
    db: "AsyncSession",
    tenant_id: Optional[UUID] = None
) -> int:
    """
    Get defect auto-creation threshold from settings hierarchy.

    Retrieves the threshold following the 3-tier hierarchy:
    1. Organization-specific setting (if tenant_id provided)
    2. Global default (tenant_id = NULL)
    3. .env default (DEFECT_AUTO_CREATION_THRESHOLD, defaults to 3)

    Args:
        db: Database session
        tenant_id: Organization/tenant UUID (optional)

    Returns:
        Defect auto-creation threshold (minimum: 1)

    Example:
        >>> async with get_db() as db:
        ...     threshold = await get_defect_threshold(db, tenant_id)
        ...     creator = DefectAutoCreator(
        ...         create_defect=func,
        ...         failure_threshold=threshold
        ...     )
    """
    from services.settings_manager import SettingsManager

    manager = SettingsManager(db)
    threshold = await manager.get_pattern_analysis_setting(
        'defect_auto_creation_threshold',
        tenant_id,
        default=3
    )

    # Ensure threshold is at least 1
    return max(1, int(threshold))
