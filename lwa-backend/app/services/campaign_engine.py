from __future__ import annotations

from dataclasses import dataclass


CAMPAIGN_ROLES: tuple[str, ...] = (
    "lead_clip",
    "trust_clip",
    "sales_clip",
    "educational_clip",
    "controversy_clip",
    "retargeting_clip",
    "community_clip",
)


@dataclass(frozen=True)
class CampaignClipRole:
    campaign_role: str
    campaign_reason: str
    funnel_stage: str
    suggested_post_order: int
    suggested_platform: str
    suggested_cta: str


def infer_campaign_role(*, transcript: str, index: int = 0, platform: str | None = None) -> CampaignClipRole:
    lowered = transcript.lower()
    if any(term in lowered for term in ("how", "steps", "method", "framework", "learn")):
        role = "educational_clip"
        stage = "education"
        reason = "Explains a process or framework."
        cta = "Save this for later."
    elif any(term in lowered for term in ("proof", "result", "before", "after", "case study")):
        role = "trust_clip"
        stage = "trust"
        reason = "Builds credibility with proof or transformation."
        cta = "Send this to someone who needs proof."
    elif any(term in lowered for term in ("book", "demo", "call", "join", "try", "upgrade")):
        role = "sales_clip"
        stage = "conversion"
        reason = "Contains an action or offer moment."
        cta = "Take the next step."
    elif any(term in lowered for term in ("wrong", "stop", "mistake", "nobody")):
        role = "controversy_clip"
        stage = "attention"
        reason = "Strong claim likely to create comments."
        cta = "Comment if you disagree."
    elif index > 3:
        role = "retargeting_clip"
        stage = "retargeting"
        reason = "Useful as a deeper follow-up asset."
        cta = "Watch the full breakdown."
    else:
        role = "lead_clip"
        stage = "awareness"
        reason = "Best positioned as an opening attention asset."
        cta = "Watch this first."

    return CampaignClipRole(
        campaign_role=role,
        campaign_reason=reason,
        funnel_stage=stage,
        suggested_post_order=index + 1,
        suggested_platform=platform or "auto",
        suggested_cta=cta,
    )


def build_campaign_plan(*, transcripts: list[str], platform: str | None = None) -> list[dict[str, object]]:
    return [
        infer_campaign_role(transcript=text, index=index, platform=platform).__dict__.copy()
        for index, text in enumerate(transcripts)
    ]
