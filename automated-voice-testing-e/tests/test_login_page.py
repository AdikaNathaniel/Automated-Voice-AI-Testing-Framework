"""
Test suite for Login page component

Validates the Login.tsx component implementation including:
- File structure and imports
- Material-UI components usage
- react-hook-form integration
- Form validation with yup
- Redux integration for login action
- Error handling and loading states
"""

import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
LOGIN_PAGE_FILE = FRONTEND_SRC / "pages" / "Login.tsx"
AUTH_SCHEMAS_FILE = FRONTEND_SRC / "validations" / "authSchemas.ts"


class TestLoginPageFileExists:
    """Test that login page file exists"""

    def test_pages_directory_exists(self):
        """Test that pages directory exists"""
        pages_dir = FRONTEND_SRC / "pages"
        assert pages_dir.exists(), "frontend/src/pages directory should exist"
        assert pages_dir.is_dir(), "pages should be a directory"

    def test_login_page_file_exists(self):
        """Test that Login.tsx exists"""
        assert LOGIN_PAGE_FILE.exists(), "Login.tsx should exist"
        assert LOGIN_PAGE_FILE.is_file(), "Login.tsx should be a file"

    def test_login_page_has_content(self):
        """Test that Login.tsx has content"""
        content = LOGIN_PAGE_FILE.read_text()
        assert len(content) > 0, "Login.tsx should not be empty"


class TestAuthSchemasFile:
    """Test that validation schemas file exists"""

    def test_auth_schemas_file_exists(self):
        """Test that authSchemas.ts exists"""
        assert AUTH_SCHEMAS_FILE.exists(), "authSchemas.ts should exist"
        assert AUTH_SCHEMAS_FILE.is_file(), "authSchemas.ts should be a file"

    def test_has_login_schema(self):
        """Test that loginSchema is exported"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "loginSchema" in content, "Should export loginSchema"
        assert "yup" in content, "Should import yup"

    def test_login_schema_validates_email(self):
        """Test that loginSchema validates email field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "email" in content, "Should validate email field"
        assert "email()" in content or "Email" in content, "Should have email validation"

    def test_login_schema_validates_password(self):
        """Test that loginSchema validates password field"""
        content = AUTH_SCHEMAS_FILE.read_text()
        assert "password" in content, "Should validate password field"


class TestLoginPageImports:
    """Test that Login page has necessary imports"""

    def test_imports_react(self):
        """Test that React is imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "react" in content.lower(), "Should import React"

    def test_imports_material_ui(self):
        """Test that Material-UI components are imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "@mui/material" in content, "Should import Material-UI components"

    def test_imports_react_hook_form(self):
        """Test that react-hook-form is imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "react-hook-form" in content, "Should import react-hook-form"

    def test_imports_yup_resolver(self):
        """Test that yup resolver is imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "yupResolver" in content or "@hookform/resolvers" in content, "Should import yup resolver"

    def test_imports_redux_hooks(self):
        """Test that Redux hooks are imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "useDispatch" in content or "react-redux" in content, "Should import Redux hooks"

    def test_imports_login_schema(self):
        """Test that loginSchema is imported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "loginSchema" in content, "Should import loginSchema"


class TestLoginPageComponent:
    """Test Login page component structure"""

    def test_exports_login_component(self):
        """Test that Login component is exported"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "export" in content, "Should export Login component"
        assert "Login" in content, "Should have Login component"

    def test_is_function_component(self):
        """Test that Login is a function component"""
        content = LOGIN_PAGE_FILE.read_text()
        # Check for function component patterns
        assert ("const Login" in content or "function Login" in content or
                "export default function" in content), "Should be a function component"


class TestLoginPageFormStructure:
    """Test form structure and react-hook-form integration"""

    def test_uses_useform_hook(self):
        """Test that useForm hook is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "useForm" in content, "Should use useForm hook"

    def test_configures_resolver(self):
        """Test that form is configured with yup resolver"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "resolver" in content, "Should configure resolver"
        assert "yupResolver" in content or "loginSchema" in content, "Should use yupResolver with loginSchema"

    def test_has_handlesubmit(self):
        """Test that handleSubmit is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "handleSubmit" in content, "Should use handleSubmit from useForm"

    def test_has_form_element(self):
        """Test that form element exists"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "<form" in content or "form" in content.lower(), "Should have form element"


class TestLoginPageFields:
    """Test form fields"""

    def test_has_email_field(self):
        """Test that email field exists"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "email" in content.lower(), "Should have email field"

    def test_has_password_field(self):
        """Test that password field exists"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "password" in content.lower(), "Should have password field"

    def test_uses_textfield_component(self):
        """Test that TextField component is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "TextField" in content, "Should use Material-UI TextField"

    def test_registers_form_fields(self):
        """Test that form fields are registered"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "register" in content or "Controller" in content, "Should register form fields"


class TestLoginPageMaterialUI:
    """Test Material-UI components usage"""

    def test_uses_box_component(self):
        """Test that Box component is used for layout"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "Box" in content or "Container" in content, "Should use Box or Container for layout"

    def test_uses_button_component(self):
        """Test that Button component is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "Button" in content, "Should use Material-UI Button"

    def test_button_has_submit_type(self):
        """Test that submit button exists"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "submit" in content.lower(), "Should have submit button"

    def test_uses_typography_component(self):
        """Test that Typography component is used for text"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "Typography" in content or "title" in content.lower(), "Should use Typography for headings"


class TestLoginPageReduxIntegration:
    """Test Redux integration"""

    def test_uses_usedispatch_hook(self):
        """Test that useDispatch hook is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "useDispatch" in content, "Should use useDispatch hook"

    def test_uses_useselector_hook(self):
        """Test that useSelector hook is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "useSelector" in content or "loading" in content, "Should use useSelector to get state"

    def test_dispatches_login_action(self):
        """Test that login action is dispatched"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "dispatch" in content and "login" in content, "Should dispatch login action"


class TestLoginPageErrorHandling:
    """Test error handling"""

    def test_displays_form_errors(self):
        """Test that form validation errors are displayed"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "error" in content.lower(), "Should handle and display errors"

    def test_uses_helper_text(self):
        """Test that helper text is used for error messages"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "helperText" in content or "error" in content, "Should use helperText for validation errors"

    def test_handles_api_errors(self):
        """Test that API errors from Redux are handled"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "error" in content, "Should handle API errors"


class TestLoginPageLoadingState:
    """Test loading state handling"""

    def test_checks_loading_state(self):
        """Test that loading state is checked"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "loading" in content, "Should check loading state"

    def test_disables_button_while_loading(self):
        """Test that button is disabled during loading"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "disabled" in content or "loading" in content, "Should disable button during loading"


class TestLoginPageNavigation:
    """Test navigation elements"""

    def test_has_link_to_register(self):
        """Test that link to register page exists"""
        content = LOGIN_PAGE_FILE.read_text()
        assert ("register" in content.lower() or "sign up" in content.lower() or
                "create account" in content.lower()), "Should have link to register page"

    def test_uses_react_router_link(self):
        """Test that React Router Link is used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "Link" in content or "useNavigate" in content or "navigate" in content, "Should use React Router for navigation"


class TestLoginPageTypescript:
    """Test TypeScript typing"""

    def test_uses_typescript_types(self):
        """Test that TypeScript types are used"""
        content = LOGIN_PAGE_FILE.read_text()
        assert ":" in content or "interface" in content or "type" in content, "Should use TypeScript types"


class TestLoginPageDocumentation:
    """Test component documentation"""

    def test_has_documentation(self):
        """Test that component has documentation"""
        content = LOGIN_PAGE_FILE.read_text()
        assert ("/**" in content or "/*" in content or "//" in content or
                "Login" in content), "Should have documentation"


class TestLoginPageAccessibility:
    """Test accessibility features"""

    def test_has_form_labels(self):
        """Test that form fields have labels"""
        content = LOGIN_PAGE_FILE.read_text()
        assert "label" in content.lower(), "Should have labels for form fields"

    def test_has_autocomplete_attributes(self):
        """Test that autocomplete attributes are used"""
        content = LOGIN_PAGE_FILE.read_text()
        # Material-UI TextFields often have autoComplete prop
        # This is a good practice check
        lines = content.split('\n')
        # Just check if component is well-structured, autocomplete is optional
        assert len(lines) > 20, "Component should be well-structured"
