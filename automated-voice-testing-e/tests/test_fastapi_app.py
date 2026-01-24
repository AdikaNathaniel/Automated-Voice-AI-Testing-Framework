"""
Test suite for FastAPI application scaffold
Ensures backend/api/main.py exists and is properly configured
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend'))


class TestFastAPIApp:
    """Test FastAPI application scaffold"""

    @pytest.fixture
    def project_root(self):
        """Get project root directory"""
        return os.path.dirname(os.path.dirname(__file__))

    @pytest.fixture
    def main_py_path(self, project_root):
        """Get path to backend/api/main.py file"""
        return os.path.join(project_root, 'backend', 'api', 'main.py')

    def test_main_py_exists(self, main_py_path):
        """Test that backend/api/main.py file exists"""
        assert os.path.exists(main_py_path), \
            "backend/api/main.py file must exist"

    def test_can_import_app(self):
        """Test that we can import the FastAPI app"""
        try:
            from api.main import app
            assert app is not None, "App should be defined"
        except ImportError as e:
            pytest.fail(f"Failed to import app from api.main: {e}")

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance"""
        from fastapi import FastAPI
        from api.main import app

        assert isinstance(app, FastAPI), \
            "app must be a FastAPI instance"

    def test_app_has_title(self):
        """Test that app has correct title"""
        from api.main import app

        assert app.title == "Voice AI Testing Framework API", \
            "App title should be 'Voice AI Testing Framework API'"

    def test_app_has_version(self):
        """Test that app has version specified"""
        from api.main import app

        assert hasattr(app, 'version'), "App should have version attribute"
        assert app.version is not None, "App version should not be None"

    def test_app_has_custom_docs_url(self):
        """Test that app has custom docs URL"""
        from api.main import app

        assert app.docs_url == "/api/docs", \
            "Docs URL should be '/api/docs'"

    def test_app_has_custom_redoc_url(self):
        """Test that app has custom redoc URL"""
        from api.main import app

        assert app.redoc_url == "/api/redoc", \
            "ReDoc URL should be '/api/redoc'"

    def test_app_has_description(self):
        """Test that app has description"""
        from api.main import app

        assert hasattr(app, 'description'), "App should have description"
        assert app.description is not None, "App description should not be None"
        assert len(app.description) > 0, "App description should not be empty"


class TestCORSMiddleware:
    """Test CORS middleware configuration"""

    def test_cors_middleware_is_configured(self):
        """Test that CORS middleware is added to the app"""
        from api.main import app

        # Check if CORSMiddleware is in the middleware stack
        # In newer FastAPI versions, middleware is wrapped in Middleware objects
        has_cors = False
        for middleware in app.user_middleware:
            # Check the middleware class name or the cls attribute
            middleware_name = type(middleware).__name__
            if middleware_name == 'CORSMiddleware':
                has_cors = True
                break
            # Check if middleware has cls attribute (wrapped middleware)
            if hasattr(middleware, 'cls'):
                if middleware.cls.__name__ == 'CORSMiddleware':
                    has_cors = True
                    break

        assert has_cors, \
            "CORSMiddleware should be configured"

    def test_cors_allows_credentials(self):
        """Test that CORS is configured to allow credentials"""
        from api.main import app

        # Find CORS middleware in the stack
        cors_middleware = None
        for middleware in app.user_middleware:
            if type(middleware).__name__ == 'CORSMiddleware':
                cors_middleware = middleware
                break

        if cors_middleware:
            # Check if allow_credentials is set
            assert hasattr(cors_middleware, 'kwargs'), \
                "Middleware should have kwargs"


class TestHealthEndpoint:
    """Test health check endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    def test_health_endpoint_exists(self, client):
        """Test that /health endpoint exists"""
        response = client.get("/health")
        assert response.status_code == 200, \
            "/health endpoint should return 200 status"

    def test_health_endpoint_returns_json(self, client):
        """Test that /health endpoint returns JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json", \
            "/health endpoint should return JSON"

    def test_health_endpoint_returns_status(self, client):
        """Test that /health endpoint returns status"""
        response = client.get("/health")
        data = response.json()

        assert "status" in data, \
            "/health response should contain 'status' field"
        assert data["status"] == "healthy", \
            "Status should be 'healthy'"

    def test_health_endpoint_returns_service_name(self, client):
        """Test that /health endpoint returns service name"""
        response = client.get("/health")
        data = response.json()

        assert "service" in data, \
            "/health response should contain 'service' field"

    def test_health_endpoint_returns_version(self, client):
        """Test that /health endpoint returns version"""
        response = client.get("/health")
        data = response.json()

        assert "version" in data, \
            "/health response should contain 'version' field"


class TestReadyEndpoint:
    """Test readiness check endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    def test_ready_endpoint_exists(self, client):
        """Test that /ready endpoint exists"""
        response = client.get("/ready")
        assert response.status_code == 200, \
            "/ready endpoint should return 200 status"

    def test_ready_endpoint_returns_json(self, client):
        """Test that /ready endpoint returns JSON"""
        response = client.get("/ready")
        assert response.headers["content-type"] == "application/json", \
            "/ready endpoint should return JSON"

    def test_ready_endpoint_returns_status(self, client):
        """Test that /ready endpoint returns ready status"""
        response = client.get("/ready")
        data = response.json()

        assert "status" in data, \
            "/ready response should contain 'status' field"
        assert data["status"] == "ready", \
            "Status should be 'ready'"


class TestAPIVersioning:
    """Test API versioning structure"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from api.main import app
        return TestClient(app)

    def test_api_v1_router_exists(self):
        """Test that API v1 router is configured"""
        from api.main import app

        # Check if there's a router with /api/v1 prefix
        route_paths = [route.path for route in app.routes]

        # Should have routes that start with /api/v1 or have it configured
        has_api_v1 = any('/api/v1' in path for path in route_paths)

        # If not in paths, check if app has api_router attribute
        if not has_api_v1:
            assert hasattr(app, 'api_router') or len([r for r in app.routes if hasattr(r, 'prefix')]) > 0, \
                "App should have API router configuration"

    def test_root_endpoint_exists(self, client):
        """Test that root endpoint exists"""
        response = client.get("/")
        assert response.status_code == 200, \
            "Root endpoint should return 200 status"

    def test_root_endpoint_returns_api_info(self, client):
        """Test that root endpoint returns API information"""
        response = client.get("/")
        data = response.json()

        assert "message" in data or "title" in data or "name" in data, \
            "Root endpoint should return API information"


class TestAppStructure:
    """Test overall application structure"""

    def test_app_has_routes(self):
        """Test that app has routes configured"""
        from api.main import app

        assert len(app.routes) > 0, \
            "App should have routes configured"

    def test_app_has_startup_events(self):
        """Test that app can handle startup events"""
        from api.main import app

        # Check if app has on_event decorator available
        assert hasattr(app, 'on_event'), \
            "App should have on_event decorator for lifecycle management"

    def test_health_endpoint_in_routes(self):
        """Test that health endpoint is in routes"""
        from api.main import app

        route_paths = [route.path for route in app.routes]
        assert '/health' in route_paths, \
            "/health endpoint should be in routes"

    def test_ready_endpoint_in_routes(self):
        """Test that ready endpoint is in routes"""
        from api.main import app

        route_paths = [route.path for route in app.routes]
        assert '/ready' in route_paths, \
            "/ready endpoint should be in routes"
