def infer_platform_fit(title: str = "", hook: str = "", duration_seconds: float = 30.0) -> str:
    """
    Infer the best platform for a clip based on title, hook, and duration.
    """
    text = f"{title} {hook}".lower()

    # High-engagement viral words suggest TikTok/Reels
    if any(word in text for word in ["stop", "crazy", "nobody", "wrong", "secret", "never", "mistake"]):
        return "TikTok / Reels"

    # Longer content suits YouTube Shorts
    if duration_seconds > 35:
        return "YouTube Shorts"

    # Educational/explanatory content works on Shorts/Reels
    if any(word in text for word in ["story", "explained", "breakdown", "how", "why"]):
        return "YouTube Shorts / Reels"

    return "Short-form multi-platform"