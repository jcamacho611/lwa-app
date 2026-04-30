from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .caption_presets import normalize_caption_preset
from .hook_formula_library import HOOK_FORMULAS
from .source_contract import normalize_source_type


@dataclass(frozen=True)
class AlgorithmInput:
    transcript: str
    target_platform: str = "tiktok"
    category: str | None = None
    source_type: str | None = None
    duration_seconds: int | None = None
    caption_preset: str | None = None


@dataclass(frozen=True)
class AlgorithmScore:
    overall: int
    components: dict[str, int]
    selected_hook_formula: str
    selected_caption_preset: str
    platform_goal: str
    recommended_duration: str
    rationale: str
    improvement_notes: list[str]
    safe_claim: bool


PLATFORM_GOALS: dict[str, tuple[str, str]] = {
    "tiktok": ("completion and replay", "7-60s"),
    "instagram_reels": ("shares and saves", "15-60s"),
    "reels": ("shares and saves", "15-60s"),
    "youtube_shorts": ("engaged views and rewatches", "15-60s"),
    "shorts": ("engaged views and rewatches", "15-60s"),
    "linkedin": ("dwell time and thoughtful comments", "30-90s"),
    "twitch_clips": ("clip velocity and context", "5-60s"),
    "whop_community": ("completion and member discussion", "30-90s"),
}

UNSAFE_CLAIM_TERMS: tuple[str, ...] = (
    "guaranteed viral",
    "guaranteed income",
    "guaranteed money",
    "risk-free income",
    "investment return",
    "roi guaranteed",
)

SPECIFICITY_HINTS: tuple[str, ...] = (
    "$",
    "%",
    "days",
    "hours",
    "minutes",
    "mistakes",
    "steps",
    "rules",
    "method",
    "framework",
)


def normalize_platform(platform: str | None) -> str:
    value = (platform or "tiktok").strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "ig": "instagram_reels",
        "instagram": "instagram_reels",
        "reels": "instagram_reels",
        "yt_shorts": "youtube_shorts",
        "youtube": "youtube_shorts",
        "shorts": "youtube_shorts",
        "x": "x_video",
        "twitter": "x_video",
        "twitch": "twitch_clips",
        "whop": "whop_community",
    }
    return aliases.get(value, value)


def words(text: str) -> list[str]:
    return [word for word in text.replace("\n", " ").split(" ") if word.strip()]


def clamp_score(value: int) -> int:
    return max(0, min(100, int(value)))


def score_hook_strength(text: str) -> int:
    tokens = words(text)
    if not tokens:
        return 20
    first_twelve = " ".join(tokens[:12]).lower()
    score = 45
    if len(tokens) >= 8:
        score += 10
    if any(mark in first_twelve for mark in ("stop", "why", "how", "mistake", "secret", "nobody", "before", "after")):
        score += 20
    if "?" in text[:120]:
        score += 10
    if any(char.isdigit() for char in text[:120]):
        score += 10
    return clamp_score(score)


def score_platform_fit(platform: str, source_type: str, duration_seconds: int | None) -> int:
    normalized = normalize_platform(platform)
    score = 65
    if normalized in PLATFORM_GOALS:
        score += 10
    if source_type in {"video_upload", "url", "video", "upload"}:
        score += 10
    if duration_seconds is not None:
        if normalized in {"tiktok", "instagram_reels", "youtube_shorts"} and 7 <= duration_seconds <= 90:
            score += 10
        elif normalized in {"linkedin", "whop_community"} and 20 <= duration_seconds <= 120:
            score += 10
        elif normalized == "twitch_clips" and 5 <= duration_seconds <= 60:
            score += 10
        else:
            score -= 10
    return clamp_score(score)


def score_captionability(text: str) -> int:
    tokens = words(text)
    if not tokens:
        return 20
    avg_word_length = sum(len(token) for token in tokens) / len(tokens)
    score = 55
    if 20 <= len(tokens) <= 180:
        score += 20
    if avg_word_length <= 8:
        score += 10
    if any(char in text for char in ".?!"):
        score += 10
    return clamp_score(score)


def score_specificity(text: str) -> int:
    lowered = text.lower()
    score = 45
    if any(char.isdigit() for char in text):
        score += 20
    if any(hint in lowered for hint in SPECIFICITY_HINTS):
        score += 15
    if any(token[:1].isupper() for token in words(text)[1:]):
        score += 10
    return clamp_score(score)


def score_safety(text: str) -> tuple[int, bool, list[str]]:
    lowered = text.lower()
    notes: list[str] = []
    safe = True
    score = 90
    for term in UNSAFE_CLAIM_TERMS:
        if term in lowered:
            safe = False
            score -= 25
            notes.append("Remove unsupported guarantee language.")
    return clamp_score(score), safe, notes


def select_hook_formula(text: str, category: str | None) -> str:
    lowered = text.lower()
    if any(char.isdigit() for char in text):
        return "specific_number"
    if "mistake" in lowered:
        return "numbered_list"
    if category and category.strip().lower() in {"education", "coaching"}:
        return "framework_name"
    if category and category.strip().lower() in {"debate", "commentary"}:
        return "contrarian_claim"
    return HOOK_FORMULAS[0].code


def build_improvement_notes(components: dict[str, int], safe_notes: list[str]) -> list[str]:
    notes = list(safe_notes)
    if components["hook_strength"] < 70:
        notes.append("Open with a stronger claim, question, or pattern interrupt.")
    if components["specificity"] < 65:
        notes.append("Add a concrete number, named method, or sharper example.")
    if components["captionability"] < 65:
        notes.append("Use shorter phrases so captions are easier to read.")
    if not notes:
        notes.append("Strong package. Lead with this clip first.")
    return notes


def score_clip_package(payload: AlgorithmInput) -> AlgorithmScore:
    text = payload.transcript.strip()
    platform = normalize_platform(payload.target_platform)
    source_type = normalize_source_type(payload.source_type or "unknown")
    platform_goal, recommended_duration = PLATFORM_GOALS.get(platform, ("short-form retention", "15-60s"))
    safety_score, safe_claim, safe_notes = score_safety(text)
    components = {
        "hook_strength": score_hook_strength(text),
        "platform_fit": score_platform_fit(platform, source_type, payload.duration_seconds),
        "captionability": score_captionability(text),
        "specificity": score_specificity(text),
        "safety": safety_score,
    }
    weighted = (
        components["hook_strength"] * 0.30
        + components["platform_fit"] * 0.25
        + components["captionability"] * 0.15
        + components["specificity"] * 0.15
        + components["safety"] * 0.15
    )
    selected_formula = select_hook_formula(text, payload.category)
    selected_preset = normalize_caption_preset(payload.caption_preset)
    return AlgorithmScore(
        overall=clamp_score(round(weighted)),
        components=components,
        selected_hook_formula=selected_formula,
        selected_caption_preset=selected_preset,
        platform_goal=platform_goal,
        recommended_duration=recommended_duration,
        rationale=f"Scored for {platform_goal} with a {selected_formula} hook and {selected_preset} captions.",
        improvement_notes=build_improvement_notes(components, safe_notes),
        safe_claim=safe_claim,
    )


def score_clip_package_dict(**kwargs: Any) -> dict[str, Any]:
    score = score_clip_package(AlgorithmInput(**kwargs))
    return {
        "overall": score.overall,
        "components": score.components,
        "selected_hook_formula": score.selected_hook_formula,
        "selected_caption_preset": score.selected_caption_preset,
        "platform_goal": score.platform_goal,
        "recommended_duration": score.recommended_duration,
        "rationale": score.rationale,
        "improvement_notes": score.improvement_notes,
        "safe_claim": score.safe_claim,
    }
