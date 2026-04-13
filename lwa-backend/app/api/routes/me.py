from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import ClipPatchRequest

router = APIRouter(prefix="/v1/me", tags=["me"])
platform_store = get_platform_store()


@router.get("/clip-packs")
async def list_clip_packs(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"clip_packs": platform_store.list_clip_packs(user_id=user.id)}


@router.get("/clip-packs/{request_id}")
async def get_clip_pack(request_id: str, request: Request) -> dict[str, object]:
    user = require_user(request)
    payload = platform_store.get_clip_pack(user_id=user.id, request_id=request_id)
    if not payload["clips"]:
        raise HTTPException(status_code=404, detail="Clip pack not found")
    return payload


@router.patch("/clips/{clip_id}")
async def patch_clip(clip_id: str, payload: ClipPatchRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    updated = platform_store.update_clip_metadata(
        clip_id=clip_id,
        user_id=user.id,
        updates=payload.model_dump(exclude_none=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Clip not found")
    return updated
