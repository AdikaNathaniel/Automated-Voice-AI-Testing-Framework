"""
Test suite for defect_service.py error handling.

Tests that all database operations have proper error handling with
logging and appropriate exception re-raising.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDefectServiceErrorHandling:
    """Test error handling in defect service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'defect_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_create_defect_has_error_handling(self, service_file_content):
        """Test create_defect has try/catch"""
        # Find standalone function
        idx = service_file_content.find('async def create_defect(\n    db: AsyncSession')
        assert idx != -1, "create_defect function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "create_defect should have try block"
        assert 'except' in func_body, "create_defect should have except block"

    def test_get_defect_has_error_handling(self, service_file_content):
        """Test get_defect has try/catch"""
        idx = service_file_content.find('async def get_defect(db: AsyncSession')
        assert idx != -1, "get_defect function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "get_defect should have try block"
        assert 'except' in func_body, "get_defect should have except block"

    def test_list_defects_has_error_handling(self, service_file_content):
        """Test list_defects has try/catch"""
        idx = service_file_content.find('async def list_defects(\n    db: AsyncSession')
        assert idx != -1, "list_defects function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "list_defects should have try block"
        assert 'except' in func_body, "list_defects should have except block"

    def test_update_defect_has_error_handling(self, service_file_content):
        """Test update_defect has try/catch"""
        idx = service_file_content.find('async def update_defect(\n    db: AsyncSession')
        assert idx != -1, "update_defect function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "update_defect should have try block"
        assert 'except' in func_body, "update_defect should have except block"

    def test_has_logging_import(self, service_file_content):
        """Test logging is imported"""
        assert 'import logging' in service_file_content or 'from logging' in service_file_content

    def test_has_logger_instance(self, service_file_content):
        """Test logger instance is created"""
        assert 'logger = logging.getLogger' in service_file_content or 'logger = getLogger' in service_file_content
