"""
Test suite for multi-path conversation support.

This module tests the framework's ability to handle:
- Branching conversations based on validation results
- Recovery paths for failed validations
- Dynamic context propagation between steps
- Confirmation flows
- Partial success scenarios
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestExpectedOutcomeMultiPath:
    """Test ExpectedOutcome multi-path support"""

    def test_has_next_step_on_success_field(self):
        """Test ExpectedOutcome has next_step_on_success field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'next_step_on_success' in columns

    def test_has_next_step_on_failure_field(self):
        """Test ExpectedOutcome has next_step_on_failure field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'next_step_on_failure' in columns

    def test_has_get_next_step_method(self):
        """Test ExpectedOutcome has get_next_step method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'get_next_step')
        assert callable(getattr(ExpectedOutcome, 'get_next_step'))

    def test_next_step_fields_are_uuid(self):
        """Test next_step fields are UUID type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'UUID' in str(columns['next_step_on_success'].type)
        assert 'UUID' in str(columns['next_step_on_failure'].type)


class TestExpectedOutcomeRecoveryPath:
    """Test ExpectedOutcome recovery path support"""

    def test_has_recovery_path_field(self):
        """Test ExpectedOutcome has recovery_path field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'recovery_path' in columns

    def test_recovery_path_is_jsonb(self):
        """Test recovery_path is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['recovery_path'].type)

    def test_recovery_path_is_nullable(self):
        """Test recovery_path can be None"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert columns['recovery_path'].nullable is True


class TestExpectedOutcomeConfirmationFlow:
    """Test ExpectedOutcome confirmation flow support"""

    def test_has_confirmation_required_field(self):
        """Test ExpectedOutcome has confirmation_required field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'confirmation_required' in columns

    def test_has_confirmation_prompt_field(self):
        """Test ExpectedOutcome has confirmation_prompt field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'confirmation_prompt' in columns

    def test_has_requires_confirmation_method(self):
        """Test ExpectedOutcome has requires_confirmation method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'requires_confirmation')

    def test_confirmation_required_is_boolean(self):
        """Test confirmation_required is Boolean type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'BOOLEAN' in str(columns['confirmation_required'].type)


class TestExpectedOutcomeDynamicContext:
    """Test ExpectedOutcome dynamic context support"""

    def test_has_dynamic_context_field(self):
        """Test ExpectedOutcome has dynamic_context field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'dynamic_context' in columns

    def test_dynamic_context_is_jsonb(self):
        """Test dynamic_context is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['dynamic_context'].type)

    def test_dynamic_context_is_nullable(self):
        """Test dynamic_context can be None"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert columns['dynamic_context'].nullable is True


class TestExpectedOutcomeToleranceSettings:
    """Test ExpectedOutcome tolerance settings for flexible matching"""

    def test_has_tolerance_settings_field(self):
        """Test ExpectedOutcome has tolerance_settings field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'tolerance_settings' in columns

    def test_has_set_semantic_tolerance_method(self):
        """Test ExpectedOutcome has set_semantic_tolerance method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'set_semantic_tolerance')

    def test_has_set_entity_tolerance_method(self):
        """Test ExpectedOutcome has set_entity_tolerance method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'set_entity_tolerance')

    def test_has_get_tolerance_method(self):
        """Test ExpectedOutcome has get_tolerance method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'get_tolerance')


class TestExpectedOutcomePartialSuccess:
    """Test ExpectedOutcome partial success support"""

    def test_has_allow_partial_success_field(self):
        """Test ExpectedOutcome has allow_partial_success field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'allow_partial_success' in columns

    def test_allow_partial_success_is_boolean(self):
        """Test allow_partial_success is Boolean type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'BOOLEAN' in str(columns['allow_partial_success'].type)

    def test_allow_partial_success_defaults_to_false(self):
        """Test allow_partial_success defaults to False"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        col = columns['allow_partial_success']
        assert col.default.arg is False


class TestExpectedOutcomeAcceptableAlternates:
    """Test ExpectedOutcome acceptable alternates support"""

    def test_has_acceptable_alternates_field(self):
        """Test ExpectedOutcome has acceptable_alternates field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'acceptable_alternates' in columns

    def test_has_add_acceptable_alternate_method(self):
        """Test ExpectedOutcome has add_acceptable_alternate method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'add_acceptable_alternate')

    def test_has_remove_acceptable_alternate_method(self):
        """Test ExpectedOutcome has remove_acceptable_alternate method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'remove_acceptable_alternate')

    def test_has_has_acceptable_alternates_method(self):
        """Test ExpectedOutcome has has_acceptable_alternates method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'has_acceptable_alternates')

    def test_has_matches_alternate_method(self):
        """Test ExpectedOutcome has matches_alternate method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'matches_alternate')


class TestValidationServiceMultiPath:
    """Test ValidationService multi-path conversation support"""

    def test_service_can_get_next_step(self):
        """Test service has get_next_validation_step method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.get_next_validation_step()
        # Returns None when no context set
        assert result is None

    def test_service_can_handle_recovery(self):
        """Test service has handle_recovery method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.handle_recovery()
        assert isinstance(result, dict)

    def test_service_resolves_first_one_reference(self):
        """Test service resolves 'first one' reference"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {
            "search_results": [
                {"name": "Shop A", "id": "1"},
                {"name": "Shop B", "id": "2"},
                {"name": "Shop C", "id": "3"}
            ]
        }

        first = service.resolve_dynamic_reference("first one", context)
        assert first["name"] == "Shop A"

    def test_service_resolves_second_reference(self):
        """Test service resolves 'second' reference"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {
            "search_results": [
                {"name": "Shop A", "id": "1"},
                {"name": "Shop B", "id": "2"}
            ]
        }

        second = service.resolve_dynamic_reference("second", context)
        assert second["name"] == "Shop B"

    def test_service_resolves_the_third_reference(self):
        """Test service resolves 'the third' reference"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {
            "search_results": [
                {"name": "Shop A", "id": "1"},
                {"name": "Shop B", "id": "2"},
                {"name": "Shop C", "id": "3"}
            ]
        }

        third = service.resolve_dynamic_reference("the third", context)
        assert third["name"] == "Shop C"

    def test_service_returns_empty_for_invalid_reference(self):
        """Test service returns empty dict for invalid references"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {"search_results": [{"name": "Only one"}]}

        # Reference beyond available results
        result = service.resolve_dynamic_reference("third one", context)
        assert result == {}

    def test_service_returns_empty_for_empty_context(self):
        """Test service returns empty dict for empty context"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {"search_results": []}

        result = service.resolve_dynamic_reference("first one", context)
        assert result == {}

    def test_service_evaluates_partial_success(self):
        """Test service evaluates partial success"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.evaluate_partial_success()

        assert "is_partial" in result
        assert "matched_criteria" in result
        assert "missing_criteria" in result


class TestValidationServiceTolerance:
    """Test ValidationService tolerance application"""

    def test_apply_tolerance_passes_when_meets_threshold(self):
        """Test tolerance passes when score meets threshold"""
        from services.validation_service import ValidationService

        service = ValidationService()
        settings = {"semantic_similarity": 0.7}

        assert service.apply_tolerance(0.8, settings) is True
        assert service.apply_tolerance(0.7, settings) is True

    def test_apply_tolerance_fails_when_below_threshold(self):
        """Test tolerance fails when score below threshold"""
        from services.validation_service import ValidationService

        service = ValidationService()
        settings = {"semantic_similarity": 0.8}

        assert service.apply_tolerance(0.79, settings) is False
        assert service.apply_tolerance(0.5, settings) is False

    def test_apply_tolerance_with_zero_threshold(self):
        """Test tolerance with zero threshold always passes"""
        from services.validation_service import ValidationService

        service = ValidationService()
        settings = {"semantic_similarity": 0.0}

        assert service.apply_tolerance(0.0, settings) is True
        assert service.apply_tolerance(0.1, settings) is True

    def test_apply_tolerance_exact_threshold(self):
        """Test tolerance passes when exactly at threshold"""
        from services.validation_service import ValidationService

        service = ValidationService()
        settings = {"semantic_similarity": 0.85}

        assert service.apply_tolerance(0.85, settings) is True


class TestValidationServiceMetadataIntegration:
    """Test ValidationService metadata integration"""

    def test_validate_with_metadata(self):
        """Test validation with metadata integration"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.validate_with_metadata()

        assert result["validated"] is True
        assert result["metadata_applied"] is True

    def test_get_outcome_metadata(self):
        """Test getting outcome metadata"""
        from services.validation_service import ValidationService

        service = ValidationService()
        metadata = service.get_outcome_metadata()

        assert "acceptable_alternates" in metadata
        assert "tolerance_settings" in metadata
        assert "confirmation_required" in metadata
        assert "allow_partial_success" in metadata

    def test_check_alternates_returns_true_for_match(self):
        """Test check_alternates returns True for matching response"""
        from services.validation_service import ValidationService

        service = ValidationService()
        alternates = ["Response A", "Response B", "Response C"]

        assert service.check_alternates("Response B", alternates) is True

    def test_check_alternates_returns_false_for_no_match(self):
        """Test check_alternates returns False for non-matching response"""
        from services.validation_service import ValidationService

        service = ValidationService()
        alternates = ["Response A", "Response B"]

        assert service.check_alternates("Response X", alternates) is False

    def test_check_alternates_with_empty_list(self):
        """Test check_alternates returns False for empty list"""
        from services.validation_service import ValidationService

        service = ValidationService()

        assert service.check_alternates("Any response", []) is False


class TestExpectedOutcomeScenarioMetadata:
    """Test ExpectedOutcome scenario metadata support"""

    def test_has_scenario_metadata_field(self):
        """Test ExpectedOutcome has scenario_metadata field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'scenario_metadata' in columns

    def test_scenario_metadata_is_jsonb(self):
        """Test scenario_metadata is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['scenario_metadata'].type)

    def test_has_scenario_step_id_field(self):
        """Test ExpectedOutcome has scenario_step_id field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'scenario_step_id' in columns

    def test_scenario_step_id_is_uuid(self):
        """Test scenario_step_id is UUID type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'UUID' in str(columns['scenario_step_id'].type)


class TestValidationServiceConfirmation:
    """Test ValidationService confirmation support"""

    def test_has_check_confirmation_method(self):
        """Test ValidationService has check_confirmation method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'check_confirmation')

    def test_has_requires_confirmation_check_method(self):
        """Test ValidationService has requires_confirmation_check method"""
        from services.validation_service import ValidationService

        assert hasattr(ValidationService, 'requires_confirmation_check')

    def test_check_confirmation_returns_bool(self):
        """Test check_confirmation returns boolean"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.check_confirmation()
        assert isinstance(result, bool)

    def test_requires_confirmation_check_returns_bool(self):
        """Test requires_confirmation_check returns boolean"""
        from services.validation_service import ValidationService

        service = ValidationService()
        result = service.requires_confirmation_check()
        assert isinstance(result, bool)

