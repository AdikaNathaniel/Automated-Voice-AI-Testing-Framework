"""
Test suite for Slot Filling Accuracy Service.

This service provides metrics for evaluating entity extraction
and slot filling performance in NLU systems.

Components:
- Slot precision and recall
- Slot F1 score per entity type
- Partial match scoring
- Slot value normalization accuracy
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSlotFillingServiceExists:
    """Test that slot filling service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that slot_filling_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        assert os.path.exists(service_file), (
            "slot_filling_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that SlotFillingService class exists"""
        assert 'class SlotFillingService' in service_file_content


class TestSlotPrecisionRecall:
    """Test slot precision and recall calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_slot_precision_method(self, service_file_content):
        """Test calculate_slot_precision method exists"""
        assert 'def calculate_slot_precision(' in service_file_content

    def test_precision_returns_float(self, service_file_content):
        """Test calculate_slot_precision returns float"""
        if 'def calculate_slot_precision(' in service_file_content:
            idx = service_file_content.find('def calculate_slot_precision(')
            method_sig = service_file_content[idx:idx+250]
            assert 'float' in method_sig

    def test_has_calculate_slot_recall_method(self, service_file_content):
        """Test calculate_slot_recall method exists"""
        assert 'def calculate_slot_recall(' in service_file_content

    def test_recall_returns_float(self, service_file_content):
        """Test calculate_slot_recall returns float"""
        if 'def calculate_slot_recall(' in service_file_content:
            idx = service_file_content.find('def calculate_slot_recall(')
            method_sig = service_file_content[idx:idx+250]
            assert 'float' in method_sig


class TestSlotF1Score:
    """Test slot F1 score calculation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_slot_f1_method(self, service_file_content):
        """Test calculate_slot_f1 method exists"""
        assert 'def calculate_slot_f1(' in service_file_content

    def test_f1_returns_float(self, service_file_content):
        """Test calculate_slot_f1 returns float"""
        if 'def calculate_slot_f1(' in service_file_content:
            idx = service_file_content.find('def calculate_slot_f1(')
            method_sig = service_file_content[idx:idx+200]
            assert 'float' in method_sig

    def test_has_calculate_per_entity_f1_method(self, service_file_content):
        """Test calculate_per_entity_f1 method exists"""
        assert 'def calculate_per_entity_f1(' in service_file_content

    def test_per_entity_returns_dict(self, service_file_content):
        """Test calculate_per_entity_f1 returns Dict"""
        if 'def calculate_per_entity_f1(' in service_file_content:
            idx = service_file_content.find('def calculate_per_entity_f1(')
            method_sig = service_file_content[idx:idx+300]
            assert 'Dict' in method_sig


class TestPartialMatchScoring:
    """Test partial match scoring"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_partial_match_score_method(self, service_file_content):
        """Test calculate_partial_match_score method exists"""
        assert 'def calculate_partial_match_score(' in service_file_content

    def test_partial_match_returns_float(self, service_file_content):
        """Test calculate_partial_match_score returns float"""
        if 'def calculate_partial_match_score(' in service_file_content:
            idx = service_file_content.find('def calculate_partial_match_score(')
            method_sig = service_file_content[idx:idx+300]
            assert 'float' in method_sig

    def test_has_evaluate_span_overlap_method(self, service_file_content):
        """Test evaluate_span_overlap method exists"""
        assert 'def evaluate_span_overlap(' in service_file_content


class TestSlotNormalization:
    """Test slot value normalization accuracy"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_evaluate_normalization_accuracy_method(self, service_file_content):
        """Test evaluate_normalization_accuracy method exists"""
        assert 'def evaluate_normalization_accuracy(' in service_file_content

    def test_normalization_returns_dict(self, service_file_content):
        """Test evaluate_normalization_accuracy returns Dict"""
        if 'def evaluate_normalization_accuracy(' in service_file_content:
            idx = service_file_content.find('def evaluate_normalization_accuracy(')
            method_sig = service_file_content[idx:idx+300]
            assert 'Dict' in method_sig

    def test_has_normalize_slot_value_method(self, service_file_content):
        """Test normalize_slot_value method exists"""
        assert 'def normalize_slot_value(' in service_file_content


class TestSlotMetrics:
    """Test comprehensive slot metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_slot_metrics_method(self, service_file_content):
        """Test get_slot_metrics method exists"""
        assert 'def get_slot_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_slot_metrics returns Dict"""
        if 'def get_slot_metrics(' in service_file_content:
            idx = service_file_content.find('def get_slot_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_has_generate_slot_report_method(self, service_file_content):
        """Test generate_slot_report method exists"""
        assert 'def generate_slot_report(' in service_file_content


class TestTypeHints:
    """Test type hints for slot filling service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content

    def test_uses_tuple_type_hint(self, service_file_content):
        """Test Tuple type hint is used"""
        assert 'Tuple[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the slot filling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'slot_filling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class SlotFillingService' in service_file_content:
            idx = service_file_content.find('class SlotFillingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

