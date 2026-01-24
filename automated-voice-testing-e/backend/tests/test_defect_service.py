"""Tests for the defect service business logic."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.exc import NoResultFound

# Import all models to ensure relationship resolution works
import models  # noqa: F401  - registers all models
from models.base import Base
from models.defect import Defect
from services.defect_service import (
    assign_defect,
    create_defect,
    get_defect,
    list_defects,
    resolve_defect,
    sync_defect_status_from_jira,
    update_defect,
)


@pytest_asyncio.fixture()
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    async with engine.begin() as connection:
        await connection.run_sync(_create_schema)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(_drop_schema)
    await engine.dispose()


async def _seed_defect(session: AsyncSession, **overrides) -> Defect:
    defaults = {
        "test_case_id": uuid4(),
        "test_execution_id": uuid4(),
        "severity": "high",
        "category": "semantic",
        "title": "Title",
        "description": "Desc",
        "language_code": "en",
        "detected_at": datetime.now(timezone.utc),
        "status": "open",
        "jira_issue_key": overrides.pop("jira_issue_key", None),
        "jira_issue_url": overrides.pop("jira_issue_url", None),
        "jira_status": overrides.pop("jira_status", None),
    }
    defaults.update(overrides)
    defect = Defect(**defaults)
    session.add(defect)
    await session.flush()
    return defect


def _create_schema(connection) -> None:  # type: ignore[no-untyped-def]
    for name, columns in _stub_table_definitions().items():
        if name not in Base.metadata.tables:
            table = sa.Table(name, Base.metadata, *columns)
            _STUB_TABLES[name] = table
    for table in _STUB_TABLES.values():
        table.create(connection, checkfirst=False)
    Defect.__table__.create(connection, checkfirst=False)


def _drop_schema(connection) -> None:  # type: ignore[no-untyped-def]
    Defect.__table__.drop(connection, checkfirst=True)
    for name, table in list(_STUB_TABLES.items()):
        table.drop(connection, checkfirst=True)
        Base.metadata.remove(table)
        _STUB_TABLES.pop(name, None)


def _stub_table_definitions() -> dict[str, tuple[sa.Column, ...]]:
    return {
        "test_cases": (
            sa.Column("id", sa.String(36), primary_key=True),
        ),
        "test_runs": (
            sa.Column("id", sa.String(36), primary_key=True),
        ),
        "users": (
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("email", sa.String(255), nullable=False, unique=True),
        ),
    }


_STUB_TABLES: dict[str, sa.Table] = {}


@pytest.mark.asyncio
async def test_create_defect_persists_record(db_session: AsyncSession):
    payload = {
        "test_case_id": uuid4(),
        "test_execution_id": uuid4(),
        "severity": "critical",
        "category": "timing",
        "title": "Voice delay",
        "description": "Response exceeded SLA",
        "language_code": "en",
        "detected_at": datetime(2024, 1, 10, tzinfo=timezone.utc),
        "status": "open",
    }

    defect = await create_defect(db_session, payload)

    assert defect.id is not None
    assert defect.severity == "critical"

    fetched = await get_defect(db_session, defect.id)
    assert fetched is not None
    assert fetched.title == "Voice delay"
    assert fetched.jira_issue_key is None
    assert fetched.jira_status is None


@pytest.mark.asyncio
async def test_get_defect_raises_for_missing(db_session: AsyncSession):
    with pytest.raises(NoResultFound):
        await get_defect(db_session, uuid4())


@pytest.mark.asyncio
async def test_list_defects_supports_filters_and_pagination(db_session: AsyncSession):
    await _seed_defect(db_session, severity="high", status="open")
    await _seed_defect(db_session, severity="low", status="resolved")
    await db_session.commit()

    items, total = await list_defects(
        db_session,
        filters={"status": "open"},
        pagination={"skip": 0, "limit": 10},
    )

    assert total == 1
    assert len(items) == 1
    assert items[0].status == "open"


@pytest.mark.asyncio
async def test_update_defect_applies_changes(db_session: AsyncSession):
    defect = await _seed_defect(db_session, status="open")
    await db_session.commit()

    updated = await update_defect(
        db_session,
        defect.id,
        {"status": "in_progress", "title": "Updated", "severity": "medium"},
    )

    assert updated.status == "in_progress"
    assert updated.title == "Updated"
    assert updated.severity == "medium"


@pytest.mark.asyncio
async def test_assign_defect_sets_assigned_user(db_session: AsyncSession):
    defect = await _seed_defect(db_session, status="open")
    await db_session.commit()
    user_id = uuid4()

    assigned = await assign_defect(db_session, defect.id, user_id)

    assert assigned.assigned_to == user_id
    assert assigned.status == "in_progress"


@pytest.mark.asyncio
async def test_resolve_defect_updates_status_and_resolution(db_session: AsyncSession):
    defect = await _seed_defect(db_session, status="in_progress")
    await db_session.commit()

    resolved = await resolve_defect(db_session, defect.id, "Fixed in release 1.2")

    assert resolved.status == "resolved"
    assert resolved.resolved_at is not None
    assert resolved.description.endswith("Fixed in release 1.2")


@pytest.mark.asyncio
async def test_defect_to_dict_includes_jira_fields(db_session: AsyncSession):
    defect = await _seed_defect(
        db_session,
        jira_issue_key="QA-123",
        jira_issue_url="https://example.atlassian.net/browse/QA-123",
        jira_status="In Progress",
    )

    as_dict = defect.to_dict()
    assert as_dict["jira_issue_key"] == "QA-123"
    assert as_dict["jira_issue_url"] == "https://example.atlassian.net/browse/QA-123"
    assert as_dict["jira_status"] == "In Progress"


@pytest.mark.asyncio
async def test_update_defect_pushes_status_to_jira(db_session: AsyncSession):
    defect = await _seed_defect(
        db_session,
        status="open",
        jira_issue_key="QA-123",
        jira_status="To Do",
    )
    await db_session.commit()

    jira_client = AsyncMock()

    updated = await update_defect(
        db_session,
        defect.id,
        {"status": "in_progress"},
        jira_client=jira_client,
    )

    jira_client.update_issue.assert_awaited_once()
    args, kwargs = jira_client.update_issue.await_args
    assert kwargs["issue_key"] == "QA-123"
    assert kwargs["data"]["fields"]["status"] == {"name": "In Progress"}
    assert updated.jira_status == "In Progress"


@pytest.mark.asyncio
async def test_sync_defect_status_from_jira_updates_local_record(db_session: AsyncSession):
    defect = await _seed_defect(
        db_session,
        status="in_progress",
        jira_issue_key="QA-123",
        jira_status="In Progress",
    )
    await db_session.commit()

    jira_client = AsyncMock()
    jira_client.get_issue.return_value = {
        "key": "QA-123",
        "fields": {"status": {"name": "Done"}},
    }

    synced = await sync_defect_status_from_jira(db_session, defect.id, jira_client=jira_client)

    jira_client.get_issue.assert_awaited_once_with(issue_key="QA-123", params={"fields": "status"})
    assert synced.status == "resolved"
    assert synced.jira_status == "Done"
@pytest.mark.asyncio
async def test_create_defect_creates_jira_issue_when_client_provided(db_session: AsyncSession):
    payload = {
        "test_case_id": uuid4(),
        "test_execution_id": uuid4(),
        "severity": "high",
        "category": "semantic",
        "title": "Transcript mismatch",
        "description": "Expected phrase differs from recognition.",
        "language_code": "en",
        "detected_at": datetime(2024, 5, 1, tzinfo=timezone.utc),
        "status": "open",
    }

    jira_client = AsyncMock()
    jira_client.create_issue.return_value = "QA-456"

    defect = await create_defect(
        db_session,
        payload,
        jira_client=jira_client,
        jira_project_key="QA",
        jira_issue_type="Bug",
        jira_browse_base_url="https://example.atlassian.net",
    )

    jira_client.create_issue.assert_awaited_once()
    args, kwargs = jira_client.create_issue.await_args
    assert kwargs["project"] == "QA"
    assert kwargs["data"]["summary"] == "Transcript mismatch"
    assert kwargs["data"]["issuetype"] == {"name": "Bug"}
    assert defect.jira_issue_key == "QA-456"
    assert defect.jira_issue_url == "https://example.atlassian.net/browse/QA-456"
    assert defect.jira_status == "To Do"
