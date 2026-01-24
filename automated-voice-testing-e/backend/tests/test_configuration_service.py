"""
Unit tests for ConfigurationService.

Covers CRUD operations, activation toggles, and history/version control
behaviour ensuring configuration changes are tracked accurately.
"""

from __future__ import annotations

from typing import Iterator
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from models.base import Base
import sqlalchemy as sa

from models.configuration import Configuration
from models.configuration_history import ConfigurationHistory
from models.user import User


from services.configuration_service import ConfigurationService


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """Provide an isolated in-memory SQLite session for each test."""
    engine = create_engine("sqlite:///:memory:", future=True)

    Base.metadata.create_all(
        bind=engine,
        tables=[User.__table__, Configuration.__table__, ConfigurationHistory.__table__],
    )
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _fetch_history(session: Session, configuration_id: UUID) -> list[ConfigurationHistory]:
    stmt = (
        select(ConfigurationHistory)
        .where(ConfigurationHistory.configuration_id == configuration_id)
        .order_by(ConfigurationHistory.created_at.asc())
    )
    return list(session.execute(stmt).scalars())


def test_create_configuration_persists_and_records_history(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()

    config = service.create_configuration(
        config_key="  smtp.settings  ",
        config_data={"host": "smtp.example.com", "port": 587},
        description="SMTP delivery configuration",
        changed_by=actor,
        change_reason="Initial import",
    )

    assert config.id is not None
    assert config.config_key == "smtp.settings"
    assert config.config_data == {"host": "smtp.example.com", "port": 587}
    assert config.description == "SMTP delivery configuration"
    assert config.is_active is True

    history = _fetch_history(db_session, config.id)
    assert len(history) == 1
    entry = history[0]
    assert entry.changed_by == actor
    assert entry.old_value is None
    assert entry.new_value["config_key"] == "smtp.settings"
    assert entry.new_value["config_data"]["host"] == "smtp.example.com"
    assert entry.new_value["is_active"] is True
    assert entry.change_reason == "Initial import"


def test_update_configuration_mutates_state_and_appends_history(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()
    config = service.create_configuration(
        config_key="feature.flag",
        config_data={"enabled": False},
        changed_by=actor,
    )

    updated = service.update_configuration(
        configuration_id=config.id,
        config_data={"enabled": True, "rollout": 0.5},
        description="Feature flag rollout",
        changed_by=actor,
        change_reason="Enable beta rollout",
    )

    assert updated.description == "Feature flag rollout"
    assert updated.config_data == {"enabled": True, "rollout": 0.5}

    history = _fetch_history(db_session, config.id)
    assert len(history) == 2
    latest = history[-1]
    assert latest.change_reason == "Enable beta rollout"
    assert latest.old_value["config_data"]["enabled"] is False
    assert latest.new_value["config_data"]["rollout"] == 0.5


def test_create_cicd_integration_configuration(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    suite_id = str(uuid4())

    config = service.create_configuration(
        config_key="integration.cicd",
        config_data={
            "default_suite_id": suite_id,
            "providers": {
                "github": {
                    "secret": "super-secret",
                    "suite_id": suite_id,
                    "enabled": True,
                },
                "gitlab": {
                    "secret": "gitlab-secret",
                    "test_case_ids": ["11111111-1111-1111-1111-111111111111"],
                },
            },
        },
    )

    assert config.config_key == "integration.cicd"
    assert config.config_data["providers"]["github"]["suite_id"] == suite_id


def test_cicd_integration_configuration_requires_secret(db_session: Session) -> None:
    service = ConfigurationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.create_configuration(
            config_key="integration.cicd",
            config_data={
                "providers": {
                    "github": {
                        "suite_id": str(uuid4()),
                    }
                }
            },
        )

    assert "secret" in str(exc_info.value)


def test_create_jira_integration_configuration(db_session: Session) -> None:
    service = ConfigurationService(db_session)

    config = service.create_configuration(
        config_key="integration.jira",
        config_data={
            "base_url": "https://example.atlassian.net/rest/api/3",
            "browse_url": "https://example.atlassian.net",
            "user_email": "qa@example.com",
            "api_token": "token-123",
            "project_mapping": {
                "voice": {
                    "project_key": "QA",
                    "issue_type": "Bug",
                    "browse_url": "https://example.atlassian.net/browse",
                },
                "analytics": {
                    "project_key": "AN",
                    "issue_type": "Task",
                },
            },
        },
    )

    assert config.config_key == "integration.jira"
    assert config.config_data["base_url"] == "https://example.atlassian.net/rest/api/3"
    assert config.config_data["project_mapping"]["voice"]["project_key"] == "QA"
    assert config.config_data["project_mapping"]["analytics"]["issue_type"] == "Task"


@pytest.mark.parametrize(
    "payload, expected_message_fragment",
    [
        (
            {
                "api_token": "token",
                "project_mapping": {"default": {"project_key": "QA"}},
            },
            "base_url",
        ),
        (
            {
                "base_url": "https://example.atlassian.net/rest/api/3",
                "project_mapping": {"default": {"project_key": "QA"}},
            },
            "api_token",
        ),
        (
            {
                "base_url": "https://example.atlassian.net/rest/api/3",
                "api_token": "token",
            },
            "project_mapping",
        ),
    ],
)
def test_jira_integration_configuration_requires_fields(
    db_session: Session,
    payload: dict,
    expected_message_fragment: str,
) -> None:
    service = ConfigurationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.create_configuration(
            config_key="integration.jira",
            config_data=payload,
        )

    assert expected_message_fragment in str(exc_info.value)


def test_jira_integration_configuration_requires_project_key_mapping(db_session: Session) -> None:
    service = ConfigurationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.create_configuration(
            config_key="integration.jira",
            config_data={
                "base_url": "https://example.atlassian.net/rest/api/3",
                "api_token": "token",
                "project_mapping": {
                    "default": {"issue_type": "Bug"},
                },
            },
        )

    assert "project_key" in str(exc_info.value)


def test_jira_integration_configuration_requires_mapping_objects(db_session: Session) -> None:
    service = ConfigurationService(db_session)

    with pytest.raises(ValueError) as exc_info:
        service.create_configuration(
            config_key="integration.jira",
            config_data={
                "base_url": "https://example.atlassian.net/rest/api/3",
                "api_token": "token",
                "project_mapping": {
                    "default": "QA",
                },
            },
        )

    assert "object" in str(exc_info.value).lower()


def test_set_active_state_toggles_flag_and_tracks_history(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()
    config = service.create_configuration(
        config_key="queue.config",
        config_data={"size": 5},
        changed_by=actor,
    )

    inactive = service.set_active_state(
        configuration_id=config.id,
        is_active=False,
        changed_by=actor,
        change_reason="Temporarily disable queue",
    )
    assert inactive.is_active is False

    # Reactivate to ensure toggling works both ways.
    active = service.set_active_state(
        configuration_id=config.id,
        is_active=True,
        changed_by=actor,
        change_reason="Re-enable queue",
    )
    assert active.is_active is True

    history = _fetch_history(db_session, config.id)
    assert len(history) == 3  # create + two toggles
    assert history[-2].new_value["is_active"] is False
    assert history[-1].new_value["is_active"] is True


def test_delete_configuration_soft_deletes_and_logs_history(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()
    config = service.create_configuration(
        config_key="orphan.config",
        config_data={"value": 1},
        changed_by=actor,
    )

    deleted = service.delete_configuration(config.id, changed_by=actor, change_reason="cleanup")
    assert deleted.is_active is False
    assert deleted.config_data == {}
    assert service.get_configuration(config.id) is None
    assert service.get_configuration(config.id, include_inactive=True) is not None

    history = _fetch_history(db_session, config.id)
    assert len(history) == 2  # creation + deletion
    assert history[-1].new_value["is_active"] is False
    assert history[-1].change_reason == "cleanup"


def test_list_configurations_filters_by_active_state(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()
    service.create_configuration(config_key="a", config_data={}, changed_by=actor)
    config_b = service.create_configuration(config_key="b", config_data={}, changed_by=actor)
    service.set_active_state(
        configuration_id=config_b.id,
        is_active=False,
        changed_by=actor,
        change_reason="Disable",
    )

    active_items, _ = service.list_configurations(is_active=True)
    inactive_items, _ = service.list_configurations(is_active=False)

    assert {cfg.config_key for cfg in active_items} == {"a"}
    assert {cfg.config_key for cfg in inactive_items} == {"b"}


def test_create_configuration_enforces_schema_validation(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()

    with pytest.raises(ValueError) as exc:
        service.create_configuration(
            config_key="smtp.settings",
            config_data={"port": 25},  # Missing required host field
            changed_by=actor,
        )

    assert "smtp.settings" in str(exc.value)
    assert "host" in str(exc.value)


def test_set_active_state_rejects_invalid_existing_payload(db_session: Session) -> None:
    service = ConfigurationService(db_session)
    actor = uuid4()
    config = service.create_configuration(
        config_key="smtp.settings",
        config_data={"host": "smtp.example.com", "port": 587},
        changed_by=actor,
        is_active=False,
    )

    # Simulate legacy invalid data bypassing service-level validation.
    config.config_data = {"host": ""}  # Empty host is invalid
    db_session.flush()

    with pytest.raises(ValueError) as exc:
        service.set_active_state(
            configuration_id=config.id,
            is_active=True,
            changed_by=actor,
            change_reason="Reactivate",
        )

    assert "smtp.settings" in str(exc.value)
    assert "host" in str(exc.value)
