"""
Test suite for Scheduled Report Service.

Components:
- Daily/weekly/monthly schedules
- Email delivery
- Slack delivery
- S3/cloud storage delivery
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestScheduledReportServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class ScheduledReportService' in service_file_content


class TestScheduleManagement:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_create_schedule_method(self, service_file_content):
        assert 'def create_schedule(' in service_file_content

    def test_has_get_schedules_method(self, service_file_content):
        assert 'def get_schedules(' in service_file_content

    def test_has_update_schedule_method(self, service_file_content):
        assert 'def update_schedule(' in service_file_content


class TestEmailDelivery:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_deliver_via_email_method(self, service_file_content):
        assert 'def deliver_via_email(' in service_file_content


class TestSlackDelivery:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_deliver_via_slack_method(self, service_file_content):
        assert 'def deliver_via_slack(' in service_file_content


class TestS3Delivery:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_deliver_to_s3_method(self, service_file_content):
        assert 'def deliver_to_s3(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_schedule_config_method(self, service_file_content):
        assert 'def get_schedule_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'scheduled_report_service.py'
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
            '..', 'backend', 'services', 'scheduled_report_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class ScheduledReportService' in service_file_content:
            idx = service_file_content.find('class ScheduledReportService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
