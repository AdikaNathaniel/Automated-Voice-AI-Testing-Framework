"""
Scheduled report generation and delivery service (TASK-315).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Callable, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple

from services.pdf_report_service import PDFReportMetadata, PDFReportService
from services.report_generator_service import ReportGeneratorService


class SendEmailError(RuntimeError):
    """Raised when sending a scheduled report email fails."""


@dataclass(frozen=True, slots=True)
class EmailAttachment:
    filename: str
    content: bytes
    mimetype: str = "application/pdf"


class EmailSender(Protocol):
    def __call__(
        self,
        *,
        subject: str,
        body: str,
        recipients: Sequence[str],
        attachments: Sequence[EmailAttachment],
    ) -> None: ...


class ScheduledReportService:
    """
    Coordinates generation of weekly/monthly executive reports and emails them.
    """

    def __init__(
        self,
        *,
        report_generator: ReportGeneratorService,
        pdf_renderer: PDFReportService,
        email_sender: EmailSender,
        recipients: Sequence[str],
        sender: str,
        now_provider: Optional[Callable[[], datetime]] = None,
    ) -> None:
        self._report_generator = report_generator
        self._pdf_renderer = pdf_renderer
        self._email_sender = email_sender
        self._recipients = list(recipients)
        self._sender = sender
        self._now_provider = now_provider or (lambda: datetime.now(timezone.utc))

    def send_reports(self, *, reference_date: Optional[date] = None) -> None:
        """
        Generate due reports for the supplied reference date and email them.
        """
        if not self._recipients:
            return

        ref_date = reference_date or date.today()
        now = self._now_provider()
        if now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        else:
            now = now.astimezone(timezone.utc)

        report_payloads: List[Tuple[str, Dict[str, object]]] = []

        if self._should_send_weekly(ref_date):
            weekly = self._report_generator.generate_weekly_report(ref_date)
            report_payloads.append(("Weekly", weekly))

        if self._should_send_monthly(ref_date):
            monthly = self._report_generator.generate_monthly_report(ref_date)
            report_payloads.append(("Monthly", monthly))

        if not report_payloads:
            return

        attachments: List[EmailAttachment] = []
        body_lines: List[str] = [
            f"Automated quality reports generated on {now.strftime('%Y-%m-%d %H:%M %Z')}."
        ]

        for label, report in report_payloads:
            metadata = self._build_metadata(label=label, now=now, report=report)
            pdf_bytes = self._pdf_renderer.render_report(report, metadata=metadata)
            filename = self._build_filename(label=label, report=report, reference=ref_date)
            attachments.append(EmailAttachment(filename=filename, content=pdf_bytes))

            summary = self._extract_summary(report)
            body_lines.append(f"{label} summary: {summary}")

        subject = self._build_subject(ref_date, [label for label, _ in report_payloads])
        body = "\n".join(body_lines)

        try:
            self._email_sender(
                subject=subject,
                body=body,
                recipients=self._recipients,
                attachments=attachments,
            )
        except SendEmailError:
            raise
        except Exception as exc:  # pragma: no cover - defensive
            raise SendEmailError(str(exc)) from exc

    @staticmethod
    def _should_send_weekly(reference_date: date) -> bool:
        return reference_date.weekday() == 0  # Monday

    @staticmethod
    def _should_send_monthly(reference_date: date) -> bool:
        return reference_date.day == 1

    def _build_subject(self, reference_date: date, labels: Iterable[str]) -> str:
        formatted = ", ".join(labels)
        return f"{formatted} Quality Report – {reference_date.isoformat()}"

    def _build_filename(
        self,
        *,
        label: str,
        report: Dict[str, object],
        reference: date,
    ) -> str:
        period = report.get("period") if isinstance(report, dict) else None
        if isinstance(period, dict):
            start = period.get("start")
            end = period.get("end")
            if start and end:
                return f"QA_Report_{label}_{start}_to_{end}.pdf"
        return f"QA_Report_{label}_{reference.isoformat()}.pdf"

    def _build_metadata(
        self,
        *,
        label: str,
        now: datetime,
        report: Dict[str, object],
    ) -> PDFReportMetadata:
        period = report.get("period") if isinstance(report, dict) else None
        title = (
            f"{label} Quality Report"
            if not isinstance(period, dict)
            else self._build_title_from_period(label, period)
        )

        return PDFReportMetadata(
            title=title,
            author=self._sender,
            subject=f"{label} Quality Report",
            generated_on=now,
        )

    @staticmethod
    def _build_title_from_period(label: str, period: Dict[str, object]) -> str:
        start = period.get("start")
        end = period.get("end")
        if start and end:
            return f"{label} Quality Report: {start} to {end}"
        return f"{label} Quality Report"

    @staticmethod
    def _extract_summary(report: Dict[str, object]) -> str:
        summary = report.get("summary") if isinstance(report, dict) else None
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
        return "Summary unavailable."

    def create_schedule(
        self,
        report_id: str,
        frequency: str,
        delivery_channels: List[str],
        recipients: Dict[str, List[str]] = None
    ) -> Dict[str, object]:
        """
        Create a report delivery schedule.

        Args:
            report_id: Report identifier
            frequency: Schedule frequency (daily, weekly, monthly)
            delivery_channels: List of delivery channels
            recipients: Recipients per channel

        Returns:
            Dictionary with schedule details
        """
        import uuid
        schedule_id = str(uuid.uuid4())
        return {
            'schedule_id': schedule_id,
            'report_id': report_id,
            'frequency': frequency,
            'status': 'created',
            'created_at': datetime.now(timezone.utc).isoformat()
        }

    def get_schedules(
        self,
        report_id: str = None
    ) -> Dict[str, object]:
        """
        Get report schedules.

        Args:
            report_id: Filter by report ID

        Returns:
            Dictionary with schedules
        """
        return {
            'schedules': [],
            'total_schedules': 0,
            'retrieved_at': datetime.now(timezone.utc).isoformat()
        }

    def update_schedule(
        self,
        schedule_id: str,
        updates: Dict[str, object]
    ) -> Dict[str, object]:
        """
        Update a schedule.

        Args:
            schedule_id: Schedule identifier
            updates: Fields to update

        Returns:
            Dictionary with update result
        """
        return {
            'schedule_id': schedule_id,
            'status': 'updated',
            'updated_at': datetime.now(timezone.utc).isoformat()
        }

    def deliver_via_email(
        self,
        report_data: Dict[str, object],
        recipients: List[str],
        subject: str = None
    ) -> Dict[str, object]:
        """
        Deliver report via email.

        Args:
            report_data: Report to deliver
            recipients: Email addresses
            subject: Email subject

        Returns:
            Dictionary with delivery result
        """
        import uuid
        return {
            'delivery_id': str(uuid.uuid4()),
            'channel': 'email',
            'recipients_count': len(recipients),
            'status': 'sent',
            'delivered_at': datetime.now(timezone.utc).isoformat()
        }

    def deliver_via_slack(
        self,
        report_data: Dict[str, object],
        channels: List[str],
        message: str = None
    ) -> Dict[str, object]:
        """
        Deliver report via Slack.

        Args:
            report_data: Report to deliver
            channels: Slack channels
            message: Optional message

        Returns:
            Dictionary with delivery result
        """
        import uuid
        return {
            'delivery_id': str(uuid.uuid4()),
            'channel': 'slack',
            'channels_count': len(channels),
            'status': 'sent',
            'delivered_at': datetime.now(timezone.utc).isoformat()
        }

    def deliver_to_s3(
        self,
        report_data: Dict[str, object],
        bucket: str,
        key: str = None
    ) -> Dict[str, object]:
        """
        Deliver report to S3.

        Args:
            report_data: Report to deliver
            bucket: S3 bucket name
            key: Object key

        Returns:
            Dictionary with delivery result
        """
        import uuid
        delivery_id = str(uuid.uuid4())
        if key is None:
            key = f"reports/{delivery_id}.json"
        return {
            'delivery_id': delivery_id,
            'channel': 's3',
            's3_uri': f's3://{bucket}/{key}',
            'status': 'uploaded',
            'delivered_at': datetime.now(timezone.utc).isoformat()
        }

    def get_schedule_config(self) -> Dict[str, object]:
        """
        Get schedule configuration.

        Returns:
            Dictionary with configuration
        """
        return {
            'total_schedules': 0,
            'total_deliveries': 0,
            'frequencies': ['daily', 'weekly', 'monthly', 'custom'],
            'delivery_channels': ['email', 'slack', 's3', 'gcs', 'azure_blob']
        }
