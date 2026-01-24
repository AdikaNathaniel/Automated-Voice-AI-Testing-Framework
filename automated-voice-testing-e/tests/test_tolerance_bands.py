"""
Test suite for tolerance bands and semantic equivalence.

This module tests the tolerance band functionality:
- Per-step tolerance definitions in ExpectedOutcome
- Semantic validator tolerance consumption
- Tolerance behavior for confirmation flows and alternate phrasing
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestExpectedOutcomeToleranceFields:
    """Test ExpectedOutcome tolerance definition fields"""

    def test_has_tolerance_config_field(self):
        """Test ExpectedOutcome has tolerance_config JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'tolerance_config' in columns

    def test_has_required_entities_field(self):
        """Test ExpectedOutcome has required_entities field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'required_entities' in columns

    def test_has_forbidden_phrases_field(self):
        """Test ExpectedOutcome has forbidden_phrases field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'forbidden_phrases' in columns

    def test_has_tone_requirement_field(self):
        """Test ExpectedOutcome has tone_requirement field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'tone_requirement' in columns

    def test_has_max_response_length_field(self):
        """Test ExpectedOutcome has max_response_length field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'max_response_length' in columns


class TestExpectedOutcomeToleranceMethods:
    """Test ExpectedOutcome tolerance helper methods"""

    def test_has_get_tolerance_config_method(self):
        """Test ExpectedOutcome has get_tolerance_config method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'get_tolerance_config')

    def test_has_check_entity_requirements_method(self):
        """Test ExpectedOutcome has check_entity_requirements method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'check_entity_requirements')

    def test_has_check_forbidden_phrases_method(self):
        """Test ExpectedOutcome has check_forbidden_phrases method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'check_forbidden_phrases')

    def test_has_check_tone_requirement_method(self):
        """Test ExpectedOutcome has check_tone_requirement method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'check_tone_requirement')

    def test_has_check_response_length_method(self):
        """Test ExpectedOutcome has check_response_length method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'check_response_length')


class TestValidationServiceToleranceMethods:
    """Test ValidationService tolerance processing methods"""

    def test_has_apply_tolerance_checks_method(self):
        """Test ValidationService has apply_tolerance_checks method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'apply_tolerance_checks')

    def test_has_validate_entity_presence_method(self):
        """Test ValidationService has validate_entity_presence method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'validate_entity_presence')

    def test_has_validate_forbidden_content_method(self):
        """Test ValidationService has validate_forbidden_content method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'validate_forbidden_content')

    def test_has_validate_tone_method(self):
        """Test ValidationService has validate_tone method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'validate_tone')

    def test_has_validate_length_method(self):
        """Test ValidationService has validate_length method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'validate_length')


class TestEntityRequirementValidation:
    """Test entity requirement validation logic"""

    def test_passes_when_all_required_entities_present(self):
        """Test validation passes when all required entities are present"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "The weather in Seattle is sunny with 72 degrees"
        required_entities = ['Seattle', 'sunny', '72']

        result = service.validate_entity_presence(response, required_entities)
        assert result['passed'] is True
        assert result['missing_entities'] == []

    def test_fails_when_required_entity_missing(self):
        """Test validation fails when required entity is missing"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "The weather in Seattle is sunny"
        required_entities = ['Seattle', 'sunny', '72']

        result = service.validate_entity_presence(response, required_entities)
        assert result['passed'] is False
        assert '72' in result['missing_entities']

    def test_case_insensitive_entity_matching(self):
        """Test entity matching is case-insensitive"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "The weather in SEATTLE is sunny"
        required_entities = ['seattle']

        result = service.validate_entity_presence(response, required_entities)
        assert result['passed'] is True


class TestForbiddenPhraseValidation:
    """Test forbidden phrase validation logic"""

    def test_passes_when_no_forbidden_phrases_present(self):
        """Test validation passes when no forbidden phrases are present"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "I can help you with that request"
        forbidden = ['I don\'t know', 'I cannot', 'error']

        result = service.validate_forbidden_content(response, forbidden)
        assert result['passed'] is True
        assert result['found_phrases'] == []

    def test_fails_when_forbidden_phrase_present(self):
        """Test validation fails when forbidden phrase is present"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "I don't know the answer to that"
        forbidden = ['I don\'t know', 'I cannot', 'error']

        result = service.validate_forbidden_content(response, forbidden)
        assert result['passed'] is False
        assert 'I don\'t know' in result['found_phrases']

    def test_multiple_forbidden_phrases_detected(self):
        """Test multiple forbidden phrases are detected"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "I cannot do that, there was an error"
        forbidden = ['I cannot', 'error']

        result = service.validate_forbidden_content(response, forbidden)
        assert result['passed'] is False
        assert len(result['found_phrases']) == 2


class TestToneValidation:
    """Test tone requirement validation logic"""

    def test_polite_tone_passes(self):
        """Test polite tone validation passes for polite response"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Thank you for your question. I'd be happy to help you with that."
        tone = 'polite'

        result = service.validate_tone(response, tone)
        assert result['passed'] is True

    def test_professional_tone_passes(self):
        """Test professional tone validation passes for professional response"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Based on the data, the analysis indicates a positive outcome."
        tone = 'professional'

        result = service.validate_tone(response, tone)
        assert result['passed'] is True

    def test_tone_confidence_returned(self):
        """Test tone validation returns confidence score"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Thank you for your patience."
        tone = 'polite'

        result = service.validate_tone(response, tone)
        assert 'confidence' in result
        assert 0.0 <= result['confidence'] <= 1.0


class TestResponseLengthValidation:
    """Test response length validation logic"""

    def test_passes_when_under_max_length(self):
        """Test validation passes when response is under max length"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Short response"
        max_length = 100

        result = service.validate_length(response, max_length)
        assert result['passed'] is True

    def test_fails_when_over_max_length(self):
        """Test validation fails when response exceeds max length"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "This is a very long response that exceeds the maximum allowed length"
        max_length = 20

        result = service.validate_length(response, max_length)
        assert result['passed'] is False
        assert result['actual_length'] > max_length

    def test_returns_length_info(self):
        """Test validation returns length information"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Hello world"
        max_length = 100

        result = service.validate_length(response, max_length)
        assert 'actual_length' in result
        assert 'max_length' in result


class TestCombinedToleranceChecks:
    """Test combined tolerance validation"""

    def test_apply_tolerance_checks_returns_complete_result(self):
        """Test apply_tolerance_checks returns complete validation result"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Thank you for asking. The weather in Seattle is sunny."
        tolerance_config = {
            'required_entities': ['Seattle', 'sunny'],
            'forbidden_phrases': ['error', 'unknown'],
            'tone_requirement': 'polite',
            'max_response_length': 200
        }

        result = service.apply_tolerance_checks(response, tolerance_config)
        assert 'entity_check' in result
        assert 'forbidden_check' in result
        assert 'tone_check' in result
        assert 'length_check' in result
        assert 'overall_passed' in result

    def test_overall_fails_if_any_check_fails(self):
        """Test overall validation fails if any individual check fails"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "I don't know the weather"
        tolerance_config = {
            'required_entities': ['Seattle'],
            'forbidden_phrases': ['I don\'t know'],
            'tone_requirement': 'polite',
            'max_response_length': 200
        }

        result = service.apply_tolerance_checks(response, tolerance_config)
        assert result['overall_passed'] is False

    def test_handles_missing_tolerance_fields(self):
        """Test tolerance checks handle missing config fields gracefully"""
        from services.validation_service import ValidationService

        service = ValidationService()
        response = "Hello there"
        tolerance_config = {}  # Empty config

        result = service.apply_tolerance_checks(response, tolerance_config)
        assert result['overall_passed'] is True


class TestAlternatePhrasingTolerance:
    """Test tolerance for alternate phrasing and confirmation flows"""

    def test_has_check_semantic_similarity_method(self):
        """Test ValidationService has check_semantic_similarity method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'check_semantic_similarity')

    def test_semantic_similarity_passes_for_equivalent_phrases(self):
        """Test semantic similarity passes for equivalent phrases"""
        from services.validation_service import ValidationService

        service = ValidationService()
        actual = "It's going to rain tomorrow"
        expected = "Rain is expected tomorrow"
        threshold = 0.2  # Lower threshold for word overlap algorithm

        result = service.check_semantic_similarity(actual, expected, threshold)
        assert result['passed'] is True

    def test_semantic_similarity_fails_for_different_phrases(self):
        """Test semantic similarity fails for different phrases"""
        from services.validation_service import ValidationService

        service = ValidationService()
        actual = "It's going to rain tomorrow"
        expected = "The restaurant opens at 5 PM"
        threshold = 0.7

        result = service.check_semantic_similarity(actual, expected, threshold)
        assert result['passed'] is False

    def test_semantic_similarity_returns_score(self):
        """Test semantic similarity returns similarity score"""
        from services.validation_service import ValidationService

        service = ValidationService()
        actual = "Hello there"
        expected = "Hi there"
        threshold = 0.5

        result = service.check_semantic_similarity(actual, expected, threshold)
        assert 'similarity_score' in result
        assert 0.0 <= result['similarity_score'] <= 1.0


class TestConfirmationFlowTolerance:
    """Test tolerance for confirmation flow variations"""

    def test_has_check_confirmation_pattern_method(self):
        """Test ValidationService has check_confirmation_pattern method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'check_confirmation_pattern')

    def test_confirmation_pattern_matches_yes(self):
        """Test confirmation pattern matches affirmative responses"""
        from services.validation_service import ValidationService

        service = ValidationService()
        responses = ['Yes', 'Yeah', 'Correct', 'That\'s right', 'Affirmative']

        for response in responses:
            result = service.check_confirmation_pattern(response, 'affirmative')
            assert result['matched'] is True, f"Failed for: {response}"

    def test_confirmation_pattern_matches_no(self):
        """Test confirmation pattern matches negative responses"""
        from services.validation_service import ValidationService

        service = ValidationService()
        responses = ['No', 'Nope', 'Incorrect', 'That\'s wrong', 'Negative']

        for response in responses:
            result = service.check_confirmation_pattern(response, 'negative')
            assert result['matched'] is True, f"Failed for: {response}"

    def test_confirmation_pattern_returns_matched_pattern(self):
        """Test confirmation pattern returns the matched pattern"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.check_confirmation_pattern('Yes, that is correct', 'affirmative')

        assert 'matched_pattern' in result


