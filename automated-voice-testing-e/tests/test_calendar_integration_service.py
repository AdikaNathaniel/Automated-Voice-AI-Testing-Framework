"""
Test suite for Calendar and Schedule Integration Service.

Components:
- Next appointment navigation
- Meeting reminders
- Schedule conflicts
- Participant contact info
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestCalendarIntegrationServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class CalendarIntegrationService' in service_file_content


class TestAppointmentNavigation:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_next_appointment_method(self, service_file_content):
        assert 'def get_next_appointment(' in service_file_content

    def test_has_navigate_to_appointment_method(self, service_file_content):
        assert 'def navigate_to_appointment(' in service_file_content


class TestMeetingReminders:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_meeting_reminders_method(self, service_file_content):
        assert 'def get_meeting_reminders(' in service_file_content

    def test_has_set_reminder_method(self, service_file_content):
        assert 'def set_reminder(' in service_file_content


class TestScheduleConflicts:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_check_schedule_conflicts_method(self, service_file_content):
        assert 'def check_schedule_conflicts(' in service_file_content

    def test_has_get_available_slots_method(self, service_file_content):
        assert 'def get_available_slots(' in service_file_content


class TestParticipantInfo:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_participant_info_method(self, service_file_content):
        assert 'def get_participant_info(' in service_file_content

    def test_has_call_participant_method(self, service_file_content):
        assert 'def call_participant(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_calendar_integration_config_method(self, service_file_content):
        assert 'def get_calendar_integration_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'calendar_integration_service.py'
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
            '..', 'backend', 'services', 'calendar_integration_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class CalendarIntegrationService' in service_file_content:
            idx = service_file_content.find('class CalendarIntegrationService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
