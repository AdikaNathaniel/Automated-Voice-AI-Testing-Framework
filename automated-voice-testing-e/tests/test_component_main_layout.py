"""
Test suite for MainLayout component (TASK-127)

Validates the MainLayout.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI AppBar component
- Material-UI Drawer (sidebar) component
- Main content area
- Responsive design (useMediaQuery)
- TypeScript usage
- Children prop handling
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
LAYOUT_DIR = COMPONENTS_DIR / "Layout"
MAIN_LAYOUT_FILE = LAYOUT_DIR / "MainLayout.tsx"


class TestMainLayoutFileStructure:
    """Test MainLayout file structure"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components directory should exist"
        assert COMPONENTS_DIR.is_dir(), "components should be a directory"

    def test_layout_directory_exists(self):
        """Test that Layout directory exists"""
        assert LAYOUT_DIR.exists(), "frontend/src/components/Layout directory should exist"
        assert LAYOUT_DIR.is_dir(), "Layout should be a directory"

    def test_main_layout_file_exists(self):
        """Test that MainLayout.tsx exists"""
        assert MAIN_LAYOUT_FILE.exists(), "MainLayout.tsx should exist"
        assert MAIN_LAYOUT_FILE.is_file(), "MainLayout.tsx should be a file"

    def test_main_layout_has_content(self):
        """Test that MainLayout.tsx has content"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert len(content) > 0, "MainLayout.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_imports_react_hooks(self):
        """Test that component imports React hooks"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should use useState for drawer state
        assert "useState" in content, "Should import useState hook"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert MAIN_LAYOUT_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_appbar(self):
        """Test that component imports AppBar"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "AppBar" in content, "Should import AppBar component"

    def test_imports_drawer(self):
        """Test that component imports Drawer"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "Drawer" in content, "Should import Drawer component"

    def test_imports_toolbar(self):
        """Test that component imports Toolbar"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "Toolbar" in content, "Should import Toolbar for AppBar"

    def test_imports_box(self):
        """Test that component imports Box"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "Box" in content, "Should import Box for layout"

    def test_imports_icon_button(self):
        """Test that component imports IconButton"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "IconButton" in content, "Should import IconButton for menu toggle"


class TestResponsiveDesign:
    """Test responsive design implementation"""

    def test_imports_use_media_query(self):
        """Test that component imports useMediaQuery"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "useMediaQuery" in content, "Should import useMediaQuery for responsive design"

    def test_imports_use_theme(self):
        """Test that component imports useTheme"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "useTheme" in content, "Should import useTheme for breakpoints"

    def test_uses_breakpoints(self):
        """Test that component uses theme breakpoints"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "breakpoints" in content, "Should use theme breakpoints"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_main_layout(self):
        """Test that component exports MainLayout"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "MainLayout" in content, "Should define MainLayout component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should be arrow function or function declaration
        assert ("const MainLayout" in content or "function MainLayout" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "export default" in content, "Should have default export"

    def test_accepts_children_prop(self):
        """Test that component accepts children prop"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "children" in content, "Should accept children prop"


class TestPropsInterface:
    """Test component props interface"""

    def test_defines_props_interface(self):
        """Test that component defines props interface"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Should define props interface/type"

    def test_props_include_children(self):
        """Test that props interface includes children"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "children" in content and "ReactNode" in content, \
            "Props should include children: ReactNode"


class TestDrawerImplementation:
    """Test Drawer (sidebar) implementation"""

    def test_has_drawer_state(self):
        """Test that component has drawer state"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "useState" in content, "Should use useState for drawer state"

    def test_has_drawer_toggle(self):
        """Test that component has drawer toggle function"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should have function to toggle drawer
        assert ("toggle" in content.lower() or "setOpen" in content or "handleDrawer" in content), \
            "Should have drawer toggle function"

    def test_drawer_is_temporary_on_mobile(self):
        """Test that Drawer is temporary on mobile"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should use variant="temporary" or conditional variant
        assert ("temporary" in content or "variant" in content), \
            "Drawer should support temporary variant for mobile"

    def test_drawer_has_width(self):
        """Test that Drawer has defined width"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should define drawer width constant
        assert ("width" in content and ("240" in content or "drawerWidth" in content)), \
            "Should define drawer width"


class TestAppBarImplementation:
    """Test AppBar implementation"""

    def test_uses_appbar_component(self):
        """Test that component uses AppBar"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "<AppBar" in content, "Should use <AppBar> component"

    def test_appbar_has_toolbar(self):
        """Test that AppBar contains Toolbar"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "<Toolbar" in content, "AppBar should contain <Toolbar>"

    def test_has_menu_icon_button(self):
        """Test that AppBar has menu IconButton"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "<IconButton" in content, "Should have IconButton for menu toggle"

    def test_menu_icon_imports_icon(self):
        """Test that component imports menu icon"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert ("MenuIcon" in content or "@mui/icons-material" in content), \
            "Should import menu icon"


class TestMainContentArea:
    """Test main content area implementation"""

    def test_has_main_content_area(self):
        """Test that component has main content area"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert ("<Box" in content or "<main" in content or "component=\"main\"" in content), \
            "Should have main content area"

    def test_renders_children(self):
        """Test that component renders children"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "{children}" in content, "Should render children in main content area"

    def test_main_area_has_padding(self):
        """Test that main content area has padding"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should use sx prop or styled components for padding
        assert ("padding" in content or "sx=" in content or "p=" in content), \
            "Main content should have padding"


class TestLayoutStructure:
    """Test overall layout structure"""

    def test_has_proper_nesting(self):
        """Test that components are properly nested"""
        content = MAIN_LAYOUT_FILE.read_text()
        # AppBar should come before main content
        appbar_pos = content.find("<AppBar")
        children_pos = content.find("{children}")
        assert appbar_pos < children_pos, \
            "AppBar should come before children content"

    def test_drawer_and_main_content_separate(self):
        """Test that Drawer and main content are separate"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "<Drawer" in content and "<Box" in content, \
            "Should have separate Drawer and Box for content"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = MAIN_LAYOUT_FILE.read_text()
        # Should have type annotations
        assert (":" in content and ("React" in content or "FC" in content)), \
            "Should use TypeScript type annotations"

    def test_imports_react_types(self):
        """Test that component imports React types"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert ("ReactNode" in content or "React.ReactNode" in content), \
            "Should import ReactNode type"


class TestTaskRequirements:
    """Test TASK-127 specific requirements"""

    def test_task_127_file_location(self):
        """Test TASK-127: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Layout" / "MainLayout.tsx"
        assert expected_path.exists(), \
            "TASK-127: File should be at frontend/src/components/Layout/MainLayout.tsx"

    def test_task_127_includes_appbar(self):
        """Test TASK-127: Includes AppBar"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "AppBar" in content, "TASK-127: Should include AppBar"

    def test_task_127_includes_drawer(self):
        """Test TASK-127: Includes Drawer (sidebar)"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "Drawer" in content, "TASK-127: Should include Drawer"

    def test_task_127_includes_main_content_area(self):
        """Test TASK-127: Includes main content area"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "{children}" in content, "TASK-127: Should include main content area with children"

    def test_task_127_responsive_design(self):
        """Test TASK-127: Has responsive design"""
        content = MAIN_LAYOUT_FILE.read_text()
        assert "useMediaQuery" in content, "TASK-127: Should implement responsive design"
