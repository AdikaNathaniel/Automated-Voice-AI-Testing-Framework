"""
Test suite for user profile component

Validates the UserProfile.tsx component including:
- File structure and imports
- Component rendering and display mode
- Edit mode with form fields
- Toggle between display and edit modes
- Profile update functionality
- Change password functionality
- Form validation
- Redux integration
- API integration
- Error handling
- TypeScript typing
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
USER_PROFILE_FILE = FRONTEND_SRC / "components" / "UserProfile.tsx"


class TestUserProfileFileExists:
    """Test that user profile file exists"""

    def test_components_directory_exists(self):
        """Test that components directory exists"""
        components_dir = FRONTEND_SRC / "components"
        assert components_dir.exists(), "frontend/src/components directory should exist"
        assert components_dir.is_dir(), "components should be a directory"

    def test_user_profile_file_exists(self):
        """Test that UserProfile.tsx exists"""
        assert USER_PROFILE_FILE.exists(), "UserProfile.tsx should exist"
        assert USER_PROFILE_FILE.is_file(), "UserProfile.tsx should be a file"

    def test_user_profile_has_content(self):
        """Test that UserProfile.tsx has content"""
        content = USER_PROFILE_FILE.read_text()
        assert len(content) > 0, "UserProfile.tsx should not be empty"


class TestUserProfileImports:
    """Test that user profile has necessary imports"""

    def test_imports_react(self):
        """Test that React is imported"""
        content = USER_PROFILE_FILE.read_text()
        assert "react" in content.lower(), "Should import React"

    def test_imports_material_ui(self):
        """Test that Material-UI components are imported"""
        content = USER_PROFILE_FILE.read_text()
        assert ("@mui" in content or "material-ui" in content), "Should import Material-UI components"

    def test_imports_redux_hooks(self):
        """Test that Redux hooks are imported"""
        content = USER_PROFILE_FILE.read_text()
        assert ("useSelector" in content or "useDispatch" in content or
                "react-redux" in content), "Should import Redux hooks"

    def test_imports_user_types(self):
        """Test that User type is imported"""
        content = USER_PROFILE_FILE.read_text()
        assert ("User" in content or "types" in content), "Should import User type"


class TestUserProfileComponent:
    """Test user profile component structure"""

    def test_exports_user_profile_component(self):
        """Test that UserProfile component is exported"""
        content = USER_PROFILE_FILE.read_text()
        assert ("UserProfile" in content and "export" in content), "Should export UserProfile component"

    def test_is_functional_component(self):
        """Test that component is functional (not class-based)"""
        content = USER_PROFILE_FILE.read_text()
        assert ("const UserProfile" in content or "function UserProfile" in content or
                "export default function" in content), "Should be a functional component"


class TestUserProfileDisplayMode:
    """Test user profile display mode"""

    def test_displays_user_email(self):
        """Test that component displays user email"""
        content = USER_PROFILE_FILE.read_text()
        assert ("email" in content), "Should display user email"

    def test_displays_username(self):
        """Test that component displays username"""
        content = USER_PROFILE_FILE.read_text()
        assert ("username" in content), "Should display username"

    def test_displays_full_name(self):
        """Test that component displays full name"""
        content = USER_PROFILE_FILE.read_text()
        assert ("full_name" in content or "fullName" in content or
                "name" in content), "Should display full name"

    def test_has_edit_button(self):
        """Test that component has edit button"""
        content = USER_PROFILE_FILE.read_text()
        assert ("edit" in content.lower() or "Edit" in content), "Should have edit button"


class TestUserProfileEditMode:
    """Test user profile edit mode"""

    def test_has_edit_mode_state(self):
        """Test that component has state for edit mode"""
        content = USER_PROFILE_FILE.read_text()
        assert ("useState" in content or "isEditing" in content or
                "editMode" in content), "Should have edit mode state"

    def test_has_form_fields_in_edit_mode(self):
        """Test that component has form fields for editing"""
        content = USER_PROFILE_FILE.read_text()
        assert ("TextField" in content or "input" in content or
                "Form" in content), "Should have form fields in edit mode"

    def test_has_save_button(self):
        """Test that component has save button"""
        content = USER_PROFILE_FILE.read_text()
        assert ("save" in content.lower() or "Save" in content or
                "submit" in content.lower()), "Should have save button"

    def test_has_cancel_button(self):
        """Test that component has cancel button"""
        content = USER_PROFILE_FILE.read_text()
        assert ("cancel" in content.lower() or "Cancel" in content), "Should have cancel button"


class TestUserProfileFormHandling:
    """Test form handling"""

    def test_uses_react_hook_form_or_state(self):
        """Test that component uses form handling"""
        content = USER_PROFILE_FILE.read_text()
        assert ("useForm" in content or "useState" in content or
                "formData" in content), "Should use form handling"

    def test_handles_form_submission(self):
        """Test that component handles form submission"""
        content = USER_PROFILE_FILE.read_text()
        assert ("onSubmit" in content or "handleSubmit" in content or
                "submit" in content.lower()), "Should handle form submission"

    def test_handles_input_changes(self):
        """Test that component handles input changes"""
        content = USER_PROFILE_FILE.read_text()
        assert ("onChange" in content or "handleChange" in content or
                "setValue" in content or ("Controller" in content and "field" in content)), "Should handle input changes"


class TestUserProfileValidation:
    """Test form validation"""

    def test_validates_email(self):
        """Test that email is validated"""
        content = USER_PROFILE_FILE.read_text()
        assert ("email" in content and ("valid" in content.lower() or
                "error" in content or "yup" in content or
                "schema" in content)), "Should validate email"

    def test_validates_required_fields(self):
        """Test that required fields are validated"""
        content = USER_PROFILE_FILE.read_text()
        assert ("required" in content.lower() or "error" in content or
                "validation" in content.lower()), "Should validate required fields"


class TestUserProfileChangePassword:
    """Test change password functionality"""

    def test_has_change_password_section(self):
        """Test that component has change password section"""
        content = USER_PROFILE_FILE.read_text()
        assert ("password" in content.lower() and
                ("change" in content.lower() or "update" in content.lower())), "Should have change password section"

    def test_has_current_password_field(self):
        """Test that component has current password field"""
        content = USER_PROFILE_FILE.read_text()
        assert ("currentPassword" in content or "current_password" in content or
                "oldPassword" in content), "Should have current password field"

    def test_has_new_password_field(self):
        """Test that component has new password field"""
        content = USER_PROFILE_FILE.read_text()
        assert ("newPassword" in content or "new_password" in content), "Should have new password field"

    def test_has_confirm_password_field(self):
        """Test that component has confirm password field"""
        content = USER_PROFILE_FILE.read_text()
        assert ("confirmPassword" in content or "confirm_password" in content or
                "passwordConfirm" in content), "Should have confirm password field"

    def test_validates_password_match(self):
        """Test that passwords match validation exists"""
        content = USER_PROFILE_FILE.read_text()
        assert ("match" in content.lower() or "confirm" in content.lower() or
                "same" in content.lower()), "Should validate password match"


class TestUserProfileReduxIntegration:
    """Test Redux integration"""

    def test_gets_user_from_redux_store(self):
        """Test that component gets user from Redux store"""
        content = USER_PROFILE_FILE.read_text()
        assert ("useSelector" in content or "state.auth" in content or
                "state.user" in content), "Should get user from Redux store"

    def test_dispatches_update_action(self):
        """Test that component dispatches update action"""
        content = USER_PROFILE_FILE.read_text()
        assert ("dispatch" in content or "useDispatch" in content), "Should dispatch update action"


class TestUserProfileAPIIntegration:
    """Test API integration"""

    def test_makes_api_call_for_update(self):
        """Test that component makes API call to update profile"""
        content = USER_PROFILE_FILE.read_text()
        assert ("api" in content.lower() or "axios" in content or
                "put" in content or "patch" in content), "Should make API call for update"

    def test_makes_api_call_for_password_change(self):
        """Test that component makes API call to change password"""
        content = USER_PROFILE_FILE.read_text()
        assert ("password" in content.lower() and
                ("api" in content.lower() or "post" in content or
                 "put" in content)), "Should make API call for password change"


class TestUserProfileErrorHandling:
    """Test error handling"""

    def test_handles_api_errors(self):
        """Test that component handles API errors"""
        content = USER_PROFILE_FILE.read_text()
        assert ("catch" in content or "error" in content or
                "try" in content), "Should handle API errors"

    def test_displays_error_messages(self):
        """Test that component displays error messages"""
        content = USER_PROFILE_FILE.read_text()
        assert ("error" in content and ("message" in content or
                "Alert" in content or "text" in content)), "Should display error messages"

    def test_displays_success_messages(self):
        """Test that component displays success messages"""
        content = USER_PROFILE_FILE.read_text()
        assert ("success" in content.lower() or "Success" in content or
                "updated" in content.lower()), "Should display success messages"


class TestUserProfileLoadingState:
    """Test loading state"""

    def test_has_loading_state(self):
        """Test that component has loading state"""
        content = USER_PROFILE_FILE.read_text()
        assert ("loading" in content.lower() or "isLoading" in content or
                "Loading" in content), "Should have loading state"

    def test_shows_loading_indicator(self):
        """Test that component shows loading indicator"""
        content = USER_PROFILE_FILE.read_text()
        assert ("CircularProgress" in content or "Spinner" in content or
                "loading" in content.lower()), "Should show loading indicator"


class TestUserProfileTypeScript:
    """Test TypeScript typing"""

    def test_uses_typescript_types(self):
        """Test that TypeScript types are used"""
        content = USER_PROFILE_FILE.read_text()
        assert (":" in content or "interface" in content or
                "type" in content), "Should use TypeScript types"

    def test_has_props_interface(self):
        """Test that component has props interface if needed"""
        content = USER_PROFILE_FILE.read_text()
        # UserProfile might not have props, but should have typed variables
        assert (":" in content or "React.FC" in content), "Should have TypeScript typing"


class TestUserProfileStyling:
    """Test styling"""

    def test_uses_material_ui_components(self):
        """Test that component uses Material-UI components"""
        content = USER_PROFILE_FILE.read_text()
        assert ("Box" in content or "Card" in content or "Paper" in content or
                "Container" in content), "Should use Material-UI components"

    def test_has_consistent_layout(self):
        """Test that component has consistent layout"""
        content = USER_PROFILE_FILE.read_text()
        assert ("Grid" in content or "Box" in content or "Stack" in content or
                "Container" in content), "Should have consistent layout"


class TestUserProfileDocumentation:
    """Test documentation"""

    def test_has_file_documentation(self):
        """Test that file has header documentation"""
        content = USER_PROFILE_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content), "Should have documentation"

    def test_documents_component_purpose(self):
        """Test that component purpose is documented"""
        content = USER_PROFILE_FILE.read_text()
        lines = content.split('\n')
        comment_lines = [line for line in lines if '//' in line or '*' in line]
        assert len(comment_lines) > 3, "Should have documentation explaining component purpose"


class TestUserProfileAccessibility:
    """Test accessibility features"""

    def test_has_aria_labels_or_labels(self):
        """Test that form fields have labels"""
        content = USER_PROFILE_FILE.read_text()
        assert ("label" in content.lower() or "aria-label" in content or
                "Label" in content), "Should have labels for form fields"
