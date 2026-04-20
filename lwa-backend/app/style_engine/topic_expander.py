from __future__ import annotations

import re


def expand_topics(*, source_title: str | None, transcript: str | None, clip_phrases: list[str]) -> dict[str, list[str]]:
    base = " ".join(part for part in [source_title or "", transcript or "", " ".join(clip_phrases)] if part).lower()
    keywords = extract_keywords(base)
    focus = keywords[0] if keywords else "this idea"

    return {
        "adjacent_topics": [
            f"{focus} mistakes",
            f"{focus} lessons",
            f"{focus} breakdown",
        ],
        "stronger_angles": [
            f"the part people miss about {focus}",
            f"why {focus} changes the outcome",
            f"the fastest way to explain {focus}",
        ],
        "emotional_variants": [
            f"what makes {focus} frustrating",
            f"why {focus} gets people to argue",
            f"the surprising side of {focus}",
        ],
        "skill_levels": [
            f"{focus} for beginners",
            f"{focus} for advanced creators",
        ],
    }


def extract_keywords(value: str) -> list[str]:
    stop_words = {
        "about",
        "after",
        "because",
        "before",
        "their",
        "there",
        "these",
        "thing",
        "this",
        "those",
        "video",
        "where",
        "which",
        "would",
        "you",
        "your",
    }
    candidates = [
        token
        for token in re.findall(r"[a-z0-9']+", value.lower())
        if len(token) > 4 and token not in stop_words
    ]
    ranked = sorted(set(candidates), key=lambda token: (-candidates.count(token), candidates.index(token)))
    return ranked[:6]
