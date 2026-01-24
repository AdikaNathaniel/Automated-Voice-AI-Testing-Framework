"""
Test suite for Queue HA Service.

Components:
- RabbitMQ clustering
- Redis Sentinel/Cluster
- Message persistence
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestQueueHAServiceExists:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_service_file_exists(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        assert os.path.exists(service_file)

    def test_service_class_exists(self, service_file_content):
        assert 'class QueueHAService' in service_file_content


class TestRabbitMQClustering:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_rabbitmq_cluster_method(self, service_file_content):
        assert 'def configure_rabbitmq_cluster(' in service_file_content

    def test_has_add_rabbitmq_node_method(self, service_file_content):
        assert 'def add_rabbitmq_node(' in service_file_content

    def test_has_get_cluster_status_method(self, service_file_content):
        assert 'def get_cluster_status(' in service_file_content


class TestRedisSentinel:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_redis_sentinel_method(self, service_file_content):
        assert 'def configure_redis_sentinel(' in service_file_content

    def test_has_add_sentinel_node_method(self, service_file_content):
        assert 'def add_sentinel_node(' in service_file_content

    def test_has_get_sentinel_status_method(self, service_file_content):
        assert 'def get_sentinel_status(' in service_file_content


class TestMessagePersistence:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_configure_persistence_method(self, service_file_content):
        assert 'def configure_persistence(' in service_file_content

    def test_has_enable_durable_queues_method(self, service_file_content):
        assert 'def enable_durable_queues(' in service_file_content

    def test_has_get_persistence_status_method(self, service_file_content):
        assert 'def get_persistence_status(' in service_file_content


class TestConfiguration:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_has_get_queue_ha_config_method(self, service_file_content):
        assert 'def get_queue_ha_config(' in service_file_content


class TestTypeHints:
    @pytest.fixture
    def service_file_content(self):
        service_file = os.path.join(
            os.path.dirname(__file__),
            '..', 'backend', 'services', 'queue_ha_service.py'
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
            '..', 'backend', 'services', 'queue_ha_service.py'
        )
        with open(service_file, 'r') as f:
            return f.read()

    def test_module_docstring_exists(self, service_file_content):
        assert service_file_content.strip().startswith('"""')

    def test_class_docstring_exists(self, service_file_content):
        if 'class QueueHAService' in service_file_content:
            idx = service_file_content.find('class QueueHAService')
            class_section = service_file_content[idx:idx+500]
            assert '"""' in class_section
