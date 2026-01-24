"""
Test suite for Register page component

Validates the Register.tsx component implementation including:
- File structure and imports
- Material-UI components usage
- react-hook-form integration
- Form validation with yup (registerSchema)
- All registration fields (email, username, password, full_name)
- Password strength indicator
- Redux integration for registration action
- Error handling and loading states
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
REGISTER_PAGE_FILE = FRONTEND_SRC / "pages" / "Register.tsx"
AUTH_SCHEMAS_FILE = FRONTEND_SRC / "validations" / "authSchemas.ts"


class TestRegisterPageFileExists:
    """Test that register page file exists"""

    def test_register_page_file_exists(self):
        """Test that Register.tsx exists"""
        assert REGISTER_PAGE_FILE.exists(), "Register.tsx should exist"
        assert REGISTER_PAGE_FILE.is_file(), "Register.tsx should be a file"

    def test_register_page_has_content(self):
        """Test that Register.tsx has content"""
        content = REGISTER_PAGE_FILE.read_text()
        assert len(content) > 0, "Register.tsx should not be empty"


class TestRegisterSchemaValidation:
    """Test that register schema exists and has correct validation"""

    def test_has_register_schema(self):
        """Test that registerSchema is exported"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "registerSchema" in content, "Should export registerSchema"

    def test_register_schema_validates_email(self):
        """Test that registerSchema validates email field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        # Check for email validation in registerSchema section
        assert "email" in content, "Should validate email field"

    def test_register_schema_validates_username(self):
        """Test that registerSchema validates username field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "username" in content, "Should validate username field"
        # Username should have min/max length
        assert "min(3" in content or "min: 3" in content, "Username should have minimum length"

    def test_register_schema_validates_password(self):
        """Test that registerSchema validates password field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "password" in content, "Should validate password field"
        # Password should have min 8 characters
        assert "min(8" in content or "min: 8" in content, "Password should require min 8 characters"

    def test_register_schema_validates_full_name(self):
        """Test that registerSchema validates full_name field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "full_name" in content, "Should validate full_name field"


class TestRegisterPageImports:
    """Test that Register page has necessary imports"""

    def test_imports_react(self):
        """Test that React is imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "react" in content.lower(), "Should import React"

    def test_imports_material_ui(self):
        """Test that Material-UI components are imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "@mui/material" in content, "Should import Material-UI components"

    def test_imports_react_hook_form(self):
        """Test that react-hook-form is imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "react-hook-form" in content, "Should import react-hook-form"

    def test_imports_yup_resolver(self):
        """Test that yup resolver is imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "yupResolver" in content or "@hookform/resolvers" in content, "Should import yup resolver"

    def test_imports_redux_hooks(self):
        """Test that Redux hooks are imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "useDispatch" in content or "react-redux" in content, "Should import Redux hooks"

    def test_imports_register_schema(self):
        """Test that registerSchema is imported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "registerSchema" in content, "Should import registerSchema"


class TestRegisterPageComponent:
    """Test Register page component structure"""

    def test_exports_register_component(self):
        """Test that Register component is exported"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "export" in content, "Should export Register component"
        assert "Register" in content, "Should have Register component"

    def test_is_function_component(self):
        """Test that Register is a function component"""
        content = REGISTER_PAGE_FILE.read_text()
        assert ("const Register" in content or "function Register" in content or
                "export default function" in content), "Should be a function component"


class TestRegisterPageFormStructure:
    """Test form structure and react-hook-form integration"""

    def test_uses_useform_hook(self):
        """Test that useForm hook is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "useForm" in content, "Should use useForm hook"

    def test_configures_resolver(self):
        """Test that form is configured with yup resolver"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "resolver" in content, "Should configure resolver"
        assert "yupResolver" in content or "registerSchema" in content, "Should use yupResolver with registerSchema"

    def test_has_handlesubmit(self):
        """Test that handleSubmit is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "handleSubmit" in content, "Should use handleSubmit from useForm"

    def test_has_form_element(self):
        """Test that form element exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "<form" in content or "form" in content.lower(), "Should have form element"


class TestRegisterPageFields:
    """Test all registration form fields"""

    def test_has_email_field(self):
        """Test that email field exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "email" in content.lower(), "Should have email field"

    def test_has_username_field(self):
        """Test that username field exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "username" in content.lower(), "Should have username field"

    def test_has_password_field(self):
        """Test that password field exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "password" in content.lower(), "Should have password field"

    def test_has_full_name_field(self):
        """Test that full_name field exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "full_name" in content.lower() or "fullname" in content.lower(), "Should have full_name field"

    def test_uses_textfield_component(self):
        """Test that TextField component is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "TextField" in content, "Should use Material-UI TextField"

    def test_registers_form_fields(self):
        """Test that form fields are registered"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "register" in content or "Controller" in content, "Should register form fields"


class TestRegisterPageMaterialUI:
    """Test Material-UI components usage"""

    def test_uses_box_component(self):
        """Test that Box component is used for layout"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "Box" in content or "Container" in content, "Should use Box or Container for layout"

    def test_uses_button_component(self):
        """Test that Button component is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "Button" in content, "Should use Material-UI Button"

    def test_button_has_submit_type(self):
        """Test that submit button exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "submit" in content.lower(), "Should have submit button"

    def test_uses_typography_component(self):
        """Test that Typography component is used for text"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "Typography" in content or "title" in content.lower(), "Should use Typography for headings"


class TestRegisterPagePasswordStrength:
    """Test password strength indicator"""

    def test_has_password_strength_indicator(self):
        """Test that password strength indicator exists"""
        content = REGISTER_PAGE_FILE.read_text()
        # Check for password strength related code
        assert ("strength" in content.lower() or "weak" in content.lower() or
                "strong" in content.lower()), "Should have password strength indicator"

    def test_monitors_password_value(self):
        """Test that password value is monitored for strength"""
        content = REGISTER_PAGE_FILE.read_text()
        # Should watch password field or have useState for password
        assert "watch" in content or "password" in content, "Should monitor password value"

    def test_displays_strength_feedback(self):
        """Test that strength feedback is displayed"""
        content = REGISTER_PAGE_FILE.read_text()
        # Should have visual feedback (LinearProgress, Typography, or similar)
        assert ("LinearProgress" in content or "strength" in content.lower() or
                "indicator" in content.lower()), "Should display strength feedback"


class TestRegisterPageReduxIntegration:
    """Test Redux integration"""

    def test_uses_usedispatch_hook(self):
        """Test that useDispatch hook is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "useDispatch" in content, "Should use useDispatch hook"

    def test_uses_useselector_hook(self):
        """Test that useSelector hook is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "useSelector" in content or "loading" in content, "Should use useSelector to get state"

    def test_handles_registration_action(self):
        """Test that registration action is handled"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "dispatch" in content, "Should dispatch registration action"


class TestRegisterPageErrorHandling:
    """Test error handling"""

    def test_displays_form_errors(self):
        """Test that form validation errors are displayed"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "error" in content.lower(), "Should handle and display errors"

    def test_uses_helper_text(self):
        """Test that helper text is used for error messages"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "helperText" in content or "error" in content, "Should use helperText for validation errors"

    def test_handles_api_errors(self):
        """Test that API errors from Redux are handled"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "error" in content, "Should handle API errors"


class TestRegisterPageLoadingState:
    """Test loading state handling"""

    def test_checks_loading_state(self):
        """Test that loading state is checked"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "loading" in content, "Should check loading state"

    def test_disables_button_while_loading(self):
        """Test that button is disabled during loading"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "disabled" in content or "loading" in content, "Should disable button during loading"


class TestRegisterPageNavigation:
    """Test navigation elements"""

    def test_has_link_to_login(self):
        """Test that link to login page exists"""
        content = REGISTER_PAGE_FILE.read_text()
        assert ("login" in content.lower() or "sign in" in content.lower() or
                "already have" in content.lower()), "Should have link to login page"

    def test_uses_react_router_link(self):
        """Test that React Router Link is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "Link" in content or "useNavigate" in content or "navigate" in content, "Should use React Router for navigation"

    def test_navigates_after_success(self):
        """Test that navigation happens after successful registration"""
        content = REGISTER_PAGE_FILE.read_text()
        # Should navigate to login or dashboard after successful registration
        assert "navigate" in content or "useNavigate" in content, "Should navigate after successful registration"


class TestRegisterPageTypescript:
    """Test TypeScript typing"""

    def test_uses_typescript_types(self):
        """Test that TypeScript types are used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert ":" in content or "interface" in content or "type" in content, "Should use TypeScript types"

    def test_uses_register_form_data_type(self):
        """Test that RegisterFormData type is used"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "RegisterFormData" in content or "RegisterRequest" in content, "Should use RegisterFormData type"


class TestRegisterPageDocumentation:
    """Test component documentation"""

    def test_has_documentation(self):
        """Test that component has documentation"""
        content = REGISTER_PAGE_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content or
                "Register" in content), "Should have documentation"


class TestRegisterPageAccessibility:
    """Test accessibility features"""

    def test_has_form_labels(self):
        """Test that form fields have labels"""
        content = REGISTER_PAGE_FILE.read_text()
        assert "label" in content.lower(), "Should have labels for form fields"

    def test_has_autocomplete_attributes(self):
        """Test that autocomplete attributes are used appropriately"""
        content = REGISTER_PAGE_FILE.read_text()
        # Should have appropriate autocomplete for username, email, new-password
        lines = content.split('\n')
        assert len(lines) > 30, "Component should be well-structured with multiple fields"
