"""
MarketplaceEngine — Campaign match, opportunity teaser.

Status: SCAFFOLDED
Safety: No real campaign claims, no payments, no external API calls.
        Returns sample match data only.
"""

from __future__ import annotations

from typing import Any

from .base import (
    EngineCapability,
    EngineDemoResult,
    EngineStatus,
    LwaEngine,
    safe_payload,
    text_value,
    number_value,
)

_SAMPLE_CAMPAIGNS = [
    {
        "campaign_id": "camp_demo_001",
        "brand": "DemoSport",
        "category": "sports",
        "payout_range": "NOT_REAL — demo only",
        "match_score": 0.91,
        "requirements": ["min 1k followers", "sports content"],
    },
    {
        "campaign_id": "camp_demo_002",
        "brand": "TechGadgetCo",
        "category": "tech",
        "payout_range": "NOT_REAL — demo only",
        "match_score": 0.78,
        "requirements": ["tech niche", "min 500 avg views"],
    },
    {
        "campaign_id": "camp_demo_003",
        "brand": "LifestyleBrand",
        "category": "lifestyle",
        "payout_range": "NOT_REAL — demo only",
        "match_score": 0.65,
        "requirements": ["lifestyle content", "authentic voice"],
    },
]


class MarketplaceEngine(LwaEngine):
    """
    Matches creators to campaigns and surfaces opportunity teasers.
    Does NOT execute real campaign claims or process payments.
    """

    @property
    def engine_id(self) -> str:
        return "marketplace"

    @property
    def display_name(self) -> str:
        return "Marketplace Engine"

    @property
    def description(self) -> str:
        return "Campaign matching and opportunity surfacing for creators (no real claims)."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.SCAFFOLDED

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="campaign_match",
                description="Match a creator profile to available campaigns",
                local_safe=True,
            ),
            EngineCapability(
                name="opportunity_teaser",
                description="Surface top opportunities without committing to a claim",
                local_safe=True,
            ),
            EngineCapability(
                name="campaign_claim",
                description="Claim a campaign slot (requires payment integration)",
                local_safe=False,
                requires_provider=True,
                requires_payment=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        creator_id = text_value(p, "creator_id", "demo-creator")
        category = text_value(p, "category", "general")
        min_score = number_value(p, "min_match_score", 0.5)

        matches = [
            c for c in _SAMPLE_CAMPAIGNS if c["match_score"] >= min_score
        ]

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Found {len(matches)} sample campaign matches for creator '{creator_id}'",
            input_echo=p,
            output={
                "creator_id": creator_id,
                "category_filter": category,
                "matches": matches,
                "total_matches": len(matches),
                "claims_blocked": True,
                "claims_blocked_reason": "SCAFFOLDED — no payment provider connected",
                "disclaimer": "Sample data only. Payout figures are not real.",
            },
            warnings=[
                "SCAFFOLDED: sample campaign data only",
                "No real campaign claims can be made",
                "Payout figures shown are placeholders",
            ],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Campaign database (real campaign inventory)",
            "Payment provider (Stripe/Whop for claim processing)",
            "Creator profile store (follower count, niche, history)",
        ]

    def health_warnings(self) -> list[str]:
        return [
            "SCAFFOLDED: using sample campaign data",
            "Payment provider not connected — claims disabled",
        ]
