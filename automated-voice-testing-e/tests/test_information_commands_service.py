"""
Test suite for Information Commands Service.

Components:
- Weather queries
- Traffic conditions
- News and sports
- Calendar and reminders
- General information
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestInformationCommandsServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class InformationCommandsService' in service_file_content


class TestWeatherQueries:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_current_weather_method(self, service_file_content):
        assert 'def get_current_weather(' in service_file_content

    def test_has_get_weather_forecast_method(self, service_file_content):
        assert 'def get_weather_forecast(' in service_file_content

    def test_has_get_destination_weather_method(self, service_file_content):
        assert 'def get_destination_weather(' in service_file_content


class TestTrafficAndNews:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_traffic_conditions_method(self, service_file_content):
        assert 'def get_traffic_conditions(' in service_file_content

    def test_has_get_news_briefing_method(self, service_file_content):
        assert 'def get_news_briefing(' in service_file_content

    def test_has_get_sports_scores_method(self, service_file_content):
        assert 'def get_sports_scores(' in service_file_content


class TestFinanceAndCalendar:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_stock_quote_method(self, service_file_content):
        assert 'def get_stock_quote(' in service_file_content

    def test_has_get_calendar_events_method(self, service_file_content):
        assert 'def get_calendar_events(' in service_file_content

    def test_has_create_reminder_method(self, service_file_content):
        assert 'def create_reminder(' in service_file_content


class TestGeneralInformation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_answer_question_method(self, service_file_content):
        assert 'def answer_question(' in service_file_content

    def test_has_convert_units_method(self, service_file_content):
        assert 'def convert_units(' in service_file_content

    def test_has_get_time_info_method(self, service_file_content):
        assert 'def get_time_info(' in service_file_content


class TestTravelServices:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_flight_status_method(self, service_file_content):
        assert 'def get_flight_status(' in service_file_content

    def test_has_make_reservation_method(self, service_file_content):
        assert 'def make_reservation(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'information_commands_service.py'
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
            '..', 'backend', 'services', 'information_commands_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class InformationCommandsService' in service_file_content:
            idx = service_file_content.find('class InformationCommandsService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
