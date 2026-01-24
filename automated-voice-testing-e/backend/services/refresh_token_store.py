"""
In-memory refresh token store with rotation semantics.

Production deployments should back this with Redis or a database; for the pilot
we keep it simple and process-local.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Set
from uuid import UUID


class RefreshTokenStore:
    """Tracks valid refresh tokens per user and enforces rotation."""

    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, object]] = {}
        self._user_tokens: Dict[UUID, Set[str]] = {}

    def save(self, token: str, *, user_id: UUID, expires_at: datetime) -> None:
        existing_tokens = self._user_tokens.get(user_id)
        if existing_tokens:
            for token_value in list(existing_tokens):
                self._records.pop(token_value, None)
            existing_tokens.clear()
        else:
            existing_tokens = set()
            self._user_tokens[user_id] = existing_tokens

        self._records[token] = {
            "user_id": user_id,
            "expires_at": expires_at,
        }
        existing_tokens.add(token)

    def revoke(self, token: str) -> None:
        data = self._records.pop(token, None)
        if not data:
            return
        user_id = data["user_id"]
        tokens = self._user_tokens.get(user_id)
        if tokens:
            tokens.discard(token)
            if not tokens:
                self._user_tokens.pop(user_id, None)

    def verify(self, token: str, *, user_id: UUID) -> bool:
        data = self._records.get(token)
        if not data:
            return False
        if data["user_id"] != user_id:
            return False

        expires_at = data["expires_at"]
        if isinstance(expires_at, datetime):
            if expires_at <= datetime.now(timezone.utc):
                self._records.pop(token, None)
                tokens = self._user_tokens.get(user_id)
                if tokens:
                    tokens.discard(token)
                    if not tokens:
                        self._user_tokens.pop(user_id, None)
                return False

        return True

    def clear(self) -> None:
        self._records.clear()
        self._user_tokens.clear()


refresh_token_store = RefreshTokenStore()
