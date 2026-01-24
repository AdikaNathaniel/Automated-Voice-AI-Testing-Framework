"""
Test suite for validator interpretation of scenario metadata.

This module tests that validators properly interpret:
- Acceptable alternates
- Confirmation requirements
- Tolerance settings
- Multi-path conversations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestValidatorAlternatesSupport:
    """Test validator support for acceptable alternates"""

    def test_validation_service_has_check_alternates_method(self):
        """Test that ValidationService has check_alternates method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'check_alternates')

    def test_check_alternates_returns_true_for_match(self):
        """Test that check_alternates returns True when response matches"""
        from services.validation_service import ValidationService

        service = ValidationService()
        alternates = ["Found 3 coffee shops", "I found nearby coffee shops"]
        response = "Found 3 coffee shops"

        result = service.check_alternates(response, alternates)
        assert result is True

    def test_check_alternates_returns_false_for_no_match(self):
        """Test that check_alternates returns False when no match"""
        from services.validation_service import ValidationService

        service = ValidationService()
        alternates = ["Found 3 coffee shops", "I found nearby coffee shops"]
        response = "No coffee shops found"

        result = service.check_alternates(response, alternates)
        assert result is False


class TestValidatorConfirmationSupport:
    """Test validator support for confirmation requirements"""

    def test_validation_service_has_check_confirmation_method(self):
        """Test that ValidationService has check_confirmation method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'check_confirmation')

    def test_validation_service_has_requires_confirmation_check_method(self):
        """Test that ValidationService has requires_confirmation_check method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'requires_confirmation_check')


class TestValidatorToleranceSupport:
    """Test validator support for tolerance settings"""

    def test_validation_service_has_apply_tolerance_method(self):
        """Test that ValidationService has apply_tolerance method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'apply_tolerance')

    def test_apply_tolerance_uses_semantic_threshold(self):
        """Test that apply_tolerance uses semantic similarity threshold"""
        from services.validation_service import ValidationService

        service = ValidationService()
        tolerance_settings = {'semantic_similarity': 0.8}
        score = 0.85

        result = service.apply_tolerance(score, tolerance_settings)
        assert result is True  # 0.85 >= 0.8

    def test_apply_tolerance_fails_below_threshold(self):
        """Test that apply_tolerance returns False below threshold"""
        from services.validation_service import ValidationService

        service = ValidationService()
        tolerance_settings = {'semantic_similarity': 0.9}
        score = 0.85

        result = service.apply_tolerance(score, tolerance_settings)
        assert result is False  # 0.85 < 0.9


class TestValidatorMultiPathSupport:
    """Test validator support for multi-path conversations"""

    def test_validation_service_has_get_next_step_method(self):
        """Test that ValidationService has get_next_step method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'get_next_validation_step')

    def test_validation_service_has_handle_recovery_method(self):
        """Test that ValidationService has handle_recovery method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'handle_recovery')


class TestValidatorDynamicContext:
    """Test validator support for dynamic context"""

    def test_validation_service_has_resolve_dynamic_reference_method(self):
        """Test that ValidationService has resolve_dynamic_reference method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'resolve_dynamic_reference')

    def test_resolve_first_one_reference(self):
        """Test resolving 'first one' reference from context"""
        from services.validation_service import ValidationService

        service = ValidationService()
        context = {
            'search_results': [
                {'name': 'Coffee Shop A', 'id': '1'},
                {'name': 'Coffee Shop B', 'id': '2'}
            ]
        }

        result = service.resolve_dynamic_reference('first one', context)
        assert result['name'] == 'Coffee Shop A'


class TestValidatorPartialSuccess:
    """Test validator support for partial success"""

    def test_validation_service_has_evaluate_partial_success_method(self):
        """Test that ValidationService has evaluate_partial_success method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'evaluate_partial_success')


class TestValidatorScenarioMetadataIntegration:
    """Test integration of scenario metadata in validation"""

    def test_validation_service_has_validate_with_metadata_method(self):
        """Test that ValidationService has validate_with_metadata method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'validate_with_metadata')

    def test_validation_service_has_get_outcome_metadata_method(self):
        """Test that ValidationService has get_outcome_metadata method"""
        from services.validation_service import ValidationService

        service = ValidationService()
        assert hasattr(service, 'get_outcome_metadata')
