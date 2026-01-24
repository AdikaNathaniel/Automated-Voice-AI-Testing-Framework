"""
Test suite for SSO Integration Service.

Components:
- SAML 2.0 support
- Okta integration
- Azure AD integration
- Google Workspace integration
- LDAP/Active Directory integration
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestSSOServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class SSOService' in service_file_content


class TestSAML:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_saml_method(self, service_file_content):
        assert 'def configure_saml(' in service_file_content

    def test_has_process_saml_response_method(self, service_file_content):
        assert 'def process_saml_response(' in service_file_content


class TestOkta:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_okta_method(self, service_file_content):
        assert 'def configure_okta(' in service_file_content


class TestAzureAD:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_azure_ad_method(self, service_file_content):
        assert 'def configure_azure_ad(' in service_file_content


class TestGoogleWorkspace:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_google_workspace_method(self, service_file_content):
        assert 'def configure_google_workspace(' in service_file_content


class TestLDAP:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_ldap_method(self, service_file_content):
        assert 'def configure_ldap(' in service_file_content

    def test_has_authenticate_ldap_method(self, service_file_content):
        assert 'def authenticate_ldap(' in service_file_content


class TestSSOConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_sso_config_method(self, service_file_content):
        assert 'def get_sso_config(' in service_file_content

    def test_has_get_providers_method(self, service_file_content):
        assert 'def get_providers(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'sso_service.py'
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
            '..', 'backend', 'services', 'sso_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class SSOService' in service_file_content:
            idx = service_file_content.find('class SSOService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
