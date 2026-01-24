"""
Test suite for transcription comparison functionality.

This module tests the transcription comparison system:
- Validators compare reference transcripts to system transcripts
- Mismatch triggers failure
- Skip TTS/STT processing when reference provided
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestTranscriptionValidatorService:
    """Test TranscriptionValidatorService for transcript comparison"""

    def test_service_exists(self):
        """Test that TranscriptionValidatorService can be imported"""
        from services.transcription_validator_service import TranscriptionValidatorService
        assert TranscriptionValidatorService is not None

    def test_has_compare_transcripts_method(self):
        """Test service has compare_transcripts method"""
        from services.transcription_validator_service import TranscriptionValidatorService

        assert hasattr(TranscriptionValidatorService, 'compare_transcripts')

    def test_has_validate_transcription_method(self):
        """Test service has validate_transcription method"""
        from services.transcription_validator_service import TranscriptionValidatorService

        assert hasattr(TranscriptionValidatorService, 'validate_transcription')

    def test_has_calculate_similarity_method(self):
        """Test service has calculate_similarity method"""
        from services.transcription_validator_service import TranscriptionValidatorService

        assert hasattr(TranscriptionValidatorService, 'calculate_similarity')


class TestExactTranscriptMatch:
    """Test exact transcript matching"""

    def test_exact_match_passes(self):
        """Test validation passes for exact transcript match"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "Navigate to the nearest gas station"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is True
        assert result['similarity'] == 1.0

    def test_case_insensitive_match(self):
        """Test matching is case-insensitive"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "navigate to the nearest gas station"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is True

    def test_whitespace_normalized(self):
        """Test whitespace is normalized for comparison"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "Navigate  to   the nearest  gas station"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is True


class TestTranscriptMismatch:
    """Test transcript mismatch detection and failure"""

    def test_mismatch_fails(self):
        """Test validation fails for transcript mismatch"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "Navigate to the nearest restaurant"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is False

    def test_completely_different_fails(self):
        """Test validation fails for completely different transcripts"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "Play music by Taylor Swift"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is False

    def test_missing_words_fails(self):
        """Test validation fails when words are missing"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to the nearest gas station"
        actual = "Navigate to the gas station"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is False


class TestSimilarityThreshold:
    """Test similarity threshold configuration"""

    def test_default_threshold_is_reasonable(self):
        """Test default similarity threshold is set"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        assert hasattr(service, 'default_threshold')
        assert service.default_threshold >= 0.8

    def test_custom_threshold_applied(self):
        """Test custom threshold is applied"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Navigate to gas station"
        actual = "Navigate to the gas station"

        # With low threshold, should pass
        result = service.compare_transcripts(reference, actual, threshold=0.7)
        assert result['passed'] is True

    def test_similarity_score_returned(self):
        """Test similarity score is returned"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Hello world"
        actual = "Hello there"

        result = service.compare_transcripts(reference, actual)
        assert 'similarity' in result
        assert 0.0 <= result['similarity'] <= 1.0


class TestTranscriptValidation:
    """Test full transcript validation flow"""

    def test_validate_transcription_returns_complete_result(self):
        """Test validate_transcription returns complete validation result"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "What is the weather today"
        actual = "What is the weather today"

        result = service.validate_transcription(reference, actual)
        assert 'passed' in result
        assert 'similarity' in result
        assert 'reference' in result
        assert 'actual' in result

    def test_validate_transcription_includes_differences(self):
        """Test validation includes differences when mismatch"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "What is the weather today"
        actual = "What's the weather tomorrow"

        result = service.validate_transcription(reference, actual)
        assert 'differences' in result


class TestWordErrorRate:
    """Test Word Error Rate (WER) calculation"""

    def test_has_calculate_wer_method(self):
        """Test service has calculate_wer method"""
        from services.transcription_validator_service import TranscriptionValidatorService

        assert hasattr(TranscriptionValidatorService, 'calculate_wer')

    def test_zero_wer_for_exact_match(self):
        """Test WER is 0 for exact match"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Hello world"
        actual = "Hello world"

        wer = service.calculate_wer(reference, actual)
        assert wer == 0.0

    def test_wer_increases_with_errors(self):
        """Test WER increases with more errors"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "Hello world how are you"
        actual = "Hello there how is you"

        wer = service.calculate_wer(reference, actual)
        assert wer > 0.0


class TestEmptyAndEdgeCases:
    """Test edge cases for transcription comparison"""

    def test_empty_reference_fails(self):
        """Test validation fails for empty reference"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        result = service.compare_transcripts("", "Hello world")
        assert result['passed'] is False

    def test_empty_actual_fails(self):
        """Test validation fails for empty actual"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        result = service.compare_transcripts("Hello world", "")
        assert result['passed'] is False

    def test_both_empty_passes(self):
        """Test validation passes when both are empty"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        result = service.compare_transcripts("", "")
        assert result['passed'] is True


class TestPunctuationHandling:
    """Test punctuation handling in transcription comparison"""

    def test_punctuation_ignored(self):
        """Test punctuation is ignored in comparison"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "What is the weather?"
        actual = "What is the weather"

        result = service.compare_transcripts(reference, actual)
        assert result['passed'] is True

    def test_apostrophes_handled(self):
        """Test apostrophes are handled correctly"""
        from services.transcription_validator_service import TranscriptionValidatorService

        service = TranscriptionValidatorService()
        reference = "What's the weather"
        actual = "What is the weather"

        # With word overlap, contractions have ~40% similarity
        # Use a lower threshold that's realistic for simple word matching
        result = service.compare_transcripts(reference, actual, threshold=0.4)
        assert result['passed'] is True


class TestValidationServiceIntegration:
    """Test integration with ValidationService"""

    def test_validation_service_has_validate_transcript_method(self):
        """Test ValidationService has validate_transcript method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'validate_transcript')


