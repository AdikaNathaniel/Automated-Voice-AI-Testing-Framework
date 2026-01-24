"""
Tests for execution resource limit monitoring (TASK-284).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable
from unittest.mock import MagicMock

import sys
import os
import pytest

# Add parent directory (backend) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.execution_resource_manager import (
    ExecutionResourceMonitor,
    ResourceLimitExceeded,
    ResourceSnapshot,
)


def make_monitor(
    *,
    cpu_limit: float = 75.0,
    memory_limit: int = 1024,
    provider: Callable[[], ResourceSnapshot],
):
    return ExecutionResourceMonitor(
        cpu_limit_percent=cpu_limit,
        memory_limit_mb=memory_limit,
        usage_provider=provider,
        logger=MagicMock(),
    )


def test_monitor_allows_usage_below_limits():
    snapshot = ResourceSnapshot(cpu_percent=42.0, memory_mb=512)
    monitor = make_monitor(provider=lambda: snapshot)

    result = monitor.ensure_capacity()

    assert result is snapshot


def test_monitor_raises_when_cpu_exceeds_limit():
    monitor = make_monitor(
        cpu_limit=70.0,
        provider=lambda: ResourceSnapshot(cpu_percent=75.5, memory_mb=128),
    )

    with pytest.raises(ResourceLimitExceeded) as exc:
        monitor.ensure_capacity()

    assert "CPU" in str(exc.value)


def test_monitor_raises_when_memory_exceeds_limit():
    monitor = make_monitor(
        memory_limit=256,
        provider=lambda: ResourceSnapshot(cpu_percent=20.0, memory_mb=512),
    )

    with pytest.raises(ResourceLimitExceeded) as exc:
        monitor.ensure_capacity()

    assert "memory" in str(exc.value).lower()
