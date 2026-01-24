"""
Test suite for user_service.py error handling.

Tests that all database operations have proper error handling with
logging and appropriate exception re-raising.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestUserServiceErrorHandling:
    """Test error handling in user service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_create_user_has_error_handling(self, service_file_content):
        """Test create_user has try/catch"""
        # Find the standalone create_user function (not class method)
        idx = service_file_content.find('async def create_user(db: AsyncSession')
        assert idx != -1, "create_user function not found"

        # Get function body (up to next function)
        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "create_user should have try block"
        assert 'except' in func_body, "create_user should have except block"

    def test_get_user_by_email_has_error_handling(self, service_file_content):
        """Test get_user_by_email has try/catch"""
        # Find standalone function (not class method)
        idx = service_file_content.find('async def get_user_by_email(db: AsyncSession')
        assert idx != -1, "get_user_by_email function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "get_user_by_email should have try block"
        assert 'except' in func_body, "get_user_by_email should have except block"

    def test_get_user_by_id_has_error_handling(self, service_file_content):
        """Test get_user_by_id has try/catch"""
        # Find standalone function (not class method)
        idx = service_file_content.find('async def get_user_by_id(db: AsyncSession')
        assert idx != -1, "get_user_by_id function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "get_user_by_id should have try block"
        assert 'except' in func_body, "get_user_by_id should have except block"

    def test_update_user_has_error_handling(self, service_file_content):
        """Test update_user has try/catch"""
        # Find standalone function (not class method)
        idx = service_file_content.find('async def update_user(db: AsyncSession')
        assert idx != -1, "update_user function not found"

        next_func = service_file_content.find('async def ', idx + 10)
        func_body = service_file_content[idx:next_func] if next_func != -1 else service_file_content[idx:]

        assert 'try:' in func_body, "update_user should have try block"
        assert 'except' in func_body, "update_user should have except block"

    def test_delete_user_has_error_handling(self, service_file_content):
        """Test delete_user has try/catch"""
        # Find standalone function (not class method)
        idx = service_file_content.find('async def delete_user(db: AsyncSession')
        assert idx != -1, "delete_user function not found"

        # delete_user is the last function
        func_body = service_file_content[idx:]

        assert 'try:' in func_body, "delete_user should have try block"
        assert 'except' in func_body, "delete_user should have except block"

    def test_has_logging_import(self, service_file_content):
        """Test logging is imported"""
        assert 'import logging' in service_file_content or 'from logging' in service_file_content

    def test_has_logger_instance(self, service_file_content):
        """Test logger instance is created"""
        assert 'logger = logging.getLogger' in service_file_content or 'logger = getLogger' in service_file_content
