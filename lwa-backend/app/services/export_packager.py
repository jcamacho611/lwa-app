from typing import Dict


def build_export_package(clip: Dict) -> Dict:
    """
    Build an export-ready package for a clip.
    """
    return {
        "title": clip.get("title"),
        "hook": clip.get("hook"),
        "caption": clip.get("caption"),
        "thumbnail_text": clip.get("thumbnail_text"),
        "cta": clip.get("cta_suggestion"),
        "platform_fit": clip.get("platform_fit"),
        "post_rank": clip.get("post_rank"),
    }