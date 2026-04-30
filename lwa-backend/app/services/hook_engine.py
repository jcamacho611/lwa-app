from __future__ import annotations

from dataclasses import dataclass

from .hook_formula_library import get_hook_formula


@dataclass(frozen=True)
class HookEngineResult:
    primary_hook: str
    variants: list[str]
    formula_code: str
    reason: str


def first_words(text: str, limit: int = 9) -> str:
    tokens = [word for word in text.replace("\n", " ").split(" ") if word.strip()]
    return " ".join(tokens[:limit]).strip() or "Your strongest clip starts here"


def select_formula_code(*, transcript: str, category: str | None = None) -> str:
    lowered = transcript.lower()
    if any(char.isdigit() for char in transcript):
        return "specific_number"
    if "mistake" in lowered or "mistakes" in lowered:
        return "numbered_list"
    if "before" in lowered and "after" in lowered:
        return "before_after"
    if "framework" in lowered or "method" in lowered:
        return "framework_name"
    if category and category.lower() in {"debate", "commentary"}:
        return "contrarian_claim"
    if category and category.lower() in {"education", "coaching"}:
        return "framework_name"
    return "contrarian_claim"


def build_hook_variants(*, transcript: str, category: str | None = None, max_variants: int = 3) -> HookEngineResult:
    seed = first_words(transcript)
    formula_code = select_formula_code(transcript=transcript, category=category)
    formula = get_hook_formula(formula_code)
    variants = [
        seed,
        f"Stop scrolling — {seed}",
        f"The clip starts here: {seed}",
        f"Watch this before you post: {seed}",
    ][: max(1, max_variants)]
    return HookEngineResult(
        primary_hook=variants[0],
        variants=variants,
        formula_code=formula_code,
        reason=(formula.name if formula else "Default formula"),
    )
