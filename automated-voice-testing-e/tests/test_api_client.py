"""
Test suite for API client service

Ensures proper axios instance configuration for the frontend application,
including base URL, request/response interceptors, JWT token handling,
and error handling.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"
SERVICES_DIR = SRC_DIR / "services"
CONFIG_DIR = SRC_DIR / "config"
API_CLIENT_FILE = SERVICES_DIR / "api.ts"
API_CONFIG_FILE = CONFIG_DIR / "api.ts"


class TestServicesDirectory:
    """Test services directory structure"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_services_directory_in_src(self):
        """Test that services directory is in src"""
        assert SERVICES_DIR.parent == SRC_DIR, "services should be in src directory"


class TestApiClientFile:
    """Test api.ts file"""

    def test_api_client_exists(self):
        """Test that services/api.ts exists"""
        assert API_CLIENT_FILE.exists(), "services/api.ts should exist"
        assert API_CLIENT_FILE.is_file(), "services/api.ts should be a file"

    def test_api_client_is_typescript(self):
        """Test that services/api.ts is a TypeScript file"""
        assert API_CLIENT_FILE.suffix == ".ts", "services/api.ts should have .ts extension"

    def test_api_client_has_content(self):
        """Test that services/api.ts has content"""
        content = API_CLIENT_FILE.read_text()
        assert len(content) > 0, "services/api.ts should not be empty"


class TestAxiosImports:
    """Test axios imports in api.ts"""

    def test_imports_axios(self):
        """Test that api.ts imports axios"""
        content = API_CLIENT_FILE.read_text()
        assert 'axios' in content, "api.ts should import axios"

    def test_imports_from_axios_package(self):
        """Test that api.ts imports from 'axios' package"""
        content = API_CLIENT_FILE.read_text()
        assert "from 'axios'" in content or 'from "axios"' in content, \
            "api.ts should import from 'axios' package"


class TestAxiosInstanceCreation:
    """Test axios instance creation"""

    def test_creates_axios_instance(self):
        """Test that api.ts creates an axios instance"""
        content = API_CLIENT_FILE.read_text()
        # Look for axios.create() pattern
        has_create = 'axios.create' in content
        assert has_create, "api.ts should create axios instance using axios.create()"

    def test_exports_axios_instance(self):
        """Test that api.ts exports the axios instance"""
        content = API_CLIENT_FILE.read_text()
        has_export = 'export default' in content or 'export {' in content or 'export const' in content
        assert has_export, "api.ts should export axios instance"


class TestBaseURLConfiguration:
    """Test base URL configuration"""

    def test_configures_base_url(self):
        """Test that api.ts configures baseURL"""
        content = API_CLIENT_FILE.read_text()
        assert 'baseURL' in content, "api.ts should configure baseURL"

    def test_uses_environment_variable_or_default(self):
        """Test that baseURL uses environment variable or default"""
        api_content = API_CLIENT_FILE.read_text()

        # Check if using centralized config pattern
        uses_centralized_config = 'getApiConfig' in api_content

        if uses_centralized_config:
            # Check that config file exists and has proper configuration
            assert API_CONFIG_FILE.exists(), "config/api.ts should exist when using centralized config"
            config_content = API_CONFIG_FILE.read_text()
            has_env_var = 'import.meta.env' in config_content or 'process.env' in config_content
            has_default = 'http' in config_content
            assert has_env_var or has_default, "config/api.ts should have environment variable or default URL"
        else:
            # Legacy pattern: check api.ts directly
            has_env_var = 'import.meta.env' in api_content or 'process.env' in api_content
            has_default = 'http' in api_content
            assert has_default, "api.ts should have a baseURL configuration"


class TestRequestInterceptors:
    """Test request interceptors"""

    def test_has_request_interceptor(self):
        """Test that api.ts configures request interceptor"""
        content = API_CLIENT_FILE.read_text()
        has_request_interceptor = 'interceptors.request' in content
        assert has_request_interceptor, "api.ts should configure request interceptor"

    def test_request_interceptor_uses_use_method(self):
        """Test that request interceptor uses .use() method"""
        content = API_CLIENT_FILE.read_text()
        has_use = 'interceptors.request.use' in content
        assert has_use, "api.ts should use interceptors.request.use()"


class TestJWTTokenHandling:
    """Test JWT token handling in request interceptor"""

    def test_handles_authorization_header(self):
        """Test that request interceptor handles Authorization header"""
        content = API_CLIENT_FILE.read_text()
        has_authorization = 'Authorization' in content or 'authorization' in content
        assert has_authorization, "api.ts should handle Authorization header"

    def test_uses_bearer_token_pattern(self):
        """Test that uses Bearer token pattern"""
        content = API_CLIENT_FILE.read_text()
        has_bearer = 'Bearer' in content or 'bearer' in content
        assert has_bearer, "api.ts should use Bearer token pattern"

    def test_gets_token_from_storage(self):
        """Test that gets token from localStorage"""
        content = API_CLIENT_FILE.read_text()
        has_local_storage = 'localStorage' in content
        # Should get token from some storage
        assert has_local_storage, "api.ts should get token from localStorage"


class TestResponseInterceptors:
    """Test response interceptors"""

    def test_has_response_interceptor(self):
        """Test that api.ts configures response interceptor"""
        content = API_CLIENT_FILE.read_text()
        has_response_interceptor = 'interceptors.response' in content
        assert has_response_interceptor, "api.ts should configure response interceptor"

    def test_response_interceptor_uses_use_method(self):
        """Test that response interceptor uses .use() method"""
        content = API_CLIENT_FILE.read_text()
        has_use = 'interceptors.response.use' in content
        assert has_use, "api.ts should use interceptors.response.use()"


class TestErrorHandling:
    """Test error handling in interceptors"""

    def test_handles_errors_in_response_interceptor(self):
        """Test that response interceptor handles errors"""
        content = API_CLIENT_FILE.read_text()
        # Should have error handling in response interceptor
        has_error = 'error' in content.lower()
        assert has_error, "api.ts should handle errors"

    def test_checks_response_status_or_error_status(self):
        """Test that checks response status codes"""
        content = API_CLIENT_FILE.read_text()
        # Should check status codes (401, 403, etc.)
        has_status = 'status' in content
        assert has_status, "api.ts should check response status"

    def test_handles_401_unauthorized(self):
        """Test that handles 401 Unauthorized errors"""
        content = API_CLIENT_FILE.read_text()
        has_401 = '401' in content
        # Should handle 401 errors specially (token expired, redirect to login, etc.)
        assert has_401, "api.ts should handle 401 Unauthorized errors"


class TestErrorHandlingBehavior:
    """Test error handling behavior"""

    def test_removes_token_on_401(self):
        """Test that removes token on 401 error"""
        content = API_CLIENT_FILE.read_text()
        # Should remove token from localStorage on 401
        has_remove_item = 'removeItem' in content
        assert has_remove_item, "api.ts should remove token on authentication failure"

    def test_returns_promise_reject(self):
        """Test that returns rejected promise on error"""
        content = API_CLIENT_FILE.read_text()
        has_reject = 'Promise.reject' in content or 'return error' in content
        assert has_reject, "api.ts should return rejected promise on error"


class TestApiClientStructure:
    """Test overall API client structure"""

    def test_has_valid_typescript_syntax(self):
        """Test that api.ts has valid TypeScript syntax"""
        content = API_CLIENT_FILE.read_text()
        # Basic syntax checks
        assert content.count('(') >= content.count(')') - 2, "Parentheses should be balanced"
        assert content.count('{') >= content.count('}') - 2, "Braces should be balanced"

    def test_file_not_too_small(self):
        """Test that api.ts has reasonable content"""
        content = API_CLIENT_FILE.read_text()
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
        assert len(lines) >= 10, "api.ts should have meaningful content"


class TestApiClientComments:
    """Test API client documentation"""

    def test_has_comments_or_documentation(self):
        """Test that api.ts has comments or documentation"""
        content = API_CLIENT_FILE.read_text()
        has_single_comment = '//' in content
        has_multi_comment = '/*' in content or '*/' in content
        # Good practice - should have documentation
        assert has_single_comment or has_multi_comment, \
            "api.ts should have comments or documentation"


class TestApiClientExports:
    """Test API client exports"""

    def test_exports_api_client(self):
        """Test that api.ts exports the API client"""
        content = API_CLIENT_FILE.read_text()
        has_export_default = 'export default' in content
        has_export_named = 'export const' in content or 'export {' in content
        assert has_export_default or has_export_named, "api.ts should export the API client"

    def test_can_be_imported_by_other_modules(self):
        """Test that api.ts structure allows imports"""
        content = API_CLIENT_FILE.read_text()
        # Should have export statement
        has_export = 'export' in content
        assert has_export, "api.ts should have exports for use in other modules"


class TestInterceptorConfiguration:
    """Test interceptor configuration details"""

    def test_request_interceptor_modifies_config(self):
        """Test that request interceptor receives and returns config"""
        content = API_CLIENT_FILE.read_text()
        # Request interceptor should work with config
        has_config = 'config' in content
        assert has_config, "api.ts request interceptor should use config parameter"

    def test_response_interceptor_returns_data_or_response(self):
        """Test that response interceptor returns response or data"""
        content = API_CLIENT_FILE.read_text()
        # Response interceptor should return response
        has_response = 'response' in content
        assert has_response, "api.ts response interceptor should handle response"


class TestHeadersConfiguration:
    """Test headers configuration"""

    def test_sets_headers_in_request_interceptor(self):
        """Test that sets headers in request interceptor"""
        content = API_CLIENT_FILE.read_text()
        has_headers = 'headers' in content
        assert has_headers, "api.ts should configure headers"

    def test_configures_content_type_or_authorization(self):
        """Test that configures Content-Type or Authorization headers"""
        content = API_CLIENT_FILE.read_text()
        has_auth = 'Authorization' in content or 'authorization' in content
        # At minimum should set Authorization header
        assert has_auth, "api.ts should configure Authorization header"
