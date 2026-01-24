"""
Scheduled report Celery task tests (TASK-315).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import date
from unittest.mock import MagicMock, patch


from services.scheduled_report_service import SendEmailError

import importlib.util
import types

_REPORTING_PATH = Path(__file__).resolve().parents[1] / "tasks" / "reporting.py"
_spec = importlib.util.spec_from_file_location("tasks.reporting", _REPORTING_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("tasks", types.ModuleType("tasks"))
sys.modules["tasks.reporting"] = _module
assert _spec.loader is not None
_spec.loader.exec_module(_module)

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-123456")
os.environ.setdefault("SOUNDHOUND_API_KEY", "test-soundhound-api-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "test-soundhound-client-id")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test-aws-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test-aws-secret-key")


@patch("tasks.reporting.get_scheduled_report_service")
def test_send_scheduled_reports_task_invokes_service(mock_factory: MagicMock) -> None:
    service = MagicMock()
    mock_factory.return_value = service

    from tasks.reporting import send_scheduled_reports

    result = send_scheduled_reports(reference_date="2024-01-08")

    service.send_reports.assert_called_once_with(reference_date=date(2024, 1, 8))
    assert result["status"] == "sent"


@patch("tasks.reporting.get_scheduled_report_service")
def test_send_scheduled_reports_task_skips_without_service(mock_factory: MagicMock) -> None:
    mock_factory.return_value = None

    from tasks.reporting import send_scheduled_reports

    result = send_scheduled_reports()

    assert result == {"status": "skipped", "reason": "reporting disabled"}


@patch("tasks.reporting.get_scheduled_report_service")
def test_send_scheduled_reports_task_handles_email_error(mock_factory: MagicMock) -> None:
    service = MagicMock()
    service.send_reports.side_effect = SendEmailError("SMTP failure")
    mock_factory.return_value = service

    from tasks.reporting import send_scheduled_reports

    result = send_scheduled_reports(reference_date="2024-01-08")

    assert result["status"] == "error"
    assert "SMTP failure" in result["reason"]


@patch("tasks.reporting.ScheduledReportService")
def test_factory_creates_service_when_recipients_present(mock_service: MagicMock) -> None:
    settings = types.SimpleNamespace(
        REPORT_EMAIL_RECIPIENTS=["qa@example.com"],
        REPORT_EMAIL_SENDER="reports@example.com",
        REPORT_EMAIL_SMTP_HOST="smtp.example.com",
        REPORT_EMAIL_SMTP_PORT=587,
        REPORT_EMAIL_SMTP_USERNAME=None,
        REPORT_EMAIL_SMTP_PASSWORD=None,
        REPORT_EMAIL_USE_TLS=True,
        REPORT_EMAIL_TIMEOUT=30,
    )

    with patch("tasks.reporting.get_settings", return_value=settings):
        result = _module.get_scheduled_report_service()

    mock_service.assert_called_once()
    assert result is mock_service.return_value


def test_factory_returns_none_without_recipients() -> None:
    settings = types.SimpleNamespace(
        REPORT_EMAIL_RECIPIENTS=[],
        REPORT_EMAIL_SENDER="reports@example.com",
        REPORT_EMAIL_SMTP_HOST=None,
        REPORT_EMAIL_SMTP_PORT=587,
        REPORT_EMAIL_SMTP_USERNAME=None,
        REPORT_EMAIL_SMTP_PASSWORD=None,
        REPORT_EMAIL_USE_TLS=True,
        REPORT_EMAIL_TIMEOUT=30,
    )

    with patch("tasks.reporting.get_settings", return_value=settings):
        result = _module.get_scheduled_report_service()

    assert result is None
