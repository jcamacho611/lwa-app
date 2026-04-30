from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SocialProviderPlan:
    code: str
    name: str
    env_vars: tuple[str, ...]
    first_slice: str
    approval_note: str


SOCIAL_PROVIDER_PLANS: tuple[SocialProviderPlan, ...] = (
    SocialProviderPlan(
        "youtube",
        "YouTube Data API",
        ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REDIRECT_URI", "YT_API_KEY"),
        "read metadata first",
        "publishing requires approved scopes",
    ),
    SocialProviderPlan(
        "tiktok",
        "TikTok for Developers",
        ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"),
        "sandbox login/status shell first",
        "direct publish requires app review",
    ),
    SocialProviderPlan(
        "instagram",
        "Instagram Graph API",
        ("IG_APP_ID", "IG_APP_SECRET", "IG_REDIRECT_URI"),
        "business account/status shell first",
        "publishing requires account and app review checks",
    ),
    SocialProviderPlan(
        "twitch",
        "Twitch Helix",
        ("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "TWITCH_REDIRECT_URI"),
        "read metadata and clip status first",
        "clip actions require explicit user scope",
    ),
    SocialProviderPlan(
        "reddit",
        "Reddit API",
        ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"),
        "trend reads first",
        "respect provider access tier and rate limits",
    ),
    SocialProviderPlan(
        "polymarket",
        "Polymarket Gamma",
        tuple(),
        "read-only cultural trend metadata first",
        "no trading, wagering, or financial-advice flows",
    ),
    SocialProviderPlan(
        "google_trends",
        "Google Trends Provider",
        tuple(),
        "trend reads first",
        "use provider carefully because there is no official public API",
    ),
)


def list_social_provider_plans() -> list[dict[str, object]]:
    return [plan.__dict__.copy() for plan in SOCIAL_PROVIDER_PLANS]


def get_social_provider_plan(code: str) -> SocialProviderPlan | None:
    normalized = code.strip().lower().replace("-", "_")
    for plan in SOCIAL_PROVIDER_PLANS:
        if plan.code == normalized:
            return plan
    return None
