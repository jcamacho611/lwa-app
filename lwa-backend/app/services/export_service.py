def build_download_url(clip: dict) -> str:
    """
    Build the download URL for a clip.
    Prefers edited_clip_url > preview_url.
    """
    return clip.get("edited_clip_url") or clip.get("preview_url") or ""