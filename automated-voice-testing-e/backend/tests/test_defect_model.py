"""
Unit tests for the Defect SQLAlchemy model.

Ensures the ORM definition matches the specifications from the defects table
migration: correct columns, constraints, defaults, and helper methods.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import sqlalchemy as sa

from models.defect import Defect
from models.base import GUID


def test_defect_model_schema_matches_migration():
    """Verify the Defect model exposes expected columns and constraints."""
    table = Defect.__table__

    assert table.name == "defects"
    assert list(table.c.keys()) == [
        "id",
        "tenant_id",
        "test_case_id",
        "test_execution_id",
        "severity",
        "category",
        "title",
        "description",
        "language_code",
        "detected_at",
        "status",
        "assigned_to",
        "resolved_at",
        "created_at",
        "jira_issue_key",
        "jira_issue_url",
        "jira_status",
    ]

    id_column = table.c.id
    assert isinstance(id_column.type, GUID)
    assert id_column.primary_key
    assert id_column.nullable is False

    tenant_id_column = table.c.tenant_id
    assert isinstance(tenant_id_column.type, GUID)
    assert tenant_id_column.nullable is True

    test_case_column = table.c.test_case_id
    assert isinstance(test_case_column.type, GUID)
    assert test_case_column.nullable is True
    test_case_fk = list(test_case_column.foreign_keys)
    assert len(test_case_fk) == 1
    assert test_case_fk[0].target_fullname == "test_cases.id"

    test_execution_column = table.c.test_execution_id
    assert isinstance(test_execution_column.type, GUID)
    assert test_execution_column.nullable is True

    severity_column = table.c.severity
    assert isinstance(severity_column.type, sa.String)
    assert severity_column.type.length == 50
    assert severity_column.nullable is False

    category_column = table.c.category
    assert isinstance(category_column.type, sa.String)
    assert category_column.type.length == 100
    assert category_column.nullable is False

    title_column = table.c.title
    assert isinstance(title_column.type, sa.String)
    assert title_column.type.length == 255
    assert title_column.nullable is False

    description_column = table.c.description
    assert isinstance(description_column.type, sa.Text)
    assert description_column.nullable is True

    language_column = table.c.language_code
    assert isinstance(language_column.type, sa.String)
    assert language_column.type.length == 10
    assert language_column.nullable is True

    detected_at_column = table.c.detected_at
    assert isinstance(detected_at_column.type, sa.DateTime)
    assert detected_at_column.type.timezone is True
    assert detected_at_column.nullable is False

    status_column = table.c.status
    assert isinstance(status_column.type, sa.String)
    assert status_column.type.length == 50
    assert status_column.nullable is False
    assert status_column.server_default is not None
    assert status_column.server_default.arg.text.strip("'\"") == "open"

    assigned_to_column = table.c.assigned_to
    assert isinstance(assigned_to_column.type, GUID)
    assert assigned_to_column.nullable is True
    assigned_fk = list(assigned_to_column.foreign_keys)
    assert len(assigned_fk) == 1
    assert assigned_fk[0].target_fullname == "users.id"

    # Check JIRA integration columns
    jira_issue_key_column = table.c.jira_issue_key
    assert isinstance(jira_issue_key_column.type, sa.String)
    assert jira_issue_key_column.nullable is True

    jira_issue_url_column = table.c.jira_issue_url
    assert isinstance(jira_issue_url_column.type, sa.String)
    assert jira_issue_url_column.nullable is True

    jira_status_column = table.c.jira_status
    assert isinstance(jira_status_column.type, sa.String)
    assert jira_status_column.nullable is True

    resolved_at_column = table.c.resolved_at
    assert isinstance(resolved_at_column.type, sa.DateTime)
    assert resolved_at_column.nullable is True

    created_at_column = table.c.created_at
    assert isinstance(created_at_column.type, sa.DateTime)
    assert created_at_column.type.timezone is True
    assert created_at_column.nullable is False
    assert created_at_column.server_default is not None


def test_defect_instance_helpers(monkeypatch):
    """Ensure helper methods (uuid generation, repr, to_dict) behave as expected."""
    fixed_uuid = uuid4()
    monkeypatch.setattr("uuid.uuid4", lambda: fixed_uuid)

    test_case_id = uuid4()
    test_execution_id = uuid4()
    assigned_to = uuid4()
    detected_at = datetime.now(timezone.utc)

    defect = Defect(
        test_case_id=test_case_id,
        test_execution_id=test_execution_id,
        severity="high",
        category="semantic",
        title="Expected response mismatch",
        description="Voice assistant returned wrong navigation route.",
        language_code="en",
        detected_at=detected_at,
        status="open",
        assigned_to=assigned_to,
    )

    assert defect.id == fixed_uuid
    assert "Defect" in repr(defect)
    assert str(fixed_uuid) in repr(defect)

    payload = defect.to_dict()
    assert payload["id"] == str(fixed_uuid)
    assert payload["test_case_id"] == str(test_case_id)
    assert payload["test_execution_id"] == str(test_execution_id)
    assert payload["severity"] == "high"
    assert payload["status"] == "open"
    assert payload["assigned_to"] == str(assigned_to)
    assert payload["detected_at"] == detected_at.isoformat()
    assert payload["resolved_at"] is None
    assert payload["created_at"] is None
