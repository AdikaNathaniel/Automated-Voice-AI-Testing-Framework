"""
Scheduled report generation service tests (TASK-315).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Sequence
from unittest.mock import MagicMock

import pytest

from services.scheduled_report_service import (
    EmailAttachment,
    ScheduledReportService,
    SendEmailError,
)


@dataclass
class _SentEmail:
    subject: str
    body: str
    recipients: Sequence[str]
    attachments: Sequence[EmailAttachment]


class _EmailSenderStub:
    def __init__(self) -> None:
        self.sent_messages: List[_SentEmail] = []
        self.raise_error: bool = False

    def send_email(
        self,
        *,
        subject: str,
        body: str,
        recipients: Sequence[str],
        attachments: Sequence[EmailAttachment],
    ) -> None:
        if self.raise_error:
            raise SendEmailError("SMTP failure")
        self.sent_messages.append(
            _SentEmail(
                subject=subject,
                body=body,
                recipients=list(recipients),
                attachments=list(attachments),
            )
        )


@pytest.fixture()
def email_sender() -> _EmailSenderStub:
    return _EmailSenderStub()


def test_send_scheduled_reports_weekly_only(email_sender: _EmailSenderStub) -> None:
    generator = MagicMock()
    generator.generate_weekly_report.return_value = {"summary": "Weekly summary"}
    generator.generate_monthly_report.return_value = {"summary": "Monthly summary"}

    pdf_service = MagicMock()
    pdf_service.render_report.return_value = b"%PDF-weekly"

    service = ScheduledReportService(
        report_generator=generator,
        pdf_renderer=pdf_service,
        email_sender=email_sender.send_email,
        recipients=["qa@example.com"],
        sender="reports@example.com",
    )

    service.send_reports(reference_date=date(2024, 1, 8))  # Monday

    generator.generate_weekly_report.assert_called_once_with(date(2024, 1, 8))
    generator.generate_monthly_report.assert_not_called()
    pdf_service.render_report.assert_called_once()

    assert len(email_sender.sent_messages) == 1
    sent = email_sender.sent_messages[0]
    assert sent.recipients == ["qa@example.com"]
    assert "Weekly" in sent.subject
    assert sent.attachments and sent.attachments[0].filename.endswith(".pdf")
    assert sent.attachments[0].content == b"%PDF-weekly"
    assert sent.attachments[0].mimetype == "application/pdf"


def test_send_scheduled_reports_monthly(email_sender: _EmailSenderStub) -> None:
    generator = MagicMock()
    generator.generate_weekly_report.return_value = {"summary": "Weekly summary"}
    generator.generate_monthly_report.return_value = {"summary": "Monthly summary"}

    pdf_service = MagicMock()
    pdf_service.render_report.side_effect = [
        b"%PDF-weekly",
        b"%PDF-monthly",
    ]

    service = ScheduledReportService(
        report_generator=generator,
        pdf_renderer=pdf_service,
        email_sender=email_sender.send_email,
        recipients=["qa@example.com", "cto@example.com"],
        sender="reports@example.com",
    )

    service.send_reports(reference_date=date(2024, 2, 1))  # First of month

    generator.generate_monthly_report.assert_called_once_with(date(2024, 2, 1))
    pdf_calls = pdf_service.render_report.call_args_list
    assert len(pdf_calls) == 1  # Monthly only (Feb 1 is Thursday)
    assert len(email_sender.sent_messages) == 1
    sent = email_sender.sent_messages[0]
    assert "Monthly" in sent.subject
    assert "Monthly summary" in sent.body
    assert sorted(sent.recipients) == ["cto@example.com", "qa@example.com"]


def test_email_error_raises(email_sender: _EmailSenderStub) -> None:
    generator = MagicMock()
    generator.generate_weekly_report.return_value = {"summary": "Weekly summary"}
    pdf_service = MagicMock()
    pdf_service.render_report.return_value = b"%PDF"
    email_sender.raise_error = True

    service = ScheduledReportService(
        report_generator=generator,
        pdf_renderer=pdf_service,
        email_sender=email_sender.send_email,
        recipients=["qa@example.com"],
        sender="reports@example.com",
    )

    with pytest.raises(SendEmailError):
        service.send_reports(reference_date=date(2024, 1, 8))
