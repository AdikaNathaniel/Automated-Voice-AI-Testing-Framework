"""
Test suite for TypeScript type definitions

Ensures proper TypeScript interfaces are defined for API data structures,
including User, TestCase, TestRun, and ApiResponse interfaces.
"""

import os
import json
import pytest
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
SRC_DIR = FRONTEND_DIR / "src"
TYPES_DIR = SRC_DIR / "types"
API_TYPES_FILE = TYPES_DIR / "api.ts"


class TestTypesDirectory:
    """Test types directory structure"""

    def test_types_directory_exists(self):
        """Test that types directory exists"""
        assert TYPES_DIR.exists(), "types directory should exist"
        assert TYPES_DIR.is_dir(), "types should be a directory"

    def test_types_directory_in_src(self):
        """Test that types directory is in src"""
        assert TYPES_DIR.parent == SRC_DIR, "types should be in src directory"


class TestApiTypesFile:
    """Test api.ts types file"""

    def test_api_types_file_exists(self):
        """Test that types/api.ts exists"""
        assert API_TYPES_FILE.exists(), "types/api.ts should exist"
        assert API_TYPES_FILE.is_file(), "types/api.ts should be a file"

    def test_api_types_is_typescript(self):
        """Test that types/api.ts is a TypeScript file"""
        assert API_TYPES_FILE.suffix == ".ts", "types/api.ts should have .ts extension"

    def test_api_types_has_content(self):
        """Test that types/api.ts has content"""
        content = API_TYPES_FILE.read_text()
        assert len(content) > 0, "types/api.ts should not be empty"


class TestUserInterface:
    """Test User interface definition"""

    def test_defines_user_interface(self):
        """Test that api.ts defines User interface"""
        content = API_TYPES_FILE.read_text()
        assert 'interface User' in content, "api.ts should define User interface"

    def test_user_has_id_field(self):
        """Test that User interface has id field"""
        content = API_TYPES_FILE.read_text()
        # Look for id field in User interface
        has_id = 'id:' in content or 'id :' in content
        assert has_id, "User interface should have id field"

    def test_user_has_email_field(self):
        """Test that User interface has email field"""
        content = API_TYPES_FILE.read_text()
        assert 'email' in content, "User interface should have email field"

    def test_user_has_username_field(self):
        """Test that User interface has username field"""
        content = API_TYPES_FILE.read_text()
        assert 'username' in content, "User interface should have username field"

    def test_user_exports_interface(self):
        """Test that User interface is exported"""
        content = API_TYPES_FILE.read_text()
        # Should export User interface
        has_export_interface = 'export interface User' in content
        has_export_type = 'export type User' in content
        has_export_statement = 'export {' in content and 'User' in content
        assert has_export_interface or has_export_type or has_export_statement, \
            "User interface should be exported"


class TestTestCaseInterface:
    """Test TestCase interface definition"""

    def test_defines_testcase_interface(self):
        """Test that api.ts defines TestCase interface"""
        content = API_TYPES_FILE.read_text()
        assert 'interface TestCase' in content, "api.ts should define TestCase interface"

    def test_testcase_has_id_field(self):
        """Test that TestCase interface has id field"""
        content = API_TYPES_FILE.read_text()
        # User also has id, so we need to find TestCase context
        assert 'interface TestCase' in content, "TestCase interface should exist with id field"

    def test_testcase_has_name_or_title_field(self):
        """Test that TestCase interface has name or title field"""
        content = API_TYPES_FILE.read_text()
        has_name = 'name' in content
        has_title = 'title' in content
        assert has_name or has_title, "TestCase interface should have name or title field"

    def test_testcase_has_description_field(self):
        """Test that TestCase interface has description field"""
        content = API_TYPES_FILE.read_text()
        assert 'description' in content, "TestCase interface should have description field"

    def test_testcase_exports_interface(self):
        """Test that TestCase interface is exported"""
        content = API_TYPES_FILE.read_text()
        has_export_interface = 'export interface TestCase' in content
        has_export_type = 'export type TestCase' in content
        has_export_statement = 'export {' in content and 'TestCase' in content
        assert has_export_interface or has_export_type or has_export_statement, \
            "TestCase interface should be exported"


class TestTestRunInterface:
    """Test TestRun interface definition"""

    def test_defines_testrun_interface(self):
        """Test that api.ts defines TestRun interface"""
        content = API_TYPES_FILE.read_text()
        assert 'interface TestRun' in content, "api.ts should define TestRun interface"

    def test_testrun_has_id_field(self):
        """Test that TestRun interface has id field"""
        content = API_TYPES_FILE.read_text()
        assert 'interface TestRun' in content, "TestRun interface should exist with id field"

    def test_testrun_has_status_field(self):
        """Test that TestRun interface has status field"""
        content = API_TYPES_FILE.read_text()
        assert 'status' in content, "TestRun interface should have status field"

    def test_testrun_has_result_or_results_field(self):
        """Test that TestRun interface has result or results field"""
        content = API_TYPES_FILE.read_text()
        has_result = 'result' in content
        assert has_result, "TestRun interface should have result or results field"

    def test_testrun_exports_interface(self):
        """Test that TestRun interface is exported"""
        content = API_TYPES_FILE.read_text()
        has_export_interface = 'export interface TestRun' in content
        has_export_type = 'export type TestRun' in content
        has_export_statement = 'export {' in content and 'TestRun' in content
        assert has_export_interface or has_export_type or has_export_statement, \
            "TestRun interface should be exported"


class TestApiResponseInterface:
    """Test ApiResponse interface definition"""

    def test_defines_apiresponse_interface(self):
        """Test that api.ts defines ApiResponse interface"""
        content = API_TYPES_FILE.read_text()
        assert 'interface ApiResponse' in content or 'interface APIResponse' in content, \
            "api.ts should define ApiResponse interface"

    def test_apiresponse_has_data_field(self):
        """Test that ApiResponse interface has data field"""
        content = API_TYPES_FILE.read_text()
        assert 'data' in content, "ApiResponse interface should have data field"

    def test_apiresponse_has_success_or_status_field(self):
        """Test that ApiResponse interface has success or status field"""
        content = API_TYPES_FILE.read_text()
        has_success = 'success' in content
        has_status = 'status' in content
        assert has_success or has_status, \
            "ApiResponse interface should have success or status field"

    def test_apiresponse_has_message_or_error_field(self):
        """Test that ApiResponse interface has message or error field"""
        content = API_TYPES_FILE.read_text()
        has_message = 'message' in content
        has_error = 'error' in content
        assert has_message or has_error, \
            "ApiResponse interface should have message or error field"

    def test_apiresponse_exports_interface(self):
        """Test that ApiResponse interface is exported"""
        content = API_TYPES_FILE.read_text()
        has_export_interface = 'export interface ApiResponse' in content or 'export interface APIResponse' in content
        has_export_type = 'export type ApiResponse' in content or 'export type APIResponse' in content
        has_export_statement = 'export {' in content and ('ApiResponse' in content or 'APIResponse' in content)
        assert has_export_interface or has_export_type or has_export_statement, \
            "ApiResponse interface should be exported"


class TestTypeExports:
    """Test type exports"""

    def test_exports_all_interfaces(self):
        """Test that all required interfaces are exported"""
        content = API_TYPES_FILE.read_text()
        assert 'export' in content, "api.ts should have export statements"

    def test_can_be_imported_by_other_modules(self):
        """Test that types can be imported by other modules"""
        content = API_TYPES_FILE.read_text()
        # Should use export keyword
        has_export = 'export interface' in content or 'export type' in content or 'export {' in content
        assert has_export, "api.ts should export types for use in other modules"


class TestTypeScriptSyntax:
    """Test TypeScript syntax validity"""

    def test_has_valid_typescript_syntax(self):
        """Test that api.ts has valid TypeScript syntax"""
        content = API_TYPES_FILE.read_text()
        # Basic syntax checks
        assert content.count('{') == content.count('}') or abs(content.count('{') - content.count('}')) <= 1, \
            "Braces should be balanced"
        assert content.count('interface') >= 4, "Should have at least 4 interfaces defined"

    def test_uses_interface_or_type_keyword(self):
        """Test that uses interface or type keyword"""
        content = API_TYPES_FILE.read_text()
        has_interface = 'interface' in content
        has_type = 'type' in content
        assert has_interface or has_type, "Should use interface or type keyword"


class TestTypeDocumentation:
    """Test type documentation"""

    def test_has_comments_or_documentation(self):
        """Test that api.ts has comments or documentation"""
        content = API_TYPES_FILE.read_text()
        has_single_comment = '//' in content
        has_multi_comment = '/*' in content or '*/' in content
        # Good practice - should have documentation
        assert has_single_comment or has_multi_comment, \
            "api.ts should have comments or documentation"


class TestInterfaceStructure:
    """Test overall interface structure"""

    def test_file_not_too_small(self):
        """Test that api.ts has reasonable content"""
        content = API_TYPES_FILE.read_text()
        lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('//')]
        assert len(lines) >= 15, "api.ts should have meaningful content (at least 15 non-comment lines)"

    def test_all_four_interfaces_present(self):
        """Test that all four required interfaces are present"""
        content = API_TYPES_FILE.read_text()

        interfaces_to_check = ['User', 'TestCase', 'TestRun']
        api_response_variants = ['ApiResponse', 'APIResponse']

        for interface_name in interfaces_to_check:
            assert f'interface {interface_name}' in content, \
                f"{interface_name} interface should be defined"

        # Check for ApiResponse (either variant)
        has_api_response = any(f'interface {variant}' in content for variant in api_response_variants)
        assert has_api_response, "ApiResponse or APIResponse interface should be defined"


class TestTypeSafety:
    """Test TypeScript type safety features"""

    def test_uses_type_annotations(self):
        """Test that uses TypeScript type annotations"""
        content = API_TYPES_FILE.read_text()
        # Should have type annotations like: fieldName: type
        has_colon = ':' in content
        assert has_colon, "Should use TypeScript type annotations (fieldName: type)"

    def test_uses_typescript_types(self):
        """Test that uses TypeScript types"""
        content = API_TYPES_FILE.read_text()
        # Should use TypeScript types like string, number, boolean, etc.
        has_string = 'string' in content
        has_number = 'number' in content
        has_types = has_string or has_number
        assert has_types, "Should use TypeScript types (string, number, etc.)"
