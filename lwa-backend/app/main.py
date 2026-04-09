import importlib.util
from pathlib import Path
import shutil
from uuid import uuid4
from urllib.parse import urlparse

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .generation import generate_clips
from .processor import process_video_source, resolve_ffmpeg_path
from .schemas import ClipBatchResponse, ProcessRequest, ProcessingSummary, TrendsResponse
from .trends import fetch_public_trends, trends_timestamp

settings = get_settings()
Path(settings.generated_assets_dir).mkdir(parents=True, exist_ok=True)

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
async def get_trends() -> TrendsResponse:
    trends = await fetch_public_trends()
    return TrendsResponse(
        status="success",
        updated_at=trends_timestamp(),
        trends=trends,
    )


@app.post("/process", response_model=ClipBatchResponse)
@app.post("/v1/generate", response_model=ClipBatchResponse)
async def process_video(request: ProcessRequest, http_request: Request) -> ClipBatchResponse:
    request_id = f"req_{uuid4().hex[:10]}"
    video_url = str(request.video_url)
    target_platform = request.target_platform or "TikTok"
    trend_context = await fetch_public_trends()
    public_base_url = (settings.api_base_url or str(http_request.base_url)).rstrip("/")
    source_context = None

    try:
        source_context = process_video_source(
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
            source_title=source_title,
            source_duration_seconds=source_duration_seconds,
            assets_created=assets_created,
        ),
        trend_context=trend_context[:6],
        clips=clips,
    )
