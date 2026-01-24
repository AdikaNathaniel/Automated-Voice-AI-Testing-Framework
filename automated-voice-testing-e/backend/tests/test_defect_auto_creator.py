"""Tests for the automatic defect creation helper."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from unittest.mock import AsyncMock

import pytest

from services.defect_auto_creator import DefectAutoCreator
from services.defect_categorizer import DefectCategorizer


class DummyExecution:
    """Lightweight stand-in for MultiTurnExecution used in unit tests."""

    def __init__(
        self,
        *,
        script_id: UUID | None,
        execution_id: UUID | None = None,
        language_code: str = "en-US",
        context: dict[str, Any] | None = None,
    ):
        self.id = execution_id or uuid4()
        self.script_id = script_id
        self._audio_params: dict[str, str] = {}
        if script_id is not None:
            self._audio_params["script_id"] = str(script_id)
        self._audio_params["language_code"] = language_code
        self._context = dict(context or {})

    def get_audio_param(self, key: str):
        return self._audio_params.get(key)

    def get_all_context(self) -> dict[str, Any]:
        return dict(self._context)


class DummyValidationResult:
    """Minimal validation result stand-in for auto-defect tests."""

    def __init__(
        self,
        *,
        command_kind_match_score: float | None = None,
    ):
        self.command_kind_match_score = command_kind_match_score


@pytest.mark.asyncio
async def test_auto_creator_triggers_defect_after_threshold():
    """The helper should create a defect after the configured number of failures."""
    script_id = uuid4()
    execution = DummyExecution(script_id=script_id)
    validation_result = DummyValidationResult(command_kind_match_score=1.0)
    detected_at = datetime(2024, 1, 10, tzinfo=timezone.utc)

    create_defect = AsyncMock(return_value={"id": uuid4()})
    creator = DefectAutoCreator(
        create_defect=create_defect,
        failure_threshold=3,
        clock=lambda: detected_at,
        categorizer=DefectCategorizer(),
    )

    # First two failures should accumulate without creating a defect.
    assert await creator.record_validation_outcome(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_fail",
    ) is None
    assert await creator.record_validation_outcome(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_fail",
    ) is None

    # Third consecutive failure should create a defect.
    defect = await creator.record_validation_outcome(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_fail",
    )

    assert defect == create_defect.return_value
    create_defect.assert_awaited_once()

    args, kwargs = create_defect.await_args
    assert not args
    payload = kwargs["data"]
    assert payload["script_id"] == script_id
    assert payload["execution_id"] == execution.id
    assert payload["language_code"] == "en-US"
    assert payload["severity"] == "high"
    assert payload["category"] == "edge_case"  # No specific issue found
    assert payload["status"] == "open"
    assert payload["detected_at"] == detected_at
    assert "Automatic defect detected after 3 consecutive auto_fail results" in payload["description"]
    assert payload["title"].startswith("Repeated failure detected for scenario")


@pytest.mark.asyncio
async def test_auto_creator_resets_on_non_failure():
    """Non-failure review statuses should reset the streak counter."""
    script_id = uuid4()
    execution = DummyExecution(script_id=script_id)
    validation_result = DummyValidationResult()

    create_defect = AsyncMock()
    creator = DefectAutoCreator(create_defect=create_defect, failure_threshold=3, categorizer=DefectCategorizer())

    # Two failures, then a non-failure should reset the streak.
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_pass")

    # After reset, it should take three more failures to trigger creation.
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    assert create_defect.await_count == 0

    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    create_defect.assert_awaited_once()


@pytest.mark.asyncio
async def test_auto_creator_skips_when_script_id_unknown():
    """If the execution lacks a resolvable script_id the helper should no-op."""
    execution = DummyExecution(script_id=None)
    validation_result = DummyValidationResult()

    create_defect = AsyncMock()
    creator = DefectAutoCreator(create_defect=create_defect, failure_threshold=3, categorizer=DefectCategorizer())

    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")
    await creator.record_validation_outcome(execution=execution, validation_result=validation_result, review_status="auto_fail")

    create_defect.assert_not_awaited()


@pytest.mark.asyncio
async def test_auto_creator_applies_audio_category():
    """Audio related context should result in an audio category."""
    script_id = uuid4()
    execution = DummyExecution(script_id=script_id, context={"audio_error": "mic_disconnected"})
    validation_result = DummyValidationResult(command_kind_match_score=1.0)

    create_defect = AsyncMock(return_value={"id": uuid4()})
    creator = DefectAutoCreator(
        create_defect=create_defect,
        failure_threshold=1,
        categorizer=DefectCategorizer(),
    )

    defect = await creator.record_validation_outcome(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_fail",
    )

    assert defect == create_defect.return_value
    payload = create_defect.await_args.kwargs["data"]
    assert payload["category"] == "audio"


@pytest.mark.asyncio
async def test_auto_creator_applies_command_mismatch_category():
    """Command kind mismatch should result in command_mismatch category."""
    script_id = uuid4()
    execution = DummyExecution(script_id=script_id)
    validation_result = DummyValidationResult(command_kind_match_score=0.0)

    create_defect = AsyncMock(return_value={"id": uuid4()})
    creator = DefectAutoCreator(
        create_defect=create_defect,
        failure_threshold=1,
        categorizer=DefectCategorizer(),
    )

    defect = await creator.record_validation_outcome(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_fail",
    )

    assert defect == create_defect.return_value
    payload = create_defect.await_args.kwargs["data"]
    assert payload["category"] == "command_mismatch"
