from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from services.validator_statistics_service import (
    ValidatorStatisticsService,
    DecisionMetrics,
)


@pytest.mark.asyncio
async def test_build_validator_statistics_merges_summary_and_counts(monkeypatch):
    validator_id = uuid4()
    summary = {
        "total_validations": 12,
        "avg_time_seconds": 42.5,
        "avg_peer_agreement": 88.0,
        "avg_final_agreement": 90.0,
        "days_active": 3,
        "cohens_kappa": 0.72,
    }
    history = [
        SimpleNamespace(
            date=date.today(),
            validations_completed=5,
            agreement_with_peers_pct=88.0,
        ),
        SimpleNamespace(
            date=date.today() - timedelta(days=1),
            validations_completed=4,
            agreement_with_peers_pct=None,
        ),
    ]
    counts = DecisionMetrics(
        total=15,
        approvals=11,
        rejections=4,
        average_time_seconds=37.0,
    )

    fake_performance_service = SimpleNamespace(
        get_validator_summary=AsyncMock(return_value=summary),
        get_performance_history=AsyncMock(return_value=history),
    )
    service = ValidatorStatisticsService(performance_service=fake_performance_service)
    monkeypatch.setattr(
        service,
        "_fetch_decision_metrics",
        AsyncMock(return_value=counts),
    )

    payload = await service.build_validator_statistics(
        db=object(),
        validator_id=validator_id,
        display_name="Validator Example",
    )

    personal = payload["personal"]
    assert personal["completedValidations"] == counts.total
    assert personal["approvals"] == counts.approvals
    assert personal["rejections"] == counts.rejections
    assert personal["averageTimeSeconds"] == int(counts.average_time_seconds)
    assert personal["accuracy"] == pytest.approx(summary["avg_peer_agreement"] / 100.0)
    assert personal["currentStreakDays"] >= 0

    leaderboard = payload["leaderboard"]
    assert leaderboard
    assert leaderboard[0]["displayName"] == "Validator Example"
    assert leaderboard[0]["validatorId"] == str(validator_id)

    trend = payload["accuracyTrend"]
    assert len(trend) == len(history)
    assert trend[0]["date"] <= trend[-1]["date"]


def test_calculate_streak_from_history_handles_gaps():
    today = date.today()
    history = [
        SimpleNamespace(date=today, validations_completed=3),
        SimpleNamespace(date=today - timedelta(days=1), validations_completed=2),
        SimpleNamespace(date=today - timedelta(days=3), validations_completed=1),
    ]
    service = ValidatorStatisticsService()

    streak = service._calculate_streak_from_history(history)

    assert streak == 2
