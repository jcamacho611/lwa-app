"""Demo Mode service for LWA.

Provides sample content for new users to experience the platform
without needing their own source video.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4


@dataclass
class SampleClip:
    id: str
    title: str
    hook: str
    caption: str
    timestamp_start: float
    timestamp_end: float
    score: float
    campaign_role: str
    funnel_stage: str
    suggested_cta: str
    why_this_matters: str


# Sample demo content (public domain / safe content)
SAMPLE_SOURCE = {
    "id": "demo_source_001",
    "title": "Sample Creator Interview - Building in Public",
    "description": "A 5-minute interview about content creation strategy",
    "duration_seconds": 300,
    "url": None,  # No actual video, text-only demo
    "type": "demo_text_only",
}

SAMPLE_CLIPS: List[SampleClip] = [
    SampleClip(
        id="demo_clip_001",
        title="Stop guessing what content works",
        hook="Stop guessing what content works. Here's the data.",
        caption="The algorithm rewards consistency + strong hooks. Watch the pattern.",
        timestamp_start=12.5,
        timestamp_end=45.0,
        score=0.88,
        campaign_role="lead_clip",
        funnel_stage="awareness",
        suggested_cta="Comment if you want the full breakdown.",
        why_this_matters="Strongest hook. Opens with contradiction + data promise.",
    ),
    SampleClip(
        id="demo_clip_002",
        title="The mistake that kills 90% of channels",
        hook="The mistake that kills 90% of channels before they hit 1000 subs.",
        caption="Posting without a system. Here's what actually works.",
        timestamp_start=67.0,
        timestamp_end=112.0,
        score=0.82,
        campaign_role="trust_clip",
        funnel_stage="consideration",
        suggested_cta="Save this before you plan your next post.",
        why_this_matters="Builds credibility with specific failure stat.",
    ),
    SampleClip(
        id="demo_clip_003",
        title="How to turn one video into 10 clips",
        hook="How to turn one video into 10 clips without more filming.",
        caption="Repurposing is a skill. Learn the system.",
        timestamp_start=145.0,
        timestamp_end=198.0,
        score=0.79,
        campaign_role="educational_clip",
        funnel_stage="consideration",
        suggested_cta="Save this and use it on your next clip.",
        why_this_matters="Teaches the core LWA value proposition.",
    ),
    SampleClip(
        id="demo_clip_004",
        title="Your first 30 days as a creator",
        hook="Your first 30 days as a creator — the truth nobody tells you.",
        caption="The real playbook. No fluff.",
        timestamp_start=210.0,
        timestamp_end=265.0,
        score=0.75,
        campaign_role="sales_clip",
        funnel_stage="conversion",
        suggested_cta="Start with LWA and turn one source into a campaign.",
        why_this_matters="Contains action/offer language for conversion.",
    ),
]


def get_demo_source() -> Dict[str, Any]:
    """Get the sample demo source for new users."""
    return {
        "success": True,
        "source": {
            **SAMPLE_SOURCE,
            "is_demo": True,
            "clips_available": len(SAMPLE_CLIPS),
        },
        "message": "Demo source loaded. This is a text-only preview for demonstration.",
    }


def get_demo_clips() -> Dict[str, Any]:
    """Get sample clips for the demo source."""
    clips = [
        {
            "clip_id": clip.id,
            "title": clip.title,
            "hook": clip.hook,
            "caption": clip.caption,
            "timestamp_start": clip.timestamp_start,
            "timestamp_end": clip.timestamp_end,
            "score": clip.score,
            "campaign_role": clip.campaign_role,
            "funnel_stage": clip.funnel_stage,
            "suggested_cta": clip.suggested_cta,
            "why_this_matters": clip.why_this_matters,
            "is_demo": True,
            "strategy_only": True,  # No playable media
            "render_status": "strategy_only",
        }
        for clip in SAMPLE_CLIPS
    ]
    
    # Sort by score descending
    clips.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "success": True,
        "clips": clips,
        "count": len(clips),
        "source_id": SAMPLE_SOURCE["id"],
        "is_demo": True,
        "message": f"Demo clip pack generated with {len(clips)} clips.",
    }


def create_demo_campaign_pack() -> Dict[str, Any]:
    """Create a full demo campaign pack ready for export."""
    clips_data = get_demo_clips()
    clips = clips_data["clips"]
    
    # Build campaign metadata
    campaign = {
        "id": f"demo_campaign_{uuid4().hex[:8]}",
        "name": "Demo Creator Campaign",
        "source_id": SAMPLE_SOURCE["id"],
        "created_at": datetime.utcnow().isoformat() + "Z",
        "clips": clips,
        "posting_schedule": [
            {"day": 1, "clip_id": clips[0]["clip_id"], "platform": "tiktok", "time": "9:00 AM"},
            {"day": 2, "clip_id": clips[1]["clip_id"], "platform": "instagram", "time": "12:00 PM"},
            {"day": 3, "clip_id": clips[2]["clip_id"], "platform": "youtube_shorts", "time": "5:00 PM"},
            {"day": 5, "clip_id": clips[3]["clip_id"], "platform": "tiktok", "time": "9:00 AM"},
        ],
        "bundle_contents": {
            "hooks": [clip["hook"] for clip in clips],
            "captions": [clip["caption"] for clip in clips],
            "timestamps": [
                {
                    "clip_id": clip["clip_id"],
                    "start": clip["timestamp_start"],
                    "end": clip["timestamp_end"],
                }
                for clip in clips
            ],
            "ctas": [clip["suggested_cta"] for clip in clips],
        },
        "is_demo": True,
    }
    
    return {
        "success": True,
        "campaign": campaign,
        "message": "Demo campaign pack ready for export.",
    }


def save_demo_proof(user_id: str) -> Dict[str, Any]:
    """Save demo clips to Proof Vault for the user."""
    clips_data = get_demo_clips()
    clips = clips_data["clips"]
    
    saved_assets = []
    for clip in clips:
        asset = {
            "asset_id": f"demo_proof_{uuid4().hex[:12]}",
            "asset_type": "hook",
            "clip_id": clip["clip_id"],
            "hook_text": clip["hook"],
            "caption_text": clip["caption"],
            "ai_score": clip["score"],
            "campaign_role": clip["campaign_role"],
            "is_demo": True,
            "saved_at": datetime.utcnow().isoformat() + "Z",
        }
        saved_assets.append(asset)
    
    return {
        "success": True,
        "user_id": user_id,
        "saved_assets": saved_assets,
        "count": len(saved_assets),
        "message": f"Saved {len(saved_assets)} demo clips to Proof Vault.",
    }


def get_demo_mode_status() -> Dict[str, Any]:
    """Get Demo Mode system status."""
    return {
        "success": True,
        "demo_mode_enabled": True,
        "sample_source_available": True,
        "sample_clips_count": len(SAMPLE_CLIPS),
        "features": [
            "sample_source",
            "sample_clips",
            "save_to_proof",
            "export_campaign",
            "view_posting_schedule",
        ],
        "limitations": [
            "No playable video (strategy-only)",
            "Demo watermark on exports",
            "Cannot upload to real platforms",
        ],
    }
