"""
Test suite for Navigation Commands Service.

Components:
- Destination setting
- POI search
- Route preferences
- Traffic queries
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestNavigationCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class NavigationCommandsService' in service_file_content


class TestDestinationSetting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_destination_method(self, service_file_content):
        assert 'def set_destination(' in service_file_content

    def test_has_search_poi_method(self, service_file_content):
        assert 'def search_poi(' in service_file_content

    def test_has_set_home_work_method(self, service_file_content):
        assert 'def set_home_work(' in service_file_content


class TestRoutePreferences:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_set_route_preferences_method(self, service_file_content):
        assert 'def set_route_preferences(' in service_file_content

    def test_has_plan_multi_stop_method(self, service_file_content):
        assert 'def plan_multi_stop(' in service_file_content

    def test_has_manage_waypoints_method(self, service_file_content):
        assert 'def manage_waypoints(' in service_file_content


class TestTrafficQueries:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_query_traffic_method(self, service_file_content):
        assert 'def query_traffic(' in service_file_content

    def test_has_get_eta_method(self, service_file_content):
        assert 'def get_eta(' in service_file_content

    def test_has_search_along_route_method(self, service_file_content):
        assert 'def search_along_route(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_navigation_commands_config_method(self, service_file_content):
        assert 'def get_navigation_commands_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'navigation_commands_service.py'
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
            '..', 'backend', 'services', 'navigation_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class NavigationCommandsService' in service_file_content:
            idx = service_file_content.find('class NavigationCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
