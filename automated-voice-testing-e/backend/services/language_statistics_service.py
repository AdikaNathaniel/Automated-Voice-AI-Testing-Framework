"""
Language statistics aggregation service.

Provides summary metrics per supported language, including coverage,
validation pass rates, and frequently failing validation dimensions.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.validation_result import ValidationResult
from services.language_service import get_supported_languages

# Thresholds used to flag recurring issues for a language.
ISSUE_THRESHOLDS: Dict[str, tuple[str, float]] = {
    "avg_intent": ("intent_mismatch", 0.8),
    "avg_entity": ("entity_mismatch", 0.8),
    "avg_semantic": ("semantic_drift", 0.8),
    "avg_confidence": ("confidence_low", 0.8),
}


class LanguageStatisticsService:
    """Aggregate language-level validation metrics."""

    def __init__(self, db: Optional[Session]):
        if db is None:
            raise ValueError("LanguageStatisticsService requires a database session")
        self.db = db

    def get_language_statistics(self) -> List[Dict[str, Any]]:
        """
        Return aggregated statistics for every supported language.

        Returns:
            List of dictionaries containing coverage, pass rate, and issue data.
        """
        coverage_counts = self._fetch_scenario_counts()
        validation_metrics = self._fetch_validation_metrics()
        languages = get_supported_languages()

        statistics: List[Dict[str, Any]] = []
        for language in languages:
            code = language["code"]
            metrics = validation_metrics.get(code)
            pass_rate = metrics["avg_accuracy"] if metrics else None
            executions = metrics["executions"] if metrics else 0
            issues = self._determine_common_issues(metrics) if metrics else []

            statistics.append(
                {
                    "language_code": code,
                    "language_name": language["name"],
                    "native_name": language["native_name"],
                    "soundhound_model": language["soundhound_model"],
                    "coverage": {
                        "scenarios": coverage_counts.get(code, 0),
                    },
                    "pass_rate": pass_rate,
                    "executions": executions,
                    "common_issues": issues,
                }
            )

        return statistics

    def _fetch_scenario_counts(self) -> Dict[str, int]:
        """
        Count scenarios by language using ValidationResult.language_code.

        Returns:
            Mapping of language code to the number of distinct scenarios tested.
        """
        stmt = (
            select(
                ValidationResult.language_code,
                func.count(func.distinct(ValidationResult.script_id)),
            )
            .where(
                ValidationResult.language_code.isnot(None),
                ValidationResult.script_id.isnot(None),
            )
            .group_by(ValidationResult.language_code)
        )

        results = self.db.execute(stmt)
        return {
            language_code: int(count)
            for language_code, count in results.fetchall()
            if language_code
        }

    def _fetch_validation_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate validation scores per language using ValidationResult.language_code.

        Returns:
            Mapping of language code to averaged validation metrics.
        """
        # Query validation results directly grouped by language_code
        stmt = select(
            ValidationResult.language_code,
            ValidationResult.accuracy_score,
            ValidationResult.confidence_score,
            ValidationResult.semantic_similarity_score,
            ValidationResult.command_kind_match_score,
            ValidationResult.asr_confidence_score,
        ).where(ValidationResult.language_code.isnot(None))

        results = self.db.execute(stmt).all()
        if not results:
            return {}

        # Accumulate metrics per language
        language_totals: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "executions": 0,
                "accuracy_sum": 0.0,
                "accuracy_count": 0,
                "confidence_sum": 0.0,
                "confidence_count": 0,
                "semantic_sum": 0.0,
                "semantic_count": 0,
                "command_kind_sum": 0.0,
                "command_kind_count": 0,
                "asr_confidence_sum": 0.0,
                "asr_confidence_count": 0,
            }
        )

        for row in results:
            language_code = row.language_code
            if not language_code:
                continue

            totals = language_totals[language_code]
            totals["executions"] += 1
            self._accumulate_metric(totals, "accuracy", row.accuracy_score)
            self._accumulate_metric(totals, "confidence", row.confidence_score)
            self._accumulate_metric(totals, "semantic", row.semantic_similarity_score)
            self._accumulate_metric(totals, "command_kind", row.command_kind_match_score)
            self._accumulate_metric(totals, "asr_confidence", row.asr_confidence_score)

        return self._compute_metric_averages(language_totals)

    @staticmethod
    def _accumulate_metric(store: Dict[str, Any], key: str, value: Optional[float]) -> None:
        """Accumulate metric totals when a score is available."""
        if value is None:
            return
        sum_key = f"{key}_sum"
        count_key = f"{key}_count"
        store[sum_key] += float(value)
        store[count_key] += 1

    @staticmethod
    def _compute_metric_averages(
        totals: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Convert running totals into averaged metrics."""
        averaged: Dict[str, Dict[str, Any]] = {}
        for language, data in totals.items():
            averaged[language] = {
                "executions": data["executions"],
                "avg_accuracy": (
                    data["accuracy_sum"] / data["accuracy_count"]
                    if data["accuracy_count"]
                    else None
                ),
                "avg_intent": (
                    data["intent_sum"] / data["intent_count"]
                    if data["intent_count"]
                    else None
                ),
                "avg_entity": (
                    data["entity_sum"] / data["entity_count"]
                    if data["entity_count"]
                    else None
                ),
                "avg_confidence": (
                    data["confidence_sum"] / data["confidence_count"]
                    if data["confidence_count"]
                    else None
                ),
                "avg_semantic": (
                    data["semantic_sum"] / data["semantic_count"]
                    if data["semantic_count"]
                    else None
                ),
            }
        return averaged

    @staticmethod
    def _determine_common_issues(metrics: Dict[str, Any]) -> List[str]:
        """
        Identify underperforming metrics for a language.

        Args:
            metrics: Averaged validation metrics for a language.

        Returns:
            List of issue identifiers.
        """
        if not metrics:
            return []

        issues: List[str] = []
        for key, (label, threshold) in ISSUE_THRESHOLDS.items():
            value = metrics.get(key)
            if value is not None and value < threshold:
                issues.append(label)

        return issues
