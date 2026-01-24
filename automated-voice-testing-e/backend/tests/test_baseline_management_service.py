"""
Tests for baseline management service (TASK-337, subtask 1).

These initial tests ensure that approving a baseline persists the snapshot
for a test case and allows it to be retrieved later with metadata intact.
"""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
from models.regression_baseline import RegressionBaseline, BaselineHistory
from services.baseline_management_service import BaselineManagementService
from services.regression_detection_service import TestResultSnapshot


@pytest.fixture()
def session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    # Only create the specific tables needed for these tests
    # (avoids PostgreSQL-specific types in other models like knowledge_base)
    RegressionBaseline.__table__.create(engine, checkfirst=True)
    BaselineHistory.__table__.create(engine, checkfirst=True)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    try:
        with SessionLocal() as session:
            yield session
            session.rollback()
    finally:
        BaselineHistory.__table__.drop(engine, checkfirst=True)
        RegressionBaseline.__table__.drop(engine, checkfirst=True)
        engine.dispose()


def test_approve_baseline_persists_snapshot(session: Session) -> None:
    service = BaselineManagementService(session)
    script_id = uuid4()
    snapshot = TestResultSnapshot(
        script_id=script_id,
        status="passed",
        metrics={"pass_rate": 0.93},
    )

    approved_by = uuid4()
    record = service.approve_baseline(snapshot=snapshot, approved_by=approved_by, note="Initial baseline")

    assert record.version == 1
    assert record.snapshot.status == "passed"
    assert record.snapshot.metrics["pass_rate"] == pytest.approx(0.93)
    assert record.approved_by == approved_by
    assert record.approved_at is not None

    fetched = service.get_baseline(script_id)
    assert fetched is not None
    assert fetched.version == 1
    assert fetched.snapshot.status == "passed"
    assert fetched.snapshot.metrics["pass_rate"] == pytest.approx(0.93)


def test_reapproving_baseline_increments_version_and_updates_metadata(session: Session) -> None:
    service = BaselineManagementService(session)
    script_id = uuid4()

    initial_snapshot = TestResultSnapshot(
        script_id=script_id,
        status="passed",
        metrics={"pass_rate": 0.95},
    )
    first_approver = uuid4()
    service.approve_baseline(snapshot=initial_snapshot, approved_by=first_approver, note="Initial")

    updated_snapshot = TestResultSnapshot(
        script_id=script_id,
        status="passed",
        metrics={"pass_rate": 0.98, "latency_ms": 120},
    )
    second_approver = uuid4()
    record = service.approve_baseline(snapshot=updated_snapshot, approved_by=second_approver, note="Improved run")

    assert record.version == 2
    assert record.snapshot.metrics["pass_rate"] == pytest.approx(0.98)
    assert record.snapshot.metrics["latency_ms"] == 120
    assert record.approved_by == second_approver
    assert record.note == "Improved run"

    fetched = service.get_baseline(script_id)
    assert fetched is not None
    assert fetched.version == 2
    assert fetched.snapshot.metrics["pass_rate"] == pytest.approx(0.98)
    assert fetched.snapshot.metrics["latency_ms"] == 120
    assert fetched.approved_by == second_approver
    assert fetched.note == "Improved run"
