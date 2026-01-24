"""
Test suite for Call Lifecycle Service.

This service manages call lifecycle operations for
testing voice AI systems.

Components:
- Call setup latency
- Call hold/resume
- Call transfer testing
- Call termination handling
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCallLifecycleServiceExists:
    """Test that call lifecycle service exists"""

    @pytest.fixture
    def service_file_content(self):
        """Read the call lifecycle service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'call_lifecycle_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        """Test that call_lifecycle_service.py exists"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'call_lifecycle_service.py'
        )
        assert os.path.exists(service_file), (
            "call_lifecycle_service.py should exist"
        )

    def test_service_class_exists(self, service_file_content):
        """Test that CallLifecycleService class exists"""
        assert 'class CallLifecycleService' in service_file_content


class TestCallSetupLatency:
    """Test call setup latency"""

    @pytest.fixture
    def service_class(self):
        """Get the CallLifecycleService class"""
        from services.call_lifecycle_service import CallLifecycleService
        return CallLifecycleService

    @pytest.fixture
    def service_file_content(self):
        """Read the call lifecycle service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'call_lifecycle_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_initiate_call_method(self, service_file_content):
        """Test initiate_call method exists"""
        assert 'def initiate_call(' in service_file_content

    def test_has_measure_setup_latency_method(self, service_class):
        """Test measure_setup_latency method exists"""
        assert hasattr(service_class, 'measure_setup_latency')
        assert callable(getattr(service_class, 'measure_setup_latency'))

    def test_has_get_call_state_method(self, service_file_content):
        """Test get_call_state method exists"""
        assert 'def get_call_state(' in service_file_content


class TestCallHoldResume:
    """Test call hold/resume"""

    @pytest.fixture
    def service_class(self):
        """Get the CallLifecycleService class"""
        from services.call_lifecycle_service import CallLifecycleService
        return CallLifecycleService

    def test_has_hold_call_method(self, service_class):
        """Test hold_call method exists"""
        assert hasattr(service_class, 'hold_call')
        assert callable(getattr(service_class, 'hold_call'))

    def test_has_resume_call_method(self, service_class):
        """Test resume_call method exists"""
        assert hasattr(service_class, 'resume_call')
        assert callable(getattr(service_class, 'resume_call'))

    def test_has_get_hold_duration_method(self, service_class):
        """Test get_hold_duration method exists"""
        assert hasattr(service_class, 'get_hold_duration')
        assert callable(getattr(service_class, 'get_hold_duration'))


class TestCallTransfer:
    """Test call transfer"""

    @pytest.fixture
    def service_class(self):
        """Get the CallLifecycleService class"""
        from services.call_lifecycle_service import CallLifecycleService
        return CallLifecycleService

    def test_has_transfer_call_method(self, service_class):
        """Test transfer_call method exists"""
        assert hasattr(service_class, 'transfer_call')
        assert callable(getattr(service_class, 'transfer_call'))

    def test_has_blind_transfer_method(self, service_class):
        """Test blind_transfer method exists"""
        assert hasattr(service_class, 'blind_transfer')
        assert callable(getattr(service_class, 'blind_transfer'))

    def test_has_attended_transfer_method(self, service_class):
        """Test attended_transfer method exists"""
        assert hasattr(service_class, 'attended_transfer')
        assert callable(getattr(service_class, 'attended_transfer'))


class TestCallTermination:
    """Test call termination handling"""

    @pytest.fixture
    def service_class(self):
        """Get the CallLifecycleService class"""
        from services.call_lifecycle_service import CallLifecycleService
        return CallLifecycleService

    def test_has_terminate_call_method(self, service_class):
        """Test terminate_call method exists"""
        assert hasattr(service_class, 'terminate_call')
        assert callable(getattr(service_class, 'terminate_call'))

    def test_has_get_termination_reason_method(self, service_class):
        """Test get_termination_reason method exists"""
        assert hasattr(service_class, 'get_termination_reason')
        assert callable(getattr(service_class, 'get_termination_reason'))

    def test_has_get_call_duration_method(self, service_class):
        """Test get_call_duration method exists"""
        assert hasattr(service_class, 'get_call_duration')
        assert callable(getattr(service_class, 'get_call_duration'))


class TestCallMetrics:
    """Test call metrics collection"""

    @pytest.fixture
    def service_class(self):
        """Get the CallLifecycleService class"""
        from services.call_lifecycle_service import CallLifecycleService
        return CallLifecycleService

    def test_has_get_call_metrics_method(self, service_class):
        """Test get_call_metrics method exists"""
        assert hasattr(service_class, 'get_call_metrics')
        assert callable(getattr(service_class, 'get_call_metrics'))

    def test_has_get_call_history_method(self, service_class):
        """Test get_call_history method exists"""
        assert hasattr(service_class, 'get_call_history')
        assert callable(getattr(service_class, 'get_call_history'))


class TestTypeHints:
    """Test type hints for call lifecycle service"""

    @pytest.fixture
    def service_file_content(self):
        """Read the call lifecycle service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'call_lifecycle_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        """Test typing modules are imported"""
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        """Test Dict type hint is used"""
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        """Test List type hint is used"""
        assert 'List[' in service_file_content


class TestDocstrings:
    """Test comprehensive documentation"""

    @pytest.fixture
    def service_file_content(self):
        """Read the call lifecycle service file"""
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'call_lifecycle_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        """Test module has docstring"""
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        """Test class has docstring"""
        if 'class CallLifecycleService' in service_file_content:
            idx = service_file_content.find('class CallLifecycleService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
