from typing import List, Optional

from .schemas import ClipResult, TrendItem


def build_mock_clips(
    video_url: str,
    target_platform: str = "TikTok",
    selected_trend: Optional[str] = None,
    trend_context: Optional[List[TrendItem]] = None,
    clip_urls: Optional[List[str]] = None,
    start_end_pairs: Optional[List[tuple[str, str]]] = None,
    source_title: Optional[str] = None,
    transcript_excerpts: Optional[List[Optional[str]]] = None,
) -> List[ClipResult]:
    source_label = video_url.split("//")[-1].split("/")[0]
    lead_trend = selected_trend or (trend_context[0].title if trend_context else "creator growth")
    platform_label = target_platform or "TikTok"
    title_prefix = source_title or platform_label
    clip_urls = normalize_clip_urls(clip_urls)
    start_end_pairs = normalize_start_end_pairs(start_end_pairs)
    transcript_excerpts = normalize_transcript_excerpts(transcript_excerpts)

    return [
        ClipResult(
            id="clip_001",
            title=f"{title_prefix} Trend Hook",
            hook=f"Stop scrolling if you want to use {lead_trend} before everyone else does.",
            caption=(
                f"Pulled from {source_label}: lead with the trend angle first, show proof fast, "
                f"and make the payoff clear for {platform_label} viewers."
            ),
            start_time=start_end_pairs[0][0],
            end_time=start_end_pairs[0][1],
            score=92,
            format="Hook First",
            clip_url=clip_urls[0],
            raw_clip_url=clip_urls[0],
            transcript_excerpt=transcript_excerpts[0],
            edit_profile="Source cut preview" if clip_urls[0] else None,
            aspect_ratio="source" if clip_urls[0] else None,
        ),
        ClipResult(
            id="clip_002",
            title="Contrarian Take",
            hook=f"Most creators will chase {lead_trend} the wrong way and still miss the moment.",
            caption=(
                "This cut turns one strong opinion into a punchy short: one sharp claim, one "
                "example, one takeaway, no wasted setup."
            ),
            start_time=start_end_pairs[1][0],
            end_time=start_end_pairs[1][1],
            score=88,
            format="Opinion",
            clip_url=clip_urls[1],
            raw_clip_url=clip_urls[1],
            transcript_excerpt=transcript_excerpts[1],
            edit_profile="Source cut preview" if clip_urls[1] else None,
            aspect_ratio="source" if clip_urls[1] else None,
        ),
        ClipResult(
            id="clip_003",
            title="Story-Based CTA",
            hook=f"Here is the exact moment the {lead_trend} angle actually started converting.",
            caption=(
                f"Use this clip as the payoff moment, then close with a platform-specific CTA for "
                f"{platform_label} to push comments, saves, or follows."
            ),
            start_time=start_end_pairs[2][0],
            end_time=start_end_pairs[2][1],
            score=85,
            format="Story CTA",
            clip_url=clip_urls[2],
            raw_clip_url=clip_urls[2],
            transcript_excerpt=transcript_excerpts[2],
            edit_profile="Source cut preview" if clip_urls[2] else None,
            aspect_ratio="source" if clip_urls[2] else None,
        ),
    ]


def normalize_clip_urls(values: Optional[List[Optional[str]]]) -> List[Optional[str]]:
    normalized = list(values or [])
    return (normalized + [None, None, None])[:3]


def normalize_start_end_pairs(values: Optional[List[tuple[str, str]]]) -> List[tuple[str, str]]:
    defaults = [("00:03", "00:18"), ("00:24", "00:39"), ("00:47", "01:04")]
    normalized = list(values or [])
    return (normalized + defaults)[0:3]


def normalize_transcript_excerpts(values: Optional[List[Optional[str]]]) -> List[Optional[str]]:
    normalized = list(values or [])
    return (normalized + [None, None, None])[:3]
