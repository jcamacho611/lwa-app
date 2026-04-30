from __future__ import annotations

import os

from .models import ApiIntegrationStatus
from .repositories import IntegrationRepository, WorldsStore


INTEGRATION_DEFINITIONS = [
    {
        "integration_key": "openai",
        "name": "OpenAI",
        "category": "ai",
        "description": "Hooks, captions, ranking, packaging, structured outputs.",
        "env_vars": ["OPENAI_API_KEY"],
        "admin_only": False,
    },
    {
        "integration_key": "anthropic",
        "name": "Anthropic Claude",
        "category": "ai",
        "description": "Long transcript analysis, creator strategy, lore consistency.",
        "env_vars": ["ANTHROPIC_API_KEY"],
        "admin_only": False,
    },
    {
        "integration_key": "youtube",
        "name": "YouTube Data API",
        "category": "social",
        "description": "Video, channel, and playlist metadata.",
        "env_vars": ["YOUTUBE_API_KEY"],
        "admin_only": False,
    },
    {
        "integration_key": "tiktok",
        "name": "TikTok",
        "category": "social",
        "description": "Future login, share, and content posting where approved.",
        "env_vars": ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"],
        "admin_only": False,
    },
    {
        "integration_key": "instagram",
        "name": "Instagram Graph API",
        "category": "social",
        "description": "Future creator/business publishing and insights.",
        "env_vars": ["META_APP_ID", "META_APP_SECRET"],
        "admin_only": False,
    },
    {
        "integration_key": "twitch",
        "name": "Twitch",
        "category": "social",
        "description": "Streamer, VOD, and clip metadata.",
        "env_vars": ["TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET"],
        "admin_only": False,
    },
    {
        "integration_key": "whop",
        "name": "Whop",
        "category": "payments",
        "description": "Paid access, memberships, founder pass, and subscriptions.",
        "env_vars": ["WHOP_API_KEY", "WHOP_WEBHOOK_SECRET"],
        "admin_only": True,
    },
    {
        "integration_key": "stripe",
        "name": "Stripe Connect",
        "category": "payments",
        "description": "Future marketplace payouts and platform fees.",
        "env_vars": ["STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET"],
        "admin_only": True,
    },
    {
        "integration_key": "wallet",
        "name": "Wallet / LWA Chain",
        "category": "blockchain",
        "description": "Future optional proof, badges, and collectibles.",
        "env_vars": ["NEXT_PUBLIC_WALLETCONNECT_PROJECT_ID"],
        "admin_only": False,
    },
]


class IntegrationStatusService:
    def __init__(self, store: WorldsStore):
        self.repo = IntegrationRepository(store)

    def detect_status(self, env_vars: list[str]) -> str:
        if not env_vars:
            return "mocked"
        configured = [bool(os.getenv(env_var, "").strip()) for env_var in env_vars]
        if all(configured):
            return "configured"
        if any(configured):
            return "warning"
        return "not_configured"

    def sync_statuses(self) -> list[ApiIntegrationStatus]:
        results: list[ApiIntegrationStatus] = []
        for definition in INTEGRATION_DEFINITIONS:
            results.append(
                self.repo.upsert(
                    ApiIntegrationStatus(
                        integration_key=definition["integration_key"],
                        name=definition["name"],
                        category=definition["category"],
                        status=self.detect_status(definition["env_vars"]),
                        description=definition["description"],
                        admin_only=bool(definition["admin_only"]),
                    )
                )
            )
        return results

    def list_statuses(self) -> list[ApiIntegrationStatus]:
        existing = self.repo.list()
        if existing:
            return existing
        return self.sync_statuses()
