"""
BrainEngine — Provider routing, style selection, confidence reasoning.

Status: LOCAL_READY
Safety: No external provider calls. Routing decisions are deterministic.
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

_PROVIDER_ROUTES = {
    "video": "seedance",
    "audio": "whisper_local",
    "text": "deterministic_heuristic",
    "image": "stable_diffusion_local",
}

_STYLE_MAP = {
    "gaming": "hype",
    "education": "educational",
    "vlog": "conversational",
    "product": "punchy",
    "default": "storytelling",
}


class BrainEngine(LwaEngine):
    """
    Routes requests to the appropriate provider, selects style, and
    produces confidence-scored reasoning. All logic is local and deterministic.
    """

    @property
    def engine_id(self) -> str:
        return "brain"

    @property
    def display_name(self) -> str:
        return "Brain Engine"

    @property
    def description(self) -> str:
        return "Provider routing, style selection, and confidence reasoning for content decisions."

    @property
    def status(self) -> EngineStatus:
        return EngineStatus.LOCAL_READY

    def capabilities(self) -> list[EngineCapability]:
        return [
            EngineCapability(
                name="provider_routing",
                description="Select the best provider for a given content type",
                local_safe=True,
            ),
            EngineCapability(
                name="style_selection",
                description="Choose the optimal content style based on category",
                local_safe=True,
            ),
            EngineCapability(
                name="confidence_reasoning",
                description="Produce a confidence score and reasoning chain",
                local_safe=True,
            ),
        ]

    def demo_run(self, payload: dict[str, Any]) -> EngineDemoResult:
        p = safe_payload(payload)
        content_type = text_value(p, "content_type", "video")
        category = text_value(p, "category", "default")
        quality_hint = number_value(p, "quality_hint", 0.8)

        route = _PROVIDER_ROUTES.get(content_type, "deterministic_heuristic")
        style = _STYLE_MAP.get(category, _STYLE_MAP["default"])
        confidence = round(min(0.95, max(0.5, quality_hint * 0.9 + 0.1)), 3)

        reasoning = [
            f"Content type '{content_type}' maps to provider '{route}'",
            f"Category '{category}' maps to style '{style}'",
            f"Quality hint {quality_hint} yields confidence {confidence}",
            "No external provider call required at LOCAL_READY status",
        ]

        return EngineDemoResult(
            engine_id=self.engine_id,
            status=self.status,
            summary=f"Routed '{content_type}' to '{route}' with {confidence:.0%} confidence",
            input_echo=p,
            output={
                "recommended_route": route,
                "style": style,
                "confidence": confidence,
                "reasoning": reasoning,
                "provider_available": False,
                "fallback_safe": True,
            },
            warnings=["Provider not connected — using deterministic fallback"],
            next_required_integrations=self.next_required_integrations(),
        )

    def next_required_integrations(self) -> list[str]:
        return [
            "Provider registry (live provider health checks)",
            "Style memory store (per-creator style history)",
            "ML confidence model (replaces heuristic scoring)",
        ]

    def health_warnings(self) -> list[str]:
        return ["No live provider connected — routing is deterministic only"]
