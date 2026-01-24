import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException

os.environ.setdefault("DATABASE_URL", "postgresql://tester:tester@localhost:5432/testdb")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret")
os.environ.setdefault("SOUNDHOUND_API_KEY", "fake-key")
os.environ.setdefault("SOUNDHOUND_CLIENT_ID", "fake-client")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "fake-aws-access-key")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "fake-aws-secret")

from api.routes import test_suites  # noqa: E402
from api.schemas.auth import UserResponse  # noqa: E402


def _user(role: str) -> UserResponse:
    return UserResponse(
        id=uuid4(),
        email="user@example.com",
        username="user",
        full_name="User",
        is_active=True,
        role=role,
        created_at=datetime.now(timezone.utc),
    )


def test_delete_suite_guard_allows_admin():
    test_suites._ensure_can_mutate_test_suite(_user("admin"))


def test_delete_suite_guard_blocks_viewer():
    with pytest.raises(HTTPException) as exc:
        test_suites._ensure_can_mutate_test_suite(_user("viewer"))
    assert exc.value.status_code == 403
