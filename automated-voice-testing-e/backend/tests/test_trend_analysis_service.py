"""
TrendAnalysisService tests.

Validates pass rate, defect, and performance trend aggregation logic prior to
exposing analytics endpoints.
"""

from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, AsyncGenerator, Optional
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import Column, String, Table
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock

from models.base import Base
from models.defect import Defect
from models.test_metric import TestMetric
from services.trend_analysis_service import TrendAnalysisService
from services.anomaly_detection_service import AnomalyDetectionService


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated async database session for trend analysis tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    # Define a minimal stub for referenced test_cases table to satisfy FK constraints.
    stub_tables: list[Table] = []
    original_tables: dict[str, Optional[Table]] = {}
    for table_name in ("users", "test_cases", "test_runs"):
        original = Base.metadata.tables.get(table_name)
        original_tables[table_name] = original
        if original is not None:
            Base.metadata.remove(original)

        table = Table(
            table_name,
            Base.metadata,
            Column("id", String(36), primary_key=True),
        )
        stub_tables.append(table)

    async with engine.begin() as connection:
        await connection.exec_driver_sql("PRAGMA foreign_keys=OFF")
        for table in stub_tables:
            await connection.run_sync(table.create)
        await connection.run_sync(Defect.__table__.create)
        await connection.run_sync(TestMetric.__table__.create)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(TestMetric.__table__.drop)
        await connection.run_sync(Defect.__table__.drop)
        for table in ("test_runs", "test_cases", "users"):
            await connection.exec_driver_sql(f"DROP TABLE IF EXISTS {table}")
        # Restore original table metadata.
        for name in ("test_runs", "test_cases", "users"):
            stub = Base.metadata.tables.get(name)
            if stub is not None:
                Base.metadata.remove(stub)
            original = original_tables.get(name)
            if original is not None:
                # In SQLAlchemy 2.0+, tables are automatically added when created with metadata
                # Just need to ensure the table is associated with the metadata
                if original.name not in Base.metadata.tables:
                    original._set_parent(Base.metadata)
    await engine.dispose()


def _metric(
    *,
    metric_type: str,
    value: float,
    day: datetime,
    aggregation: str = "day",
    count: int = 1,
) -> list[TestMetric]:
    """Create a TestMetric row with optional duplication for counts."""
    metrics = []
    dimensions = {"aggregation": aggregation}
    for _ in range(count):
        metrics.append(
            TestMetric(
                metric_type=metric_type,
                metric_value=Decimal(str(value)),
                dimensions=dimensions,
                timestamp=day,
            )
        )
    return metrics


@pytest.mark.asyncio
async def test_analyze_pass_rate_trend_returns_percentages(db_session: AsyncSession):
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    day_two = start + timedelta(days=1)
    day_three = start + timedelta(days=2)

    metrics = (
        _metric(metric_type="validation_pass", value=1.0, day=start, count=3)
        + _metric(metric_type="validation_pass", value=0.0, day=start, count=1)
        + _metric(metric_type="validation_pass", value=1.0, day=day_two, count=4)
        + _metric(metric_type="validation_pass", value=0.0, day=day_two, count=0)
        + _metric(metric_type="validation_pass", value=0.0, day=day_three, count=2)
        + _metric(metric_type="validation_pass", value=1.0, day=day_three, count=1)
    )
    db_session.add_all(metrics)
    await db_session.commit()

    service = TrendAnalysisService(db_session)

    results = await service.analyze_pass_rate_trend(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        granularity="day",
    )

    assert len(results) == 3

    first, second, third = results
    assert first["period_start"] == start
    assert first["pass_rate_pct"] == pytest.approx(75.0)
    assert first["total_executions"] == 4
    assert first["change_pct"] is None
    assert first["direction"] == "flat"

    assert second["period_start"] == day_two
    assert second["pass_rate_pct"] == pytest.approx(100.0)
    assert second["total_executions"] == 4
    assert second["change_pct"] == pytest.approx(25.0)
    assert second["direction"] == "up"

    assert third["period_start"] == day_three
    assert third["pass_rate_pct"] == pytest.approx(33.0)
    assert third["total_executions"] == 3
    assert third["change_pct"] == pytest.approx(-67.0)
    assert third["direction"] == "down"


@pytest.mark.asyncio
async def test_analyze_pass_rate_trend_validates_inputs(db_session: AsyncSession):
    service = TrendAnalysisService(db_session)

    with pytest.raises(ValueError):
        await service.analyze_pass_rate_trend(
            start_date=date(2024, 1, 3),
            end_date=date(2024, 1, 1),
            granularity="day",
        )

    with pytest.raises(ValueError):
        await service.analyze_pass_rate_trend(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 2),
            granularity="month",
        )


@pytest.mark.asyncio
async def test_analyze_defect_trend_calculates_running_open(db_session: AsyncSession):
    service = TrendAnalysisService(db_session)
    case_id = uuid4()

    baseline_detected = datetime(2023, 12, 31, 10, tzinfo=timezone.utc)
    baseline_resolved = datetime(2024, 1, 2, 8, tzinfo=timezone.utc)

    defects = [
        Defect(
            test_case_id=case_id,
            severity="high",
            category="audio",
            title="Latency spike",
            detected_at=baseline_detected,
            resolved_at=baseline_resolved,
            status="resolved",
        ),
        Defect(
            test_case_id=case_id,
            severity="medium",
            category="audio",
            title="Wake failure",
            detected_at=datetime(2024, 1, 1, 9, tzinfo=timezone.utc),
            resolved_at=datetime(2024, 1, 1, 18, tzinfo=timezone.utc),
            status="resolved",
        ),
        Defect(
            test_case_id=case_id,
            severity="medium",
            category="audio",
            title="False positive trigger",
            detected_at=datetime(2024, 1, 1, 12, tzinfo=timezone.utc),
            status="open",
        ),
        Defect(
            test_case_id=case_id,
            severity="low",
            category="timing",
            title="Slow prompt",
            detected_at=datetime(2024, 1, 2, 10, tzinfo=timezone.utc),
            resolved_at=datetime(2024, 1, 2, 18, tzinfo=timezone.utc),
            status="resolved",
        ),
    ]

    db_session.add_all(defects)
    await db_session.commit()

    results = await service.analyze_defect_trend(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        granularity="day",
    )

    assert [entry["period_start"] for entry in results] == [
        datetime(2024, 1, 1, tzinfo=timezone.utc),
        datetime(2024, 1, 2, tzinfo=timezone.utc),
        datetime(2024, 1, 3, tzinfo=timezone.utc),
    ]

    day_one, day_two, day_three = results

    assert day_one["detected"] == 2
    assert day_one["resolved"] == 1
    assert day_one["net_open"] == 2  # baseline 1 open +1 net increase
    assert day_one["change_open"] is None
    assert day_one["direction"] == "flat"

    assert day_two["detected"] == 1
    assert day_two["resolved"] == 2  # includes baseline closure
    assert day_two["net_open"] == 1
    assert day_two["change_open"] == -1
    assert day_two["direction"] == "down"

    assert day_three["detected"] == 0
    assert day_three["resolved"] == 0
    assert day_three["net_open"] == 1
    assert day_three["change_open"] == 0
    assert day_three["direction"] == "flat"


@pytest.mark.asyncio
async def test_analyze_performance_trend_returns_average_ms(db_session: AsyncSession):
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    day_two = start + timedelta(days=1)
    day_three = start + timedelta(days=2)

    metrics = (
        _metric(metric_type="response_time", value=1.2, day=start, count=1)
        + _metric(metric_type="response_time", value=1.4, day=start, count=1)
        + _metric(metric_type="response_time", value=0.8, day=day_two, count=1)
        + _metric(metric_type="response_time", value=1.0, day=day_two, count=1)
        + _metric(metric_type="response_time", value=0.9, day=day_three, count=1)
    )
    db_session.add_all(metrics)
    await db_session.commit()

    service = TrendAnalysisService(db_session)

    results = await service.analyze_performance_trend(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        granularity="day",
    )

    first, second, third = results

    assert first["avg_response_time_ms"] == pytest.approx(1300.0)
    assert first["sample_size"] == 2
    assert first["change_ms"] is None
    assert first["direction"] == "flat"

    assert second["avg_response_time_ms"] == pytest.approx(900.0)
    assert second["sample_size"] == 2
    assert second["change_ms"] == pytest.approx(-400.0)
    assert second["direction"] == "down"

    assert third["avg_response_time_ms"] == pytest.approx(900.0)
    assert third["sample_size"] == 1
    assert third["change_ms"] == pytest.approx(0.0)
    assert third["direction"] == "flat"


@pytest.mark.asyncio
async def test_pass_rate_trend_handles_empty_dataset():
    service = object.__new__(TrendAnalysisService)
    service._db = object()

    class StubMetrics:
        async def get_metrics(self, **kwargs: Any):
            return []

    service._metrics = StubMetrics()

    results = await TrendAnalysisService.analyze_pass_rate_trend(
        service,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
        granularity="day",
    )

    assert results == []


@pytest.mark.asyncio
async def test_performance_trend_handles_empty_dataset():
    service = object.__new__(TrendAnalysisService)
    service._db = object()

    class StubMetrics:
        async def get_metrics(self, **kwargs: Any):
            return []

    service._metrics = StubMetrics()

    results = await TrendAnalysisService.analyze_performance_trend(
        service,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        granularity="day",
    )

    assert results == []


@pytest.mark.asyncio
async def test_defect_trend_handles_no_defects(monkeypatch: pytest.MonkeyPatch):
    service = object.__new__(TrendAnalysisService)
    service._db = object()
    service._metrics = object()

    async def fake_collect(**kwargs: Any):
        return {}

    async def fake_count(start_time: datetime) -> int:
        return 0

    monkeypatch.setattr(service, "_collect_defect_counts", fake_collect)
    monkeypatch.setattr(service, "_count_open_defects_before", fake_count)

    results = await TrendAnalysisService.analyze_defect_trend(
        service,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 2),
        granularity="day",
    )

    assert len(results) == 2
    for idx, entry in enumerate(results):
        assert entry["detected"] == 0
        assert entry["resolved"] == 0
        assert entry["net_open"] == 0
        if idx == 0:
            assert entry["change_open"] is None
        else:
            assert entry["change_open"] == 0
        assert entry["direction"] == "flat"


@pytest.mark.asyncio
async def test_analyze_trends_with_anomalies_handles_empty_dataset():
    service = object.__new__(TrendAnalysisService)
    service._db = object()
    service._metrics = object()

    zero_defects = [
        {
            "period_start": datetime(2024, 1, 1, tzinfo=timezone.utc) + timedelta(days=offset),
            "detected": 0,
            "resolved": 0,
            "net_open": 0,
            "change_open": None if offset == 0 else 0,
            "direction": "flat",
        }
        for offset in range(3)
    ]

    service.analyze_pass_rate_trend = AsyncMock(return_value=[])
    service.analyze_defect_trend = AsyncMock(return_value=zero_defects)
    service.analyze_performance_trend = AsyncMock(return_value=[])

    result = await TrendAnalysisService.analyze_trends_with_anomalies(
        service,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 3),
        granularity="day",
    )

    assert result["pass_rate"] == []
    assert result["defects"] == zero_defects
    assert result["performance"] == []
    assert result["anomalies"] == []


@pytest.mark.asyncio
async def test_analyze_trends_with_anomalies(db_session: AsyncSession):
    service = TrendAnalysisService(db_session)
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)

    pass_metrics = (
        _metric(metric_type="validation_pass", value=1.0, day=base, count=3)
        + _metric(metric_type="validation_pass", value=0.0, day=base, count=1)
        + _metric(metric_type="validation_pass", value=1.0, day=base + timedelta(days=1), count=4)
        + _metric(metric_type="validation_pass", value=0.0, day=base + timedelta(days=2), count=2)
        + _metric(metric_type="validation_pass", value=0.0, day=base + timedelta(days=2), count=1)
    )
    response_metrics = []
    for idx, seconds in enumerate([0.95, 0.98, 1.01, 1.35]):
        response_metrics.extend(
            _metric(
                metric_type="response_time",
                value=seconds,
                day=base + timedelta(days=idx),
            )
        )
    db_session.add_all(pass_metrics + response_metrics)

    case_id = uuid4()
    defects = [
        Defect(
            test_case_id=case_id,
            severity="medium",
            category="audio",
            title="Wake failure",
            detected_at=base,
            resolved_at=base + timedelta(hours=1),
            status="resolved",
        ),
        Defect(
            test_case_id=case_id,
            severity="medium",
            category="audio",
            title="Recurring slip",
            detected_at=base + timedelta(days=1, hours=2),
            status="open",
        ),
        Defect(
            test_case_id=case_id,
            severity="high",
            category="timing",
            title="Slow response",
            detected_at=base + timedelta(days=2, hours=1),
            status="open",
        ),
    ]
    db_session.add_all(defects)
    await db_session.commit()

    anomaly_detector = AnomalyDetectionService(
        pass_rate_drop_threshold_pct=8.0,
        response_time_increase_threshold_pct=30.0,
        defect_backlog_threshold=2,
    )

    result = await service.analyze_trends_with_anomalies(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 4),
        granularity="day",
        anomaly_service=anomaly_detector,
    )

    anomalies = result["anomalies"]
    assert anomalies, "Expected at least one anomaly"
    assert any(alert.metric == "pass_rate" for alert in anomalies)
