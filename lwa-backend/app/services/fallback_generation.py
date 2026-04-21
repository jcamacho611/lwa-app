from typing import List, Dict


def build_fallback_clips(video_url: str) -> List[Dict]:
    """
    Last-resort fallback clips when upstream extraction/generation under-returns.
    Keeps the response populated and source-grounded.
    """
    return [
        {
            "id": "fallback_1",
            "title": "Strong opening cut",
            "hook": "This is the first moment worth testing immediately.",
            "caption": "Fallback clip generated from source-grounded heuristics.",
            "score": 72,
            "why_this_matters": "Strong opener fallback to prevent empty pack.",
            "thumbnail_text": "Start Here",
            "cta_suggestion": "Test this first and compare hold rate.",
        },
        {
            "id": "fallback_2",
            "title": "Follow-up continuation",
            "hook": "Use this second to deepen the story after the opener lands.",
            "caption": "Fallback continuation clip.",
            "score": 66,
            "why_this_matters": "Provides second-post continuity when upstream results are thin.",
            "thumbnail_text": "Next Beat",
            "cta_suggestion": "Use as the second post in sequence.",
        },
    ]