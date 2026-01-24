"""
Baseline management service (TASK-337).

Provides helpers to persist and retrieve regression baselines for scenario scripts.
Baselines are stored per script and refreshed whenever a new set of results
is approved by a reviewer. History is preserved for audit trail.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.regression_baseline import RegressionBaseline, BaselineHistory
from services.regression_detection_service import TestResultSnapshot


@dataclass(frozen=True)
class BaselineRecord:
    """Immutable view of a baseline along with approval metadata."""

    snapshot: TestResultSnapshot
    version: int
    approved_at: datetime
    approved_by: Optional[UUID]
    note: Optional[str]


@dataclass(frozen=True)
class BaselineHistoryRecord:
    """Immutable view of a historical baseline version."""

    version: int
    status: str
    metrics: Dict[str, object]
    approved_at: Optional[datetime]
    approved_by: Optional[UUID]
    note: Optional[str]


class BaselineManagementService:
    """Store and update regression baselines per scenario script."""

    def __init__(self, session: Session) -> None:
        if session is None:
            raise ValueError("BaselineManagementService requires a database session.")
        self._session = session

    def get_baseline(self, script_id: UUID) -> Optional[BaselineRecord]:
        """Return the approved baseline for a scenario script, if present."""
        baseline = self._session.execute(
            select(RegressionBaseline).where(
                RegressionBaseline.script_id == str(script_id)
            )
        ).scalar_one_or_none()
        if baseline is None:
            return None
        return self._to_record(baseline)

    def get_baseline_history(self, script_id: UUID) -> List[BaselineHistoryRecord]:
        """Return the history of baseline versions for a scenario script."""
        baseline = self._session.execute(
            select(RegressionBaseline).where(
                RegressionBaseline.script_id == str(script_id)
            )
        ).scalar_one_or_none()

        if baseline is None:
            return []

        history_records = []

        # First add the current version
        history_records.append(
            BaselineHistoryRecord(
                version=baseline.version,
                status=baseline.result_status,
                metrics=dict(baseline.metrics or {}),
                approved_at=baseline.approved_at,
                approved_by=(
                    UUID(baseline.approved_by) if baseline.approved_by else None
                ),
                note=baseline.note,
            )
        )

        # Then add archived history versions (ordered by version desc)
        for hist in baseline.history:
            history_records.append(
                BaselineHistoryRecord(
                    version=hist.version,
                    status=hist.result_status,
                    metrics=dict(hist.metrics or {}),
                    approved_at=hist.approved_at,
                    approved_by=(
                        UUID(hist.approved_by) if hist.approved_by else None
                    ),
                    note=hist.note,
                )
            )

        return history_records

    def approve_baseline(
        self,
        *,
        snapshot: TestResultSnapshot,
        approved_by: Optional[UUID],
        note: Optional[str] = None,
    ) -> BaselineRecord:
        """
        Persist an approved baseline snapshot for a scenario script.

        If a baseline already exists, the current version is archived to
        history before being updated. Version number is incremented.
        """
        baseline = self._session.execute(
            select(RegressionBaseline).where(
                RegressionBaseline.script_id == str(snapshot.script_id)
            )
        ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        approved_by_str = str(approved_by) if approved_by else None

        if baseline is None:
            # First baseline - no history to archive
            baseline = RegressionBaseline(
                script_id=str(snapshot.script_id),
                result_status=snapshot.status,
                metrics=self._coerce_metrics(snapshot.metrics),
                version=1,
                approved_by=approved_by_str,
                approved_at=now,
                note=note,
            )
            self._session.add(baseline)
        else:
            # Archive current state to history before updating
            history_record = baseline.archive_current()
            self._session.add(history_record)

            # Update to new version
            baseline.version += 1
            baseline.update_from_snapshot(
                status=snapshot.status,
                metrics=self._coerce_metrics(snapshot.metrics),
                approved_by=approved_by_str,
                approved_at=now,
                note=note,
            )

        self._session.commit()
        self._session.refresh(baseline)
        return self._to_record(baseline)

    def _to_record(self, baseline: RegressionBaseline) -> BaselineRecord:
        snapshot = TestResultSnapshot(
            script_id=UUID(baseline.script_id),
            status=baseline.result_status,
            metrics=dict(baseline.metrics or {}),
        )
        approved_by_uuid = UUID(baseline.approved_by) if baseline.approved_by else None
        return BaselineRecord(
            snapshot=snapshot,
            version=baseline.version,
            approved_at=baseline.approved_at or datetime.now(timezone.utc),
            approved_by=approved_by_uuid,
            note=baseline.note,
        )

    @staticmethod
    def _coerce_metrics(metrics: Dict[str, object] | None) -> Dict[str, object]:
        coerced: Dict[str, object] = {}
        if not metrics:
            return coerced
        for key, value in metrics.items():
            coerced[key] = float(value) if isinstance(value, (int, float)) else value
        return coerced

