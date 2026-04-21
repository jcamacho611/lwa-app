def render_clip(clip: dict) -> dict:
    """
    Stub render layer — replace with ffmpeg pipeline later.
    Ensures edited_clip_url is set if preview_url exists.
    """
    # simulate rendered output
    clip["edited_clip_url"] = clip.get("edited_clip_url") or clip.get("preview_url")

    return clip