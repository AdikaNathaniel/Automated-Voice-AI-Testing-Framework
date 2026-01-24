"""
Slack slash command bot utilities (TASK-330).

Provides a lightweight command dispatcher that can be wired to Slack slash
commands. The bot currently supports:
  * `/voiceai status`  – Summarise system health metrics.
  * `/voiceai run <suite_id>` – Trigger a new test run for the given suite.
  * `/voiceai defects` – List the most recent open defects.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


class SlackBot:
    """Simple Slack bot command handler."""

    STATUS_TIME_RANGE = "24h"
    DEFECT_LIMIT = 5

    def __init__(
        self,
        *,
        dashboard_service: Any,
        orchestration_service: Any,
        defect_service: Any,
    ) -> None:
        self._dashboard_service = dashboard_service
        self._orchestration_service = orchestration_service
        self._defect_service = defect_service

    async def handle_command(
        self,
        *,
        db: AsyncSession,
        text: str,
        channel_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dispatch a Slack slash command and return the formatted response payload.
        """
        command_text = (text or "").strip()
        if command_text.lower().startswith("/voiceai"):
            command_text = command_text[len("/voiceai") :].strip()

        if not command_text:
            return self._help_response()

        parts = command_text.split()
        command = parts[0].lower()
        args = parts[1:]

        if command == "status":
            return await self._status(db)
        if command == "run":
            return await self._run(db, args, channel_id=channel_id, user_id=user_id)
        if command == "defects":
            return await self._defects(db)

        return self._help_response()

    async def _status(self, db: AsyncSession) -> Dict[str, Any]:
        snapshot = await self._dashboard_service.get_dashboard_snapshot(
            db,
            time_range=self.STATUS_TIME_RANGE,
        )
        kpis = snapshot.get("kpis", {})
        health = _format_number(kpis.get("system_health_pct", 0.0))
        tests_executed = int(kpis.get("tests_executed") or 0)
        issues_detected = int(kpis.get("issues_detected") or 0)
        avg_response = _format_number(kpis.get("avg_response_time_ms", 0.0))

        lines = [
            "*Voice AI System Status*",
            f"• System health: {health}%",
            f"• Tests executed: {tests_executed}",
            f"• Issues detected: {issues_detected}",
            f"• Avg response: {avg_response}ms",
        ]
        return {
            "response_type": "ephemeral",
            "text": "\n".join(lines),
        }

    async def _run(
        self,
        db: AsyncSession,
        args: Sequence[str],
        *,
        channel_id: Optional[str],
        user_id: Optional[str],
    ) -> Dict[str, Any]:
        if not args:
            return {
                "response_type": "ephemeral",
                "text": "Provide a suite ID: `/voiceai run <suite_id>`.",
            }

        suite_token = args[0]
        try:
            suite_id = UUID(suite_token)
        except (ValueError, TypeError):
            return {
                "response_type": "ephemeral",
                "text": f"Invalid suite identifier `{suite_token}`. Provide a UUID.",
            }

        trigger_metadata = {"channel": channel_id, "user_id": user_id}
        test_run = await self._orchestration_service.create_test_run(
            db,
            suite_id=suite_id,
            trigger_type="slack_command",
            trigger_metadata=trigger_metadata,
        )

        await self._orchestration_service.schedule_test_executions(db, test_run.id)

        message = (
            f"Triggered test run `{test_run.id}` for suite `{suite_id}`. "
            f"{getattr(test_run, 'total_tests', 'Tests')} tests queued."
        )
        return {
            "response_type": "in_channel",
            "text": message,
        }

    async def _defects(self, db: AsyncSession) -> Dict[str, Any]:
        defects, total = await self._defect_service.list_defects(
            db,
            {"status": "open"},
            {"skip": 0, "limit": self.DEFECT_LIMIT},
        )

        if not defects:
            return {
                "response_type": "ephemeral",
                "text": "No open defects 🎉",
            }

        heading = f"{total} open defects (showing up to {self.DEFECT_LIMIT}):"
        items = [
            f"• {self._format_defect(defect)}"
            for defect in defects
        ]
        return {
            "response_type": "ephemeral",
            "text": "\n".join([heading, *items]),
        }

    @staticmethod
    def _format_defect(defect: Any) -> str:
        title = _safe_attr(defect, "title", default="Untitled defect")
        severity = _safe_attr(defect, "severity", default="unknown")
        status = _safe_attr(defect, "status", default="open")
        return f"[{severity.upper()}] {title} — {status}"

    @staticmethod
    def _help_response() -> Dict[str, Any]:
        return {
            "response_type": "ephemeral",
            "text": (
                "Available commands:\n"
                "• `/voiceai status` – Show system health summary.\n"
                "• `/voiceai run <suite_id>` – Trigger a test suite.\n"
                "• `/voiceai defects` – List open defects."
            ),
        }


def _format_number(value: Any) -> str:
    try:
        as_float = float(value)
    except (TypeError, ValueError):
        return "0"

    if as_float.is_integer():
        return f"{int(as_float)}"
    return f"{as_float:.1f}"


def _safe_attr(obj: Any, attr: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)
