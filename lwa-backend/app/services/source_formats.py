from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".m4v", ".webm"}
SUPPORTED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a"}
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
SUPPORTED_UPLOAD_EXTENSIONS = (
    SUPPORTED_VIDEO_EXTENSIONS | SUPPORTED_AUDIO_EXTENSIONS | SUPPORTED_IMAGE_EXTENSIONS
)

SUPPORTED_VIDEO_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-m4v",
    "video/webm",
}
SUPPORTED_AUDIO_MIME_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/x-m4a",
}
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}
SUPPORTED_UPLOAD_MIME_TYPES = (
    SUPPORTED_VIDEO_MIME_TYPES | SUPPORTED_AUDIO_MIME_TYPES | SUPPORTED_IMAGE_MIME_TYPES
)

FRONTEND_ACCEPT = ",".join(
    sorted(
        SUPPORTED_UPLOAD_EXTENSIONS
        | SUPPORTED_VIDEO_MIME_TYPES
        | SUPPORTED_AUDIO_MIME_TYPES
        | SUPPORTED_IMAGE_MIME_TYPES
    )
)

UNSUPPORTED_UPLOAD_MESSAGE = (
    "Unsupported file type. Upload MP4, MOV, M4V, WEBM, MP3, WAV, M4A, "
    "JPG, PNG, WebP, HEIC, or HEIF."
)


@dataclass(frozen=True)
class SourceFormat:
    extension: str
    content_type: str
    source_type: str
    category: str


def normalize_extension(filename: str | None) -> str:
    return Path(filename or "").suffix.lower()


def normalize_content_type(content_type: str | None) -> str:
    return (content_type or "").split(";", 1)[0].strip().lower()


def source_type_for_upload(filename: str | None, content_type: str | None = None) -> str:
    extension = normalize_extension(filename)
    normalized_content_type = normalize_content_type(content_type)

    if extension in SUPPORTED_AUDIO_EXTENSIONS or normalized_content_type in SUPPORTED_AUDIO_MIME_TYPES:
        return "audio_upload"
    if extension in SUPPORTED_IMAGE_EXTENSIONS or normalized_content_type in SUPPORTED_IMAGE_MIME_TYPES:
        return "image_upload"
    if extension in SUPPORTED_VIDEO_EXTENSIONS or normalized_content_type in SUPPORTED_VIDEO_MIME_TYPES:
        return "video_upload"
    return "unknown"


def validate_upload_format(filename: str | None, content_type: str | None = None) -> SourceFormat:
    extension = normalize_extension(filename)
    normalized_content_type = normalize_content_type(content_type)
    source_type = source_type_for_upload(filename, normalized_content_type)

    if extension not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise ValueError(UNSUPPORTED_UPLOAD_MESSAGE)

    if normalized_content_type and normalized_content_type != "application/octet-stream":
        allowed_by_type = normalized_content_type in SUPPORTED_UPLOAD_MIME_TYPES
        allowed_by_extension = source_type != "unknown"
        if not allowed_by_type and not allowed_by_extension:
            raise ValueError(UNSUPPORTED_UPLOAD_MESSAGE)

    if source_type == "audio_upload":
        category = "audio"
    elif source_type == "image_upload":
        category = "image"
    elif source_type == "video_upload":
        category = "video"
    else:
        raise ValueError(UNSUPPORTED_UPLOAD_MESSAGE)

    return SourceFormat(
        extension=extension,
        content_type=normalized_content_type or "application/octet-stream",
        source_type=source_type,
        category=category,
    )
