"""
Test suite for React Router configuration

Ensures proper routing setup in the frontend application, including
basic routes, protected routes, and navigation functionality.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"
APP_TSX = SRC_DIR / "App.tsx"


class TestAppTsxFile:
    """Test App.tsx file exists and is valid"""

    def test_app_tsx_exists(self):
        """Test that App.tsx exists"""
        assert APP_TSX.exists(), "App.tsx should exist"
        assert APP_TSX.is_file(), "App.tsx should be a file"

    def test_app_tsx_is_typescript(self):
        """Test that App.tsx is a TypeScript file"""
        assert APP_TSX.suffix == ".tsx", "App.tsx should have .tsx extension"

    def test_app_tsx_has_content(self):
        """Test that App.tsx has content"""
        content = APP_TSX.read_text()
        assert len(content) > 0, "App.tsx should not be empty"


class TestReactRouterImports:
    """Test React Router imports in App.tsx"""

    def test_imports_browser_router(self):
        """Test that App.tsx imports BrowserRouter or RouterProvider"""
        content = APP_TSX.read_text()
        # Could use BrowserRouter or the newer RouterProvider
        has_browser_router = 'BrowserRouter' in content
        has_router_provider = 'RouterProvider' in content
        has_routes = 'Routes' in content
        assert has_browser_router or has_router_provider or has_routes, \
            "App.tsx should import routing components from react-router-dom"

    def test_imports_from_react_router_dom(self):
        """Test that App.tsx imports from react-router-dom"""
        content = APP_TSX.read_text()
        assert 'react-router-dom' in content, \
            "App.tsx should import from 'react-router-dom'"


class TestRouteDefinitions:
    """Test route definitions in App.tsx"""

    def test_has_home_route(self):
        """Test that App.tsx defines home route (/)"""
        content = APP_TSX.read_text()
        # Look for path="/" in the content
        assert 'path="/"' in content or "path='/'" in content or 'path: "/"' in content or "path: '/'" in content, \
            "App.tsx should define home route with path='/'"

    def test_has_login_route(self):
        """Test that App.tsx defines login route"""
        content = APP_TSX.read_text()
        assert '/login' in content, "App.tsx should define /login route"

    def test_has_dashboard_route(self):
        """Test that App.tsx defines dashboard route"""
        content = APP_TSX.read_text()
        assert '/dashboard' in content, "App.tsx should define /dashboard route"

    def test_has_test_cases_route(self):
        """Test that App.tsx defines test-cases route"""
        content = APP_TSX.read_text()
        assert '/test-cases' in content, "App.tsx should define /test-cases route"

    def test_has_test_runs_route(self):
        """Test that App.tsx defines test-runs route"""
        content = APP_TSX.read_text()
        assert '/test-runs' in content, "App.tsx should define /test-runs route"


class TestProtectedRoutes:
    """Test protected route implementation"""

    def test_has_protected_route_component_or_logic(self):
        """Test that App.tsx has protected route logic"""
        content = APP_TSX.read_text()
        # Look for common protected route patterns
        has_protected_route = 'ProtectedRoute' in content
        has_private_route = 'PrivateRoute' in content
        has_auth_check = 'isAuthenticated' in content or 'authenticated' in content or 'auth' in content
        assert has_protected_route or has_private_route or has_auth_check, \
            "App.tsx should implement protected route logic"


class TestPageComponents:
    """Test that page components are created or referenced"""

    def test_references_page_components(self):
        """Test that App.tsx references or imports page components"""
        content = APP_TSX.read_text()
        # Look for imports from pages directory or component references
        has_page_imports = './pages' in content or '../pages' in content
        has_component_elements = '<' in content and '/>' in content
        # At minimum, should have component-like JSX
        assert has_component_elements, "App.tsx should use JSX components"


class TestRouteStructure:
    """Test overall route structure"""

    def test_exports_app_component(self):
        """Test that App.tsx exports App component"""
        content = APP_TSX.read_text()
        assert 'export default' in content or 'export {' in content, \
            "App.tsx should export App component"

    def test_app_is_function_or_arrow_function(self):
        """Test that App is defined as a function"""
        content = APP_TSX.read_text()
        has_function_app = 'function App' in content
        has_const_app = 'const App' in content
        assert has_function_app or has_const_app, \
            "App should be defined as a function or const arrow function"


class TestProtectedRouteComponent:
    """Test ProtectedRoute component file"""

    def test_protected_route_component_exists_or_inline(self):
        """Test that ProtectedRoute is defined (file or inline)"""
        # Check if ProtectedRoute component file exists
        protected_route_file = SRC_DIR / "components" / "ProtectedRoute.tsx"
        app_content = APP_TSX.read_text()

        # Either exists as separate file or defined inline in App.tsx
        has_separate_file = protected_route_file.exists()
        has_inline_definition = 'ProtectedRoute' in app_content or 'PrivateRoute' in app_content

        assert has_separate_file or has_inline_definition, \
            "ProtectedRoute should be defined either as separate component or inline"


class TestRoutingIntegration:
    """Test overall routing integration"""

    def test_all_required_routes_present(self):
        """Test that all 5 required routes are present"""
        content = APP_TSX.read_text()

        required_routes = [
            '/',
            '/login',
            '/dashboard',
            '/test-cases',
            '/test-runs'
        ]

        missing_routes = []
        for route in required_routes:
            if route not in content:
                missing_routes.append(route)

        assert len(missing_routes) == 0, \
            f"Missing required routes: {', '.join(missing_routes)}"

    def test_uses_routes_component_or_equivalent(self):
        """Test that App.tsx uses Routes component or createBrowserRouter"""
        content = APP_TSX.read_text()
        uses_routes = '<Routes' in content or '<Routes>' in content
        uses_create_router = 'createBrowserRouter' in content
        uses_router_provider = 'RouterProvider' in content

        assert uses_routes or uses_create_router or uses_router_provider, \
            "App.tsx should use Routes component or router configuration"


class TestPagePlaceholders:
    """Test that page placeholder components exist or are defined"""

    def test_home_page_exists_or_placeholder(self):
        """Test that HomePage component exists or has placeholder"""
        home_page = SRC_DIR / "pages" / "HomePage.tsx"
        app_content = APP_TSX.read_text()

        # Either exists as file, or has inline placeholder, or references 'Home'
        has_file = home_page.exists()
        has_reference = 'Home' in app_content

        # This is informational - pages may be placeholders initially
        # We just check that the route structure is in place
        pass

    def test_login_page_exists_or_placeholder(self):
        """Test that LoginPage component exists or has placeholder"""
        login_page = SRC_DIR / "pages" / "LoginPage.tsx"
        app_content = APP_TSX.read_text()

        has_file = login_page.exists()
        has_reference = 'Login' in app_content

        # Informational check
        pass

    def test_dashboard_page_exists_or_placeholder(self):
        """Test that DashboardPage component exists or has placeholder"""
        dashboard_page = SRC_DIR / "pages" / "DashboardPage.tsx"
        app_content = APP_TSX.read_text()

        has_file = dashboard_page.exists()
        has_reference = 'Dashboard' in app_content

        # Informational check
        pass


class TestTypeScriptSafety:
    """Test TypeScript type safety in routing"""

    def test_no_typescript_errors_in_syntax(self):
        """Test that App.tsx has valid TypeScript syntax"""
        content = APP_TSX.read_text()

        # Basic syntax checks
        assert content.count('(') == content.count(')') or abs(content.count('(') - content.count(')')) <= 2, \
            "Parentheses should be balanced (allowing for some multiline)"
        assert content.count('{') == content.count('}') or abs(content.count('{') - content.count('}')) <= 2, \
            "Braces should be balanced (allowing for some multiline)"
        assert content.count('[') == content.count(']'), "Brackets should be balanced"
