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
    clip_urls = clip_urls or [None, None, None]
    start_end_pairs = start_end_pairs or [("00:03", "00:18"), ("00:24", "00:39"), ("00:47", "01:04")]
    transcript_excerpts = transcript_excerpts or [None, None, None]

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
            transcript_excerpt=transcript_excerpts[0],
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
            transcript_excerpt=transcript_excerpts[1],
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
            transcript_excerpt=transcript_excerpts[2],
        ),
    ]
