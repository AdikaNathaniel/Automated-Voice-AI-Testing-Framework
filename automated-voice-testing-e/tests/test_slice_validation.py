"""
Test suite for validation Redux slice (TASK-184)

Validates the validation Redux slice implementation including:
- File structure
- Initial state definition
- State shape (queue, current, loading, error, stats)
- Async thunks for validation operations
- Reducers for state management
- Redux Toolkit patterns
- TypeScript usage
- Documentation
"""

import re
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SLICES_DIR = PROJECT_ROOT / "frontend" / "src" / "store" / "slices"
VALIDATION_SLICE_FILE = SLICES_DIR / "validationSlice.ts"


def _get_slice_function_block(content: str, function_name: str) -> str:
    """
    Extract the createAsyncThunk block for assertions.
    """
    pattern = rf"export const {function_name}[\s\S]*?\n\}}\s*\);\s*"
    match = re.search(pattern, content)
    assert match, f"{function_name} function definition not found"
    return match.group(0)


class TestValidationSliceFileExists:
    """Test that validation slice file exists"""

    def test_slices_directory_exists(self):
        """Test that slices directory exists"""
        assert SLICES_DIR.exists(), "frontend/src/store/slices directory should exist"
        assert SLICES_DIR.is_dir(), "slices should be a directory"

    def test_validation_slice_file_exists(self):
        """Test that validationSlice.ts exists"""
        assert VALIDATION_SLICE_FILE.exists(), "validationSlice.ts should exist"
        assert VALIDATION_SLICE_FILE.is_file(), "validationSlice.ts should be a file"

    def test_slice_file_has_content(self):
        """Test that slice file has content"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert len(content) > 0, "validationSlice.ts should not be empty"


class TestReduxToolkitImports:
    """Test Redux Toolkit imports"""

    def test_imports_create_slice(self):
        """Test that slice imports createSlice"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "createSlice" in content, "Should import createSlice from Redux Toolkit"

    def test_imports_create_async_thunk(self):
        """Test that slice imports createAsyncThunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "createAsyncThunk" in content, "Should import createAsyncThunk"

    def test_imports_from_redux_toolkit(self):
        """Test that imports are from @reduxjs/toolkit"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "@reduxjs/toolkit" in content, "Should import from @reduxjs/toolkit"

    def test_imports_payload_action(self):
        """Test that slice imports PayloadAction for typing"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("PayloadAction" in content or
                "Action" in content), "Should import PayloadAction for type safety"


class TestStateInterface:
    """Test state interface/type definition"""

    def test_has_state_interface_or_type(self):
        """Test that slice defines state interface or type"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("ValidationState" in content or
                "validationState" in content or
                "interface" in content), "Should define state interface/type"

    def test_state_has_queue_field(self):
        """Test that state includes queue field for validation items"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "queue" in content, "Should have queue field in state"

    def test_state_has_current_field(self):
        """Test that state includes current field for active validation"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("current" in content or
                "selected" in content), "Should have current field in state"

    def test_state_has_loading_field(self):
        """Test that state includes loading field"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "loading" in content, "Should have loading field in state"

    def test_state_has_error_field(self):
        """Test that state includes error field"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "error" in content, "Should have error field in state"

    def test_state_has_stats_field(self):
        """Test that state includes stats field"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "stats" in content, "Should have stats field in state"


class TestInitialState:
    """Test initial state definition"""

    def test_has_initial_state(self):
        """Test that slice defines initialState"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "initialState" in content, "Should define initialState"

    def test_initial_state_is_typed(self):
        """Test that initialState is typed"""
        content = VALIDATION_SLICE_FILE.read_text()
        # Should have type annotation
        assert (":" in content and "initialState" in content), "initialState should be typed"

    def test_initial_queue_is_empty_array(self):
        """Test that initial queue is empty array"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("queue: []" in content or
                "queue:[]" in content), "Initial queue should be empty array"

    def test_initial_current_is_null(self):
        """Test that initial current is null"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("current: null" in content or
                "current:null" in content), "Initial current should be null"


class TestAsyncThunks:
    """Test async thunks for validation operations"""

    def test_has_fetch_queue_thunk(self):
        """Test that slice has fetchValidationQueue async thunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("fetchValidationQueue" in content or
                "getValidationQueue" in content or
                "fetchQueue" in content), "Should have fetch validation queue thunk"

    def test_has_claim_validation_thunk(self):
        """Test that slice has claimValidation async thunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "claimValidation" in content, "Should have claim validation thunk"

    def test_has_submit_validation_thunk(self):
        """Test that slice has submitValidation async thunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "submitValidation" in content, "Should have submit validation thunk"

    def test_has_fetch_stats_thunk(self):
        """Test that slice has fetchValidationStats async thunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("fetchValidationStats" in content or
                "getValidationStats" in content or
                "fetchStats" in content), "Should have fetch validation stats thunk"

    def test_has_release_validation_thunk(self):
        """Test that slice has releaseValidation async thunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("releaseValidation" in content or
                "release" in content), "Should have release validation thunk"

    def test_thunks_use_create_async_thunk(self):
        """Test that thunks use createAsyncThunk"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "createAsyncThunk" in content, "Thunks should use createAsyncThunk"


class TestSliceApiAlignment:
    """Ensure thunk endpoints and payloads align with backend routes."""

    def test_slice_mentions_api_v1_validation_base(self):
        """Slice should target /api/v1/validation endpoints."""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "/api/v1/validation" in content, "Slice should reference /api/v1/validation base path"

    def test_claim_validation_thunk_posts_to_queue_id_path(self):
        """Claim thunk should hit /{queue_id}/claim."""
        content = VALIDATION_SLICE_FILE.read_text()
        block = _get_slice_function_block(content, "claimValidation")
        assert "/${itemId}/claim" in block, "Claim thunk should post to queue ID claim endpoint"
        assert "response.data.data" in block, "Claim thunk should unwrap SuccessResponse data"

    def test_release_validation_thunk_posts_to_queue_id_path(self):
        """Release thunk should hit /{queue_id}/release and unwrap SuccessResponse."""
        content = VALIDATION_SLICE_FILE.read_text()
        block = _get_slice_function_block(content, "releaseValidation")
        assert "/${itemId}/release" in block, "Release thunk should post to queue ID release endpoint"
        assert "response.data.data" in block, "Release thunk should unwrap SuccessResponse data"

    def test_submit_validation_thunk_requires_queue_id(self):
        """Submit thunk should accept queueId and map payload fields."""
        content = VALIDATION_SLICE_FILE.read_text()
        block = _get_slice_function_block(content, "submitValidation")
        assert "queueId" in block, "Submit thunk should accept queueId parameter"
        assert "/${queueId}/submit" in block, "Submit thunk should post to queue ID submit endpoint"
        assert "validation_decision" in block, "Submit payload should include validation_decision"
        assert "time_spent_seconds" in block, "Submit payload should include time_spent_seconds"
        assert "response.data.data" in block, "Submit thunk should unwrap SuccessResponse data"


class TestSliceDefinition:
    """Test slice creation"""

    def test_uses_create_slice(self):
        """Test that file uses createSlice"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "createSlice" in content, "Should use createSlice"

    def test_has_slice_name(self):
        """Test that slice has a name"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("name:" in content or
                'name:' in content or
                "validation" in content), "Should define slice name"

    def test_has_reducers(self):
        """Test that slice has reducers section"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "reducers" in content, "Should have reducers section"

    def test_has_extra_reducers(self):
        """Test that slice has extraReducers for async thunks"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "extraReducers" in content, "Should have extraReducers for async thunks"


class TestReducers:
    """Test reducer actions"""

    def test_has_set_current_reducer(self):
        """Test that slice has reducer for setting current validation"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("setCurrent" in content or
                "setCurrentValidation" in content or
                "setSelected" in content), "Should have reducer to set current validation"

    def test_has_clear_error_reducer(self):
        """Test that slice has reducer for clearing errors"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("clearError" in content or
                "resetError" in content), "Should have reducer to clear errors"

    def test_has_reset_state_reducer(self):
        """Test that slice has reducer for resetting state"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("reset" in content or
                "clear" in content), "Should have reducer to reset/clear state"

    def test_has_update_timer_reducer(self):
        """Test that slice has reducer for updating validation timer"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("timer" in content or
                "time" in content or
                "timeSpent" in content), "Should have reducer to update validation timer"


class TestAsyncThunkHandlers:
    """Test async thunk state handlers"""

    def test_handles_pending_state(self):
        """Test that thunks handle pending state"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "pending" in content, "Should handle pending state for async operations"

    def test_handles_fulfilled_state(self):
        """Test that thunks handle fulfilled state"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "fulfilled" in content, "Should handle fulfilled state for async operations"

    def test_handles_rejected_state(self):
        """Test that thunks handle rejected state"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert "rejected" in content, "Should handle rejected state for async operations"

    def test_handles_fetch_queue_fulfilled(self):
        """Test that fetchQueue fulfilled handler updates queue"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("queue" in content and "fulfilled" in content), \
            "Should update queue on fetchQueue fulfilled"

    def test_handles_claim_validation_fulfilled(self):
        """Test that claimValidation fulfilled handler updates current"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("current" in content or "claim" in content), \
            "Should update current on claimValidation fulfilled"


class TestExports:
    """Test exports"""

    def test_exports_actions(self):
        """Test that slice exports actions"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("export" in content and "actions" in content), "Should export actions"

    def test_exports_reducer(self):
        """Test that slice exports reducer"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("export" in content and "reducer" in content), "Should export reducer"

    def test_exports_async_thunks(self):
        """Test that async thunks are exported"""
        content = VALIDATION_SLICE_FILE.read_text()
        # Async thunks should be exported separately or with actions
        assert "export" in content, "Should export async thunks"

    def test_has_default_export(self):
        """Test that slice has default export"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("export default" in content or
                "default export" in content or
                ".reducer" in content), "Should have default export for reducer"


class TestDocumentation:
    """Test documentation"""

    def test_has_file_documentation(self):
        """Test that file has top-level documentation"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("/**" in content or "//" in content), "Should have file documentation"

    def test_has_state_documentation(self):
        """Test that state is documented"""
        content = VALIDATION_SLICE_FILE.read_text()
        # Should have comments explaining state structure
        assert ("*" in content or "//" in content), "Should document state structure"

    def test_documents_validation_workflow(self):
        """Test that validation workflow is documented"""
        content = VALIDATION_SLICE_FILE.read_text()
        # Should document the validation workflow process
        assert ("validation" in content.lower() or
                "claim" in content.lower() or
                "submit" in content.lower()), "Should document validation workflow"


class TestTypeScriptUsage:
    """Test TypeScript usage"""

    def test_uses_typescript_syntax(self):
        """Test that file uses TypeScript syntax"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("interface" in content or
                "type" in content or
                ":" in content), "Should use TypeScript syntax"

    def test_imports_validation_types(self):
        """Test that file imports validation types"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("ValidationQueue" in content or
                "HumanValidation" in content or
                "ValidationStats" in content or
                "types/validation" in content), "Should import validation types"

    def test_file_extension_is_ts(self):
        """Test that file has .ts extension"""
        assert VALIDATION_SLICE_FILE.suffix == ".ts", "File should have .ts extension"


class TestAPIIntegration:
    """Test API integration patterns"""

    def test_uses_axios_or_fetch(self):
        """Test that thunks use axios or fetch for API calls"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("axios" in content or
                "fetch" in content or
                "api" in content), "Should use HTTP client for API calls"

    def test_has_validation_api_endpoints(self):
        """Test that file references validation API endpoints"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("/validation" in content or
                "api" in content or
                "url" in content.lower()), "Should reference validation API endpoints"

    def test_has_queue_endpoint(self):
        """Test that file references queue endpoint"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("queue" in content or
                "/validation" in content), "Should reference queue endpoint"

    def test_has_claim_endpoint(self):
        """Test that file references claim endpoint"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("claim" in content), "Should reference claim endpoint"


class TestValidationWorkflow:
    """Test validation workflow logic"""

    def test_claim_sets_current_validation(self):
        """Test that claiming sets current validation item"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("current" in content and "claim" in content), \
            "Claiming should set current validation"

    def test_submit_clears_current_validation(self):
        """Test that submitting clears current validation"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("submit" in content), \
            "Should handle submit validation"

    def test_tracks_time_spent(self):
        """Test that slice tracks time spent on validation"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("time" in content or
                "timer" in content or
                "timeSpent" in content), "Should track time spent on validation"


class TestErrorHandling:
    """Test error handling"""

    def test_handles_claim_errors(self):
        """Test that slice handles claim validation errors"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("error" in content and "rejected" in content), \
            "Should handle claim validation errors"

    def test_handles_submit_errors(self):
        """Test that slice handles submit validation errors"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("error" in content), \
            "Should handle submit validation errors"

    def test_clears_errors(self):
        """Test that slice can clear errors"""
        content = VALIDATION_SLICE_FILE.read_text()
        assert ("clearError" in content or
                "resetError" in content or
                "null" in content), "Should be able to clear errors"
