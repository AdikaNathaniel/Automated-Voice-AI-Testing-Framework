"""
Test suite for OAuth Provider Service.

Components:
- Provider registration
- Authorization code flow
- Token exchange
- Token refresh
- OIDC ID token validation
- Token introspection
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestOAuthProviderServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class OAuthProviderService' in service_file_content


class TestProviderRegistration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_register_provider_method(self, service_file_content):
        assert 'def register_provider(' in service_file_content

    def test_has_get_provider_method(self, service_file_content):
        assert 'def get_provider(' in service_file_content

    def test_has_list_providers_method(self, service_file_content):
        assert 'def list_providers(' in service_file_content


class TestAuthorizationCodeFlow:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_generate_authorization_url_method(self, service_file_content):
        assert 'def generate_authorization_url(' in service_file_content

    def test_has_exchange_code_for_tokens_method(self, service_file_content):
        assert 'def exchange_code_for_tokens(' in service_file_content


class TestTokenManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_refresh_access_token_method(self, service_file_content):
        assert 'def refresh_access_token(' in service_file_content

    def test_has_revoke_token_method(self, service_file_content):
        assert 'def revoke_token(' in service_file_content


class TestOIDCValidation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_validate_id_token_method(self, service_file_content):
        assert 'def validate_id_token(' in service_file_content

    def test_has_get_jwks_method(self, service_file_content):
        assert 'def get_jwks(' in service_file_content


class TestTokenIntrospection:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_introspect_token_method(self, service_file_content):
        assert 'def introspect_token(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_oauth_config_method(self, service_file_content):
        assert 'def get_oauth_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'oauth_provider_service.py'
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
            '..', 'backend', 'services', 'oauth_provider_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class OAuthProviderService' in service_file_content:
            idx = service_file_content.find('class OAuthProviderService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
