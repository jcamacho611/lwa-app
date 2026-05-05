from __future__ import annotations

from fastapi import Request

from app.dependencies.auth import get_optional_user, require_user


def _user_to_dict(user: object | None) -> dict | None:
    if user is None:
        return None
    return {
        "id": getattr(user, "id", None),
        "user_id": getattr(user, "id", None),
        "email": getattr(user, "email", None),
        "plan": getattr(user, "plan", None),
        "role": getattr(user, "role", "creator"),
    }


def get_current_user_optional(request: Request) -> dict | None:
    return _user_to_dict(get_optional_user(request))


def get_current_user(request: Request) -> dict:
    return _user_to_dict(require_user(request)) or {}
