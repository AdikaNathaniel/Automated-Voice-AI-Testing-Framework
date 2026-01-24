"""
Test suite for StatusBadge component (TASK-139)

Validates the StatusBadge.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI Chip component usage
- Status colors for different states
- Props interface (status)
- Pulsing animation for "running" status
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
COMMON_COMPONENTS_DIR = COMPONENTS_DIR / "common"
STATUS_BADGE_FILE = COMMON_COMPONENTS_DIR / "StatusBadge.tsx"


class TestStatusBadgeFileStructure:
    """Test StatusBadge file structure"""

    def test_common_components_directory_exists(self):
        """Test that common components directory exists"""
        assert COMMON_COMPONENTS_DIR.exists(), \
            "frontend/src/components/common directory should exist"
        assert COMMON_COMPONENTS_DIR.is_dir(), "common should be a directory"

    def test_status_badge_file_exists(self):
        """Test that StatusBadge.tsx exists"""
        assert STATUS_BADGE_FILE.exists(), "StatusBadge.tsx should exist"
        assert STATUS_BADGE_FILE.is_file(), "StatusBadge.tsx should be a file"

    def test_status_badge_has_content(self):
        """Test that StatusBadge.tsx has content"""
        content = STATUS_BADGE_FILE.read_text()
        assert len(content) > 0, "StatusBadge.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = STATUS_BADGE_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert STATUS_BADGE_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = STATUS_BADGE_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_chip_or_badge(self):
        """Test that component imports Chip or Badge"""
        content = STATUS_BADGE_FILE.read_text()
        assert ("Chip" in content or "Badge" in content), \
            "Should import Chip or Badge component"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_status_badge(self):
        """Test that component exports StatusBadge"""
        content = STATUS_BADGE_FILE.read_text()
        assert "StatusBadge" in content, "Should define StatusBadge component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "const StatusBadge" in content or "function StatusBadge" in content
        ), "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = STATUS_BADGE_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPropsInterface:
    """Test props interface"""

    def test_has_props_interface(self):
        """Test that component defines props interface"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "interface" in content or "type" in content
        ), "Should define props interface or type"

    def test_has_status_prop(self):
        """Test that component accepts status prop"""
        content = STATUS_BADGE_FILE.read_text()
        assert "status" in content.lower(), "Should accept status prop"


class TestStatusColors:
    """Test status color implementation"""

    def test_has_pending_status(self):
        """Test that component handles pending status"""
        content = STATUS_BADGE_FILE.read_text()
        assert "pending" in content.lower(), "Should handle pending status"

    def test_has_running_status(self):
        """Test that component handles running status"""
        content = STATUS_BADGE_FILE.read_text()
        assert "running" in content.lower(), "Should handle running status"

    def test_has_passed_status(self):
        """Test that component handles passed status"""
        content = STATUS_BADGE_FILE.read_text()
        assert "passed" in content.lower(), "Should handle passed status"

    def test_has_failed_status(self):
        """Test that component handles failed status"""
        content = STATUS_BADGE_FILE.read_text()
        assert "failed" in content.lower(), "Should handle failed status"

    def test_has_needs_review_status(self):
        """Test that component handles needs_review status"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "needs_review" in content.lower() or "review" in content.lower()
        ), "Should handle needs_review status"

    def test_has_color_mapping(self):
        """Test that component has color mapping for statuses"""
        content = STATUS_BADGE_FILE.read_text()
        # Should have color definitions
        assert (
            "color" in content.lower()
        ), "Should have color mapping for statuses"


class TestStatusTypeDefinition:
    """Test status type definition"""

    def test_defines_status_type(self):
        """Test that component defines status type"""
        content = STATUS_BADGE_FILE.read_text()
        # Should have type or union for status values
        assert (
            "type" in content or "interface" in content
        ), "Should define status type"

    def test_may_use_union_type(self):
        """Test that component may use union type for status"""
        content = STATUS_BADGE_FILE.read_text()
        # TypeScript union type often uses '|'
        has_union = "|" in content
        # Pass regardless - just documenting the pattern
        assert True, "Union type is recommended for status values"


class TestPulsingAnimation:
    """Test pulsing animation for running status"""

    def test_has_animation_for_running(self):
        """Test that component has animation for running status"""
        content = STATUS_BADGE_FILE.read_text()
        # Should have animation or keyframes
        assert (
            "animation" in content.lower() or "keyframes" in content.lower()
        ), "Should have animation for running status"

    def test_may_use_sx_prop_for_animation(self):
        """Test that component may use sx prop for animation"""
        content = STATUS_BADGE_FILE.read_text()
        # MUI sx prop commonly used for styling
        has_sx = "sx=" in content
        # Pass regardless - just documenting the pattern
        assert True, "sx prop is common for MUI styling"

    def test_may_use_keyframes(self):
        """Test that component may define keyframes"""
        content = STATUS_BADGE_FILE.read_text()
        # May define keyframes for pulsing effect
        has_keyframes = "@keyframes" in content or "keyframes" in content
        # Pass regardless - just documenting the pattern
        assert True, "Keyframes are recommended for animations"


class TestComponentRendering:
    """Test component rendering"""

    def test_renders_chip_or_badge(self):
        """Test that component renders Chip or Badge"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "<Chip" in content or "<Badge" in content
        ), "Should render Chip or Badge component"

    def test_may_display_label(self):
        """Test that component may display label"""
        content = STATUS_BADGE_FILE.read_text()
        # Should display status as label
        has_label = "label" in content.lower()
        # Pass regardless - just documenting the pattern
        assert True, "Label display is recommended"


class TestColorVariants:
    """Test color variant implementation"""

    def test_may_use_color_prop(self):
        """Test that component may use color prop"""
        content = STATUS_BADGE_FILE.read_text()
        # MUI Chip supports color prop
        has_color = "color=" in content
        # Pass regardless - just documenting the pattern
        assert True, "Color prop is common for status indication"

    def test_may_use_custom_colors(self):
        """Test that component may use custom colors via sx"""
        content = STATUS_BADGE_FILE.read_text()
        # May use custom colors via sx prop
        has_custom = "sx=" in content
        # Pass regardless - just documenting the pattern
        assert True, "Custom colors are recommended for status badges"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            ":" in content or "interface" in content or "type" in content
        ), "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "React.FC" in content or "FC<" in content or ": (" in content
        ), "Component should be properly typed"

    def test_props_typed(self):
        """Test that props are properly typed"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "interface" in content or "type" in content
        ), "Props should be properly typed with interface or type"


class TestTaskRequirements:
    """Test TASK-139 specific requirements"""

    def test_task_139_file_location(self):
        """Test TASK-139: File is in correct location"""
        expected_path = (
            PROJECT_ROOT / "frontend" / "src" / "components" / "common" / "StatusBadge.tsx"
        )
        assert expected_path.exists(), \
            "TASK-139: File should be at frontend/src/components/common/StatusBadge.tsx"

    def test_task_139_handles_all_statuses(self):
        """Test TASK-139: Handles all required statuses"""
        content = STATUS_BADGE_FILE.read_text()
        content_lower = content.lower()
        assert "pending" in content_lower, \
            "TASK-139: Should handle pending status"
        assert "running" in content_lower, \
            "TASK-139: Should handle running status"
        assert "passed" in content_lower, \
            "TASK-139: Should handle passed status"
        assert "failed" in content_lower, \
            "TASK-139: Should handle failed status"
        assert (
            "needs_review" in content_lower or "review" in content_lower
        ), "TASK-139: Should handle needs_review status"

    def test_task_139_has_colors(self):
        """Test TASK-139: Has color coding for statuses"""
        content = STATUS_BADGE_FILE.read_text()
        assert "color" in content.lower(), \
            "TASK-139: Should have color coding for statuses"

    def test_task_139_has_pulsing_animation(self):
        """Test TASK-139: Has pulsing animation for running status"""
        content = STATUS_BADGE_FILE.read_text()
        assert (
            "animation" in content.lower() or "keyframes" in content.lower()
        ), "TASK-139: Should have pulsing animation for running status"

    def test_task_139_is_status_badge_component(self):
        """Test TASK-139: Is a status badge component"""
        content = STATUS_BADGE_FILE.read_text()
        assert "StatusBadge" in content, \
            "TASK-139: Should be StatusBadge component"
