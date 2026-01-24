"""
Voice AI Testing Framework - Models Module

Importing this package registers all SQLAlchemy models so relationship
strings can be resolved during tests and application startup.
"""

from models import (
    user,  # noqa: F401
    test_suite,  # noqa: F401
    test_suite_scenario,  # noqa: F401  - must be after test_suite and scenario_script
    suite_run,  # noqa: F401
    defect,  # noqa: F401
    edge_case,  # noqa: F401
    pattern_group,  # noqa: F401 - must be before knowledge_base (Phase 3 KB integration)
    validation_result,  # noqa: F401
    validation_queue,  # noqa: F401
    human_validation,  # noqa: F401
    validator_performance,  # noqa: F401
    expected_outcome,  # noqa: F401
    scenario_script,  # noqa: F401
    multi_turn_execution,  # noqa: F401
    configuration,  # noqa: F401
    configuration_history,  # noqa: F401
    knowledge_base,  # noqa: F401
    activity_log,  # noqa: F401
    comment,  # noqa: F401
    test_metric,  # noqa: F401
    test_execution_queue,  # noqa: F401
    device_test_execution,  # noqa: F401
    escalation_policy,  # noqa: F401
    llm_provider_config,  # noqa: F401
    llm_usage_log,  # noqa: F401 - LLM API usage and cost tracking
    llm_model_pricing,  # noqa: F401 - LLM model pricing (database-driven)
    audit_trail,  # noqa: F401 - Audit trail for config changes
    regression_baseline,  # noqa: F401 - regression testing baselines
    regression,  # noqa: F401 - persistent regression tracking
    notification_config,  # noqa: F401 - tenant notification settings
    cicd_run,  # noqa: F401 - CI/CD pipeline runs
    integration_config,  # noqa: F401 - external service integrations (GitHub, Jira)
    category,  # noqa: F401 - scenario categories for organization
    pattern_analysis_config,  # noqa: F401 - pattern analysis configuration per tenant
)

__version__ = "0.1.0"
