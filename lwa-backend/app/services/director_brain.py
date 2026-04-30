from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .caption_presets import normalize_caption_preset
from .hook_formula_library import HOOK_FORMULAS


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


def _words(text: str) -> list[str]:
    return [word for word in text.replace("\n", " ").split(" ") if word.strip()]


def _first_words(text: str, limit: int) -> str:
    words = _words(text)
    return " ".join(words[:limit]).strip() or "Your strongest moment starts here"


def _platform_goal(platform: str) -> str:
    normalized = platform.strip().lower().replace(" ", "_").replace("-", "_")
    goals = {
        "tiktok": "completion and replay",
        "instagram_reels": "sharing and saves",
        "reels": "sharing and saves",
        "youtube_shorts": "engaged views and rewatches",
        "shorts": "engaged views and rewatches",
        "linkedin": "dwell time and comments",
        "twitch": "clip velocity",
    }
    return goals.get(normalized, "short-form retention")


def build_director_brain_output(payload: DirectorBrainInput) -> DirectorBrainOutput:
    text = payload.transcript.strip()
    platform = payload.target_platform or "tiktok"
    caption_preset = normalize_caption_preset(payload.caption_preset)
    hook_seed = _first_words(text, 9)
    hooks = [
        hook_seed,
        f"Stop scrolling — {hook_seed}",
        f"The key moment: {hook_seed}",
    ]
    caption_text = text[:180].strip() or hook_seed
    captions = [caption_text]
    moments = [
        {
            "start": 0,
            "end": 30,
            "reason": f"Opening segment optimized for {_platform_goal(platform)}",
            "hook_formula": HOOK_FORMULAS[0].code,
        }
    ]
    score = min(95, max(55, 65 + len(_words(text)) // 20))
    return DirectorBrainOutput(
        target_platform=platform,
        caption_preset=caption_preset,
        hooks=hooks,
        captions=captions,
        moments=moments,
        score=score,
        rationale=f"Director Brain v0 selected a short-form opening for {_platform_goal(platform)}.",
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
    }
