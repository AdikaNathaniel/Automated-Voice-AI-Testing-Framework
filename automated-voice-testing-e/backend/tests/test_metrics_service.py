"""
MetricsService tests for recording and aggregating metrics.

Validates time-series persistence behaviour before integrating into the
dashboard endpoints.
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import pytest_asyncio
from typing import AsyncGenerator

from models.base import Base
from models.test_metric import TestMetric
from services.metrics_service import MetricsService


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated async database session for metrics tests."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_record_metric_persists_row(db_session: AsyncSession):
    service = MetricsService(db_session)
    timestamp = datetime(2024, 1, 1, 12, 30, tzinfo=timezone.utc)

    metric = await service.record_metric(
        metric_type="pass_rate",
        metric_value=95.5,
        dimensions={"language": "en-US", "suite": "smoke"},
        timestamp=timestamp,
    )

    assert metric.metric_type == "pass_rate"
    assert metric.metric_value == Decimal("95.50")
    assert metric.dimensions == {"language": "en-US", "suite": "smoke"}
    assert metric.timestamp == timestamp

    result = await db_session.execute(sa.select(TestMetric))
    stored_metrics = result.scalars().all()
    assert len(stored_metrics) == 1
    assert stored_metrics[0].id == metric.id


@pytest.mark.asyncio
async def test_record_metric_handles_missing_dimensions(db_session: AsyncSession):
    service = MetricsService(db_session)
    timestamp = datetime(2024, 1, 2, tzinfo=timezone.utc)

    metric = await service.record_metric(
        metric_type="response_time",
        metric_value=123.4,
        dimensions=None,
        timestamp=timestamp,
    )

    assert metric.dimensions == {}


@pytest.mark.asyncio
async def test_record_metric_rejects_naive_timestamp(db_session: AsyncSession):
    service = MetricsService(db_session)
    naive_timestamp = datetime(2024, 1, 3, 15, 0, 0)  # no tzinfo

    with pytest.raises(ValueError):
        await service.record_metric(
            metric_type="execution_time",
            metric_value=42.0,
            dimensions={},
            timestamp=naive_timestamp,
        )


@pytest.mark.asyncio
async def test_get_metrics_groups_by_hour(db_session: AsyncSession):
    service = MetricsService(db_session)
    base = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)

    await service.record_metric(
        metric_type="pass_rate",
        metric_value=90.0,
        dimensions={"language": "en-US"},
        timestamp=base + timedelta(minutes=10),
    )
    await service.record_metric(
        metric_type="pass_rate",
        metric_value=95.5,
        dimensions={"language": "en-US"},
        timestamp=base + timedelta(minutes=35),
    )
    await service.record_metric(
        metric_type="pass_rate",
        metric_value=80.0,
        dimensions={"language": "en-US"},
        timestamp=base + timedelta(hours=1, minutes=5),
    )
    await service.record_metric(
        metric_type="pass_rate",
        metric_value=70.0,
        dimensions={"language": "es-ES"},
        timestamp=base + timedelta(minutes=15),
    )

    results = await service.get_metrics(
        metric_type="pass_rate",
        start_time=base,
        end_time=base + timedelta(hours=2),
        granularity="hour",
        dimensions={"language": "en-US"},
    )

    assert len(results) == 2
    assert results[0]["timestamp"] == base
    assert results[0]["metric_value"] == pytest.approx(92.75)
    assert results[0]["count"] == 2

    assert results[1]["timestamp"] == base + timedelta(hours=1)
    assert results[1]["metric_value"] == pytest.approx(80.0)
    assert results[1]["count"] == 1


@pytest.mark.asyncio
async def test_get_metrics_filters_and_groups_by_day(db_session: AsyncSession):
    service = MetricsService(db_session)
    day_one = datetime(2024, 2, 1, 9, 0, tzinfo=timezone.utc)
    day_two = datetime(2024, 2, 2, 9, 0, tzinfo=timezone.utc)

    await service.record_metric(
        metric_type="execution_time",
        metric_value=120.0,
        dimensions={"language": "en-US", "suite": "smoke"},
        timestamp=day_one,
    )
    await service.record_metric(
        metric_type="execution_time",
        metric_value=150.0,
        dimensions={"language": "en-US", "suite": "smoke"},
        timestamp=day_one + timedelta(hours=2),
    )
    await service.record_metric(
        metric_type="execution_time",
        metric_value=95.0,
        dimensions={"language": "en-US", "suite": "regression"},
        timestamp=day_one,
    )
    await service.record_metric(
        metric_type="execution_time",
        metric_value=200.0,
        dimensions={"language": "en-US", "suite": "smoke"},
        timestamp=day_two + timedelta(hours=1),
    )

    results = await service.get_metrics(
        metric_type="execution_time",
        start_time=day_one,
        end_time=day_two + timedelta(days=1),
        granularity="day",
        dimensions={"language": "en-US", "suite": "smoke"},
    )

    assert len(results) == 2
    assert results[0]["timestamp"] == datetime(2024, 2, 1, tzinfo=timezone.utc)
    assert results[0]["metric_value"] == pytest.approx(135.0)
    assert results[0]["count"] == 2

    assert results[1]["timestamp"] == datetime(2024, 2, 2, tzinfo=timezone.utc)
    assert results[1]["metric_value"] == pytest.approx(200.0)
    assert results[1]["count"] == 1


@pytest.mark.asyncio
async def test_get_metrics_rejects_unknown_granularity(db_session: AsyncSession):
    service = MetricsService(db_session)
    now = datetime.now(timezone.utc)

    with pytest.raises(ValueError):
        await service.get_metrics(
            metric_type="pass_rate",
            start_time=now - timedelta(hours=1),
            end_time=now,
            granularity="minute",
        )
