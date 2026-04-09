import importlib.util
import asyncio
from pathlib import Path
import shutil
from uuid import uuid4
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .generation import generate_clips
from .job_store import JobStore
from .processor import process_video_source, resolve_ffmpeg_path
from .schemas import (
    ClipBatchResponse,
    JobCreatedResponse,
    JobStatusResponse,
    ProcessRequest,
    ProcessingSummary,
    TrendsResponse,
)
from .trends import fetch_public_trends, trends_timestamp

settings = get_settings()
Path(settings.generated_assets_dir).mkdir(parents=True, exist_ok=True)
job_store = JobStore()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Starter backend for local video clip processing and monetizable MVP testing.",
)
app.mount("/generated", StaticFiles(directory=settings.generated_assets_dir), name="generated")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict[str, object]:
    base_url = settings.api_base_url or "http://127.0.0.1:8000"
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "docs_url": f"{base_url}/docs",
        "health_url": f"{base_url}/health",
        "jobs_url": f"{base_url}/v1/jobs",
        "trends_url": f"{base_url}/v1/trends",
        "api_key_header": settings.api_key_header_name if settings.api_key_secret else None,
    }


def dependency_health() -> dict[str, bool]:
    return {
        "ffmpeg": resolve_ffmpeg_path(settings) is not None,
        "yt_dlp": importlib.util.find_spec("yt_dlp") is not None,
        "openai_key_present": bool(settings.openai_api_key),
        "whop_key_present": bool(settings.whop_api_key),
        "google_key_present": bool(settings.google_api_key or settings.youtube_api_key),
        "tiktok_keys_present": bool(settings.tiktok_client_key and settings.tiktok_client_secret),
        "meta_keys_present": bool(
            (settings.meta_app_id and settings.meta_app_secret)
            or settings.facebook_page_access_token
            or settings.instagram_access_token
        ),
    }


def enforce_api_key(request: Request) -> None:
    if not settings.api_key_secret:
        return

    provided_key = request.headers.get(settings.api_key_header_name)
    if provided_key != settings.api_key_secret:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
@app.get("/v1/status/health")
async def health_check() -> dict[str, object]:
    checks = dependency_health()
    required_checks = [checks["ffmpeg"], checks["yt_dlp"]]
    overall_status = "ok" if all(required_checks) else "degraded"

    return {
        "status": overall_status,
        "service": settings.app_name,
        "environment": settings.environment,
        "version": settings.service_version,
        "port": settings.port,
        "dependencies": checks,
    }


def detect_platform(video_url: str) -> str:
    hostname = urlparse(video_url).netloc.lower()

    if "youtube" in hostname or "youtu.be" in hostname:
        return "YouTube"
    if "tiktok" in hostname:
        return "TikTok"
    if "instagram" in hostname:
        return "Instagram"

    return "Web"


@app.get("/v1/trends", response_model=TrendsResponse)
async def get_trends(http_request: Request) -> TrendsResponse:
    enforce_api_key(http_request)
    trends = await fetch_public_trends()
    return TrendsResponse(
        status="success",
        updated_at=trends_timestamp(),
        trends=trends,
    )


async def build_clip_response(
    *,
    request_id: str,
    request: ProcessRequest,
    public_base_url: str,
) -> ClipBatchResponse:
    video_url = str(request.video_url)
    target_platform = request.target_platform or "TikTok"
    trend_context = await fetch_public_trends()
    source_context = None

    try:
        source_context = await asyncio.to_thread(
            process_video_source,
            settings=settings,
            request_id=request_id,
            video_url=video_url,
            public_base_url=public_base_url,
        )
    except Exception:
        source_context = None

    clips, provider_used = await generate_clips(
        settings=settings,
        video_url=video_url,
        target_platform=target_platform,
        selected_trend=request.selected_trend,
        trend_context=trend_context,
        source_context=source_context,
    )
    processing_mode = source_context.processing_mode if source_context else "mock"
    source_title = source_context.title if source_context else None
    source_duration_seconds = source_context.duration_seconds if source_context else None
    assets_created = len([clip for clip in clips if clip.clip_url])
    selection_strategy = source_context.selection_strategy if source_context else "timeline"

    return ClipBatchResponse(
        request_id=request_id,
        video_url=request.video_url,
        status="success",
        source_platform=detect_platform(video_url),
        processing_summary=ProcessingSummary(
            plan_name=settings.default_plan_name,
            credits_remaining=settings.default_credits_remaining,
            estimated_turnaround="ready now" if assets_created else settings.default_turnaround,
            recommended_next_step=(
                "Open the generated clip asset, review the hook and caption, then push upgrades "
                "through Whop or your direct checkout."
                if assets_created
                else "Turn the top trend-led clip into a platform-specific export, then route upgrades "
                "through Whop or your direct checkout."
            ),
            ai_provider=provider_used,
            target_platform=target_platform,
            trend_used=request.selected_trend,
            sources_considered=sorted({item.source for item in trend_context}),
            processing_mode=processing_mode,
            selection_strategy=selection_strategy,
            source_title=source_title,
            source_duration_seconds=source_duration_seconds,
            assets_created=assets_created,
        ),
        trend_context=trend_context[:6],
        clips=clips,
    )


async def run_job(job_id: str, request: ProcessRequest, public_base_url: str) -> None:
    await job_store.update(
        job_id,
        status="processing",
        message="Downloading source, cutting clips, and generating copy.",
    )

    try:
        response = await build_clip_response(
            request_id=job_id,
            request=request,
            public_base_url=public_base_url,
        )
        await job_store.complete(job_id, response)
    except Exception as error:  # pragma: no cover - defensive runtime path
        await job_store.fail(job_id, str(error))


@app.post("/v1/jobs", response_model=JobCreatedResponse)
async def create_processing_job(request: ProcessRequest, http_request: Request) -> JobCreatedResponse:
    enforce_api_key(http_request)
    job_id = f"job_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    await job_store.create(job_id, "Job queued. Starting source analysis.")
    asyncio.create_task(run_job(job_id, request, public_base_url))
    return JobCreatedResponse(
        job_id=job_id,
        status="queued",
        poll_url=f"{public_base_url}/v1/jobs/{job_id}",
        message="Job queued. Poll for results.",
    )


@app.get("/v1/jobs/{job_id}", response_model=JobStatusResponse)
async def get_processing_job(job_id: str, http_request: Request) -> JobStatusResponse:
    enforce_api_key(http_request)
    record = await job_store.get(job_id)
    if not record:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=record.id,
        status=record.status,
        message=record.message,
        created_at=record.created_at,
        updated_at=record.updated_at,
        result=record.result,
        error=record.error,
    )


@app.post("/process", response_model=ClipBatchResponse)
@app.post("/v1/generate", response_model=ClipBatchResponse)
async def process_video(request: ProcessRequest, http_request: Request) -> ClipBatchResponse:
    enforce_api_key(http_request)
    request_id = f"req_{uuid4().hex[:10]}"
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    return await build_clip_response(
        request_id=request_id,
        request=request,
        public_base_url=public_base_url,
    )
