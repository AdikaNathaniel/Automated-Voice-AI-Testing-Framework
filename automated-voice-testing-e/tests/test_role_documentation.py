"""
Test suite for role requirements documentation.

Validates that role requirements for API endpoints are properly documented.
"""

import pytest
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent
AUTH_DIR = PROJECT_ROOT / "backend" / "api" / "auth"
ROLES_FILE = AUTH_DIR / "roles.py"


class TestRoleDocumentationExists:
    """Verify role documentation exists in the codebase."""

    @pytest.fixture
    def roles_content(self):
        return ROLES_FILE.read_text()

    def test_roles_file_exists(self):
        """roles.py should exist in auth module."""
        assert ROLES_FILE.exists()

    def test_endpoint_role_requirements_documented(self, roles_content):
        """Endpoint role requirements should be documented."""
        assert "ENDPOINT_ROLE_REQUIREMENTS" in roles_content or \
               "Endpoint Role Requirements" in roles_content

    def test_documents_test_runs_endpoints(self, roles_content):
        """Should document test_runs endpoint roles."""
        assert "test_runs" in roles_content.lower() or "test-runs" in roles_content.lower()

    def test_documents_test_cases_endpoints(self, roles_content):
        """Should document test_cases endpoint roles."""
        assert "test_cases" in roles_content.lower() or "test-cases" in roles_content.lower()

    def test_documents_test_suites_endpoints(self, roles_content):
        """Should document test_suites endpoint roles."""
        assert "test_suites" in roles_content.lower() or "test-suites" in roles_content.lower()

    def test_documents_defects_endpoints(self, roles_content):
        """Should document defects endpoint roles."""
        assert "defects" in roles_content.lower()

    def test_documents_admin_role_capabilities(self, roles_content):
        """Should document what admin role can do."""
        assert "admin" in roles_content.lower()

    def test_documents_qa_lead_role_capabilities(self, roles_content):
        """Should document what qa_lead role can do."""
        assert "qa_lead" in roles_content.lower()

    def test_documents_viewer_role_capabilities(self, roles_content):
        """Should document what viewer role can do."""
        assert "viewer" in roles_content.lower()
