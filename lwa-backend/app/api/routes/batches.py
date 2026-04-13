from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.omega_contracts import BatchCreateRequest

router = APIRouter(prefix="/v1/batches", tags=["batches"])
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


@router.post("")
async def create_batch(payload: BatchCreateRequest, request: Request) -> dict[str, object]:
    user = require_user(request)
    batch = platform_store.create_batch(
        user_id=user.id,
        title=payload.title,
        target_platform=payload.target_platform,
        selected_trend=payload.selected_trend,
        sources=[source.model_dump() for source in payload.sources],
    )
    logger.info("batch_created user_id=%s batch_id=%s sources=%s", user.id, batch["id"], len(payload.sources))
    return batch


@router.get("")
async def list_batches(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"batches": platform_store.list_batches(user_id=user.id)}


@router.get("/{batch_id}")
async def get_batch(batch_id: str, request: Request) -> dict[str, object]:
    user = require_user(request)
    batch = platform_store.get_batch(batch_id=batch_id, user_id=user.id)
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch
