"""
Unit tests for the EdgeCaseService.

Verifies CRUD operations, categorisation heuristics, and search/list helpers
behave as expected when interacting with the EdgeCase ORM model.
"""

from __future__ import annotations

from datetime import date
from typing import Iterator, List
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base

from models.edge_case import EdgeCase
from services.edge_case_service import EdgeCaseService

# Create a separate Base for test stubs to avoid conflicts with real models
TestBase = declarative_base()


class UserStub(TestBase):
    """Minimal user table to satisfy FK constraints for discovered_by."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), nullable=True)
    username = Column(String(255), nullable=False)


class TestCaseStub(TestBase):
    """Minimal test case table to satisfy FK constraints for test_case_id."""

    __tablename__ = "test_cases"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, default="stub")
    title = Column(String(255), nullable=True)


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:", future=True)

    # Create stub tables from TestBase
    TestBase.metadata.create_all(bind=engine)

    # Create EdgeCase table separately (it uses the real Base)
    EdgeCase.__table__.create(bind=engine, checkfirst=True)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = SessionLocal()
    try:
        # seed a user to satisfy FK lookups when needed
        user_id = str(uuid4())
        user = UserStub(id=user_id, email="qa@example.com", username=f"user_{user_id[:8]}")
        session.add(user)
        session.commit()
        yield session
    finally:
        session.rollback()
        session.close()

        # Drop tables in reverse order
        EdgeCase.__table__.drop(bind=engine, checkfirst=True)
        TestBase.metadata.drop_all(bind=engine)

        engine.dispose()


def _collect_ids(edge_cases: List[EdgeCase]) -> List[UUID]:
    return [edge_case.id for edge_case in edge_cases]


def test_create_edge_case_normalises_tags_and_title(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    test_case_id = str(uuid4())
    db_session.add(TestCaseStub(id=test_case_id, title="Navigation regression"))
    db_session.commit()

    edge_case = service.create_edge_case(
        title="  Ambiguous navigation near mall ",
        description="Assistant chooses wrong store when multiple options exist.",
        scenario_definition={"steps": ["Ask for nearest mall", "Expect correct store"]},
        tags=["navigation", "Ambiguity", "navigation"],
        category=None,
        severity=None,
        test_case_id=UUID(test_case_id),
        discovered_date=date(2025, 10, 20),
        discovered_by=UUID(db_session.query(UserStub.id).first()[0]),
    )

    assert edge_case.id is not None
    assert edge_case.title == "Ambiguous navigation near mall"
    assert sorted(edge_case.tags) == ["ambiguity", "navigation"]
    assert edge_case.status == "active"
    assert edge_case.scenario_definition["steps"][0].startswith("Ask for nearest")


def test_get_and_update_edge_case(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    edge_case = service.create_edge_case(
        title="Audio distortion after long prompts",
        description="Static noise after 30s utterance.",
        scenario_definition={"symptom": "static"},
        tags=["audio", "regression"],
    )

    fetched = service.get_edge_case(edge_case.id)
    assert fetched.title == "Audio distortion after long prompts"

    updated = service.update_edge_case(
        edge_case.id,
        description="Static noise after prolonged utterance (>30s).",
        tags=["audio", "regression", "quality"],
        status="resolved",
    )

    assert updated.description.endswith("(>30s).")
    assert sorted(updated.tags) == ["audio", "quality", "regression"]
    assert updated.status == "resolved"


def test_list_edge_cases_filters_and_paginates(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    service.create_edge_case(
        title="Context lost during multi-turn dialog",
        description="Assistant forgets prior answer.",
        scenario_definition={"context": "lost"},
        tags=["context", "memory"],
        category="context_loss",
        severity="high",
    )
    service.create_edge_case(
        title="Ambiguous restaurant selection",
        description="Picks wrong branch when multiple exist.",
        scenario_definition={"issue": "ambiguous"},
        tags=["navigation", "ambiguity"],
        category="ambiguity",
        severity="medium",
    )
    service.create_edge_case(
        title="Background noise misinterpretation",
        description="Car noise leads to misrecognition.",
        scenario_definition={"issue": "noise"},
        tags=["audio", "noise"],
        category="audio_quality",
        severity="high",
    )

    items, total = service.list_edge_cases(
        filters={"severity": "high", "tags": ["audio"]},
        pagination={"skip": 0, "limit": 10},
    )

    assert total == 1
    assert len(items) == 1
    assert items[0].category == "audio_quality"


def test_search_edge_cases_matches_title_description_and_tags(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    first = service.create_edge_case(
        title="Landmark confusion downtown",
        description="Assistant mixes museum and memorial.",
        scenario_definition={},
        tags=["city", "landmark"],
    )
    second = service.create_edge_case(
        title="Media playback stutter",
        description="Song buffer underflow with bluetooth.",
        scenario_definition={},
        tags=["media", "bluetooth"],
    )

    results, total = service.search_edge_cases(
        query="landmark",
        filters={"status": "active"},
        pagination={"skip": 0, "limit": 5},
    )

    assert total == 1
    assert _collect_ids(results) == [first.id]

    results, total = service.search_edge_cases(
        query="bluetooth",
        filters={},
        pagination={"skip": 0, "limit": 5},
    )
    assert total == 1
    assert _collect_ids(results) == [second.id]


def test_categorize_edge_case_derives_category_and_severity(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    edge_case = service.create_edge_case(
        title="Engine noise impacts recognition",
        description="High cabin noise reduces accuracy.",
        scenario_definition={"ambient_db": 78},
        tags=["Audio", "noise", "regression"],
        severity=None,
        category=None,
    )

    updated = service.categorize_edge_case(
        edge_case.id,
        signals={"impact_score": 0.82, "occurrence_rate": 0.4},
    )

    assert updated.category == "audio_quality"
    assert updated.severity == "high"


def test_delete_edge_case_removes_record(db_session: Session) -> None:
    service = EdgeCaseService(db_session)
    edge_case = service.create_edge_case(
        title="Fallback to default locale unexpectedly",
        description="Assistant switches to default locale mid conversation.",
        scenario_definition={},
        tags=["locale", "context"],
    )

    deleted = service.delete_edge_case(edge_case.id)
    assert deleted is True

    with pytest.raises(ValueError):
        service.get_edge_case(edge_case.id)
