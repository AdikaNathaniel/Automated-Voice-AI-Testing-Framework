"""
Machine learning model performance monitoring service.

The MLMonitoringService keeps an in-memory record of model predictions
alongside the corresponding human validation decisions. This enables the
system to derive accuracy metrics and review historical predictions when
an ML model disagrees with human evaluators.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID


@dataclass(frozen=True)
class PredictionOutcome:
    """
    Immutable record capturing a model prediction and human validation outcome.
    """

    model_name: str
    suite_run_id: UUID
    prediction_label: str
    human_decision: str
    metadata: Dict[str, Any]

    @property
    def is_match(self) -> bool:
        """
        Whether the model prediction matches the human decision exactly.
        """
        return self.prediction_label == self.human_decision


@dataclass(frozen=True)
class AccuracySummary:
    """
    Aggregated accuracy metrics for a given model (or all models).
    """

    model_name: Optional[str]
    total_predictions: int
    matching_predictions: int
    accuracy: Optional[float]


class MLMonitoringService:
    """
    Service for tracking ML model predictions against human validation results.
    """

    def __init__(self) -> None:
        self._history: List[PredictionOutcome] = []

    def record_prediction_outcome(
        self,
        *,
        model_name: str,
        suite_run_id: UUID,
        prediction_label: str,
        human_decision: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PredictionOutcome:
        """
        Record the outcome of an ML prediction compared to human validation.
        """
        outcome = PredictionOutcome(
            model_name=model_name,
            suite_run_id=suite_run_id,
            prediction_label=prediction_label,
            human_decision=human_decision,
            metadata=dict(metadata or {}),
        )
        self._history.append(outcome)
        return outcome

    def get_prediction_history(
        self,
        *,
        model_name: Optional[str] = None,
    ) -> List[PredictionOutcome]:
        """
        Retrieve recorded prediction outcomes, optionally filtered by model.
        """
        if model_name is None:
            return list(self._history)
        return [outcome for outcome in self._history if outcome.model_name == model_name]

    def iter_prediction_history(self) -> Iterable[PredictionOutcome]:
        """
        Iterate through recorded prediction outcomes in insertion order.
        """
        return iter(self._history)

    def get_accuracy_summary(
        self,
        *,
        model_name: Optional[str] = None,
    ) -> AccuracySummary:
        """
        Calculate aggregate accuracy metrics for recorded predictions.
        """
        relevant = self.get_prediction_history(model_name=model_name)
        total = len(relevant)
        matches = sum(1 for outcome in relevant if outcome.is_match)
        accuracy = (matches / total) if total else None
        return AccuracySummary(
            model_name=model_name,
            total_predictions=total,
            matching_predictions=matches,
            accuracy=accuracy,
        )
