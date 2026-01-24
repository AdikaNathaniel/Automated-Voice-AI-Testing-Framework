"""
Test Performance Testing Script

This module tests that the performance testing script can execute
load tests and measure system performance under concurrent load.

Test Coverage:
    - Performance testing script exists
    - Load test configuration
    - Concurrent execution testing
    - Response time measurement
    - Throughput measurement
    - Performance report generation
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest


# =============================================================================
# Module Existence Tests
# =============================================================================

class TestPerformanceTestingModule:
    """Test that performance testing module exists"""

    def test_performance_testing_script_exists(self):
        """Test that performance testing script exists"""
        # Arrange
        project_root = Path(__file__).parent.parent
        script_file = project_root / "backend" / "scripts" / "run_performance_tests.py"

        # Act & Assert
        assert script_file.exists(), "run_performance_tests.py should exist in backend/scripts/"
        assert script_file.is_file(), "run_performance_tests.py should be a file"


# =============================================================================
# Configuration Tests
# =============================================================================

class TestPerformanceTestConfiguration:
    """Test that performance test configuration is defined"""

    def test_has_load_test_config(self):
        """Test that load test configuration is defined"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'LOAD_TEST_CONFIG'), \
            "run_performance_tests should define LOAD_TEST_CONFIG"

    def test_config_has_concurrent_users(self):
        """Test that config specifies concurrent users"""
        # Arrange
        from scripts.run_performance_tests import LOAD_TEST_CONFIG

        # Act & Assert
        assert 'concurrent_users' in LOAD_TEST_CONFIG, \
            "Config should specify concurrent_users"
        assert LOAD_TEST_CONFIG['concurrent_users'] >= 10, \
            "Should support at least 10 concurrent users"

    def test_config_has_test_duration(self):
        """Test that config specifies test duration"""
        # Arrange
        from scripts.run_performance_tests import LOAD_TEST_CONFIG

        # Act & Assert
        assert 'duration_seconds' in LOAD_TEST_CONFIG, \
            "Config should specify duration_seconds"

    def test_config_has_endpoints_to_test(self):
        """Test that config specifies endpoints to test"""
        # Arrange
        from scripts.run_performance_tests import LOAD_TEST_CONFIG

        # Act & Assert
        assert 'endpoints' in LOAD_TEST_CONFIG, \
            "Config should specify endpoints to test"
        assert len(LOAD_TEST_CONFIG['endpoints']) > 0, \
            "Should have at least one endpoint to test"


# =============================================================================
# Load Testing Function Tests
# =============================================================================

class TestLoadTestingFunctions:
    """Test that load testing functions exist"""

    def test_has_run_load_test_function(self):
        """Test that run_load_test function exists"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'run_load_test'), \
            "run_performance_tests should have run_load_test function"
        assert callable(run_performance_tests.run_load_test), \
            "run_load_test should be callable"

    def test_has_measure_response_time_function(self):
        """Test that measure_response_time function exists"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'measure_response_time'), \
            "run_performance_tests should have measure_response_time function"


# =============================================================================
# Metrics Collection Tests
# =============================================================================

class TestMetricsCollection:
    """Test that metrics collection is implemented"""

    def test_has_performance_metrics_class(self):
        """Test that PerformanceMetrics class exists"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'PerformanceMetrics'), \
            "run_performance_tests should define PerformanceMetrics class"

    def test_metrics_tracks_response_times(self):
        """Test that metrics track response times"""
        # Arrange
        from scripts.run_performance_tests import PerformanceMetrics

        # Act
        metrics = PerformanceMetrics()

        # Assert
        assert hasattr(metrics, 'response_times'), \
            "PerformanceMetrics should track response_times"

    def test_metrics_tracks_throughput(self):
        """Test that metrics track throughput"""
        # Arrange
        from scripts.run_performance_tests import PerformanceMetrics

        # Act
        metrics = PerformanceMetrics()

        # Assert
        assert hasattr(metrics, 'requests_per_second'), \
            "PerformanceMetrics should track requests_per_second"

    def test_metrics_tracks_success_rate(self):
        """Test that metrics track success rate"""
        # Arrange
        from scripts.run_performance_tests import PerformanceMetrics

        # Act
        metrics = PerformanceMetrics()

        # Assert
        assert hasattr(metrics, 'success_count'), \
            "PerformanceMetrics should track success_count"
        assert hasattr(metrics, 'failure_count'), \
            "PerformanceMetrics should track failure_count"

    def test_metrics_calculates_statistics(self):
        """Test that metrics can calculate statistics"""
        # Arrange
        from scripts.run_performance_tests import PerformanceMetrics

        # Act
        metrics = PerformanceMetrics()

        # Assert
        assert hasattr(metrics, 'calculate_statistics'), \
            "PerformanceMetrics should have calculate_statistics method"


# =============================================================================
# Report Generation Tests
# =============================================================================

class TestReportGeneration:
    """Test that performance report generation is implemented"""

    def test_has_generate_report_function(self):
        """Test that generate_report function exists"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'generate_report'), \
            "run_performance_tests should have generate_report function"

    def test_report_includes_summary_statistics(self):
        """Test that report includes summary statistics"""
        # Arrange
        from scripts.run_performance_tests import PerformanceMetrics

        metrics = PerformanceMetrics()
        # Add some sample data
        metrics.response_times = [0.1, 0.2, 0.15, 0.3, 0.25]
        metrics.success_count = 5
        metrics.failure_count = 0

        # Act
        stats = metrics.calculate_statistics()

        # Assert
        assert 'mean_response_time' in stats, \
            "Statistics should include mean_response_time"
        assert 'median_response_time' in stats, \
            "Statistics should include median_response_time"
        assert 'p95_response_time' in stats, \
            "Statistics should include p95_response_time"
        assert 'p99_response_time' in stats, \
            "Statistics should include p99_response_time"


# =============================================================================
# Concurrent Execution Tests
# =============================================================================

class TestConcurrentExecution:
    """Test that concurrent execution is supported"""

    def test_has_concurrent_worker_function(self):
        """Test that concurrent worker function exists"""
        # Arrange
        from scripts import run_performance_tests

        # Act & Assert
        assert hasattr(run_performance_tests, 'concurrent_worker'), \
            "run_performance_tests should have concurrent_worker function"

    def test_supports_asyncio_or_threading(self):
        """Test that script uses asyncio or threading for concurrency"""
        # Arrange
        from scripts import run_performance_tests
        import inspect

        # Act
        source = inspect.getsource(run_performance_tests)

        # Assert
        has_concurrency = any(term in source for term in [
            'asyncio', 'threading', 'concurrent.futures', 'ThreadPoolExecutor'
        ])
        assert has_concurrency, \
            "Performance tests should use asyncio or threading for concurrency"


# =============================================================================
# Integration Tests
# =============================================================================

class TestPerformanceTestIntegration:
    """Test that performance testing integrates with system"""

    def test_can_test_health_endpoint(self):
        """Test that performance script can test health endpoint"""
        # Arrange
        from scripts.run_performance_tests import LOAD_TEST_CONFIG

        # Act
        endpoints = LOAD_TEST_CONFIG.get('endpoints', [])
        endpoint_paths = [ep.get('path', ep) if isinstance(ep, dict) else ep
                         for ep in endpoints]

        # Assert
        has_health = any('health' in str(path).lower() for path in endpoint_paths)
        assert has_health, \
            "Performance tests should include health endpoint"

    def test_config_has_base_url(self):
        """Test that config specifies base URL"""
        # Arrange
        from scripts.run_performance_tests import LOAD_TEST_CONFIG

        # Act & Assert
        assert 'base_url' in LOAD_TEST_CONFIG, \
            "Config should specify base_url"
