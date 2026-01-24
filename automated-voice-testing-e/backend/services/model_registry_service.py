"""
Model registry service for tracking deployed ML model versions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from ml import ABTestManager, ABTestVariant

def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ModelVersion:
    """
    Representation of a model version entry in the registry.
    """

    model_name: str
    version_tag: str
    artifact_uri: str
    is_active: bool
    registered_at: datetime
    metadata: Dict[str, object] = field(default_factory=dict)


class ModelRegistryService:
    """
    Simple in-memory registry tracking model versions and active deployments.
    """

    def __init__(
        self,
        *,
        ab_manager: Optional[ABTestManager] = None,
    ) -> None:
        self._versions: Dict[str, List[ModelVersion]] = {}
        self._ab_manager = ab_manager or ABTestManager()
        self._experiments: Dict[str, str] = {}

    def register_model_version(
        self,
        *,
        model_name: str,
        version_tag: str,
        artifact_uri: str,
        metadata: Optional[Dict[str, object]] = None,
        registered_at: Optional[datetime] = None,
        activate: bool = True,
    ) -> ModelVersion:
        """
        Register a new model version and optionally mark it active.
        """
        versions = self._versions.setdefault(model_name, [])
        if activate:
            for existing in versions:
                existing.is_active = False

        entry = ModelVersion(
            model_name=model_name,
            version_tag=version_tag,
            artifact_uri=artifact_uri,
            is_active=activate,
            registered_at=registered_at or _now(),
            metadata=dict(metadata or {}),
        )
        versions.append(entry)
        return entry

    def get_active_version(self, model_name: str) -> Optional[ModelVersion]:
        """
        Retrieve the currently active version for a model, if any.
        """
        versions = self._versions.get(model_name, [])
        for version in reversed(versions):
            if version.is_active:
                return version
        return None

    def get_version_history(self, model_name: str) -> List[ModelVersion]:
        """
        Return all registered versions for the given model in registration order.
        """
        return list(self._versions.get(model_name, []))

    def rollback_model(self, model_name: str) -> Optional[ModelVersion]:
        """
        Roll back to the previous model version, if available.
        """
        versions = self._versions.get(model_name, [])
        if len(versions) < 2:
            return None

        current = versions[-1]
        previous = versions[-2]

        current.is_active = False
        previous.is_active = True
        return previous

    def launch_ab_test(
        self,
        *,
        model_name: str,
        candidate_version: str,
        baseline_weight: float = 1.0,
        candidate_weight: float = 1.0,
    ) -> str:
        """
        Launch an A/B test comparing the active version with a candidate version.
        """
        active = self.get_active_version(model_name)
        if not active:
            raise ValueError(f"No active version available for model '{model_name}'")

        candidate = self._find_version(model_name, candidate_version)
        if not candidate:
            raise ValueError("Candidate version not found")

        experiment_name = f"{model_name}-ab-test"
        if experiment_name in self._experiments.values():
            raise ValueError(f"Experiment '{experiment_name}' already running")

        baseline_variant = ABTestVariant(
            name="baseline",
            model_name=model_name,
            threshold=float(active.metadata.get("threshold", 0.0)),
            weight=baseline_weight,
            metadata={
                "version_tag": active.version_tag,
                "artifact_uri": active.artifact_uri,
            },
        )
        candidate_variant = ABTestVariant(
            name="candidate",
            model_name=model_name,
            threshold=float(candidate.metadata.get("threshold", 0.0)),
            weight=candidate_weight,
            metadata={
                "version_tag": candidate.version_tag,
                "artifact_uri": candidate.artifact_uri,
            },
        )

        self._ab_manager.create_experiment(
            name=experiment_name,
            variants=[baseline_variant, candidate_variant],
        )
        self._experiments[model_name] = experiment_name
        return experiment_name

    def record_ab_test_outcome(
        self,
        *,
        experiment: str,
        variant: str,
        matched: bool,
        accuracy: Optional[float] = None,
    ) -> None:
        """
        Record an outcome for an active A/B experiment.
        """
        self._ab_manager.record_outcome(
            experiment=experiment,
            variant=variant,
            matched=matched,
            accuracy=accuracy,
        )

    def _find_version(self, model_name: str, version_tag: str) -> Optional[ModelVersion]:
        versions = self._versions.get(model_name, [])
        for version in versions:
            if version.version_tag == version_tag:
                return version
        return None
