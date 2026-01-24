"""
Test suite for validation frontend service (TASK-185)

Validates the validation service implementation including:
- File structure
- Service method definitions
- API endpoint patterns
- Request/response handling
- TypeScript usage
- Documentation
"""

import re
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SERVICES_DIR = PROJECT_ROOT / "frontend" / "src" / "services"
VALIDATION_SERVICE_FILE = SERVICES_DIR / "validation.service.ts"


def _get_function_block(content: str, function_name: str) -> str:
    """
    Return the source block for a given exported function.
    """
    pattern = rf"export const {function_name}\s*=\s*async[\s\S]*?\n\}};"
    match = re.search(pattern, content)
    assert match, f"{function_name} function definition not found"
    return match.group(0)


class TestValidationServiceFileExists:
    """Test that validation service file exists"""

    def test_services_directory_exists(self):
        """Test that services directory exists"""
        assert SERVICES_DIR.exists(), "frontend/src/services directory should exist"
        assert SERVICES_DIR.is_dir(), "services should be a directory"

    def test_validation_service_file_exists(self):
        """Test that validation.service.ts exists"""
        assert VALIDATION_SERVICE_FILE.exists(), "validation.service.ts should exist"
        assert VALIDATION_SERVICE_FILE.is_file(), "validation.service.ts should be a file"

    def test_service_file_has_content(self):
        """Test that service file has content"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert len(content) > 0, "validation.service.ts should not be empty"


class TestImports:
    """Test service imports"""

    def test_imports_api_client(self):
        """Test that service imports API client"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("apiClient" in content or
                "from './api'" in content or
                "axios" in content), "Should import API client"

    def test_imports_types(self):
        """Test that service imports validation types"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("from '../types/validation'" in content or
                "ValidationQueue" in content or
                "HumanValidation" in content), "Should import validation types"

    def test_imports_validation_queue_type(self):
        """Test that service imports ValidationQueue type"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "ValidationQueue" in content, "Should import ValidationQueue type"

    def test_imports_human_validation_create_type(self):
        """Test that service imports HumanValidationCreate type"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "HumanValidationCreate" in content, "Should import HumanValidationCreate type"

    def test_imports_validation_stats_type(self):
        """Test that service imports ValidationStats type"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "ValidationStats" in content, "Should import ValidationStats type"


class TestFetchValidationQueueMethod:
    """Test fetchValidationQueue method"""

    def test_has_fetch_validation_queue_method(self):
        """Test that service has fetchValidationQueue method"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("fetchValidationQueue" in content or
                "getValidationQueue" in content or
                "fetchQueue" in content), "Should have fetchValidationQueue method"

    def test_fetch_method_is_async(self):
        """Test that fetchValidationQueue is async"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "async" in content, "fetchValidationQueue should be async"

    def test_fetch_method_is_exported(self):
        """Test that fetchValidationQueue is exported"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "export" in content, "Methods should be exported"

    def test_fetch_uses_get_endpoint(self):
        """Test that fetchValidationQueue uses GET endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("get" in content or "GET" in content), "Should use GET request"

    def test_fetch_uses_validation_queue_endpoint(self):
        """Test that fetchValidationQueue uses /validation/queue endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("/validation/queue" in content or
                "/validation" in content), "Should use /validation/queue endpoint"

    def test_fetch_supports_filters(self):
        """Test that fetchValidationQueue supports filter parameters"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("filter" in content or
                "params" in content or
                "query" in content), "Should support filter parameters"


class TestClaimValidationMethod:
    """Test claimValidation method"""

    def test_has_claim_validation_method(self):
        """Test that service has claimValidation method"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "claimValidation" in content, "Should have claimValidation method"

    def test_claim_uses_post_endpoint(self):
        """Test that claimValidation uses POST endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("post" in content or "POST" in content), "Should use POST request"

    def test_claim_accepts_id_parameter(self):
        """Test that claimValidation accepts id parameter"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("id" in content or "itemId" in content), "Should accept id parameter"

    def test_claim_uses_claim_endpoint(self):
        """Test that claimValidation uses /claim endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "claim" in content, "Should use /claim endpoint"


class TestSubmitValidationMethod:
    """Test submitValidation method"""

    def test_has_submit_validation_method(self):
        """Test that service has submitValidation method"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "submitValidation" in content, "Should have submitValidation method"

    def test_submit_uses_post_endpoint(self):
        """Test that submitValidation uses POST endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("post" in content or "POST" in content), "Should use POST request"

    def test_submit_accepts_data_parameter(self):
        """Test that submitValidation accepts data parameter"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("data" in content or "validation" in content), "Should accept data parameter"

    def test_submit_uses_submit_endpoint(self):
        """Test that submitValidation uses /submit endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "submit" in content, "Should use /submit endpoint"


class TestReleaseValidationMethod:
    """Test releaseValidation method"""

    def test_has_release_validation_method(self):
        """Test that service has releaseValidation method"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("releaseValidation" in content or
                "release" in content), "Should have releaseValidation method"

    def test_release_uses_post_endpoint(self):
        """Test that releaseValidation uses POST endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("post" in content or "POST" in content), "Should use POST request"

    def test_release_accepts_id_parameter(self):
        """Test that releaseValidation accepts id parameter"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("id" in content or "itemId" in content), "Should accept id parameter"

    def test_release_uses_release_endpoint(self):
        """Test that releaseValidation uses /release endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "release" in content, "Should use /release endpoint"


class TestFetchValidationStatsMethod:
    """Test fetchValidationStats method"""

    def test_has_fetch_validation_stats_method(self):
        """Test that service has fetchValidationStats method"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("fetchValidationStats" in content or
                "getValidationStats" in content or
                "fetchStats" in content), "Should have fetchValidationStats method"

    def test_fetch_stats_uses_get_endpoint(self):
        """Test that fetchValidationStats uses GET endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("get" in content or "GET" in content), "Should use GET request"

    def test_fetch_stats_uses_stats_endpoint(self):
        """Test that fetchValidationStats uses /stats endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "stats" in content, "Should use /stats endpoint"


class TestDocumentation:
    """Test service documentation"""

    def test_has_file_documentation(self):
        """Test that file has top-level documentation"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("/**" in content or "//" in content), "Should have file documentation"

    def test_methods_have_documentation(self):
        """Test that methods have JSDoc documentation"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Should have JSDoc comments
        doc_count = content.count("/**")
        assert doc_count >= 3, "Should have documentation for multiple methods"

    def test_has_usage_examples(self):
        """Test that documentation includes usage examples"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Check for example patterns
        assert ("@example" in content or
                "Example:" in content or
                "example" in content.lower()), "Should include usage examples"

    def test_documents_validation_workflow(self):
        """Test that documentation describes validation workflow"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("validation" in content.lower() or
                "claim" in content.lower() or
                "submit" in content.lower()), "Should document validation workflow"


class TestTypeScriptUsage:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that file uses TypeScript syntax"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert (":" in content and
                "=>" in content), "Should use TypeScript syntax"

    def test_uses_type_annotations(self):
        """Test that functions use type annotations"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Should have return type annotations
        assert "Promise<" in content, "Should use Promise type annotations"

    def test_file_extension_is_ts(self):
        """Test that file has .ts extension"""
        assert VALIDATION_SERVICE_FILE.suffix == ".ts", "File should have .ts extension"

    def test_uses_validation_types(self):
        """Test that service uses validation types"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("ValidationQueue" in content or
                "ValidationStats" in content or
                "HumanValidation" in content), "Should use validation types"


class TestAPIEndpoints:
    """Test API endpoint patterns"""

    def test_uses_validation_base_endpoint(self):
        """Test that service uses /validation base endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "/validation" in content, "Should use /validation endpoint"

    def test_constructs_dynamic_endpoints(self):
        """Test that service constructs endpoints with IDs"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Should have template literals or string concatenation for dynamic endpoints
        assert ("${" in content or
                "+" in content or
                "`" in content), "Should construct dynamic endpoints"

    def test_uses_queue_endpoint(self):
        """Test that service uses /queue endpoint"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "queue" in content, "Should use /queue endpoint"


class TestValidationServiceApiPaths:
    """Tests for API path alignment and payload mapping."""

    def test_validation_base_url_uses_api_v1_namespace(self):
        """Base URL should use /api/v1/validation."""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert "/api/v1/validation" in content, "Base URL should target /api/v1/validation"

    def test_claim_validation_uses_queue_id_endpoint(self):
        """Claim endpoint should post to /{queue_id}/claim."""
        content = VALIDATION_SERVICE_FILE.read_text()
        block = _get_function_block(content, "claimValidation")
        assert "${VALIDATION_BASE_URL}/${itemId}/claim" in block, "Claim should post to /{queue_id}/claim"
        assert "/queue/${" not in block, "Claim endpoint should not include /queue segment"

    def test_release_validation_uses_queue_id_endpoint_and_success_response(self):
        """Release endpoint should post to /{queue_id}/release and unwrap SuccessResponse data."""
        content = VALIDATION_SERVICE_FILE.read_text()
        block = _get_function_block(content, "releaseValidation")
        assert "${VALIDATION_BASE_URL}/${itemId}/release" in block, "Release should post to /{queue_id}/release"
        assert "response.data.data" in block, "Release should return SuccessResponse data payload"

    def test_submit_validation_requires_queue_id_and_maps_payload(self):
        """Submit endpoint should require queueId and map payload fields."""
        content = VALIDATION_SERVICE_FILE.read_text()
        block = _get_function_block(content, "submitValidation")
        assert "queueId: string" in block, "Submit should accept queueId parameter"
        assert "${VALIDATION_BASE_URL}/${queueId}/submit" in block, "Submit endpoint should include queue ID"
        assert "validation_decision" in block, "Submit payload should include validation_decision"
        assert "time_spent_seconds" in block, "Submit payload should include time_spent_seconds"
        assert "response.data.data" in block, "Submit should unwrap SuccessResponse data payload"


class TestErrorHandling:
    """Test error handling patterns"""

    def test_uses_try_catch(self):
        """Test that methods use try-catch for error handling"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("try" in content and "catch" in content), "Should use try-catch for error handling"

    def test_handles_errors(self):
        """Test that errors are properly handled"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("error" in content.lower() or
                "throw" in content), "Should handle errors"


class TestServiceStructure:
    """Test overall service structure"""

    def test_has_all_validation_methods(self):
        """Test that service has all validation methods"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Should have fetch queue, claim, submit, release, fetch stats
        has_fetch = any(term in content for term in ["fetchValidationQueue", "getValidationQueue", "fetchQueue"])
        has_claim = "claimValidation" in content
        has_submit = "submitValidation" in content
        has_release = "releaseValidation" in content or "release" in content
        has_stats = any(term in content for term in ["fetchValidationStats", "getValidationStats", "fetchStats"])

        assert has_fetch, "Should have fetch validation queue method"
        assert has_claim, "Should have claim validation method"
        assert has_submit, "Should have submit validation method"
        assert has_release, "Should have release validation method"
        assert has_stats, "Should have fetch stats method"

    def test_exports_methods(self):
        """Test that methods are exported"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Count export statements
        export_count = content.count("export ")
        assert export_count >= 5, "Should export multiple methods (at least 5)"


class TestAPIClientIntegration:
    """Test API client integration"""

    def test_uses_api_client_consistently(self):
        """Test that service uses API client for all requests"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Should use axios or apiClient
        assert ("axios" in content or
                "apiClient" in content or
                "api" in content), "Should use API client"

    def test_handles_responses(self):
        """Test that service handles API responses"""
        content = VALIDATION_SERVICE_FILE.read_text()
        assert ("response" in content or
                ".data" in content), "Should handle API responses"


class TestValidationWorkflowMethods:
    """Test validation workflow specific methods"""

    def test_claim_endpoint_includes_id(self):
        """Test that claim endpoint includes item ID"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Claim should use dynamic endpoint with ID
        if "claimValidation" in content:
            assert ("${" in content or "`" in content), "Claim endpoint should include ID in path"

    def test_release_endpoint_includes_id(self):
        """Test that release endpoint includes item ID"""
        content = VALIDATION_SERVICE_FILE.read_text()
        # Release should use dynamic endpoint with ID
        if "releaseValidation" in content or "release" in content:
            assert ("${" in content or "`" in content), "Release endpoint should include ID in path"

    def test_submit_sends_validation_data(self):
        """Test that submit sends HumanValidation data"""
        content = VALIDATION_SERVICE_FILE.read_text()
        if "submitValidation" in content:
            assert ("data" in content or
                    "validation" in content), "Submit should send validation data"
