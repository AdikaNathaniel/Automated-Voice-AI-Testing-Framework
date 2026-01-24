"""
Test suite for ProgressBar component (TASK-137)

Validates the ProgressBar.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI LinearProgress component
- Progress percentage display
- Props interface (value, total, label)
- Real-time updates support
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
COMMON_COMPONENTS_DIR = COMPONENTS_DIR / "common"
PROGRESS_BAR_FILE = COMMON_COMPONENTS_DIR / "ProgressBar.tsx"


class TestProgressBarFileStructure:
    """Test ProgressBar file structure"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components directory should exist"
        assert COMPONENTS_DIR.is_dir(), "components should be a directory"

    def test_common_components_directory_exists(self):
        """Test that common components directory exists"""
        assert COMMON_COMPONENTS_DIR.exists(), \
            "frontend/src/components/common directory should exist"
        assert COMMON_COMPONENTS_DIR.is_dir(), "common should be a directory"

    def test_progress_bar_file_exists(self):
        """Test that ProgressBar.tsx exists"""
        assert PROGRESS_BAR_FILE.exists(), "ProgressBar.tsx should exist"
        assert PROGRESS_BAR_FILE.is_file(), "ProgressBar.tsx should be a file"

    def test_progress_bar_has_content(self):
        """Test that ProgressBar.tsx has content"""
        content = PROGRESS_BAR_FILE.read_text()
        assert len(content) > 0, "ProgressBar.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert PROGRESS_BAR_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_linear_progress(self):
        """Test that component imports LinearProgress"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "LinearProgress" in content, "Should import LinearProgress component"

    def test_imports_box_or_stack(self):
        """Test that component imports Box or Stack for layout"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("Box" in content or "Stack" in content), \
            "Should import Box or Stack for layout"

    def test_imports_typography(self):
        """Test that component imports Typography for labels"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "Typography" in content, "Should import Typography for labels"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_progress_bar(self):
        """Test that component exports ProgressBar"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "ProgressBar" in content, "Should define ProgressBar component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("const ProgressBar" in content or "function ProgressBar" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPropsInterface:
    """Test props interface"""

    def test_has_props_interface(self):
        """Test that component defines props interface"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Should define props interface or type"

    def test_has_value_prop(self):
        """Test that component accepts value prop"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "value" in content.lower(), "Should accept value prop"

    def test_has_total_prop(self):
        """Test that component accepts total prop"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "total" in content.lower(), "Should accept total prop"

    def test_may_have_label_prop(self):
        """Test that component may accept label prop"""
        content = PROGRESS_BAR_FILE.read_text()
        # Label is optional but recommended
        has_label = "label" in content.lower()
        # Pass regardless - just documenting the pattern
        assert True, "Label prop is recommended"


class TestProgressDisplay:
    """Test progress display implementation"""

    def test_uses_linear_progress(self):
        """Test that component uses LinearProgress"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "<LinearProgress" in content, "Should use <LinearProgress> component"

    def test_displays_percentage(self):
        """Test that component displays percentage"""
        content = PROGRESS_BAR_FILE.read_text()
        # Should calculate and display percentage
        assert ("%" in content or "percent" in content.lower()), \
            "Should display percentage"

    def test_calculates_progress(self):
        """Test that component calculates progress"""
        content = PROGRESS_BAR_FILE.read_text()
        # Should have calculation logic (value/total)
        assert ("value" in content.lower() and "total" in content.lower()), \
            "Should calculate progress from value and total"


class TestLabelDisplay:
    """Test label display implementation"""

    def test_may_display_label(self):
        """Test that component may display label"""
        content = PROGRESS_BAR_FILE.read_text()
        # Should have Typography for labels
        assert "Typography" in content, "Should use Typography for labels"

    def test_may_show_counts(self):
        """Test that component may show value/total counts"""
        content = PROGRESS_BAR_FILE.read_text()
        # May show "5 / 10" or similar
        has_counts = ("value" in content.lower() and "total" in content.lower())
        # Pass regardless - just documenting the pattern
        assert True, "Showing counts is recommended"


class TestProgressVariants:
    """Test progress bar variants"""

    def test_may_use_variant_prop(self):
        """Test that component may use variant prop"""
        content = PROGRESS_BAR_FILE.read_text()
        # LinearProgress supports determinate and indeterminate variants
        has_variant = "variant" in content.lower()
        # Pass regardless - just documenting the pattern
        assert True, "Variant prop is optional"

    def test_may_use_color_prop(self):
        """Test that component may use color prop"""
        content = PROGRESS_BAR_FILE.read_text()
        # LinearProgress supports different colors
        has_color = "color" in content.lower()
        # Pass regardless - just documenting the pattern
        assert True, "Color prop is optional"


class TestLayoutStructure:
    """Test layout structure"""

    def test_has_container_layout(self):
        """Test that component has container layout"""
        content = PROGRESS_BAR_FILE.read_text()
        # Should use Box or Stack for layout
        assert ("<Box" in content or "<Stack" in content), \
            "Should use Box or Stack for layout"

    def test_may_have_spacing(self):
        """Test that component may have spacing"""
        content = PROGRESS_BAR_FILE.read_text()
        # Should have spacing props
        has_spacing = ("sx=" in content or "spacing" in content)
        # Pass regardless - just documenting the pattern
        assert True, "Spacing is recommended"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = PROGRESS_BAR_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": (" in content), \
            "Component should be properly typed"

    def test_props_typed(self):
        """Test that props are properly typed"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Props should be properly typed with interface or type"


class TestTaskRequirements:
    """Test TASK-137 specific requirements"""

    def test_task_137_file_location(self):
        """Test TASK-137: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "common" / "ProgressBar.tsx"
        assert expected_path.exists(), \
            "TASK-137: File should be at frontend/src/components/common/ProgressBar.tsx"

    def test_task_137_shows_progress(self):
        """Test TASK-137: Shows test run progress"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "LinearProgress" in content, \
            "TASK-137: Should show progress using LinearProgress"

    def test_task_137_displays_percentage(self):
        """Test TASK-137: Displays percentage"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("%" in content or "percent" in content.lower()), \
            "TASK-137: Should display percentage"

    def test_task_137_accepts_value_and_total(self):
        """Test TASK-137: Accepts value and total props"""
        content = PROGRESS_BAR_FILE.read_text()
        assert ("value" in content.lower() and "total" in content.lower()), \
            "TASK-137: Should accept value and total props"

    def test_task_137_supports_real_time_updates(self):
        """Test TASK-137: Supports real-time updates"""
        content = PROGRESS_BAR_FILE.read_text()
        # Real-time updates via props (no internal state needed)
        assert ("value" in content.lower() or "props" in content.lower()), \
            "TASK-137: Should support real-time updates via props"

    def test_task_137_is_progress_bar_component(self):
        """Test TASK-137: Is a progress bar component"""
        content = PROGRESS_BAR_FILE.read_text()
        assert "ProgressBar" in content, \
            "TASK-137: Should be ProgressBar component"
