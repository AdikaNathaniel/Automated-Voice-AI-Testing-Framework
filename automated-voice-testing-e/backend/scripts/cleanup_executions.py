#!/usr/bin/env python
"""
Cleanup script to remove all execution-related data from the database.

This script removes:
- Human validations
- Validation queue items
- Validation results
- Step executions
- Multi-turn executions
- Suite runs
- Test execution queue items
- Related activity logs
- Related test metrics

Usage:
    cd backend
    python scripts/cleanup_executions.py
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from api.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def cleanup_executions():
    """Remove all execution-related data from the database."""
    settings = get_settings()
    engine = create_engine(str(settings.DATABASE_URL))

    print("Starting cleanup of all execution-related data...")
    print("=" * 60)

    # Order matters due to foreign key constraints
    # Delete children before parents
    # Only include tables that definitely exist
    tables_to_clean = [
        "human_validations",
        "validation_queue",
        "validation_results",
        "step_executions",
        "multi_turn_executions",
        "suite_runs",
        "test_execution_queue",
        "validator_performance",
        "test_metrics",
    ]

    # Use raw connection for each delete to avoid transaction issues
    with engine.connect() as conn:
        for table_name in tables_to_clean:
            try:
                result = conn.execute(text(f"DELETE FROM {table_name}"))
                conn.commit()
                print(f"Deleted {result.rowcount} {table_name}")
            except Exception as e:
                conn.rollback()
                if "does not exist" in str(e):
                    print(f"Skipped {table_name} (table does not exist)")
                else:
                    print(f"Error deleting {table_name}: {e}")

    print("=" * 60)
    print("Cleanup completed successfully!")
    print("\nAll execution-related data has been removed.")
    print("Scenarios, test suites, and configuration remain intact.")


if __name__ == "__main__":
    # Confirmation prompt
    print("=" * 60)
    print("WARNING: This will delete ALL execution-related data!")
    print("=" * 60)
    print("\nThis includes:")
    print("  - All suite runs")
    print("  - All multi-turn executions")
    print("  - All step executions")
    print("  - All validation results")
    print("  - All validation queue items")
    print("  - All human validations")
    print("  - All validator performance records")
    print("  - All test metrics")
    print("  - Related activity logs")
    print("\nScenarios, test suites, and configuration will NOT be deleted.")
    print("")

    confirm = input("Type 'DELETE' to confirm: ")
    if confirm == "DELETE":
        cleanup_executions()
    else:
        print("Cleanup cancelled.")
