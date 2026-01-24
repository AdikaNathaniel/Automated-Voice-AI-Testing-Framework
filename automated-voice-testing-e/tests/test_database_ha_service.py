"""
Test suite for Database HA Service.

Components:
- Primary-replica setup
- Automatic failover
- Read replica routing
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestDatabaseHAServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class DatabaseHAService' in service_file_content


class TestPrimaryReplicaSetup:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_primary_method(self, service_file_content):
        assert 'def configure_primary(' in service_file_content

    def test_has_add_replica_method(self, service_file_content):
        assert 'def add_replica(' in service_file_content

    def test_has_get_replication_status_method(self, service_file_content):
        assert 'def get_replication_status(' in service_file_content


class TestAutomaticFailover:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_failover_method(self, service_file_content):
        assert 'def configure_failover(' in service_file_content

    def test_has_trigger_failover_method(self, service_file_content):
        assert 'def trigger_failover(' in service_file_content

    def test_has_get_failover_status_method(self, service_file_content):
        assert 'def get_failover_status(' in service_file_content


class TestReadReplicaRouting:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_read_routing_method(self, service_file_content):
        assert 'def configure_read_routing(' in service_file_content

    def test_has_get_read_replica_method(self, service_file_content):
        assert 'def get_read_replica(' in service_file_content

    def test_has_balance_read_load_method(self, service_file_content):
        assert 'def balance_read_load(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_database_ha_config_method(self, service_file_content):
        assert 'def get_database_ha_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'database_ha_service.py'
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
            '..', 'backend', 'services', 'database_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class DatabaseHAService' in service_file_content:
            idx = service_file_content.find('class DatabaseHAService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
