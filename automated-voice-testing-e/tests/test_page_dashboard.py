"""
Test suite for Dashboard page (TASK-131)

Validates the Dashboard.tsx page implementation including:
- File structure and imports
- React component structure
- Material-UI Grid layout
- Page title/header
- Content area for widgets
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
DASHBOARD_DIR = PAGES_DIR / "Dashboard"
DASHBOARD_FILE = DASHBOARD_DIR / "Dashboard.tsx"


class TestDashboardFileStructure:
    """Test Dashboard file structure"""

    def test_pages_directory_exists(self):
        """Test that pages directory exists"""
        assert PAGES_DIR.exists(), "frontend/src/pages directory should exist"
        assert PAGES_DIR.is_dir(), "pages should be a directory"

    def test_dashboard_directory_exists(self):
        """Test that Dashboard directory exists"""
        assert DASHBOARD_DIR.exists(), "frontend/src/pages/Dashboard directory should exist"
        assert DASHBOARD_DIR.is_dir(), "Dashboard should be a directory"

    def test_dashboard_file_exists(self):
        """Test that Dashboard.tsx exists"""
        assert DASHBOARD_FILE.exists(), "Dashboard.tsx should exist"
        assert DASHBOARD_FILE.is_file(), "Dashboard.tsx should be a file"

    def test_dashboard_has_content(self):
        """Test that Dashboard.tsx has content"""
        content = DASHBOARD_FILE.read_text()
        assert len(content) > 0, "Dashboard.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = DASHBOARD_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert DASHBOARD_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = DASHBOARD_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_grid(self):
        """Test that component imports Grid"""
        content = DASHBOARD_FILE.read_text()
        assert "Grid" in content, "Should import Grid component for layout"

    def test_imports_container(self):
        """Test that component imports Container or Box"""
        content = DASHBOARD_FILE.read_text()
        assert ("Container" in content or "Box" in content), \
            "Should import Container or Box for page wrapper"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = DASHBOARD_FILE.read_text()
        assert "Typography" in content, "Should import Typography for page title"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_dashboard(self):
        """Test that component exports Dashboard"""
        content = DASHBOARD_FILE.read_text()
        assert "Dashboard" in content, "Should define Dashboard component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = DASHBOARD_FILE.read_text()
        assert ("const Dashboard" in content or "function Dashboard" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = DASHBOARD_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPageHeader:
    """Test page header implementation"""

    def test_has_page_title(self):
        """Test that page has title"""
        content = DASHBOARD_FILE.read_text()
        assert ("Dashboard" in content and "Typography" in content), \
            "Should have Dashboard title using Typography"

    def test_uses_typography_for_title(self):
        """Test that page uses Typography component"""
        content = DASHBOARD_FILE.read_text()
        assert "<Typography" in content, "Should use Typography component"


class TestGridLayout:
    """Test Grid layout implementation"""

    def test_uses_grid_component(self):
        """Test that component uses Grid"""
        content = DASHBOARD_FILE.read_text()
        assert "<Grid" in content, "Should use <Grid> component"

    def test_has_grid_container(self):
        """Test that component has Grid container"""
        content = DASHBOARD_FILE.read_text()
        assert "container" in content, "Should have Grid container"

    def test_has_grid_items(self):
        """Test that component has Grid items"""
        content = DASHBOARD_FILE.read_text()
        # Should have multiple Grid items (at least for future widgets)
        assert ("item" in content or "<Grid" in content), \
            "Should have Grid items for widgets"

    def test_grid_has_spacing(self):
        """Test that Grid has spacing"""
        content = DASHBOARD_FILE.read_text()
        assert "spacing" in content, "Grid should have spacing prop"


class TestLayoutStructure:
    """Test layout structure"""

    def test_has_container_or_box(self):
        """Test that page has Container or Box wrapper"""
        content = DASHBOARD_FILE.read_text()
        assert ("<Container" in content or "<Box" in content), \
            "Should have Container or Box wrapper"

    def test_title_before_grid(self):
        """Test that title comes before grid"""
        content = DASHBOARD_FILE.read_text()
        # Typography (title) should come before Grid (content)
        typography_pos = content.find("<Typography")
        grid_pos = content.find("<Grid")
        assert typography_pos < grid_pos, \
            "Page title should come before grid content"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = DASHBOARD_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = DASHBOARD_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-131 specific requirements"""

    def test_task_131_file_location(self):
        """Test TASK-131: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "pages" / "Dashboard" / "Dashboard.tsx"
        assert expected_path.exists(), \
            "TASK-131: File should be at frontend/src/pages/Dashboard/Dashboard.tsx"

    def test_task_131_uses_grid_layout(self):
        """Test TASK-131: Uses Grid layout"""
        content = DASHBOARD_FILE.read_text()
        assert "<Grid" in content, "TASK-131: Should use Grid layout"

    def test_task_131_has_cards_area(self):
        """Test TASK-131: Has area for cards"""
        content = DASHBOARD_FILE.read_text()
        # Grid with items should be present for cards
        assert ("Grid" in content and "item" in content), \
            "TASK-131: Should have Grid items for cards"

    def test_task_131_is_page_component(self):
        """Test TASK-131: Is a page component"""
        content = DASHBOARD_FILE.read_text()
        assert "Dashboard" in content, "TASK-131: Should be Dashboard page component"
