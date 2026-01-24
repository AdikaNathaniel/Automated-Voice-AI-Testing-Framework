"""
Tests for API documentation security (Phase 5.1 API Documentation).
"""

import os
import pytest


@pytest.fixture
def main_py_path():
    """Get path to main.py."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(project_root, "backend", "api", "main.py")


@pytest.fixture
def main_py_content(main_py_path):
    """Read main.py content."""
    with open(main_py_path) as f:
        return f.read()


class TestDocsDisabledInProduction:
    """Test that API docs are disabled in production."""

    def test_docs_url_conditional(self, main_py_content):
        """Test that docs_url is conditionally disabled."""
        # Should have conditional docs_url based on environment
        has_conditional = (
            "docs_url=None" in main_py_content or
            "docs_url=" in main_py_content and "production" in main_py_content.lower()
        )
        assert has_conditional, \
            "FastAPI app should conditionally disable docs_url in production"

    def test_redoc_url_conditional(self, main_py_content):
        """Test that redoc_url is conditionally disabled."""
        has_conditional = (
            "redoc_url=None" in main_py_content or
            "redoc_url=" in main_py_content and "production" in main_py_content.lower()
        )
        assert has_conditional, \
            "FastAPI app should conditionally disable redoc_url in production"

    def test_openapi_url_conditional(self, main_py_content):
        """Test that openapi_url is conditionally disabled."""
        has_conditional = (
            "openapi_url=None" in main_py_content or
            "openapi_url=" in main_py_content and "production" in main_py_content.lower()
        )
        assert has_conditional, \
            "FastAPI app should conditionally disable openapi_url in production"

    def test_environment_check_exists(self, main_py_content):
        """Test that environment check exists for docs."""
        # Should check ENVIRONMENT variable
        has_env_check = (
            "ENVIRONMENT" in main_py_content or
            "settings.ENVIRONMENT" in main_py_content or
            "get_settings()" in main_py_content
        )
        assert has_env_check, \
            "main.py should check environment for documentation visibility"
