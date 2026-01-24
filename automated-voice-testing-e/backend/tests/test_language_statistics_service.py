"""
Tests for language statistics service aggregation.
"""

from unittest.mock import Mock

import pytest


class TestLanguageStatisticsService:
    """Validate language statistics aggregation logic."""

    def test_requires_database_session(self):
        """Service should enforce presence of a database session."""
        from services.language_statistics_service import LanguageStatisticsService

        with pytest.raises(ValueError):
            LanguageStatisticsService(db=None)

    def test_get_language_statistics_merges_config_and_metrics(self, monkeypatch):
        """Statistics should combine language config, coverage, pass rates, and issues."""
        from services.language_statistics_service import LanguageStatisticsService

        db = Mock()
        service = LanguageStatisticsService(db=db)

        languages = [
            {
                "code": "en-US",
                "name": "English (United States)",
                "native_name": "English",
                "soundhound_model": "en-US-v3.2",
            },
            {
                "code": "ja-JP",
                "name": "Japanese (Japan)",
                "native_name": "日本語",
                "soundhound_model": "ja-JP-v2.4",
            },
        ]

        monkeypatch.setattr(
            "services.language_statistics_service.get_supported_languages",
            lambda: languages,
        )

        monkeypatch.setattr(
            LanguageStatisticsService,
            "_fetch_test_case_counts",
            lambda self: {"en-US": 12},
        )

        monkeypatch.setattr(
            LanguageStatisticsService,
            "_fetch_validation_metrics",
            lambda self: {
                "en-US": {
                    "executions": 18,
                    "avg_accuracy": 0.93,
                    "avg_intent": 0.89,
                    "avg_entity": 0.91,
                    "avg_confidence": 0.95,
                    "avg_semantic": 0.9,
                },
                "ja-JP": {
                    "executions": 7,
                    "avg_accuracy": 0.71,
                    "avg_intent": 0.58,
                    "avg_entity": 0.63,
                    "avg_confidence": 0.77,
                    "avg_semantic": 0.69,
                },
            },
        )

        stats = service.get_language_statistics()

        assert len(stats) == 2

        english = next(item for item in stats if item["language_code"] == "en-US")
        japanese = next(item for item in stats if item["language_code"] == "ja-JP")

        assert english["language_name"] == "English (United States)"
        assert english["coverage"]["test_cases"] == 12
        assert english["pass_rate"] == pytest.approx(0.93)
        assert english["executions"] == 18
        assert english["common_issues"] == []

        assert japanese["coverage"]["test_cases"] == 0
        assert japanese["pass_rate"] == pytest.approx(0.71)
        assert japanese["executions"] == 7
        assert sorted(japanese["common_issues"]) == [
            "confidence_low",
            "entity_mismatch",
            "intent_mismatch",
            "semantic_drift",
        ]

