"""
Test suite for Disambiguation Handling Service.

This service provides testing and validation for disambiguation
handling in conversational AI systems.

Components:
- Clarification question generation
- User correction handling
- Implicit vs explicit disambiguation
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDisambiguationHandlingServiceExists:
    """Test that disambiguation handling service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that disambiguation_handling_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        assert os.path.exists(service_file), (
            "disambiguation_handling_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that DisambiguationHandlingService class exists"""
        assert 'class DisambiguationHandlingService' in service_file_content


class TestClarificationQuestionGeneration:
    """Test clarification question generation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_clarification_generation_method(self, service_file_content):
        """Test test_clarification_generation method exists"""
        assert 'def test_clarification_generation(' in service_file_content

    def test_clarification_returns_dict(self, service_file_content):
        """Test test_clarification_generation returns Dict"""
        if 'def test_clarification_generation(' in service_file_content:
            idx = service_file_content.find('def test_clarification_generation(')
            method_sig = service_file_content[idx:idx+300]
            assert 'Dict' in method_sig

    def test_has_generate_clarification_test_cases_method(self, service_file_content):
        """Test generate_clarification_test_cases method exists"""
        assert 'def generate_clarification_test_cases(' in service_file_content


class TestUserCorrectionHandling:
    """Test user correction handling"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_correction_handling_method(self, service_file_content):
        """Test test_correction_handling method exists"""
        assert 'def test_correction_handling(' in service_file_content

    def test_has_generate_correction_test_cases_method(self, service_file_content):
        """Test generate_correction_test_cases method exists"""
        assert 'def generate_correction_test_cases(' in service_file_content


class TestImplicitExplicitDisambiguation:
    """Test implicit vs explicit disambiguation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_test_disambiguation_method(self, service_file_content):
        """Test test_disambiguation method exists"""
        assert 'def test_disambiguation(' in service_file_content

    def test_has_generate_disambiguation_test_cases_method(self, service_file_content):
        """Test generate_disambiguation_test_cases method exists"""
        assert 'def generate_disambiguation_test_cases(' in service_file_content


class TestDisambiguationMetrics:
    """Test disambiguation metrics"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_disambiguation_metrics_method(self, service_file_content):
        """Test get_disambiguation_metrics method exists"""
        assert 'def get_disambiguation_metrics(' in service_file_content

    def test_metrics_returns_dict(self, service_file_content):
        """Test get_disambiguation_metrics returns Dict"""
        if 'def get_disambiguation_metrics(' in service_file_content:
            idx = service_file_content.find('def get_disambiguation_metrics(')
            method_sig = service_file_content[idx:idx+300]
            assert 'Dict' in method_sig


class TestTypeHints:
    """Test type hints for disambiguation handling service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
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


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the disambiguation handling service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'disambiguation_handling_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class DisambiguationHandlingService' in service_file_content:
            idx = service_file_content.find('class DisambiguationHandlingService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section

