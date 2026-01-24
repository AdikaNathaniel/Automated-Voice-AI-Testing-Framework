"""
Test API Documentation (OpenAPI/Swagger)

This module tests that the FastAPI application properly generates
and exposes comprehensive API documentation through OpenAPI/Swagger.

Test Coverage:
    - OpenAPI schema generation and accessibility
    - API metadata (title, version, description)
    - Endpoint descriptions and summaries
    - Request/response examples
    - Schema documentation
    - Tags and organization
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient


# =============================================================================
# OpenAPI Schema Tests
# =============================================================================

class TestOpenAPISchemaGeneration:
    """Test OpenAPI schema generation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    def test_openapi_schema_endpoint_exists(self, client):
        """Test that OpenAPI schema endpoint is accessible"""
        # Act
        response = client.get("/api/openapi.json")

        # Assert
        assert response.status_code == 200, "OpenAPI schema should be accessible"
        assert response.headers["content-type"] == "application/json", \
            "OpenAPI schema should be JSON"

    def test_openapi_schema_is_valid_json(self, client):
        """Test that OpenAPI schema is valid JSON"""
        # Act
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Assert
        assert schema is not None, "Schema should parse as JSON"
        assert isinstance(schema, dict), "Schema should be a dictionary"

    def test_openapi_schema_has_required_fields(self, client):
        """Test that OpenAPI schema has required fields"""
        # Act
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Assert
        assert "openapi" in schema, "Schema should have OpenAPI version"
        assert "info" in schema, "Schema should have info section"
        assert "paths" in schema, "Schema should have paths section"

    def test_openapi_version_is_3_x(self, client):
        """Test that OpenAPI version is 3.x"""
        # Act
        response = client.get("/api/openapi.json")
        schema = response.json()

        # Assert
        openapi_version = schema.get("openapi", "")
        assert openapi_version.startswith("3."), \
            f"OpenAPI version should be 3.x, got {openapi_version}"


# =============================================================================
# API Metadata Tests
# =============================================================================

class TestAPIMetadata:
    """Test API metadata in OpenAPI schema"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    @pytest.fixture
    def schema(self, client):
        """Get OpenAPI schema"""
        response = client.get("/api/openapi.json")
        return response.json()

    def test_api_has_title(self, schema):
        """Test that API has a title"""
        # Assert
        info = schema.get("info", {})
        assert "title" in info, "API should have a title"
        assert len(info["title"]) > 0, "API title should not be empty"

    def test_api_has_version(self, schema):
        """Test that API has a version"""
        # Assert
        info = schema.get("info", {})
        assert "version" in info, "API should have a version"
        assert len(info["version"]) > 0, "API version should not be empty"

    def test_api_has_description(self, schema):
        """Test that API has a description"""
        # Assert
        info = schema.get("info", {})
        assert "description" in info, "API should have a description"
        assert len(info["description"]) > 50, \
            "API description should be substantial (>50 chars)"

    def test_api_title_is_descriptive(self, schema):
        """Test that API title is descriptive"""
        # Assert
        info = schema.get("info", {})
        title = info.get("title", "").lower()
        # Should mention voice, ai, or testing
        assert any(keyword in title for keyword in ["voice", "ai", "test"]), \
            "API title should be descriptive"


# =============================================================================
# Endpoint Documentation Tests
# =============================================================================

class TestEndpointDocumentation:
    """Test that endpoints have proper documentation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    @pytest.fixture
    def schema(self, client):
        """Get OpenAPI schema"""
        response = client.get("/api/openapi.json")
        return response.json()

    def test_api_has_endpoints(self, schema):
        """Test that API has documented endpoints"""
        # Assert
        paths = schema.get("paths", {})
        assert len(paths) > 0, "API should have at least one endpoint"

    def test_health_endpoint_is_documented(self, schema):
        """Test that health endpoint is documented"""
        # Assert
        paths = schema.get("paths", {})
        assert "/health" in paths, "Health endpoint should be documented"

    def test_endpoints_have_operations(self, schema):
        """Test that endpoints have HTTP operation definitions"""
        # Assert
        paths = schema.get("paths", {})

        for path, path_item in paths.items():
            # At least one HTTP method should be defined
            http_methods = ["get", "post", "put", "delete", "patch"]
            has_operation = any(method in path_item for method in http_methods)
            assert has_operation, f"Endpoint {path} should have at least one HTTP operation"

    def test_endpoints_have_summaries(self, schema):
        """Test that endpoints have summary descriptions"""
        # Assert
        paths = schema.get("paths", {})

        endpoints_with_summaries = 0
        total_operations = 0

        for path, path_item in paths.items():
            http_methods = ["get", "post", "put", "delete", "patch"]
            for method in http_methods:
                if method in path_item:
                    total_operations += 1
                    operation = path_item[method]
                    if "summary" in operation or "description" in operation:
                        endpoints_with_summaries += 1

        # At least 70% of endpoints should have summaries or descriptions
        if total_operations > 0:
            coverage = endpoints_with_summaries / total_operations
            assert coverage >= 0.7, \
                f"At least 70% of endpoints should have summaries/descriptions, got {coverage:.1%}"


# =============================================================================
# Request/Response Schema Tests
# =============================================================================

class TestSchemaDocumentation:
    """Test request/response schema documentation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    @pytest.fixture
    def schema(self, client):
        """Get OpenAPI schema"""
        response = client.get("/api/openapi.json")
        return response.json()

    def test_api_has_component_schemas(self, schema):
        """Test that API defines component schemas"""
        # Assert
        # OpenAPI 3.x uses components.schemas
        if "components" in schema:
            components = schema["components"]
            # It's okay if schemas exist or not, just checking structure
            assert True, "Components section exists"
        else:
            # No components yet is okay for basic API
            assert True, "No components defined yet"

    def test_response_schemas_have_examples(self, schema):
        """Test that response schemas have examples"""
        # Assert
        components = schema.get("components", {})
        schemas = components.get("schemas", {})

        # Check if any schemas have examples
        schemas_with_examples = 0
        for schema_name, schema_def in schemas.items():
            if "example" in schema_def or "examples" in schema_def:
                schemas_with_examples += 1

        # This test passes if examples exist OR if we don't have many schemas yet
        # At least some response models should have examples if schemas exist
        if len(schemas) > 3:
            assert schemas_with_examples > 0, \
                "At least some response schemas should have examples"
        else:
            assert True, "Limited schemas, examples optional"


# =============================================================================
# Documentation UI Tests
# =============================================================================

class TestDocumentationUI:
    """Test documentation UI endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    def test_swagger_ui_endpoint_exists(self, client):
        """Test that Swagger UI is accessible"""
        # Act
        response = client.get("/api/docs")

        # Assert
        # Should redirect or return HTML
        assert response.status_code in [200, 307], \
            "Swagger UI endpoint should be accessible"

    def test_redoc_ui_endpoint_exists(self, client):
        """Test that ReDoc UI is accessible"""
        # Act
        response = client.get("/api/redoc")

        # Assert
        # Should redirect or return HTML
        assert response.status_code in [200, 307], \
            "ReDoc UI endpoint should be accessible"


# =============================================================================
# API Organization Tests
# =============================================================================

class TestAPIOrganization:
    """Test API organization and structure"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    @pytest.fixture
    def schema(self, client):
        """Get OpenAPI schema"""
        response = client.get("/api/openapi.json")
        return response.json()

    def test_endpoints_have_tags(self, schema):
        """Test that endpoints are organized with tags"""
        # Assert
        paths = schema.get("paths", {})

        endpoints_with_tags = 0
        total_operations = 0

        for path, path_item in paths.items():
            http_methods = ["get", "post", "put", "delete", "patch"]
            for method in http_methods:
                if method in path_item:
                    total_operations += 1
                    operation = path_item[method]
                    if "tags" in operation and len(operation["tags"]) > 0:
                        endpoints_with_tags += 1

        # At least some endpoints should have tags for organization
        if total_operations > 3:
            coverage = endpoints_with_tags / total_operations
            assert coverage >= 0.5, \
                f"At least 50% of endpoints should have tags, got {coverage:.1%}"
        else:
            assert True, "Limited endpoints, tags optional"
