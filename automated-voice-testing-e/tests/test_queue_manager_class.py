"""
Test suite for QueueManager class-based implementation.

This ensures the queue_manager.py has been converted from
function-based to class-based pattern.
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestQueueManagerClassExists:
    """Test that class-based service exists"""

    def test_service_file_exists(self):
        """Test that queue_manager.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_manager.py'
        )
        assert os.path.exists(service_file)

    def test_class_exists(self):
        """Test that QueueManager class exists"""
        from services.queue_manager import QueueManager
        assert QueueManager is not None

    def test_class_is_importable(self):
        """Test class can be instantiated"""
        from services.queue_manager import QueueManager
        service = QueueManager()
        assert service is not None


class TestQueueManagerMethods:
    """Test that class has required methods"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.queue_manager import QueueManager
        return QueueManager()

    def test_has_enqueue_test_method(self, service):
        """Test enqueue_test method exists"""
        assert hasattr(service, 'enqueue_test')
        assert callable(getattr(service, 'enqueue_test'))

    def test_has_dequeue_test_method(self, service):
        """Test dequeue_test method exists"""
        assert hasattr(service, 'dequeue_test')
        assert callable(getattr(service, 'dequeue_test'))

    def test_has_update_queue_status_method(self, service):
        """Test update_queue_status method exists"""
        assert hasattr(service, 'update_queue_status')
        assert callable(getattr(service, 'update_queue_status'))

    def test_has_get_queue_stats_method(self, service):
        """Test get_queue_stats method exists"""
        assert hasattr(service, 'get_queue_stats')
        assert callable(getattr(service, 'get_queue_stats'))


class TestQueueManagerConfiguration:
    """Test service configuration"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        from services.queue_manager import QueueManager
        return QueueManager()

    def test_has_valid_statuses(self, service):
        """Test service has valid_statuses attribute"""
        assert hasattr(service, 'valid_statuses')
        assert 'queued' in service.valid_statuses


class TestBackwardCompatibility:
    """Test that function-based API still works"""

    def test_enqueue_test_function_exists(self):
        """Test enqueue_test function still exists"""
        from services.queue_manager import enqueue_test
        assert enqueue_test is not None
        assert callable(enqueue_test)

    def test_dequeue_test_function_exists(self):
        """Test dequeue_test function still exists"""
        from services.queue_manager import dequeue_test
        assert dequeue_test is not None
        assert callable(dequeue_test)

    def test_get_queue_stats_function_exists(self):
        """Test get_queue_stats function still exists"""
        from services.queue_manager import get_queue_stats
        assert get_queue_stats is not None
        assert callable(get_queue_stats)


class TestDocumentation:
    """Test documentation quality"""

    @pytest.fixture
    def service_file_content(self):
        """Read the service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_manager.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_class_docstring(self, service_file_content):
        """Test class has docstring"""
        assert 'class QueueManager' in service_file_content
        idx = service_file_content.find('class QueueManager')
        class_section = service_file_content[idx:idx+500]
        assert '"""' in class_section
