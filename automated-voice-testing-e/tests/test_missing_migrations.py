"""
Test suite for missing database migrations.

Tests that migrations exist for:
- JudgePersona table (judge_personas)
- LLMJudge table (llm_judges)
- JudgeDecision table (judge_decisions)
- ScenarioScript table (scenario_scripts)
- ScenarioStep table (scenario_steps)
- EscalationPolicy table (escalation_policies)
"""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

PROJECT_ROOT = Path(__file__).parent.parent
MIGRATIONS_DIR = PROJECT_ROOT / "alembic" / "versions"


class TestJudgePersonaMigration:
    """Test JudgePersona migration exists."""

    def test_migration_creates_judge_personas_table(self):
        """Migration should create judge_personas table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "judge_personas" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for judge_personas table not found"


class TestLLMJudgeMigration:
    """Test LLMJudge migration exists."""

    def test_migration_creates_llm_judges_table(self):
        """Migration should create llm_judges table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "llm_judges" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for llm_judges table not found"


class TestJudgeDecisionMigration:
    """Test JudgeDecision migration exists."""

    def test_migration_creates_judge_decisions_table(self):
        """Migration should create judge_decisions table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "judge_decisions" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for judge_decisions table not found"


class TestScenarioScriptMigration:
    """Test ScenarioScript migration exists."""

    def test_migration_creates_scenario_scripts_table(self):
        """Migration should create scenario_scripts table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "scenario_scripts" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for scenario_scripts table not found"


class TestScenarioStepMigration:
    """Test ScenarioStep migration exists."""

    def test_migration_creates_scenario_steps_table(self):
        """Migration should create scenario_steps table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "scenario_steps" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for scenario_steps table not found"


class TestEscalationPolicyMigration:
    """Test EscalationPolicy migration exists."""

    def test_migration_creates_escalation_policies_table(self):
        """Migration should create escalation_policies table."""
        migration_files = list(MIGRATIONS_DIR.glob("*.py"))

        found = False
        for migration_file in migration_files:
            content = migration_file.read_text()
            if "escalation_policies" in content and "create_table" in content.lower():
                found = True
                break

        assert found, "Migration for escalation_policies table not found"
