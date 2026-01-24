"""
Tests for Houndify validation mixin

This module tests the ValidationHoundifyMixin methods for extracting
and validating Houndify-specific data.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest
from services.validation_houndify import ValidationHoundifyMixin


class TestValidationHoundifyMixin:
    """Test ValidationHoundifyMixin methods"""

    @pytest.fixture
    def mixin(self):
        """Create ValidationHoundifyMixin instance"""
        return ValidationHoundifyMixin()

    def test_extract_houndify_data_with_valid_response(self, mixin):
        """Test extracting Houndify data from valid context"""
        context = {
            "houndify_response": {
                "Status": "OK",
                "AllResults": [{"CommandKind": "WeatherCommand"}]
            }
        }
        result = mixin._extract_houndify_data(context)
        assert result is not None
        assert result["Status"] == "OK"
        assert "AllResults" in result

    def test_extract_houndify_data_with_missing_response(self, mixin):
        """Test extracting Houndify data from context without response"""
        context = {"other_data": "value"}
        result = mixin._extract_houndify_data(context)
        assert result is None

    def test_extract_houndify_data_with_empty_context(self, mixin):
        """Test extracting Houndify data from empty context"""
        context = {}
        result = mixin._extract_houndify_data(context)
        assert result is None

    def test_extract_command_kind_from_valid_response(self, mixin):
        """Test extracting CommandKind from valid Houndify response"""
        houndify_data = {
            "AllResults": [
                {"CommandKind": "WeatherCommand", "ASRConfidence": 0.95}
            ]
        }
        result = mixin._extract_command_kind(houndify_data)
        assert result == "WeatherCommand"

    def test_extract_command_kind_from_response_with_no_results(self, mixin):
        """Test extracting CommandKind when AllResults is empty"""
        houndify_data = {"AllResults": []}
        result = mixin._extract_command_kind(houndify_data)
        assert result is None

    def test_extract_command_kind_from_response_without_command_kind(self, mixin):
        """Test extracting CommandKind when field is missing"""
        houndify_data = {
            "AllResults": [{"ASRConfidence": 0.95}]
        }
        result = mixin._extract_command_kind(houndify_data)
        assert result is None

    def test_extract_asr_confidence_from_valid_response(self, mixin):
        """Test extracting ASR confidence from valid response"""
        houndify_data = {
            "AllResults": [
                {"CommandKind": "WeatherCommand", "ASRConfidence": 0.95}
            ]
        }
        result = mixin._extract_asr_confidence(houndify_data)
        assert result == 0.95

    def test_extract_asr_confidence_from_response_with_no_results(self, mixin):
        """Test extracting ASR confidence when AllResults is empty"""
        houndify_data = {"AllResults": []}
        result = mixin._extract_asr_confidence(houndify_data)
        assert result is None

    def test_extract_asr_confidence_from_response_without_field(self, mixin):
        """Test extracting ASR confidence when field is missing"""
        houndify_data = {
            "AllResults": [{"CommandKind": "WeatherCommand"}]
        }
        result = mixin._extract_asr_confidence(houndify_data)
        assert result is None

    def test_calculate_command_kind_match_score_matching(self, mixin):
        """Test CommandKind match score when CommandKinds match"""
        score = mixin._calculate_command_kind_match_score(
            "WeatherCommand",
            "WeatherCommand"
        )
        assert score == 1.0

    def test_calculate_command_kind_match_score_not_matching(self, mixin):
        """Test CommandKind match score when CommandKinds don't match"""
        score = mixin._calculate_command_kind_match_score(
            "WeatherCommand",
            "MusicCommand"
        )
        assert score == 0.0

    def test_calculate_command_kind_match_score_no_expected(self, mixin):
        """Test CommandKind match score when no expected CommandKind"""
        score = mixin._calculate_command_kind_match_score(
            "WeatherCommand",
            None
        )
        assert score == 1.0

    def test_calculate_command_kind_match_score_no_actual(self, mixin):
        """Test CommandKind match score when no actual CommandKind"""
        score = mixin._calculate_command_kind_match_score(
            None,
            "WeatherCommand"
        )
        assert score == 0.0

    def test_validate_asr_confidence_above_threshold(self, mixin):
        """Test ASR confidence validation when above threshold"""
        score = mixin._validate_asr_confidence(0.95, 0.80)
        assert score == 0.95

    def test_validate_asr_confidence_below_threshold(self, mixin):
        """Test ASR confidence validation when below threshold"""
        score = mixin._validate_asr_confidence(0.70, 0.80)
        assert score == 0.0

    def test_validate_asr_confidence_at_threshold(self, mixin):
        """Test ASR confidence validation when exactly at threshold"""
        score = mixin._validate_asr_confidence(0.80, 0.80)
        assert score == 0.80

    def test_validate_asr_confidence_no_min_threshold(self, mixin):
        """Test ASR confidence validation when no minimum threshold"""
        score = mixin._validate_asr_confidence(0.75, None)
        assert score == 0.75

    def test_validate_asr_confidence_no_actual_confidence(self, mixin):
        """Test ASR confidence validation when no actual confidence"""
        score = mixin._validate_asr_confidence(None, 0.80)
        assert score == 0.0

    def test_extract_command_kind_music_command(self, mixin):
        """Test extracting MusicCommand"""
        houndify_data = {
            "AllResults": [
                {"CommandKind": "MusicCommand", "ASRConfidence": 0.92}
            ]
        }
        result = mixin._extract_command_kind(houndify_data)
        assert result == "MusicCommand"

    def test_extract_asr_confidence_low_confidence(self, mixin):
        """Test extracting low ASR confidence"""
        houndify_data = {
            "AllResults": [
                {"CommandKind": "WeatherCommand", "ASRConfidence": 0.45}
            ]
        }
        result = mixin._extract_asr_confidence(houndify_data)
        assert result == 0.45

    def test_extract_asr_confidence_perfect_confidence(self, mixin):
        """Test extracting perfect ASR confidence"""
        houndify_data = {
            "AllResults": [
                {"CommandKind": "WeatherCommand", "ASRConfidence": 1.0}
            ]
        }
        result = mixin._extract_asr_confidence(houndify_data)
        assert result == 1.0
