from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...auth.security import create_access_token, hash_password, verify_password
from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.omega_contracts import AuthTokenResponse, UserProfile
from ...models.schemas import AuthRequest

router = APIRouter(prefix="/v1/auth", tags=["auth"])
settings = get_settings()
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


def to_user_profile(user: UserProfile | object) -> UserProfile:
    if isinstance(user, UserProfile):
        return user
    return UserProfile(
        id=getattr(user, "id"),
        email=getattr(user, "email"),
        plan_code=getattr(user, "plan"),
        created_at=getattr(user, "created_at"),
    )


@router.post("/signup", response_model=AuthTokenResponse)
async def signup(payload: AuthRequest) -> AuthTokenResponse:
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    user = platform_store.create_user(
        email=payload.email,
        password_hash=hash_password(payload.password),
        plan="free",
    )
    logger.info("auth_signup_success email=%s user_id=%s", user.email, user.id)
    token = create_access_token(
        secret=settings.jwt_secret,
        user_id=user.id,
        email=user.email,
        plan=user.plan,
        exp_minutes=settings.jwt_exp_minutes,
    )
    return AuthTokenResponse(access_token=token, user=to_user_profile(user))


@router.post("/login", response_model=AuthTokenResponse)
async def login(payload: AuthRequest) -> AuthTokenResponse:
    user = platform_store.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning("auth_login_failed email=%s", payload.email.lower())
        raise HTTPException(status_code=401, detail="Invalid email or password")
    logger.info("auth_login_success email=%s user_id=%s", user.email, user.id)

    token = create_access_token(
        secret=settings.jwt_secret,
        user_id=user.id,
        email=user.email,
        plan=user.plan,
        exp_minutes=settings.jwt_exp_minutes,
    )
    return AuthTokenResponse(access_token=token, user=to_user_profile(user))


@router.post("/logout")
async def logout(_: Request) -> dict[str, str]:
    logger.info("auth_logout")
    return {"status": "ok", "message": "Client-side token logout complete."}


@router.get("/me", response_model=UserProfile)
async def me(request: Request) -> UserProfile:
    user = require_user(request)
    return to_user_profile(user)
