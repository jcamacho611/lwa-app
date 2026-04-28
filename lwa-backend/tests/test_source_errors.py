from __future__ import annotations

from app.services.source_errors import (
    PLATFORM_BLOCKED_MESSAGE,
    SourceFailureCode,
    classify_source_failure,
    public_source_error_message,
    source_failure_detail,
)


def test_youtube_bot_check_maps_to_platform_blocked() -> None:
    error = (
        "ERROR: [youtube] 3Or_EMwfr8U: Sign in to confirm you’re not a bot. "
        "Use --cookies-from-browser or --cookies for the authentication. "
        "See https://github.com/yt-dlp/yt-dlp/wiki/FAQ"
    )

    failure = classify_source_failure(error)

    assert failure is not None
    assert failure.code == SourceFailureCode.PLATFORM_BLOCKED
    assert failure.user_message == PLATFORM_BLOCKED_MESSAGE


def test_public_message_hides_raw_ytdlp_cookie_text() -> None:
    raw_error = (
        "ERROR: [youtube] 3Or_EMwfr8U: Sign in to confirm you’re not a bot. "
        "Use --cookies-from-browser or --cookies. See yt-dlp wiki."
    )

    message = public_source_error_message(raw_error)

    assert message == PLATFORM_BLOCKED_MESSAGE
    assert "yt-dlp" not in message.lower()
    assert "cookies" not in message.lower()
    assert "sign in to confirm" not in message.lower()
    assert "github" not in message.lower()


def test_source_failure_detail_is_frontend_safe() -> None:
    raw_error = "ERROR: [youtube] abc123: Sign in to confirm you’re not a bot. Use --cookies."

    failure = classify_source_failure(raw_error)
    assert failure is not None

    detail = source_failure_detail(failure)

    assert detail["code"] == "PLATFORM_BLOCKED"
    assert detail["message"] == PLATFORM_BLOCKED_MESSAGE
    assert detail["user_message"] == PLATFORM_BLOCKED_MESSAGE
    assert "cookies" not in detail["message"].lower()
    assert "yt-dlp" not in detail["message"].lower()
