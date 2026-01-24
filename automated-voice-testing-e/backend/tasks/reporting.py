"""
Reporting Celery tasks (TASK-315).
"""

from __future__ import annotations

import logging
import smtplib
from datetime import date
from email.message import EmailMessage
from typing import Iterable, List, Optional

from api.config import get_settings
from celery_app import celery
from services.pdf_report_service import PDFReportService
from services.report_generator_service import ReportGeneratorService
from services.scheduled_report_service import (
    EmailAttachment,
    ScheduledReportService,
    SendEmailError,
)

logger = logging.getLogger(__name__)


@celery.task(name="tasks.reporting.send_scheduled_reports")
def send_scheduled_reports(*, reference_date: str | None = None) -> dict:
    """
    Celery entrypoint that generates and emails scheduled executive reports.
    """
    service = get_scheduled_report_service()
    if service is None:
        return {"status": "skipped", "reason": "reporting disabled"}

    try:
        target_date = _parse_reference_date(reference_date)
    except ValueError as exc:
        logger.error("Invalid reference date supplied to reporting task: %s", exc)
        return {"status": "error", "reason": str(exc)}

    try:
        service.send_reports(reference_date=target_date)
    except SendEmailError as exc:
        logger.error("Scheduled report email failed: %s", exc)
        return {"status": "error", "reason": str(exc)}

    logger.info("Scheduled reports generated for %s", target_date.isoformat())
    return {"status": "sent", "reference_date": target_date.isoformat()}


def get_scheduled_report_service() -> Optional[ScheduledReportService]:
    """
    Build the ScheduledReportService from application configuration.
    Returns None if reporting is not fully configured.
    """
    settings = get_settings()
    recipients = _normalise_recipients(getattr(settings, "REPORT_EMAIL_RECIPIENTS", []))
    sender = getattr(settings, "REPORT_EMAIL_SENDER", None)
    smtp_host = getattr(settings, "REPORT_EMAIL_SMTP_HOST", None)

    if not recipients:
        logger.info("Scheduled report recipients not configured; skipping.")
        return None

    if not sender:
        logger.warning("REPORT_EMAIL_SENDER is not configured; skipping scheduled reports.")
        return None

    if not smtp_host:
        logger.warning("SMTP host missing for scheduled reports; skipping.")
        return None

    email_sender = _build_email_sender(
        sender=sender,
        host=smtp_host,
        port=getattr(settings, "REPORT_EMAIL_SMTP_PORT", 587),
        username=getattr(settings, "REPORT_EMAIL_SMTP_USERNAME", None),
        password=getattr(settings, "REPORT_EMAIL_SMTP_PASSWORD", None),
        use_tls=getattr(settings, "REPORT_EMAIL_USE_TLS", True),
        timeout=getattr(settings, "REPORT_EMAIL_TIMEOUT", 30),
    )

    report_generator = ReportGeneratorService(
        execution_summary_provider=_default_summary_provider,
        trend_provider=_default_trend_provider,
        risk_provider=_default_risk_provider,
    )

    pdf_renderer = PDFReportService()

    return ScheduledReportService(
        report_generator=report_generator,
        pdf_renderer=pdf_renderer,
        email_sender=email_sender,
        recipients=recipients,
        sender=sender,
    )


def _parse_reference_date(reference_date: Optional[str]) -> date:
    if reference_date is None:
        return date.today()
    try:
        return date.fromisoformat(reference_date)
    except ValueError as exc:
        raise ValueError(f"Invalid reference date '{reference_date}'") from exc


def _normalise_recipients(recipients: Iterable[str]) -> List[str]:
    return [recipient.strip() for recipient in recipients if recipient and recipient.strip()]


def _build_email_sender(
    *,
    sender: str,
    host: str,
    port: int,
    username: Optional[str],
    password: Optional[str],
    use_tls: bool,
    timeout: int,
):
    def _send_email(
        *,
        subject: str,
        body: str,
        recipients: Iterable[str],
        attachments: Iterable[EmailAttachment],
    ) -> None:
        message = EmailMessage()
        recipient_list = list(recipients)

        if not recipient_list:
            raise SendEmailError("No recipients configured for scheduled reports.")

        message["Subject"] = subject
        message["From"] = sender
        message["To"] = ", ".join(recipient_list)
        message.set_content(body)

        for attachment in attachments:
            maintype, subtype = _split_mimetype(attachment.mimetype)
            message.add_attachment(
                attachment.content,
                maintype=maintype,
                subtype=subtype,
                filename=attachment.filename,
            )

        try:
            with smtplib.SMTP(host, port, timeout=timeout) as smtp:
                if use_tls:
                    smtp.starttls()
                if username and password:
                    smtp.login(username, password)
                smtp.send_message(message)
        except Exception as exc:  # pragma: no cover - network failure paths
            raise SendEmailError(f"Failed to send scheduled report email: {exc}") from exc

    return _send_email


def _split_mimetype(mimetype: str) -> tuple[str, str]:
    if "/" in mimetype:
        maintype, subtype = mimetype.split("/", 1)
        return maintype or "application", subtype or "octet-stream"
    return "application", "octet-stream"


def _default_summary_provider(start: date, end: date) -> dict:
    return {
        "total_executions": 0,
        "pass_rate": 0.0,
        "defects_found": 0,
        "mean_response_time_ms": 0,
        "summary": f"No execution data available from {start} to {end}.",
        "period": {"start": start, "end": end},
    }


def _default_trend_provider(start: date, end: date) -> dict:
    return {}


def _default_risk_provider(limit: int) -> list:
    return []
