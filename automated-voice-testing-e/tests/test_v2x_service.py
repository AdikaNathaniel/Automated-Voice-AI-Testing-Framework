"""
Test suite for Vehicle-to-Everything (V2X) Service.

Components:
- V2I (Infrastructure) communication
- Traffic signal information
- Parking availability feeds
- Road hazard warnings
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestV2XServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class V2XService' in service_file_content


class TestV2ICommunication:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_connect_to_infrastructure_method(self, service_file_content):
        assert 'def connect_to_infrastructure(' in service_file_content

    def test_has_send_v2i_message_method(self, service_file_content):
        assert 'def send_v2i_message(' in service_file_content


class TestTrafficSignalInfo:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_signal_phase_method(self, service_file_content):
        assert 'def get_signal_phase(' in service_file_content

    def test_has_predict_signal_timing_method(self, service_file_content):
        assert 'def predict_signal_timing(' in service_file_content


class TestParkingAvailability:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_parking_availability_method(self, service_file_content):
        assert 'def get_parking_availability(' in service_file_content

    def test_has_reserve_parking_spot_method(self, service_file_content):
        assert 'def reserve_parking_spot(' in service_file_content


class TestRoadHazardWarnings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_hazard_warnings_method(self, service_file_content):
        assert 'def get_hazard_warnings(' in service_file_content

    def test_has_report_hazard_method(self, service_file_content):
        assert 'def report_hazard(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_v2x_config_method(self, service_file_content):
        assert 'def get_v2x_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_imports_typing_modules(self, service_file_content):
        assert 'from typing import' in service_file_content

    def test_uses_dict_type_hint(self, service_file_content):
        assert 'Dict[' in service_file_content

    def test_uses_list_type_hint(self, service_file_content):
        assert 'List[' in service_file_content


class TestDocstrings:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'v2x_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class V2XService' in service_file_content:
            idx = service_file_content.find('class V2XService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
