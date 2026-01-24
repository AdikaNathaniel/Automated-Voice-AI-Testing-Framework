"""
Test suite for Location-aware Commands Service.

Components:
- "Near me" / "Nearby" queries
- Context from current location
- Destination-aware suggestions
- Geofencing triggers
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestLocationAwareCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class LocationAwareCommandsService' in service_file_content


class TestNearbyQueries:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_process_nearby_query_method(self, service_file_content):
        assert 'def process_nearby_query(' in service_file_content

    def test_has_find_near_me_method(self, service_file_content):
        assert 'def find_near_me(' in service_file_content


class TestLocationContext:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_location_context_method(self, service_file_content):
        assert 'def get_location_context(' in service_file_content

    def test_has_update_current_location_method(self, service_file_content):
        assert 'def update_current_location(' in service_file_content


class TestDestinationSuggestions:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_destination_suggestions_method(self, service_file_content):
        assert 'def get_destination_suggestions(' in service_file_content

    def test_has_set_destination_method(self, service_file_content):
        assert 'def set_destination(' in service_file_content


class TestGeofencing:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_geofence_trigger_method(self, service_file_content):
        assert 'def check_geofence_trigger(' in service_file_content

    def test_has_set_geofence_method(self, service_file_content):
        assert 'def set_geofence(' in service_file_content

    def test_has_get_active_geofences_method(self, service_file_content):
        assert 'def get_active_geofences(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_location_aware_config_method(self, service_file_content):
        assert 'def get_location_aware_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'location_aware_commands_service.py'
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
            '..', 'backend', 'services', 'location_aware_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class LocationAwareCommandsService' in service_file_content:
            idx = service_file_content.find('class LocationAwareCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
