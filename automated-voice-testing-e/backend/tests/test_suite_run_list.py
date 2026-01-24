import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock

import pytest

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-access")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-secret")

from services import orchestration_service
from api.routes.suite_runs import (
    list_suite_runs as list_suite_runs_route,
    get_test_executions,
)


class FakeResult:
    def __init__(self, *, value=None, items=None):
        self._value = value
        self._items = items

    def scalar_one(self):
        if self._value is None:
            raise AssertionError("scalar_one called on list result")
        return self._value

    def scalars(self):
        if self._items is None:
            raise AssertionError("scalars called on scalar result")
        return SimpleNamespace(all=lambda: list(self._items))

    def fetchall(self):
        if self._items is None:
            return []
        return list(self._items)


class FakeSession:
    def __init__(self, results):
        self._results = list(results)
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        if not self._results:
            raise AssertionError("No more fake results configured")
        return self._results.pop(0)


@pytest.mark.asyncio
async def test_list_test_runs_service_applies_filters_and_pagination():
    now = datetime.now(timezone.utc)
    run_1 = SimpleNamespace(id=uuid4(),
        suite_id=uuid4(),
        status="completed",
        created_by=uuid4(),
        created_at=now,
        started_at=now - timedelta(minutes=5),
        completed_at=now,
        total_tests=10,
        passed_tests=9,
        failed_tests=1,
        skipped_tests=0,
        trigger_metadata={"languageCode": "en-US"},
    )

    fake_session = FakeSession(
        [
            FakeResult(value=1),
            FakeResult(items=[run_1]),
            FakeResult(items=[]),
        ]
    )

    runs, total = await orchestration_service.list_test_runs(
        db=fake_session,
        suite_id=run_1.suite_id,
        status_filter="completed",
        created_by=run_1.created_by,
        start_date=now - timedelta(days=1),
        end_date=now + timedelta(days=1),
        skip=5,
        limit=10,
    )

    assert total == 1
    assert runs == [run_1]
    assert len(fake_session.statements) == 3


@pytest.mark.asyncio
async def test_list_test_runs_service_filters_by_language():
    now = datetime.now(timezone.utc)
    run_1 = SimpleNamespace(id=uuid4(),
        suite_id=uuid4(),
        status="completed",
        created_at=now,
    )

    fake_session = FakeSession(
        [
            FakeResult(value=1),
            FakeResult(items=[run_1]),
            FakeResult(items=[]),
        ]
    )

    await orchestration_service.list_test_runs(
        db=fake_session,
        language_code="ja-JP",
    )

    assert len(fake_session.statements) == 3
    compiled = str(fake_session.statements[0].compile(compile_kwargs={"literal_binds": True}))
    assert "multi_turn_executions" in compiled.lower()
    assert "ja-JP" in compiled


@pytest.mark.asyncio
async def test_list_test_runs_route_serializes_payload(monkeypatch):
    run = SimpleNamespace(id=uuid4(),
        suite_id=uuid4(),
        status="running",
        started_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        completed_at=None,
        total_tests=42,
        passed_tests=20,
        failed_tests=5,
        skipped_tests=17,
        trigger_metadata={"languageCode": "fr-FR"},
    )
    mock_service = AsyncMock(return_value=([run], 1))
    monkeypatch.setattr(orchestration_service, "list_test_runs", mock_service)

    tenant_id = uuid4()
    current_user = SimpleNamespace(id=uuid4(), tenant_id=tenant_id)
    response = await list_suite_runs_route(
        db=object(),
        current_user=current_user,
        suite_id=None,
        status_filter=None,
        created_by=None,
        start_date=None,
        end_date=None,
        skip=0,
        limit=50,
        language_code=None,
    )

    assert response["total"] == 1
    assert response["skip"] == 0
    assert response["limit"] == 50
    mock_service.assert_awaited_once()
    assert mock_service.await_args.kwargs["tenant_id"] == tenant_id
    assert len(response["runs"]) == 1
    payload = response["runs"][0]
    assert payload["id"] == str(run.id)
    assert payload["testSuiteId"] == str(run.suite_id)
    assert payload["languageCode"] == "fr-FR"
    assert payload["totalTests"] == 42


@pytest.mark.asyncio
async def test_list_test_runs_route_passes_language_code(monkeypatch):
    mock_service = AsyncMock(return_value=([], 0))
    monkeypatch.setattr(orchestration_service, "list_test_runs", mock_service)

    await list_suite_runs_route(
        db=object(),
        current_user=SimpleNamespace(id=uuid4(), tenant_id=uuid4()),
        suite_id=None,
        status_filter=None,
        created_by=None,
        start_date=None,
        end_date=None,
        skip=0,
        limit=25,
        language_code="es-ES",
    )

    assert mock_service.await_args.kwargs["language_code"] == "es-ES"


@pytest.mark.asyncio
async def test_list_test_runs_route_uses_derived_language(monkeypatch):
    run = SimpleNamespace(id=uuid4(),
        suite_id=uuid4(),
        status="completed",
        started_at=None,
        completed_at=None,
        total_tests=5,
        passed_tests=3,
        failed_tests=2,
        skipped_tests=0,
        trigger_metadata={},
        _derived_language_code="ja-JP",
    )
    mock_service = AsyncMock(return_value=([run], 1))
    monkeypatch.setattr(orchestration_service, "list_test_runs", mock_service)

    response = await list_suite_runs_route(
        db=object(),
        current_user=SimpleNamespace(id=uuid4(), tenant_id=uuid4()),
        suite_id=None,
        status_filter=None,
        created_by=None,
        start_date=None,
        end_date=None,
        skip=0,
        limit=25,
        language_code=None,
    )

    assert response["runs"][0]["languageCode"] == "ja-JP"


@pytest.mark.asyncio
async def test_get_test_run_executions_service_uses_filters():
    run_id = uuid4()
    execution = SimpleNamespace(id=uuid4(), status="completed")
    fake_session = FakeSession(
        [
            FakeResult(items=[execution]),
            FakeResult(items=[]),
        ]
    )

    executions = await orchestration_service.get_test_run_executions(
        db=fake_session,
        test_run_id=run_id,
        status_filter="completed",
    )

    assert executions == [execution]
    assert len(fake_session.statements) == 2


@pytest.mark.asyncio
async def test_get_test_run_executions_enriches_validation_metadata():
    run_id = uuid4()
    exec_id = uuid4()
    test_case_id = uuid4()
    execution = SimpleNamespace(id=exec_id,
        test_run_id=run_id,
        test_case_id=test_case_id,
        created_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
        status="pending",
    )
    queue_pending = SimpleNamespace(id=uuid4(), status="pending")
    queue_completed = SimpleNamespace(id=uuid4(), status="completed")
    human_pending = SimpleNamespace(id=uuid4(), submitted_at=None)
    human_completed = SimpleNamespace(id=uuid4(),
        submitted_at=datetime(2024, 1, 1, 1, 0, tzinfo=timezone.utc),
    )
    validation_result = SimpleNamespace(id=uuid4(),
        multi_turn_execution_id=exec_id,
        review_status="needs_review",
        queue_items=[queue_completed, queue_pending],
        human_validations=[human_pending, human_completed],
    )

    fake_session = FakeSession(
        [
            FakeResult(items=[execution]),
            FakeResult(items=[validation_result]),
        ]
    )

    executions = await orchestration_service.get_test_run_executions(
        db=fake_session,
        test_run_id=run_id,
    )

    enriched = executions[0]
    assert getattr(enriched, "validation_result") is validation_result
    assert getattr(enriched, "pending_validation_queue_item").id == queue_pending.id
    assert getattr(enriched, "latest_human_validation").id == human_completed.id


@pytest.mark.asyncio
async def test_get_test_executions_route_serializes_fields(monkeypatch):
    started = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    completed = started + timedelta(seconds=5)

    class DummyExecution(SimpleNamespace):
        def get_all_response_entities(self):
            return dict(self.response_entities or {})

    validation_result = SimpleNamespace(id=uuid4(), review_status="needs_review")
    queue_item = SimpleNamespace(id=uuid4())
    human_validation = SimpleNamespace(id=uuid4())

    execution = DummyExecution(
        id=uuid4(),
        test_run_id=uuid4(),
        test_case_id=uuid4(),
        status="completed",
        language_code="es-ES",
        created_at=started,
        updated_at=completed,
        started_at=started,
        completed_at=completed,
        error_message=None,
        response_entities={"confidence": 0.91, "transcript": "hola"},
        validation_result=validation_result,
        pending_validation_queue_item=queue_item,
        latest_human_validation=human_validation,
    )

    mock_service = AsyncMock(return_value=[execution])
    monkeypatch.setattr(orchestration_service, "get_test_run_executions", mock_service)

    # Create a mock db with async get method - ensure tenant_id matches
    shared_tenant_id = uuid4()
    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=SimpleNamespace(id=execution.test_run_id, tenant_id=shared_tenant_id))

    response = await get_test_executions(
        test_run_id=execution.test_run_id,
        db=mock_db,
        current_user=SimpleNamespace(id=uuid4(), tenant_id=shared_tenant_id),
        status_filter="completed",
    )

    assert len(response) == 1
    payload = response[0]
    assert payload.language_code == "es-ES"
    assert payload.response_summary == "hola"
    assert payload.confidence_score == 0.91
    assert payload.response_time_seconds == pytest.approx(5.0)
    assert payload.validation_result_id == validation_result.id
    assert payload.validation_review_status == "needs_review"
    assert payload.pending_validation_queue_id == queue_item.id
    assert payload.latest_human_validation_id == human_validation.id
@pytest.mark.asyncio
async def test_list_test_runs_service_derives_language_from_executions():
    run = SimpleNamespace(id=uuid4(),
        suite_id=uuid4(),
        status="completed",
        created_at=datetime.now(timezone.utc),
        trigger_metadata={},
    )
    fake_session = FakeSession(
        [
            FakeResult(value=1),
            FakeResult(items=[run]),
            FakeResult(items=[SimpleNamespace(test_run_id=run.id, language_code="ja-JP")]),
        ]
    )

    runs, total = await orchestration_service.list_test_runs(db=fake_session)

    assert total == 1
    assert runs[0]._derived_language_code == "ja-JP"
