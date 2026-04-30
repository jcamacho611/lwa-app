from __future__ import annotations

from fastapi import HTTPException, Request

from ..auth.security import decode_access_token
from ..core.config import get_settings
from ..models.user import UserRecord
from ..services.platform_store import PlatformStore

settings = get_settings()
platform_store = PlatformStore(settings.platform_db_path)


def get_platform_store() -> PlatformStore:
    return platform_store


def get_optional_user(request: Request) -> UserRecord | None:
    authorization = (request.headers.get("Authorization") or "").strip()
    if not authorization:
        return None

    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_access_token(token, secret=settings.jwt_secret)
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error

    user_id = str(payload.get("sub") or "").strip()
    user = platform_store.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def free_launch_guest_user() -> UserRecord:
    return UserRecord(
        id="guest",
        email="guest@free-launch.local",
        plan="free_launch",
        role="guest",
        balance_cents=0,
        created_at="free_launch",
    )


def require_user(request: Request) -> UserRecord:
    user = get_optional_user(request)
    if not user:
        if settings.free_launch_mode:
            return free_launch_guest_user()
        raise HTTPException(status_code=401, detail="Authentication required")
    return user
