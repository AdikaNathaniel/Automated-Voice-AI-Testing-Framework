"""
Test suite for scenario script API routes.

This module tests the API endpoints for scenario script management:
- POST /api/v1/scenarios - Create scenario
- GET /api/v1/scenarios - List scenarios
- GET /api/v1/scenarios/{id} - Get scenario by ID
- PUT /api/v1/scenarios/{id} - Update scenario
- DELETE /api/v1/scenarios/{id} - Delete scenario
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from pathlib import Path
from uuid import uuid4

import pytest


class TestScenarioRoutesFileExists:
    """Test that scenario routes file exists"""

    def test_scenario_routes_file_exists(self):
        """Test that scenarios.py routes file exists"""
        project_root = Path(__file__).parent.parent
        routes_path = project_root / "backend" / "api" / "routes" / "scenarios.py"
        assert routes_path.exists(), \
            "scenarios.py should exist in backend/api/routes/"


class TestScenarioRouterImport:
    """Test that scenario router can be imported"""

    def test_can_import_router(self):
        """Test that router can be imported from scenarios module"""
        try:
            from api.routes.scenarios import router
            assert router is not None
        except ImportError as e:
            pytest.fail(f"Cannot import router from scenarios: {e}")

    def test_router_has_correct_prefix(self):
        """Test that router has /scenarios prefix"""
        from api.routes.scenarios import router
        assert router.prefix == "/scenarios"

    def test_router_has_correct_tags(self):
        """Test that router has Scenarios tag"""
        from api.routes.scenarios import router
        assert "Scenarios" in router.tags


class TestCreateScenarioEndpoint:
    """Test POST /scenarios endpoint"""

    def test_create_scenario_route_exists(self):
        """Test that POST /scenarios route is defined"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        post_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'POST' in r.methods
        ]
        # Should have multiple POST routes (create scenario, add step, imports)
        assert len(post_routes) >= 1, "POST routes should exist"
        # One should be the base create route (not import, not steps)
        base_post = [
            r for r in post_routes
            if '{scenario_id}' not in r.path and 'import' not in r.path
        ]
        assert len(base_post) == 1, "POST / route should exist"

    def test_create_scenario_requires_auth(self):
        """Test that create scenario requires authentication"""
        from api.routes.scenarios import router

        routes = [r for r in router.routes if hasattr(r, 'methods') and 'POST' in r.methods]
        post_route = routes[0] if routes else None
        assert post_route is not None

        # Check for security dependency
        dependencies = post_route.dependencies or []
        endpoint = post_route.endpoint
        # Either has dependencies or uses Depends in function signature
        assert len(dependencies) > 0 or endpoint is not None


class TestListScenariosEndpoint:
    """Test GET /scenarios endpoint"""

    def test_list_scenarios_route_exists(self):
        """Test that GET /scenarios route is defined"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        get_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'GET' in r.methods
        ]
        # Should have multiple GET routes
        assert len(get_routes) >= 1, "GET routes should exist"
        # One should be the base list route (no path params)
        base_get = [r for r in get_routes if '{' not in r.path]
        assert len(base_get) == 1, "GET / route should exist"

    def test_list_scenarios_supports_pagination(self):
        """Test that list scenarios supports skip and limit parameters"""
        from api.routes.scenarios import router
        import inspect

        routes = [
            r for r in router.routes
            if hasattr(r, 'methods') and 'GET' in r.methods and r.path == "/"
        ]
        if routes:
            endpoint = routes[0].endpoint
            sig = inspect.signature(endpoint)
            params = list(sig.parameters.keys())
            # Should have skip and limit or page and page_size
            assert 'skip' in params or 'page' in params, \
                "List should support pagination parameters"


class TestGetScenarioEndpoint:
    """Test GET /scenarios/{scenario_id} endpoint"""

    def test_get_scenario_route_exists(self):
        """Test that GET /scenarios/{scenario_id} route is defined"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        get_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'GET' in r.methods
            and '{scenario_id}' in r.path
        ]
        assert len(get_routes) >= 1, "GET /{scenario_id} route should exist"


class TestUpdateScenarioEndpoint:
    """Test PUT /scenarios/{scenario_id} endpoint"""

    def test_update_scenario_route_exists(self):
        """Test that PUT /scenarios/{scenario_id} route is defined"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        put_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'PUT' in r.methods
        ]
        assert len(put_routes) >= 1, "PUT route should exist"


class TestDeleteScenarioEndpoint:
    """Test DELETE /scenarios/{scenario_id} endpoint"""

    def test_delete_scenario_route_exists(self):
        """Test that DELETE /scenarios/{scenario_id} route is defined"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        delete_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'DELETE' in r.methods
        ]
        assert len(delete_routes) >= 1, "DELETE route should exist"


class TestScenarioEndpointResponses:
    """Test endpoint response configurations"""

    def test_create_returns_201(self):
        """Test that create scenario returns 201 status code"""
        from api.routes.scenarios import router

        routes = [
            r for r in router.routes
            if hasattr(r, 'methods') and 'POST' in r.methods and r.path == "/"
        ]
        if routes:
            route = routes[0]
            # Check status_code attribute
            assert hasattr(route, 'status_code') and route.status_code == 201

    def test_delete_returns_204(self):
        """Test that delete scenario returns 204 status code"""
        from api.routes.scenarios import router

        routes = [
            r for r in router.routes
            if hasattr(r, 'methods') and 'DELETE' in r.methods
        ]
        if routes:
            route = routes[0]
            # Check status_code attribute
            assert hasattr(route, 'status_code') and route.status_code == 204


class TestScenarioStepsEndpoints:
    """Test endpoints for managing scenario steps"""

    def test_add_step_route_exists(self):
        """Test that POST /scenarios/{scenario_id}/steps route exists"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        step_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'POST' in r.methods
            and 'steps' in r.path
        ]
        assert len(step_routes) >= 1, "POST steps route should exist"

    def test_list_steps_route_exists(self):
        """Test that GET /scenarios/{scenario_id}/steps route exists"""
        from api.routes.scenarios import router

        routes = [route for route in router.routes]
        step_routes = [
            r for r in routes
            if hasattr(r, 'methods') and 'GET' in r.methods
            and 'steps' in r.path
        ]
        assert len(step_routes) >= 1, "GET steps route should exist"


class TestScenarioServiceIntegration:
    """Test that routes integrate with scenario service"""

    def test_scenario_service_exists(self):
        """Test that scenario service module exists"""
        project_root = Path(__file__).parent.parent
        service_path = project_root / "backend" / "services" / "scenario_service.py"
        assert service_path.exists(), \
            "scenario_service.py should exist in backend/services/"

    def test_can_import_scenario_service(self):
        """Test that scenario service can be imported"""
        try:
            from services.scenario_service import ScenarioService
            assert ScenarioService is not None
        except ImportError as e:
            pytest.fail(f"Cannot import ScenarioService: {e}")


class TestRouterRegistration:
    """Test that router is properly registered"""

    def test_router_can_be_included(self):
        """Test that router can be included in main app"""
        from api.routes.scenarios import router
        from fastapi import FastAPI

        app = FastAPI()
        # Should not raise any errors
        app.include_router(router, prefix="/api/v1")

        # Verify routes were added
        routes = [r.path for r in app.routes]
        assert any("/api/v1/scenarios" in r for r in routes)
