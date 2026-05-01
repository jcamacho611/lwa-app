from __future__ import annotations

import json
from typing import Any

from ..core.config import Settings
from .ai_cost_control import check_ai_limits, record_ai_usage

try:
    from anthropic import Anthropic
except Exception:  # pragma: no cover - runtime dependency guard
    Anthropic = None  # type: ignore[assignment]


DEFAULT_SYSTEM_PROMPT = """
You are the LWA premium clip intelligence engine.

Return concise, creator-native, packaging-first output that stays grounded in the supplied source context.
Always follow the requested JSON shape exactly.
""".strip()


def anthropic_available(settings: Settings) -> bool:
    return bool(settings.enable_anthropic and settings.anthropic_api_key and Anthropic is not None)


def generate_clip_packaging_with_sonnet(
    *,
    settings: Settings,
    user_id: str,
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_tokens: int = 2400,
) -> str:
    return _generate_text(
        settings=settings,
        user_id=user_id,
        model=settings.anthropic_model_sonnet,
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        operation="clip_packaging",
    )


def generate_clip_packaging_with_opus(
    *,
    settings: Settings,
    user_id: str,
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_tokens: int = 2800,
) -> str:
    return _generate_text(
        settings=settings,
        user_id=user_id,
        model=settings.anthropic_model_opus,
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        operation="clip_packaging",
    )


def classify_clip_metadata_with_haiku(
    *,
    settings: Settings,
    user_id: str,
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    max_tokens: int = 1200,
) -> dict[str, Any]:
    raw = _generate_text(
        settings=settings,
        user_id=user_id,
        model=settings.anthropic_model_haiku,
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        operation="classify_metadata",
    )
    try:
        return json.loads(raw)
    except Exception:
        return {"raw": raw.strip()}


def select_anthropic_model(settings: Settings, *, premium_reasoning: bool) -> str:
    return settings.anthropic_model_opus if premium_reasoning else settings.anthropic_model_sonnet


def _generate_text(
    *,
    settings: Settings,
    user_id: str,
    model: str,
    prompt: str,
    system_prompt: str,
    max_tokens: int,
    operation: str,
) -> str:
    if not anthropic_available(settings):
        raise RuntimeError("Anthropic is not available. Set LWA_ENABLE_ANTHROPIC=true and ANTHROPIC_API_KEY.")

    # Check AI limits before making request
    if not check_ai_limits(settings, user_id, model, max_tokens):
        raise RuntimeError(f"AI request limit exceeded for user {user_id} with model {model}.")

    client = Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model=model,
        system=system_prompt,
        max_tokens=max_tokens,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    
    # Extract usage information
    tokens_used = 0
    if hasattr(response, 'usage'):
        tokens_used = getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0)
    else:
        # Fallback: estimate tokens based on max_tokens
        tokens_used = max_tokens
    
    # Record usage for cost tracking
    record_ai_usage(settings, user_id, operation, model, tokens_used)
    
    text_parts: list[str] = []
    for item in response.content:
        text = getattr(item, "text", None)
        if text:
            text_parts.append(text)
    combined = "\n".join(part.strip() for part in text_parts if part and part.strip()).strip()
    if not combined:
        raise RuntimeError(f"Anthropic returned no text for model={model}.")
    return combined
