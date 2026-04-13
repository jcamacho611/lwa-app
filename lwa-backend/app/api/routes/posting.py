from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Request

from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import PostingConnectionCreate, ScheduledPostCreate, ScheduledPostPatch

router = APIRouter(prefix="/v1/posting", tags=["posting"])
platform_store = get_platform_store()
logger = logging.getLogger("uvicorn.error")


@router.get("/connections")
async def list_connections(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"connections": platform_store.list_posting_connections(user_id=user.id)}


@router.post("/connections")
async def create_connection(payload: PostingConnectionCreate, request: Request) -> dict[str, object]:
    user = require_user(request)
    connection = platform_store.create_posting_connection(
        user_id=user.id,
        provider=payload.provider,
        account_label=payload.account_label,
    )
    logger.info("posting_connection_created user_id=%s connection_id=%s provider=%s", user.id, connection["id"], payload.provider)
    return connection


@router.get("/scheduled")
async def list_scheduled(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"scheduled_posts": platform_store.list_scheduled_posts(user_id=user.id)}


@router.post("/scheduled")
async def create_scheduled(payload: ScheduledPostCreate, request: Request) -> dict[str, object]:
    user = require_user(request)
    clip = platform_store.get_clip(clip_id=payload.clip_id, user_id=user.id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    scheduled = platform_store.create_scheduled_post(
        user_id=user.id,
        clip_id=payload.clip_id,
        provider=payload.provider,
        caption=payload.caption,
        scheduled_for=payload.scheduled_for,
    )
    logger.info("posting_queue_event user_id=%s scheduled_id=%s provider=%s", user.id, scheduled["id"], payload.provider)
    return scheduled


@router.patch("/scheduled/{post_id}")
async def update_scheduled(post_id: str, payload: ScheduledPostPatch, request: Request) -> dict[str, object]:
    user = require_user(request)
    updated = platform_store.update_scheduled_post(
        post_id=post_id,
        user_id=user.id,
        updates=payload.model_dump(exclude_none=True),
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Scheduled post not found")
    return updated
