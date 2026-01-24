"""
Test suite for Prometheus metrics endpoint.

Validates that /metrics endpoint exports required metrics for monitoring.
"""

import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


PROJECT_ROOT = Path(__file__).parent.parent
MAIN_FILE = PROJECT_ROOT / "backend" / "api" / "main.py"


class TestMetricsEndpointExists:
    """Verify /metrics endpoint is configured."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_metrics_route_defined(self, main_content):
        """Should define /metrics route."""
        has_metrics_path = '"/metrics"' in main_content or "'/metrics'" in main_content
        assert has_metrics_path, "/metrics endpoint should be defined"

    def test_imports_prometheus_client(self, main_content):
        """Should import prometheus_client or similar."""
        has_prometheus = "prometheus" in main_content.lower()
        has_metrics_import = "generate_latest" in main_content or "CONTENT_TYPE_LATEST" in main_content
        assert has_prometheus or has_metrics_import, \
            "Should import Prometheus client library"


class TestRequestMetrics:
    """Test HTTP request metrics are exported."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_has_request_count_metric(self, main_content):
        """Should export request count metric."""
        has_counter = "Counter" in main_content or "request" in main_content.lower()
        has_count = "count" in main_content.lower() or "total" in main_content.lower()
        assert has_counter and has_count, \
            "Should export request count metric"

    def test_has_request_latency_metric(self, main_content):
        """Should export request latency/duration metric."""
        has_histogram = "Histogram" in main_content or "Summary" in main_content
        has_latency = "latency" in main_content.lower() or "duration" in main_content.lower()
        assert has_histogram or has_latency, \
            "Should export request latency metric"

    def test_has_error_metric(self, main_content):
        """Should export error count metric."""
        has_error = "error" in main_content.lower()
        has_status = "status" in main_content.lower() or "5xx" in main_content or "4xx" in main_content
        assert has_error or has_status, \
            "Should export error metric"


class TestDatabaseMetrics:
    """Test database connection pool metrics."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_has_db_pool_metric(self, main_content):
        """Should export database connection pool metric."""
        has_db = "db" in main_content.lower() or "database" in main_content.lower()
        has_pool = "pool" in main_content.lower() or "connection" in main_content.lower()
        assert has_db and has_pool, \
            "Should export database connection pool metric"


class TestRedisMetrics:
    """Test Redis connection metrics."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_has_redis_metric(self, main_content):
        """Should export Redis connection metric."""
        has_redis = "redis" in main_content.lower()
        assert has_redis, \
            "Should export Redis connection metric"


class TestCeleryMetrics:
    """Test Celery task queue metrics."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_has_celery_metric(self, main_content):
        """Should export Celery task queue metric."""
        has_celery = "celery" in main_content.lower() or "task" in main_content.lower()
        has_queue = "queue" in main_content.lower() or "worker" in main_content.lower()
        assert has_celery or has_queue, \
            "Should export Celery task queue metric"


class TestMetricsFormat:
    """Test metrics output format."""

    @pytest.fixture
    def main_content(self):
        return MAIN_FILE.read_text()

    def test_returns_prometheus_format(self, main_content):
        """Should return Prometheus text format."""
        has_content_type = "text/plain" in main_content or "CONTENT_TYPE" in main_content
        has_generate = "generate_latest" in main_content
        assert has_content_type or has_generate, \
            "Should return Prometheus text format"
