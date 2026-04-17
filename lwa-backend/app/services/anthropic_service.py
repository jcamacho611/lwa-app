"""Anthropic (Claude) provider for LWA clip intelligence.

Supports Sonnet (default production), Opus (premium reasoning), and
Haiku (lightweight tagging). Falls back gracefully when the anthropic
SDK is not installed or the API key is empty.
"""
from __future__ import annotations

import json
import logging
from typing import List, Optional

from ..core.config import Settings
from ..models.schemas import ClipResult, TrendItem
from ..processor import SourceContext

logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# Lazy SDK loader — keeps the import optional so the rest of the backend
# works even if `anthropic` is not installed.
# ---------------------------------------------------------------------------
_anthropic_module = None  # None = not checked yet, False = unavailable


def _load_sdk():
    global _anthropic_module
    if _anthropic_module is None:
        try:
            import anthropic as _sdk  # type: ignore[import-untyped]
            _anthropic_module = _sdk
        except ImportError:
            _anthropic_module = False
    return _anthropic_module if _anthropic_module is not False else None


def anthropic_available(settings: Settings) -> bool:
    """True when the SDK is installed, the key is set, and the feature is enabled."""
    if not settings.enable_anthropic:
        return False
    if not settings.anthropic_api_key:
        return False
    return _load_sdk() is not None


# ---------------------------------------------------------------------------
# Core generation entry point
# ---------------------------------------------------------------------------

async def generate_with_anthropic(
    *,
    settings: Settings,
    prompt: str,
    tier: str = "sonnet",
) -> str:
    """Send *prompt* to Claude and return the raw text response.

    *tier* controls model selection:
      - ``"sonnet"`` — default production intelligence
      - ``"opus"``   — premium / high-depth reasoning
      - ``"haiku"``  — lightweight cleanup / tagging

    Raises on any failure so the caller can fall through to the next provider.
    """
    sdk = _load_sdk()
    if sdk is None:
        raise RuntimeError("anthropic SDK is not installed")
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    model = _resolve_model(settings, tier)
    client = sdk.Anthropic(api_key=settings.anthropic_api_key)

    logger.info(
        "anthropic_request tier=%s model=%s prompt_chars=%s",
        tier, model, len(prompt),
    )

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    text_parts: list[str] = []
    for block in message.content:
        if hasattr(block, "text"):
            text_parts.append(block.text)
    raw = "\n".join(text_parts).strip()

    logger.info("anthropic_response tier=%s model=%s chars=%s", tier, model, len(raw))
    return raw


# ---------------------------------------------------------------------------
# Attention compiler entry point — uses the same Claude call but with
# the attention-compiler prompt instead of the generation prompt.
# ---------------------------------------------------------------------------

async def compile_attention_with_anthropic(
    *,
    settings: Settings,
    prompt: str,
    premium: bool = False,
) -> str:
    """Run the attention-compiler prompt through Claude.

    When *premium* is True, uses Opus for deeper analysis.
    """
    tier = "opus" if premium else "sonnet"
    return await generate_with_anthropic(
        settings=settings,
        prompt=prompt,
        tier=tier,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resolve_model(settings: Settings, tier: str) -> str:
    if tier == "opus":
        return settings.anthropic_model_opus
    if tier == "haiku":
        return settings.anthropic_model_haiku
    return settings.anthropic_model_sonnet


def resolve_anthropic_tier_for_plan(settings: Settings, plan_code: str) -> str:
    """Map a plan code to the appropriate Claude tier.

    Uses Opus for premium plans when the premium reasoning provider is anthropic.
    """
    if settings.premium_reasoning_provider != "anthropic":
        return "sonnet"
    premium_codes = {"pro", "scale", "enterprise"}
    if plan_code.lower() in premium_codes:
        return "opus"
    return "sonnet"
