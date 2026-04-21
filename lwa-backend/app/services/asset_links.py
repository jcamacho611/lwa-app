def normalize_assets(clip: dict) -> dict:
    """
    Normalize asset URLs on a clip.
    Ensures preview_url and download_url are always set if possible.
    """
    # Set preview_url as fallback chain
    clip["preview_url"] = (
        clip.get("preview_url")
        or clip.get("edited_clip_url")
        or clip.get("clip_url")
    )

    # Set download_url as fallback chain
    clip["download_url"] = (
        clip.get("download_url")
        or clip.get("edited_clip_url")
        or clip.get("preview_url")
    )

    return clip