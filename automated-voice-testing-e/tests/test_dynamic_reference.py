"""
Test suite for dynamic reference resolution functionality.

This module tests handling of contextual references like:
- "the first one", "choose the second result"
- "confirm selection", "yes, that one"
- Dynamic entity resolution from search results
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestDynamicReferenceService:
    """Test DynamicReferenceService for contextual reference handling"""

    def test_service_exists(self):
        """Test that DynamicReferenceService can be imported"""
        from services.dynamic_reference_service import DynamicReferenceService
        assert DynamicReferenceService is not None

    def test_has_resolve_reference_method(self):
        """Test service has resolve_reference method"""
        from services.dynamic_reference_service import DynamicReferenceService

        assert hasattr(DynamicReferenceService, 'resolve_reference')

    def test_has_set_context_method(self):
        """Test service has set_context method"""
        from services.dynamic_reference_service import DynamicReferenceService

        assert hasattr(DynamicReferenceService, 'set_context')

    def test_has_validate_selection_method(self):
        """Test service has validate_selection method"""
        from services.dynamic_reference_service import DynamicReferenceService

        assert hasattr(DynamicReferenceService, 'validate_selection')


class TestOrdinalReferences:
    """Test ordinal reference resolution (first, second, etc.)"""

    def test_resolve_first_one(self):
        """Test resolving 'the first one' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Coffee Shop A', 'id': '1'},
                {'name': 'Coffee Shop B', 'id': '2'},
                {'name': 'Coffee Shop C', 'id': '3'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('the first one')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Coffee Shop A'
        assert result['index'] == 0

    def test_resolve_second_result(self):
        """Test resolving 'the second result' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Restaurant A', 'id': '1'},
                {'name': 'Restaurant B', 'id': '2'},
                {'name': 'Restaurant C', 'id': '3'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('the second result')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Restaurant B'
        assert result['index'] == 1

    def test_resolve_third_option(self):
        """Test resolving 'third option' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Gas Station A'},
                {'name': 'Gas Station B'},
                {'name': 'Gas Station C'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('third option')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Gas Station C'

    def test_resolve_last_one(self):
        """Test resolving 'the last one' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Item A'},
                {'name': 'Item B'},
                {'name': 'Item C'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('the last one')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Item C'


class TestConfirmationReferences:
    """Test confirmation-style references"""

    def test_resolve_yes_that_one(self):
        """Test resolving 'yes, that one' confirms current selection"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'current_selection': {'name': 'Selected Item', 'id': '42'}
        }
        service.set_context(context)

        result = service.resolve_reference('yes, that one')
        assert result['resolved'] is True
        assert result['confirmed'] is True
        assert result['entity']['name'] == 'Selected Item'

    def test_resolve_confirm_selection(self):
        """Test resolving 'confirm selection'"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'current_selection': {'name': 'My Choice', 'id': '100'}
        }
        service.set_context(context)

        result = service.resolve_reference('confirm selection')
        assert result['resolved'] is True
        assert result['confirmed'] is True

    def test_no_selection_to_confirm(self):
        """Test handling when there's no selection to confirm"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {}  # No current selection
        service.set_context(context)

        result = service.resolve_reference('yes, that one')
        assert result['resolved'] is False
        assert 'error' in result


class TestSelectionValidation:
    """Test selection validation against expected entity"""

    def test_validate_correct_selection(self):
        """Test validation passes when correct entity selected"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Coffee Shop A', 'id': '1'},
                {'name': 'Coffee Shop B', 'id': '2'}
            ]
        }
        service.set_context(context)

        # User said "the first one", system should select Coffee Shop A
        result = service.validate_selection(
            reference='the first one',
            selected_entity={'name': 'Coffee Shop A', 'id': '1'}
        )
        assert result['valid'] is True

    def test_validate_incorrect_selection(self):
        """Test validation fails when wrong entity selected"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Coffee Shop A', 'id': '1'},
                {'name': 'Coffee Shop B', 'id': '2'}
            ]
        }
        service.set_context(context)

        # User said "the first one" but system selected second
        result = service.validate_selection(
            reference='the first one',
            selected_entity={'name': 'Coffee Shop B', 'id': '2'}
        )
        assert result['valid'] is False
        assert 'expected' in result
        assert 'actual' in result

    def test_validate_with_partial_match(self):
        """Test validation with partial entity match"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Starbucks Coffee', 'id': '1', 'address': '123 Main St'}
            ]
        }
        service.set_context(context)

        # System selected entity with only some fields
        result = service.validate_selection(
            reference='the first one',
            selected_entity={'name': 'Starbucks Coffee'}
        )
        assert result['valid'] is True


class TestContextManagement:
    """Test context setting and retrieval"""

    def test_set_and_get_context(self):
        """Test setting and retrieving context"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [{'name': 'Test'}],
            'session_id': 'abc123'
        }
        service.set_context(context)

        assert service.get_context() == context

    def test_update_context(self):
        """Test updating existing context"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        service.set_context({'search_results': [{'name': 'A'}]})
        service.set_context({'current_selection': {'name': 'A'}})

        context = service.get_context()
        assert 'search_results' in context
        assert 'current_selection' in context

    def test_clear_context(self):
        """Test clearing context"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        service.set_context({'data': 'test'})
        service.clear_context()

        assert service.get_context() == {}


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_invalid_index_reference(self):
        """Test handling of invalid index reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [{'name': 'Only One'}]
        }
        service.set_context(context)

        result = service.resolve_reference('the fifth one')
        assert result['resolved'] is False
        assert 'error' in result

    def test_empty_search_results(self):
        """Test handling of empty search results"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {'search_results': []}
        service.set_context(context)

        result = service.resolve_reference('the first one')
        assert result['resolved'] is False

    def test_no_context_set(self):
        """Test handling when no context is set"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        result = service.resolve_reference('the first one')
        assert result['resolved'] is False

    def test_unrecognized_reference(self):
        """Test handling of unrecognized reference patterns"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {'search_results': [{'name': 'Test'}]}
        service.set_context(context)

        result = service.resolve_reference('some random text')
        assert result['resolved'] is False


class TestNumericReferences:
    """Test numeric reference patterns"""

    def test_resolve_number_one(self):
        """Test resolving 'number one' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Item 1'},
                {'name': 'Item 2'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('number one')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Item 1'

    def test_resolve_option_two(self):
        """Test resolving 'option 2' reference"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()
        context = {
            'search_results': [
                {'name': 'Choice A'},
                {'name': 'Choice B'}
            ]
        }
        service.set_context(context)

        result = service.resolve_reference('option 2')
        assert result['resolved'] is True
        assert result['entity']['name'] == 'Choice B'


class TestReferencePatterns:
    """Test various reference pattern detection"""

    def test_has_detect_pattern_method(self):
        """Test service has detect_pattern method"""
        from services.dynamic_reference_service import DynamicReferenceService

        assert hasattr(DynamicReferenceService, 'detect_pattern')

    def test_detect_ordinal_pattern(self):
        """Test detecting ordinal patterns"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()

        pattern = service.detect_pattern('the first one')
        assert pattern['type'] == 'ordinal'
        assert pattern['value'] == 1

    def test_detect_confirmation_pattern(self):
        """Test detecting confirmation patterns"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()

        pattern = service.detect_pattern('yes, that one')
        assert pattern['type'] == 'confirmation'

    def test_detect_numeric_pattern(self):
        """Test detecting numeric patterns"""
        from services.dynamic_reference_service import DynamicReferenceService

        service = DynamicReferenceService()

        pattern = service.detect_pattern('number 3')
        assert pattern['type'] == 'numeric'
        assert pattern['value'] == 3


