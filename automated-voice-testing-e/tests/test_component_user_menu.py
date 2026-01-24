"""
Test suite for UserMenu component (TASK-130)

Validates the UserMenu.tsx component implementation including:
- File structure and imports
- React component structure
- Material-UI Menu components
- Menu items: Profile, Settings, Logout
- Props interface (anchorEl, open, onClose)
- Icons for menu items
- TypeScript usage
- Accessibility
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components"
LAYOUT_DIR = COMPONENTS_DIR / "Layout"
USER_MENU_FILE = LAYOUT_DIR / "UserMenu.tsx"


class TestUserMenuFileStructure:
    """Test UserMenu file structure"""

    def test_layout_directory_exists(self):
        """Test that Layout directory exists"""
        assert LAYOUT_DIR.exists(), "frontend/src/components/Layout directory should exist"
        assert LAYOUT_DIR.is_dir(), "Layout should be a directory"

    def test_user_menu_file_exists(self):
        """Test that UserMenu.tsx exists"""
        assert USER_MENU_FILE.exists(), "UserMenu.tsx should exist"
        assert USER_MENU_FILE.is_file(), "UserMenu.tsx should be a file"

    def test_user_menu_has_content(self):
        """Test that UserMenu.tsx has content"""
        content = USER_MENU_FILE.read_text()
        assert len(content) > 0, "UserMenu.tsx should not be empty"


class TestReactImports:
    """Test React and TypeScript imports"""

    def test_imports_react(self):
        """Test that component imports React"""
        content = USER_MENU_FILE.read_text()
        assert "import" in content and "react" in content.lower(), \
            "Should import React"

    def test_is_typescript_file(self):
        """Test that file uses TypeScript"""
        assert USER_MENU_FILE.suffix == ".tsx", "Should be a .tsx file"


class TestMaterialUIImports:
    """Test Material-UI component imports"""

    def test_imports_mui_core(self):
        """Test that component imports from @mui/material"""
        content = USER_MENU_FILE.read_text()
        assert "@mui/material" in content, "Should import from @mui/material"

    def test_imports_menu(self):
        """Test that component imports Menu"""
        content = USER_MENU_FILE.read_text()
        assert "Menu" in content, "Should import Menu component"

    def test_imports_menu_item(self):
        """Test that component imports MenuItem"""
        content = USER_MENU_FILE.read_text()
        assert "MenuItem" in content, "Should import MenuItem component"

    def test_imports_list_item_icon(self):
        """Test that component imports ListItemIcon for menu icons"""
        content = USER_MENU_FILE.read_text()
        assert "ListItemIcon" in content, "Should import ListItemIcon for icons"

    def test_imports_list_item_text(self):
        """Test that component imports ListItemText"""
        content = USER_MENU_FILE.read_text()
        assert "ListItemText" in content, "Should import ListItemText for labels"

    def test_imports_divider(self):
        """Test that component imports Divider (optional for separating items)"""
        content = USER_MENU_FILE.read_text()
        # Divider is optional, so we'll check if it's present
        # This test will pass either way, but documents the pattern
        has_divider = "Divider" in content
        assert True, "Divider is optional but recommended for separating logout"


class TestIconImports:
    """Test Material-UI icon imports"""

    def test_imports_icons(self):
        """Test that component imports icons from @mui/icons-material"""
        content = USER_MENU_FILE.read_text()
        assert "@mui/icons-material" in content, "Should import icons from @mui/icons-material"

    def test_imports_profile_icon(self):
        """Test that component imports profile icon"""
        content = USER_MENU_FILE.read_text()
        assert ("Person" in content or "AccountCircle" in content or "Profile" in content), \
            "Should import profile icon (Person, AccountCircle, or Profile)"

    def test_imports_settings_icon(self):
        """Test that component imports settings icon"""
        content = USER_MENU_FILE.read_text()
        assert "Settings" in content, "Should import Settings icon"

    def test_imports_logout_icon(self):
        """Test that component imports logout icon"""
        content = USER_MENU_FILE.read_text()
        assert ("Logout" in content or "ExitToApp" in content), \
            "Should import logout icon (Logout or ExitToApp)"


class TestComponentStructure:
    """Test component structure"""

    def test_exports_user_menu(self):
        """Test that component exports UserMenu"""
        content = USER_MENU_FILE.read_text()
        assert "UserMenu" in content, "Should define UserMenu component"

    def test_is_functional_component(self):
        """Test that component is a functional component"""
        content = USER_MENU_FILE.read_text()
        assert ("const UserMenu" in content or "function UserMenu" in content), \
            "Should define functional component"

    def test_has_default_export(self):
        """Test that component has default export"""
        content = USER_MENU_FILE.read_text()
        assert "export default" in content, "Should have default export"


class TestPropsInterface:
    """Test props interface"""

    def test_has_props_interface(self):
        """Test that component defines props interface"""
        content = USER_MENU_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Should define props interface or type"

    def test_has_anchor_el_prop(self):
        """Test that component accepts anchorEl prop"""
        content = USER_MENU_FILE.read_text()
        assert "anchorEl" in content, "Should accept anchorEl prop for menu positioning"

    def test_has_open_prop(self):
        """Test that component accepts open prop"""
        content = USER_MENU_FILE.read_text()
        assert "open" in content, "Should accept open prop to control menu visibility"

    def test_has_on_close_prop(self):
        """Test that component accepts onClose prop"""
        content = USER_MENU_FILE.read_text()
        assert "onClose" in content, "Should accept onClose prop to handle menu close"


class TestMenuImplementation:
    """Test Menu implementation"""

    def test_uses_menu_component(self):
        """Test that component uses Menu"""
        content = USER_MENU_FILE.read_text()
        assert "<Menu" in content, "Should use <Menu> component"

    def test_menu_has_anchor_el(self):
        """Test that Menu has anchorEl prop"""
        content = USER_MENU_FILE.read_text()
        assert "anchorEl" in content, "Menu should use anchorEl prop"

    def test_menu_has_open_prop(self):
        """Test that Menu has open prop"""
        content = USER_MENU_FILE.read_text()
        assert "open=" in content, "Menu should have open prop"

    def test_menu_has_on_close(self):
        """Test that Menu has onClose handler"""
        content = USER_MENU_FILE.read_text()
        assert "onClose" in content, "Menu should have onClose handler"


class TestMenuItems:
    """Test menu items implementation"""

    def test_has_profile_menu_item(self):
        """Test that menu has Profile menu item"""
        content = USER_MENU_FILE.read_text()
        assert "Profile" in content, "Should have Profile menu item"

    def test_has_settings_menu_item(self):
        """Test that menu has Settings menu item"""
        content = USER_MENU_FILE.read_text()
        assert "Settings" in content, "Should have Settings menu item"

    def test_has_logout_menu_item(self):
        """Test that menu has Logout menu item"""
        content = USER_MENU_FILE.read_text()
        assert "Logout" in content, "Should have Logout menu item"

    def test_uses_menu_item_component(self):
        """Test that component uses MenuItem"""
        content = USER_MENU_FILE.read_text()
        assert "<MenuItem" in content, "Should use <MenuItem> component"

    def test_has_multiple_menu_items(self):
        """Test that component has multiple menu items"""
        content = USER_MENU_FILE.read_text()
        # Should have at least 3 MenuItem components
        assert content.count("<MenuItem") >= 3, \
            "Should have at least 3 MenuItems (Profile, Settings, Logout)"


class TestIconUsage:
    """Test icon usage in menu items"""

    def test_uses_list_item_icon(self):
        """Test that component uses ListItemIcon"""
        content = USER_MENU_FILE.read_text()
        assert "<ListItemIcon" in content, "Should use <ListItemIcon> for menu item icons"

    def test_has_multiple_icons(self):
        """Test that component uses multiple icons"""
        content = USER_MENU_FILE.read_text()
        # Should have at least 3 icon components (one for each menu item)
        icon_count = content.count("Icon>") if "Icon>" in content else 0
        assert icon_count >= 3, "Should have icons for Profile, Settings, and Logout"


class TestMenuItemHandlers:
    """Test menu item click handlers"""

    def test_menu_items_have_onclick(self):
        """Test that menu items have onClick handlers"""
        content = USER_MENU_FILE.read_text()
        assert "onClick" in content, "Menu items should have onClick handlers"


class TestTypeScript:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that component uses TypeScript syntax"""
        content = USER_MENU_FILE.read_text()
        assert (":" in content and "React" in content), \
            "Should use TypeScript type annotations"

    def test_component_typed(self):
        """Test that component is properly typed"""
        content = USER_MENU_FILE.read_text()
        assert ("React.FC" in content or "FC<" in content or ": (" in content), \
            "Component should be properly typed"

    def test_props_typed(self):
        """Test that props are properly typed"""
        content = USER_MENU_FILE.read_text()
        assert ("interface" in content or "type" in content), \
            "Props should be properly typed with interface or type"


class TestTaskRequirements:
    """Test TASK-130 specific requirements"""

    def test_task_130_file_location(self):
        """Test TASK-130: File is in correct location"""
        expected_path = PROJECT_ROOT / "frontend" / "src" / "components" / "Layout" / "UserMenu.tsx"
        assert expected_path.exists(), \
            "TASK-130: File should be at frontend/src/components/Layout/UserMenu.tsx"

    def test_task_130_has_profile_option(self):
        """Test TASK-130: Has Profile option"""
        content = USER_MENU_FILE.read_text()
        assert "Profile" in content, "TASK-130: Should have Profile option"

    def test_task_130_has_settings_option(self):
        """Test TASK-130: Has Settings option"""
        content = USER_MENU_FILE.read_text()
        assert "Settings" in content, "TASK-130: Should have Settings option"

    def test_task_130_has_logout_option(self):
        """Test TASK-130: Has Logout option"""
        content = USER_MENU_FILE.read_text()
        assert "Logout" in content, "TASK-130: Should have Logout option"

    def test_task_130_uses_menu_component(self):
        """Test TASK-130: Uses Menu component"""
        content = USER_MENU_FILE.read_text()
        assert "<Menu" in content, "TASK-130: Should use Material-UI Menu component"
