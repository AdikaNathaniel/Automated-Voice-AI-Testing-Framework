"""
Test suite for reporting metrics functionality.

This module tests the reporting system:
- Judge consensus metrics
- Tolerance band usage statistics
- Human escalation stats
- Per-scenario audit trail
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend'))

from uuid import uuid4

import pytest


class TestReportingMetricsService:
    """Test ReportingMetricsService for dashboard metrics"""

    def test_service_exists(self):
        """Test that ReportingMetricsService can be imported"""
        from services.reporting_metrics_service import ReportingMetricsService
        assert ReportingMetricsService is not None

    def test_has_get_consensus_metrics_method(self):
        """Test service has get_consensus_metrics method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'get_consensus_metrics')

    def test_has_get_tolerance_stats_method(self):
        """Test service has get_tolerance_stats method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'get_tolerance_stats')

    def test_has_get_escalation_stats_method(self):
        """Test service has get_escalation_stats method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'get_escalation_stats')


class TestJudgeConsensusMetrics:
    """Test judge consensus metrics"""

    def test_get_consensus_metrics_returns_data(self):
        """Test getting consensus metrics returns expected structure"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        metrics = service.get_consensus_metrics()

        assert 'total_validations' in metrics
        assert 'average_agreement_ratio' in metrics
        assert 'unanimous_decisions' in metrics

    def test_consensus_metrics_by_time_range(self):
        """Test filtering consensus metrics by time range"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        metrics = service.get_consensus_metrics(
            start_date='2024-01-01',
            end_date='2024-12-31'
        )

        assert 'time_range' in metrics
        assert metrics['time_range']['start'] == '2024-01-01'

    def test_consensus_metrics_by_judge(self):
        """Test getting per-judge consensus metrics"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        metrics = service.get_consensus_metrics(group_by='judge')

        assert 'by_judge' in metrics

    def test_dissenting_judge_frequency(self):
        """Test tracking dissenting judge frequency"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        metrics = service.get_consensus_metrics()

        assert 'dissenting_frequency' in metrics


class TestToleranceBandMetrics:
    """Test tolerance band usage statistics"""

    def test_get_tolerance_stats_returns_data(self):
        """Test getting tolerance stats returns expected structure"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_tolerance_stats()

        assert 'total_checks' in stats
        assert 'pass_rate' in stats
        assert 'by_type' in stats

    def test_tolerance_stats_by_type(self):
        """Test tolerance stats broken down by check type"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_tolerance_stats()

        # Should have stats for different tolerance check types
        by_type = stats['by_type']
        assert isinstance(by_type, dict)

    def test_semantic_similarity_distribution(self):
        """Test semantic similarity score distribution"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_tolerance_stats()

        assert 'score_distribution' in stats

    def test_threshold_effectiveness(self):
        """Test threshold effectiveness metrics"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_tolerance_stats()

        assert 'threshold_effectiveness' in stats


class TestEscalationMetrics:
    """Test human escalation statistics"""

    def test_get_escalation_stats_returns_data(self):
        """Test getting escalation stats returns expected structure"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_escalation_stats()

        assert 'total_escalations' in stats
        assert 'escalation_rate' in stats
        assert 'average_resolution_time' in stats

    def test_escalation_by_reason(self):
        """Test escalation stats broken down by reason"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_escalation_stats()

        assert 'by_reason' in stats

    def test_escalation_resolution_outcomes(self):
        """Test tracking escalation resolution outcomes"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_escalation_stats()

        assert 'resolution_outcomes' in stats

    def test_validator_workload_stats(self):
        """Test validator workload statistics"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        stats = service.get_escalation_stats()

        assert 'validator_workload' in stats


class TestAuditTrailService:
    """Test per-scenario audit trail service"""

    def test_service_exists(self):
        """Test that AuditTrailService can be imported"""
        from services.audit_trail_service import AuditTrailService
        assert AuditTrailService is not None

    def test_has_get_scenario_audit_method(self):
        """Test service has get_scenario_audit method"""
        from services.audit_trail_service import AuditTrailService

        assert hasattr(AuditTrailService, 'get_scenario_audit')

    def test_has_get_validation_audit_method(self):
        """Test service has get_validation_audit method"""
        from services.audit_trail_service import AuditTrailService

        assert hasattr(AuditTrailService, 'get_validation_audit')


class TestScenarioAuditTrail:
    """Test per-scenario audit trail"""

    def test_get_scenario_audit_returns_data(self):
        """Test getting scenario audit returns expected structure"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        scenario_id = str(uuid4())

        audit = service.get_scenario_audit(scenario_id)

        assert 'scenario_id' in audit
        assert 'events' in audit
        assert 'summary' in audit

    def test_audit_includes_rule_scores(self):
        """Test audit includes rule evaluation scores"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        scenario_id = str(uuid4())

        audit = service.get_scenario_audit(scenario_id)

        # Should include rule score details
        assert 'rule_scores' in audit or 'events' in audit

    def test_audit_includes_judge_votes(self):
        """Test audit includes individual judge votes"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        scenario_id = str(uuid4())

        audit = service.get_scenario_audit(scenario_id)

        # Should include judge voting details
        assert 'judge_votes' in audit or 'events' in audit

    def test_audit_includes_human_decisions(self):
        """Test audit includes human validation decisions"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        scenario_id = str(uuid4())

        audit = service.get_scenario_audit(scenario_id)

        # Should include human decisions
        assert 'human_decisions' in audit or 'events' in audit


class TestValidationAuditTrail:
    """Test validation-specific audit trail"""

    def test_get_validation_audit_returns_data(self):
        """Test getting validation audit returns expected structure"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        validation_id = str(uuid4())

        audit = service.get_validation_audit(validation_id)

        assert 'validation_id' in audit
        assert 'timeline' in audit

    def test_validation_audit_includes_timestamps(self):
        """Test validation audit includes event timestamps"""
        from services.audit_trail_service import AuditTrailService

        service = AuditTrailService()
        validation_id = str(uuid4())

        audit = service.get_validation_audit(validation_id)

        # Each event should have timestamp
        for event in audit.get('timeline', []):
            assert 'timestamp' in event or audit.get('timeline') == []


class TestReportingAggregation:
    """Test report aggregation features"""

    def test_aggregate_by_test_run(self):
        """Test aggregating metrics by test run"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        test_run_id = str(uuid4())

        metrics = service.get_run_summary(test_run_id)

        assert 'test_run_id' in metrics
        assert 'total_validations' in metrics

    def test_aggregate_by_test_suite(self):
        """Test aggregating metrics by test suite"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        suite_id = str(uuid4())

        metrics = service.get_suite_summary(suite_id)

        assert 'suite_id' in metrics

    def test_has_get_run_summary_method(self):
        """Test service has get_run_summary method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'get_run_summary')

    def test_has_get_suite_summary_method(self):
        """Test service has get_suite_summary method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'get_suite_summary')


class TestExportFormats:
    """Test report export capabilities"""

    def test_export_to_json(self):
        """Test exporting report to JSON format"""
        from services.reporting_metrics_service import ReportingMetricsService

        service = ReportingMetricsService()
        metrics = service.get_consensus_metrics()

        exported = service.export_to_json(metrics)
        assert isinstance(exported, str)

    def test_has_export_to_json_method(self):
        """Test service has export_to_json method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'export_to_json')

    def test_has_export_to_csv_method(self):
        """Test service has export_to_csv method"""
        from services.reporting_metrics_service import ReportingMetricsService

        assert hasattr(ReportingMetricsService, 'export_to_csv')


