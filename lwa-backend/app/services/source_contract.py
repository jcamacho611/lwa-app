from __future__ import annotations

from pathlib import Path
from typing import Final

SOURCE_TYPE_VIDEO_UPLOAD: Final[str] = "video_upload"
SOURCE_TYPE_AUDIO_UPLOAD: Final[str] = "audio_upload"
SOURCE_TYPE_IMAGE_UPLOAD: Final[str] = "image_upload"
SOURCE_TYPE_PROMPT: Final[str] = "prompt"
SOURCE_TYPE_MUSIC: Final[str] = "music"
SOURCE_TYPE_CAMPAIGN: Final[str] = "campaign"
SOURCE_TYPE_URL: Final[str] = "url"
SOURCE_TYPE_UNKNOWN: Final[str] = "unknown"

STABLE_SOURCE_TYPES: Final[set[str]] = {
    SOURCE_TYPE_VIDEO_UPLOAD,
    SOURCE_TYPE_AUDIO_UPLOAD,
    SOURCE_TYPE_IMAGE_UPLOAD,
    SOURCE_TYPE_PROMPT,
    SOURCE_TYPE_MUSIC,
    SOURCE_TYPE_CAMPAIGN,
    SOURCE_TYPE_URL,
    "video",
    "audio",
    "image",
    "twitch",
    "stream",
    "upload",
    SOURCE_TYPE_UNKNOWN,
}

VIDEO_EXTENSIONS: Final[set[str]] = {".mp4", ".mov", ".m4v", ".webm"}
AUDIO_EXTENSIONS: Final[set[str]] = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".flac"}
IMAGE_EXTENSIONS: Final[set[str]] = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
ALLOWED_UPLOAD_EXTENSIONS: Final[set[str]] = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | IMAGE_EXTENSIONS

UPLOAD_ACCEPT_MIME_PREFIXES: Final[tuple[str, ...]] = ("video/", "audio/", "image/")

UNSUPPORTED_UPLOAD_MESSAGE: Final[str] = (
    "Unsupported file type. Upload a common video, audio, or image file, "
    "or use prompt mode for strategy-only generation."
)


def normalize_source_type(value: str | None) -> str:
    normalized = (value or "").strip().lower().replace("-", "_")
    if not normalized:
        return SOURCE_TYPE_UNKNOWN

    aliases = {
        "text": SOURCE_TYPE_PROMPT,
        "idea": SOURCE_TYPE_PROMPT,
        "prompt_only": SOURCE_TYPE_PROMPT,
        "campaign_objective": SOURCE_TYPE_CAMPAIGN,
        "objective": SOURCE_TYPE_CAMPAIGN,
        "file": "upload",
        "upload_file": "upload",
        "source_file": "upload",
        "public_url": SOURCE_TYPE_URL,
        "link": SOURCE_TYPE_URL,
    }
    normalized = aliases.get(normalized, normalized)
    return normalized if normalized in STABLE_SOURCE_TYPES else SOURCE_TYPE_UNKNOWN


def classify_upload_source_type(*, filename: str | None, content_type: str | None) -> str:
    lowered_content_type = (content_type or "").lower()
    suffix = Path(filename or "").suffix.lower()

    if lowered_content_type.startswith("audio/") or suffix in AUDIO_EXTENSIONS:
        return SOURCE_TYPE_AUDIO_UPLOAD
    if lowered_content_type.startswith("image/") or suffix in IMAGE_EXTENSIONS:
        return SOURCE_TYPE_IMAGE_UPLOAD
    if lowered_content_type.startswith("video/") or suffix in VIDEO_EXTENSIONS:
        return SOURCE_TYPE_VIDEO_UPLOAD
    return SOURCE_TYPE_UNKNOWN


def is_allowed_upload(*, filename: str | None, content_type: str | None) -> bool:
    suffix = Path(filename or "").suffix.lower()
    if suffix in ALLOWED_UPLOAD_EXTENSIONS:
        return True
    lowered_content_type = (content_type or "").lower()
    return any(lowered_content_type.startswith(prefix) for prefix in UPLOAD_ACCEPT_MIME_PREFIXES)


def upload_source_ref(*, upload_id: str, source_type: str) -> dict[str, str]:
    return {
        "source_kind": "upload",
        "source_type": normalize_source_type(source_type),
        "upload_id": upload_id,
    }


def supported_upload_summary() -> dict[str, list[str]]:
    return {
        "video": sorted(VIDEO_EXTENSIONS),
        "audio": sorted(AUDIO_EXTENSIONS),
        "image": sorted(IMAGE_EXTENSIONS),
    }
