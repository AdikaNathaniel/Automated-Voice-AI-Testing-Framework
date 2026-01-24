"""
Execution resource monitoring utilities.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class ResourceSnapshot:
    """
    Represents a point-in-time snapshot of resource usage.
    """

    cpu_percent: float
    memory_mb: float


class ResourceLimitExceeded(RuntimeError):
    """
    Raised when resource limits are exceeded.
    """


def _default_usage_provider() -> ResourceSnapshot:
    """
    Default resource usage provider leveraging psutil when available.

    Falls back to load average and process RSS if psutil is missing.
    """
    try:
        import psutil  # type: ignore

        process = psutil.Process()
        cpu = psutil.cpu_percent(interval=None)
        memory_mb = process.memory_info().rss / (1024 * 1024)
        return ResourceSnapshot(cpu_percent=float(cpu), memory_mb=float(memory_mb))
    except Exception:  # pragma: no cover - fallback path
        cpu_percent = 0.0
        if hasattr(os, "getloadavg"):
            try:
                load1, _, _ = os.getloadavg()
                cpu_percent = float(load1) * 100
            except OSError:
                cpu_percent = 0.0

        try:
            import resource  # type: ignore

            usage = resource.getrusage(resource.RUSAGE_SELF)
            memory_mb = float(usage.ru_maxrss) / 1024.0
        except Exception:
            memory_mb = 0.0

        return ResourceSnapshot(cpu_percent=cpu_percent, memory_mb=memory_mb)


class ExecutionResourceMonitor:
    """
    Monitors system resource usage and enforces execution limits.
    """

    def __init__(
        self,
        *,
        cpu_limit_percent: Optional[float],
        memory_limit_mb: Optional[int],
        usage_provider: Optional[Callable[[], ResourceSnapshot]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self._cpu_limit = cpu_limit_percent if cpu_limit_percent and cpu_limit_percent > 0 else None
        self._memory_limit = memory_limit_mb if memory_limit_mb and memory_limit_mb > 0 else None
        self._usage_provider = usage_provider or _default_usage_provider
        self._logger = logger or logging.getLogger(__name__)

    def ensure_capacity(self) -> ResourceSnapshot:
        """
        Returns a snapshot when within limits, otherwise raises ResourceLimitExceeded.
        """
        snapshot = self._usage_provider()

        if self._cpu_limit is not None and snapshot.cpu_percent > self._cpu_limit:
            self._logger.warning(
                "CPU usage %.2f%% exceeds limit %.2f%%", snapshot.cpu_percent, self._cpu_limit
            )
            raise ResourceLimitExceeded(
                f"CPU usage {snapshot.cpu_percent:.2f}% exceeds limit {self._cpu_limit:.2f}%"
            )

        if self._memory_limit is not None and snapshot.memory_mb > self._memory_limit:
            self._logger.warning(
                "Memory usage %.2f MB exceeds limit %d MB", snapshot.memory_mb, self._memory_limit
            )
            raise ResourceLimitExceeded(
                f"Memory usage {snapshot.memory_mb:.2f} MB exceeds limit {self._memory_limit} MB"
            )

        return snapshot

    def within_limits(self) -> bool:
        """
        Returns True when usage is within limits.
        """
        try:
            self.ensure_capacity()
            return True
        except ResourceLimitExceeded:
            return False

    @classmethod
    def from_settings(cls, settings) -> "ExecutionResourceMonitor":
        """
        Build a monitor using Settings configuration.
        """
        return cls(
            cpu_limit_percent=getattr(settings, "EXECUTION_CPU_LIMIT_PERCENT", None),
            memory_limit_mb=getattr(settings, "EXECUTION_MEMORY_LIMIT_MB", None),
        )
