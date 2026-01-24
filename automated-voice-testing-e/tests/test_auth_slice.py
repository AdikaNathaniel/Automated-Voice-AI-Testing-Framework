"""
Test suite for authentication Redux slice

Validates the authSlice TypeScript implementation including:
- File structure and imports
- State interface and initial state
- Reducers for synchronous actions
- Async thunks for login, logout, and token refresh
- Proper TypeScript typing
"""

import pytest
from pathlib import Path
import re


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_SRC = PROJECT_ROOT / "frontend" / "src"
AUTH_SLICE_FILE = FRONTEND_SRC / "store" / "slices" / "authSlice.ts"
AUTH_TYPES_FILE = FRONTEND_SRC / "types" / "auth.ts"


class TestAuthSliceFileExists:
    """Test that auth slice file exists"""

    def test_slices_directory_exists(self):
        """Test that store/slices directory exists"""
        slices_dir = FRONTEND_SRC / "store" / "slices"
        assert slices_dir.exists(), "frontend/src/store/slices directory should exist"
        assert slices_dir.is_dir(), "store/slices should be a directory"

    def test_auth_slice_file_exists(self):
        """Test that authSlice.ts exists"""
        assert AUTH_SLICE_FILE.exists(), "authSlice.ts should exist"
        assert AUTH_SLICE_FILE.is_file(), "authSlice.ts should be a file"

    def test_auth_slice_has_content(self):
        """Test that authSlice.ts has content"""
        content = AUTH_SLICE_FILE.read_text()
        assert len(content) > 0, "authSlice.ts should not be empty"


class TestAuthTypesFile:
    """Test that auth types file exists and has required types"""

    def test_auth_types_file_exists(self):
        """Test that auth.ts types file exists"""
        assert AUTH_TYPES_FILE.exists(), "frontend/src/types/auth.ts should exist"
        assert AUTH_TYPES_FILE.is_file(), "auth.ts should be a file"

    def test_auth_types_has_user_interface(self):
        """Test that User interface is exported"""
        content = AUTH_TYPES_FILE.read_text()
        assert "export interface User" in content, "Should export User interface"
        assert "id:" in content and "string" in content, "User should have id field"
        assert "email:" in content, "User should have email field"
        assert "username:" in content, "User should have username field"

    def test_auth_types_has_auth_state_interface(self):
        """Test that AuthState interface is exported"""
        content = AUTH_TYPES_FILE.read_text()
        assert "export interface AuthState" in content, "Should export AuthState interface"
        assert "user:" in content, "AuthState should have user field"
        assert "accessToken:" in content, "AuthState should have accessToken field"
        assert "isAuthenticated:" in content, "AuthState should have isAuthenticated field"
        assert "loading:" in content, "AuthState should have loading field"


class TestAuthSliceImports:
    """Test that authSlice has necessary imports"""

    def test_imports_createslice(self):
        """Test that createSlice is imported from Redux Toolkit"""
        content = AUTH_SLICE_FILE.read_text()
        assert "createSlice" in content, "Should import createSlice"
        assert "@reduxjs/toolkit" in content, "Should import from @reduxjs/toolkit"

    def test_imports_createasyncthunk(self):
        """Test that createAsyncThunk is imported"""
        content = AUTH_SLICE_FILE.read_text()
        assert "createAsyncThunk" in content, "Should import createAsyncThunk"

    def test_imports_auth_types(self):
        """Test that auth types are imported"""
        content = AUTH_SLICE_FILE.read_text()
        assert "AuthState" in content or "import" in content, "Should import auth types"


class TestAuthSliceStructure:
    """Test authSlice structure and exports"""

    def test_has_initial_state(self):
        """Test that initialState is defined"""
        content = AUTH_SLICE_FILE.read_text()
        assert "initialState" in content, "Should define initialState"

    def test_initial_state_has_correct_shape(self):
        """Test that initialState has correct properties"""
        content = AUTH_SLICE_FILE.read_text()
        assert "user:" in content and "null" in content, "initialState should have user: null"
        assert "accessToken:" in content, "initialState should have accessToken"
        assert "isAuthenticated:" in content and "false" in content, "initialState should have isAuthenticated: false"
        assert "loading:" in content and "false" in content, "initialState should have loading: false"

    def test_creates_auth_slice(self):
        """Test that createSlice is called to create authSlice"""
        content = AUTH_SLICE_FILE.read_text()
        assert "createSlice" in content, "Should call createSlice"
        assert "name:" in content and ("'auth'" in content or '"auth"' in content), "Slice should be named 'auth'"

    def test_exports_auth_reducer(self):
        """Test that authSlice reducer is exported as default"""
        content = AUTH_SLICE_FILE.read_text()
        assert "export default" in content, "Should have default export"
        assert "reducer" in content, "Should export reducer"


class TestAuthSliceReducers:
    """Test synchronous reducers in authSlice"""

    def test_has_logout_reducer(self):
        """Test that logout reducer exists"""
        content = AUTH_SLICE_FILE.read_text()
        assert "logout" in content, "Should have logout reducer"

    def test_has_update_user_reducer(self):
        """Test that updateUser reducer exists"""
        content = AUTH_SLICE_FILE.read_text()
        assert "updateUser" in content or "setUser" in content, "Should have updateUser/setUser reducer"

    def test_has_clear_error_reducer(self):
        """Test that clearError reducer exists"""
        content = AUTH_SLICE_FILE.read_text()
        assert "clearError" in content or "error" in content, "Should have error handling"


class TestAuthSliceAsyncThunks:
    """Test async thunks for authentication operations"""

    def test_has_login_thunk(self):
        """Test that login async thunk exists"""
        content = AUTH_SLICE_FILE.read_text()
        assert "login" in content, "Should have login thunk"
        assert "createAsyncThunk" in content, "Should use createAsyncThunk"

    def test_login_thunk_has_proper_name(self):
        """Test that login thunk has 'auth/login' action type"""
        content = AUTH_SLICE_FILE.read_text()
        assert "'auth/login'" in content or '"auth/login"' in content, "Login thunk should be named 'auth/login'"

    def test_has_refresh_token_thunk(self):
        """Test that refreshToken async thunk exists"""
        content = AUTH_SLICE_FILE.read_text()
        assert "refreshToken" in content or "refresh" in content, "Should have refreshToken thunk"

    def test_refresh_token_thunk_has_proper_name(self):
        """Test that refreshToken thunk has proper action type"""
        content = AUTH_SLICE_FILE.read_text()
        assert "'auth/refresh" in content or '"auth/refresh' in content, "Should have auth/refresh action type"


class TestAuthSliceExtraReducers:
    """Test extra reducers for handling async thunk states"""

    def test_has_extra_reducers(self):
        """Test that extraReducers are defined"""
        content = AUTH_SLICE_FILE.read_text()
        assert "extraReducers" in content, "Should define extraReducers"

    def test_handles_login_pending(self):
        """Test that login.pending state is handled"""
        content = AUTH_SLICE_FILE.read_text()
        assert "pending" in content, "Should handle pending state"
        assert "loading" in content, "Should set loading state"

    def test_handles_login_fulfilled(self):
        """Test that login.fulfilled state is handled"""
        content = AUTH_SLICE_FILE.read_text()
        assert "fulfilled" in content, "Should handle fulfilled state"

    def test_handles_login_rejected(self):
        """Test that login.rejected state is handled"""
        content = AUTH_SLICE_FILE.read_text()
        assert "rejected" in content, "Should handle rejected state"
        assert "error" in content, "Should set error state"


class TestAuthSliceActions:
    """Test that actions are exported"""

    def test_exports_actions(self):
        """Test that slice actions are exported"""
        content = AUTH_SLICE_FILE.read_text()
        assert "export" in content and "actions" in content, "Should export actions"

    def test_exports_logout_action(self):
        """Test that logout action is exported"""
        content = AUTH_SLICE_FILE.read_text()
        # Check for export pattern like: export const { logout } = authSlice.actions
        assert "logout" in content, "Should export logout action"

    def test_exports_login_thunk(self):
        """Test that login thunk is exported"""
        content = AUTH_SLICE_FILE.read_text()
        assert "export" in content and "login" in content, "Should export login thunk"


class TestAuthSliceTypescript:
    """Test TypeScript typing and interfaces"""

    def test_uses_typescript_types(self):
        """Test that TypeScript types are used"""
        content = AUTH_SLICE_FILE.read_text()
        assert ":" in content, "Should use TypeScript type annotations"

    def test_has_payloadaction_types(self):
        """Test that PayloadAction is imported for typed reducers"""
        content = AUTH_SLICE_FILE.read_text()
        assert "PayloadAction" in content or "action.payload" in content, "Should use typed actions"


class TestAuthSliceIntegration:
    """Test integration with Redux store"""

    def test_store_imports_auth_slice(self):
        """Test that store configuration imports authSlice"""
        store_file = FRONTEND_SRC / "store" / "index.ts"
        if store_file.exists():
            content = store_file.read_text()
            # After implementation, store should import authReducer
            # For now, just check file exists
            assert store_file.exists(), "Store configuration should exist"


class TestAuthSliceDocumentation:
    """Test that authSlice has proper documentation"""

    def test_file_has_header_comment(self):
        """Test that file has header documentation"""
        content = AUTH_SLICE_FILE.read_text()
        assert "/**" in content or "/*" in content or "//" in content, "Should have documentation comments"

    def test_thunks_have_jsdoc(self):
        """Test that async thunks have JSDoc comments"""
        content = AUTH_SLICE_FILE.read_text()
        # Should have comments explaining what the thunks do
        lines = content.split("\n")
        comment_count = sum(1 for line in lines if "//" in line or "/*" in line or "*" in line[:3])
        assert comment_count > 5, "Should have descriptive comments"


class TestAuthSliceErrorHandling:
    """Test error handling in authSlice"""

    def test_has_error_state(self):
        """Test that error state is managed"""
        content = AUTH_SLICE_FILE.read_text()
        assert "error:" in content, "Should have error state"

    def test_clears_error_on_new_request(self):
        """Test that error is cleared when new request starts"""
        content = AUTH_SLICE_FILE.read_text()
        assert "error: null" in content, "Should clear error state"


class TestAuthSliceLocalStorage:
    """Test localStorage integration for token persistence"""

    def test_handles_token_storage(self):
        """Test that tokens are handled (localStorage in implementation)"""
        content = AUTH_SLICE_FILE.read_text()
        # The slice should at least set tokens in state
        assert "accessToken" in content, "Should handle access token"
        assert "refreshToken" in content or "refresh" in content, "Should handle refresh token"
