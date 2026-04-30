from __future__ import annotations

from dataclasses import dataclass

from .caption_presets import normalize_caption_preset


@dataclass(frozen=True)
class CaptionStyleRecommendation:
    caption_style: str
    emphasis_words: list[str]
    safe_area: str
    burned_in_ready: bool
    reason: str


EMPHASIS_TERMS: tuple[str, ...] = (
    "mistake",
    "secret",
    "method",
    "framework",
    "money",
    "clip",
    "post",
    "attention",
    "source",
    "campaign",
)


def find_emphasis_words(text: str, limit: int = 5) -> list[str]:
    lowered_words = [word.strip(".,!?;:()[]{}\"'").lower() for word in text.split()]
    matches: list[str] = []
    for word in lowered_words:
        if word in EMPHASIS_TERMS and word not in matches:
            matches.append(word)
    return matches[:limit]


def recommend_caption_style(*, transcript: str, category: str | None = None, preferred_style: str | None = None) -> CaptionStyleRecommendation:
    category_key = (category or "").strip().lower().replace(" ", "_").replace("-", "_")
    if preferred_style:
        style = normalize_caption_preset(preferred_style)
    elif category_key in {"music", "gaming", "entertainment"}:
        style = "karaoke_neon"
    elif category_key in {"podcast", "interview"}:
        style = "signal_low"
    elif category_key in {"ai_tech", "product_demo", "developer"}:
        style = "dev_brutal"
    elif category_key in {"personal_brand", "motivation"}:
        style = "bigframe"
    else:
        style = "clean_op"

    return CaptionStyleRecommendation(
        caption_style=style,
        emphasis_words=find_emphasis_words(transcript),
        safe_area="bottom_third" if style == "signal_low" else "center_lower",
        burned_in_ready=bool(transcript.strip()),
        reason="Caption style selected from category and transcript emphasis.",
    )


def caption_style_dict(**kwargs: object) -> dict[str, object]:
    result = recommend_caption_style(
        transcript=str(kwargs.get("transcript") or ""),
        category=str(kwargs.get("category") or "") if kwargs.get("category") is not None else None,
        preferred_style=str(kwargs.get("preferred_style") or "") if kwargs.get("preferred_style") is not None else None,
    )
    return result.__dict__.copy()
