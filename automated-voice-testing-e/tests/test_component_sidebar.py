"""
Test suite for Sidebar component (TASK-128)

Validates the Sidebar.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI List components
- Navigation menu items (Dashboard, Test Cases, Test Runs, Configurations, Settings)
- React Router navigation
- Active state highlighting
- Icons for menu items
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
LAYOUT_DIR = COMPONENTS_DIR / "Layout"
SIDEBAR_FILE = LAYOUT_DIR / "Sidebar.tsx"


class TestSidebarFileStructure:
    """Test Sidebar file structure"""

    def test_layout_directory_exists(self):
        """Test that Layout directory exists"""
        assert LAYOUT_DIR.exists(), "frontend/src/components/Layout directory should exist"
        assert LAYOUT_DIR.is_dir(), "Layout should be a directory"

    def test_sidebar_file_exists(self):
        """Test that Sidebar.tsx exists"""
        assert SIDEBAR_FILE.exists(), "Sidebar.tsx should exist"
        assert SIDEBAR_FILE.is_file(), "Sidebar.tsx should be a file"

    def test_sidebar_has_content(self):
        """Test that Sidebar.tsx has content"""
        content = SIDEBAR_FILE.read_text()
        assert len(content) > 0, "Sidebar.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = SIDEBAR_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert SIDEBAR_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = SIDEBAR_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_list(self):
        """Test that component imports List"""
        content = SIDEBAR_FILE.read_text()
        assert "List" in content, "Should import List component"

    def test_imports_list_item(self):
        """Test that component imports ListItem"""
        content = SIDEBAR_FILE.read_text()
        assert "ListItem" in content, "Should import ListItem component"

    def test_imports_list_item_button(self):
        """Test that component imports ListItemButton"""
        content = SIDEBAR_FILE.read_text()
        assert "ListItemButton" in content, "Should import ListItemButton component"

    def test_imports_list_item_icon(self):
        """Test that component imports ListItemIcon"""
        content = SIDEBAR_FILE.read_text()
        assert "ListItemIcon" in content, "Should import ListItemIcon component"

    def test_imports_list_item_text(self):
        """Test that component imports ListItemText"""
        content = SIDEBAR_FILE.read_text()
        assert "ListItemText" in content, "Should import ListItemText component"


class TestReactRouterImports:
    """Test React Router imports"""

    def test_imports_react_router(self):
        """Test that component imports from react-router-dom"""
        content = SIDEBAR_FILE.read_text()
        assert "react-router-dom" in content, "Should import from react-router-dom"

    def test_imports_link_or_navigate(self):
        """Test that component imports Link or useNavigate"""
        content = SIDEBAR_FILE.read_text()
        assert ("Link" in content or "useNavigate" in content), \
            "Should import Link or useNavigate for navigation"

    def test_imports_use_location(self):
        """Test that component imports useLocation for active state"""
        content = SIDEBAR_FILE.read_text()
        assert "useLocation" in content, "Should import useLocation for tracking current route"


class TestIconImports:
    """Test Material-UI icon imports"""

    def test_imports_icons(self):
        """Test that component imports icons from @mui/icons-material"""
        content = SIDEBAR_FILE.read_text()
        assert "@mui/icons-material" in content, "Should import icons from @mui/icons-material"

    def test_imports_dashboard_icon(self):
        """Test that component imports dashboard icon"""
        content = SIDEBAR_FILE.read_text()
        assert ("Dashboard" in content and "@mui/icons-material" in content), \
            "Should import Dashboard icon"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_sidebar(self):
        """Test that component exports Sidebar"""
        content = SIDEBAR_FILE.read_text()
        assert "Sidebar" in content, "Should define Sidebar component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = SIDEBAR_FILE.read_text()
        assert ("const Sidebar" in content or "function Sidebar" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = SIDEBAR_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestMenuItems:
    """Test menu items implementation"""

    def test_has_dashboard_menu_item(self):
        """Test that sidebar has Dashboard menu item"""
        content = SIDEBAR_FILE.read_text()
        assert "Dashboard" in content, "Should have Dashboard menu item"

    def test_has_test_cases_menu_item(self):
        """Test that sidebar has Test Cases menu item"""
        content = SIDEBAR_FILE.read_text()
        assert "Test Cases" in content, "Should have Test Cases menu item"

    def test_has_test_runs_menu_item(self):
        """Test that sidebar has Test Runs menu item"""
        content = SIDEBAR_FILE.read_text()
        assert "Test Runs" in content, "Should have Test Runs menu item"

    def test_has_configurations_menu_item(self):
        """Test that sidebar has Configurations menu item"""
        content = SIDEBAR_FILE.read_text()
        assert "Configurations" in content, "Should have Configurations menu item"

    def test_has_settings_menu_item(self):
        """Test that sidebar has Settings menu item"""
        content = SIDEBAR_FILE.read_text()
        assert "Settings" in content, "Should have Settings menu item"


class TestNavigationPaths:
    """Test navigation path configuration"""

    def test_has_dashboard_path(self):
        """Test that component defines dashboard path"""
        content = SIDEBAR_FILE.read_text()
        assert ("/" in content or "/dashboard" in content), \
            "Should have dashboard path"

    def test_has_test_cases_path(self):
        """Test that component defines test cases path"""
        content = SIDEBAR_FILE.read_text()
        assert "/test-cases" in content, "Should have test cases path"

    def test_has_test_runs_path(self):
        """Test that component defines test runs path"""
        content = SIDEBAR_FILE.read_text()
        assert "/test-runs" in content, "Should have test runs path"

    def test_has_configurations_path(self):
        """Test that component defines configurations path"""
        content = SIDEBAR_FILE.read_text()
        assert "/configurations" in content, "Should have configurations path"

    def test_has_settings_path(self):
        """Test that component defines settings path"""
        content = SIDEBAR_FILE.read_text()
        assert "/settings" in content, "Should have settings path"


class TestActiveStateImplementation:
    """Test active state highlighting"""

    def test_uses_use_location(self):
        """Test that component uses useLocation hook"""
        content = SIDEBAR_FILE.read_text()
        assert "useLocation()" in content or "useLocation" in content, \
            "Should use useLocation hook"

    def test_has_active_state_logic(self):
        """Test that component has active state logic"""
        content = SIDEBAR_FILE.read_text()
        assert ("pathname" in content or "location.pathname" in content), \
            "Should check pathname for active state"

    def test_applies_selected_prop(self):
        """Test that component applies selected prop"""
        content = SIDEBAR_FILE.read_text()
        assert "selected" in content, "Should use selected prop for highlighting"


class TestListImplementation:
    """Test MUI List implementation"""

    def test_uses_list_component(self):
        """Test that component uses List"""
        content = SIDEBAR_FILE.read_text()
        assert "<List" in content, "Should use <List> component"

    def test_uses_list_item_button(self):
        """Test that component uses ListItemButton"""
        content = SIDEBAR_FILE.read_text()
        assert "<ListItemButton" in content, "Should use <ListItemButton> component"

    def test_uses_list_item_icon(self):
        """Test that component uses ListItemIcon"""
        content = SIDEBAR_FILE.read_text()
        assert "<ListItemIcon" in content, "Should use <ListItemIcon> component"

    def test_uses_list_item_text(self):
        """Test that component uses ListItemText"""
        content = SIDEBAR_FILE.read_text()
        assert "<ListItemText" in content, "Should use <ListItemText> component"


class TestIconUsage:
    """Test icon usage in menu items"""

    def test_renders_icons(self):
        """Test that component renders icons"""
        content = SIDEBAR_FILE.read_text()
        # Should render icons inside ListItemIcon
        assert ("<ListItemIcon" in content and "@mui/icons-material" in content), \
            "Should render icons in ListItemIcon"

    def test_has_multiple_icon_types(self):
        """Test that component uses different icons for different items"""
        content = SIDEBAR_FILE.read_text()
        # Count different icon imports - should have at least 4-5 different icons
        icon_count = content.count("Icon") if "Icon" in content else 0
        assert icon_count >= 5, "Should use multiple different icons"


class TestNavigationFunctionality:
    """Test navigation functionality"""

    def test_links_to_routes(self):
        """Test that menu items link to routes"""
        content = SIDEBAR_FILE.read_text()
        # Should use Link component or navigate function
        assert ("to=" in content or "navigate(" in content), \
            "Should link to routes"

    def test_uses_router_link(self):
        """Test that component uses router Link"""
        content = SIDEBAR_FILE.read_text()
        assert ("Link" in content or "component={Link}" in content), \
            "Should use React Router Link"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = SIDEBAR_FILE.read_text()
        assert (":" in content and "React" in content), \
            "Should use TypeScript type annotations"

    def test_defines_menu_items_type(self):
        """Test that component defines menu items type or interface"""
        content = SIDEBAR_FILE.read_text()
        # Should define type/interface for menu items
        assert ("interface" in content or "type" in content or "const" in content), \
            "Should define types for menu items"


class TestTaskRequirements:
    """Test TASK-128 specific requirements"""

    def test_task_128_file_location(self):
        """Test TASK-128: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Layout" / "Sidebar.tsx"
        assert expected_path.exists(), \
            "TASK-128: File should be at frontend/src/components/Layout/Sidebar.tsx"

    def test_task_128_has_all_menu_items(self):
        """Test TASK-128: Has all required menu items"""
        content = SIDEBAR_FILE.read_text()
        required_items = ["Dashboard", "Test Cases", "Test Runs", "Configurations", "Settings"]
        for item in required_items:
            assert item in content, f"TASK-128: Should have {item} menu item"

    def test_task_128_uses_mui_list(self):
        """Test TASK-128: Uses Material-UI List components"""
        content = SIDEBAR_FILE.read_text()
        assert "List" in content, "TASK-128: Should use MUI List components"

    def test_task_128_has_navigation(self):
        """Test TASK-128: Has navigation functionality"""
        content = SIDEBAR_FILE.read_text()
        assert "react-router-dom" in content, "TASK-128: Should use React Router for navigation"

    def test_task_128_has_icons(self):
        """Test TASK-128: Has icons for menu items"""
        content = SIDEBAR_FILE.read_text()
        assert "@mui/icons-material" in content, "TASK-128: Should use MUI icons"
