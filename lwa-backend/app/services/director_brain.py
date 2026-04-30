from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .caption_presets import normalize_caption_preset
from .hook_formula_library import HOOK_FORMULAS, HookFormula

ALGORITHM_VERSION = "director-brain-v0.2"

PLATFORM_PROFILES: dict[str, dict[str, Any]] = {
    "tiktok": {
        "goal": "completion, replay, and first-frame retention",
        "length": "15-45s",
        "hook_window_seconds": 2,
        "recommended_output_style": "fast pattern-interrupt short",
    },
    "instagram_reels": {
        "goal": "DM shares, saves, and muted watch retention",
        "length": "15-60s",
        "hook_window_seconds": 2,
        "recommended_output_style": "shareable clean-caption reel",
    },
    "reels": {
        "goal": "DM shares, saves, and muted watch retention",
        "length": "15-60s",
        "hook_window_seconds": 2,
        "recommended_output_style": "shareable clean-caption reel",
    },
    "youtube_shorts": {
        "goal": "engaged views, rewatches, and low swipe-away",
        "length": "20-60s",
        "hook_window_seconds": 1,
        "recommended_output_style": "tight payoff-first short",
    },
    "shorts": {
        "goal": "engaged views, rewatches, and low swipe-away",
        "length": "20-60s",
        "hook_window_seconds": 1,
        "recommended_output_style": "tight payoff-first short",
    },
    "linkedin": {
        "goal": "dwell time, comment depth, and saves",
        "length": "30-90s",
        "hook_window_seconds": 3,
        "recommended_output_style": "credible proof-led vertical clip",
    },
    "facebook_reels": {
        "goal": "watch time and shares",
        "length": "15-60s",
        "hook_window_seconds": 3,
        "recommended_output_style": "broad-share vertical clip",
    },
    "x": {
        "goal": "replies, reposts, and conversation pull",
        "length": "15-90s",
        "hook_window_seconds": 2,
        "recommended_output_style": "opinion-first conversation clip",
    },
    "twitter": {
        "goal": "replies, reposts, and conversation pull",
        "length": "15-90s",
        "hook_window_seconds": 2,
        "recommended_output_style": "opinion-first conversation clip",
    },
    "twitch": {
        "goal": "clip velocity, chat reaction, and replay value",
        "length": "7-45s",
        "hook_window_seconds": 3,
        "recommended_output_style": "reaction-first highlight clip",
    },
    "whop": {
        "goal": "community retention, comment depth, and paid-member value",
        "length": "30-120s",
        "hook_window_seconds": 3,
        "recommended_output_style": "community value clip",
    },
}

CATEGORY_FORMULA_MAP: dict[str, tuple[str, ...]] = {
    "finance": ("specific_number", "objection_first", "dataset_pattern"),
    "business": ("specific_number", "framework_name", "contrarian_claim"),
    "coaching": ("persona_callout", "objection_first", "framework_name"),
    "medspa": ("before_after", "persona_callout", "specific_number"),
    "beauty": ("before_after", "pattern_interrupt", "share_hook"),
    "gaming": ("pattern_interrupt", "dialogue_cold_open", "reverse_hook"),
    "podcast": ("contrarian_claim", "unexpected_admission", "dialogue_cold_open"),
    "tech": ("dataset_pattern", "framework_name", "pattern_interrupt"),
    "ai": ("dataset_pattern", "framework_name", "specific_number"),
}

RISK_TERMS = {
    "guaranteed": "Avoid guaranteed result language.",
    "cure": "Avoid medical cure claims.",
    "investment": "Avoid investment framing.",
    "passive income": "Avoid passive income promises.",
    "risk free": "Avoid risk-free claims.",
}


@dataclass(frozen=True)
class DirectorBrainInput:
    transcript: str
    target_platform: str = "tiktok"
    category: str | None = None
    caption_preset: str | None = None


@dataclass(frozen=True)
class DirectorBrainOutput:
    target_platform: str
    caption_preset: str
    hooks: list[str]
    captions: list[str]
    moments: list[dict[str, Any]]
    score: int
    rationale: str
    algorithm_version: str
    recommended_platform: str
    recommended_content_type: str
    recommended_output_style: str
    platform_recommendation_reason: str
    quality_gate_status: str
    quality_gate_warnings: list[str]
    hook_formula_codes: list[str]
    risk_penalty: int


def _normalize_platform(platform: str) -> str:
    normalized = platform.strip().lower().replace(" ", "_").replace("-", "_")
    return normalized or "tiktok"


def _words(text: str) -> list[str]:
    return [word for word in text.replace("\n", " ").split(" ") if word.strip()]


def _first_words(text: str, limit: int) -> str:
    words = _words(text)
    return " ".join(words[:limit]).strip() or "Your strongest moment starts here"


def _profile(platform: str) -> dict[str, Any]:
    return PLATFORM_PROFILES.get(_normalize_platform(platform), PLATFORM_PROFILES["tiktok"])


def _formula_by_code(code: str) -> HookFormula:
    for formula in HOOK_FORMULAS:
        if formula.code == code:
            return formula
    return HOOK_FORMULAS[0]


def _select_formulas(category: str | None, transcript: str) -> list[HookFormula]:
    normalized_category = (category or "").strip().lower().replace(" ", "_")
    codes = list(CATEGORY_FORMULA_MAP.get(normalized_category, ()))
    text = transcript.lower()
    if any(char.isdigit() for char in text):
        codes.append("specific_number")
    if "wrong" in text or "mistake" in text:
        codes.append("contrarian_claim")
    if not codes:
        codes = ["pattern_interrupt", "persona_callout", "framework_name"]
    unique_codes = []
    for code in codes:
        if code not in unique_codes:
            unique_codes.append(code)
    return [_formula_by_code(code) for code in unique_codes[:3]]


def _risk_warnings(text: str) -> list[str]:
    lower = text.lower()
    return [message for term, message in RISK_TERMS.items() if term in lower]


def _score(text: str, platform: str, warnings: list[str]) -> int:
    words = _words(text)
    base = 58
    base += min(len(words) // 12, 18)
    base += 6 if any(char.isdigit() for char in text) else 0
    base += 5 if "?" in text else 0
    base += 4 if _normalize_platform(platform) in PLATFORM_PROFILES else 0
    base -= min(len(warnings) * 8, 28)
    return max(35, min(96, base))


def _recommended_content_type(category: str | None, text: str) -> str:
    if category:
        return category.strip().replace("_", " ").title()
    lower = text.lower()
    if "mistake" in lower or "wrong" in lower:
        return "Contrarian commentary"
    if any(char.isdigit() for char in text):
        return "Number-led breakdown"
    if "how" in lower or "why" in lower:
        return "Educational explainer"
    return "Short-form highlight"


def _build_hooks(seed: str, formulas: list[HookFormula]) -> list[str]:
    hooks = [seed]
    for formula in formulas:
        if formula.code == "contrarian_claim":
            hooks.append(f"Stop doing this: {seed}")
        elif formula.code == "persona_callout":
            hooks.append(f"If you make content, this is for you: {seed}")
        elif formula.code == "specific_number":
            hooks.append(f"3 reasons this moment works: {seed}")
        elif formula.code == "framework_name":
            hooks.append(f"The LWA clip test starts here: {seed}")
        elif formula.code == "before_after":
            hooks.append(f"Before you post, watch this: {seed}")
        else:
            hooks.append(f"The key moment: {seed}")
    seen: list[str] = []
    for hook in hooks:
        if hook and hook not in seen:
            seen.append(hook[:140])
    return seen[:4]


def build_director_brain_output(payload: DirectorBrainInput) -> DirectorBrainOutput:
    text = payload.transcript.strip()
    platform = _normalize_platform(payload.target_platform or "tiktok")
    profile = _profile(platform)
    caption_preset = normalize_caption_preset(payload.caption_preset)
    formulas = _select_formulas(payload.category, text)
    hook_seed = _first_words(text, 9)
    hooks = _build_hooks(hook_seed, formulas)
    caption_text = text[:180].strip() or hook_seed
    warnings = _risk_warnings(text)
    score = _score(text, platform, warnings)
    content_type = _recommended_content_type(payload.category, text)
    moments = [
        {
            "start": 0,
            "end": 30,
            "reason": f"Opening segment optimized for {profile['goal']}",
            "hook_formula": formulas[0].code,
            "platform_fit_score": score,
            "recommended_length": profile["length"],
            "hook_window_seconds": profile["hook_window_seconds"],
        }
    ]
    quality_gate_status = "warning" if warnings else "pass"
    return DirectorBrainOutput(
        target_platform=platform,
        caption_preset=caption_preset,
        hooks=hooks,
        captions=[caption_text],
        moments=moments,
        score=score,
        rationale=f"Director Brain selected a short-form opening for {profile['goal']}.",
        algorithm_version=ALGORITHM_VERSION,
        recommended_platform=platform,
        recommended_content_type=content_type,
        recommended_output_style=str(profile["recommended_output_style"]),
        platform_recommendation_reason=f"{platform} prioritizes {profile['goal']} with a {profile['hook_window_seconds']}s hook window.",
        quality_gate_status=quality_gate_status,
        quality_gate_warnings=warnings,
        hook_formula_codes=[formula.code for formula in formulas],
        risk_penalty=min(len(warnings) * 8, 28),
    )


def director_brain_package(
    *,
    transcript: str,
    target_platform: str = "tiktok",
    category: str | None = None,
    caption_preset: str | None = None,
) -> dict[str, Any]:
    output = build_director_brain_output(
        DirectorBrainInput(
            transcript=transcript,
            target_platform=target_platform,
            category=category,
            caption_preset=caption_preset,
        )
    )
    return {
        "target_platform": output.target_platform,
        "caption_preset": output.caption_preset,
        "hooks": output.hooks,
        "captions": output.captions,
        "moments": output.moments,
        "score": output.score,
        "rationale": output.rationale,
        "algorithm_version": output.algorithm_version,
        "recommended_platform": output.recommended_platform,
        "recommended_content_type": output.recommended_content_type,
        "recommended_output_style": output.recommended_output_style,
        "platform_recommendation_reason": output.platform_recommendation_reason,
        "quality_gate_status": output.quality_gate_status,
        "quality_gate_warnings": output.quality_gate_warnings,
        "hook_formula_codes": output.hook_formula_codes,
        "risk_penalty": output.risk_penalty,
    }
