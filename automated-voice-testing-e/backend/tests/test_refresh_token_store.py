from datetime import datetime, timedelta, timezone
from uuid import uuid4

from services.refresh_token_store import RefreshTokenStore


def _expires() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=1)


def test_save_revokes_existing_tokens_for_user():
    store = RefreshTokenStore()
    user_id = uuid4()

    store.save("token-1", user_id=user_id, expires_at=_expires())
    assert store.verify("token-1", user_id=user_id)

    store.save("token-2", user_id=user_id, expires_at=_expires())

    assert store.verify("token-2", user_id=user_id)
    assert store.verify("token-1", user_id=user_id) is False
