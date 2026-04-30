from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserActionSignal:
    action: str
    weight: int
    meaning: str


USER_ACTION_SIGNALS: dict[str, UserActionSignal] = {
    "play_clip": UserActionSignal("play_clip", 5, "clip earned attention"),
    "download_clip": UserActionSignal("download_clip", 20, "clip was useful"),
    "copy_hook": UserActionSignal("copy_hook", 12, "hook packaging was useful"),
    "copy_caption": UserActionSignal("copy_caption", 10, "caption packaging was useful"),
    "reject_clip": UserActionSignal("reject_clip", -20, "recommendation missed"),
    "regenerate": UserActionSignal("regenerate", -12, "output missed expectation"),
    "external_post": UserActionSignal("external_post", 25, "clip was high value"),
    "repeat_source_type": UserActionSignal("repeat_source_type", 8, "source workflow is working"),
}


def normalize_action(action: str | None) -> str:
    return (action or "").strip().lower().replace(" ", "_").replace("-", "_")


def score_user_action(action: str | None) -> dict[str, object]:
    normalized = normalize_action(action)
    signal = USER_ACTION_SIGNALS.get(normalized)
    if not signal:
        return {"action": normalized or "unknown", "weight": 0, "meaning": "unknown or neutral action"}
    return signal.__dict__.copy()


def aggregate_learning_score(actions: list[str]) -> dict[str, object]:
    scored = [score_user_action(action) for action in actions]
    total = sum(int(item["weight"]) for item in scored)
    if total > 25:
        interpretation = "strong_positive"
    elif total > 0:
        interpretation = "positive"
    elif total < 0:
        interpretation = "negative"
    else:
        interpretation = "neutral"
    return {
        "learning_score": total,
        "interpretation": interpretation,
        "signals": scored,
    }
