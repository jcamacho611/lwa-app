from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from urllib.parse import urlencode

# LWA SOCIAL INTEGRATIONS FOUNDATION
# SANDBOX FIRST
# NO PASSWORD COLLECTION
# NO FAKE POSTING SUCCESS
# POLYMARKET READ ONLY CULTURAL METADATA
# DIRECT POSTING DISABLED UNTIL APPROVALS


class SocialProvider(StrEnum):
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITCH = "twitch"
    REDDIT = "reddit"
    POLYMARKET = "polymarket"
    GOOGLE_TRENDS = "google_trends"


class IntegrationStatus(StrEnum):
    AVAILABLE_READ_ONLY = "available_read_only"
    OAUTH_REQUIRED = "oauth_required"
    SANDBOX_ONLY = "sandbox_only"
    APPROVAL_REQUIRED = "approval_required"
    NOT_CONFIGURED = "not_configured"


@dataclass(frozen=True)
class ProviderCapability:
    provider: SocialProvider
    status: IntegrationStatus
    read_supported: bool
    publish_supported: bool
    required_env: tuple[str, ...] = ()
    required_scopes: tuple[str, ...] = ()
    safety_note: str = ""


@dataclass(frozen=True)
class OAuthStartRequest:
    provider: SocialProvider
    client_id: str
    redirect_uri: str
    state: str
    scopes: tuple[str, ...] = ()
    auth_base_url: str = ""
    extra_params: dict[str, str] = field(default_factory=dict)


PROVIDER_CAPABILITIES: tuple[ProviderCapability, ...] = (
    ProviderCapability(
        provider=SocialProvider.YOUTUBE,
        status=IntegrationStatus.OAUTH_REQUIRED,
        read_supported=True,
        publish_supported=False,
        required_env=("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REDIRECT_URI"),
        required_scopes=("youtube.readonly",),
        safety_note="Read first. Upload/publish requires approval and a separate explicit user action.",
    ),
    ProviderCapability(
        provider=SocialProvider.TIKTOK,
        status=IntegrationStatus.SANDBOX_ONLY,
        read_supported=True,
        publish_supported=False,
        required_env=("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"),
        safety_note="Sandbox first. Do not claim direct posting until app review and scopes are approved.",
    ),
    ProviderCapability(
        provider=SocialProvider.INSTAGRAM,
        status=IntegrationStatus.APPROVAL_REQUIRED,
        read_supported=True,
        publish_supported=False,
        required_env=("IG_APP_ID", "IG_APP_SECRET", "IG_REDIRECT_URI"),
        safety_note="Business/Creator account and app review required before publishing.",
    ),
    ProviderCapability(
        provider=SocialProvider.TWITCH,
        status=IntegrationStatus.OAUTH_REQUIRED,
        read_supported=True,
        publish_supported=False,
        required_env=("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "TWITCH_REDIRECT_URI"),
        required_scopes=("clips:edit",),
        safety_note="Clip creation requires user authorization. Live ingestion is future worker work.",
    ),
    ProviderCapability(
        provider=SocialProvider.REDDIT,
        status=IntegrationStatus.OAUTH_REQUIRED,
        read_supported=True,
        publish_supported=False,
        required_env=("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"),
        safety_note="Trend reads only unless commercial/API terms are reviewed.",
    ),
    ProviderCapability(
        provider=SocialProvider.POLYMARKET,
        status=IntegrationStatus.AVAILABLE_READ_ONLY,
        read_supported=True,
        publish_supported=False,
        required_env=(),
        safety_note="Read-only cultural-attention metadata only. No wagering, trading, or betting advice.",
    ),
    ProviderCapability(
        provider=SocialProvider.GOOGLE_TRENDS,
        status=IntegrationStatus.AVAILABLE_READ_ONLY,
        read_supported=True,
        publish_supported=False,
        required_env=(),
        safety_note="Trend metadata only. Provider implementation can be swapped later.",
    ),
)


def list_provider_capabilities() -> list[dict[str, Any]]:
    return [capability.__dict__.copy() for capability in PROVIDER_CAPABILITIES]


def get_provider_capability(provider: SocialProvider | str) -> ProviderCapability | None:
    normalized = SocialProvider(str(provider).strip().lower())
    return next((item for item in PROVIDER_CAPABILITIES if item.provider == normalized), None)


def build_oauth_authorization_url(request: OAuthStartRequest) -> str:
    if not request.auth_base_url:
        raise ValueError("auth_base_url is required for OAuth providers")
    if not request.client_id.strip():
        raise ValueError("client_id is required")
    if not request.redirect_uri.strip():
        raise ValueError("redirect_uri is required")
    if not request.state.strip():
        raise ValueError("state is required")

    params = {
        "client_id": request.client_id,
        "redirect_uri": request.redirect_uri,
        "response_type": "code",
        "state": request.state,
        **request.extra_params,
    }
    if request.scopes:
        params["scope"] = " ".join(request.scopes)
    return f"{request.auth_base_url}?{urlencode(params)}"


def posting_allowed(provider: SocialProvider | str) -> bool:
    capability = get_provider_capability(provider)
    return bool(capability and capability.publish_supported)


def social_integration_disclosure() -> str:
    return "Social integrations are sandbox/read-first until provider approvals, scopes, token storage, and explicit user actions are verified."
