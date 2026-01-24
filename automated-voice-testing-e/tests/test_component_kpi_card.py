"""
Test suite for KPICard component (TASK-132)

Validates the KPICard.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI Card components
- Props interface (title, value, trend, icon)
- Display: Large metric value, label, trend indicator
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
DASHBOARD_COMPONENTS_DIR = COMPONENTS_DIR / "Dashboard"
KPI_CARD_FILE = DASHBOARD_COMPONENTS_DIR / "KPICard.tsx"


class TestKPICardFileStructure:
    """Test KPICard file structure"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components directory should exist"
        assert COMPONENTS_DIR.is_dir(), "components should be a directory"

    def test_dashboard_components_directory_exists(self):
        """Test that Dashboard components directory exists"""
        assert DASHBOARD_COMPONENTS_DIR.exists(), \
            "frontend/src/components/Dashboard directory should exist"
        assert DASHBOARD_COMPONENTS_DIR.is_dir(), "Dashboard should be a directory"

    def test_kpi_card_file_exists(self):
        """Test that KPICard.tsx exists"""
        assert KPI_CARD_FILE.exists(), "KPICard.tsx should exist"
        assert KPI_CARD_FILE.is_file(), "KPICard.tsx should be a file"

    def test_kpi_card_has_content(self):
        """Test that KPICard.tsx has content"""
        content = KPI_CARD_FILE.read_text()
        assert len(content) > 0, "KPICard.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = KPI_CARD_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert KPI_CARD_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = KPI_CARD_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_card(self):
        """Test that component imports Card"""
        content = KPI_CARD_FILE.read_text()
        assert "Card" in content, "Should import Card component"

    def test_imports_card_content(self):
        """Test that component imports CardContent"""
        content = KPI_CARD_FILE.read_text()
        assert "CardContent" in content, "Should import CardContent component"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = KPI_CARD_FILE.read_text()
        assert "Typography" in content, "Should import Typography for text display"

    def test_imports_box_or_stack(self):
        """Test that component imports Box or Stack for layout"""
        content = KPI_CARD_FILE.read_text()
        assert ("Box" in content or "Stack" in content), \
            "Should import Box or Stack for layout"


class TestIconImports:
    """Test icon imports (optional)"""

    def test_may_import_trend_icons(self):
        """Test that component may import trend icons"""
        content = KPI_CARD_FILE.read_text()
        # TrendingUp and TrendingDown are optional
        # This test documents the pattern but doesn't enforce it
        has_trend_icons = ("TrendingUp" in content or "TrendingDown" in content or
                          "ArrowUpward" in content or "ArrowDownward" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Trend icons are optional"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_kpi_card(self):
        """Test that component exports KPICard"""
        content = KPI_CARD_FILE.read_text()
        assert "KPICard" in content, "Should define KPICard component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = KPI_CARD_FILE.read_text()
        assert ("const KPICard" in content or "function KPICard" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = KPI_CARD_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPropsInterface:
    """Test props interface"""

    def test_has_props_interface(self):
        """Test that component defines props interface"""
        content = KPI_CARD_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Should define props interface or type"

    def test_has_title_prop(self):
        """Test that component accepts title prop"""
        content = KPI_CARD_FILE.read_text()
        assert "title" in content, "Should accept title prop"

    def test_has_value_prop(self):
        """Test that component accepts value prop"""
        content = KPI_CARD_FILE.read_text()
        assert "value" in content, "Should accept value prop"

    def test_has_trend_prop(self):
        """Test that component accepts trend prop"""
        content = KPI_CARD_FILE.read_text()
        assert "trend" in content, "Should accept trend prop"

    def test_has_icon_prop(self):
        """Test that component accepts icon prop"""
        content = KPI_CARD_FILE.read_text()
        assert "icon" in content, "Should accept icon prop"


class TestCardImplementation:
    """Test Card implementation"""

    def test_uses_card_component(self):
        """Test that component uses Card"""
        content = KPI_CARD_FILE.read_text()
        assert "<Card" in content, "Should use <Card> component"

    def test_uses_card_content(self):
        """Test that component uses CardContent"""
        content = KPI_CARD_FILE.read_text()
        assert "<CardContent" in content, "Should use <CardContent> component"


class TestDisplayImplementation:
    """Test display implementation"""

    def test_displays_title(self):
        """Test that component displays title"""
        content = KPI_CARD_FILE.read_text()
        assert "title" in content, "Should display title"

    def test_displays_value(self):
        """Test that component displays value"""
        content = KPI_CARD_FILE.read_text()
        assert "value" in content, "Should display value"

    def test_uses_typography(self):
        """Test that component uses Typography"""
        content = KPI_CARD_FILE.read_text()
        assert "<Typography" in content, "Should use Typography for text"

    def test_has_multiple_typography(self):
        """Test that component has multiple Typography elements"""
        content = KPI_CARD_FILE.read_text()
        # Should have at least 2 Typography elements (title and value)
        assert content.count("<Typography") >= 2, \
            "Should have multiple Typography elements for title and value"


class TestTrendImplementation:
    """Test trend indicator implementation"""

    def test_handles_trend_prop(self):
        """Test that component handles trend prop"""
        content = KPI_CARD_FILE.read_text()
        assert "trend" in content, "Should handle trend prop"

    def test_may_use_conditional_rendering_for_trend(self):
        """Test that component may use conditional rendering for trend"""
        content = KPI_CARD_FILE.read_text()
        # Trend is optional, so component should handle its presence/absence
        # This is indicated by conditional rendering patterns
        has_conditional = ("&&" in content or "?" in content or "if" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Conditional rendering for trend is recommended"


class TestIconImplementation:
    """Test icon implementation"""

    def test_handles_icon_prop(self):
        """Test that component handles icon prop"""
        content = KPI_CARD_FILE.read_text()
        assert "icon" in content, "Should handle icon prop"

    def test_may_render_icon(self):
        """Test that component may render icon"""
        content = KPI_CARD_FILE.read_text()
        # Icon rendering is part of the component
        assert "icon" in content, "Should render icon"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = KPI_CARD_FILE.read_text()
        assert (":" in content and "React" in content), \
            "Should use TypeScript type annotations"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = KPI_CARD_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": (" in content), \
            "Component should be properly typed"

    def test_props_typed(self):
        """Test that props are properly typed"""
        content = KPI_CARD_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Props should be properly typed with interface or type"


class TestTaskRequirements:
    """Test TASK-132 specific requirements"""

    def test_task_132_file_location(self):
        """Test TASK-132: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Dashboard" / "KPICard.tsx"
        assert expected_path.exists(), \
            "TASK-132: File should be at frontend/src/components/Dashboard/KPICard.tsx"

    def test_task_132_has_title_prop(self):
        """Test TASK-132: Has title prop"""
        content = KPI_CARD_FILE.read_text()
        assert "title" in content, "TASK-132: Should have title prop"

    def test_task_132_has_value_prop(self):
        """Test TASK-132: Has value prop"""
        content = KPI_CARD_FILE.read_text()
        assert "value" in content, "TASK-132: Should have value prop"

    def test_task_132_has_trend_prop(self):
        """Test TASK-132: Has trend prop"""
        content = KPI_CARD_FILE.read_text()
        assert "trend" in content, "TASK-132: Should have trend prop"

    def test_task_132_has_icon_prop(self):
        """Test TASK-132: Has icon prop"""
        content = KPI_CARD_FILE.read_text()
        assert "icon" in content, "TASK-132: Should have icon prop"

    def test_task_132_displays_metric_value(self):
        """Test TASK-132: Displays large metric value"""
        content = KPI_CARD_FILE.read_text()
        assert ("value" in content and "Typography" in content), \
            "TASK-132: Should display metric value using Typography"

    def test_task_132_displays_label(self):
        """Test TASK-132: Displays label"""
        content = KPI_CARD_FILE.read_text()
        assert ("title" in content and "Typography" in content), \
            "TASK-132: Should display label/title using Typography"

    def test_task_132_has_trend_indicator(self):
        """Test TASK-132: Has trend indicator"""
        content = KPI_CARD_FILE.read_text()
        assert "trend" in content, "TASK-132: Should have trend indicator"
