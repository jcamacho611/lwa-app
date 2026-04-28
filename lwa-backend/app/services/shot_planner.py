from __future__ import annotations

from dataclasses import dataclass
import re

from ..models.schemas import ClipResult, ShotPlanStep


@dataclass(frozen=True)
class ShotPlanBlueprint:
    clip_type: str
    viral_trigger: str
    energy_level: str
    shot_plan: list[ShotPlanStep]
    shot_plan_confidence: int
    visual_engine_prompt: str
    motion_prompt: str
    text_overlay_plan: str
    subtitle_guidance: str
    transition_plan: str

    def as_clip_update(self) -> dict[str, object]:
        return {
            "clip_type": self.clip_type,
            "viral_trigger": self.viral_trigger,
            "energy_level": self.energy_level,
            "shot_plan": self.shot_plan,
            "shot_plan_confidence": self.shot_plan_confidence,
            "visual_engine_prompt": self.visual_engine_prompt,
            "motion_prompt": self.motion_prompt,
            "text_overlay_plan": self.text_overlay_plan,
            "subtitle_guidance": self.subtitle_guidance,
            "transition_plan": self.transition_plan,
        }


def build_shot_plan_for_clip(
    clip: ClipResult,
    *,
    target_platform: str | None = None,
) -> ShotPlanBlueprint:
    clip_type = infer_clip_type(clip)
    viral_trigger = infer_viral_trigger(clip, clip_type=clip_type)
    energy_level = infer_energy_level(clip)
    total_duration = estimate_total_duration_seconds(clip)
    durations = distribute_shot_durations(total_duration)
    overlay = build_text_overlay_plan(clip)
    subtitle_guidance = build_subtitle_guidance(target_platform or clip.platform_fit)
    transition_plan = build_transition_plan(clip_type=clip_type, energy_level=energy_level)
    shot_plan = [
        ShotPlanStep(
            role="hook",
            duration_seconds=durations[0],
            camera_direction=hook_camera_direction(energy_level),
            visual_direction=f"Open on the most instantly legible {viral_trigger.replace('_', ' ')} frame.",
            motion_direction="Punch in immediately and land the first beat inside one second.",
            text_overlay=overlay,
            subtitle_behavior=subtitle_guidance,
            transition="Hard cut open.",
            retention_goal="Stop the scroll and make the payoff feel immediate.",
        ),
        ShotPlanStep(
            role="context",
            duration_seconds=durations[1],
            camera_direction="Hold a readable medium frame that clarifies the setup without slowing down.",
            visual_direction=f"Show the minimum context needed to understand the {clip_type.replace('_', ' ')} angle.",
            motion_direction="Keep motion steady with one supporting camera move at most.",
            text_overlay="Add one supporting proof line only if clarity drops.",
            subtitle_behavior=subtitle_guidance,
            transition="Snap cut into context.",
            retention_goal="Give enough setup to make the payoff feel earned.",
        ),
        ShotPlanStep(
            role="payoff",
            duration_seconds=durations[2],
            camera_direction="Return to the most expressive close framing for the strongest line.",
            visual_direction="Show the exact proof, reaction, or reveal that makes the clip worth posting.",
            motion_direction="Accelerate the pacing and let the strongest movement land on the main claim.",
            text_overlay="Reveal the payoff phrase in 3 to 5 words.",
            subtitle_behavior=subtitle_guidance,
            transition="Cut on emphasis.",
            retention_goal="Deliver the reason the viewer stays through the middle.",
        ),
        ShotPlanStep(
            role="loop_end",
            duration_seconds=durations[3],
            camera_direction="Finish on a frame that can loop or point back to the opener cleanly.",
            visual_direction="End on a lingering question, reaction, or callback that invites another watch.",
            motion_direction="Ease the motion into a visual loop or hold.",
            text_overlay="Close with a loop line or CTA, not both.",
            subtitle_behavior=subtitle_guidance,
            transition="Use a soft loop or purposeful hold on the last word.",
            retention_goal="Increase rewatches and make the post order feel intentional.",
        ),
    ]
    shot_plan_confidence = build_shot_plan_confidence(
        clip=clip,
        total_duration=total_duration,
        energy_level=energy_level,
    )
    visual_engine_prompt = build_visual_engine_prompt(
        clip=clip,
        clip_type=clip_type,
        viral_trigger=viral_trigger,
        energy_level=energy_level,
        shot_plan=shot_plan,
        target_platform=target_platform,
    )
    motion_prompt = build_motion_prompt(
        energy_level=energy_level,
        clip_type=clip_type,
        transition_plan=transition_plan,
    )
    return ShotPlanBlueprint(
        clip_type=clip_type,
        viral_trigger=viral_trigger,
        energy_level=energy_level,
        shot_plan=shot_plan,
        shot_plan_confidence=shot_plan_confidence,
        visual_engine_prompt=visual_engine_prompt,
        motion_prompt=motion_prompt,
        text_overlay_plan=overlay,
        subtitle_guidance=subtitle_guidance,
        transition_plan=transition_plan,
    )


def infer_clip_type(clip: ClipResult) -> str:
    angle = (clip.packaging_angle or "").strip().lower()
    title_text = " ".join(
        part for part in [clip.hook, clip.title, clip.why_this_matters, clip.reason] if part
    ).lower()
    if angle == "story" or any(word in title_text for word in {"story", "journey", "before", "after"}):
        return "story"
    if angle == "controversy" or any(word in title_text for word in {"wrong", "debate", "controvers", "mistake"}):
        return "debate"
    if angle == "shock" or any(word in title_text for word in {"stop", "never", "instantly", "nobody"}):
        return "pattern_interrupt"
    if angle == "curiosity" or any(word in title_text for word in {"why", "how", "hidden", "secret"}):
        return "curiosity_explainer"
    if any(word in title_text for word in {"step", "framework", "breakdown", "process"}):
        return "tutorial"
    return "commentary"


def infer_viral_trigger(clip: ClipResult, *, clip_type: str) -> str:
    angle = (clip.packaging_angle or "").strip().lower()
    if angle == "controversy" or clip_type == "debate":
        return "disagreement"
    if angle == "story" or clip_type == "story":
        return "open_loop"
    if angle == "curiosity" or clip_type == "curiosity_explainer":
        return "curiosity_gap"
    if angle == "shock" or clip_type == "pattern_interrupt":
        return "pattern_interrupt"
    if clip.why_this_matters and "post this first" in clip.why_this_matters.lower():
        return "best_clip_first"
    return "fast_value"


def infer_energy_level(clip: ClipResult) -> str:
    text = " ".join(part for part in [clip.hook, clip.title, clip.caption] if part)
    exclamations = text.count("!")
    urgency_hits = len(re.findall(r"\b(now|fast|stop|must|instantly|today)\b", text.lower()))
    score = (clip.score or 0) + (exclamations * 5) + (urgency_hits * 4)
    if score >= 85:
        return "high"
    if score >= 65:
        return "medium"
    return "low"


def estimate_total_duration_seconds(clip: ClipResult) -> int:
    if clip.duration and clip.duration > 0:
        return max(clip.duration, 8)
    start_seconds = parse_timecode_to_seconds(clip.start_time or clip.timestamp_start)
    end_seconds = parse_timecode_to_seconds(clip.end_time or clip.timestamp_end)
    if start_seconds is not None and end_seconds is not None and end_seconds > start_seconds:
        return max(end_seconds - start_seconds, 8)
    return 18


def distribute_shot_durations(total_duration: int) -> tuple[int, int, int, int]:
    base = [0.24, 0.22, 0.36, 0.18]
    durations = [max(int(round(total_duration * weight)), 2) for weight in base]
    delta = total_duration - sum(durations)
    durations[-1] += delta
    if durations[-1] < 2:
        durations[-2] = max(durations[-2] - (2 - durations[-1]), 2)
        durations[-1] = 2
    return durations[0], durations[1], durations[2], durations[3]


def build_text_overlay_plan(clip: ClipResult) -> str:
    source = clip.thumbnail_text or clip.hook or clip.title or "Best clip first"
    words = [word for word in re.findall(r"[A-Za-z0-9']+", source) if len(word) > 2]
    if not words:
        return "Best clip first"
    return " ".join(words[:4]).title()


def build_subtitle_guidance(platform_hint: str | None) -> str:
    value = (platform_hint or "").lower()
    if "youtube" in value:
        return "Burn fast two-line subtitles with stronger emphasis on the last clause."
    if "instagram" in value:
        return "Use polished subtitle pacing with a little more spacing between ideas."
    return "Use bold center-safe subtitles that change every short clause."


def build_transition_plan(*, clip_type: str, energy_level: str) -> str:
    if clip_type == "story":
        return "Open hard, bridge with one clean match cut, then soften into the loop."
    if energy_level == "high":
        return "Hard cuts first, one snap zoom on the payoff, then a tight loop hold."
    if energy_level == "low":
        return "Keep transitions clean and minimal so the voice carries the momentum."
    return "Use hard cuts between beats and one purposeful hold for the ending loop."


def build_shot_plan_confidence(
    *,
    clip: ClipResult,
    total_duration: int,
    energy_level: str,
) -> int:
    confidence = int(clip.confidence_score or clip.score or 60)
    if total_duration <= 30:
        confidence += 4
    if energy_level == "high":
        confidence += 3
    if clip.transcript_excerpt:
        confidence += 3
    return max(min(confidence, 95), 55)


def build_visual_engine_prompt(
    *,
    clip: ClipResult,
    clip_type: str,
    viral_trigger: str,
    energy_level: str,
    shot_plan: list[ShotPlanStep],
    target_platform: str | None,
) -> str:
    platform = target_platform or clip.platform_fit or "short-form"
    shot_roles = " -> ".join(step.role for step in shot_plan)
    return (
        f"Build a {platform} clip plan for a {clip_type.replace('_', ' ')} angle with "
        f"a {viral_trigger.replace('_', ' ')} trigger and {energy_level} energy. "
        f"Sequence the beats as {shot_roles}. "
        f"Lead with '{clip.hook or clip.title}', keep subtitles creator-native, "
        f"and preserve the payoff before the CTA."
    )


def build_motion_prompt(*, energy_level: str, clip_type: str, transition_plan: str) -> str:
    energy_motion = {
        "high": "quick punch-ins, velocity ramps, assertive reframes",
        "medium": "steady handheld motion, one accent zoom, clean cut cadence",
        "low": "controlled framing, subtle push-ins, minimal camera drift",
    }
    return (
        f"Use {energy_motion.get(energy_level, energy_motion['medium'])} for a "
        f"{clip_type.replace('_', ' ')} clip. Transition plan: {transition_plan}"
    )


def hook_camera_direction(energy_level: str) -> str:
    if energy_level == "high":
        return "Start tight and aggressive with a close crop on the first claim."
    if energy_level == "low":
        return "Start centered and readable with a calm but immediate crop."
    return "Start medium-tight and push in on the first phrase."


def parse_timecode_to_seconds(value: str | None) -> int | None:
    if not value:
        return None
    parts = value.strip().split(":")
    if not parts or not all(part.isdigit() for part in parts):
        return None
    total = 0
    for part in parts:
        total = (total * 60) + int(part)
    return total
