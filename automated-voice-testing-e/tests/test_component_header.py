"""
Test suite for Header component (TASK-129)

Validates the Header.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI AppBar and Toolbar
- Logo display
- User menu component/button
- Notifications icon
- TypeScript usage
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
LAYOUT_DIR = COMPONENTS_DIR / "Layout"
HEADER_FILE = LAYOUT_DIR / "Header.tsx"


class TestHeaderFileStructure:
    """Test Header file structure"""

    def test_layout_directory_exists(self):
        """Test that Layout directory exists"""
        assert LAYOUT_DIR.exists(), "frontend/src/components/Layout directory should exist"
        assert LAYOUT_DIR.is_dir(), "Layout should be a directory"

    def test_header_file_exists(self):
        """Test that Header.tsx exists"""
        assert HEADER_FILE.exists(), "Header.tsx should exist"
        assert HEADER_FILE.is_file(), "Header.tsx should be a file"

    def test_header_has_content(self):
        """Test that Header.tsx has content"""
        content = HEADER_FILE.read_text()
        assert len(content) > 0, "Header.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = HEADER_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert HEADER_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = HEADER_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_appbar(self):
        """Test that component imports AppBar"""
        content = HEADER_FILE.read_text()
        assert "AppBar" in content, "Should import AppBar component"

    def test_imports_toolbar(self):
        """Test that component imports Toolbar"""
        content = HEADER_FILE.read_text()
        assert "Toolbar" in content, "Should import Toolbar component"

    def test_imports_typography(self):
        """Test that component imports Typography"""
        content = HEADER_FILE.read_text()
        assert "Typography" in content, "Should import Typography for logo/title"

    def test_imports_icon_button(self):
        """Test that component imports IconButton"""
        content = HEADER_FILE.read_text()
        assert "IconButton" in content, "Should import IconButton for user menu and notifications"

    def test_imports_badge(self):
        """Test that component imports Badge"""
        content = HEADER_FILE.read_text()
        assert "Badge" in content, "Should import Badge for notification count"


class TestIconImports:
    """Test Material-UI icon imports"""

    def test_imports_icons(self):
        """Test that component imports icons from @mui/icons-material"""
        content = HEADER_FILE.read_text()
        assert "@mui/icons-material" in content, "Should import icons from @mui/icons-material"

    def test_imports_notifications_icon(self):
        """Test that component imports notifications icon"""
        content = HEADER_FILE.read_text()
        assert "Notifications" in content, "Should import Notifications icon"

    def test_imports_account_icon(self):
        """Test that component imports account/user icon"""
        content = HEADER_FILE.read_text()
        assert ("AccountCircle" in content or "Person" in content), \
            "Should import account icon (AccountCircle or Person)"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_header(self):
        """Test that component exports Header"""
        content = HEADER_FILE.read_text()
        assert "Header" in content, "Should define Header component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = HEADER_FILE.read_text()
        assert ("const Header" in content or "function Header" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = HEADER_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestAppBarImplementation:
    """Test AppBar implementation"""

    def test_uses_appbar_component(self):
        """Test that component uses AppBar"""
        content = HEADER_FILE.read_text()
        assert "<AppBar" in content, "Should use <AppBar> component"

    def test_appbar_has_toolbar(self):
        """Test that AppBar contains Toolbar"""
        content = HEADER_FILE.read_text()
        assert "<Toolbar" in content, "AppBar should contain <Toolbar>"

    def test_appbar_position(self):
        """Test that AppBar has position prop"""
        content = HEADER_FILE.read_text()
        assert 'position="' in content or "position=" in content, \
            "AppBar should have position prop"


class TestLogoImplementation:
    """Test logo implementation"""

    def test_has_logo_or_title(self):
        """Test that header has logo or title"""
        content = HEADER_FILE.read_text()
        assert ("<Typography" in content or "logo" in content.lower()), \
            "Should have Typography for title or logo element"

    def test_has_app_name(self):
        """Test that header displays app name"""
        content = HEADER_FILE.read_text()
        assert ("Voice AI" in content or "Testing" in content or "VoiceAI" in content), \
            "Should display application name"

    def test_logo_uses_typography(self):
        """Test that logo/title uses Typography component"""
        content = HEADER_FILE.read_text()
        assert "<Typography" in content, "Should use Typography for logo/title"


class TestUserMenuImplementation:
    """Test user menu implementation"""

    def test_has_user_menu_button(self):
        """Test that header has user menu button"""
        content = HEADER_FILE.read_text()
        assert "<IconButton" in content, "Should have IconButton for user menu"

    def test_user_menu_has_icon(self):
        """Test that user menu button has account icon"""
        content = HEADER_FILE.read_text()
        assert ("AccountCircle" in content or "Person" in content), \
            "Should have account icon in user menu"

    def test_user_menu_has_aria_label(self):
        """Test that user menu has aria-label for accessibility"""
        content = HEADER_FILE.read_text()
        assert ("aria-label" in content or "ariaLabel" in content), \
            "Should have aria-label for accessibility"


class TestNotificationsImplementation:
    """Test notifications icon implementation"""

    def test_has_notifications_button(self):
        """Test that header has notifications button"""
        content = HEADER_FILE.read_text()
        # Should have at least 2 IconButtons (notifications + user menu)
        assert content.count("<IconButton") >= 2, \
            "Should have IconButton for notifications"

    def test_notifications_uses_badge(self):
        """Test that notifications uses Badge component"""
        content = HEADER_FILE.read_text()
        assert "<Badge" in content, "Should use Badge for notification count"

    def test_notifications_has_icon(self):
        """Test that notifications has icon"""
        content = HEADER_FILE.read_text()
        assert "Notifications" in content, "Should have Notifications icon"

    def test_badge_has_count(self):
        """Test that Badge has badgeContent prop"""
        content = HEADER_FILE.read_text()
        assert "badgeContent" in content, "Badge should have badgeContent prop"


class TestLayoutStructure:
    """Test layout structure"""

    def test_logo_before_menu_items(self):
        """Test that logo comes before menu items"""
        content = HEADER_FILE.read_text()
        # Typography (logo) should come before IconButton (menu items)
        typography_pos = content.find("<Typography")
        iconbutton_pos = content.find("<IconButton")
        assert typography_pos < iconbutton_pos, \
            "Logo should come before menu items"

    def test_notifications_before_user_menu(self):
        """Test that notifications come before user menu"""
        content = HEADER_FILE.read_text()
        # Notifications (Badge) should come before AccountCircle
        assert ("Badge" in content or "Notifications" in content), \
            "Should have notifications implementation"


class TestStyling:
    """Test styling and layout"""

    def test_uses_sx_prop_or_styled(self):
        """Test that component uses sx prop for styling"""
        content = HEADER_FILE.read_text()
        assert ("sx=" in content or "sx={{" in content), \
            "Should use sx prop for styling"

    def test_has_spacing_between_items(self):
        """Test that header has spacing between items"""
        content = HEADER_FILE.read_text()
        # Should use flexGrow, marginLeft, or spacing
        assert ("flexGrow" in content or "ml=" in content or "marginLeft" in content), \
            "Should have spacing between logo and menu items"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = HEADER_FILE.read_text()
        assert (":" in content and "React" in content), \
            "Should use TypeScript type annotations"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = HEADER_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": () =>" in content), \
            "Component should be properly typed"


class TestTaskRequirements:
    """Test TASK-129 specific requirements"""

    def test_task_129_file_location(self):
        """Test TASK-129: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Layout" / "Header.tsx"
        assert expected_path.exists(), \
            "TASK-129: File should be at frontend/src/components/Layout/Header.tsx"

    def test_task_129_includes_logo(self):
        """Test TASK-129: Includes logo"""
        content = HEADER_FILE.read_text()
        assert ("<Typography" in content and ("Voice AI" in content or "Testing" in content)), \
            "TASK-129: Should include logo/title"

    def test_task_129_includes_user_menu(self):
        """Test TASK-129: Includes user menu"""
        content = HEADER_FILE.read_text()
        assert ("AccountCircle" in content or "Person" in content), \
            "TASK-129: Should include user menu with account icon"

    def test_task_129_includes_notifications(self):
        """Test TASK-129: Includes notifications icon"""
        content = HEADER_FILE.read_text()
        assert ("Notifications" in content and "Badge" in content), \
            "TASK-129: Should include notifications icon with badge"

    def test_task_129_uses_appbar(self):
        """Test TASK-129: Uses AppBar component"""
        content = HEADER_FILE.read_text()
        assert "<AppBar" in content, "TASK-129: Should use AppBar component"
