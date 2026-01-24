"""
Tests for EdgeCaseAnalyticsService (Phase 5).

Validates aggregation queries, time-series data, and distribution calculations.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from models.edge_case import EdgeCase
from models.pattern_group import EdgeCasePatternLink, PatternGroup
from services.edge_case_analytics_service import EdgeCaseAnalyticsService


@pytest.fixture()
def session() -> Session:
    """Create in-memory SQLite session with required tables."""
    engine = create_engine("sqlite:///:memory:", future=True)

    # Create tables needed for tests
    EdgeCase.__table__.create(engine, checkfirst=True)
    PatternGroup.__table__.create(engine, checkfirst=True)
    EdgeCasePatternLink.__table__.create(engine, checkfirst=True)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    try:
        with SessionLocal() as db:
            yield db
            db.rollback()
    finally:
        EdgeCasePatternLink.__table__.drop(engine, checkfirst=True)
        PatternGroup.__table__.drop(engine, checkfirst=True)
        EdgeCase.__table__.drop(engine, checkfirst=True)
        engine.dispose()


@pytest.fixture()
def sample_edge_cases(session: Session) -> list[EdgeCase]:
    """Create sample edge cases for testing."""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    two_weeks_ago = today - timedelta(days=14)

    edge_cases = [
        EdgeCase(
            title="Audio quality issue",
            category="audio_quality",
            severity="high",
            status="active",
            auto_created=True,
            created_at=today,
            updated_at=today,
        ),
        EdgeCase(
            title="Ambiguous intent detection",
            category="ambiguity",
            severity="medium",
            status="active",
            auto_created=True,
            created_at=yesterday,
            updated_at=yesterday,
        ),
        EdgeCase(
            title="Context loss in conversation",
            category="context_loss",
            severity="critical",
            status="resolved",
            auto_created=False,
            created_at=last_week,
            updated_at=today,  # Resolved today
        ),
        EdgeCase(
            title="Localization failure",
            category="localization",
            severity="low",
            status="active",
            auto_created=True,
            created_at=two_weeks_ago,
            updated_at=two_weeks_ago,
        ),
        EdgeCase(
            title="Uncategorized issue",
            category=None,
            severity=None,
            status="wont_fix",
            auto_created=False,
            created_at=last_week,
            updated_at=last_week,
        ),
    ]

    for ec in edge_cases:
        session.add(ec)
    session.commit()

    for ec in edge_cases:
        session.refresh(ec)

    return edge_cases


@pytest.fixture()
def sample_pattern_group(session: Session, sample_edge_cases: list[EdgeCase]) -> PatternGroup:
    """Create a sample pattern group with linked edge cases."""
    pattern = PatternGroup(
        name="Audio Issues Pattern",
        pattern_type="semantic",
        severity="high",
        status="active",
        occurrence_count=2,
    )
    session.add(pattern)
    session.commit()
    session.refresh(pattern)

    # Link first two edge cases to the pattern
    for ec in sample_edge_cases[:2]:
        link = EdgeCasePatternLink(
            edge_case_id=ec.id,
            pattern_group_id=pattern.id,
            similarity_score=0.9,
        )
        session.add(link)
    session.commit()

    return pattern


def test_get_analytics_returns_all_sections(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test that get_analytics returns all expected data sections."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics()

    assert "date_range" in result
    assert "summary" in result
    assert "count_over_time" in result
    assert "category_distribution" in result
    assert "severity_distribution" in result
    assert "status_distribution" in result
    assert "resolution_metrics" in result
    assert "top_patterns" in result
    assert "auto_vs_manual" in result


def test_get_analytics_summary_counts(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test that summary counts are correct."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics()

    summary = result["summary"]
    # 5 total edge cases
    assert summary["total_all_time"] == 5
    # 3 active (audio_quality, ambiguity, localization)
    assert summary["active_count"] == 3
    # 1 critical active (context_loss is resolved, so 0 critical active)
    assert summary["critical_active"] == 0


def test_get_analytics_with_date_range(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test filtering by date range."""
    service = EdgeCaseAnalyticsService(session)

    # Only get last 7 days
    today = date.today()
    week_ago = today - timedelta(days=7)

    result = service.get_analytics(date_from=week_ago, date_to=today)

    # Should include only edge cases created in last 7 days
    # (today, yesterday, and last_week - excludes two_weeks_ago)
    assert result["date_range"]["from"] == week_ago.isoformat()
    assert result["date_range"]["to"] == today.isoformat()


def test_count_over_time_includes_all_days_in_range(session: Session) -> None:
    """Test that count_over_time includes entries for all days."""
    service = EdgeCaseAnalyticsService(session)

    today = date.today()
    week_ago = today - timedelta(days=6)

    result = service.get_analytics(date_from=week_ago, date_to=today)

    # Should have 7 days of data
    assert len(result["count_over_time"]) == 7


def test_category_distribution_groups_correctly(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test that categories are grouped and percentages calculated."""
    service = EdgeCaseAnalyticsService(session)

    # Use wide date range to include all
    result = service.get_analytics(
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
    )

    distribution = result["category_distribution"]
    categories = {item["category"]: item for item in distribution}

    # Verify known categories are present
    assert "audio_quality" in categories
    assert "ambiguity" in categories
    assert "uncategorized" in categories

    # Verify percentages sum to ~100%
    total_percentage = sum(item["percentage"] for item in distribution)
    assert 99.0 <= total_percentage <= 101.0


def test_severity_distribution_orders_correctly(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test that severity distribution is ordered by severity level."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics(
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
    )

    distribution = result["severity_distribution"]
    severity_order = ["critical", "high", "medium", "low"]

    # Get severities that are present
    present_severities = [
        item["severity"]
        for item in distribution
        if item["severity"] in severity_order
    ]

    # Verify order is maintained for known severities
    for i in range(len(present_severities) - 1):
        curr_idx = severity_order.index(present_severities[i])
        next_idx = severity_order.index(present_severities[i + 1])
        assert curr_idx <= next_idx


def test_resolution_metrics_calculates_rate(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test that resolution rate is calculated correctly."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics(
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
    )

    metrics = result["resolution_metrics"]

    # Total should be resolved + active + wont_fix
    assert metrics["total_created"] == metrics["resolved"] + metrics["active"] + metrics["wont_fix"]

    # Resolution rate should be (resolved / total) * 100
    if metrics["total_created"] > 0:
        expected_rate = round((metrics["resolved"] / metrics["total_created"]) * 100, 1)
        assert metrics["resolution_rate_percent"] == expected_rate


def test_auto_vs_manual_breakdown(
    session: Session, sample_edge_cases: list[EdgeCase]
) -> None:
    """Test auto-created vs manual breakdown."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics(
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
    )

    auto_manual = result["auto_vs_manual"]

    # From sample data: 3 auto-created, 2 manual
    assert auto_manual["auto_created"] == 3
    assert auto_manual["manually_created"] == 2

    # Percentages should sum to 100
    total_pct = auto_manual["auto_created_percent"] + auto_manual["manually_created_percent"]
    assert 99.9 <= total_pct <= 100.1


def test_top_patterns_returns_linked_patterns(
    session: Session,
    sample_edge_cases: list[EdgeCase],
    sample_pattern_group: PatternGroup,
) -> None:
    """Test that top patterns are returned with linked edge case counts."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics(
        date_from=date.today() - timedelta(days=30),
        date_to=date.today(),
    )

    patterns = result["top_patterns"]

    assert len(patterns) >= 1
    assert patterns[0]["name"] == "Audio Issues Pattern"
    assert patterns[0]["linked_edge_cases"] >= 1


def test_trend_comparison_calculates_change(session: Session) -> None:
    """Test trend comparison between periods."""
    # Create edge cases in different periods
    today = datetime.now()
    current_period_date = today - timedelta(days=5)
    previous_period_date = today - timedelta(days=35)

    # Add more edge cases to current period
    for i in range(3):
        session.add(
            EdgeCase(
                title=f"Current period edge case {i}",
                status="active",
                created_at=current_period_date,
                updated_at=current_period_date,
            )
        )

    # Add fewer to previous period
    session.add(
        EdgeCase(
            title="Previous period edge case",
            status="active",
            created_at=previous_period_date,
            updated_at=previous_period_date,
        )
    )
    session.commit()

    service = EdgeCaseAnalyticsService(session)
    result = service.get_trend_comparison(date_to=date.today(), period_days=30)

    assert "current_period" in result
    assert "previous_period" in result
    assert "change" in result
    assert "change_percent" in result
    assert "trend" in result

    # Current period should have more
    assert result["current_period"]["count"] >= result["previous_period"]["count"]
    assert result["trend"] in ["up", "down", "stable"]


def test_empty_database_returns_zeros(session: Session) -> None:
    """Test that empty database returns valid structure with zeros."""
    service = EdgeCaseAnalyticsService(session)

    result = service.get_analytics()

    assert result["summary"]["total_all_time"] == 0
    assert result["summary"]["active_count"] == 0
    assert result["resolution_metrics"]["total_created"] == 0
    assert len(result["top_patterns"]) == 0
