"""
Test suite for ON DELETE constraints in SQLAlchemy models.

Tests that foreign key columns have proper ondelete behavior:
- Defect: test_case_id, test_execution_id, assigned_to
- EdgeCase: test_case_id, discovered_by
- ConfigurationHistory: changed_by
"""

import pytest
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

PROJECT_ROOT = Path(__file__).parent.parent
MODELS_DIR = PROJECT_ROOT / "backend" / "models"


class TestDefectOnDeleteConstraints:
    """Test Defect model ON DELETE constraints."""

    @pytest.fixture
    def defect_content(self):
        """Read Defect model content."""
        return (MODELS_DIR / "defect.py").read_text()

    def test_test_case_id_has_ondelete_set_null(self, defect_content):
        """Defect.test_case_id should have ondelete='SET NULL'."""
        # Find test_case_id ForeignKey definition
        assert "test_case_id" in defect_content, \
            "Defect should have test_case_id column"
        # Check for ondelete in the ForeignKey
        # The pattern should be near the test_case_id definition
        lines = defect_content.split('\n')
        in_test_case_id = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'test_case_id' in line and 'Column' in line:
                in_test_case_id = True
            if in_test_case_id:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                # Check next few lines for ForeignKey with ondelete
                if 'ForeignKey' in line:
                    # Check current line and next few
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_test_case_id:
                    # End of column definition
                    in_test_case_id = False

        assert found_ondelete, \
            "Defect.test_case_id ForeignKey should have ondelete='SET NULL'"

    def test_test_execution_id_has_ondelete_set_null(self, defect_content):
        """Defect.test_execution_id should have ondelete='SET NULL'."""
        assert "test_execution_id" in defect_content, \
            "Defect should have test_execution_id column"
        # Check for ondelete in the ForeignKey
        lines = defect_content.split('\n')
        in_column = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'test_execution_id' in line and 'Column' in line:
                in_column = True
            if in_column:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                if 'ForeignKey' in line:
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_column:
                    in_column = False

        assert found_ondelete, \
            "Defect.test_execution_id ForeignKey should have ondelete='SET NULL'"

    def test_assigned_to_has_ondelete_set_null(self, defect_content):
        """Defect.assigned_to should have ondelete='SET NULL'."""
        assert "assigned_to" in defect_content, \
            "Defect should have assigned_to column"
        # Check for ondelete in the ForeignKey
        lines = defect_content.split('\n')
        in_column = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'assigned_to' in line and 'Column' in line:
                in_column = True
            if in_column:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                if 'ForeignKey' in line:
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_column:
                    in_column = False

        assert found_ondelete, \
            "Defect.assigned_to ForeignKey should have ondelete='SET NULL'"


class TestEdgeCaseOnDeleteConstraints:
    """Test EdgeCase model ON DELETE constraints."""

    @pytest.fixture
    def edge_case_content(self):
        """Read EdgeCase model content."""
        return (MODELS_DIR / "edge_case.py").read_text()

    def test_test_case_id_has_ondelete_set_null(self, edge_case_content):
        """EdgeCase.test_case_id should have ondelete='SET NULL'."""
        assert "test_case_id" in edge_case_content, \
            "EdgeCase should have test_case_id column"
        lines = edge_case_content.split('\n')
        in_column = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'test_case_id' in line and 'Column' in line:
                in_column = True
            if in_column:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                if 'ForeignKey' in line:
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_column:
                    in_column = False

        assert found_ondelete, \
            "EdgeCase.test_case_id ForeignKey should have ondelete='SET NULL'"

    def test_discovered_by_has_ondelete_set_null(self, edge_case_content):
        """EdgeCase.discovered_by should have ondelete='SET NULL'."""
        assert "discovered_by" in edge_case_content, \
            "EdgeCase should have discovered_by column"
        lines = edge_case_content.split('\n')
        in_column = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'discovered_by' in line and 'Column' in line:
                in_column = True
            if in_column:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                if 'ForeignKey' in line:
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_column:
                    in_column = False

        assert found_ondelete, \
            "EdgeCase.discovered_by ForeignKey should have ondelete='SET NULL'"


class TestConfigurationHistoryOnDeleteConstraints:
    """Test ConfigurationHistory model ON DELETE constraints."""

    @pytest.fixture
    def config_history_content(self):
        """Read ConfigurationHistory model content."""
        return (MODELS_DIR / "configuration_history.py").read_text()

    def test_changed_by_has_ondelete_set_null(self, config_history_content):
        """ConfigurationHistory.changed_by should have ondelete='SET NULL'."""
        assert "changed_by" in config_history_content, \
            "ConfigurationHistory should have changed_by column"
        lines = config_history_content.split('\n')
        in_column = False
        found_ondelete = False
        for i, line in enumerate(lines):
            if 'changed_by' in line and 'Column' in line:
                in_column = True
            if in_column:
                if "ondelete='SET NULL'" in line or 'ondelete="SET NULL"' in line:
                    found_ondelete = True
                    break
                if 'ForeignKey' in line:
                    context = '\n'.join(lines[max(0, i-1):i+3])
                    if "ondelete='SET NULL'" in context or 'ondelete="SET NULL"' in context:
                        found_ondelete = True
                        break
                if ')' in line and '=' not in line and in_column:
                    in_column = False

        assert found_ondelete, \
            "ConfigurationHistory.changed_by ForeignKey should have ondelete='SET NULL'"
