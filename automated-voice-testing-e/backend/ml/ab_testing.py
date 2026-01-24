"""
A/B testing utilities for comparing ML model configurations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import cycle
from typing import Any, Dict, Iterable, List, Optional


@dataclass(frozen=True)
class ABTestVariant:
    """
    Represents a single variant participating in an A/B experiment.
    """

    name: str
    model_name: str
    threshold: float
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.weight <= 0:
            raise ValueError("Variant weight must be positive.")


@dataclass(frozen=True)
class VariantOutcome:
    """
    Outcome metrics for a single prediction evaluated in an experiment.
    """

    variant: str
    matched: bool
    accuracy: Optional[float] = None


@dataclass(frozen=True)
class VariantMetrics:
    """
    Aggregated performance metrics for a variant.
    """

    exposures: int
    matches: int
    match_rate: Optional[float]
    average_accuracy: Optional[float]


@dataclass(frozen=True)
class ExperimentSummary:
    """
    Aggregated metrics for an experiment, including per-variant statistics.
    """

    experiment: str
    variant_metrics: Dict[str, VariantMetrics]
    total_exposures: int
    total_matches: int
    overall_match_rate: Optional[float]
    overall_average_accuracy: Optional[float]


class ABTestExperiment:
    """
    Internal representation of an A/B test experiment.
    """

    def __init__(self, name: str, variants: Iterable[ABTestVariant]) -> None:
        self.name = name
        self.variants: List[ABTestVariant] = list(variants)
        if not self.variants:
            raise ValueError("A/B experiment must contain at least one variant.")

        variant_names = [variant.name for variant in self.variants]
        if len(set(variant_names)) != len(variant_names):
            raise ValueError("Variant names must be unique within an experiment.")

        self._exposures: Dict[str, int] = {variant.name: 0 for variant in self.variants}
        self._outcomes: List[VariantOutcome] = []
        self._assignment_cycle = cycle(self._build_assignment_sequence())

    def _build_assignment_sequence(self) -> List[ABTestVariant]:
        sequence: List[ABTestVariant] = []
        for variant in self.variants:
            repeat = max(1, int(round(variant.weight)))
            sequence.extend([variant] * repeat)
        return sequence

    def assign_variant(self) -> ABTestVariant:
        variant = next(self._assignment_cycle)
        self._exposures[variant.name] += 1
        return variant

    def record_outcome(self, variant: str, matched: bool, accuracy: Optional[float]) -> VariantOutcome:
        if variant not in self._exposures:
            raise ValueError(f"Unknown variant '{variant}' for experiment '{self.name}'.")
        outcome = VariantOutcome(variant=variant, matched=matched, accuracy=accuracy)
        self._outcomes.append(outcome)
        return outcome

    def get_exposure_counts(self) -> Dict[str, int]:
        return dict(self._exposures)

    def iter_outcomes(self) -> Iterable[VariantOutcome]:
        return iter(self._outcomes)

    def get_variant_outcomes(self, variant: str) -> List[VariantOutcome]:
        return [outcome for outcome in self._outcomes if outcome.variant == variant]

    def summarize(self) -> ExperimentSummary:
        total_exposures = 0
        total_matches = 0
        accuracy_sum = 0.0
        accuracy_count = 0
        variant_metrics: Dict[str, VariantMetrics] = {}

        for variant in self.variants:
            exposures = self._exposures[variant.name]
            total_exposures += exposures

            outcomes = self.get_variant_outcomes(variant.name)
            matches = sum(1 for outcome in outcomes if outcome.matched)
            total_matches += matches

            accuracies = [outcome.accuracy for outcome in outcomes if outcome.accuracy is not None]
            if accuracies:
                accuracy_sum += sum(accuracies)
                accuracy_count += len(accuracies)

            average_accuracy = (sum(accuracies) / len(accuracies)) if accuracies else None
            match_rate = (matches / exposures) if exposures else None

            variant_metrics[variant.name] = VariantMetrics(
                exposures=exposures,
                matches=matches,
                match_rate=match_rate,
                average_accuracy=average_accuracy,
            )

        overall_match_rate = (total_matches / total_exposures) if total_exposures else None
        overall_average_accuracy = (accuracy_sum / accuracy_count) if accuracy_count else None

        return ExperimentSummary(
            experiment=self.name,
            variant_metrics=variant_metrics,
            total_exposures=total_exposures,
            total_matches=total_matches,
            overall_match_rate=overall_match_rate,
            overall_average_accuracy=overall_average_accuracy,
        )


class ABTestManager:
    """
    Facade for registering experiments and querying their performance.
    """

    def __init__(self) -> None:
        self._experiments: Dict[str, ABTestExperiment] = {}

    def create_experiment(self, *, name: str, variants: Iterable[ABTestVariant]) -> None:
        if name in self._experiments:
            raise ValueError(f"Experiment '{name}' already exists.")
        self._experiments[name] = ABTestExperiment(name=name, variants=variants)

    def assign_variant(self, experiment: str) -> ABTestVariant:
        return self._get_experiment(experiment).assign_variant()

    def record_outcome(
        self,
        *,
        experiment: str,
        variant: str,
        matched: bool,
        accuracy: Optional[float] = None,
    ) -> VariantOutcome:
        return self._get_experiment(experiment).record_outcome(
            variant=variant,
            matched=matched,
            accuracy=accuracy,
        )

    def get_exposure_counts(self, experiment: str) -> Dict[str, int]:
        return self._get_experiment(experiment).get_exposure_counts()

    def iter_outcomes(self, experiment: str) -> Iterable[VariantOutcome]:
        return self._get_experiment(experiment).iter_outcomes()

    def get_performance_summary(self, experiment: str) -> ExperimentSummary:
        return self._get_experiment(experiment).summarize()

    def _get_experiment(self, name: str) -> ABTestExperiment:
        if name not in self._experiments:
            raise ValueError(f"Experiment '{name}' has not been registered.")
        return self._experiments[name]
