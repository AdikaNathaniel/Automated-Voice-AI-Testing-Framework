"""
Test suite for Error Categorization Service.

Components:
- Automatic error type classification
- Root cause clustering
- Error pattern detection
- Recurring error identification
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestErrorCategorizationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ErrorCategorizationService' in service_file_content


class TestErrorClassification:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_classify_error_method(self, service_file_content):
        assert 'def classify_error(' in service_file_content

    def test_has_get_error_types_method(self, service_file_content):
        assert 'def get_error_types(' in service_file_content


class TestRootCauseClustering:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_cluster_errors_method(self, service_file_content):
        assert 'def cluster_errors(' in service_file_content

    def test_has_get_root_causes_method(self, service_file_content):
        assert 'def get_root_causes(' in service_file_content


class TestPatternDetection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_detect_patterns_method(self, service_file_content):
        assert 'def detect_patterns(' in service_file_content

    def test_has_get_pattern_summary_method(self, service_file_content):
        assert 'def get_pattern_summary(' in service_file_content


class TestRecurringErrors:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_identify_recurring_method(self, service_file_content):
        assert 'def identify_recurring(' in service_file_content

    def test_has_get_recurrence_report_method(self, service_file_content):
        assert 'def get_recurrence_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_categorization_config_method(self, service_file_content):
        assert 'def get_categorization_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'error_categorization_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ErrorCategorizationService' in service_file_content:
            idx = service_file_content.find('class ErrorCategorizationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
