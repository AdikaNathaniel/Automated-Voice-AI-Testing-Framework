"""
Dashboard API response schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DashboardKPIs(BaseModel):
    tests_executed: int = Field(0, description="Total tests executed in period")
    system_health_pct: float = Field(0.0, description="Overall system health percentage")
    issues_detected: int = Field(0, description="Issues detected in the selected range")
    avg_response_time_ms: float = Field(0.0, description="Average response time in milliseconds")


class RealTimeExecution(BaseModel):
    current_run_id: Optional[str] = Field(None, description="Identifier of the current active test run")
    progress_pct: float = Field(0.0, description="Progress percentage of the current run")
    tests_passed: int = Field(0, description="Tests passed in the active run")
    tests_failed: int = Field(0, description="Tests failed in the active run")
    under_review: int = Field(0, description="Tests awaiting human review")
    queued: int = Field(0, description="Tests queued for execution")


class ValidationAccuracy(BaseModel):
    overall_accuracy_pct: float = Field(0.0, description="Overall validation accuracy percentage")
    total_validations: int = Field(0, description="Total validations processed")
    human_reviews: int = Field(0, description="Number of validations escalated to humans")
    agreements: int = Field(0, description="Number of times AI and human agreed")
    disagreements: int = Field(0, description="Number of times AI and human disagreed")
    ai_overturned: int = Field(0, description="Cases where human changed AI's decision")
    time_saved_hours: float = Field(0.0, description="Estimated time saved through automation")


class LanguageCoverageEntry(BaseModel):
    language_code: str = Field(..., description="Language code (e.g., en-US)")
    test_cases: int = Field(0, description="Number of test cases executed for the language")
    pass_rate_pct: float = Field(0.0, description="Validation pass rate percentage")


class DefectSummary(BaseModel):
    open: int = Field(0, description="Total open defects")
    critical: int = Field(0, description="Critical severity defects")
    high: int = Field(0, description="High severity defects")
    medium: int = Field(0, description="Medium severity defects")
    low: int = Field(0, description="Low severity defects")


class DefectTrendPoint(BaseModel):
    date: str = Field(..., description="ISO timestamp bucket for the trend point")
    open: int = Field(0, description="Open defects at the time bucket")


class TestCoverageEntry(BaseModel):
    area: str = Field(..., description="Test coverage area e.g. intents/entities")
    coverage_pct: float = Field(0.0, description="Coverage percentage for the area")
    automated_pct: float = Field(0.0, description="Automation percentage for the area")


class PipelineStatus(BaseModel):
    id: str = Field(..., description="Pipeline identifier")
    name: str = Field(..., description="Human readable pipeline name")
    status: str = Field(..., description="Pipeline status label")
    last_run_at: Optional[str] = Field(None, description="Last run timestamp")


class CICDStatus(BaseModel):
    pipelines: List[PipelineStatus] = Field(default_factory=list)
    incidents: int = Field(0, description="Open CI/CD incidents")


class EdgeCaseCategory(BaseModel):
    category: str = Field(..., description="Edge case category label")
    count: int = Field(0, description="Edge case count for the category")


class EdgeCaseStatistics(BaseModel):
    total: int = Field(0, description="Total edge cases evaluated")
    resolved: int = Field(0, description="Resolved edge cases")
    categories: List[EdgeCaseCategory] = Field(default_factory=list)


class PassRateTrendPoint(BaseModel):
    """Pass rate trend point for time-series data"""
    date: str = Field(..., description="ISO timestamp bucket for the trend point")
    pass_rate_pct: float = Field(0.0, description="Pass rate percentage for this date")
    tests_passed: int = Field(0, description="Number of tests passed")
    tests_failed: int = Field(0, description="Number of tests failed")
    total_tests: int = Field(0, description="Total tests executed")


class RegressionEntry(BaseModel):
    """Details of a detected regression"""
    test_case_id: str = Field(..., description="ID of the test case that regressed")
    test_name: str = Field(..., description="Name of the test case")
    detected_at: str = Field(..., description="ISO timestamp when regression was detected")
    previous_status: str = Field("passed", description="Previous test status")
    current_status: str = Field("failed", description="Current test status")


class RegressionSummary(BaseModel):
    """Summary of regressions detected"""
    total: int = Field(0, description="Total number of regressions detected")
    recent: List[RegressionEntry] = Field(default_factory=list, description="Recent regressions (last 10)")


class ValidationAccuracyTrendPoint(BaseModel):
    """Validation accuracy trend point for time-series data"""
    date: str = Field(..., description="ISO timestamp bucket for the trend point")
    accuracy_pct: float = Field(0.0, description="Validation accuracy percentage for this date")
    validations: int = Field(0, description="Total validations processed on this date")
    correct: int = Field(0, description="Number of correct validations")


class ScenarioStats(BaseModel):
    """Scenario statistics summary"""
    total: int = Field(0, description="Total number of scenarios")


class TestSuiteStats(BaseModel):
    """Test suite statistics summary"""
    total: int = Field(0, description="Total number of test suites")


class SuiteRunStats(BaseModel):
    """Suite run statistics summary"""
    total: int = Field(0, description="Total suite runs in the period")
    completed: int = Field(0, description="Completed suite runs")
    failed: int = Field(0, description="Failed suite runs")
    running: int = Field(0, description="Currently running suite runs")


class ValidationQueueStats(BaseModel):
    """Validation queue statistics"""
    pending_reviews: int = Field(0, description="Number of items pending human review")


class DashboardResponse(BaseModel):
    kpis: DashboardKPIs
    real_time_execution: RealTimeExecution
    validation_accuracy: ValidationAccuracy
    validation_queue: ValidationQueueStats = Field(default_factory=ValidationQueueStats, description="Validation queue statistics")
    language_coverage: List[LanguageCoverageEntry]
    defects: DefectSummary
    defects_trend: List[DefectTrendPoint] = Field(default_factory=list)
    test_coverage: List[TestCoverageEntry]
    cicd_status: CICDStatus
    edge_cases: EdgeCaseStatistics
    scenarios: ScenarioStats = Field(default_factory=ScenarioStats, description="Scenario statistics")
    test_suites: TestSuiteStats = Field(default_factory=TestSuiteStats, description="Test suite statistics")
    suite_runs: SuiteRunStats = Field(default_factory=SuiteRunStats, description="Suite run statistics")
    pass_rate_trend: List[PassRateTrendPoint] = Field(default_factory=list, description="Pass rate over time")
    regressions: RegressionSummary = Field(default_factory=RegressionSummary, description="Detected regressions")
    validation_accuracy_trend: List[ValidationAccuracyTrendPoint] = Field(default_factory=list, description="Validation accuracy over time")
    updated_at: datetime
