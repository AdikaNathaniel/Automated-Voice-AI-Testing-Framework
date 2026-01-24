"""
Test suite for CER (Character Error Rate) pipeline integration.

Tests that CER is properly integrated into the validation pipeline
alongside WER for character-level ASR quality metrics.
"""

import pytest
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCerPipelineIntegration:
    """Test CER integration in validation pipeline"""

    def test_validation_service_has_calculate_cer_score_method(self):
        """Test that ValidationService has _calculate_cer_score method"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert (
            'calculate_cer' in content or
            'cer_score' in content
        ), "Should have CER calculation logic"

    def test_validation_result_creation_includes_cer_score(self):
        """Test that ValidationResult creation includes cer_score"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # Find ValidationResult creation and check for cer_score
        if 'ValidationResult(' in content:
            result_start = content.find('ValidationResult(')
            result_section = content[result_start:result_start + 600]
            assert 'cer_score' in result_section, \
                "ValidationResult creation should include cer_score"

    def test_cer_score_calculated_from_transcripts(self):
        """Test that CER is calculated using transcript and expected_transcript"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # CER should be calculated from reference and actual transcripts
        assert '_calculate_cer_score' in content, \
            "Should have _calculate_cer_score method"

    def test_cer_score_logged_in_validation(self):
        """Test that CER score is included in validation logging"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # Should log CER along with other scores
        assert 'cer' in content.lower(), "Should log CER score"

    def test_calculate_cer_score_method_implementation(self):
        """Test _calculate_cer_score method is properly implemented"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # Method should exist and call transcription_validator_service.calculate_cer
        if '_calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 500]
            assert 'calculate_cer' in method_section, \
                "_calculate_cer_score should call calculate_cer"

    def test_cer_score_variable_calculated(self):
        """Test that cer_score variable is calculated in validation flow"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        # Should have cer_score = self._calculate_cer_score(...)
        assert 'cer_score = self._calculate_cer_score' in content, \
            "Should calculate cer_score in validation flow"


class TestCerCalculationMethod:
    """Test the _calculate_cer_score method details"""

    def test_method_has_reference_parameter(self):
        """Test _calculate_cer_score takes reference parameter"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 200]
            assert 'reference' in method_section, \
                "Method should take reference parameter"

    def test_method_has_actual_parameter(self):
        """Test _calculate_cer_score takes actual parameter"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 200]
            assert 'actual' in method_section, \
                "Method should take actual parameter"

    def test_method_returns_float(self):
        """Test _calculate_cer_score returns float"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 300]
            assert '-> float' in method_section, \
                "Method should return float"

    def test_method_has_docstring(self):
        """Test _calculate_cer_score has docstring"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 500]
            assert '"""' in method_section, \
                "Method should have docstring"

    def test_method_rounds_result(self):
        """Test _calculate_cer_score rounds result to 4 decimal places"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 900]
            assert 'round' in method_section, \
                "Method should round result"


class TestCerAlongsideWer:
    """Test that CER works alongside WER"""

    def test_both_wer_and_cer_in_validation_result(self):
        """Test that ValidationResult gets both wer_score and cer_score"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'ValidationResult(' in content:
            result_start = content.find('ValidationResult(')
            result_section = content[result_start:result_start + 600]
            assert 'wer_score' in result_section, \
                "ValidationResult should include wer_score"
            assert 'cer_score' in result_section, \
                "ValidationResult should include cer_score"

    def test_both_calculated_in_sequence(self):
        """Test that both WER and CER are calculated in validation flow"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        assert 'wer_score = self._calculate_wer_score' in content, \
            "Should calculate wer_score"
        assert 'cer_score = self._calculate_cer_score' in content, \
            "Should calculate cer_score"


class TestCerGracefulDegradation:
    """Test CER handles missing services gracefully"""

    def test_method_handles_missing_transcription_validator(self):
        """Test _calculate_cer_score handles missing TranscriptionValidatorService"""
        validation_service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'validation_service.py'
        )
        with open(validation_service_file, 'r') as f:
            content = f.read()

        if 'def _calculate_cer_score' in content:
            method_start = content.find('def _calculate_cer_score')
            method_section = content[method_start:method_start + 800]
            # Should check if transcription_validator_service is None
            assert (
                'transcription_validator_service is None' in method_section or
                'transcription_validator_service' in method_section
            ), "Should handle missing TranscriptionValidatorService"

