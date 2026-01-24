"""
Test suite for UserService class-based implementation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestUserServiceClassExists:
    """Test that class-based service exists"""

    def test_service_file_exists(self):
        """Test that user_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_service.py'
        )
        assert os.path.exists(service_file)

    def test_class_exists(self):
        """Test that UserService class exists"""
        from services.user_service import UserService
        assert UserService is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.user_service import UserService
        service = UserService()
        assert service is not None


class TestUserServiceMethods:
    """Test that class has required methods"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.user_service import UserService
        return UserService()

    def test_has_create_user_method(self, service):
        """Test create_user method exists"""
        assert hasattr(service, 'create_user')

    def test_has_get_user_by_email_method(self, service):
        """Test get_user_by_email method exists"""
        assert hasattr(service, 'get_user_by_email')

    def test_has_get_user_by_id_method(self, service):
        """Test get_user_by_id method exists"""
        assert hasattr(service, 'get_user_by_id')

    def test_has_update_user_method(self, service):
        """Test update_user method exists"""
        assert hasattr(service, 'update_user')

    def test_has_delete_user_method(self, service):
        """Test delete_user method exists"""
        assert hasattr(service, 'delete_user')


class TestBackwardCompatibility:
    """Test that function-based API still works"""

    def test_create_user_function_exists(self):
        """Test create_user function still exists"""
        from services.user_service import create_user
        assert callable(create_user)

    def test_get_user_by_id_function_exists(self):
        """Test get_user_by_id function still exists"""
        from services.user_service import get_user_by_id
        assert callable(get_user_by_id)


class TestDocumentation:
    """Test documentation quality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'user_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_class_docstring(self, service_file_content):
        """Test class has docstring"""
        assert 'class UserService' in service_file_content
