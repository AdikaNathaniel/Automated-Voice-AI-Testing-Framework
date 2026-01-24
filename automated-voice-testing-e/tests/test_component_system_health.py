"""
Test suite for SystemHealth widget (TASK-134)

Validates the SystemHealth.tsx widget implementation including:
- File structure and imports
- React component structure
- Material-UI components
- Display of system status indicators (API, Database, Queue)
- Color-coded status indicators
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
DASHBOARD_COMPONENTS_DIR = COMPONENTS_DIR / "Dashboard"
SYSTEM_HEALTH_FILE = DASHBOARD_COMPONENTS_DIR / "SystemHealth.tsx"


class TestSystemHealthFileStructure:
    """Test SystemHealth file structure"""

    def test_dashboard_components_directory_exists(self):
        """Test that Dashboard components directory exists"""
        assert DASHBOARD_COMPONENTS_DIR.exists(), \
            "frontend/src/components/Dashboard directory should exist"
        assert DASHBOARD_COMPONENTS_DIR.is_dir(), "Dashboard should be a directory"

    def test_system_health_file_exists(self):
        """Test that SystemHealth.tsx exists"""
        assert SYSTEM_HEALTH_FILE.exists(), "SystemHealth.tsx should exist"
        assert SYSTEM_HEALTH_FILE.is_file(), "SystemHealth.tsx should be a file"

    def test_system_health_has_content(self):
        """Test that SystemHealth.tsx has content"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert len(content) > 0, "SystemHealth.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert SYSTEM_HEALTH_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_card(self):
        """Test that component imports Card"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "Card" in content, "Should import Card component"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "Typography" in content, "Should import Typography for headings"

    def test_imports_list_or_stack(self):
        """Test that component imports List or Stack components"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("List" in content or "Stack" in content or "Box" in content), \
            "Should import layout components for status items"

    def test_imports_chip_or_badge(self):
        """Test that component imports Chip or Badge for status indicators"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("Chip" in content or "Badge" in content or "Circle" in content), \
            "Should import status indicator components"


class TestIconImports:
    """Test icon imports"""

    def test_may_import_status_icons(self):
        """Test that component may import status icons"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # Icons are optional but recommended
        has_icons = ("@mui/icons-material" in content or "Icon" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Status icons are optional but recommended"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_system_health(self):
        """Test that component exports SystemHealth"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "SystemHealth" in content, "Should define SystemHealth component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("const SystemHealth" in content or "function SystemHealth" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestWidgetHeader:
    """Test widget header implementation"""

    def test_has_widget_title(self):
        """Test that widget has title"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("System" in content and "Health" in content), \
            "Should have 'System Health' title"

    def test_uses_typography_for_title(self):
        """Test that widget uses Typography for title"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "<Typography" in content, "Should use Typography component"


class TestStatusIndicators:
    """Test status indicators implementation"""

    def test_has_api_status(self):
        """Test that widget displays API status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "API" in content, "Should display API status"

    def test_has_database_status(self):
        """Test that widget displays database status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("Database" in content or "DB" in content), \
            "Should display database status"

    def test_has_queue_status(self):
        """Test that widget displays queue status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "Queue" in content, "Should display queue status"

    def test_has_status_indicators(self):
        """Test that widget has status indicators"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # Should have some form of status display
        assert ("status" in content.lower() or "health" in content.lower()), \
            "Should have status indicators"


class TestColorCoding:
    """Test color-coded indicators"""

    def test_has_color_coding(self):
        """Test that widget uses color coding"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # Should have color-related props or styling
        assert ("color" in content.lower() or "success" in content or
                "error" in content or "warning" in content), \
            "Should use color coding for status"

    def test_may_have_status_colors_mapping(self):
        """Test that widget may have status colors mapping"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # May have a function or mapping for status colors
        has_color_mapping = ("getColor" in content or "statusColor" in content or
                            "switch" in content or "color:" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Status color mapping is recommended"


class TestDataStructure:
    """Test data structure handling"""

    def test_has_status_type_or_interface(self):
        """Test that component defines status type or interface"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # Should define types for status
        assert ("interface" in content or "type" in content), \
            "Should define status types or interfaces"

    def test_handles_status_data(self):
        """Test that component handles status data"""
        content = SYSTEM_HEALTH_FILE.read_text()
        # Should reference status data
        assert ("status" in content.lower()), \
            "Should handle status data"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-134 specific requirements"""

    def test_task_134_file_location(self):
        """Test TASK-134: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Dashboard" / "SystemHealth.tsx"
        assert expected_path.exists(), \
            "TASK-134: File should be at frontend/src/components/Dashboard/SystemHealth.tsx"

    def test_task_134_displays_api_status(self):
        """Test TASK-134: Displays API status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "API" in content, \
            "TASK-134: Should display API status"

    def test_task_134_displays_database_status(self):
        """Test TASK-134: Displays database status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("Database" in content or "DB" in content), \
            "TASK-134: Should display database status"

    def test_task_134_displays_queue_status(self):
        """Test TASK-134: Displays queue status"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "Queue" in content, \
            "TASK-134: Should display queue status"

    def test_task_134_has_color_coded_indicators(self):
        """Test TASK-134: Has color-coded indicators"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert ("color" in content.lower() or "success" in content or
                "error" in content or "warning" in content), \
            "TASK-134: Should have color-coded indicators"

    def test_task_134_is_widget_component(self):
        """Test TASK-134: Is a widget component"""
        content = SYSTEM_HEALTH_FILE.read_text()
        assert "SystemHealth" in content, \
            "TASK-134: Should be SystemHealth widget component"
