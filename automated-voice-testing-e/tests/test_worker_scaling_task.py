"""
Tests for the Celery worker auto-scaling task wiring.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import os
import pytest
import sys
import types

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "dummy-secret-key-123456")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-soundhound-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-soundhound-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-aws-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-aws-secret")

sys.modules.setdefault("tasks.validation", types.ModuleType("tasks.validation"))

from services.worker_scaling_service import AutoScalingDecision
from tasks import worker_scaling


class _Settings:
    ENABLE_AUTO_SCALING: bool = False
    MIN_WORKERS: int = 1
    MAX_WORKERS: int = 5
    AUTO_SCALING_TARGET_TASKS_PER_WORKER: int = 10
    AUTO_SCALING_SCALE_DOWN_THRESHOLD: int = 0
    AUTO_SCALING_COOLDOWN_SECONDS: int = 30
    AUTO_SCALING_QUEUE_NAME: str = "default"


def _patch_settings(monkeypatch: pytest.MonkeyPatch, *, enabled: bool) -> _Settings:
    settings = _Settings()
    settings.ENABLE_AUTO_SCALING = enabled
    monkeypatch.setattr(worker_scaling, "get_settings", lambda: settings)
    return settings


def test_auto_scale_workers_task_skips_when_disabled(monkeypatch: pytest.MonkeyPatch):
    _patch_settings(monkeypatch, enabled=False)
    scaler_cls = MagicMock()
    monkeypatch.setattr(worker_scaling, "CeleryWorkerAutoScaler", scaler_cls)

    result = worker_scaling.auto_scale_workers.run()

    scaler_cls.assert_not_called()
    assert result == {"status": "disabled"}


def test_auto_scale_workers_task_invokes_scaler(monkeypatch: pytest.MonkeyPatch):
    settings = _patch_settings(monkeypatch, enabled=True)

    scaler_instance = MagicMock()
    scaler_instance.evaluate_and_scale.return_value = AutoScalingDecision(
        queue_depth=12,
        active_workers=3,
        target_workers=4,
        scaled=True,
        scale_direction="grow",
    )

    scaler_cls = MagicMock(return_value=scaler_instance)
    monkeypatch.setattr(worker_scaling, "CeleryWorkerAutoScaler", scaler_cls)

    result = worker_scaling.auto_scale_workers.run()

    scaler_cls.assert_called_once_with(
        celery_app=worker_scaling.celery,
        min_workers=settings.MIN_WORKERS,
        max_workers=settings.MAX_WORKERS,
        target_tasks_per_worker=settings.AUTO_SCALING_TARGET_TASKS_PER_WORKER,
        scale_down_queue_threshold=settings.AUTO_SCALING_SCALE_DOWN_THRESHOLD,
        cooldown_seconds=settings.AUTO_SCALING_COOLDOWN_SECONDS,
        queue_name=settings.AUTO_SCALING_QUEUE_NAME,
    )
    scaler_instance.evaluate_and_scale.assert_called_once_with()
    assert result == {
        "queue_depth": 12,
        "active_workers": 3,
        "target_workers": 4,
        "scaled": True,
        "direction": "grow",
    }
