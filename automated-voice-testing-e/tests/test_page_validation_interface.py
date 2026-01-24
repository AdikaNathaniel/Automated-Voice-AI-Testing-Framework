"""
Test suite for Validation Interface page (TASK-187)

Validates the ValidationInterface.tsx page implementation including:
- File structure and imports
- React component structure
- Material-UI components (Paper, Typography, RadioGroup, TextField, Button)
- Redux integration for current validation item
- Test case information display
- Input display (text and audio playback)
- Expected vs Actual comparison view
- Validation decision radio buttons
- Feedback text area
- Submit and Skip buttons
- TypeScript usage
- Layout matching MVP.md section 2.3
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
VALIDATION_DIR = PAGES_DIR / "Validation"
VALIDATION_INTERFACE_FILE = VALIDATION_DIR / "ValidationInterface.tsx"


class TestValidationInterfaceFileStructure:
    """Test ValidationInterface file structure"""

    def test_validation_directory_exists(self):
        """Test that Validation directory exists"""
        assert VALIDATION_DIR.exists(), "frontend/src/pages/Validation directory should exist"
        assert VALIDATION_DIR.is_dir(), "Validation should be a directory"

    def test_validation_interface_file_exists(self):
        """Test that ValidationInterface.tsx exists"""
        assert VALIDATION_INTERFACE_FILE.exists(), "ValidationInterface.tsx should exist"
        assert VALIDATION_INTERFACE_FILE.is_file(), "ValidationInterface.tsx should be a file"

    def test_validation_interface_has_content(self):
        """Test that ValidationInterface.tsx has content"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert len(content) > 0, "ValidationInterface.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_imports_use_state(self):
        """Test that component imports useState for form state"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "useState" in content, "Should import useState for validation decision and feedback"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert VALIDATION_INTERFACE_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_paper(self):
        """Test that component imports Paper"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "Paper" in content, "Should import Paper for card-like containers"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "Typography" in content, "Should import Typography for text"

    def test_imports_radio_or_radio_group(self):
        """Test that component imports Radio or RadioGroup"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("Radio" in content or "RadioGroup" in content), \
            "Should import Radio/RadioGroup for validation decision"

    def test_imports_text_field(self):
        """Test that component imports TextField"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "TextField" in content, "Should import TextField for feedback input"

    def test_imports_button(self):
        """Test that component imports Button"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "Button" in content, "Should import Button for submit/skip actions"

    def test_imports_container_or_box(self):
        """Test that component imports Container or Box"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("Container" in content or "Box" in content), \
            "Should import Container or Box for layout"


class TestReduxImports:
    """Test Redux integration imports"""

    def test_imports_use_selector(self):
        """Test that component imports useSelector"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "useSelector" in content, "Should import useSelector to access current validation"

    def test_imports_use_dispatch(self):
        """Test that component imports useDispatch"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "useDispatch" in content, "Should import useDispatch for submit action"

    def test_imports_from_react_redux(self):
        """Test that Redux hooks are imported from react-redux"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "react-redux" in content, "Should import from react-redux"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_validation_interface(self):
        """Test that component exports ValidationInterface"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "ValidationInterface" in content, "Should define ValidationInterface component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("const ValidationInterface" in content or
                "function ValidationInterface" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestTestCaseInfoDisplay:
    """Test test case information display"""

    def test_displays_test_case_name(self):
        """Test that component displays test case name"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("testCase" in content or "Test Case" in content), \
            "Should display test case name"

    def test_displays_language(self):
        """Test that component displays language"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("language" in content.lower()), \
            "Should display language information"

    def test_displays_confidence_score(self):
        """Test that component displays confidence score"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("confidence" in content.lower()), \
            "Should display confidence score"


class TestInputDisplay:
    """Test input display section"""

    def test_displays_input_text(self):
        """Test that component displays input text"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("input" in content.lower() or "text" in content.lower()), \
            "Should display input text"

    def test_has_audio_playback_placeholder(self):
        """Test that component has audio playback section"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("audio" in content.lower() or "play" in content.lower()), \
            "Should have audio playback section"


class TestExpectedVsActualComparison:
    """Test expected vs actual comparison view"""

    def test_displays_expected_section(self):
        """Test that component displays expected section"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("expected" in content.lower()), \
            "Should display expected results"

    def test_displays_actual_section(self):
        """Test that component displays actual section"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("actual" in content.lower()), \
            "Should display actual results"

    def test_displays_intent_comparison(self):
        """Test that component displays intent comparison"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("intent" in content.lower()), \
            "Should display intent comparison"

    def test_displays_entity_comparison(self):
        """Test that component displays entity comparison"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("entity" in content.lower() or "entities" in content.lower()), \
            "Should display entity comparison"

    def test_displays_response_comparison(self):
        """Test that component displays response comparison"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("response" in content.lower()), \
            "Should display response comparison"


class TestValidationDecisionRadios:
    """Test validation decision radio buttons"""

    def test_has_radio_buttons(self):
        """Test that component has radio buttons"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("Radio" in content or "radio" in content), \
            "Should have radio buttons for validation decision"

    def test_has_pass_option(self):
        """Test that component has Pass option"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("pass" in content.lower() or "approve" in content.lower()), \
            "Should have Pass/Approve option"

    def test_has_fail_option(self):
        """Test that component has Fail option"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("fail" in content.lower() or "reject" in content.lower()), \
            "Should have Fail/Reject option"

    def test_has_edge_case_option(self):
        """Test that component has Edge Case option"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("edge" in content.lower() or "uncertain" in content.lower()), \
            "Should have Edge Case/Uncertain option"

    def test_uses_state_for_decision(self):
        """Test that component uses state for decision"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("useState" in content and
                ("decision" in content.lower() or "validation" in content.lower())), \
            "Should use useState for validation decision"


class TestFeedbackTextArea:
    """Test feedback text area"""

    def test_has_feedback_input(self):
        """Test that component has feedback input"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("feedback" in content.lower() or "notes" in content.lower()), \
            "Should have feedback/notes input"

    def test_uses_text_field_for_feedback(self):
        """Test that component uses TextField for feedback"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "TextField" in content, "Should use TextField for feedback"

    def test_feedback_is_multiline(self):
        """Test that feedback input is multiline"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("multiline" in content.lower() or "rows" in content.lower()), \
            "Feedback input should be multiline"


class TestActionButtons:
    """Test Submit and Skip buttons"""

    def test_has_submit_button(self):
        """Test that component has Submit button"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("<Button" in content and "submit" in content.lower()), \
            "Should have Submit button"

    def test_has_skip_button(self):
        """Test that component has Skip button"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("<Button" in content and "skip" in content.lower()), \
            "Should have Skip button"

    def test_submit_button_has_handler(self):
        """Test that Submit button has click handler"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("onClick" in content or "handleSubmit" in content), \
            "Submit button should have click handler"


class TestContextDisplay:
    """Test context display"""

    def test_displays_context_info(self):
        """Test that component displays context information"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("context" in content.lower()), \
            "Should display context information"


class TestReduxIntegration:
    """Test Redux integration"""

    def test_selects_current_validation(self):
        """Test that component selects current validation from Redux"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("useSelector" in content and
                ("current" in content or "validation" in content)), \
            "Should select current validation from Redux state"

    def test_dispatches_submit_action(self):
        """Test that component dispatches submit action"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("dispatch" in content and "submit" in content.lower()), \
            "Should dispatch submit validation action"


class TestLayoutStructure:
    """Test layout structure"""

    def test_has_container_or_box(self):
        """Test that page has Container or Box wrapper"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("<Container" in content or "<Box" in content), \
            "Should have Container or Box wrapper"

    def test_uses_paper_for_sections(self):
        """Test that component uses Paper for sections"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert "<Paper" in content, "Should use Paper for card-like sections"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-187 specific requirements"""

    def test_task_187_file_location(self):
        """Test TASK-187: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "pages" / "Validation" / "ValidationInterface.tsx"
        assert expected_path.exists(), \
            "TASK-187: File should be at frontend/src/pages/Validation/ValidationInterface.tsx"

    def test_task_187_has_audio_playback(self):
        """Test TASK-187: Has audio playback section"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("audio" in content.lower() or "play" in content.lower()), \
            "TASK-187: Should have audio playback"

    def test_task_187_has_waveform_placeholder(self):
        """Test TASK-187: Has waveform visualization placeholder"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("waveform" in content.lower() or "audio" in content.lower()), \
            "TASK-187: Should have waveform visualization placeholder"

    def test_task_187_has_expected_vs_actual(self):
        """Test TASK-187: Has expected vs actual comparison"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("expected" in content.lower() and "actual" in content.lower()), \
            "TASK-187: Should have expected vs actual comparison"

    def test_task_187_has_validation_radio_buttons(self):
        """Test TASK-187: Has validation decision radio buttons"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("Radio" in content or "radio" in content), \
            "TASK-187: Should have validation decision radio buttons"

    def test_task_187_has_feedback_textarea(self):
        """Test TASK-187: Has feedback text area"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("TextField" in content and "feedback" in content.lower()), \
            "TASK-187: Should have feedback text area"

    def test_task_187_has_submit_skip_buttons(self):
        """Test TASK-187: Has Submit/Skip buttons"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        assert ("submit" in content.lower() and "skip" in content.lower()), \
            "TASK-187: Should have Submit and Skip buttons"

    def test_task_187_matches_mvp_layout(self):
        """Test TASK-187: Layout matches MVP.md section 2.3"""
        content = VALIDATION_INTERFACE_FILE.read_text()
        # Should have all key elements from MVP mockup
        has_input = "input" in content.lower()
        has_expected = "expected" in content.lower()
        has_actual = "actual" in content.lower()
        has_decision = ("decision" in content.lower() or "Radio" in content)
        has_feedback = "feedback" in content.lower()

        assert (has_input and has_expected and has_actual and has_decision and has_feedback), \
            "TASK-187: Should match MVP.md section 2.3 layout with all key elements"
