from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class StyleProfile:
    hook_style: str
    sentence_length: str
    pacing: str
    tone: str
    cta_style: str
    slang_level: str
    structure_pattern: str


def extract_style(source_text: str) -> StyleProfile:
    text = normalize_text(source_text)
    sentences = split_sentences(text)
    average_words = sum(len(sentence.split()) for sentence in sentences) / max(len(sentences), 1)
    lower = text.lower()

    hook_style = "curiosity"
    if any(word in lower for word in ["wrong", "mistake", "nobody", "never"]):
        hook_style = "contrarian"
    elif any(word in lower for word in ["stop", "wild", "crazy", "secret"]):
        hook_style = "interrupt"
    elif "?" in text:
        hook_style = "question"

    sentence_length = "short" if average_words <= 9 else "medium" if average_words <= 16 else "long"
    pacing = "fast" if average_words <= 12 or len(sentences) >= 4 else "steady"
    tone = "direct"
    if any(word in lower for word in ["money", "growth", "learn", "how"]):
        tone = "operator"
    elif any(word in lower for word in ["feel", "love", "hate", "afraid"]):
        tone = "emotional"
    elif any(word in lower for word in ["wrong", "debate", "agree"]):
        tone = "tension-led"

    cta_style = "comment"
    if any(word in lower for word in ["part", "next", "series"]):
        cta_style = "part-two"
    elif any(word in lower for word in ["save", "send", "share"]):
        cta_style = "save-share"

    slang_level = "low"
    if any(word in lower for word in ["bro", "insane", "wild", "crazy", "lowkey"]):
        slang_level = "medium"

    structure_pattern = "hook-payoff-cta"
    if hook_style == "question":
        structure_pattern = "question-answer-cta"
    elif tone == "operator":
        structure_pattern = "claim-proof-action"

    return StyleProfile(
        hook_style=hook_style,
        sentence_length=sentence_length,
        pacing=pacing,
        tone=tone,
        cta_style=cta_style,
        slang_level=slang_level,
        structure_pattern=structure_pattern,
    )


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def split_sentences(value: str) -> list[str]:
    parts = [part.strip() for part in re.split(r"(?<=[.!?])\s+", normalize_text(value)) if part.strip()]
    return parts or ([normalize_text(value)] if normalize_text(value) else [])
