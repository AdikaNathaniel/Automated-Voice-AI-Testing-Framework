"""
Predictive analytics service tests (TASK-312).

Validates defect likelihood calculations and supporting metadata.
"""

from __future__ import annotations

import pytest

from services.predictive_analytics_service import (
    DefectRiskPrediction,
    PredictiveAnalyticsService,
    PredictiveFeatures,
)


@pytest.fixture()
def predictive_service() -> PredictiveAnalyticsService:
    return PredictiveAnalyticsService()


def test_high_risk_prediction_identifies_contributing_factors(
    predictive_service: PredictiveAnalyticsService,
) -> None:
    features = PredictiveFeatures(
        recent_pass_rate=72.5,
        failure_rate_last_7d=0.45,
        defect_density_last_30d=8.0,
        critical_defects_last_30d=3,
        code_changes_last_14d=18,
        coverage_gap_pct=22.0,
    )

    prediction = predictive_service.calculate_defect_likelihood(features)

    assert isinstance(prediction, DefectRiskPrediction)
    assert 0.0 <= prediction.probability <= 1.0
    assert prediction.probability >= 0.75
    assert prediction.risk_level == "high"
    assert "Low pass rate" in prediction.contributing_factors
    assert "Recent code churn" in prediction.contributing_factors


def test_low_risk_prediction_caps_probability(
    predictive_service: PredictiveAnalyticsService,
) -> None:
    features = PredictiveFeatures(
        recent_pass_rate=99.0,
        failure_rate_last_7d=0.02,
        defect_density_last_30d=0.5,
        critical_defects_last_30d=0,
        code_changes_last_14d=3,
        coverage_gap_pct=2.5,
    )

    prediction = predictive_service.calculate_defect_likelihood(features)

    assert prediction.probability <= 0.25
    assert prediction.risk_level == "low"
    assert prediction.contributing_factors == []


def test_rankings_sort_by_probability_descending(
    predictive_service: PredictiveAnalyticsService,
) -> None:
    scenarios = {
        "stable_case": PredictiveFeatures(
            recent_pass_rate=96.0,
            failure_rate_last_7d=0.05,
            defect_density_last_30d=1.0,
            critical_defects_last_30d=0,
            code_changes_last_14d=2,
            coverage_gap_pct=4.0,
        ),
        "risky_case": PredictiveFeatures(
            recent_pass_rate=70.0,
            failure_rate_last_7d=0.4,
            defect_density_last_30d=6.0,
            critical_defects_last_30d=2,
            code_changes_last_14d=15,
            coverage_gap_pct=18.0,
        ),
        "moderate_case": PredictiveFeatures(
            recent_pass_rate=88.0,
            failure_rate_last_7d=0.18,
            defect_density_last_30d=3.0,
            critical_defects_last_30d=1,
            code_changes_last_14d=8,
            coverage_gap_pct=10.0,
        ),
    }

    rankings = predictive_service.rank_test_cases(scenarios)

    ordered_names = [name for name, _ in rankings]
    assert ordered_names == ["risky_case", "moderate_case", "stable_case"]
    assert rankings[0][1].risk_level == "high"
    assert rankings[-1][1].risk_level == "low"
