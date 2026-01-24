import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

os_env = {
    "DATABASE_URL": "postgresql://tester:tester@localhost:5432/testdb",
    "REDIS_URL": "redis://localhost:6379/0",
    "JWT_SECRET_KEY": "unit-test-secret",
    "SOUNDHOUND_API_KEY": "fake-soundhound-key",
    "SOUNDHOUND_CLIENT_ID": "fake-client-id",
    "AWS_ACCESS_KEY_ID": "fake-aws-access-key",
    "AWS_SECRET_ACCESS_KEY": "fake-aws-secret",
}


for key, value in os_env.items():
    os.environ.setdefault(key, value)


from api.routes.auth import _ensure_admin_user  # noqa: E402
from api.schemas.auth import UserResponse  # noqa: E402


def _make_user(role: str) -> UserResponse:
    return UserResponse(
        id=uuid4(),
        email="user@example.com",
        username="user",
        full_name="User",
        is_active=True,
        role=role,
        created_at=datetime.now(timezone.utc),
    )


def test_admin_guard_allows_admin():
    _ensure_admin_user(_make_user("admin"))


def test_admin_guard_blocks_viewer():
    viewer = _make_user("viewer")
    with pytest.raises(HTTPException) as exc:
        _ensure_admin_user(viewer)
    assert exc.value.status_code == 403
