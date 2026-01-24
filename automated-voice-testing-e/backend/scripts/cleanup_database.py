#!/usr/bin/env python3
"""
Database Cleanup Script

This script clears execution-related data while preserving:
- Test suites
- Test suite scenarios (junction table)
- Scenario scripts
- Scenario steps
- Expected outcomes
- LLM judges and personas

Run with: python scripts/cleanup_database.py
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from api.database import SessionLocal


async def cleanup_database():
    """Clear all execution-related data from the database."""

    # Tables to clear in order (respecting foreign key constraints)
    tables_to_clear = [
        # First: tables with no dependents
        'human_validations',
        'judge_decisions',
        'validation_queue',

        # Second: validation results (depends on above)
        'validation_results',

        # Third: step executions
        'step_executions',

        # Fourth: multi-turn executions
        'multi_turn_executions',
        'device_test_executions',

        # Fifth: test execution queue
        'test_execution_queue',

        # Sixth: suite runs
        'suite_runs',

        # Seventh: defects (may reference executions)
        'defects',
    ]

    async with SessionLocal() as db:
        print("=" * 60)
        print("DATABASE CLEANUP - Clearing Execution Data")
        print("=" * 60)
        print()

        for table in tables_to_clear:
            try:
                # Check row count before
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count_before = result.scalar()

                if count_before > 0:
                    # Delete all rows
                    await db.execute(text(f"DELETE FROM {table}"))
                    await db.commit()
                    print(f"✓ {table}: Deleted {count_before} rows")
                else:
                    print(f"  {table}: Already empty")

            except Exception as e:
                print(f"✗ {table}: Error - {str(e)}")
                await db.rollback()

        print()
        print("=" * 60)
        print("PRESERVED TABLES (not cleared):")
        print("=" * 60)

        preserved_tables = [
            'test_suites',
            'test_suite_scenarios',
            'scenario_scripts',
            'scenario_steps',
            'expected_outcomes',
            'users',
        ]

        for table in preserved_tables:
            try:
                result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} rows preserved")
            except Exception as e:
                print(f"  {table}: Not found or error - {str(e)}")

        print()
        print("=" * 60)
        print("CLEANUP COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(cleanup_database())
