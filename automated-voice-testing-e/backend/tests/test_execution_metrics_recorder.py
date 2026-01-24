"""
Tests for the ExecutionMetricsRecorder helper.

Validates that execution and validation data trigger the expected metric
recordings via MetricsService.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from services.execution_metrics_recorder import ExecutionMetricsRecorder


class StubExecution:
    """Lightweight execution object exposing the accessors used by the recorder."""

    def __init__(self) -> None:
        self.id = uuid4()
        self.test_run_id = uuid4()
        self._audio_params = {"language_code": "en-US"}
        self._context = {
            "execution_duration_ms": 2400,
            "response_time_ms": 900,
        }

    def get_audio_param(self, key: str):
        return self._audio_params.get(key)

    def get_all_context(self):
        return dict(self._context)


@pytest.mark.asyncio
async def test_recorder_emits_core_metrics(monkeypatch: pytest.MonkeyPatch):
    metrics_service = AsyncMock()
    fixed_time = datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)
    recorder = ExecutionMetricsRecorder(metrics_service=metrics_service, clock=lambda: fixed_time)

    invalidate_mock = AsyncMock()
    monkeypatch.setattr(
        "services.execution_metrics_recorder.invalidate_dashboard_cache", invalidate_mock
    )

    execution = StubExecution()
    validation_result = SimpleNamespace(
        accuracy_score=0.9,
        confidence_score=0.82,
    )

    await recorder.record_execution_metrics(
        execution=execution,
        validation_result=validation_result,
        review_status="auto_pass",
    )

    assert metrics_service.record_metric.await_count == 12

    recorded_calls = metrics_service.record_metric.await_args_list
    metric_flow = [
        (call.kwargs["metric_type"], call.kwargs["dimensions"]["aggregation"])
        for call in recorded_calls
    ]
    assert metric_flow == [
        ("execution_time", "raw"),
        ("execution_time", "hour"),
        ("execution_time", "day"),
        ("response_time", "raw"),
        ("response_time", "hour"),
        ("response_time", "day"),
        ("validation_confidence", "raw"),
        ("validation_confidence", "hour"),
        ("validation_confidence", "day"),
        ("validation_pass", "raw"),
        ("validation_pass", "hour"),
        ("validation_pass", "day"),
    ]

    execution_call = recorded_calls[0].kwargs
    assert execution_call["metric_value"] == pytest.approx(2.4)
    assert execution_call["timestamp"] is fixed_time
    assert execution_call["dimensions"]["aggregation"] == "raw"
    assert execution_call["dimensions"]["language_code"] == "en-US"

    pass_call = recorded_calls[-1].kwargs
    assert pass_call["metric_value"] == pytest.approx(1.0)
    assert pass_call["dimensions"]["status"] == "auto_pass"
    assert "execution_id" not in pass_call["dimensions"]
    assert pass_call["timestamp"] == fixed_time.replace(hour=0, minute=0, second=0, microsecond=0)
    invalidate_mock.assert_awaited_once()
