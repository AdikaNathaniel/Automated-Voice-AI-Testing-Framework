"""Tests for the defect aggregation service (TASK-243)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest

from services.defect_aggregation_service import (
    DefectAggregationService,
    DefectPatternSummary,
)


@dataclass
class DummyDefect:
    id: str
    test_case_id: str
    category: str
    severity: str
    title: str
    detected_at: datetime
    language_code: str | None = None


@pytest.fixture()
def sample_defects() -> list[DummyDefect]:
    base_time = datetime(2024, 4, 10, tzinfo=timezone.utc)
    tc1 = str(uuid4())
    tc2 = str(uuid4())
    return [
        DummyDefect(
            id=str(uuid4()),
            test_case_id=tc1,
            category="semantic",
            severity="high",
            title="Refund flow fails on invalid amount",
            detected_at=base_time,
        ),
        DummyDefect(
            id=str(uuid4()),
            test_case_id=tc1,
            category="semantic",
            severity="high",
            title="refund flow fails due to invalid amount",
            detected_at=base_time + timedelta(hours=3),
        ),
        DummyDefect(
            id=str(uuid4()),
            test_case_id=tc2,
            category="timing",
            severity="medium",
            title="Checkout confirmation slow response",
            detected_at=base_time + timedelta(days=1),
        ),
    ]


def test_cluster_groups_similar_defects(sample_defects: list[DummyDefect]):
    service = DefectAggregationService()

    clusters = service.cluster(sample_defects)

    assert len(clusters) == 2

    primary_cluster = next(
        cluster for cluster in clusters if cluster.category == "semantic"
    )
    assert primary_cluster.count == 2
    assert primary_cluster.test_case_id == sample_defects[0].test_case_id
    # Ensure timestamps represent the full range of grouped defects.
    assert primary_cluster.first_detected == sample_defects[0].detected_at
    assert primary_cluster.last_detected == sample_defects[1].detected_at


def test_summarize_patterns_counts_category_and_repeating_cases(sample_defects: list[DummyDefect]):
    service = DefectAggregationService()
    clusters = service.cluster(sample_defects)

    summary = service.summarize_patterns(clusters)

    assert isinstance(summary, DefectPatternSummary)
    assert summary.category_counts["semantic"] == 2
    assert summary.category_counts["timing"] == 1
    assert summary.severity_counts["high"] == 2
    assert summary.severity_counts["medium"] == 1
    # Only the first test case appears more than once.
    assert summary.repeating_test_cases == [sample_defects[0].test_case_id]
