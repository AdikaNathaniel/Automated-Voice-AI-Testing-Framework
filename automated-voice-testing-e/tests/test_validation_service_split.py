"""
Tests for ValidationService split into multiple files.

These tests ensure that the ValidationService functionality is preserved
after splitting validation_service.py into 3 files:
- validation_core.py (core validation logic)
- validation_scoring.py (ML scoring methods)
- validation_checks.py (tolerance and metadata checks)
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from uuid import uuid4

import sys
import os

# Set required environment variables before importing
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret-key-1234567890')
os.environ.setdefault('SOUNDHOUND_API_KEY', 'test-key')
os.environ.setdefault('SOUNDHOUND_CLIENT_ID', 'test-client')
os.environ.setdefault('AWS_ACCESS_KEY_ID', 'test-access-key')
os.environ.setdefault('AWS_SECRET_ACCESS_KEY', 'test-secret')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.validation_service import ValidationService, determine_review_status


class TestValidationServiceInitialization:
    """Test ValidationService initialization."""

    def test_init_with_no_validators(self):
        """Test initialization without ML validators."""
        service = ValidationService()

        assert service._semantic_matcher is None
        assert service._intent_classifier is None
        assert service._entity_extractor is None
        assert service._metrics_recorder is None
        assert service._defect_auto_creator is None

    def test_init_with_custom_validators(self):
        """Test initialization with custom ML validators."""
        mock_matcher = MagicMock()
        mock_classifier = MagicMock()
        mock_extractor = MagicMock()

        service = ValidationService(
            semantic_matcher=mock_matcher,
            intent_classifier=mock_classifier,
            entity_extractor=mock_extractor,
        )

        assert service._semantic_matcher is mock_matcher
        assert service._intent_classifier is mock_classifier
        assert service._entity_extractor is mock_extractor


class TestDetermineReviewStatus:
    """Test the determine_review_status helper function."""

    def test_auto_pass_high_confidence(self):
        """Test auto_pass for confidence >= 75%."""
        assert determine_review_status(0.75) == "auto_pass"
        assert determine_review_status(0.80) == "auto_pass"
        assert determine_review_status(1.0) == "auto_pass"

    def test_needs_review_medium_confidence(self):
        """Test needs_review for 40% <= confidence < 75%."""
        assert determine_review_status(0.40) == "needs_review"
        assert determine_review_status(0.50) == "needs_review"
        assert determine_review_status(0.74) == "needs_review"

    def test_auto_fail_low_confidence(self):
        """Test auto_fail for confidence < 40%."""
        assert determine_review_status(0.0) == "auto_fail"
        assert determine_review_status(0.20) == "auto_fail"
        assert determine_review_status(0.39) == "auto_fail"

    def test_needs_review_none_confidence(self):
        """Test needs_review when confidence is None."""
        assert determine_review_status(None) == "needs_review"


class TestValidationServiceScoring:
    """Test ValidationService scoring methods."""

    def test_calculate_accuracy(self):
        """Test accuracy calculation with weights."""
        service = ValidationService()

        # Test with perfect scores
        accuracy = service._calculate_accuracy(1.0, 1.0, 1.0)
        assert accuracy == 1.0

        # Test with zero scores
        accuracy = service._calculate_accuracy(0.0, 0.0, 0.0)
        assert accuracy == 0.0

        # Test with mixed scores (weights: semantic=0.4, intent=0.4, entity=0.2)
        accuracy = service._calculate_accuracy(0.5, 0.5, 0.5)
        assert accuracy == 0.5

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        service = ValidationService()

        # Test with perfect scores
        confidence = service._calculate_confidence_score(1.0, 1.0)
        assert confidence == 1.0

        # Test with zero scores
        confidence = service._calculate_confidence_score(0.0, 0.0)
        assert confidence == 0.0

        # Test average
        confidence = service._calculate_confidence_score(0.8, 0.6)
        assert confidence == 0.7

    def test_resolve_transcript(self):
        """Test transcript resolution from entities."""
        service = ValidationService()

        # Test with transcript field
        entities = {"transcript": "Hello world"}
        assert service._resolve_transcript(entities) == "Hello world"

        # Test fallback to formatted_transcription
        entities = {"formatted_transcription": "Formatted text"}
        assert service._resolve_transcript(entities) == "Formatted text"

        # Test fallback to raw_transcription
        entities = {"raw_transcription": "Raw text"}
        assert service._resolve_transcript(entities) == "Raw text"

        # Test empty result
        entities = {}
        assert service._resolve_transcript(entities) == ""

    def test_resolve_locale(self):
        """Test locale resolution."""
        service = ValidationService()

        # Test from actual_entities
        actual = {"locale": "en-US"}
        rules = {}
        assert service._resolve_locale(actual, rules) == "en-US"

        # Test from validation_rules
        actual = {}
        rules = {"locale": "es-ES"}
        assert service._resolve_locale(actual, rules) == "es-ES"

        # Test no locale
        actual = {}
        rules = {}
        assert service._resolve_locale(actual, rules) is None


class TestValidationServiceMetadataMethods:
    """Test ValidationService scenario metadata methods."""

    def test_check_alternates_match(self):
        """Test alternate response matching."""
        service = ValidationService()

        alternates = ["Found 3 coffee shops", "I found nearby coffee shops"]

        assert service.check_alternates("Found 3 coffee shops", alternates) is True
        assert service.check_alternates("No match", alternates) is False
        assert service.check_alternates("Found 3 coffee shops", []) is False

    def test_check_confirmation(self):
        """Test confirmation check."""
        service = ValidationService()

        # Default implementation returns True
        assert service.check_confirmation() is True

    def test_requires_confirmation_check(self):
        """Test confirmation requirement check."""
        service = ValidationService()

        # Default implementation returns True
        assert service.requires_confirmation_check() is True

    def test_apply_tolerance(self):
        """Test tolerance application."""
        service = ValidationService()

        # Score meets threshold
        assert service.apply_tolerance(0.85, {'semantic_similarity': 0.8}) is True

        # Score below threshold
        assert service.apply_tolerance(0.75, {'semantic_similarity': 0.8}) is False

        # No threshold specified
        assert service.apply_tolerance(0.5, {}) is True

    def test_get_next_validation_step(self):
        """Test getting next validation step."""
        service = ValidationService()

        # Default returns None
        assert service.get_next_validation_step() is None

    def test_handle_recovery(self):
        """Test recovery handling."""
        service = ValidationService()

        # Default returns empty dict
        assert service.handle_recovery() == {}

    def test_resolve_dynamic_reference(self):
        """Test dynamic reference resolution."""
        service = ValidationService()

        context = {
            'search_results': [
                {'name': 'Coffee Shop A', 'id': '1'},
                {'name': 'Coffee Shop B', 'id': '2'},
                {'name': 'Coffee Shop C', 'id': '3'}
            ]
        }

        # First item
        result = service.resolve_dynamic_reference('first one', context)
        assert result['name'] == 'Coffee Shop A'

        # Second item
        result = service.resolve_dynamic_reference('the second', context)
        assert result['name'] == 'Coffee Shop B'

        # Third item
        result = service.resolve_dynamic_reference('third', context)
        assert result['name'] == 'Coffee Shop C'

        # Empty context
        result = service.resolve_dynamic_reference('first one', {})
        assert result == {}

    def test_evaluate_partial_success(self):
        """Test partial success evaluation."""
        service = ValidationService()

        result = service.evaluate_partial_success()
        assert result['is_partial'] is False
        assert result['matched_criteria'] == []
        assert result['missing_criteria'] == []

    def test_validate_with_metadata(self):
        """Test validation with metadata."""
        service = ValidationService()

        result = service.validate_with_metadata()
        assert result['validated'] is True
        assert result['metadata_applied'] is True


class TestValidationServiceToleranceMethods:
    """Test ValidationService tolerance validation methods."""

    def test_validate_entity_presence(self):
        """Test entity presence validation."""
        service = ValidationService()

        # All entities present
        result = service.validate_entity_presence(
            "The weather in New York is sunny",
            ["weather", "New York"]
        )
        assert result['passed'] is True
        assert result['missing_entities'] == []

        # Missing entities
        result = service.validate_entity_presence(
            "The temperature is 75 degrees",
            ["weather", "New York"]
        )
        assert result['passed'] is False
        assert "New York" in result['missing_entities']

        # No required entities
        result = service.validate_entity_presence("Any text", [])
        assert result['passed'] is True

    def test_validate_forbidden_content(self):
        """Test forbidden content validation."""
        service = ValidationService()

        # No forbidden content
        result = service.validate_forbidden_content(
            "Welcome to our service",
            ["error", "sorry"]
        )
        assert result['passed'] is True
        assert result['found_phrases'] == []

        # Contains forbidden content
        result = service.validate_forbidden_content(
            "I'm sorry, there was an error",
            ["error", "sorry"]
        )
        assert result['passed'] is False
        assert "error" in result['found_phrases']
        assert "sorry" in result['found_phrases']

    def test_validate_tone_polite(self):
        """Test polite tone validation."""
        service = ValidationService()

        # Polite response
        result = service.validate_tone(
            "Thank you for your patience, I'm happy to help",
            "polite"
        )
        assert result['passed'] is True
        assert result['confidence'] > 0.5

        # Neutral response
        result = service.validate_tone(
            "Here is the information",
            "polite"
        )
        assert result['confidence'] == 0.5

    def test_validate_tone_professional(self):
        """Test professional tone validation."""
        service = ValidationService()

        # Professional response
        result = service.validate_tone(
            "Based on the analysis, data indicates positive result",
            "professional"
        )
        assert result['passed'] is True
        assert result['confidence'] > 0.5

    def test_validate_length(self):
        """Test response length validation."""
        service = ValidationService()

        # Within limit
        result = service.validate_length("Short text", 100)
        assert result['passed'] is True
        assert result['actual_length'] == 10
        assert result['max_length'] == 100

        # Exceeds limit
        result = service.validate_length("This is a long text", 10)
        assert result['passed'] is False
        assert result['actual_length'] == 19

    def test_apply_tolerance_checks(self):
        """Test applying all tolerance checks."""
        service = ValidationService()

        response = "Thank you for calling, the weather in New York is sunny"
        config = {
            'required_entities': ['weather', 'New York'],
            'forbidden_phrases': ['error', 'sorry'],
            'tone_requirement': 'polite',
            'max_response_length': 100
        }

        result = service.apply_tolerance_checks(response, config)
        assert result['overall_passed'] is True
        assert result['entity_check']['passed'] is True
        assert result['forbidden_check']['passed'] is True
        assert result['tone_check']['passed'] is True
        assert result['length_check']['passed'] is True

    def test_check_semantic_similarity(self):
        """Test semantic similarity check."""
        service = ValidationService()

        # Identical text
        result = service.check_semantic_similarity(
            "Hello world",
            "Hello world",
            0.8
        )
        assert result['passed'] is True
        assert result['similarity_score'] == 1.0

        # Similar text
        result = service.check_semantic_similarity(
            "Hello world today",
            "Hello world tomorrow",
            0.5
        )
        assert result['passed'] is True  # Good overlap

        # Empty text
        result = service.check_semantic_similarity("", "Hello", 0.5)
        assert result['passed'] is False
        assert result['similarity_score'] == 0.0

    def test_check_confirmation_pattern_affirmative(self):
        """Test affirmative confirmation pattern."""
        service = ValidationService()

        # Affirmative match
        result = service.check_confirmation_pattern("Yes, that's correct", "affirmative")
        assert result['matched'] is True
        assert result['matched_pattern'] in ['yes', 'correct']

        # No match
        result = service.check_confirmation_pattern("No, that's wrong", "affirmative")
        assert result['matched'] is False

    def test_check_confirmation_pattern_negative(self):
        """Test negative confirmation pattern."""
        service = ValidationService()

        # Negative match
        result = service.check_confirmation_pattern("No, I don't want that", "negative")
        assert result['matched'] is True
        assert result['matched_pattern'] == 'no'

        # No match
        result = service.check_confirmation_pattern("Yes please", "negative")
        assert result['matched'] is False

    def test_get_outcome_metadata(self):
        """Test getting outcome metadata."""
        service = ValidationService()

        metadata = service.get_outcome_metadata()
        assert 'acceptable_alternates' in metadata
        assert 'tolerance_settings' in metadata
        assert 'confirmation_required' in metadata
        assert 'allow_partial_success' in metadata


class TestValidationServiceEntityMatching:
    """Test ValidationService entity matching."""

    def test_calculate_entity_match_all_match(self):
        """Test entity match with all matching entities."""
        service = ValidationService()

        actual = {'city': 'New York', 'temperature': '75'}
        expected = {'city': 'New York', 'temperature': '75'}

        score = service._calculate_entity_match(actual, expected)
        assert score == 1.0

    def test_calculate_entity_match_partial(self):
        """Test entity match with partial matching."""
        service = ValidationService()

        actual = {'city': 'New York', 'temperature': '70'}
        expected = {'city': 'New York', 'temperature': '75'}

        score = service._calculate_entity_match(actual, expected)
        assert score == 0.5

    def test_calculate_entity_match_none(self):
        """Test entity match with no matches."""
        service = ValidationService()

        actual = {'city': 'Boston', 'temperature': '60'}
        expected = {'city': 'New York', 'temperature': '75'}

        score = service._calculate_entity_match(actual, expected)
        assert score == 0.0

    def test_calculate_entity_match_excludes_intent(self):
        """Test entity match excludes intent and confidence keys."""
        service = ValidationService()

        actual = {'city': 'New York', 'intent': 'wrong', 'confidence': 0.5}
        expected = {'city': 'New York', 'intent': 'weather', 'confidence': 0.9}

        # Only city should be compared
        score = service._calculate_entity_match(actual, expected)
        assert score == 1.0

    def test_calculate_entity_match_empty_expected(self):
        """Test entity match with no expected entities."""
        service = ValidationService()

        actual = {'city': 'New York'}
        expected = {}

        score = service._calculate_entity_match(actual, expected)
        assert score == 1.0


class TestValidationServiceCandidateIntents:
    """Test ValidationService candidate intent collection."""

    def test_collect_candidate_intents_from_list(self):
        """Test collecting candidates from list."""
        service = ValidationService()

        validation_rules = {
            'intent_labels': ['weather', 'navigation', 'music']
        }

        candidates = service._collect_candidate_intents(
            'weather',
            validation_rules,
            None
        )

        assert 'weather' in candidates
        assert 'navigation' in candidates
        assert 'music' in candidates

    def test_collect_candidate_intents_from_dict_with_locale(self):
        """Test collecting candidates from dict with locale."""
        service = ValidationService()

        validation_rules = {
            'intent_labels': {
                'en-US': ['weather', 'navigation'],
                'default': ['general']
            }
        }

        candidates = service._collect_candidate_intents(
            'weather',
            validation_rules,
            'en-US'
        )

        assert 'weather' in candidates
        assert 'navigation' in candidates
        assert 'general' in candidates

    def test_collect_candidate_intents_adds_expected(self):
        """Test that expected intent is always included."""
        service = ValidationService()

        validation_rules = {
            'intent_labels': ['navigation', 'music']
        }

        candidates = service._collect_candidate_intents(
            'weather',
            validation_rules,
            None
        )

        assert 'weather' in candidates

    def test_collect_candidate_intents_default_fallback(self):
        """Test default fallback when no candidates."""
        service = ValidationService()

        candidates = service._collect_candidate_intents(
            None,
            {},
            None
        )

        assert candidates == ['unknown_intent']


class TestNormaliseExtractedEntities:
    """Test entity normalisation."""

    def test_normalise_extracted_entities(self):
        """Test normalising extracted entities."""
        service = ValidationService()

        extracted = [
            {'label': 'CITY', 'text': 'New York'},
            {'label': 'city', 'text': 'Boston'},
            {'label': 'Temperature', 'text': '75'},
        ]

        normalised = service._normalise_extracted_entities(extracted)

        assert 'new york' in normalised['city']
        assert 'boston' in normalised['city']
        assert '75' in normalised['temperature']

    def test_normalise_extracted_entities_empty(self):
        """Test normalising empty list."""
        service = ValidationService()

        normalised = service._normalise_extracted_entities([])
        assert normalised == {}

    def test_normalise_extracted_entities_skips_empty(self):
        """Test that empty labels/text are skipped."""
        service = ValidationService()

        extracted = [
            {'label': '', 'text': 'value'},
            {'label': 'city', 'text': ''},
        ]

        normalised = service._normalise_extracted_entities(extracted)
        assert normalised == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
