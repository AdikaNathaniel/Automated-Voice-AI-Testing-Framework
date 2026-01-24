import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost:5432/testdb"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["JWT_SECRET_KEY"] = "super-secret-key-1234567890"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["SOUNDHOUND_API_KEY"] = "test-key"
os.environ["SOUNDHOUND_CLIENT_ID"] = "test-client"
os.environ["AWS_ACCESS_KEY_ID"] = "test-access"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret"

from api.routes import configurations  # noqa: E402
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


def test_ensure_privileged_user_allows_admin():
    user = _make_user("admin")
    configurations._ensure_privileged_user(user)


def test_ensure_privileged_user_rejects_viewer():
    viewer = _make_user("viewer")
    with pytest.raises(HTTPException) as exc:
        configurations._ensure_privileged_user(viewer)
    assert exc.value.status_code == 403
