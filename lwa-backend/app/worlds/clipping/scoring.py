from __future__ import annotations

import re


def score_text_signal(text: str) -> dict[str, int]:
    lowered = text.lower()
    emotional_words = [
        "love",
        "hate",
        "fear",
        "angry",
        "shocked",
        "crazy",
        "insane",
        "mistake",
        "secret",
        "truth",
        "money",
        "fail",
        "win",
        "lost",
    ]
    hook_words = [
        "most people",
        "nobody",
        "everyone",
        "first",
        "biggest",
        "mistake",
        "secret",
        "truth",
        "never",
        "always",
        "why",
    ]

    clarity = min(100, max(20, 100 - len(text.split()) // 4))
    emotion = min(100, sum(12 for word in emotional_words if word in lowered))
    hook = min(100, sum(14 for phrase in hook_words if phrase in lowered))
    question_bonus = 15 if "?" in text else 0
    number_bonus = 10 if re.search(r"\d", text) else 0
    retention = min(100, hook + emotion // 2 + question_bonus + number_bonus)
    shareability = min(100, hook // 2 + emotion + number_bonus)
    platform_fit = min(100, 70 + hook // 5)
    total = round(
        (hook * 0.22)
        + (retention * 0.22)
        + (clarity * 0.18)
        + (emotion * 0.14)
        + (shareability * 0.14)
        + (platform_fit * 0.10)
    )
    return {
        "score_total": max(0, min(100, total)),
        "score_hook": hook,
        "score_retention": retention,
        "score_clarity": clarity,
        "score_emotion": emotion,
        "score_shareability": shareability,
        "score_platform_fit": platform_fit,
    }


def classify_moment(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["mistake", "wrong", "fail", "lost"]):
        return "mistake_or_failure"
    if any(word in lowered for word in ["secret", "truth", "nobody", "hidden"]):
        return "reveal"
    if "?" in text:
        return "question"
    if any(word in lowered for word in ["money", "revenue", "sales", "profit"]):
        return "money"
    return "insight"
