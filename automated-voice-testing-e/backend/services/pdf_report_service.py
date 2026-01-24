"""
PDF report generation service (TASK-314).
"""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, Optional

from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


@dataclass(slots=True)
class PDFReportMetadata:
    """
    Metadata describing the rendered PDF document.
    """

    title: str | None = None
    author: str | None = None
    subject: str | None = None
    generated_on: Optional[datetime] = None
    keywords: Iterable[str] = field(default_factory=tuple)


class PDFReportService:
    """
    Render an executive report into PDF format using ReportLab.
    """

    def __init__(
        self,
        *,
        page_size: tuple[float, float] = pagesizes.A4,
        margin: float = 0.75 * inch,
        body_font: str = "Helvetica",
        heading_font: str = "Helvetica-Bold",
    ) -> None:
        self._page_size = page_size
        self._margin = margin
        self._body_font = body_font
        self._heading_font = heading_font

    def render_report(
        self,
        report: Dict[str, Any],
        *,
        metadata: Optional[PDFReportMetadata] = None,
    ) -> bytes:
        """
        Render the supplied report payload to a PDF binary.
        """
        metadata = metadata or PDFReportMetadata()
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=self._page_size)
        pdf.setPageCompression(0)
        width, height = self._page_size
        y_position = height - self._margin

        self._apply_metadata(pdf, report, metadata)

        # Title
        period = report.get("period", {})
        title = metadata.title or self._default_title(period)
        pdf.setFont(self._heading_font, 18)
        pdf.drawString(self._margin, y_position, title)
        y_position -= 28

        # Generation timestamp
        if metadata.generated_on:
            generated_label = metadata.generated_on.strftime("%Y-%m-%d %H:%M")
        else:
            generated_label = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        pdf.setFont(self._body_font, 10)
        pdf.drawString(
            self._margin,
            y_position,
            f"Generated on: {generated_label}",
        )
        y_position -= 20

        # Executive summary
        pdf.setFont(self._heading_font, 14)
        pdf.drawString(self._margin, y_position, "Executive Summary")
        y_position -= 18
        pdf.setFont(self._body_font, 11)
        y_position = self._draw_paragraph(
            pdf,
            report.get("summary", "No summary available."),
            start_y=y_position,
            width=width,
        )
        y_position -= 10

        # Trend highlights
        pdf.setFont(self._heading_font, 14)
        y_position = self._ensure_space(pdf, width, y_position, lines=3)
        pdf.drawString(self._margin, y_position, "Trend Highlights")
        y_position -= 18
        pdf.setFont(self._body_font, 11)
        trends = report.get("trends", {})
        if trends:
            for name, details in trends.items():
                line = self._format_trend_line(name, details)
                y_position = self._draw_paragraph(
                    pdf, line, start_y=y_position, width=width
                )
                y_position -= 4
        else:
            pdf.drawString(self._margin, y_position, "No trend data available.")
            y_position -= 14

        # Key risks
        pdf.setFont(self._heading_font, 14)
        y_position = self._ensure_space(pdf, width, y_position, lines=3)
        pdf.drawString(self._margin, y_position, "Key Risks")
        y_position -= 18
        pdf.setFont(self._body_font, 11)
        risks = report.get("key_risks", []) or []
        if risks:
            for risk in risks:
                line = self._format_risk_line(risk)
                y_position = self._draw_bullet(pdf, line, y_position, width)
        else:
            pdf.drawString(self._margin, y_position, "No significant risks identified.")
            y_position -= 14

        # Recommendations
        pdf.setFont(self._heading_font, 14)
        y_position = self._ensure_space(pdf, width, y_position, lines=4)
        pdf.drawString(self._margin, y_position, "Recommendations")
        y_position -= 18
        pdf.setFont(self._body_font, 11)
        recommendations = report.get("recommendations", []) or []
        if recommendations:
            for recommendation in recommendations:
                y_position = self._draw_bullet(
                    pdf, recommendation, y_position, width
                )
        else:
            pdf.drawString(self._margin, y_position, "No recommendations at this time.")

        pdf.showPage()
        pdf.save()
        return buffer.getvalue()

    def _apply_metadata(
        self,
        pdf: canvas.Canvas,
        report: Dict[str, Any],
        metadata: PDFReportMetadata,
    ) -> None:
        title = metadata.title or self._default_title(report.get("period", {}))
        pdf.setTitle(title)

        if metadata.author:
            pdf.setAuthor(metadata.author)
        if metadata.subject is not None:
            pdf.setSubject(metadata.subject)
        if metadata.keywords:
            pdf.setKeywords(", ".join(str(keyword) for keyword in metadata.keywords))

    @staticmethod
    def _default_title(period: Dict[str, Any]) -> str:
        start = period.get("start")
        end = period.get("end")
        if start and end:
            return f"Quality Report: {start} to {end}"
        return "Quality Engineering Report"

    def _draw_paragraph(
        self,
        pdf: canvas.Canvas,
        text: str,
        *,
        start_y: float,
        width: float,
        leading: float = 14.0,
    ) -> float:
        lines = self._wrap_text(text, max_chars=95)
        y = start_y
        for line in lines:
            y = self._ensure_space(pdf, width, y, lines=1)
            pdf.drawString(self._margin, y, line)
            y -= leading
        return y

    def _draw_bullet(
        self,
        pdf: canvas.Canvas,
        text: str,
        y_position: float,
        width: float,
        *,
        bullet: str = "\u2022",
        leading: float = 14.0,
    ) -> float:
        wrapped = self._wrap_text(text, max_chars=90)
        for index, line in enumerate(wrapped):
            y_position = self._ensure_space(pdf, width, y_position, lines=1)
            prefix = bullet if index == 0 else " "
            pdf.drawString(self._margin, y_position, f"{prefix} {line}")
            y_position -= leading
        return y_position

    def _ensure_space(
        self,
        pdf: canvas.Canvas,
        width: float,
        y_position: float,
        *,
        lines: int,
        leading: float = 14.0,
    ) -> float:
        required = self._margin + (lines * leading)
        if y_position <= required:
            pdf.showPage()
            y_position = self._page_size[1] - self._margin
            pdf.setFont(self._body_font, 11)
        return y_position

    @staticmethod
    def _wrap_text(text: str, *, max_chars: int) -> list[str]:
        stripped = (text or "").strip()
        if not stripped:
            return ["—"]
        words = stripped.split()
        lines: list[str] = []
        current: list[str] = []
        for word in words:
            tentative = " ".join((*current, word))
            if len(tentative) > max_chars and current:
                lines.append(" ".join(current))
                current = [word]
            else:
                current.append(word)
        if current:
            lines.append(" ".join(current))
        return lines

    @staticmethod
    def _format_trend_line(name: str, details: Dict[str, Any]) -> str:
        current = details.get("current")
        delta = details.get("delta")
        label = name.replace("_", " ").title()
        parts = [f"{label}: {current}"]
        if delta is not None:
            sign = "+" if delta >= 0 else ""
            parts.append(f"(Δ {sign}{delta})")
        return " ".join(parts)

    @staticmethod
    def _format_risk_line(risk: Dict[str, Any]) -> str:
        name = risk.get("name", "Unnamed risk")
        probability = risk.get("probability")
        level = risk.get("risk_level", "unknown")
        if isinstance(probability, (int, float)):
            probability_text = f"{probability * 100:.0f}%"
        else:
            probability_text = "N/A"
        return f"{name} — Level: {level}; Likelihood: {probability_text}"
