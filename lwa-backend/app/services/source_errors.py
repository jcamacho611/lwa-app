from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


PLATFORM_BLOCKED_MESSAGE = (
    "This platform blocked server access. Upload the video/audio file directly, "
    "try another public source, or use prompt mode."
)

SOURCE_TIMEOUT_MESSAGE = (
    "This source took too long to process. Try a shorter source, upload a trimmed file, "
    "or use prompt mode."
)

SOURCE_UNAVAILABLE_MESSAGE = (
    "This source is private, removed, unavailable, or region-locked. Upload your own file, "
    "try another public source, or use prompt mode."
)

PLATFORM_LIVE_MESSAGE = (
    "Live streams cannot be clipped from a public link yet. Upload the stream recording "
    "after it ends, or use prompt mode."
)

UNSUPPORTED_SOURCE_MESSAGE = (
    "This source could not be processed from a public link. Upload the file directly, "
    "try another public source, or use prompt mode."
)


class SourceFailureCode(str, Enum):
    PLATFORM_BLOCKED = "PLATFORM_BLOCKED"
    PLATFORM_PRIVATE = "PLATFORM_PRIVATE"
    PLATFORM_LIVE = "PLATFORM_LIVE"
    SOURCE_TIMEOUT = "SOURCE_TIMEOUT"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    UNSUPPORTED_SOURCE = "UNSUPPORTED_SOURCE"


@dataclass(frozen=True)
class SourceFailure:
    code: SourceFailureCode
    user_message: str
    technical_message: str


def _stringify_error(error: Any) -> str:
    if error is None:
        return ""

    detail = getattr(error, "detail", None)
    if isinstance(detail, str):
        return detail
    if isinstance(detail, dict):
        return " ".join(str(value) for value in detail.values() if value is not None)
    if isinstance(detail, list):
        return " ".join(str(value) for value in detail)

    return str(error)


def classify_source_failure(error: Any) -> SourceFailure | None:
    technical_message = _stringify_error(error)
    lower = technical_message.lower()

    if not lower:
        return None

    platform_blocked_markers = [
        "sign in to confirm",
        "not a bot",
        "use --cookies-from-browser",
        "--cookies",
        "cookies",
        "cookie",
        "yt-dlp",
        "youtube said",
        "confirm you",
        "blocked server access",
        "platform blocked",
    ]

    if any(marker in lower for marker in platform_blocked_markers):
        return SourceFailure(
            code=SourceFailureCode.PLATFORM_BLOCKED,
            user_message=PLATFORM_BLOCKED_MESSAGE,
            technical_message=technical_message,
        )

    live_markers = ["live stream", "livestream", "premiere", "currently live", "this live event"]
    if any(marker in lower for marker in live_markers):
        return SourceFailure(
            code=SourceFailureCode.PLATFORM_LIVE,
            user_message=PLATFORM_LIVE_MESSAGE,
            technical_message=technical_message,
        )

    timeout_markers = ["timeout", "timed out", "too long", "504", "deadline"]
    if any(marker in lower for marker in timeout_markers):
        return SourceFailure(
            code=SourceFailureCode.SOURCE_TIMEOUT,
            user_message=SOURCE_TIMEOUT_MESSAGE,
            technical_message=technical_message,
        )

    unavailable_markers = [
        "private",
        "removed",
        "unavailable",
        "region",
        "geo",
        "copyright",
        "age-restricted",
        "age restricted",
        "login required",
    ]
    if any(marker in lower for marker in unavailable_markers):
        return SourceFailure(
            code=SourceFailureCode.SOURCE_UNAVAILABLE,
            user_message=SOURCE_UNAVAILABLE_MESSAGE,
            technical_message=technical_message,
        )

    extractor_markers = ["extractor", "download", "source", "unsupported url", "unsupported source"]
    if any(marker in lower for marker in extractor_markers):
        return SourceFailure(
            code=SourceFailureCode.UNSUPPORTED_SOURCE,
            user_message=UNSUPPORTED_SOURCE_MESSAGE,
            technical_message=technical_message,
        )

    return None


def source_failure_detail(failure: SourceFailure) -> dict[str, str]:
    return {
        "code": failure.code.value,
        "message": failure.user_message,
        "user_message": failure.user_message,
    }


def public_source_error_message(error: Any) -> str:
    failure = classify_source_failure(error)
    if failure:
        return failure.user_message
    return _stringify_error(error) or "Could not process that source. Try uploading the file directly or use prompt mode."
