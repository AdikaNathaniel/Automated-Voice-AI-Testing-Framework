"""
Test suite for Bias Mitigation Service.

Components:
- Pre/post mitigation comparison
- Fairness improvement trends
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestBiasMitigationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class BiasMitigationService' in service_file_content


class TestPrePostComparison:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_compare_pre_post_method(self, service_file_content):
        assert 'def compare_pre_post(' in service_file_content

    def test_has_record_baseline_method(self, service_file_content):
        assert 'def record_baseline(' in service_file_content

    def test_has_record_post_mitigation_method(self, service_file_content):
        assert 'def record_post_mitigation(' in service_file_content


class TestFairnessImprovementTrends:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_track_fairness_trend_method(self, service_file_content):
        assert 'def track_fairness_trend(' in service_file_content

    def test_has_get_improvement_history_method(self, service_file_content):
        assert 'def get_improvement_history(' in service_file_content


class TestMitigationReporting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_mitigation_report_method(self, service_file_content):
        assert 'def generate_mitigation_report(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_mitigation_config_method(self, service_file_content):
        assert 'def get_mitigation_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'bias_mitigation_service.py'
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
            '..', 'backend', 'services', 'bias_mitigation_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class BiasMitigationService' in service_file_content:
            idx = service_file_content.find('class BiasMitigationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
