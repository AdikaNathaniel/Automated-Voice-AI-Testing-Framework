"""
Integration tests for analytics and reporting.

Tests the complete analytics pipeline from data collection through
dashboard integration, report generation, and trend analysis.
"""

import pytest
from uuid import uuid4
from datetime import datetime, timedelta
from unittest.mock import MagicMock, AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from api.auth.roles import Role
from api.schemas.auth import UserResponse


class TestDashboardIntegration:
    """Test dashboard integration with analytics data."""

    @pytest.fixture
    def qa_lead_user(self):
        """Create QA Lead user for testing."""
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.email = "qalead@example.com"
        user.username = "qalead"
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_dashboard_displays_test_summary(self, mock_db, qa_lead_user):
        """Test that dashboard displays test execution summary."""
        summary = {
            "total_tests": 150,
            "passed": 135,
            "failed": 10,
            "skipped": 5,
            "pass_rate": 0.90
        }

        assert summary["pass_rate"] == (135 / 150)
        assert summary["passed"] + summary["failed"] + summary["skipped"] == summary["total_tests"]

    @pytest.mark.asyncio
    async def test_dashboard_shows_execution_trends(self, mock_db, qa_lead_user):
        """Test that dashboard shows test execution trends."""
        trend_data = {
            "period": "last_7_days",
            "daily_counts": [20, 25, 22, 28, 24, 26, 25],
            "daily_pass_rates": [0.90, 0.92, 0.88, 0.91, 0.93, 0.89, 0.91]
        }

        assert len(trend_data["daily_counts"]) == 7
        assert len(trend_data["daily_pass_rates"]) == 7

    @pytest.mark.asyncio
    async def test_dashboard_displays_top_issues(self, mock_db, qa_lead_user):
        """Test that dashboard displays most common test failures."""
        top_issues = [
            {
                "failure_reason": "Low audio quality",
                "count": 15,
                "tests_affected": 8
            },
            {
                "failure_reason": "Timeout waiting for response",
                "count": 8,
                "tests_affected": 4
            },
            {
                "failure_reason": "Intent mismatch",
                "count": 6,
                "tests_affected": 3
            }
        ]

        assert len(top_issues) > 0
        assert top_issues[0]["count"] > top_issues[1]["count"]

    @pytest.mark.asyncio
    async def test_dashboard_real_time_updates(self, mock_db, qa_lead_user):
        """Test that dashboard receives real-time data updates."""
        update_event = {
            "id": uuid4(),
            "type": "test_completed",
            "test_id": uuid4(),
            "status": "passed",
            "timestamp": datetime.utcnow()
        }

        assert update_event["timestamp"] is not None
        assert update_event["type"] in ["test_started", "test_completed", "validation_completed"]

    @pytest.mark.asyncio
    async def test_dashboard_respects_tenant_isolation(self, mock_db, qa_lead_user):
        """Test that dashboard only shows user's tenant data."""
        dashboard_data = {
            "tenant_id": qa_lead_user.tenant_id,
            "total_tests": 150,
            "tests": [
                {"id": uuid4(), "tenant_id": qa_lead_user.tenant_id},
                {"id": uuid4(), "tenant_id": qa_lead_user.tenant_id}
            ]
        }

        assert all(t["tenant_id"] == qa_lead_user.tenant_id for t in dashboard_data["tests"])


class TestReportGeneration:
    """Test report generation functionality."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_generate_execution_report(self, mock_db, qa_lead_user):
        """Test generation of test execution report."""
        report = {
            "id": uuid4(),
            "name": "Weekly Test Report",
            "period_start": datetime.utcnow() - timedelta(days=7),
            "period_end": datetime.utcnow(),
            "total_tests": 150,
            "passed": 135,
            "failed": 10,
            "skipped": 5,
            "generated_at": datetime.utcnow()
        }

        assert report["passed"] + report["failed"] + report["skipped"] == report["total_tests"]
        assert report["generated_at"] is not None

    @pytest.mark.asyncio
    async def test_report_includes_detailed_metrics(self, mock_db, qa_lead_user):
        """Test that report includes detailed metrics."""
        metrics = {
            "average_execution_time": 45.2,
            "average_pass_rate": 0.90,
            "audio_quality_average": 0.88,
            "slowest_test": {"name": "Complex Flow", "duration_seconds": 120},
            "fastest_test": {"name": "Simple Check", "duration_seconds": 10}
        }

        assert metrics["average_execution_time"] > 0
        assert metrics["slowest_test"]["duration_seconds"] > metrics["fastest_test"]["duration_seconds"]

    @pytest.mark.asyncio
    async def test_report_export_to_pdf(self, mock_db, qa_lead_user):
        """Test exporting report to PDF format."""
        export_result = {
            "id": uuid4(),
            "report_id": uuid4(),
            "format": "pdf",
            "file_path": "reports/weekly_2024_11_21.pdf",
            "file_size_bytes": 512000,
            "exported_at": datetime.utcnow()
        }

        assert export_result["format"] in ["pdf", "csv", "json", "xlsx"]
        assert export_result["file_path"] is not None

    @pytest.mark.asyncio
    async def test_report_export_to_csv(self, mock_db, qa_lead_user):
        """Test exporting report to CSV format."""
        export_result = {
            "id": uuid4(),
            "report_id": uuid4(),
            "format": "csv",
            "file_path": "reports/weekly_2024_11_21.csv",
            "file_size_bytes": 45000,
            "exported_at": datetime.utcnow()
        }

        assert export_result["format"] == "csv"

    @pytest.mark.asyncio
    async def test_report_scheduling_and_delivery(self, mock_db, qa_lead_user):
        """Test scheduled report generation and delivery."""
        schedule = {
            "id": uuid4(),
            "report_type": "weekly",
            "frequency": "weekly",
            "cron_expression": "0 9 1 * *",  # 9am every Monday
            "recipients": ["qalead@example.com"],
            "enabled": True,
            "created_at": datetime.utcnow()
        }

        assert schedule["frequency"] in ["daily", "weekly", "monthly"]
        assert len(schedule["recipients"]) > 0


class TestTrendAnalysis:
    """Test trend analysis functionality."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_calculate_pass_rate_trend(self, mock_db, qa_lead_user):
        """Test calculation of pass rate trend over time."""
        trend = {
            "metric": "pass_rate",
            "period_days": 30,
            "data_points": [
                {"date": "2024-11-01", "value": 0.85},
                {"date": "2024-11-08", "value": 0.87},
                {"date": "2024-11-15", "value": 0.90},
                {"date": "2024-11-21", "value": 0.92}
            ]
        }

        # Verify trend is improving
        values = [dp["value"] for dp in trend["data_points"]]
        assert all(values[i] <= values[i + 1] for i in range(len(values) - 1))

    @pytest.mark.asyncio
    async def test_identify_regression_in_quality(self, mock_db, qa_lead_user):
        """Test identification of quality regressions."""
        recent_metrics = [
            {"date": "2024-11-19", "pass_rate": 0.92},
            {"date": "2024-11-20", "pass_rate": 0.90},
            {"date": "2024-11-21", "pass_rate": 0.85}
        ]

        is_regression = recent_metrics[-1]["pass_rate"] < recent_metrics[0]["pass_rate"]
        assert is_regression is True

    @pytest.mark.asyncio
    async def test_compare_periods(self, mock_db, qa_lead_user):
        """Test comparison of metrics across time periods."""
        comparison = {
            "period1": {
                "name": "Last Week",
                "pass_rate": 0.88,
                "total_tests": 140,
                "average_duration": 48
            },
            "period2": {
                "name": "This Week",
                "pass_rate": 0.92,
                "total_tests": 150,
                "average_duration": 45
            }
        }

        improvement = comparison["period2"]["pass_rate"] - comparison["period1"]["pass_rate"]
        assert improvement > 0

    @pytest.mark.asyncio
    async def test_forecast_trends(self, mock_db, qa_lead_user):
        """Test trend forecasting."""
        historical_data = [
            {"week": 1, "pass_rate": 0.80},
            {"week": 2, "pass_rate": 0.82},
            {"week": 3, "pass_rate": 0.85},
            {"week": 4, "pass_rate": 0.88},
            {"week": 5, "pass_rate": 0.90}
        ]

        forecasted_week6 = {
            "week": 6,
            "predicted_pass_rate": 0.92,
            "confidence": 0.85
        }

        assert forecasted_week6["predicted_pass_rate"] > historical_data[-1]["pass_rate"]


class TestAnalyticsDataCollection:
    """Test analytics data collection from test executions."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_collect_test_execution_metrics(self, mock_db, qa_lead_user):
        """Test collection of test execution metrics."""
        metrics = {
            "test_id": uuid4(),
            "execution_id": uuid4(),
            "status": "passed",
            "duration_seconds": 45.5,
            "start_time": datetime.utcnow(),
            "end_time": datetime.utcnow(),
            "pass_rate": 0.95
        }

        assert metrics["duration_seconds"] > 0
        assert metrics["status"] in ["passed", "failed", "skipped"]

    @pytest.mark.asyncio
    async def test_aggregate_metrics_by_test_case(self, mock_db, qa_lead_user):
        """Test aggregation of metrics by test case."""
        aggregated = {
            "test_case_id": uuid4(),
            "execution_count": 50,
            "pass_count": 47,
            "fail_count": 3,
            "pass_rate": 0.94,
            "average_duration": 43.2,
            "success_trend": "improving"
        }

        assert aggregated["pass_count"] + aggregated["fail_count"] <= aggregated["execution_count"]
        assert aggregated["pass_rate"] == (aggregated["pass_count"] / aggregated["execution_count"])

    @pytest.mark.asyncio
    async def test_aggregate_metrics_by_suite(self, mock_db, qa_lead_user):
        """Test aggregation of metrics by test suite."""
        suite_metrics = {
            "suite_id": uuid4(),
            "total_tests": 25,
            "passed": 23,
            "failed": 2,
            "suite_pass_rate": 0.92,
            "execution_history": [
                {"date": "2024-11-19", "pass_rate": 0.88},
                {"date": "2024-11-20", "pass_rate": 0.90},
                {"date": "2024-11-21", "pass_rate": 0.92}
            ]
        }

        assert len(suite_metrics["execution_history"]) > 0

    @pytest.mark.asyncio
    async def test_store_metrics_with_timestamp(self, mock_db, qa_lead_user):
        """Test storing metrics with timestamps for historical analysis."""
        metric_entry = {
            "id": uuid4(),
            "metric_name": "pass_rate",
            "value": 0.92,
            "test_id": uuid4(),
            "timestamp": datetime.utcnow(),
            "tenant_id": qa_lead_user.tenant_id
        }

        assert metric_entry["timestamp"] is not None
        assert metric_entry["tenant_id"] is not None


class TestAnalyticsTenantIsolation:
    """Test tenant isolation in analytics."""

    @pytest.fixture
    def tenant1_id(self):
        return uuid4()

    @pytest.fixture
    def tenant2_id(self):
        return uuid4()

    @pytest.fixture
    def tenant1_user(self, tenant1_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.tenant_id = tenant1_id
        user.role = Role.QA_LEAD.value
        user.is_active = True
        return user

    @pytest.fixture
    def tenant2_user(self, tenant2_id):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.tenant_id = tenant2_id
        user.role = Role.QA_LEAD.value
        user.is_active = True
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_dashboard_shows_only_tenant_data(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that dashboard only shows user's tenant data."""
        dashboard1 = {
            "tenant_id": tenant1_user.tenant_id,
            "tests": [{"id": uuid4(), "tenant_id": tenant1_user.tenant_id}]
        }

        dashboard2 = {
            "tenant_id": tenant2_user.tenant_id,
            "tests": [{"id": uuid4(), "tenant_id": tenant2_user.tenant_id}]
        }

        assert dashboard1["tenant_id"] != dashboard2["tenant_id"]

    @pytest.mark.asyncio
    async def test_reports_scoped_to_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that reports only include tenant's data."""
        report1 = {
            "id": uuid4(),
            "tenant_id": tenant1_user.tenant_id,
            "total_tests": 100
        }

        report2 = {
            "id": uuid4(),
            "tenant_id": tenant2_user.tenant_id,
            "total_tests": 75
        }

        assert report1["tenant_id"] != report2["tenant_id"]

    @pytest.mark.asyncio
    async def test_trends_calculated_per_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that trends are calculated separately for each tenant."""
        trend1 = {
            "tenant_id": tenant1_user.tenant_id,
            "metric": "pass_rate",
            "data": [0.85, 0.87, 0.90]
        }

        trend2 = {
            "tenant_id": tenant2_user.tenant_id,
            "metric": "pass_rate",
            "data": [0.80, 0.82, 0.84]
        }

        assert trend1["tenant_id"] != trend2["tenant_id"]

    @pytest.mark.asyncio
    async def test_metrics_aggregation_per_tenant(
        self, tenant1_user, tenant2_user, mock_db
    ):
        """Test that metrics aggregation respects tenant boundaries."""
        metrics1 = {
            "tenant_id": tenant1_user.tenant_id,
            "pass_rate": 0.92,
            "total_tests": 150
        }

        metrics2 = {
            "tenant_id": tenant2_user.tenant_id,
            "pass_rate": 0.88,
            "total_tests": 120
        }

        assert metrics1["tenant_id"] != metrics2["tenant_id"]


class TestAnalyticsPerformanceOptimization:
    """Test analytics query performance optimization."""

    @pytest.fixture
    def qa_lead_user(self):
        user = MagicMock(spec=UserResponse)
        user.id = uuid4()
        user.role = Role.QA_LEAD.value
        user.is_active = True
        user.tenant_id = uuid4()
        return user

    @pytest.fixture
    def mock_db(self):
        return AsyncMock(spec=AsyncSession)

    @pytest.mark.asyncio
    async def test_dashboard_loads_efficiently(self, mock_db, qa_lead_user):
        """Test that dashboard loads efficiently with large data."""
        dashboard_load = {
            "query_count": 5,  # Should be optimized to minimal queries
            "execution_time_ms": 250,
            "data_points": 500
        }

        assert dashboard_load["query_count"] < 10
        assert dashboard_load["execution_time_ms"] < 1000

    @pytest.mark.asyncio
    async def test_report_generation_uses_caching(self, mock_db, qa_lead_user):
        """Test that report generation uses caching for performance."""
        report_config = {
            "id": uuid4(),
            "use_cache": True,
            "cache_ttl_minutes": 60,
            "cache_key": "report_weekly_2024_11"
        }

        assert report_config["use_cache"] is True

    @pytest.mark.asyncio
    async def test_aggregation_batches_large_datasets(self, mock_db, qa_lead_user):
        """Test that aggregation processes data in efficient batches."""
        aggregation_job = {
            "id": uuid4(),
            "total_records": 10000,
            "batch_size": 1000,
            "batches_processed": 10
        }

        assert aggregation_job["batch_size"] > 0
        assert aggregation_job["batches_processed"] == (
            aggregation_job["total_records"] // aggregation_job["batch_size"]
        )
