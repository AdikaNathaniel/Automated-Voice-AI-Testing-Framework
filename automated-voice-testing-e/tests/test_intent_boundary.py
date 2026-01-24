"""
Test suite for Intent Boundary Testing Service.

This service provides metrics for evaluating how well an NLU system
handles boundary cases between similar intents.

Components:
- Similar intent disambiguation
- Intent overlap measurement
- Edge case utterances for each intent
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIntentBoundaryServiceExists:
    """Test that intent boundary service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that intent_boundary_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        assert os.path.exists(service_file), (
            "intent_boundary_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that IntentBoundaryService class exists"""
        assert 'class IntentBoundaryService' in service_file_content


class TestSimilarIntentDisambiguation:
    """Test similar intent disambiguation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_intent_similarity_method(self, service_file_content):
        """Test calculate_intent_similarity method exists"""
        assert 'def calculate_intent_similarity(' in service_file_content

    def test_similarity_returns_float(self, service_file_content):
        """Test calculate_intent_similarity returns float"""
        if 'def calculate_intent_similarity(' in service_file_content:
            idx = service_file_content.find('def calculate_intent_similarity(')
            method_sig = service_file_content[idx:idx+300]
            assert 'float' in method_sig

    def test_has_find_similar_intents_method(self, service_file_content):
        """Test find_similar_intents method exists"""
        assert 'def find_similar_intents(' in service_file_content

    def test_find_similar_returns_list(self, service_file_content):
        """Test find_similar_intents returns List"""
        if 'def find_similar_intents(' in service_file_content:
            idx = service_file_content.find('def find_similar_intents(')
            method_sig = service_file_content[idx:idx+300]
            assert 'List' in method_sig

    def test_has_calculate_disambiguation_score_method(self, service_file_content):
        """Test calculate_disambiguation_score method exists"""
        assert 'def calculate_disambiguation_score(' in service_file_content


class TestIntentOverlapMeasurement:
    """Test intent overlap measurement"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_calculate_overlap_method(self, service_file_content):
        """Test calculate_overlap method exists"""
        assert 'def calculate_overlap(' in service_file_content

    def test_overlap_returns_dict(self, service_file_content):
        """Test calculate_overlap returns Dict"""
        if 'def calculate_overlap(' in service_file_content:
            idx = service_file_content.find('def calculate_overlap(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig

    def test_has_identify_overlap_regions_method(self, service_file_content):
        """Test identify_overlap_regions method exists"""
        assert 'def identify_overlap_regions(' in service_file_content

    def test_has_calculate_boundary_sharpness_method(self, service_file_content):
        """Test calculate_boundary_sharpness method exists"""
        assert 'def calculate_boundary_sharpness(' in service_file_content


class TestEdgeCaseUtterances:
    """Test edge case utterance handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_identify_edge_cases_method(self, service_file_content):
        """Test identify_edge_cases method exists"""
        assert 'def identify_edge_cases(' in service_file_content

    def test_edge_cases_returns_list(self, service_file_content):
        """Test identify_edge_cases returns List"""
        if 'def identify_edge_cases(' in service_file_content:
            idx = service_file_content.find('def identify_edge_cases(')
            method_sig = service_file_content[idx:idx+250]
            assert 'List' in method_sig

    def test_has_evaluate_edge_case_performance_method(self, service_file_content):
        """Test evaluate_edge_case_performance method exists"""
        assert 'def evaluate_edge_case_performance(' in service_file_content

    def test_has_generate_edge_case_report_method(self, service_file_content):
        """Test generate_edge_case_report method exists"""
        assert 'def generate_edge_case_report(' in service_file_content


class TestBoundaryAnalysis:
    """Test boundary analysis functionality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_analyze_decision_boundary_method(self, service_file_content):
        """Test analyze_decision_boundary method exists"""
        assert 'def analyze_decision_boundary(' in service_file_content

    def test_has_get_boundary_metrics_method(self, service_file_content):
        """Test get_boundary_metrics method exists"""
        assert 'def get_boundary_metrics(' in service_file_content

    def test_boundary_metrics_returns_dict(self, service_file_content):
        """Test get_boundary_metrics returns Dict"""
        if 'def get_boundary_metrics(' in service_file_content:
            idx = service_file_content.find('def get_boundary_metrics(')
            method_sig = service_file_content[idx:idx+250]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for intent boundary service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
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
        """Read the intent boundary service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'intent_boundary_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class IntentBoundaryService' in service_file_content:
            idx = service_file_content.find('class IntentBoundaryService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

