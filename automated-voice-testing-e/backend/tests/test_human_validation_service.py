from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from services.human_validation_service import HumanValidationService


class DummySession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.refreshed = []
        self._counts = {}

    def add(self, obj):
        self.added.append(obj)

    async def commit(self):
        self.committed = True

    async def refresh(self, obj):
        self.refreshed.append(obj)

    async def execute(self, stmt):
        key = ("performed", tuple(stmt.compile().params.items()))
        count = self._counts.get(key, 0)
        if count == 0:
            pass
        else:
            SimpleNamespace(search_key=key)
        self._counts[key] = count + 1
        return SimpleNamespace(scalar_one_or_none=lambda: None)


@pytest.mark.asyncio
async def test_submit_decision_updates_queue_and_returns_payload(monkeypatch):
    queue_id = uuid4()
    validator_id = uuid4()
    queue_item = SimpleNamespace(id=queue_id,
        validation_result_id=uuid4(),
        status="claimed",
        claimed_by=validator_id,
        claimed_at=None,
    )

    dummy_human_records = []

    class DummyHumanValidation(SimpleNamespace):
        pass

    def fake_human_validation(**kwargs):
        record = DummyHumanValidation(id=uuid4(), **kwargs)
        dummy_human_records.append(record)
        return record

    monkeypatch.setattr(
        "services.human_validation_service.HumanValidation",
        fake_human_validation,
    )

    service = HumanValidationService()

    async def fake_get_queue_item(db, qid, tenant_id=None):
        return queue_item

    monkeypatch.setattr(service, "_get_queue_item", fake_get_queue_item)

    perf_updates = []

    async def fake_update_performance(**kwargs):
        perf_updates.append(kwargs)

    monkeypatch.setattr(
        service,
        "_update_validator_performance",
        fake_update_performance,
    )

    session = DummySession()
    payload = SimpleNamespace(
        validation_decision="fail",
        feedback="Intent mismatch",
        time_spent_seconds=42,
    )

    result = await service.submit_decision(session, queue_id, validator_id, payload)

    assert queue_item.status == "completed"
    assert session.committed is True
    assert dummy_human_records[0].validation_decision == "fail"
    assert result["decision"] == "fail"
    assert perf_updates and perf_updates[0]["validator_id"] == validator_id


def test_ensure_queue_claim_validations():
    queue_item = SimpleNamespace(status="pending", claimed_by=uuid4())
    service = HumanValidationService()

    with pytest.raises(HTTPException):
        service._ensure_queue_claim(queue_item, uuid4())

    queue_item.status = "claimed"
    queue_item.claimed_by = uuid4()
    with pytest.raises(HTTPException):
        service._ensure_queue_claim(queue_item, uuid4())


@pytest.mark.asyncio
async def test_submit_decision_edge_case_sends_notification(monkeypatch):
    """Edge case decisions trigger notification after commit."""
    from unittest.mock import AsyncMock

    queue_id = uuid4()
    validator_id = uuid4()
    edge_case_id = uuid4()

    queue_item = SimpleNamespace(
        id=queue_id,
        validation_result_id=uuid4(),
        status="claimed",
        claimed_by=validator_id,
        claimed_at=None,
    )

    dummy_human_records = []

    class DummyHumanValidation(SimpleNamespace):
        pass

    def fake_human_validation(**kwargs):
        record = DummyHumanValidation(id=uuid4(), **kwargs)
        dummy_human_records.append(record)
        return record

    monkeypatch.setattr(
        "services.human_validation_service.HumanValidation",
        fake_human_validation,
    )

    # Mock edge case creation
    edge_case = SimpleNamespace(
        id=edge_case_id,
        title="Test Edge Case",
        category="ambiguous_intent",
        severity="high",
        scenario_definition={"scenario_name": "Test Scenario"},
    )

    async def fake_create_edge_case(**kwargs):
        return edge_case

    service = HumanValidationService()
    monkeypatch.setattr(service, "_create_edge_case_entry", fake_create_edge_case)

    async def fake_get_queue_item(db, qid, tenant_id=None):
        return queue_item

    monkeypatch.setattr(service, "_get_queue_item", fake_get_queue_item)

    async def fake_update_performance(**kwargs):
        pass

    monkeypatch.setattr(service, "_update_validator_performance", fake_update_performance)

    # Track notification calls
    notification_calls = []

    async def fake_send_notification(db, edge_case_data, tenant_id=None):
        notification_calls.append(edge_case_data)

    monkeypatch.setattr(service, "_send_edge_case_notification", fake_send_notification)

    session = DummySession()
    payload = SimpleNamespace(
        validation_decision="edge_case",
        feedback="Unclear user intent",
        time_spent_seconds=30,
    )

    result = await service.submit_decision(session, queue_id, validator_id, payload)

    assert result["edge_case_id"] == str(edge_case_id)
    assert len(notification_calls) == 1
    assert notification_calls[0]["id"] == str(edge_case_id)
    assert notification_calls[0]["title"] == "Test Edge Case"
    assert notification_calls[0]["severity"] == "high"
    assert notification_calls[0]["scenario_name"] == "Test Scenario"


@pytest.mark.asyncio
async def test_send_edge_case_notification_handles_errors(monkeypatch, caplog):
    """Notification errors are logged but don't fail the flow."""
    import logging

    service = HumanValidationService()

    # Mock get_settings and get_notification_service to raise
    def fake_get_settings():
        raise RuntimeError("Config error")

    monkeypatch.setattr(
        "services.human_validation_service.get_settings",
        fake_get_settings,
        raising=False,
    )

    edge_case_data = {
        "id": "ec-123",
        "title": "Test",
        "category": "test",
        "severity": "high",
    }

    session = DummySession()

    with caplog.at_level(logging.WARNING):
        await service._send_edge_case_notification(session, edge_case_data)

    # Should log warning but not raise
    assert "Failed to send edge case notification" in caplog.text
