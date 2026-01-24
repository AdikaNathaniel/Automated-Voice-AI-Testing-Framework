"""
Heuristics for automatic defect categorisation.

The categoriser inspects validation results and execution metadata to determine
an appropriate defect category without human intervention.

Uses the actual validation fields:
- command_kind_match_score: Houndify CommandKind match
- houndify_passed: Overall Houndify validation
- llm_passed: LLM ensemble validation
"""

from __future__ import annotations

from typing import Any


class DefectCategorizer:
    """Classify validation failures into predefined defect categories."""

    COMMAND_KIND_THRESHOLD = 0.5
    TIMING_THRESHOLD_SECONDS = 3.0

    def categorize(self, *, execution: Any, validation_result: Any) -> str:
        """
        Determine a defect category from execution and validation details.

        Categories (in priority order):
        - command_mismatch: Houndify CommandKind doesn't match expected
        - timing: Response latency exceeds threshold
        - audio: Audio/ASR related errors
        - integration: External service failures
        - edge_case: Default when no specific category matches
        """
        if self._is_command_kind_issue(validation_result):
            return "command_mismatch"
        if self._is_timing_issue(execution):
            return "timing"
        if self._is_audio_issue(execution):
            return "audio"
        if self._is_integration_issue(execution):
            return "integration"
        return "edge_case"

    def _is_command_kind_issue(self, validation_result: Any) -> bool:
        """Check if this is a CommandKind mismatch (Houndify validation)."""
        score = getattr(validation_result, "command_kind_match_score", None)
        if isinstance(score, (int, float)) and score < self.COMMAND_KIND_THRESHOLD:
            return True
        return False

    def _is_timing_issue(self, execution: Any) -> bool:
        """Check if response time exceeded threshold."""
        context = self._get_context(execution)
        if not context:
            return False
        candidate_keys = (
            "response_time_ms",
            "response_duration_ms",
            "response_latency_ms",
            "execution_time_ms",
            "latency_ms",
        )
        for key in candidate_keys:
            value = context.get(key)
            if isinstance(value, (int, float)):
                seconds = float(value) / 1000.0
                if seconds >= self.TIMING_THRESHOLD_SECONDS:
                    return True
        # Some integrations may already store seconds.
        candidate_keys_seconds = (
            "response_time_seconds",
            "response_duration_seconds",
            "response_latency_seconds",
            "execution_time_seconds",
        )
        for key in candidate_keys_seconds:
            value = context.get(key)
            if isinstance(value, (int, float)) and float(value) >= self.TIMING_THRESHOLD_SECONDS:
                return True
        return False

    def _is_audio_issue(self, execution: Any) -> bool:
        """Check if there was an audio/ASR issue."""
        context = self._get_context(execution)
        audio_flags = (
            "audio_error",
            "audio_issue",
            "audio_quality_issue",
            "speech_recognition_error",
        )
        for key in audio_flags:
            if context.get(key):
                return True
        # Some audio flags may be present in audio params.
        if hasattr(execution, "get_audio_param"):
            if execution.get_audio_param("audio_issue") or execution.get_audio_param("audio_error"):
                return True
        return False

    def _is_integration_issue(self, execution: Any) -> bool:
        """Check if there was an external service failure."""
        context = self._get_context(execution)
        if context.get("integration_error") or context.get("external_service_error"):
            return True
        http_status = context.get("http_status") or context.get("response_status")
        if isinstance(http_status, int) and http_status >= 500:
            return True
        return False

    @staticmethod
    def _get_context(execution: Any) -> dict[str, Any]:
        """Extract context from execution object."""
        if hasattr(execution, "get_all_context"):
            context = execution.get_all_context()
            if isinstance(context, dict):
                return dict(context)
        context = getattr(execution, "context", None)
        if isinstance(context, dict):
            return dict(context)
        return {}
