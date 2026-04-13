from __future__ import annotations

from pydantic import BaseModel


class UserRecord(BaseModel):
    id: str
    email: str
    plan: str
    balance_cents: int = 0
    created_at: str


class StoredUser(UserRecord):
    password_hash: str
