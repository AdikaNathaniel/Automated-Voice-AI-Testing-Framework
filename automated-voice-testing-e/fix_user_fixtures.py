#!/usr/bin/env python3
"""Fix user fixtures to add role and tenant_id attributes."""

import re
import sys
from pathlib import Path

def fix_user_simplenamespace(content: str) -> str:
    """Add role and tenant_id to user SimpleNamespace objects."""

    # Pattern to match SimpleNamespace with user attributes (email= or username=)
    # This matches multi-line SimpleNamespace definitions
    pattern = r'SimpleNamespace\s*\(([^)]*(?:email=|username=)[^)]*)\)'

    def add_attributes(match):
        args = match.group(1)

        # Check if this already has role and tenant_id
        has_role = 'role=' in args
        has_tenant_id = 'tenant_id=' in args

        if has_role and has_tenant_id:
            return match.group(0)  # Already has both

        # Remove trailing commas and whitespace
        args = args.rstrip().rstrip(',')

        # Add missing attributes
        if not has_role:
            args += ', role="admin"'
        if not has_tenant_id:
            args += ', tenant_id=None'

        return f'SimpleNamespace({args})'

    return re.sub(pattern, add_attributes, content, flags=re.DOTALL)

def main():
    test_files = [
        "backend/tests/test_validator_stats_route.py",
        "backend/tests/test_metrics_api.py",
        "backend/tests/test_regression_suite_executor.py",
        "backend/tests/test_edge_case_detection.py",
        "backend/tests/test_auth_endpoints.py",
        "backend/tests/test_rate_limit.py",
        "backend/tests/test_test_run_list.py",
        "backend/tests/test_validation_submit_route.py",
        "backend/tests/test_human_validation_tenancy.py",
        "backend/tests/test_orchestration.py",
        "backend/tests/test_analytics_api.py",
        "backend/tests/test_human_validation_service.py",
        "backend/tests/test_regressions_api.py",
        "backend/tests/test_reports_api.py",
        "backend/tests/test_validation_service_db.py",
        "tests/test_routes_test_cases.py",
        "tests/test_routes_test_runs.py",
        "tests/test_routes_test_suites.py",
        "tests/test_routes_human_validation.py",
        "tests/test_routes_knowledge_base.py",
    ]

    for filepath in test_files:
        path = Path(filepath)
        if not path.exists():
            print(f"Skipping {filepath} (not found)")
            continue

        content = path.read_text()
        new_content = fix_user_simplenamespace(content)

        if content != new_content:
            path.write_text(new_content)
            print(f"Fixed {filepath}")
        else:
            print(f"No changes needed for {filepath}")

if __name__ == "__main__":
    main()
