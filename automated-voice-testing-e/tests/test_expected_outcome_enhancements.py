"""
Test suite for ExpectedOutcome model enhancements.

This module tests the new fields added to ExpectedOutcome:
- Scenario step references
- Acceptable alternates
- Confirmation required flags
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestScenarioStepReference:
    """Test scenario step reference field"""

    def test_expected_outcome_has_scenario_step_id_field(self):
        """Test that ExpectedOutcome has scenario_step_id field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'scenario_step_id' in columns, \
            "scenario_step_id field should exist"

    def test_scenario_step_id_is_nullable(self):
        """Test that scenario_step_id is nullable (optional link)"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert columns['scenario_step_id'].nullable is True

    def test_expected_outcome_has_step_relationship(self):
        """Test that ExpectedOutcome has step relationship"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'scenario_step')


class TestAcceptableAlternates:
    """Test acceptable alternates field"""

    def test_expected_outcome_has_acceptable_alternates_field(self):
        """Test that ExpectedOutcome has acceptable_alternates JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'acceptable_alternates' in columns, \
            "acceptable_alternates field should exist"

    def test_acceptable_alternates_is_jsonb(self):
        """Test that acceptable_alternates is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['acceptable_alternates'].type)

    def test_add_acceptable_alternate_method(self):
        """Test add_acceptable_alternate helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'add_acceptable_alternate')

    def test_remove_acceptable_alternate_method(self):
        """Test remove_acceptable_alternate helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'remove_acceptable_alternate')

    def test_has_acceptable_alternates_method(self):
        """Test has_acceptable_alternates helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'has_acceptable_alternates')


class TestConfirmationFlags:
    """Test confirmation required flags"""

    def test_expected_outcome_has_confirmation_required_field(self):
        """Test that ExpectedOutcome has confirmation_required field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'confirmation_required' in columns, \
            "confirmation_required field should exist"

    def test_confirmation_required_defaults_to_false(self):
        """Test that confirmation_required defaults to False"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        col = columns['confirmation_required']
        assert col.default.arg is False

    def test_expected_outcome_has_confirmation_prompt_field(self):
        """Test that ExpectedOutcome has confirmation_prompt field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'confirmation_prompt' in columns, \
            "confirmation_prompt field should exist"

    def test_expected_outcome_has_allow_partial_success_field(self):
        """Test that ExpectedOutcome has allow_partial_success field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'allow_partial_success' in columns, \
            "allow_partial_success field should exist"


class TestToleranceFields:
    """Test tolerance-related fields"""

    def test_expected_outcome_has_tolerance_settings_field(self):
        """Test that ExpectedOutcome has tolerance_settings JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'tolerance_settings' in columns, \
            "tolerance_settings field should exist"

    def test_tolerance_settings_is_jsonb(self):
        """Test that tolerance_settings is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['tolerance_settings'].type)

    def test_set_semantic_tolerance_method(self):
        """Test set_semantic_tolerance helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'set_semantic_tolerance')

    def test_set_entity_tolerance_method(self):
        """Test set_entity_tolerance helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'set_entity_tolerance')


class TestMultiPathSupport:
    """Test multi-path conversation support fields"""

    def test_expected_outcome_has_next_step_on_success_field(self):
        """Test that ExpectedOutcome has next_step_on_success field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'next_step_on_success' in columns, \
            "next_step_on_success field should exist"

    def test_expected_outcome_has_next_step_on_failure_field(self):
        """Test that ExpectedOutcome has next_step_on_failure field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'next_step_on_failure' in columns, \
            "next_step_on_failure field should exist"

    def test_expected_outcome_has_recovery_path_field(self):
        """Test that ExpectedOutcome has recovery_path JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'recovery_path' in columns, \
            "recovery_path field should exist"


class TestHelperMethods:
    """Test new helper methods for enhanced functionality"""

    def test_requires_confirmation_method(self):
        """Test requires_confirmation helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'requires_confirmation')

    def test_get_tolerance_method(self):
        """Test get_tolerance helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'get_tolerance')

    def test_matches_alternate_method(self):
        """Test matches_alternate helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'matches_alternate')

    def test_get_next_step_method(self):
        """Test get_next_step helper method"""
        from models.expected_outcome import ExpectedOutcome

        assert hasattr(ExpectedOutcome, 'get_next_step')


class TestScenarioMetadata:
    """Test scenario metadata fields"""

    def test_expected_outcome_has_scenario_metadata_field(self):
        """Test that ExpectedOutcome has scenario_metadata JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'scenario_metadata' in columns, \
            "scenario_metadata field should exist"

    def test_scenario_metadata_is_jsonb(self):
        """Test that scenario_metadata is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['scenario_metadata'].type)


class TestContextFields:
    """Test context-related fields for dynamic references"""

    def test_expected_outcome_has_dynamic_context_field(self):
        """Test that ExpectedOutcome has dynamic_context JSONB field"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'dynamic_context' in columns, \
            "dynamic_context field should exist"

    def test_dynamic_context_is_jsonb(self):
        """Test that dynamic_context is JSONB type"""
        from models.expected_outcome import ExpectedOutcome

        columns = {c.name: c for c in ExpectedOutcome.__table__.columns}
        assert 'JSONB' in str(columns['dynamic_context'].type)
