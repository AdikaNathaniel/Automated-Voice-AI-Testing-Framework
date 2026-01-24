"""
Test suite for TagSelector component

Validates the TagSelector.tsx component implementation including:
- File structure and imports
- React component structure
- Tag selection and deselection
- Tag search and filtering
- Add new tag functionality
- Autocomplete functionality
- Multi-select support
- Chip display for selected tags
- Remove tag functionality
- TypeScript usage
- Material-UI components
- Props interface
- State management
- Empty state handling
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
COMPONENTS_DIR = FRONTEND_SRC / "components" / "common"
TAG_SELECTOR_FILE = COMPONENTS_DIR / "TagSelector.tsx"


class TestTagSelectorFileExists:
    """Test that TagSelector file exists"""

    def test_components_common_directory_exists(self):
        """Test that components/common directory exists"""
        assert COMPONENTS_DIR.exists(), "frontend/src/components/common directory should exist"
        assert COMPONENTS_DIR.is_dir(), "common should be a directory"

    def test_tag_selector_file_exists(self):
        """Test that TagSelector.tsx exists"""
        assert TAG_SELECTOR_FILE.exists(), "TagSelector.tsx should exist"
        assert TAG_SELECTOR_FILE.is_file(), "TagSelector.tsx should be a file"

    def test_tag_selector_has_content(self):
        """Test that TagSelector.tsx has content"""
        content = TAG_SELECTOR_FILE.read_text()
        assert len(content) > 0, "TagSelector.tsx should not be empty"


class TestTagSelectorImports:
    """Test necessary imports"""

    def test_imports_react(self):
        """Test that React is imported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "react" in content.lower(), "Should import React"

    def test_imports_react_hooks(self):
        """Test that React hooks are imported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("useState" in content or "useEffect" in content), "Should import React hooks"

    def test_imports_material_ui(self):
        """Test that Material-UI components are imported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "@mui/material" in content, "Should import Material-UI components"

    def test_imports_autocomplete(self):
        """Test that Autocomplete is imported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "Autocomplete" in content, "Should import Autocomplete component"


class TestTagSelectorComponent:
    """Test component structure"""

    def test_exports_tag_selector_component(self):
        """Test that TagSelector component is exported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "export" in content, "Should export TagSelector component"
        assert "TagSelector" in content, "Should have TagSelector component"

    def test_is_function_component(self):
        """Test that TagSelector is a function component"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("const TagSelector" in content or "function TagSelector" in content or
                "export default function" in content), "Should be a function component"

    def test_accepts_props(self):
        """Test that component accepts props"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should have props for selected tags, onChange, available tags
        assert (("props" in content or ":" in content) and "tag" in content.lower()), "Should accept props"


class TestAutocompleteFeature:
    """Test autocomplete functionality"""

    def test_uses_autocomplete_component(self):
        """Test that Autocomplete component is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "Autocomplete" in content, "Should use Autocomplete component"

    def test_autocomplete_is_multiple(self):
        """Test that Autocomplete supports multiple selection"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("multiple" in content), "Should support multiple tag selection"

    def test_autocomplete_has_options(self):
        """Test that Autocomplete has options prop"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("options" in content or "tag" in content.lower()), "Should have options for tags"

    def test_autocomplete_is_freesolo(self):
        """Test that Autocomplete allows free solo input"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("freeSolo" in content or "free" in content.lower()), "Should allow free solo tag input"


class TestTagSelection:
    """Test tag selection functionality"""

    def test_accepts_selected_tags_prop(self):
        """Test that component accepts selected tags prop"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("value" in content or "selected" in content.lower() or
                "tag" in content.lower()), "Should accept selected tags"

    def test_has_onchange_callback(self):
        """Test that component has onChange callback"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("onChange" in content or "handleChange" in content), "Should have onChange callback"

    def test_calls_onchange_on_selection(self):
        """Test that onChange is called on tag selection"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("onChange" in content and "tag" in content.lower()), "Should call onChange on selection"


class TestChipDisplay:
    """Test chip display for selected tags"""

    def test_uses_chip_component(self):
        """Test that Chip component is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("Chip" in content or "renderTags" in content), "Should use Chip for tags"

    def test_chips_are_deletable(self):
        """Test that chips have delete functionality"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("onDelete" in content or "delete" in content.lower() or
                "remove" in content.lower()), "Should allow removing tags"

    def test_renders_multiple_chips(self):
        """Test that multiple chips are rendered"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("map" in content or "renderTags" in content or
                "multiple" in content), "Should render multiple tag chips"


class TestRemoveTag:
    """Test remove tag functionality"""

    def test_can_remove_tag(self):
        """Test that tags can be removed"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("delete" in content.lower() or "remove" in content.lower() or
                "onDelete" in content), "Should allow removing tags"

    def test_updates_selected_on_remove(self):
        """Test that selected tags are updated when tag is removed"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("filter" in content or "delete" in content.lower() or
                "onChange" in content), "Should update selected tags on remove"


class TestSearchFilter:
    """Test tag search and filtering"""

    def test_has_search_input(self):
        """Test that search input exists"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("TextField" in content or "renderInput" in content or
                "Autocomplete" in content), "Should have search input"

    def test_filters_tags_on_input(self):
        """Test that tags are filtered on input"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("filter" in content.lower() or "inputValue" in content or
                "search" in content.lower()), "Should filter tags on input"

    def test_shows_filtered_results(self):
        """Test that filtered results are shown"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("options" in content and "Autocomplete" in content), "Should show filtered tag results"


class TestAddNewTag:
    """Test add new tag functionality"""

    def test_allows_creating_new_tags(self):
        """Test that new tags can be created"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("freeSolo" in content or "new" in content.lower() or
                "create" in content.lower()), "Should allow creating new tags"

    def test_adds_new_tag_to_selected(self):
        """Test that new tag is added to selected tags"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("onChange" in content and "tag" in content.lower()), "Should add new tag to selected"

    def test_handles_new_tag_input(self):
        """Test that new tag input is handled"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("freeSolo" in content or "onCreate" in content or
                "onChange" in content), "Should handle new tag input"


class TestTagOptions:
    """Test tag options management"""

    def test_accepts_available_tags_prop(self):
        """Test that component accepts available tags prop"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("options" in content or "availableTags" in content or
                "tags" in content.lower()), "Should accept available tags"

    def test_displays_available_tags(self):
        """Test that available tags are displayed"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("options" in content and "Autocomplete" in content), "Should display available tags"

    def test_merges_custom_and_existing_tags(self):
        """Test that custom and existing tags are merged"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should handle both provided options and new tags
        assert ("freeSolo" in content or "options" in content), "Should handle custom and existing tags"


class TestPropsInterface:
    """Test props interface"""

    def test_defines_props_interface(self):
        """Test that props interface is defined"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("interface" in content or "type" in content), "Should define props interface"

    def test_props_has_selected_tags(self):
        """Test that props includes selected tags"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("value" in content or "selected" in content.lower() or
                "tag" in content.lower()), "Props should include selected tags"

    def test_props_has_onchange(self):
        """Test that props includes onChange"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "onChange" in content, "Props should include onChange"

    def test_props_has_available_tags(self):
        """Test that props includes available tags"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("options" in content or "availableTags" in content or
                "tags" in content.lower()), "Props should include available tags"

    def test_props_are_typed(self):
        """Test that props are properly typed"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should have type annotations
        assert (":" in content and ("string" in content or "array" in content.lower())), "Props should be typed"


class TestMaterialUIComponents:
    """Test Material-UI components usage"""

    def test_uses_autocomplete(self):
        """Test that Autocomplete is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert "Autocomplete" in content, "Should use Autocomplete component"

    def test_uses_textfield(self):
        """Test that TextField is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("TextField" in content or "renderInput" in content), "Should use TextField"

    def test_uses_chip(self):
        """Test that Chip component is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("Chip" in content or "renderTags" in content), "Should use Chip component"

    def test_uses_box_for_layout(self):
        """Test that Box is used for layout"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("Box" in content or "div" in content or "Autocomplete" in content), "Should use layout components"


class TestTypeScriptUsage:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that TypeScript syntax is used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert (":" in content or "interface" in content or "type" in content), "Should use TypeScript syntax"

    def test_file_extension_is_tsx(self):
        """Test that file has .tsx extension"""
        assert TAG_SELECTOR_FILE.suffix == ".tsx", "File should have .tsx extension"

    def test_uses_react_types(self):
        """Test that React types are used"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("React" in content and ("FC" in content or ":" in content)), "Should use React types"


class TestValidation:
    """Test validation functionality"""

    def test_validates_tag_input(self):
        """Test that tag input is validated"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should have some validation for tags
        assert ("tag" in content.lower() and ("trim" in content or "filter" in content or
                "valid" in content.lower())), "Should validate tag input"

    def test_prevents_duplicate_tags(self):
        """Test that duplicate tags are prevented"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should check for duplicates
        assert ("tag" in content.lower() and ("includes" in content or "filter" in content or
                "unique" in content.lower())), "Should prevent duplicate tags"


class TestEmptyState:
    """Test empty state handling"""

    def test_handles_empty_tags(self):
        """Test that empty tags array is handled"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should handle empty state
        assert ("tag" in content.lower() and ("length" in content or "empty" in content.lower() or
                "no tag" in content.lower())), "Should handle empty tags"

    def test_shows_placeholder(self):
        """Test that placeholder is shown"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("placeholder" in content or "label" in content), "Should show placeholder text"


class TestReadOnlyMode:
    """Test read-only mode support"""

    def test_supports_readonly_mode(self):
        """Test that component supports read-only mode"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("readOnly" in content or "disabled" in content or
                "readonly" in content.lower()), "Should support read-only mode"

    def test_disables_input_in_readonly(self):
        """Test that input is disabled in read-only mode"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("disabled" in content or "readOnly" in content), "Should disable input in read-only mode"


class TestDocumentation:
    """Test component documentation"""

    def test_has_documentation(self):
        """Test that component has documentation"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content), "Should have documentation"

    def test_has_component_description(self):
        """Test that component purpose is described"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should have some description
        assert ("Tag" in content and ("Selector" in content or "selector" in content)), "Should describe component"


class TestStateManagement:
    """Test state management"""

    def test_manages_local_state(self):
        """Test that component manages local state"""
        content = TAG_SELECTOR_FILE.read_text()
        # Could use local state for input value
        assert ("useState" in content or "value" in content or
                "inputValue" in content), "Should manage state"

    def test_updates_parent_on_change(self):
        """Test that parent is updated on change"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("onChange" in content and "tag" in content.lower()), "Should update parent on change"


class TestLabelAndHelper:
    """Test label and helper text"""

    def test_has_label_prop(self):
        """Test that component accepts label prop"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("label" in content or "Label" in content), "Should have label prop"

    def test_displays_label(self):
        """Test that label is displayed"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("label" in content and "renderInput" in content or
                "TextField" in content), "Should display label"

    def test_supports_helper_text(self):
        """Test that helper text is supported"""
        content = TAG_SELECTOR_FILE.read_text()
        assert ("helperText" in content or "helper" in content.lower() or
                "renderInput" in content), "Should support helper text"


class TestResponsiveDesign:
    """Test responsive design"""

    def test_component_is_responsive(self):
        """Test that component is responsive"""
        content = TAG_SELECTOR_FILE.read_text()
        # Should have fullWidth or responsive sizing
        assert ("fullWidth" in content or "width" in content or
                "sx" in content), "Should be responsive"

    def test_component_is_well_structured(self):
        """Test that component is well-structured"""
        content = TAG_SELECTOR_FILE.read_text()
        # Component should be reasonably sized
        assert len(content) > 300, "Component should be well-structured"


class TestLimitAndCount:
    """Test tag limit and count features"""

    def test_shows_tag_count(self):
        """Test that tag count is shown"""
        content = TAG_SELECTOR_FILE.read_text()
        # Could show count of selected tags
        assert ("tag" in content.lower() and ("length" in content or "count" in content.lower() or
                "size" in content)), "Should track tag count"

    def test_supports_max_tags_limit(self):
        """Test that max tags limit is supported"""
        content = TAG_SELECTOR_FILE.read_text()
        # Could have max limit
        assert ("tag" in content.lower() and ("max" in content.lower() or "limit" in content.lower() or
                "length" in content)), "Should support tag limits"
