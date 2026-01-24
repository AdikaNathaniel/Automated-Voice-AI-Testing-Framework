"""
Unit tests for the EdgeCase SQLAlchemy model.

Ensures the ORM definition matches the edge_cases table migration schema and
that helper methods provide serialisable representations for downstream usage.
"""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import sqlalchemy as sa

from models.base import GUID
from models.edge_case import EdgeCase


def test_edge_case_model_schema_matches_migration():
    """Verify the EdgeCase model exposes expected columns and constraints."""
    table = EdgeCase.__table__

    assert table.name == "edge_cases"
    assert list(table.c.keys()) == [
        "id",
        "title",
        "description",
        "category",
        "severity",
        "scenario_definition",
        "test_case_id",
        "discovered_date",
        "discovered_by",
        "status",
        "tags",
        "created_at",
        "updated_at",
    ]

    id_column = table.c.id
    assert isinstance(id_column.type, GUID)
    assert id_column.primary_key
    assert id_column.nullable is False

    title_column = table.c.title
    assert isinstance(title_column.type, sa.String)
    assert title_column.type.length == 255
    assert title_column.nullable is False

    description_column = table.c.description
    assert isinstance(description_column.type, sa.Text)
    assert description_column.nullable is True

    category_column = table.c.category
    assert isinstance(category_column.type, sa.String)
    assert category_column.type.length == 100
    assert category_column.nullable is True

    severity_column = table.c.severity
    assert isinstance(severity_column.type, sa.String)
    assert severity_column.type.length == 50
    assert severity_column.nullable is True

    scenario_definition_column = table.c.scenario_definition
    assert isinstance(scenario_definition_column.type, sa.dialects.postgresql.JSONB)
    assert scenario_definition_column.nullable is False
    assert scenario_definition_column.server_default is not None
    assert scenario_definition_column.server_default is not None
    assert "{}" in scenario_definition_column.server_default.arg.text

    test_case_column = table.c.test_case_id
    assert isinstance(test_case_column.type, GUID)
    assert test_case_column.nullable is True
    test_case_fk = list(test_case_column.foreign_keys)
    assert len(test_case_fk) == 1
    assert test_case_fk[0].target_fullname == "test_cases.id"

    discovered_date_column = table.c.discovered_date
    assert isinstance(discovered_date_column.type, sa.Date)
    assert discovered_date_column.nullable is True

    discovered_by_column = table.c.discovered_by
    assert isinstance(discovered_by_column.type, GUID)
    assert discovered_by_column.nullable is True
    discovered_by_fk = list(discovered_by_column.foreign_keys)
    assert len(discovered_by_fk) == 1
    assert discovered_by_fk[0].target_fullname == "users.id"

    status_column = table.c.status
    assert isinstance(status_column.type, sa.String)
    assert status_column.type.length == 50
    assert status_column.nullable is False
    assert status_column.server_default is not None
    assert "active" in status_column.server_default.arg.text

    tags_column = table.c.tags
    assert isinstance(tags_column.type, sa.dialects.postgresql.ARRAY)
    assert isinstance(tags_column.type.item_type, sa.Text)
    assert tags_column.nullable is False
    assert tags_column.server_default is not None
    assert tags_column.server_default is not None
    assert "[]" in tags_column.server_default.arg.text

    created_at_column = table.c.created_at
    assert isinstance(created_at_column.type, sa.DateTime)
    assert created_at_column.type.timezone is True
    assert created_at_column.nullable is False
    assert created_at_column.server_default is not None

    updated_at_column = table.c.updated_at
    assert isinstance(updated_at_column.type, sa.DateTime)
    assert updated_at_column.type.timezone is True
    assert updated_at_column.nullable is False
    assert updated_at_column.server_default is not None


def test_edge_case_to_dict_and_repr(monkeypatch):
    """Ensure helper behaviours serialise primitives and include identifiers."""
    fixed_uuid = uuid4()
    monkeypatch.setattr("models.edge_case.uuid.uuid4", lambda: fixed_uuid)

    test_case_id = uuid4()
    discovered_by = uuid4()
    scenario = {"steps": ["user says 'Navigate home'", "assistant confirms route"]}
    discovered_on = date(2025, 10, 26)
    edge_case = EdgeCase(
        title="Navigation ambiguity near landmarks",
        description="Voice assistant chooses incorrect landmark when multiple match.",
        category="ambiguity",
        severity="high",
        scenario_definition=scenario,
        test_case_id=test_case_id,
        discovered_date=discovered_on,
        discovered_by=discovered_by,
        status="active",
        tags=["navigation", "ambiguity"],
    )

    assert edge_case.id == fixed_uuid
    assert f"{fixed_uuid}" in repr(edge_case)

    payload = edge_case.to_dict()
    assert payload["id"] == str(fixed_uuid)
    assert payload["title"] == "Navigation ambiguity near landmarks"
    assert payload["scenario_definition"] == scenario
    assert payload["test_case_id"] == str(test_case_id)
    assert payload["discovered_date"] == discovered_on.isoformat()
    assert payload["discovered_by"] == str(discovered_by)
    assert payload["status"] == "active"
    assert payload["tags"] == ["navigation", "ambiguity"]
    # created_at/updated_at not set until persisted
    assert payload["created_at"] is None
    assert payload["updated_at"] is None
