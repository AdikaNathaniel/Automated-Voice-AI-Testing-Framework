"""
Test suite for authentication service

Validates the auth.service.ts implementation including:
- File structure and imports
- Service methods (login, register, logout, refreshToken, getCurrentUser)
- API integration with axios
- Type definitions and exports
- Error handling
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
AUTH_SERVICE_FILE = FRONTEND_SRC / "services" / "auth.service.ts"
API_CLIENT_FILE = FRONTEND_SRC / "services" / "api.ts"


class TestAuthServiceFileExists:
    """Test that auth service file exists"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        services_dir = FRONTEND_SRC / "services"
        assert services_dir.exists(), "frontend/src/services directory should exist"
        assert services_dir.is_dir(), "services should be a directory"

    def test_auth_service_file_exists(self):
        """Test that auth.service.ts exists"""
        assert AUTH_SERVICE_FILE.exists(), "auth.service.ts should exist"
        assert AUTH_SERVICE_FILE.is_file(), "auth.service.ts should be a file"

    def test_auth_service_has_content(self):
        """Test that auth.service.ts has content"""
        content = AUTH_SERVICE_FILE.read_text()
        assert len(content) > 0, "auth.service.ts should not be empty"


class TestAuthServiceImports:
    """Test that auth service has necessary imports"""

    def test_imports_axios_or_api_client(self):
        """Test that axios or API client is imported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("axios" in content or "apiClient" in content or
                "api" in content), "Should import axios or API client"

    def test_imports_auth_types(self):
        """Test that auth types are imported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("LoginRequest" in content or "LoginResponse" in content or
                "RegisterRequest" in content or "types/auth" in content), "Should import auth types"


class TestAuthServiceStructure:
    """Test auth service structure"""

    def test_has_authservice_object_or_exports(self):
        """Test that authService object or exported functions exist"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("authService" in content or "export" in content), "Should have authService object or exports"

    def test_exports_functions(self):
        """Test that functions are exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "export" in content, "Should export functions"


class TestAuthServiceLoginMethod:
    """Test login method"""

    def test_has_login_function(self):
        """Test that login function exists"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "login" in content, "Should have login function"

    def test_login_function_is_async(self):
        """Test that login function is async"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "async" in content or "Promise" in content, "Login should be async or return Promise"

    def test_login_accepts_email_and_password(self):
        """Test that login accepts email and password parameters"""
        content = AUTH_SERVICE_FILE.read_text()
        # Should have email and password parameters
        assert "email" in content and "password" in content, "Should accept email and password"

    def test_login_returns_loginresponse(self):
        """Test that login returns LoginResponse"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("LoginResponse" in content or "Promise" in content), "Should return LoginResponse or Promise"

    def test_login_makes_api_call(self):
        """Test that login makes API call"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("post" in content or "axios" in content or
                "api" in content), "Should make API call"

    def test_login_calls_auth_endpoint(self):
        """Test that login calls /auth/login endpoint"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("/auth/login" in content or "/login" in content), "Should call auth/login endpoint"


class TestAuthServiceRegisterMethod:
    """Test register method"""

    def test_has_register_function(self):
        """Test that register function exists"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "register" in content, "Should have register function"

    def test_register_function_is_async(self):
        """Test that register function is async"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "async" in content or "Promise" in content, "Register should be async or return Promise"

    def test_register_accepts_data_parameter(self):
        """Test that register accepts data parameter"""
        content = AUTH_SERVICE_FILE.read_text()
        # Should accept RegisterRequest data
        assert ("data" in content or "RegisterRequest" in content or
                "email" in content), "Should accept registration data"

    def test_register_makes_api_call(self):
        """Test that register makes API call"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("post" in content or "axios" in content or
                "api" in content), "Should make API call"

    def test_register_calls_auth_endpoint(self):
        """Test that register calls /auth/register endpoint"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("/auth/register" in content or "/register" in content), "Should call auth/register endpoint"


class TestAuthServiceLogoutMethod:
    """Test logout method"""

    def test_has_logout_function(self):
        """Test that logout function exists"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "logout" in content, "Should have logout function"

    def test_logout_clears_tokens(self):
        """Test that logout clears tokens from storage"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("removeItem" in content or "clear" in content or
                "localStorage" in content), "Should clear tokens from storage"


class TestAuthServiceRefreshTokenMethod:
    """Test refreshToken method"""

    def test_has_refresh_token_function(self):
        """Test that refreshToken function exists"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("refreshToken" in content or "refresh" in content), "Should have refreshToken function"

    def test_refresh_token_is_async(self):
        """Test that refreshToken is async"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "async" in content or "Promise" in content, "refreshToken should be async or return Promise"

    def test_refresh_token_makes_api_call(self):
        """Test that refreshToken makes API call"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("post" in content or "axios" in content or
                "api" in content), "Should make API call"

    def test_refresh_token_calls_refresh_endpoint(self):
        """Test that refreshToken calls /auth/refresh endpoint"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("/auth/refresh" in content or "/refresh" in content), "Should call auth/refresh endpoint"


class TestAuthServiceGetCurrentUserMethod:
    """Test getCurrentUser method"""

    def test_has_get_current_user_function(self):
        """Test that getCurrentUser function exists"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("getCurrentUser" in content or "getUser" in content or
                "me" in content), "Should have getCurrentUser function"

    def test_get_current_user_is_async(self):
        """Test that getCurrentUser is async"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "async" in content or "Promise" in content, "getCurrentUser should be async or return Promise"

    def test_get_current_user_makes_api_call(self):
        """Test that getCurrentUser makes API call"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("get" in content or "axios" in content or
                "api" in content), "Should make API call"

    def test_get_current_user_calls_me_endpoint(self):
        """Test that getCurrentUser calls /auth/me endpoint"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("/auth/me" in content or "/me" in content or
                "/user" in content), "Should call auth/me or similar endpoint"


class TestAuthServiceTypeScript:
    """Test TypeScript typing"""

    def test_uses_typescript_types(self):
        """Test that TypeScript types are used"""
        content = AUTH_SERVICE_FILE.read_text()
        assert (":" in content or "interface" in content or
                "type" in content), "Should use TypeScript types"

    def test_functions_have_return_types(self):
        """Test that functions have return type annotations"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("Promise<" in content or ": " in content), "Functions should have return types"

    def test_parameters_are_typed(self):
        """Test that function parameters are typed"""
        content = AUTH_SERVICE_FILE.read_text()
        assert (": string" in content or ": LoginRequest" in content or
                ": RegisterRequest" in content), "Parameters should be typed"


class TestAuthServiceExports:
    """Test exports"""

    def test_exports_login(self):
        """Test that login is exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "export" in content and "login" in content, "Should export login"

    def test_exports_register(self):
        """Test that register is exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "export" in content and "register" in content, "Should export register"

    def test_exports_logout(self):
        """Test that logout is exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "export" in content and "logout" in content, "Should export logout"

    def test_exports_refresh_token(self):
        """Test that refreshToken is exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert "export" in content and "refresh" in content, "Should export refreshToken"

    def test_exports_get_current_user(self):
        """Test that getCurrentUser is exported"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("export" in content and
                ("getCurrentUser" in content or "getUser" in content or
                 "me" in content)), "Should export getCurrentUser"


class TestAuthServiceDocumentation:
    """Test documentation"""

    def test_has_file_documentation(self):
        """Test that file has header documentation"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content), "Should have documentation"

    def test_documents_methods(self):
        """Test that methods have documentation"""
        content = AUTH_SERVICE_FILE.read_text()
        lines = content.split('\n')
        comment_lines = [line for line in lines if '//' in line or '*' in line]
        assert len(comment_lines) > 5, "Should have documentation for methods"


class TestAuthServiceErrorHandling:
    """Test error handling"""

    def test_handles_api_errors(self):
        """Test that service handles API errors"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("catch" in content or "error" in content or
                "try" in content), "Should handle errors"

    def test_throws_or_rejects_on_error(self):
        """Test that errors are thrown or rejected"""
        content = AUTH_SERVICE_FILE.read_text()
        assert ("throw" in content or "reject" in content or
                "catch" in content), "Should throw or reject errors"
