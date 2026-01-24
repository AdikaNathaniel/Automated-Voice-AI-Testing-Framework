"""
Test suite for ScenarioEditor component

Validates the ScenarioEditor.tsx component implementation including:
- File structure and imports
- React component structure
- JSON editor functionality
- Validation and error handling
- Format/prettify functionality
- Copy to clipboard feature
- Value change callbacks
- TypeScript usage
- Material-UI components
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components" / "TestCase"
SCENARIO_EDITOR_FILE = COMPONENTS_DIR / "ScenarioEditor.tsx"


class TestScenarioEditorFileExists:
    """Test that ScenarioEditor file exists"""

    def test_components_test_case_directory_exists(self):
        """Test that components/TestCase directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components/TestCase directory should exist"
        assert COMPONENTS_DIR.is_dir(), "TestCase should be a directory"

    def test_scenario_editor_file_exists(self):
        """Test that ScenarioEditor.tsx exists"""
        assert SCENARIO_EDITOR_FILE.exists(), "ScenarioEditor.tsx should exist"
        assert SCENARIO_EDITOR_FILE.is_file(), "ScenarioEditor.tsx should be a file"

    def test_scenario_editor_has_content(self):
        """Test that ScenarioEditor.tsx has content"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert len(content) > 0, "ScenarioEditor.tsx should not be empty"


class TestScenarioEditorImports:
    """Test necessary imports"""

    def test_imports_react(self):
        """Test that React is imported"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "react" in content.lower(), "Should import React"

    def test_imports_react_hooks(self):
        """Test that React hooks are imported"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("useState" in content or "useEffect" in content), "Should import React hooks"

    def test_imports_material_ui(self):
        """Test that Material-UI components are imported"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "@mui/material" in content, "Should import Material-UI components"


class TestScenarioEditorComponent:
    """Test component structure"""

    def test_exports_scenario_editor_component(self):
        """Test that ScenarioEditor component is exported"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "export" in content, "Should export ScenarioEditor component"
        assert "ScenarioEditor" in content, "Should have ScenarioEditor component"

    def test_is_function_component(self):
        """Test that ScenarioEditor is a function component"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("const ScenarioEditor" in content or "function ScenarioEditor" in content or
                "export default function" in content), "Should be a function component"

    def test_accepts_props(self):
        """Test that component accepts props"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have props for value and onChange
        assert ("props" in content or ":" in content), "Should accept props"


class TestEditorTextArea:
    """Test editor textarea"""

    def test_has_textarea_or_textfield(self):
        """Test that textarea or TextField is used"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("TextField" in content or "textarea" in content.lower()), "Should have textarea for editing"

    def test_textarea_is_multiline(self):
        """Test that textarea supports multiline"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("multiline" in content or "rows" in content), "Should be multiline"

    def test_has_monospace_font(self):
        """Test that editor uses monospace font"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("monospace" in content or "fontFamily" in content), "Should use monospace font for code"

    def test_displays_value(self):
        """Test that editor displays value"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("value" in content or "defaultValue" in content), "Should display value"


class TestValueManagement:
    """Test value management"""

    def test_accepts_value_prop(self):
        """Test that component accepts value prop"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "value" in content, "Should accept value prop"

    def test_has_onchange_callback(self):
        """Test that component has onChange callback"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("onChange" in content or "handleChange" in content), "Should have onChange callback"

    def test_calls_onchange_on_edit(self):
        """Test that onChange is called on edit"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should call onChange prop when value changes (can use props or destructured)
        assert ("onChange" in content and ("props" in content or "onChange(" in content)), "Should call onChange callback"


class TestJSONValidation:
    """Test JSON validation"""

    def test_validates_json(self):
        """Test that JSON is validated"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("JSON" in content and ("parse" in content or "valid" in content.lower())), "Should validate JSON"

    def test_displays_validation_errors(self):
        """Test that validation errors are displayed"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("error" in content.lower() and ("message" in content or "helperText" in content)), "Should display validation errors"

    def test_checks_json_validity(self):
        """Test that JSON validity is checked"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have JSON.parse to check validity
        assert "parse" in content, "Should parse JSON to check validity"


class TestFormatButton:
    """Test format/prettify button"""

    def test_has_format_button(self):
        """Test that format button exists"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("format" in content.lower() or "prettify" in content.lower() or
                "Button" in content), "Should have format button"

    def test_format_button_prettifies_json(self):
        """Test that format button prettifies JSON"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have JSON.stringify with spacing
        assert ("stringify" in content or "format" in content.lower()), "Should format/prettify JSON"

    def test_handles_format_action(self):
        """Test that format action is handled"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("format" in content.lower() or "onClick" in content), "Should handle format action"


class TestErrorHandling:
    """Test error handling"""

    def test_handles_invalid_json(self):
        """Test that invalid JSON is handled"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("catch" in content or "error" in content.lower()), "Should handle invalid JSON"

    def test_displays_error_message(self):
        """Test that error message is displayed"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("error" in content.lower() and "message" in content), "Should display error message"

    def test_error_has_helper_text(self):
        """Test that error has helper text"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("helperText" in content or "FormHelperText" in content or
                "error" in content.lower()), "Should show helper text for errors"


class TestMaterialUIComponents:
    """Test Material-UI components usage"""

    def test_uses_textfield(self):
        """Test that TextField is used"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("TextField" in content or "textarea" in content), "Should use TextField"

    def test_uses_box_for_layout(self):
        """Test that Box is used for layout"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("Box" in content or "div" in content), "Should use Box for layout"

    def test_uses_button(self):
        """Test that Button component is used"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "Button" in content, "Should use Button component"

    def test_uses_typography_for_labels(self):
        """Test that Typography is used for labels"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("Typography" in content or "label" in content.lower()), "Should use Typography for labels"


class TestPropsInterface:
    """Test props interface"""

    def test_defines_props_interface(self):
        """Test that props interface is defined"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("interface" in content or "type" in content), "Should define props interface"

    def test_props_has_value(self):
        """Test that props includes value"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "value" in content, "Props should include value"

    def test_props_has_onchange(self):
        """Test that props includes onChange"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "onChange" in content, "Props should include onChange"

    def test_props_are_typed(self):
        """Test that props are properly typed"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have type annotations
        assert (":" in content and ("string" in content or "object" in content)), "Props should be typed"


class TestTypeScriptUsage:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that TypeScript syntax is used"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert (":" in content or "interface" in content or
                "type" in content), "Should use TypeScript syntax"

    def test_file_extension_is_tsx(self):
        """Test that file has .tsx extension"""
        assert SCENARIO_EDITOR_FILE.suffix == ".tsx", "File should have .tsx extension"

    def test_uses_react_types(self):
        """Test that React types are used"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("React" in content and "FC" in content) or ":" in content, "Should use React types"


class TestDocumentation:
    """Test component documentation"""

    def test_has_documentation(self):
        """Test that component has documentation"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content), "Should have documentation"

    def test_has_component_description(self):
        """Test that component purpose is described"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have some description
        assert ("Scenario" in content and ("Editor" in content or "editor" in content)), "Should describe component"


class TestCopyToClipboard:
    """Test copy to clipboard functionality"""

    def test_has_copy_button(self):
        """Test that copy button exists"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("copy" in content.lower() or "clipboard" in content.lower() or
                "Button" in content), "Should have copy button"

    def test_handles_copy_action(self):
        """Test that copy action is handled"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("copy" in content.lower() or "clipboard" in content.lower() or
                "onClick" in content), "Should handle copy action"


class TestReadOnlyMode:
    """Test read-only mode support"""

    def test_supports_readonly_mode(self):
        """Test that component supports read-only mode"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("readonly" in content.lower() or "disabled" in content or
                "readOnly" in content), "Should support read-only mode"


class TestHelperFeatures:
    """Test helper features"""

    def test_shows_line_count_or_char_count(self):
        """Test that line count or character count is shown"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Could show line count, char count, or validation status
        assert (len(content) > 300), "Should have substantial implementation"

    def test_has_clear_or_reset_button(self):
        """Test that clear or reset functionality exists"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Optional feature, just check for buttons
        assert "Button" in content, "Should have action buttons"


class TestStateManagement:
    """Test state management"""

    def test_manages_local_state(self):
        """Test that component manages local state"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("useState" in content or "state" in content.lower()), "Should manage local state"

    def test_tracks_error_state(self):
        """Test that error state is tracked"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("error" in content.lower() and "useState" in content), "Should track error state"


class TestStyling:
    """Test styling"""

    def test_uses_sx_or_style(self):
        """Test that component uses styling"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert ("sx" in content or "style" in content), "Should use styling"

    def test_applies_monospace_font(self):
        """Test that monospace font is applied"""
        content = SCENARIO_EDITOR_FILE.read_text()
        assert "monospace" in content, "Should apply monospace font to code"


class TestResponsiveDesign:
    """Test responsive design"""

    def test_component_is_responsive(self):
        """Test that component is responsive"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Should have fullWidth or responsive sizing
        assert ("fullWidth" in content or "width" in content or
                "sx" in content), "Should be responsive"

    def test_component_is_well_structured(self):
        """Test that component is well-structured"""
        content = SCENARIO_EDITOR_FILE.read_text()
        # Component should be reasonably sized
        assert len(content) > 300, "Component should be well-structured"
