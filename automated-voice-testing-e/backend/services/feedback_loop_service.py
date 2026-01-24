"""
Feedback loop service for incorporating human validation overrides into the
continuous learning pipeline.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID

from ml import TrainingDataCollector, TrainingDataSample


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FeedbackLoopService:
    """
    Coordinate capture of human validation overrides and schedule retraining.
    """

    def __init__(
        self,
        *,
        collector: Optional[TrainingDataCollector] = None,
        retrain_threshold: int = 50,
    ) -> None:
        if retrain_threshold <= 0:
            raise ValueError("retrain_threshold must be positive")
        self._collector = collector or TrainingDataCollector()
        self._retrain_threshold = retrain_threshold
        self._overrides_since_retrain = 0
        self._last_retrain_at = _now()

    @property
    def overrides_since_last_retrain(self) -> int:
        """
        Number of human overrides recorded since the last retraining run.
        """
        return self._overrides_since_retrain

    @property
    def last_retrain_at(self) -> datetime:
        """
        Timestamp of the last retraining run.
        """
        return self._last_retrain_at

    def record_human_feedback(
        self,
        *,
        suite_run_id: UUID,
        utterance: str,
        expected_outcome: str,
        automated_label: str,
        human_decision: str,
        locale: str,
        recorded_at: Optional[datetime] = None,
        feedback: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[TrainingDataSample]:
        """
        Record human feedback; store sample if it overrides automated decision.
        """
        if human_decision == automated_label:
            return None

        combined_metadata: Dict[str, Any] = {}
        if metadata:
            combined_metadata.update(metadata)
        if feedback:
            combined_metadata.setdefault("feedback", feedback)

        sample = self._collector.record_validation(
            suite_run_id=suite_run_id,
            utterance=utterance,
            expected_outcome=expected_outcome,
            prediction_label=automated_label,
            human_decision=human_decision,
            locale=locale,
            recorded_at=recorded_at,
            metadata=combined_metadata,
        )
        self._overrides_since_retrain += 1
        return sample

    def should_trigger_retraining(self) -> bool:
        """
        Determine whether the accumulated overrides warrant retraining.
        """
        return self._overrides_since_retrain >= self._retrain_threshold

    def mark_retraining_complete(self, *, timestamp: Optional[datetime] = None) -> None:
        """
        Reset counters after a retraining cycle completes.
        """
        self._overrides_since_retrain = 0
        self._last_retrain_at = timestamp or _now()

