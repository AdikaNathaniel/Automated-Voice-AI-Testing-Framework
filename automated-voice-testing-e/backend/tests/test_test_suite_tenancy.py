from datetime import datetime, timezone
from uuid import uuid4

import pytest

from api.routes import test_suites
from api.schemas.auth import UserResponse
from api.schemas.test_suite import TestSuiteCreate, TestSuiteResponse


def _tenant_user(role: str = "admin") -> UserResponse:
    return UserResponse(
        id=uuid4(),
        email="tenant@example.com",
        username="tenant",
        full_name="Tenant Admin",
        role=role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tenant_id=uuid4(),
    )


@pytest.mark.asyncio
async def test_list_test_suites_passes_tenant(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()

    async def fake_list(db, filters, pagination, tenant_id=None):
        assert tenant_id == user.tenant_id
        return [], 0

    monkeypatch.setattr(test_suites.test_suite_service, "list_test_suites", fake_list)

    response = await test_suites.list_test_suites(
        db=object(),
        current_user=user,
        category=None,
        is_active=None,
        skip=0,
        limit=50,
    )

    assert response["total"] == 0


@pytest.mark.asyncio
async def test_create_test_suite_sets_tenant_id(monkeypatch: pytest.MonkeyPatch):
    user = _tenant_user()
    payload = TestSuiteCreate(
        name="Suite",
        description="desc",
        category="cat",
    )
    fake_suite = TestSuiteResponse(
        id=uuid4(),
        name=payload.name,
        description=payload.description,
        category=payload.category,
        is_active=True,
        created_by=user.id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    async def fake_create(db, data, user_id, tenant_id=None):
        assert tenant_id == user.tenant_id
        return fake_suite

    monkeypatch.setattr(test_suites.test_suite_service, "create_test_suite", fake_create)

    response = await test_suites.create_test_suite(
        data=payload,
        db=object(),
        current_user=user,
    )
    assert response.name == payload.name
