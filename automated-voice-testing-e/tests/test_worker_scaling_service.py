"""
Test suite for worker_scaling_service.py.

Tests the Celery worker auto-scaling functionality including:
- MetricsProvider protocol
- CeleryMetricsProvider implementation
- CeleryWorkerAutoScaler scaling logic
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

PROJECT_ROOT = Path(__file__).parent.parent
SERVICE_FILE = PROJECT_ROOT / "backend" / "services" / "worker_scaling_service.py"


class TestWorkerScalingServiceStructure:
    """Test worker_scaling_service file structure and patterns."""

    @pytest.fixture
    def service_content(self):
        """Read service file content."""
        return SERVICE_FILE.read_text()

    def test_file_exists(self):
        """worker_scaling_service.py should exist."""
        assert SERVICE_FILE.exists(), "worker_scaling_service.py should exist"

    def test_file_under_500_lines(self, service_content):
        """File should be under 500 lines."""
        line_count = len(service_content.splitlines())
        assert line_count <= 500, \
            f"worker_scaling_service.py has {line_count} lines, should be <= 500"

    def test_has_module_docstring(self, service_content):
        """Should have module docstring."""
        assert service_content.strip().startswith('"""'), \
            "Module should have a docstring"

    def test_no_notimplementederror_in_protocol(self, service_content):
        """Protocol methods should use ... not NotImplementedError."""
        # Find the MetricsProvider class and check it doesn't raise NotImplementedError
        lines = service_content.splitlines()
        in_protocol = False
        for i, line in enumerate(lines):
            if "class MetricsProvider(Protocol):" in line:
                in_protocol = True
            elif in_protocol and line.strip().startswith("class "):
                in_protocol = False
            elif in_protocol and "raise NotImplementedError" in line:
                pytest.fail(
                    f"Line {i+1}: MetricsProvider protocol should use '...' "
                    "instead of 'raise NotImplementedError'"
                )


class TestMetricsProviderProtocol:
    """Test MetricsProvider protocol definition."""

    def test_protocol_can_be_imported(self):
        """MetricsProvider should be importable."""
        from services.worker_scaling_service import MetricsProvider
        assert MetricsProvider is not None

    def test_protocol_has_get_metrics_method(self):
        """MetricsProvider should define get_metrics method."""
        from services.worker_scaling_service import MetricsProvider
        assert hasattr(MetricsProvider, 'get_metrics')


class TestQueueMetrics:
    """Test QueueMetrics dataclass."""

    def test_queue_metrics_creation(self):
        """QueueMetrics should be creatable with required fields."""
        from services.worker_scaling_service import QueueMetrics

        metrics = QueueMetrics(queue_depth=10, active_workers=5)

        assert metrics.queue_depth == 10
        assert metrics.active_workers == 5

    def test_queue_metrics_is_frozen(self):
        """QueueMetrics should be immutable."""
        from services.worker_scaling_service import QueueMetrics

        metrics = QueueMetrics(queue_depth=10, active_workers=5)

        with pytest.raises(Exception):  # FrozenInstanceError
            metrics.queue_depth = 20


class TestAutoScalingDecision:
    """Test AutoScalingDecision dataclass."""

    def test_decision_creation(self):
        """AutoScalingDecision should be creatable with all fields."""
        from services.worker_scaling_service import AutoScalingDecision

        decision = AutoScalingDecision(
            queue_depth=10,
            active_workers=5,
            target_workers=8,
            scaled=True,
            scale_direction="grow"
        )

        assert decision.queue_depth == 10
        assert decision.active_workers == 5
        assert decision.target_workers == 8
        assert decision.scaled is True
        assert decision.scale_direction == "grow"


class TestCeleryMetricsProvider:
    """Test CeleryMetricsProvider implementation."""

    @pytest.fixture
    def mock_celery_app(self):
        """Create mock Celery app."""
        app = MagicMock()
        return app

    def test_provider_creation(self, mock_celery_app):
        """CeleryMetricsProvider should be creatable."""
        from services.worker_scaling_service import CeleryMetricsProvider

        provider = CeleryMetricsProvider(
            celery_app=mock_celery_app,
            queue_name="test_queue"
        )

        assert provider is not None

    def test_get_metrics_returns_queue_metrics(self, mock_celery_app):
        """get_metrics should return QueueMetrics instance."""
        from services.worker_scaling_service import (
            CeleryMetricsProvider, QueueMetrics
        )

        # Setup mock inspector
        mock_inspector = MagicMock()
        mock_inspector.reserved.return_value = {}
        mock_inspector.scheduled.return_value = {}
        mock_inspector.stats.return_value = {}
        mock_celery_app.control.inspect.return_value = mock_inspector

        provider = CeleryMetricsProvider(celery_app=mock_celery_app)
        metrics = provider.get_metrics()

        assert isinstance(metrics, QueueMetrics)
        assert metrics.queue_depth >= 0
        assert metrics.active_workers >= 0

    def test_get_metrics_handles_inspector_failure(self, mock_celery_app):
        """get_metrics should handle Celery inspector failures gracefully."""
        from services.worker_scaling_service import CeleryMetricsProvider

        mock_celery_app.control.inspect.side_effect = Exception("Connection failed")

        provider = CeleryMetricsProvider(celery_app=mock_celery_app)
        metrics = provider.get_metrics()

        # Should return zero values on failure
        assert metrics.queue_depth == 0
        assert metrics.active_workers == 0


class TestCeleryWorkerAutoScaler:
    """Test CeleryWorkerAutoScaler scaling logic."""

    @pytest.fixture
    def mock_celery_app(self):
        """Create mock Celery app."""
        app = MagicMock()
        return app

    @pytest.fixture
    def mock_metrics_provider(self):
        """Create mock metrics provider."""
        provider = MagicMock()
        return provider

    def test_autoscaler_creation(self, mock_celery_app):
        """CeleryWorkerAutoScaler should be creatable."""
        from services.worker_scaling_service import CeleryWorkerAutoScaler

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            min_workers=1,
            max_workers=10
        )

        assert scaler is not None

    def test_autoscaler_validates_min_workers(self, mock_celery_app):
        """Should raise ValueError for negative min_workers."""
        from services.worker_scaling_service import CeleryWorkerAutoScaler

        with pytest.raises(ValueError) as exc_info:
            CeleryWorkerAutoScaler(
                celery_app=mock_celery_app,
                min_workers=-1
            )

        assert "min_workers" in str(exc_info.value)

    def test_autoscaler_validates_max_workers(self, mock_celery_app):
        """Should raise ValueError for max_workers < 1."""
        from services.worker_scaling_service import CeleryWorkerAutoScaler

        with pytest.raises(ValueError) as exc_info:
            CeleryWorkerAutoScaler(
                celery_app=mock_celery_app,
                max_workers=0
            )

        assert "max_workers" in str(exc_info.value)

    def test_autoscaler_validates_max_gte_min(self, mock_celery_app):
        """Should raise ValueError if max_workers < min_workers."""
        from services.worker_scaling_service import CeleryWorkerAutoScaler

        with pytest.raises(ValueError) as exc_info:
            CeleryWorkerAutoScaler(
                celery_app=mock_celery_app,
                min_workers=10,
                max_workers=5
            )

        assert "max_workers" in str(exc_info.value)

    def test_evaluate_and_scale_returns_decision(
        self, mock_celery_app, mock_metrics_provider
    ):
        """evaluate_and_scale should return AutoScalingDecision."""
        from services.worker_scaling_service import (
            CeleryWorkerAutoScaler, AutoScalingDecision, QueueMetrics
        )

        mock_metrics_provider.get_metrics.return_value = QueueMetrics(
            queue_depth=50,
            active_workers=3
        )

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            metrics_provider=mock_metrics_provider,
            min_workers=1,
            max_workers=10,
            target_tasks_per_worker=10,
            cooldown_seconds=0
        )

        decision = scaler.evaluate_and_scale()

        assert isinstance(decision, AutoScalingDecision)

    def test_scale_up_when_queue_depth_high(
        self, mock_celery_app, mock_metrics_provider
    ):
        """Should scale up when queue depth exceeds worker capacity."""
        from services.worker_scaling_service import (
            CeleryWorkerAutoScaler, QueueMetrics
        )

        mock_metrics_provider.get_metrics.return_value = QueueMetrics(
            queue_depth=50,
            active_workers=2
        )

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            metrics_provider=mock_metrics_provider,
            min_workers=1,
            max_workers=10,
            target_tasks_per_worker=10,
            cooldown_seconds=0
        )

        decision = scaler.evaluate_and_scale()

        assert decision.target_workers == 5  # 50/10 = 5
        assert decision.scaled is True
        assert decision.scale_direction == "grow"
        mock_celery_app.control.pool_grow.assert_called()

    def test_scale_down_when_queue_empty(
        self, mock_celery_app, mock_metrics_provider
    ):
        """Should scale down when queue is empty."""
        from services.worker_scaling_service import (
            CeleryWorkerAutoScaler, QueueMetrics
        )

        mock_metrics_provider.get_metrics.return_value = QueueMetrics(
            queue_depth=0,
            active_workers=5
        )

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            metrics_provider=mock_metrics_provider,
            min_workers=1,
            max_workers=10,
            target_tasks_per_worker=10,
            cooldown_seconds=0
        )

        decision = scaler.evaluate_and_scale()

        assert decision.target_workers == 1  # min_workers
        assert decision.scaled is True
        assert decision.scale_direction == "shrink"
        mock_celery_app.control.pool_shrink.assert_called()

    def test_respects_cooldown_period(
        self, mock_celery_app, mock_metrics_provider
    ):
        """Should not scale during cooldown period."""
        from services.worker_scaling_service import (
            CeleryWorkerAutoScaler, QueueMetrics
        )

        mock_metrics_provider.get_metrics.return_value = QueueMetrics(
            queue_depth=50,
            active_workers=2
        )

        fixed_time = datetime(2024, 1, 1, 12, 0, 0)

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            metrics_provider=mock_metrics_provider,
            cooldown_seconds=60,
            time_provider=lambda: fixed_time
        )

        # First scale should work
        decision1 = scaler.evaluate_and_scale()
        assert decision1.scaled is True

        # Second scale should be blocked by cooldown
        decision2 = scaler.evaluate_and_scale()
        assert decision2.scaled is False

    def test_disabled_scaler_does_not_scale(
        self, mock_celery_app, mock_metrics_provider
    ):
        """Disabled scaler should not perform scaling."""
        from services.worker_scaling_service import (
            CeleryWorkerAutoScaler, QueueMetrics
        )

        mock_metrics_provider.get_metrics.return_value = QueueMetrics(
            queue_depth=100,
            active_workers=1
        )

        scaler = CeleryWorkerAutoScaler(
            celery_app=mock_celery_app,
            metrics_provider=mock_metrics_provider,
            enabled=False
        )

        decision = scaler.evaluate_and_scale()

        assert decision.scaled is False
        mock_celery_app.control.pool_grow.assert_not_called()


class TestErrorHandling:
    """Test error handling in worker_scaling_service."""

    @pytest.fixture
    def service_content(self):
        """Read service file content."""
        return SERVICE_FILE.read_text()

    def test_has_try_except_blocks(self, service_content):
        """Should have try/except for error handling."""
        assert "try:" in service_content
        assert "except" in service_content

    def test_has_logging(self, service_content):
        """Should use logging for error reporting."""
        assert "LOGGER" in service_content or "logger" in service_content
        assert "logging" in service_content
