from __future__ import annotations

from fastapi import Request

from ..core.config import get_settings
from ..dependencies.auth import get_optional_user
from .repositories import WorldsStore

settings = get_settings()
worlds_store = WorldsStore(settings.worlds_db_path)


def get_worlds_store() -> WorldsStore:
    return worlds_store


def get_demo_user_id(request: Request) -> str:
    user = get_optional_user(request)
    if user:
        return user.id
    return "demo_user"


def get_optional_actor_id(request: Request) -> str | None:
    user = get_optional_user(request)
    if user:
        return user.id
    return "demo_user"
