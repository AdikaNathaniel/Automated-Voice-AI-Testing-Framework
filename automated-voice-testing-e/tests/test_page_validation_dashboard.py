"""
Test suite for Validation Dashboard page (TASK-186)

Validates the ValidationDashboard.tsx page implementation including:
- File structure and imports
- React component structure
- Material-UI components (Grid, Card, Typography, Button)
- Redux integration for validation state
- Queue stats display
- Validator stats display
- Claim button functionality
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
PAGES_DIR = FRONTEND_SRC / "pages"
VALIDATION_DIR = PAGES_DIR / "Validation"
VALIDATION_DASHBOARD_FILE = VALIDATION_DIR / "ValidationDashboard.tsx"


class TestValidationDashboardFileStructure:
    """Test ValidationDashboard file structure"""

    def test_pages_directory_exists(self):
        """Test that pages directory exists"""
        assert PAGES_DIR.exists(), "frontend/src/pages directory should exist"
        assert PAGES_DIR.is_dir(), "pages should be a directory"

    def test_validation_directory_exists(self):
        """Test that Validation directory exists"""
        assert VALIDATION_DIR.exists(), "frontend/src/pages/Validation directory should exist"
        assert VALIDATION_DIR.is_dir(), "Validation should be a directory"

    def test_validation_dashboard_file_exists(self):
        """Test that ValidationDashboard.tsx exists"""
        assert VALIDATION_DASHBOARD_FILE.exists(), "ValidationDashboard.tsx should exist"
        assert VALIDATION_DASHBOARD_FILE.is_file(), "ValidationDashboard.tsx should be a file"

    def test_validation_dashboard_has_content(self):
        """Test that ValidationDashboard.tsx has content"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert len(content) > 0, "ValidationDashboard.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_imports_use_effect(self):
        """Test that component imports useEffect for data fetching"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useEffect" in content, "Should import useEffect for fetching stats"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert VALIDATION_DASHBOARD_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_grid(self):
        """Test that component imports Grid"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Grid" in content, "Should import Grid component for layout"

    def test_imports_container_or_box(self):
        """Test that component imports Container or Box"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("Container" in content or "Box" in content), \
            "Should import Container or Box for page wrapper"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Typography" in content, "Should import Typography for text"

    def test_imports_card(self):
        """Test that component imports Card"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Card" in content, "Should import Card for stats display"

    def test_imports_button(self):
        """Test that component imports Button"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Button" in content, "Should import Button for claim action"


class TestReduxImports:
    """Test Redux integration imports"""

    def test_imports_use_selector(self):
        """Test that component imports useSelector"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useSelector" in content, "Should import useSelector to access Redux state"

    def test_imports_use_dispatch(self):
        """Test that component imports useDispatch"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useDispatch" in content, "Should import useDispatch to dispatch actions"

    def test_imports_from_react_redux(self):
        """Test that Redux hooks are imported from react-redux"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "react-redux" in content, "Should import from react-redux"

    def test_imports_validation_slice(self):
        """Test that component imports from validation slice"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("validationSlice" in content or
                "store/slices/validationSlice" in content or
                "fetchValidationStats" in content), \
            "Should import from validation slice"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_validation_dashboard(self):
        """Test that component exports ValidationDashboard"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "ValidationDashboard" in content, "Should define ValidationDashboard component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("const ValidationDashboard" in content or
                "function ValidationDashboard" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestReduxHooks:
    """Test Redux hooks usage"""

    def test_uses_use_selector(self):
        """Test that component uses useSelector"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useSelector" in content, "Should use useSelector hook"

    def test_uses_use_dispatch(self):
        """Test that component uses useDispatch"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useDispatch" in content, "Should use useDispatch hook"

    def test_selects_validation_state(self):
        """Test that component selects validation state"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("state.validation" in content or
                "validation" in content), \
            "Should select validation state from Redux"


class TestPageHeader:
    """Test page header implementation"""

    def test_has_page_title(self):
        """Test that page has title"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("Validation" in content and "Typography" in content), \
            "Should have Validation title using Typography"

    def test_uses_typography_for_title(self):
        """Test that page uses Typography component"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "<Typography" in content, "Should use Typography component"


class TestQueueStatsDisplay:
    """Test queue stats display"""

    def test_displays_queue_stats(self):
        """Test that component displays queue stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("stats" in content or "queue" in content), \
            "Should display queue stats"

    def test_uses_snake_case_counts(self):
        """Queue stats should read pending/claimed counts from backend snake_case keys"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "stats?.pending_count" in content, "Should reference pending_count"
        assert "stats?.claimed_count" in content, "Should reference claimed_count"

    def test_uses_card_for_stats(self):
        """Test that component uses Card for stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "<Card" in content, "Should use Card component for stats"

    def test_shows_total_pending(self):
        """Test that component shows total pending items"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("pending" in content.lower() and "pending_count" in content), \
            "Should show total pending items using pending_count"

    def test_shows_total_claimed(self):
        """Test that component shows total claimed items"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("claimed" in content.lower() and "claimed_count" in content), \
            "Should show total claimed items using claimed_count"

    def test_has_queue_stats_empty_state_message(self):
        """Component should include queue stats unavailable fallback text"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Queue stats unavailable" in content, \
            "Should provide queue stats empty-state message"


class TestQueueDistributionDisplay:
    """Test queue distribution widgets"""

    def test_priority_distribution_uses_snake_case(self):
        """Priority distribution list should read from priority_distribution field"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "priority_distribution" in content, \
            "Should reference priority_distribution field"

    def test_language_distribution_uses_snake_case(self):
        """Language distribution list should read from language_distribution field"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "language_distribution" in content, \
            "Should reference language_distribution field"

    def test_priority_distribution_error_message_present(self):
        """Priority card should include error fallback text"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Unable to load priority distribution data" in content, \
            "Should include priority distribution error message"

    def test_language_distribution_error_message_present(self):
        """Language card should include error fallback text"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "Unable to load language distribution data" in content, \
            "Should include language distribution error message"


class TestValidatorStatsDisplay:
    """Test validator stats display"""

    def test_displays_validator_stats(self):
        """Test that component displays validator stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("stats" in content or "validator" in content.lower()), \
            "Should display validator stats"

    def test_shows_completed_count(self):
        """Test that component shows completed validations count"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("completed" in content.lower() and "completed_count" in content), \
            "Should show completed validations using completed_count"


class TestClaimButton:
    """Test claim button implementation"""

    def test_has_claim_button(self):
        """Test that component has claim button"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("<Button" in content and "claim" in content.lower()), \
            "Should have claim button"

    def test_claim_button_has_text(self):
        """Test that claim button has text"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("Claim" in content or "claim" in content), \
            "Claim button should have text"

    def test_claim_button_has_click_handler(self):
        """Test that claim button has click handler"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("onClick" in content or "handleClaim" in content), \
            "Claim button should have click handler"


class TestGridLayout:
    """Test Grid layout implementation"""

    def test_uses_grid_component(self):
        """Test that component uses Grid"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "<Grid" in content, "Should use <Grid> component"

    def test_has_grid_container(self):
        """Test that component has Grid container"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "container" in content, "Should have Grid container"

    def test_has_grid_items(self):
        """Test that component has Grid items"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "item" in content, "Should have Grid items for stats cards"

    def test_grid_has_spacing(self):
        """Test that Grid has spacing"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "spacing" in content, "Grid should have spacing prop"


class TestLayoutStructure:
    """Test layout structure"""

    def test_has_container_or_box(self):
        """Test that page has Container or Box wrapper"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("<Container" in content or "<Box" in content), \
            "Should have Container or Box wrapper"

    def test_title_before_stats(self):
        """Test that title comes before stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        # Typography (title) should come before Card (stats)
        if "<Typography" in content and "<Card" in content:
            typography_pos = content.find("<Typography")
            card_pos = content.find("<Card")
            assert typography_pos < card_pos, \
                "Page title should come before stats cards"


class TestDataFetching:
    """Test data fetching implementation"""

    def test_uses_use_effect(self):
        """Test that component uses useEffect"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "useEffect" in content, "Should use useEffect for data fetching"

    def test_dispatches_fetch_stats(self):
        """Test that component dispatches fetch stats action"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("dispatch" in content and
                ("fetchValidationStats" in content or "stats" in content)), \
            "Should dispatch fetch validation stats action"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert (":)" in content or "React" in content), \
            "Should use TypeScript syntax"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-186 specific requirements"""

    def test_task_186_file_location(self):
        """Test TASK-186: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "pages" / "Validation" / "ValidationDashboard.tsx"
        assert expected_path.exists(), \
            "TASK-186: File should be at frontend/src/pages/Validation/ValidationDashboard.tsx"

    def test_task_186_shows_queue_stats(self):
        """Test TASK-186: Shows queue stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("queue" in content.lower() and "stats" in content), \
            "TASK-186: Should show queue stats"

    def test_task_186_shows_validator_stats(self):
        """Test TASK-186: Shows validator stats"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("stats" in content), \
            "TASK-186: Should show validator stats"

    def test_task_186_has_claim_button(self):
        """Test TASK-186: Has claim button"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("Button" in content and "claim" in content.lower()), \
            "TASK-186: Should have claim button"

    def test_task_186_uses_redux_state(self):
        """Test TASK-186: Uses Redux validation state"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert ("useSelector" in content or "validation" in content), \
            "TASK-186: Should use Redux validation state"

    def test_task_186_is_page_component(self):
        """Test TASK-186: Is a page component"""
        content = VALIDATION_DASHBOARD_FILE.read_text()
        assert "ValidationDashboard" in content, \
            "TASK-186: Should be ValidationDashboard page component"
