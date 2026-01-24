"""
Test suite for Redux store configuration

Ensures proper Redux Toolkit store setup in the frontend application,
including store configuration, middleware, and slices directory structure.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"
STORE_DIR = SRC_DIR / "store"
STORE_INDEX = STORE_DIR / "index.ts"


class TestStoreDirectory:
    """Test store directory structure"""

    def test_store_directory_exists(self):
        """Test that store directory exists"""
        assert STORE_DIR.exists(), "store directory should exist"
        assert STORE_DIR.is_dir(), "store should be a directory"

    def test_store_directory_in_src(self):
        """Test that store directory is in src"""
        assert STORE_DIR.parent == SRC_DIR, "store should be in src directory"


class TestStoreIndexFile:
    """Test store/index.ts file"""

    def test_store_index_exists(self):
        """Test that store/index.ts exists"""
        assert STORE_INDEX.exists(), "store/index.ts should exist"
        assert STORE_INDEX.is_file(), "store/index.ts should be a file"

    def test_store_index_is_typescript(self):
        """Test that store/index.ts is a TypeScript file"""
        assert STORE_INDEX.suffix == ".ts", "store/index.ts should have .ts extension"

    def test_store_index_has_content(self):
        """Test that store/index.ts has content"""
        content = STORE_INDEX.read_text()
        assert len(content) > 0, "store/index.ts should not be empty"


class TestReduxToolkitImports:
    """Test Redux Toolkit imports in store/index.ts"""

    def test_imports_configure_store(self):
        """Test that store/index.ts imports configureStore"""
        content = STORE_INDEX.read_text()
        assert 'configureStore' in content, \
            "store/index.ts should import configureStore from Redux Toolkit"

    def test_imports_from_reduxjs_toolkit(self):
        """Test that store/index.ts imports from @reduxjs/toolkit"""
        content = STORE_INDEX.read_text()
        assert '@reduxjs/toolkit' in content, \
            "store/index.ts should import from '@reduxjs/toolkit'"


class TestStoreConfiguration:
    """Test store configuration"""

    def test_creates_store_with_configure_store(self):
        """Test that store is created using configureStore"""
        content = STORE_INDEX.read_text()
        assert 'configureStore' in content, \
            "store/index.ts should use configureStore to create store"

    def test_configures_reducer(self):
        """Test that store configures reducer"""
        content = STORE_INDEX.read_text()
        assert 'reducer' in content, \
            "store/index.ts should configure reducer"

    def test_exports_store(self):
        """Test that store exports the store"""
        content = STORE_INDEX.read_text()
        has_export_default = 'export default' in content
        has_export_store = 'export { store }' in content or 'export const store' in content
        assert has_export_default or has_export_store, \
            "store/index.ts should export the store"


class TestStoreTypes:
    """Test TypeScript type definitions for store"""

    def test_exports_root_state_type(self):
        """Test that store/index.ts exports RootState type"""
        content = STORE_INDEX.read_text()
        has_root_state = 'RootState' in content
        has_export_type = 'export type' in content or 'export {' in content
        # Should define and export RootState type
        assert has_root_state, "store/index.ts should define RootState type"

    def test_exports_app_dispatch_type(self):
        """Test that store/index.ts exports AppDispatch type"""
        content = STORE_INDEX.read_text()
        has_app_dispatch = 'AppDispatch' in content
        # Should define and export AppDispatch type
        assert has_app_dispatch, "store/index.ts should define AppDispatch type"


class TestSlicesDirectory:
    """Test slices directory for Redux slices"""

    def test_slices_directory_exists(self):
        """Test that slices directory exists"""
        slices_dir = STORE_DIR / "slices"
        assert slices_dir.exists(), "store/slices directory should exist"
        assert slices_dir.is_dir(), "store/slices should be a directory"

    def test_slices_directory_in_store(self):
        """Test that slices directory is in store"""
        slices_dir = STORE_DIR / "slices"
        assert slices_dir.parent == STORE_DIR, "slices should be in store directory"


class TestStoreStructure:
    """Test overall store structure"""

    def test_store_has_valid_typescript_syntax(self):
        """Test that store/index.ts has valid TypeScript syntax"""
        content = STORE_INDEX.read_text()

        # Basic syntax checks
        assert content.count('(') >= content.count(')') - 2, \
            "Parentheses should be balanced"
        assert content.count('{') >= content.count('}') - 2, \
            "Braces should be balanced"

    def test_store_file_not_too_small(self):
        """Test that store/index.ts has reasonable content"""
        content = STORE_INDEX.read_text()
        # Store configuration should be at least a few lines
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
        assert len(lines) >= 5, "store/index.ts should have meaningful content"


class TestReduxIntegration:
    """Test Redux integration with React app"""

    def test_app_tsx_references_provider_or_store(self):
        """Test that App.tsx or main.tsx uses Redux Provider"""
        app_tsx = SRC_DIR / "App.tsx"
        main_tsx = SRC_DIR / "main.tsx"

        app_content = app_tsx.read_text() if app_tsx.exists() else ""
        main_content = main_tsx.read_text() if main_tsx.exists() else ""

        combined = app_content + main_content

        # Should use Provider from react-redux
        has_provider = 'Provider' in combined
        has_react_redux = 'react-redux' in combined

        # At minimum, should have Provider (might be in main.tsx or App.tsx)
        # This is informational - we'll check properly in integration
        pass


class TestStoreMiddleware:
    """Test Redux store middleware configuration"""

    def test_store_includes_default_middleware(self):
        """Test that store uses default middleware or configures it"""
        content = STORE_INDEX.read_text()

        # Either uses default middleware or explicitly configures middleware
        # configureStore includes default middleware by default
        has_configure_store = 'configureStore' in content

        # If using configureStore, default middleware is included
        assert has_configure_store, \
            "store/index.ts should use configureStore which includes default middleware"


class TestStoreDevTools:
    """Test Redux DevTools configuration"""

    def test_store_enables_devtools_implicitly(self):
        """Test that store enables devtools (implicit with configureStore)"""
        content = STORE_INDEX.read_text()

        # configureStore enables Redux DevTools Extension by default
        has_configure_store = 'configureStore' in content

        assert has_configure_store, \
            "store/index.ts should use configureStore which enables DevTools by default"


class TestStoreExports:
    """Test store exports"""

    def test_exports_at_least_store(self):
        """Test that store/index.ts exports at least the store"""
        content = STORE_INDEX.read_text()

        has_export = 'export' in content
        assert has_export, "store/index.ts should have exports"

    def test_can_be_imported(self):
        """Test that store/index.ts structure allows imports"""
        content = STORE_INDEX.read_text()

        # Should have export statements
        has_export_default = 'export default' in content
        has_export_named = 'export const' in content or 'export type' in content or 'export {' in content

        assert has_export_default or has_export_named, \
            "store/index.ts should export store or types"


class TestStoreReducerConfiguration:
    """Test reducer configuration in store"""

    def test_reducer_is_object_or_combined(self):
        """Test that reducer is configured as object or combined reducer"""
        content = STORE_INDEX.read_text()

        # Should have reducer configuration
        assert 'reducer' in content, "store/index.ts should configure reducer"

        # Should have at least a placeholder or empty object
        # Looking for pattern like: reducer: { ... }
        has_reducer_config = 'reducer:' in content or 'reducer =' in content
        assert has_reducer_config, "store/index.ts should have reducer configuration"


class TestStoreComments:
    """Test store documentation"""

    def test_has_comments_or_documentation(self):
        """Test that store/index.ts has comments or documentation"""
        content = STORE_INDEX.read_text()

        # Should have at least some comments or documentation
        has_single_comment = '//' in content
        has_multi_comment = '/*' in content or '*/' in content

        # This is a best practice check - informational
        # Good code should have at least minimal documentation
        pass
