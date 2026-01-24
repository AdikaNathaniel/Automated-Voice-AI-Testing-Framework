"""
Training data collector for aggregating human validation decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID


def _timestamp() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_timestamp(value: Optional[datetime]) -> datetime:
    if value is None:
        return _timestamp()
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class TrainingDataSample:
    """
    Immutable representation of a validation sample for model retraining.
    """

    suite_run_id: UUID
    utterance: str
    expected_outcome: str
    prediction_label: str
    human_decision: str
    locale: str
    recorded_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the sample to a dictionary suitable for JSON export.
        """
        return {
            "suite_run_id": str(self.suite_run_id),
            "utterance": self.utterance,
            "expected_outcome": self.expected_outcome,
            "prediction_label": self.prediction_label,
            "human_decision": self.human_decision,
            "locale": self.locale,
            "recorded_at": self.recorded_at.isoformat(),
            "metadata": dict(self.metadata),
        }


class TrainingDataCollector:
    """
    Collects training samples derived from human validation decisions.
    """

    def __init__(self) -> None:
        self._samples: List[TrainingDataSample] = []

    def record_validation(
        self,
        *,
        suite_run_id: UUID,
        utterance: str,
        expected_outcome: str,
        prediction_label: str,
        human_decision: str,
        locale: str,
        recorded_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TrainingDataSample:
        """
        Record a new training sample from a validation decision.
        """
        sample = TrainingDataSample(
            suite_run_id=suite_run_id,
            utterance=utterance,
            expected_outcome=expected_outcome,
            prediction_label=prediction_label,
            human_decision=human_decision,
            locale=locale,
            recorded_at=_normalize_timestamp(recorded_at),
            metadata=dict(metadata or {}),
        )
        self._samples.append(sample)
        return sample

    def get_samples(self) -> List[TrainingDataSample]:
        """
        Retrieve all recorded samples in insertion order.
        """
        return list(self._samples)

    def iter_samples(self) -> Iterable[TrainingDataSample]:
        """
        Iterate through recorded samples.
        """
        return iter(self._samples)

    def export_dataset(
        self,
        *,
        locale: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Export recorded samples as serializable dictionaries suitable for
        retraining pipelines.
        """
        samples = (
            sample for sample in self._samples if locale is None or sample.locale == locale
        )
        return [sample.to_dict() for sample in samples]
