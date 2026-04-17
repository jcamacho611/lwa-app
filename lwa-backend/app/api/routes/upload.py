from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from ...core.config import get_settings
from ...dependencies.auth import get_platform_store, require_user
from ...models.schemas import UploadResponse
from ...services.entitlements import UsageStore, get_plan_for_user

router = APIRouter(prefix="/v1/uploads", tags=["uploads"])
settings = get_settings()
platform_store = get_platform_store()
usage_store = UsageStore(settings.usage_store_path)
ALLOWED_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".oga",
    ".flac",
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".heic",
    ".heif",
}
logger = logging.getLogger("uvicorn.error")


@router.post("", response_model=UploadResponse)
async def upload_file(request: Request, file: UploadFile = File(...)) -> UploadResponse:
    user = require_user(request)
    logger.info("upload_received user_id=%s filename=%s", user.id, file.filename)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    plan = get_plan_for_user(settings=settings, user=user)
    upload_limit = int(plan.feature_flags.max_uploads_per_day or 0)
    usage_day: str | None = None
    if upload_limit >= 0:
        try:
            usage_day, _ = usage_store.reserve(
                subject=f"upload:user:{user.id}",
                daily_limit=upload_limit,
            )
        except HTTPException as error:
            raise HTTPException(
                status_code=402,
                detail=(
                    "Daily upload limit reached for the current plan. "
                    "Upgrade to Pro for more daily source uploads or Scale for higher throughput."
                ),
            ) from error

    destination_dir = Path(settings.uploads_dir) / user.id
    destination_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex[:12]}{suffix}"
    stored_path = destination_dir / stored_name
    size_limit = settings.max_upload_mb * 1024 * 1024
    total_size = 0

    try:
        with stored_path.open("wb") as handle:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > size_limit:
                    stored_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=413, detail="Upload exceeds configured size limit")
                handle.write(chunk)

        base_url = (settings.api_base_url or str(request.base_url)).rstrip("/")
        public_url = f"{base_url}/uploads/{user.id}/{stored_name}"
        upload = platform_store.create_upload(
            user_id=user.id,
            file_name=file.filename or stored_name,
            stored_path=str(stored_path),
            public_url=public_url,
            content_type=file.content_type,
            file_size=total_size,
        )
        logger.info("upload_validated user_id=%s upload_id=%s size_bytes=%s", user.id, upload["id"], total_size)
        return UploadResponse(
            file_id=upload["id"],
            filename=upload["file_name"],
            content_type=upload["content_type"] or "application/octet-stream",
            size_bytes=upload["file_size"],
            public_url=upload["public_url"],
            storage_path=upload["stored_path"],
            source_ref={"source_kind": "upload", "upload_id": upload["id"]},
        )
    except Exception:
        if usage_day:
            usage_store.release(subject=f"upload:user:{user.id}", usage_day=usage_day)
        raise


@router.get("")
async def list_uploads(request: Request) -> dict[str, object]:
    user = require_user(request)
    return {"uploads": platform_store.list_uploads(user_id=user.id)}


@router.get("/{upload_id}")
async def get_upload(upload_id: str, request: Request) -> dict[str, object]:
    user = require_user(request)
    upload = platform_store.get_upload(upload_id, user_id=user.id)
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    return upload
