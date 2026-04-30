from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlatformSignal:
    platform: str
    recommended_length: str
    hook_window: str
    main_signal: str
    caption_note: str


PLATFORM_SIGNALS: dict[str, PlatformSignal] = {
    "tiktok": PlatformSignal("TikTok", "7-60s", "first 1-3s", "completion and replay", "fast burned-in captions"),
    "instagram_reels": PlatformSignal("Instagram Reels", "15-60s", "first 2s", "shares and saves", "clean readable captions"),
    "youtube_shorts": PlatformSignal("YouTube Shorts", "15-60s", "first 1s", "engaged views and rewatches", "captions plus title keywords"),
    "linkedin": PlatformSignal("LinkedIn", "30-90s", "first 3s", "dwell and comment depth", "professional readable captions"),
    "facebook_reels": PlatformSignal("Facebook Reels", "15-60s", "first 3s", "watch time and sharing", "retention captions"),
    "x_video": PlatformSignal("X Video", "15-140s", "first 2s", "replies and reposts", "manual captions recommended"),
    "twitch_clips": PlatformSignal("Twitch Clips", "5-60s", "first 3s", "clip velocity", "context text helps"),
    "whop_community": PlatformSignal("Whop Community", "30-90s", "first 3s", "completion and discussion", "accessibility captions"),
}


def normalize_platform(platform: str | None) -> str:
    value = (platform or "tiktok").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "instagram": "instagram_reels",
        "reels": "instagram_reels",
        "youtube": "youtube_shorts",
        "shorts": "youtube_shorts",
        "twitter": "x_video",
        "x": "x_video",
        "twitch": "twitch_clips",
        "whop": "whop_community",
    }
    return aliases.get(value, value)


def get_platform_signal(platform: str | None) -> PlatformSignal:
    return PLATFORM_SIGNALS.get(normalize_platform(platform), PLATFORM_SIGNALS["tiktok"])


def platform_fit_score(*, platform: str | None, duration_seconds: int | None, has_captions: bool = True) -> dict[str, object]:
    signal = get_platform_signal(platform)
    score = 70
    if duration_seconds is not None:
        if signal.platform in {"TikTok", "Instagram Reels", "YouTube Shorts", "Facebook Reels"} and 7 <= duration_seconds <= 90:
            score += 15
        elif signal.platform == "Twitch Clips" and 5 <= duration_seconds <= 60:
            score += 15
        elif signal.platform in {"LinkedIn", "Whop Community"} and 20 <= duration_seconds <= 120:
            score += 15
        else:
            score -= 10
    if has_captions:
        score += 5
    return {
        "platform": signal.platform,
        "score": max(0, min(100, score)),
        "recommended_length": signal.recommended_length,
        "hook_window": signal.hook_window,
        "main_signal": signal.main_signal,
        "caption_note": signal.caption_note,
    }
