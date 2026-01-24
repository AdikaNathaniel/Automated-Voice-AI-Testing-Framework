"""
Automatic edge case detection service.

Analyses failed test executions to infer common edge case patterns and
creates `EdgeCase` records via the EdgeCaseService.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from uuid import UUID

from services.edge_case_service import EdgeCaseService


@dataclass(frozen=True)
class _Classification:
    category: str
    severity: str
    tag: str
    signature: str
    summary: str


class EdgeCaseDetectionService:
    """Detects edge case patterns from failed test executions."""

    def __init__(
        self,
        edge_case_service: EdgeCaseService,
        *,
        base_tags: Optional[Iterable[str]] = None,
    ) -> None:
        self._edge_case_service = edge_case_service
        self._base_tags = list(base_tags or ["auto-detected"])

    def detect_from_failures(
        self,
        failures: Sequence[Dict[str, Any]],
        *,
        discovered_by: Optional[UUID] = None,
    ) -> List[Any]:
        """
        Analyse failure records and create edge cases for recognised patterns.

        Args:
            failures: Sequence of dictionaries describing failed executions.
            discovered_by: Optional UUID of the analyst or system generating the detection.

        Returns:
            List of EdgeCase instances created by the underlying service.
        """
        created: List[Any] = []
        seen: Set[Tuple[str, str, str]] = set()

        for failure in failures:
            classification = self._classify_failure(failure)
            if classification is None:
                continue

            test_case_id = failure.get("test_case_id")
            signature_key = (
                str(test_case_id),
                classification.category,
                classification.signature,
            )
            if signature_key in seen:
                continue
            seen.add(signature_key)

            payload = self._build_payload(
                failure=failure,
                classification=classification,
                discovered_by=discovered_by,
            )
            created_case = self._edge_case_service.create_edge_case(**payload)
            created.append(created_case)

        return created

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #
    def _classify_failure(self, failure: Dict[str, Any]) -> Optional[_Classification]:
        reason = (failure.get("failure_reason") or "").strip()
        error_type = (failure.get("error_type") or "").strip()
        metadata = failure.get("metadata") or {}

        reason_lower = reason.lower()
        error_lower = error_type.lower()

        if "timeout" in reason_lower or "timeout" in error_lower or metadata.get("elapsed_ms", 0) > 0:
            signature = reason_lower or error_lower or str(metadata.get("elapsed_ms"))
            summary = reason or error_type or "Detected timeout"
            return _Classification(
                category="timeout",
                severity=None,  # Manual assignment by QA team
                tag="timeout",
                signature=signature,
                summary=summary,
            )

        if "ambigu" in reason_lower or "ambiguous" in metadata.get("classification", "").lower() or metadata.get("candidates"):
            candidate_signature = ",".join(sorted(metadata.get("candidates", [])))
            signature = reason_lower or candidate_signature or error_lower
            summary = reason or "Ambiguous resolution detected"
            return _Classification(
                category="ambiguity",
                severity=None,  # Manual assignment by QA team
                tag="ambiguity",
                signature=signature,
                summary=summary,
            )

        if (
            "context" in reason_lower
            or "context" in error_lower
            or metadata.get("context_shift")
            or metadata.get("lost_context")
        ):
            signature = reason_lower or error_lower or str(metadata.get("turn_index"))
            summary = reason or "Conversation context lost"
            return _Classification(
                category="context_loss",
                severity=None,  # Manual assignment by QA team
                tag="context_loss",
                signature=signature,
                summary=summary,
            )

        return None

    def _build_payload(
        self,
        *,
        failure: Dict[str, Any],
        classification: _Classification,
        discovered_by: Optional[UUID],
    ) -> Dict[str, Any]:
        metadata = failure.get("metadata") or {}
        scenario_definition = {
            "failure_reason": failure.get("failure_reason"),
            "error_type": failure.get("error_type"),
            "metadata": metadata,
            "transcript": failure.get("transcript"),
            "step": failure.get("step"),
            "source": "auto_detection",
        }

        base_title = classification.category.replace("_", " ")
        title = f"Auto-detected {base_title} edge case"
        if failure.get("test_case_title"):
            title += f": {failure['test_case_title']}"

        description = classification.summary

        tags = set(self._base_tags)
        tags.add(classification.tag)
        if failure.get("tags"):
            tags.update(str(t) for t in failure["tags"])

        payload: Dict[str, Any] = {
            "title": title,
            "description": description,
            "scenario_definition": scenario_definition,
            "tags": sorted(tags),
            "severity": classification.severity,
            "category": classification.category,
            "status": "active",
            "test_case_id": failure.get("test_case_id"),
            "discovered_date": failure.get("detected_at"),
            "discovered_by": discovered_by,
        }
        return payload
