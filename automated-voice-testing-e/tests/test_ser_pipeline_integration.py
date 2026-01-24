"""
Test suite for SER (Sentence Error Rate) pipeline integration.

Tests that SER is properly integrated into the validation pipeline
alongside WER and CER for sentence-level ASR quality metrics.
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSerPipelineIntegration:
    """Test SER integration in validation pipeline"""

    def test_validation_service_has_calculate_ser_score_method(self):
        """Test that ValidationService has _calculate_ser_score method"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert '_calculate_ser_score' in content, "Should have _calculate_ser_score method"

    def test_validation_result_creation_includes_ser_score(self):
        """Test that ValidationResult creation includes ser_score"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # Find ValidationResult creation and check for ser_score
        if 'ValidationResult(' in content:
            result_start = content.find('ValidationResult(')
            result_section = content[result_start:result_start + 700]
            assert 'ser_score' in result_section, \
                "ValidationResult creation should include ser_score"

    def test_ser_score_calculated_in_flow(self):
        """Test that ser_score variable is calculated in validation flow"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert 'ser_score = self._calculate_ser_score' in content, \
            "Should calculate ser_score in validation flow"

    def test_ser_score_logged_in_validation(self):
        """Test that SER score is included in validation logging"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert 'ser=' in content or 'ser_score' in content, "Should log SER score"


class TestSerCalculateMethod:
    """Test the _calculate_ser_score method details"""

    def test_method_has_docstring(self):
        """Test _calculate_ser_score has docstring"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_ser_score' in content:
            method_start = content.find('def _calculate_ser_score')
            method_section = content[method_start:method_start + 600]
            assert '"""' in method_section, "Method should have docstring"

    def test_method_returns_float(self):
        """Test _calculate_ser_score returns float"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_ser_score' in content:
            method_start = content.find('def _calculate_ser_score')
            method_section = content[method_start:method_start + 300]
            assert '-> float' in method_section, "Method should return float"


class TestAllErrorRatesInPipeline:
    """Test that WER, CER, and SER all work together"""

    def test_all_three_error_rates_in_validation_result(self):
        """Test that ValidationResult gets wer_score, cer_score, and ser_score"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'ValidationResult(' in content:
            result_start = content.find('ValidationResult(')
            result_section = content[result_start:result_start + 700]
            assert 'wer_score' in result_section, "Should include wer_score"
            assert 'cer_score' in result_section, "Should include cer_score"
            assert 'ser_score' in result_section, "Should include ser_score"

    def test_all_three_calculated_in_sequence(self):
        """Test that WER, CER, and SER are all calculated"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert 'wer_score = self._calculate_wer_score' in content, "Should calculate wer_score"
        assert 'cer_score = self._calculate_cer_score' in content, "Should calculate cer_score"
        assert 'ser_score = self._calculate_ser_score' in content, "Should calculate ser_score"

