from __future__ import annotations

import os
from uuid import uuid4

from .models import WebhookEvent, WebhookProvider
from .repositories import WebhookEventRepository, WorldsStore


WHOP_REQUIRED_ENV_VARS = ["WHOP_API_KEY", "WHOP_WEBHOOK_SECRET"]


def whop_readiness() -> dict:
    missing = [key for key in WHOP_REQUIRED_ENV_VARS if not os.getenv(key)]
    return {
        "configured": len(missing) == 0,
        "required_env_vars": WHOP_REQUIRED_ENV_VARS,
        "missing_env_vars": missing,
        "note": "Whop entitlement processing must verify webhook signatures before live use.",
    }


class WhopWebhookService:
    def __init__(self, store: WorldsStore):
        self.webhooks = WebhookEventRepository(store)

    def record_unprocessed_event(
        self,
        *,
        external_event_id: str | None,
        event_type: str,
        note: str,
    ) -> WebhookEvent:
        return self.webhooks.create(
            WebhookEvent(
                public_id=f"webhook_{uuid4().hex[:12]}",
                provider=WebhookProvider.whop,
                external_event_id=external_event_id,
                event_type=event_type,
                processed=False,
                status="blocked",
                note=note,
            )
        )
