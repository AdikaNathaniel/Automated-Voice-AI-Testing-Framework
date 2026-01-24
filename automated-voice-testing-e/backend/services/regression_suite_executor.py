"""
Automatic regression suite execution helpers (TASK-339).

Provides utilities to resolve regression test suites and trigger full
executions via the orchestration service whenever automation is enabled.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.test_suite import TestSuite
from services import orchestration_service


class RegressionSuiteExecutor:
    """Coordinate automatic execution of regression test suites."""

    def __init__(
        self,
        *,
        db: AsyncSession,
        settings: Any,
        run_creator: Optional[Any] = None,
    ) -> None:
        if db is None:
            raise ValueError("RegressionSuiteExecutor requires a database session.")
        if settings is None:
            raise ValueError("RegressionSuiteExecutor requires application settings.")

        self._db = db
        self._settings = settings
        self._create_suite_run = run_creator or orchestration_service.create_suite_run

    async def execute(
        self,
        *,
        trigger: str,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Execute the regression suite based on configuration and metadata.
        """
        if not getattr(self._settings, "ENABLE_AUTO_REGRESSION", False):
            return {"status": "disabled"}

        suite_ids = await self._resolve_suite_ids(metadata)
        if not suite_ids:
            return {"status": "skipped", "reason": "no_regression_suites"}

        trigger_metadata = self._build_trigger_metadata(trigger, metadata, suite_ids)

        runs = []
        for suite_id in suite_ids:
            run = await self._create_suite_run(
                db=self._db,
                suite_id=suite_id,
                trigger_type=f"auto:{trigger}",
                trigger_metadata=trigger_metadata,
            )
            run_id = getattr(run, "id", None)
            total_tests = getattr(run, "total_tests", None)
            runs.append(
                {
                    "suite_id": str(suite_id),
                    "suite_run_id": str(run_id) if run_id else None,
                    "total_tests": total_tests,
                }
            )

        return {
            "status": "scheduled",
            "trigger": trigger,
            "runs": runs,
        }

    async def _resolve_suite_ids(self, metadata: Optional[Mapping[str, Any]]) -> list[UUID]:
        resolved: list[UUID] = []
        meta = metadata or {}

        # Direct identifiers from metadata payload
        for key in ("regression_suite_id", "suite_id"):
            candidate = self._coerce_uuid(meta.get(key))
            if candidate:
                resolved.append(candidate)

        # Explicit list provided in metadata
        meta_ids = meta.get("regression_suite_ids") or []
        if isinstance(meta_ids, Iterable) and not isinstance(meta_ids, (str, bytes)):
            for value in meta_ids:
                candidate = self._coerce_uuid(value)
                if candidate:
                    resolved.append(candidate)

        # Settings-provided fallback
        settings_ids = getattr(self._settings, "REGRESSION_SUITE_IDS", []) or []
        if isinstance(settings_ids, Iterable) and not isinstance(settings_ids, (str, bytes)):
            for value in settings_ids:
                candidate = self._coerce_uuid(value)
                if candidate:
                    resolved.append(candidate)
        elif isinstance(settings_ids, (str, bytes)):
            candidate = self._coerce_uuid(settings_ids)
            if candidate:
                resolved.append(candidate)

        if not resolved:
            db_ids = await self._fetch_regression_suite_ids_from_db()
            resolved.extend(db_ids)

        # Remove duplicates while preserving order
        unique: list[UUID] = []
        seen: set[UUID] = set()
        for suite_id in resolved:
            if suite_id not in seen:
                seen.add(suite_id)
                unique.append(suite_id)

        return unique

    async def _fetch_regression_suite_ids_from_db(self) -> list[UUID]:
        """
        Retrieve active regression suites from the database.

        Regression suites are identified by either their category or name.
        """
        stmt = (
            select(TestSuite.id)
            .where(
                TestSuite.is_active.is_(True),
                or_(
                    func.lower(TestSuite.category) == "regression",
                    func.lower(TestSuite.name).like("%regression%"),
                ),
            )
            .order_by(TestSuite.created_at.asc())
        )

        result = await self._db.execute(stmt)
        suite_ids = result.scalars().all()

        normalized: list[UUID] = []
        for item in suite_ids:
            if isinstance(item, UUID):
                normalized.append(item)
            else:
                try:
                    normalized.append(UUID(str(item)))
                except (TypeError, ValueError):
                    continue
        return normalized

    @staticmethod
    def _coerce_uuid(value: Any) -> Optional[UUID]:
        if value is None:
            return None
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _stringify(value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, Mapping):
            return {str(k): RegressionSuiteExecutor._stringify(v) for k, v in value.items()}
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
            return [RegressionSuiteExecutor._stringify(item) for item in value]
        return str(value)

    def _build_trigger_metadata(
        self,
        trigger: str,
        metadata: Optional[Mapping[str, Any]],
        suite_ids: list[UUID],
    ) -> dict[str, Any]:
        payload = {
            "trigger": trigger,
            "suite_ids": [str(item) for item in suite_ids],
        }
        if metadata:
            payload["source"] = {
                str(key): self._stringify(value) for key, value in metadata.items()
            }
        return payload
