"""
Test suite for Industry-specific Compliance Service.

Components:
- HIPAA for healthcare voice AI
- PCI-DSS for payment voice AI
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIndustryComplianceServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class IndustryComplianceService' in service_file_content


class TestHIPAACompliance:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_hipaa_compliance_method(self, service_file_content):
        assert 'def check_hipaa_compliance(' in service_file_content

    def test_has_detect_phi_method(self, service_file_content):
        assert 'def detect_phi(' in service_file_content

    def test_has_get_hipaa_requirements_method(self, service_file_content):
        assert 'def get_hipaa_requirements(' in service_file_content


class TestPCIDSSCompliance:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_pcidss_compliance_method(self, service_file_content):
        assert 'def check_pcidss_compliance(' in service_file_content

    def test_has_detect_payment_data_method(self, service_file_content):
        assert 'def detect_payment_data(' in service_file_content

    def test_has_get_pcidss_requirements_method(self, service_file_content):
        assert 'def get_pcidss_requirements(' in service_file_content


class TestIndustryConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_industry_config_method(self, service_file_content):
        assert 'def get_industry_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'industry_compliance_service.py'
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
            '..', 'backend', 'services', 'industry_compliance_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class IndustryComplianceService' in service_file_content:
            idx = service_file_content.find('class IndustryComplianceService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
