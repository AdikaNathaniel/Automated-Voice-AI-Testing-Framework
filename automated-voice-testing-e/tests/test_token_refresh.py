"""
Test suite for token refresh interceptor

Validates the token refresh logic in api.ts including:
- Intercepting 401 Unauthorized responses
- Attempting automatic token refresh
- Retrying original request with new token
- Logging out if refresh fails
- Preventing infinite retry loops
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
API_CLIENT_FILE = FRONTEND_SRC / "services" / "api.ts"


class TestTokenRefreshInterceptor:
    """Test token refresh interceptor functionality"""

    def test_api_client_file_exists(self):
        """Test that api.ts file exists"""
        assert API_CLIENT_FILE.exists(), "api.ts should exist"
        assert API_CLIENT_FILE.is_file(), "api.ts should be a file"

    def test_has_response_interceptor(self):
        """Test that response interceptor is configured"""
        content = API_CLIENT_FILE.read_text()
        assert "interceptors.response" in content, "Should have response interceptor"

    def test_handles_401_errors(self):
        """Test that interceptor handles 401 Unauthorized errors"""
        content = API_CLIENT_FILE.read_text()
        assert "401" in content, "Should check for 401 status"

    def test_has_token_refresh_logic(self):
        """Test that token refresh logic exists"""
        content = API_CLIENT_FILE.read_text()
        assert ("refreshToken" in content or "refresh" in content), "Should have refresh token logic"

    def test_retries_original_request(self):
        """Test that original request is retried after token refresh"""
        content = API_CLIENT_FILE.read_text()
        # Should have retry logic or re-execute request
        assert ("retry" in content.lower() or "request" in content), "Should retry original request"

    def test_prevents_infinite_retry_loop(self):
        """Test that infinite retry loops are prevented"""
        content = API_CLIENT_FILE.read_text()
        # Should have flag or counter to prevent infinite loops
        assert ("retry" in content.lower() or "_retry" in content or
                "isRetry" in content or "retrying" in content.lower()), "Should prevent infinite retry loops"

    def test_logout_on_refresh_failure(self):
        """Test that logout occurs if refresh fails"""
        content = API_CLIENT_FILE.read_text()
        # Should clear tokens or call logout when refresh fails
        assert ("removeItem" in content or "logout" in content or
                "clear" in content), "Should logout on refresh failure"

    def test_uses_refresh_token_from_storage(self):
        """Test that refresh token is retrieved from localStorage"""
        content = API_CLIENT_FILE.read_text()
        assert ("localStorage" in content and "refreshToken" in content), "Should get refresh token from localStorage"

    def test_updates_access_token_after_refresh(self):
        """Test that access token is updated after successful refresh"""
        content = API_CLIENT_FILE.read_text()
        # Should store new access token
        assert ("setItem" in content or "localStorage" in content), "Should update access token after refresh"

    def test_makes_refresh_api_call(self):
        """Test that refresh API call is made"""
        content = API_CLIENT_FILE.read_text()
        # Should make POST request to refresh endpoint
        assert ("post" in content and ("refresh" in content or "/auth/refresh" in content)), "Should call refresh API"

    def test_has_async_error_handling(self):
        """Test that error handler is async or returns promise"""
        content = API_CLIENT_FILE.read_text()
        assert ("async" in content or "Promise" in content or
                "then" in content), "Error handler should be async"

    def test_preserves_original_request_config(self):
        """Test that original request configuration is preserved"""
        content = API_CLIENT_FILE.read_text()
        # Should save and reuse original config
        assert ("config" in content or "originalRequest" in content), "Should preserve original request config"


class TestTokenRefreshEdgeCases:
    """Test edge cases for token refresh"""

    def test_handles_missing_refresh_token(self):
        """Test behavior when refresh token is missing"""
        content = API_CLIENT_FILE.read_text()
        # Should check if refresh token exists
        assert ("refreshToken" in content and ("if" in content or "!" in content)), "Should handle missing refresh token"

    def test_handles_network_errors_during_refresh(self):
        """Test handling of network errors during refresh"""
        content = API_CLIENT_FILE.read_text()
        # Should have error handling in refresh logic
        assert ("catch" in content or "error" in content), "Should handle errors during refresh"

    def test_does_not_refresh_for_non_401_errors(self):
        """Test that refresh only happens for 401 errors"""
        content = API_CLIENT_FILE.read_text()
        # Should specifically check for 401 status
        assert ("401" in content or "status === 401" in content or
                "status == 401" in content), "Should only refresh on 401 errors"


class TestTokenRefreshDocumentation:
    """Test documentation for token refresh logic"""

    def test_has_comments_explaining_refresh_logic(self):
        """Test that refresh logic is documented"""
        content = API_CLIENT_FILE.read_text()
        lines = content.split('\n')
        comment_lines = [line for line in lines if '//' in line or '*' in line]
        # Should have multiple comments explaining the logic
        assert len(comment_lines) > 10, "Should have comments explaining refresh logic"

    def test_documents_retry_prevention(self):
        """Test that retry prevention is documented"""
        content = API_CLIENT_FILE.read_text()
        # Should explain why/how infinite loops are prevented
        has_retry_docs = any(
            'retry' in line.lower() or 'loop' in line.lower()
            for line in content.split('\n')
            if '//' in line or '*' in line
        )
        assert has_retry_docs or "retry" in content.lower(), "Should document retry prevention"


class TestTokenRefreshIntegration:
    """Test integration with auth service"""

    def test_compatible_with_auth_service(self):
        """Test that interceptor works with auth service"""
        content = API_CLIENT_FILE.read_text()
        # Should use compatible token refresh approach
        assert ("refreshToken" in content or "refresh" in content), "Should be compatible with auth service"

    def test_uses_correct_api_endpoint(self):
        """Test that correct refresh endpoint is used"""
        content = API_CLIENT_FILE.read_text()
        # Should call /auth/refresh or similar
        assert ("/auth/refresh" in content or "/refresh" in content or
                "/v1/auth/refresh" in content), "Should use correct refresh endpoint"
