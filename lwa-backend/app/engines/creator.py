"""
CreatorEngine — Hook generation, caption packaging, clip prioritization.

Status: LOCAL_READY
Safety: No external provider calls, no payments, no social posting.
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
)

_HOOK_TEMPLATES = [
    "You won't believe what happened when {topic} went viral",
    "The {topic} strategy nobody is talking about",
    "Stop making this mistake with {topic}",
    "How {topic} changed everything in 60 seconds",
    "The truth about {topic} that creators hide",
]

_CAPTION_STYLES = ["punchy", "storytelling", "educational", "hype", "conversational"]


class CreatorEngine(LwaEngine):
    """
    Generates hooks, packages captions, and prioritises clips for a creator.
    All logic is deterministic and local — no AI provider required.
    """

    @property
    def engine_id(self) -> str:
        return "creator"

    @property
    def display_name(self) -> str:
        return "Creator Engine"

    @property
    def description(self) -> str:
        return "Hook generation, caption packaging, and clip prioritization for creators."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="hook_generation",
                description="Generate viral hook variants for a topic",
                local_safe=True,
            ),
            EngineCapability(
                name="caption_packaging",
                description="Package captions with style and platform metadata",
                local_safe=True,
            ),
            EngineCapability(
                name="clip_prioritization",
                description="Score and rank clips by estimated virality",
                local_safe=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        topic = text_value(p, "topic", "your content")
        platform = text_value(p, "platform", "tiktok")

        hooks = [t.format(topic=topic) for t in _HOOK_TEMPLATES]
        captions = [
            {
                "style": style,
                "text": f"[{style.upper()}] {hooks[0]} #{topic.replace(' ', '')}",
                "platform": platform,
                "char_count": len(hooks[0]) + 20,
            }
            for style in _CAPTION_STYLES[:3]
        ]
        scores = [
            {"hook": h, "score": round(85 - i * 4, 1), "rank": i + 1}
            for i, h in enumerate(hooks)
        ]

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Generated {len(hooks)} hooks and {len(captions)} captions for topic '{topic}'",
            input_echo=p,
            output={
                "hooks": hooks,
                "captions": captions,
                "scores": scores,
                "export_ready": True,
                "platform": platform,
            },
            warnings=[],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "AI provider (OpenAI/Anthropic) for dynamic hook personalisation",
            "User profile store for creator style memory",
        ]

    def health_warnings(self) -> list[str]:
        return []
