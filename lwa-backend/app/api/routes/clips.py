from __future__ import annotations

from fastapi import APIRouter

from ...dependencies.auth import get_platform_store

router = APIRouter(tags=["clips"])
platform_store = get_platform_store()


@router.get("/clips/public")
async def public_clips() -> dict[str, object]:
    return {"clips": platform_store.list_public_clips(limit=50)}
