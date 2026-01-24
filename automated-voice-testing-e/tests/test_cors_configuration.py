"""
Test suite for CORS configuration security.

Validates that CORS middleware is configured with explicit allowed methods
and headers rather than wildcards, and that origin validation is secure.
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


PROJECT_ROOT = Path(__file__).parent.parent
MAIN_FILE = PROJECT_ROOT / "backend" / "api" / "main.py"


class TestCORSFileExists:
    """Verify main.py exists with CORS configuration."""

    def test_main_file_exists(self):
        """main.py should exist."""
        assert MAIN_FILE.exists()


class TestCORSMethodsConfiguration:
    """Test that allow_methods uses explicit list."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_no_wildcard_methods(self, main_content):
        """CORS should not use wildcard for allow_methods."""
        # Look for the CORSMiddleware configuration
        assert 'allow_methods=["*"]' not in main_content, \
            "CORS allow_methods should not use wildcard"

    def test_explicit_methods_list(self, main_content):
        """CORS should use explicit methods list."""
        # Check for explicit HTTP methods
        has_get = '"GET"' in main_content or "'GET'" in main_content
        has_post = '"POST"' in main_content or "'POST'" in main_content
        has_put = '"PUT"' in main_content or "'PUT'" in main_content

        assert has_get and has_post and has_put, \
            "CORS should specify explicit HTTP methods (GET, POST, PUT, etc.)"


class TestCORSHeadersConfiguration:
    """Test that allow_headers uses explicit list."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_no_wildcard_headers(self, main_content):
        """CORS should not use wildcard for allow_headers."""
        assert 'allow_headers=["*"]' not in main_content, \
            "CORS allow_headers should not use wildcard"

    def test_explicit_headers_list(self, main_content):
        """CORS should use explicit headers list."""
        # Check for common required headers
        has_content_type = "Content-Type" in main_content
        has_authorization = "Authorization" in main_content

        assert has_content_type and has_authorization, \
            "CORS should specify explicit headers (Content-Type, Authorization, etc.)"


class TestCORSOriginValidation:
    """Test that origin validation is secure with credentials."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_no_wildcard_origin_with_credentials(self, main_content):
        """CORS should not allow wildcard origins with credentials enabled."""
        # If credentials are enabled, origins should not be wildcard
        has_credentials = "allow_credentials=True" in main_content
        has_wildcard_origins = 'allow_origins=["*"]' in main_content

        if has_credentials:
            assert not has_wildcard_origins, \
                "Cannot use wildcard origins with allow_credentials=True"

    def test_origins_are_from_config(self, main_content):
        """CORS origins should be loaded from configuration."""
        # Origins should be from ALLOWED_ORIGINS variable, not hardcoded
        assert "ALLOWED_ORIGINS" in main_content, \
            "CORS origins should be loaded from ALLOWED_ORIGINS configuration"


class TestCORSSecurityHeaders:
    """Test for additional security-related CORS headers."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_has_max_age_configuration(self, main_content):
        """CORS should have max_age configured for preflight caching."""
        # max_age helps reduce preflight requests
        has_max_age = "max_age" in main_content

        assert has_max_age, \
            "CORS should specify max_age for preflight caching"

    def test_expose_headers_configured(self, main_content):
        """CORS should configure expose_headers for response headers."""
        # expose_headers tells browser which headers to expose to JS
        has_expose = "expose_headers" in main_content

        assert has_expose, \
            "CORS should specify expose_headers for response header access"
