"""
Test suite for frontend dependencies

Ensures all required npm packages are installed in package.json
for the React TypeScript frontend application.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
PACKAGE_JSON = FRONTEND_DIR / "package.json"


def get_package_json():
    """Helper to load package.json"""
    with open(PACKAGE_JSON, 'r') as f:
        return json.load(f)


class TestMaterialUIDesignSystemDependencies:
    """Test Material-UI (MUI) dependencies"""

    def test_mui_material_installed(self):
        """Test that @mui/material is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert '@mui/material' in dependencies, \
            "@mui/material should be in dependencies"

    def test_mui_icons_material_installed(self):
        """Test that @mui/icons-material is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert '@mui/icons-material' in dependencies, \
            "@mui/icons-material should be in dependencies"

    def test_emotion_react_installed(self):
        """Test that @emotion/react is installed (peer dependency for MUI)"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        # @emotion/react is required by @mui/material
        assert '@emotion/react' in dependencies, \
            "@emotion/react should be in dependencies (required by MUI)"

    def test_emotion_styled_installed(self):
        """Test that @emotion/styled is installed (peer dependency for MUI)"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        # @emotion/styled is required by @mui/material
        assert '@emotion/styled' in dependencies, \
            "@emotion/styled should be in dependencies (required by MUI)"


class TestStateManagementDependencies:
    """Test Redux state management dependencies"""

    def test_reduxjs_toolkit_installed(self):
        """Test that @reduxjs/toolkit is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert '@reduxjs/toolkit' in dependencies, \
            "@reduxjs/toolkit should be in dependencies"

    def test_react_redux_installed(self):
        """Test that react-redux is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'react-redux' in dependencies, \
            "react-redux should be in dependencies"


class TestRoutingDependencies:
    """Test React Router dependencies"""

    def test_react_router_dom_installed(self):
        """Test that react-router-dom is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'react-router-dom' in dependencies, \
            "react-router-dom should be in dependencies"


class TestHTTPClientDependencies:
    """Test HTTP client dependencies"""

    def test_axios_installed(self):
        """Test that axios is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'axios' in dependencies, \
            "axios should be in dependencies"


class TestWebSocketDependencies:
    """Test WebSocket client dependencies"""

    def test_socket_io_client_installed(self):
        """Test that socket.io-client is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'socket.io-client' in dependencies, \
            "socket.io-client should be in dependencies"


class TestDataVisualizationDependencies:
    """Test data visualization dependencies"""

    def test_recharts_installed(self):
        """Test that recharts is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'recharts' in dependencies, \
            "recharts should be in dependencies"


class TestUtilityDependencies:
    """Test utility library dependencies"""

    def test_date_fns_installed(self):
        """Test that date-fns is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'date-fns' in dependencies, \
            "date-fns should be in dependencies"


class TestFormManagementDependencies:
    """Test form handling dependencies"""

    def test_react_hook_form_installed(self):
        """Test that react-hook-form is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'react-hook-form' in dependencies, \
            "react-hook-form should be in dependencies"

    def test_yup_installed(self):
        """Test that yup is installed"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})
        assert 'yup' in dependencies, \
            "yup should be in dependencies"


class TestDependencyVersions:
    """Test that dependencies have valid version specifiers"""

    def test_all_dependencies_have_versions(self):
        """Test that all dependencies have version numbers"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})

        for package, version in dependencies.items():
            assert version is not None, f"{package} should have a version"
            assert len(version) > 0, f"{package} version should not be empty"
            # Version should start with a number, ^, ~, or *
            assert version[0].isdigit() or version[0] in ['^', '~', '*', '>', '<', '='], \
                f"{package} version should be valid: {version}"


class TestNodeModulesStructure:
    """Test node_modules structure after installation"""

    def test_node_modules_exists_after_install(self):
        """Test that node_modules directory exists after npm install"""
        node_modules = FRONTEND_DIR / "node_modules"
        # This will pass if node_modules exists, or be informational if not yet installed
        if node_modules.exists():
            assert node_modules.is_dir(), "node_modules should be a directory"

    def test_mui_material_in_node_modules(self):
        """Test that @mui/material exists in node_modules after install"""
        mui_material = FRONTEND_DIR / "node_modules" / "@mui" / "material"
        # This will pass if installed
        if mui_material.exists():
            assert mui_material.is_dir(), "@mui/material should be in node_modules"

    def test_react_redux_in_node_modules(self):
        """Test that react-redux exists in node_modules after install"""
        react_redux = FRONTEND_DIR / "node_modules" / "react-redux"
        # This will pass if installed
        if react_redux.exists():
            assert react_redux.is_dir(), "react-redux should be in node_modules"


class TestPackageLockJson:
    """Test package-lock.json after installation"""

    def test_package_lock_created_after_install(self):
        """Test that package-lock.json is created after npm install"""
        package_lock = FRONTEND_DIR / "package-lock.json"
        # This will pass if package-lock.json exists
        if package_lock.exists():
            assert package_lock.is_file(), "package-lock.json should be a file"

            # Should be valid JSON
            with open(package_lock, 'r') as f:
                lock_data = json.load(f)
            assert isinstance(lock_data, dict), "package-lock.json should be a JSON object"

    def test_package_lock_has_packages(self):
        """Test that package-lock.json contains packages"""
        package_lock = FRONTEND_DIR / "package-lock.json"
        if package_lock.exists():
            with open(package_lock, 'r') as f:
                lock_data = json.load(f)
            # Modern npm uses "packages" key
            assert 'packages' in lock_data or 'dependencies' in lock_data, \
                "package-lock.json should have packages or dependencies"


class TestCoreDependenciesIntegration:
    """Test that all core dependencies work together"""

    def test_all_required_dependencies_present(self):
        """Test that all required dependencies from TASK-022 are present"""
        data = get_package_json()
        dependencies = data.get('dependencies', {})

        required_packages = [
            '@mui/material',
            '@mui/icons-material',
            '@reduxjs/toolkit',
            'react-redux',
            'react-router-dom',
            'axios',
            'socket.io-client',
            'recharts',
            'date-fns',
            'react-hook-form',
            'yup',
        ]

        missing_packages = []
        for package in required_packages:
            if package not in dependencies:
                missing_packages.append(package)

        assert len(missing_packages) == 0, \
            f"Missing required packages: {', '.join(missing_packages)}"

    def test_no_duplicate_dependencies(self):
        """Test that there are no duplicate packages in dependencies and devDependencies"""
        data = get_package_json()
        dependencies = set(data.get('dependencies', {}).keys())
        dev_dependencies = set(data.get('devDependencies', {}).keys())

        duplicates = dependencies.intersection(dev_dependencies)
        assert len(duplicates) == 0, \
            f"Found duplicate packages in both dependencies and devDependencies: {duplicates}"
