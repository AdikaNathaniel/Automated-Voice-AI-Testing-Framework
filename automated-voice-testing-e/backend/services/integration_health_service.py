"""
Integration health monitoring service (TASK-335).

The service coordinates asynchronous health checks for external integrations
and aggregates the results into a structured report so that dashboards and
alerting pipelines can consume a consistent format.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Mapping, MutableMapping, Optional, Sequence

IntegrationStatus = str  # Literal["healthy", "degraded", "critical"] once Python 3.11+ typing finalisers available

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class IntegrationCheckResult:
    """
    Result payload returned by individual integration checkers.

    Attributes:
        integration: Identifier for the integration (e.g., "slack").
        status: Health status keyword ("healthy", "degraded", or "critical").
        detail: Human-readable summary describing the check outcome.
        metadata: Optional structured metadata (latency, error codes, etc.).
    """

    integration: str
    status: IntegrationStatus
    detail: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class IntegrationHealthResult:
    """
    Normalised representation of a single integration's health state.
    """

    integration: str
    status: IntegrationStatus
    detail: str
    metadata: Mapping[str, Any]
    checked_at: datetime


@dataclass(frozen=True)
class IntegrationHealthReport:
    """
    Aggregated health report for all integrations.

    Attributes:
        status: Overall system status derived from the worst integration outcome.
        results: Per-integration health results.
        checked_at: Timestamp when the checks were executed.
    """

    status: IntegrationStatus
    results: List[IntegrationHealthResult]
    checked_at: datetime


Checker = Callable[[], Awaitable[IntegrationCheckResult]]


class IntegrationHealthService:
    """
    Orchestrates periodic health checks across integrations.
    """

    _STATUS_SEVERITY: Mapping[str, int] = {"healthy": 0, "degraded": 1, "critical": 2}

    def __init__(
        self,
        *,
        checkers: Mapping[str, Checker],
        notification_service: Optional[Any] = None,
        clock: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._checkers: Dict[str, Checker] = dict(checkers)
        self._notification_service = notification_service
        self._clock = clock or self._default_clock

    async def run_checks(self) -> IntegrationHealthReport:
        """
        Execute all configured health checks and return the aggregated report.
        """
        checked_at = self._clock()
        results: List[IntegrationHealthResult] = []
        overall_status: IntegrationStatus = "healthy"

        for integration, checker in self._checkers.items():
            raw_result = await self._execute_checker(integration, checker)
            normalised = self._normalise_result(raw_result, fallback_integration=integration, checked_at=checked_at)
            results.append(normalised)
            if self._STATUS_SEVERITY.get(normalised.status, 2) > self._STATUS_SEVERITY.get(overall_status, 2):
                overall_status = normalised.status

        await self._maybe_alert(results=results, overall_status=overall_status)

        return IntegrationHealthReport(
            status=overall_status,
            results=results,
            checked_at=checked_at,
        )

    @staticmethod
    def _default_clock() -> datetime:
        return datetime.now(timezone.utc)

    async def _execute_checker(self, integration: str, checker: Checker) -> IntegrationCheckResult:
        try:
            return await checker()
        except Exception as exc:
            logger.exception("Integration health check failed for %s", integration)
            return IntegrationCheckResult(
                integration=integration,
                status="critical",
                detail=f"Health check failed with {exc.__class__.__name__}: {exc}",
                metadata={
                    "exception_type": exc.__class__.__name__,
                    "exception_message": str(exc),
                },
            )

    def _normalise_result(
        self,
        result: IntegrationCheckResult,
        *,
        fallback_integration: str,
        checked_at: datetime,
    ) -> IntegrationHealthResult:
        integration_name = (result.integration or fallback_integration).lower()
        metadata: MutableMapping[str, Any] = dict(result.metadata or {})
        return IntegrationHealthResult(
            integration=integration_name,
            status=result.status,
            detail=result.detail,
            metadata=metadata,
            checked_at=checked_at,
        )

    async def _maybe_alert(
        self,
        *,
        results: Sequence[IntegrationHealthResult],
        overall_status: IntegrationStatus,
    ) -> None:
        if overall_status == "healthy" or not self._notification_service:
            return

        notifier = getattr(self._notification_service, "notify_system_alert", None)
        if notifier is None:
            return

        failing = [result for result in results if result.status != "healthy"]
        if not failing:
            return

        severity = "critical" if any(result.status == "critical" for result in failing) else "warning"
        title = "Integration health check failures detected"
        lines = [
            f"- {result.integration}: {result.status} — {result.detail or 'No details provided.'}"
            for result in failing
        ]
        message = "The following integrations reported issues:\n" + "\n".join(lines)

        await notifier(
            severity=severity,
            title=title,
            message=message,
        )
