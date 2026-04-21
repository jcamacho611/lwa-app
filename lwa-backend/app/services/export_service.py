from __future__ import annotations

from typing import Any

from .export_bundle import create_export_bundle


def build_download_url(clip: dict[str, Any]) -> str:
    """Build the best direct download URL for a clip."""
    return (
        clip.get("download_url")
        or clip.get("edited_clip_url")
        or clip.get("preview_url")
        or clip.get("clip_url")
        or clip.get("raw_clip_url")
        or ""
    )


__all__ = ["build_download_url", "create_export_bundle"]
