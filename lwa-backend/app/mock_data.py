from typing import List, Optional

from .schemas import ClipResult, TrendItem


def build_mock_clips(
    video_url: str,
    target_platform: str = "Short-form",
    selected_trend: Optional[str] = None,
    content_angle: Optional[str] = None,
    trend_context: Optional[List[TrendItem]] = None,
    clip_urls: Optional[List[str]] = None,
    start_end_pairs: Optional[List[tuple[str, str]]] = None,
    source_title: Optional[str] = None,
    transcript_excerpts: Optional[List[Optional[str]]] = None,
) -> List[ClipResult]:
    source_label = video_url.split("//")[-1].split("/")[0]
    lead_trend = selected_trend or (trend_context[0].title if trend_context else "creator growth")
    preferred_angle = (content_angle or "").strip().lower()
    platform_label = target_platform or "Short-form"
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
            virality_score=92,
            confidence=0.94,
            rank=1,
            reason=(
                f"This is the strongest first impression because it reaches the payoff fast and makes the {lead_trend} angle "
                f"clear without extra setup."
            ),
            format="Hook First",
            clip_url=clip_urls[0],
            raw_clip_url=clip_urls[0],
            transcript_excerpt=transcript_excerpts[0],
            edit_profile="Source cut preview" if clip_urls[0] else None,
            aspect_ratio="source" if clip_urls[0] else None,
            why_this_matters=(
                f"Use this as the first post because it gets to the payoff fast and gives {platform_label} viewers "
                f"a clear reason to keep watching."
            ),
            confidence_score=94,
            thumbnail_text="Use This Angle",
            cta_suggestion=f"Ask viewers if they would test this {lead_trend} angle themselves.",
            post_rank=1,
            best_post_order=1,
            hook_variants=[
                f"The fastest way to use {lead_trend} before it gets crowded.",
                f"Most creators are still underusing this {lead_trend} move.",
                f"Use this {lead_trend} hook before your competitors catch up.",
            ],
            caption_variants={
                "viral": f"Use this {lead_trend} angle before it gets saturated. Comment if you want part 2.",
                "story": f"We pulled this from {source_label} because it gets to the payoff fast and earns the next swipe.",
                "educational": f"Save this breakdown and test the {lead_trend} format in your next post.",
                "controversial": f"Most creators are still framing {lead_trend} wrong. That is why this version wins.",
            },
            caption_style=caption_style_for(platform_label),
            platform_fit=platform_fit_for(platform_label, "Hook First"),
            packaging_angle=preferred_angle if preferred_angle in {"shock", "story", "value", "curiosity", "controversy"} else "value",
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
            virality_score=88,
            confidence=0.89,
            rank=2,
            reason="This clip creates tension and debate, which makes it strong as the second post in the pack.",
            format="Opinion",
            clip_url=clip_urls[1],
            raw_clip_url=clip_urls[1],
            transcript_excerpt=transcript_excerpts[1],
            edit_profile="Source cut preview" if clip_urls[1] else None,
            aspect_ratio="source" if clip_urls[1] else None,
            why_this_matters="This is the tension clip. Post it second to deepen the angle after the opening hook lands.",
            confidence_score=89,
            thumbnail_text="Everyone Gets This Wrong",
            cta_suggestion="Invite comments by asking whether the audience agrees or disagrees.",
            post_rank=2,
            best_post_order=2,
            hook_variants=[
                "Why the obvious version of this clip will underperform.",
                "The contrarian edit that makes this point hit harder.",
                "Everyone is clipping this wrong and missing the real point.",
            ],
            caption_variants={
                "viral": "Everyone clips this wrong. Test the sharper take first.",
                "story": "This cut works because it starts with tension and lands the opinion before attention drops.",
                "educational": "Use this structure when you want to turn one sharp point into a high-retention short.",
                "controversial": "Most creators chase safe takes. This clip wins by leaning into the disagreement.",
            },
            caption_style=caption_style_for(platform_label),
            platform_fit=platform_fit_for(platform_label, "Opinion"),
            packaging_angle=preferred_angle if preferred_angle in {"shock", "story", "value", "curiosity", "controversy"} else "controversy",
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
            virality_score=85,
            confidence=0.84,
            rank=3,
            reason="This clip works best after the stronger openers because it converts attention into a concrete next step.",
            format="Story CTA",
            clip_url=clip_urls[2],
            raw_clip_url=clip_urls[2],
            transcript_excerpt=transcript_excerpts[2],
            edit_profile="Source cut preview" if clip_urls[2] else None,
            aspect_ratio="source" if clip_urls[2] else None,
            why_this_matters="This is the conversion clip. Use it after the first two to turn attention into action.",
            confidence_score=84,
            thumbnail_text="This Is The Pivot",
            cta_suggestion=f"Close by telling {platform_label} viewers what to save, follow, or test next.",
            post_rank=3,
            best_post_order=3,
            hook_variants=[
                "The exact moment this angle starts converting.",
                "If you only post one follow-up, make it this one.",
                f"The {platform_label} follow-up that turns attention into action.",
            ],
            caption_variants={
                "viral": f"This is the follow-up that keeps the series moving on {platform_label}.",
                "story": "The story lands here. Use it after the opener to turn curiosity into momentum.",
                "educational": "Save this sequence if you want a clean example of payoff-first storytelling.",
                "controversial": "Most people would post this first. It works better as the third clip in the run.",
            },
            caption_style=caption_style_for(platform_label),
            platform_fit=platform_fit_for(platform_label, "Story CTA"),
            packaging_angle=preferred_angle if preferred_angle in {"shock", "story", "value", "curiosity", "controversy"} else "story",
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


def caption_style_for(platform_label: str) -> str:
    normalized = platform_label.lower()
    if normalized == "tiktok":
        return "Punchy proof-first"
    if normalized == "instagram":
        return "Polished emotional"
    if normalized == "youtube":
        return "Clarity-led payoff"
    if normalized == "facebook":
        return "Story-first social"
    return "Short-form native"


def platform_fit_for(platform_label: str, clip_format: str) -> str:
    normalized = platform_label.lower()
    if normalized == "tiktok":
        return "Fast hook and proof-first pacing for TikTok."
    if normalized == "instagram":
        return "Polished, emotional framing that suits Reels."
    if normalized == "youtube":
        return f"Context-light setup with clear payoff for Shorts via {clip_format.lower()} packaging."
    if normalized == "facebook":
        return "Comment-friendly social framing with broader audience clarity."
    return f"Short-form native packaging for {platform_label}."
