from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..core.config import Settings
from ..models.schemas import ProcessRequest
from ..processor import SourceContext

logger = logging.getLogger("uvicorn.error")

ANY_SOURCE_TYPES = {
    "video",
    "audio",
    "music",
    "prompt",
    "twitch",
    "stream",
    "campaign",
    "upload",
    "url",
    "video_upload",
    "audio_upload",
    "image_upload",
    "image",
    "idea",
    "unknown",
}

MEDIA_PROCESSABLE_SOURCE_TYPES = {
    "video",
    "audio",
    "twitch",
    "stream",
    "upload",
    "url",
    "video_upload",
    "audio_upload",
}

SOURCE_TYPE_ALIASES = {
    "text": "prompt",
    "idea": "prompt",
    "prompt_only": "prompt",
    "twitch_vod": "twitch",
    "vod": "stream",
    "livestream": "stream",
    "campaign_objective": "campaign",
    "objective": "campaign",
    "file": "upload",
    "upload_file": "upload",
    "source_file": "upload",
}


def normalize_source_type(value: str | None) -> str:
    normalized = (value or "").strip().lower().replace("-", "_")
    if not normalized:
        return "unknown"
    normalized = SOURCE_TYPE_ALIASES.get(normalized, normalized)
    return normalized if normalized in ANY_SOURCE_TYPES else "unknown"


def infer_source_type(request: ProcessRequest) -> str:
    explicit = normalize_source_type(request.source_type)
    if explicit != "unknown":
        return explicit

    content_type = (request.upload_content_type or "").lower()
    if request.upload_file_id:
        if content_type.startswith("audio/"):
            return "audio_upload"
        if content_type.startswith("image/"):
            return "image_upload"
        return "video_upload"

    source_url = (request.video_url or request.source_url or "").lower()
    if "twitch.tv" in source_url:
        return "twitch"
    if source_url:
        return "url"
    if (request.campaign_goal or request.campaign_brief or "").strip():
        return "campaign"
    if (request.prompt or request.text_prompt or "").strip():
        return "prompt"
    return "unknown"


def source_type_uses_media_pipeline(source_type: str, *, has_source_path: bool, source_url: str | None) -> bool:
    if has_source_path:
        return normalize_source_type(source_type) in MEDIA_PROCESSABLE_SOURCE_TYPES
    return bool(source_url) and normalize_source_type(source_type) in MEDIA_PROCESSABLE_SOURCE_TYPES


def source_platform_label(source_type: str, source_url: str | None = None) -> str:
    normalized = normalize_source_type(source_type)
    if normalized == "twitch":
        return "Twitch"
    if normalized == "stream":
        return "Stream"
    if normalized == "audio" or normalized == "audio_upload":
        return "Audio"
    if normalized == "music":
        return "Music"
    if normalized == "prompt":
        return "Prompt"
    if normalized == "campaign":
        return "Campaign"
    if normalized in {"upload", "video_upload", "image_upload"}:
        return "Upload"
    if source_url:
        lowered = source_url.lower()
        if "tiktok" in lowered:
            return "TikTok"
        if "instagram" in lowered:
            return "Instagram"
        if "youtube" in lowered or "youtu.be" in lowered:
            return "YouTube"
    if normalized == "video" or normalized == "url":
        return "Web"
    return "Unknown"


def source_value_for_request(request: ProcessRequest) -> str:
    return (
        (request.video_url or "").strip()
        or (request.source_url or "").strip()
        or (request.prompt or "").strip()
        or (request.text_prompt or "").strip()
        or (request.campaign_goal or "").strip()
        or (request.campaign_brief or "").strip()
        or "source"
    )


def classify_upload_source(upload: dict[str, object]) -> str:
    content_type = str(upload.get("content_type") or "").lower()
    filename = str(upload.get("file_name") or upload.get("filename") or "")
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if content_type.startswith("audio/") or suffix in {"mp3", "wav", "m4a", "aac", "ogg", "oga", "flac"}:
        return "audio_upload"
    if content_type.startswith("image/") or suffix in {"jpg", "jpeg", "png", "webp", "heic", "heif"}:
        return "image_upload"
    return "video_upload"


def build_strategy_source_context(*, request: ProcessRequest, source_type: str, source_value: str) -> SourceContext:
    prompt = (request.prompt or request.text_prompt or "").strip()
    campaign = (request.campaign_goal or request.campaign_brief or "").strip()
    metadata_parts = [
        prompt,
        campaign,
        (request.content_angle or "").strip(),
        ", ".join(request.allowed_platforms or []),
    ]
    description = " | ".join(part for part in metadata_parts if part)
    if not description:
        description = f"Strategy-only source package for {source_value}."

    title = (
        (request.source_metadata or {}).get("title")
        or prompt[:90]
        or campaign[:90]
        or source_value[:90]
        or f"{source_platform_label(source_type)} source"
    )

    return SourceContext(
        title=str(title),
        description=description,
        uploader=None,
        duration_seconds=None,
        source_url=source_value,
        clip_seeds=[],
        processing_mode="strategy_only",
        selection_strategy=f"{normalize_source_type(source_type)}_package",
        source_type=normalize_source_type(source_type),
        source_platform=source_platform_label(source_type, source_value),
        transcript=description,
        visual_summary=(
            "No rendered media was extracted for this request. "
            "LWA generated a strategy package with hooks, captions, thumbnail text, post order, and visual direction."
        ),
    )


class SourceIngestService:
    """Service for ingesting video sources from URLs."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    async def ingest_from_url(self, video_url: str) -> Dict[str, Any]:
        """Ingest video from URL and return metadata."""
        try:
            import yt_dlp

            if video_url and not video_url.startswith("http"):
                video_url = f"https://{video_url}"
            
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'best[height<=720]',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                "extractor_args": {"youtube": {"player_client": ["android", "web"]}},
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            }
            from ..processor import resolve_yt_cookie_file
            cookie_path = resolve_yt_cookie_file(self.settings)
            if cookie_path:
                ydl_opts["cookiefile"] = cookie_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                return {
                    "local_path": None,  # URL sources don't have local files
                    "title": info.get("title"),
                    "duration_seconds": info.get("duration"),
                    "webpage_url": info.get("webpage_url") or video_url,
                    "uploader": info.get("uploader"),
                }
                
        except Exception as error:
            logger.error(f"source_ingest_failed url={video_url} error={str(error)}")
            raise ValueError(f"Failed to ingest video from URL: {str(error)}")
