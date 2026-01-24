"""
Test API Integration Guide Documentation

This module tests that the API integration guide provides comprehensive
instructions for integrating with the Voice AI Testing API.

Test Coverage:
    - File existence and structure
    - Required sections present
    - Authentication documentation
    - Endpoints documentation
    - Request/response examples
    - Code examples in multiple languages
    - Error handling documentation
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest


# =============================================================================
# File Structure Tests
# =============================================================================

class TestAPIGuideFileStructure:
    """Test API guide file structure"""

    def test_api_guide_file_exists(self):
        """Test that api-guide.md file exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"

        # Act & Assert
        assert api_guide_file.exists(), "api-guide.md should exist in docs/"
        assert api_guide_file.is_file(), "api-guide.md should be a file"

    def test_api_guide_has_content(self):
        """Test that api-guide.md has substantial content"""
        # Arrange
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"

        # Act
        content = api_guide_file.read_text()

        # Assert
        assert len(content) > 2000, \
            "API guide should have substantial content (>2000 chars)"

    def test_api_guide_is_markdown(self):
        """Test that API guide uses markdown formatting"""
        # Arrange
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"

        # Act
        content = api_guide_file.read_text()

        # Assert
        assert "# " in content or "## " in content, \
            "API guide should have markdown headers"


# =============================================================================
# Required Sections Tests
# =============================================================================

class TestAPIGuideRequiredSections:
    """Test that API guide has all required sections"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_has_title(self, content):
        """Test that API guide has a title"""
        # Assert
        assert "# " in content, "API guide should have a main title"

    def test_has_authentication_section(self, content):
        """Test that API guide has authentication section"""
        # Assert
        content_lower = content.lower()
        assert "authentication" in content_lower or "auth" in content_lower, \
            "API guide should have authentication section"

    def test_has_endpoints_section(self, content):
        """Test that API guide has endpoints section"""
        # Assert
        content_lower = content.lower()
        assert "endpoint" in content_lower, \
            "API guide should have endpoints section"

    def test_has_examples_section(self, content):
        """Test that API guide has examples section"""
        # Assert
        content_lower = content.lower()
        assert "example" in content_lower, \
            "API guide should have examples section"

    def test_has_error_handling_section(self, content):
        """Test that API guide has error handling section"""
        # Assert
        content_lower = content.lower()
        assert "error" in content_lower, \
            "API guide should have error handling section"

    def test_has_getting_started_section(self, content):
        """Test that API guide has getting started section"""
        # Assert
        content_lower = content.lower()
        assert "getting started" in content_lower or "quick start" in content_lower, \
            "API guide should have getting started section"


# =============================================================================
# Authentication Documentation Tests
# =============================================================================

class TestAPIGuideAuthentication:
    """Test that API guide documents authentication"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_documents_jwt_authentication(self, content):
        """Test that API guide mentions JWT authentication"""
        # Assert
        content_lower = content.lower()
        assert "jwt" in content_lower or "token" in content_lower, \
            "API guide should mention JWT or token authentication"

    def test_documents_registration(self, content):
        """Test that API guide documents user registration"""
        # Assert
        content_lower = content.lower()
        assert "register" in content_lower or "signup" in content_lower, \
            "API guide should document user registration"

    def test_documents_login(self, content):
        """Test that API guide documents login"""
        # Assert
        content_lower = content.lower()
        assert "login" in content_lower or "sign in" in content_lower, \
            "API guide should document login process"

    def test_documents_token_usage(self, content):
        """Test that API guide documents how to use tokens"""
        # Assert
        content_lower = content.lower()
        assert "bearer" in content_lower or "authorization" in content_lower, \
            "API guide should document how to use authentication tokens"

    def test_documents_token_refresh(self, content):
        """Test that API guide documents token refresh"""
        # Assert
        content_lower = content.lower()
        assert "refresh" in content_lower, \
            "API guide should document token refresh"


# =============================================================================
# Endpoints Documentation Tests
# =============================================================================

class TestAPIGuideEndpoints:
    """Test that API guide documents key endpoints"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_documents_base_url(self, content):
        """Test that API guide documents base URL"""
        # Assert
        content_lower = content.lower()
        assert "base url" in content_lower or "baseurl" in content_lower or "http" in content_lower, \
            "API guide should document base URL"

    def test_documents_http_methods(self, content):
        """Test that API guide documents HTTP methods"""
        # Assert
        content_upper = content.upper()
        # Should mention at least GET and POST
        assert "GET" in content_upper and "POST" in content_upper, \
            "API guide should document HTTP methods (GET, POST)"

    def test_documents_test_case_endpoints(self, content):
        """Test that API guide documents test case endpoints"""
        # Assert
        content_lower = content.lower()
        assert "test case" in content_lower or "test-case" in content_lower, \
            "API guide should document test case endpoints"

    def test_documents_test_run_endpoints(self, content):
        """Test that API guide documents test run endpoints"""
        # Assert
        content_lower = content.lower()
        assert "test run" in content_lower or "test-run" in content_lower, \
            "API guide should document test run endpoints"

    def test_documents_test_suite_endpoints(self, content):
        """Test that API guide documents test suite endpoints"""
        # Assert
        content_lower = content.lower()
        assert "test suite" in content_lower or "test-suite" in content_lower, \
            "API guide should document test suite endpoints"


# =============================================================================
# Code Examples Tests
# =============================================================================

class TestAPIGuideCodeExamples:
    """Test that API guide includes code examples"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_has_code_blocks(self, content):
        """Test that API guide has code blocks"""
        # Assert
        assert "```" in content, \
            "API guide should have code blocks (markdown ```)"

    def test_has_curl_examples(self, content):
        """Test that API guide has cURL examples"""
        # Assert
        content_lower = content.lower()
        assert "curl" in content_lower, \
            "API guide should have cURL examples"

    def test_has_json_examples(self, content):
        """Test that API guide has JSON examples"""
        # Assert
        assert "```json" in content.lower(), \
            "API guide should have JSON code blocks"

    def test_has_multiple_code_examples(self, content):
        """Test that API guide has multiple code examples"""
        # Assert
        code_block_count = content.count("```")
        assert code_block_count >= 20, \
            f"API guide should have at least 10 code blocks (pairs), got {code_block_count // 2}"

    def test_has_request_examples(self, content):
        """Test that API guide has request examples"""
        # Assert
        content_lower = content.lower()
        assert "request" in content_lower, \
            "API guide should have request examples"

    def test_has_response_examples(self, content):
        """Test that API guide has response examples"""
        # Assert
        content_lower = content.lower()
        assert "response" in content_lower, \
            "API guide should have response examples"


# =============================================================================
# Request/Response Documentation Tests
# =============================================================================

class TestAPIGuideRequestResponse:
    """Test that API guide documents requests and responses"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_documents_request_headers(self, content):
        """Test that API guide documents request headers"""
        # Assert
        content_lower = content.lower()
        assert "header" in content_lower or "content-type" in content_lower, \
            "API guide should document request headers"

    def test_documents_request_body(self, content):
        """Test that API guide documents request body"""
        # Assert
        content_lower = content.lower()
        assert "body" in content_lower or "payload" in content_lower, \
            "API guide should document request body"

    def test_documents_response_format(self, content):
        """Test that API guide documents response format"""
        # Assert
        content_lower = content.lower()
        # Should mention success or data structure
        assert "success" in content_lower or "data" in content_lower, \
            "API guide should document response format"

    def test_documents_status_codes(self, content):
        """Test that API guide documents HTTP status codes"""
        # Assert
        # Should mention common status codes
        has_200 = "200" in content
        has_201 = "201" in content
        has_400 = "400" in content
        has_401 = "401" in content
        has_404 = "404" in content

        assert has_200 or has_201 or has_400 or has_401 or has_404, \
            "API guide should document HTTP status codes"


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestAPIGuideErrorHandling:
    """Test that API guide documents error handling"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_documents_error_responses(self, content):
        """Test that API guide documents error responses"""
        # Assert
        content_lower = content.lower()
        assert "error" in content_lower, \
            "API guide should document error responses"

    def test_documents_error_codes(self, content):
        """Test that API guide documents error codes"""
        # Assert
        content_lower = content.lower()
        # Should mention error codes or error handling
        assert "error code" in content_lower or "error_code" in content_lower or "code" in content_lower, \
            "API guide should document error codes"

    def test_documents_validation_errors(self, content):
        """Test that API guide documents validation errors"""
        # Assert
        content_lower = content.lower()
        assert "validation" in content_lower or "invalid" in content_lower, \
            "API guide should document validation errors"


# =============================================================================
# Best Practices Tests
# =============================================================================

class TestAPIGuideBestPractices:
    """Test that API guide follows documentation best practices"""

    @pytest.fixture
    def content(self):
        """Load API guide content"""
        project_root = Path(__file__).parent.parent
        api_guide_file = project_root / "docs" / "api-guide.md"
        return api_guide_file.read_text()

    def test_has_table_of_contents(self, content):
        """Test that API guide has table of contents"""
        # Assert
        content_lower = content.lower()
        has_toc = "table of contents" in content_lower or "## " in content
        assert has_toc, \
            "API guide should have table of contents or clear section organization"

    def test_uses_consistent_formatting(self, content):
        """Test that API guide uses consistent markdown formatting"""
        # Assert
        has_headers = "## " in content
        has_code_blocks = "```" in content
        has_lists = "\n- " in content or "\n* " in content

        assert has_headers and has_code_blocks and has_lists, \
            "API guide should use consistent markdown formatting"

    def test_has_practical_examples(self, content):
        """Test that API guide has practical, complete examples"""
        # Assert
        # Should have multiple complete examples (endpoints with full request/response)
        curl_count = content.lower().count("curl")
        assert curl_count >= 3, \
            f"API guide should have multiple practical cURL examples, got {curl_count}"

    def test_documents_api_version(self, content):
        """Test that API guide documents API version"""
        # Assert
        content_lower = content.lower()
        assert "version" in content_lower or "/api" in content_lower or "v1" in content_lower, \
            "API guide should document API version or base path"
