"""
Predictive analytics service for defect likelihood estimation (TASK-312).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class PredictiveFeatures:
    """
    Normalised feature bundle describing recent quality signals.
    """

    recent_pass_rate: float  # percentage between 0 and 100
    failure_rate_last_7d: float  # ratio between 0 and 1
    defect_density_last_30d: float  # defects per 100 executions
    critical_defects_last_30d: int
    code_changes_last_14d: int
    coverage_gap_pct: float  # uncovered portion of the test surface


@dataclass(frozen=True)
class DefectRiskPrediction:
    """
    Result of a defect likelihood estimation.
    """

    probability: float  # value in [0, 1]
    risk_level: str  # low, medium, high
    contributing_factors: List[str]


class PredictiveAnalyticsService:
    """
    Applies heuristic weighting to derive defect likelihood scores.
    """

    _DEFAULT_WEIGHTS: Dict[str, float] = {
        "pass_rate": 0.35,
        "failure_rate": 0.25,
        "defect_density": 0.15,
        "critical_defects": 0.15,
        "code_churn": 0.07,
        "coverage_gap": 0.03,
    }

    def __init__(
        self,
        *,
        weights: Optional[Dict[str, float]] = None,
        risk_scale: float = 1.5,
    ) -> None:
        self._weights = dict(self._DEFAULT_WEIGHTS)
        if weights:
            self._weights.update(weights)
        self._risk_scale = risk_scale

    def calculate_defect_likelihood(self, features: PredictiveFeatures) -> DefectRiskPrediction:
        """
        Estimate the probability that an execution uncovers a new defect.
        """
        probability = 0.0
        contributing_factors: List[str] = []

        pass_rate_component = self._weights["pass_rate"] * self._invert_percentage(features.recent_pass_rate)
        if features.recent_pass_rate < 85.0:
            contributing_factors.append("Low pass rate")
        probability += pass_rate_component

        failure_rate_component = self._weights["failure_rate"] * self._clamp(features.failure_rate_last_7d)
        if features.failure_rate_last_7d > 0.3:
            contributing_factors.append("Elevated recent failures")
        probability += failure_rate_component

        density_norm = min(features.defect_density_last_30d / 10.0, 1.0)
        probability += self._weights["defect_density"] * self._clamp(density_norm)

        critical_norm = min(features.critical_defects_last_30d / 3.0, 1.0)
        if features.critical_defects_last_30d >= 2:
            contributing_factors.append("Critical defects trend")
        probability += self._weights["critical_defects"] * self._clamp(critical_norm)

        code_churn_norm = min(features.code_changes_last_14d / 20.0, 1.0)
        if features.code_changes_last_14d >= 10:
            contributing_factors.append("Recent code churn")
        probability += self._weights["code_churn"] * self._clamp(code_churn_norm)

        coverage_gap_component = self._weights["coverage_gap"] * self._clamp(features.coverage_gap_pct / 100.0)
        if features.coverage_gap_pct > 15.0:
            contributing_factors.append("Coverage gaps")
        probability += coverage_gap_component

        probability = self._clamp(probability * self._risk_scale)

        if probability >= 0.65:
            risk_level = "high"
        elif probability >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return DefectRiskPrediction(
            probability=probability,
            risk_level=risk_level,
            contributing_factors=contributing_factors,
        )

    def rank_test_cases(
        self,
        feature_map: Dict[str, PredictiveFeatures],
        *,
        limit: Optional[int] = None,
    ) -> List[Tuple[str, DefectRiskPrediction]]:
        """
        Score test cases and return them ordered by highest predicted risk.
        """
        rankings: List[Tuple[str, DefectRiskPrediction]] = []
        for name, features in feature_map.items():
            prediction = self.calculate_defect_likelihood(features)
            rankings.append((name, prediction))

        rankings.sort(key=lambda item: item[1].probability, reverse=True)
        if limit is not None:
            return rankings[: limit if limit >= 0 else 0]
        return rankings

    @staticmethod
    def _invert_percentage(value: float) -> float:
        return PredictiveAnalyticsService._clamp(1.0 - (value / 100.0 if value is not None else 0.0))

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        if value is None:
            return minimum
        return max(minimum, min(maximum, float(value)))
