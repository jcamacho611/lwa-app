"""
LWA Auto Editor Brain — additive enrichment layer.

Attaches an `auto_editor` object to each ClipResult. Never fails /generate.
If an LLM provider is unavailable or errors, returns a deterministic heuristic
computed from fields already present on the clip.

Guarantees:
  * No new env vars required.
  * No DB schema change, no ffmpeg call, no new external HTTP at import time.
  * All provider calls are timed-out, retried once, and exception-isolated.
  * All return paths produce a fully-populated AutoEditorBrain.
  * Pydantic v2 (mirrors the rest of the codebase).
  * Structured logging via stdlib logging. No print, no console output.
"""
from __future__ import annotations

import asyncio
import importlib
import json
import logging
import os
import re
from typing import Any, List, Optional, Sequence

from pydantic import BaseModel, Field

logger = logging.getLogger("lwa.auto_editor_brain")

_LLM_TIMEOUT_S = float(os.environ.get("LWA_AUTO_EDITOR_LLM_TIMEOUT", "8"))
_LLM_MAX_RETRIES = 1


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class AutoEditorScores(BaseModel):
    model_config = {"extra": "ignore", "protected_namespaces": ()}

    viral_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Estimated viral-grade probability (0-100).")
    retention_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Estimated audience retention (0-100).")
    hook_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Strength of the first ~3 seconds (0-100).")
    clarity_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="How clearly the core idea lands (0-100).")
    focus_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="How tightly the clip stays on one idea (0-100).")
    silence_risk_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Risk that quiet stretches hurt retention (higher==worse).")
    dead_scene_risk_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Risk of visually static frames (higher==worse).")
    pacing_score: float = Field(default=0.0, ge=0.0, le=100.0,
        description="Editorial pacing health (higher==better).")


class AutoEditorRecommendations(BaseModel):
    model_config = {"extra": "ignore", "protected_namespaces": ()}

    caption_style_recommendation: Optional[str] = Field(default=None,
        description="Recommended caption style token, e.g. 'bold-centered-yellow'.")
    font_style_recommendation: Optional[str] = Field(default=None,
        description="Recommended font, e.g. 'Montserrat ExtraBold'.")
    edit_style_recommendation: Optional[str] = Field(default=None,
        description="Recommended edit style, e.g. 'fast-cut-with-zoom-pulses'.")
    filter_recommendation: Optional[str] = Field(default=None,
        description="Recommended color/filter direction, e.g. 'warm-cinematic'.")
    music_sync_notes: Optional[str] = Field(default=None,
        description="Notes for music/beat alignment.")
    b_roll_suggestions: List[str] = Field(default_factory=list,
        description="B-roll concepts that reinforce the clip.")
    pacing_notes: Optional[str] = Field(default=None,
        description="Free-form pacing guidance for an editor.")


class AutoEditorExportProfile(BaseModel):
    model_config = {"extra": "ignore", "protected_namespaces": ()}

    width: int = Field(default=1080, gt=0, description="Recommended width in px.")
    height: int = Field(default=1920, gt=0, description="Recommended height in px.")
    fps: int = Field(default=30, gt=0, le=120, description="Recommended frame rate.")
    bitrate: str = Field(default="8M", description="Recommended encoder bitrate.")
    container: str = Field(default="mp4", description="Recommended container.")
    label: str = Field(default="1080p-vertical-tiktok",
        description="Human-readable export label.")


class AutoEditorCustomization(BaseModel):
    model_config = {"extra": "ignore", "protected_namespaces": ()}

    options: List[str] = Field(default_factory=list,
        description="Customization toggles, e.g. 'add_zoom_pulses'.")


class AutoEditorBrain(BaseModel):
    """Additive enrichment payload attached to ClipResult.auto_editor."""
    model_config = {"extra": "ignore", "protected_namespaces": ()}

    status: str = Field(default="heuristic",
        description="One of: 'ai', 'heuristic', 'skipped'.")
    provider: str = Field(default="heuristic",
        description="Provider used: 'anthropic', 'openai', 'internal', 'heuristic'.")
    provider_note: Optional[str] = Field(default=None,
        description="Sanitized operator note.")
    scores: AutoEditorScores = Field(default_factory=AutoEditorScores)
    recommendations: AutoEditorRecommendations = Field(default_factory=AutoEditorRecommendations)
    export_profile_recommendation: AutoEditorExportProfile = Field(default_factory=AutoEditorExportProfile)
    customization: AutoEditorCustomization = Field(default_factory=AutoEditorCustomization)
    next_edit_actions: List[str] = Field(default_factory=list)
    risk_flags: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _coerce_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        v = float(value)
        return default if v != v else v  # NaN guard
    except (TypeError, ValueError):
        return default


def _clamp(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def _normalize_to_100(value: Any) -> float:
    v = _coerce_float(value, 0.0)
    if v <= 1.0:
        return _clamp(v * 100.0)
    if v <= 10.0:
        return _clamp(v * 10.0)
    return _clamp(v)


def _is_strategy_only(clip: Any) -> bool:
    return bool(_get(clip, "is_strategy_only") or _get(clip, "strategy_only"))


def _duration(clip: Any) -> float:
    return _coerce_float(
        _get(clip, "duration_seconds") or _get(clip, "duration"), 0.0
    )


def _transcript(clip: Any) -> str:
    return str(
        _get(clip, "transcript_excerpt")
        or _get(clip, "transcript")
        or _get(clip, "caption")
        or ""
    )


# ---------------------------------------------------------------------------
# Export profiles
# ---------------------------------------------------------------------------

_PLATFORM_PROFILES: dict[str, AutoEditorExportProfile] = {
    "tiktok":    AutoEditorExportProfile(width=1080, height=1920, fps=30, bitrate="8M",  container="mp4", label="1080p-vertical-tiktok"),
    "reels":     AutoEditorExportProfile(width=1080, height=1920, fps=30, bitrate="8M",  container="mp4", label="1080p-vertical-reels"),
    "shorts":    AutoEditorExportProfile(width=1080, height=1920, fps=30, bitrate="8M",  container="mp4", label="1080p-vertical-shorts"),
    "youtube":   AutoEditorExportProfile(width=1920, height=1080, fps=30, bitrate="12M", container="mp4", label="1080p-horizontal-youtube"),
    "twitter":   AutoEditorExportProfile(width=1280, height=720,  fps=30, bitrate="6M",  container="mp4", label="720p-horizontal-twitter"),
    "x":         AutoEditorExportProfile(width=1280, height=720,  fps=30, bitrate="6M",  container="mp4", label="720p-horizontal-x"),
    "instagram": AutoEditorExportProfile(width=1080, height=1350, fps=30, bitrate="8M",  container="mp4", label="1080x1350-instagram"),
}


def _pick_profile(target_platform: Optional[str]) -> AutoEditorExportProfile:
    if not target_platform:
        return _PLATFORM_PROFILES["tiktok"]
    return _PLATFORM_PROFILES.get(str(target_platform).strip().lower(), _PLATFORM_PROFILES["tiktok"])


# ---------------------------------------------------------------------------
# Heuristic path (deterministic, no I/O)
# ---------------------------------------------------------------------------

def _heuristic_brain(
    clip: Any,
    target_platform: Optional[str],
    source_type: Optional[str],
    fallback_reason: Optional[str],
) -> AutoEditorBrain:
    score       = _normalize_to_100(_get(clip, "score"))
    hook        = _normalize_to_100(_get(clip, "hook_score"))
    confidence  = _normalize_to_100(_get(clip, "confidence_score"))
    duration    = _duration(clip)
    transcript  = _transcript(clip)
    plat_fit    = _normalize_to_100(_get(clip, "platform_fit"))
    breakdown   = _get(clip, "score_breakdown") or {}
    risk_in     = list(_get(clip, "risk_flags") or [])

    has_hook_text = bool(
        _get(clip, "hook")
        or re.search(r"[!?]|wait|stop|listen|nobody", transcript[:80], re.I)
    )
    word_density = len(transcript.split()) / duration if duration > 0 else 0.0

    viral    = _clamp(0.55 * score + 0.30 * hook + 0.15 * plat_fit)
    retention = _clamp(0.50 * score + 0.30 * confidence + 0.20 * (100.0 if 8 <= duration <= 45 else 60.0))
    hook_s   = _clamp(hook if hook > 0 else (75.0 if has_hook_text else 45.0))

    bd_clarity = _get(breakdown, "clarity") if isinstance(breakdown, dict) else None
    bd_focus   = _get(breakdown, "focus") if isinstance(breakdown, dict) else None
    clarity  = _clamp(_normalize_to_100(bd_clarity) or (80.0 if 4 <= len(transcript.split()) <= 60 else 55.0))
    focus    = _clamp(_normalize_to_100(bd_focus) or (70.0 if duration <= 60 else 45.0))

    silence_risk   = 80.0 if word_density and word_density < 0.6 else (40.0 if word_density < 1.2 else 15.0)
    dead_scene_risk = 70.0 if source_type and str(source_type).lower() in {"podcast", "audio", "interview"} else 30.0
    pacing = _clamp(100.0 - 0.5 * silence_risk - 0.3 * dead_scene_risk)

    scores = AutoEditorScores(
        viral_score=round(viral, 1),
        retention_score=round(retention, 1),
        hook_score=round(hook_s, 1),
        clarity_score=round(clarity, 1),
        focus_score=round(focus, 1),
        silence_risk_score=round(silence_risk, 1),
        dead_scene_risk_score=round(dead_scene_risk, 1),
        pacing_score=round(pacing, 1),
    )

    plat = (target_platform or "tiktok").lower()
    if plat in {"tiktok", "reels", "shorts"}:
        cap_style, font, edit_style, filt = "bold-centered-yellow", "Montserrat ExtraBold", "fast-cut-with-zoom-pulses" if pacing < 80 else "fast-cut-rhythmic", "warm-cinematic"
    elif plat == "youtube":
        cap_style, font, edit_style, filt = "lower-third-white-shadow", "Inter SemiBold", "long-form-with-bookmark-cuts", "neutral-broadcast"
    else:
        cap_style, font, edit_style, filt = "burned-in-bottom-bold", "Inter Bold", "punchy-quote-cut", "neutral-broadcast"

    music_sync = (
        "Cut on transients in the first 3s; sustain low pad under dialogue; drop beat on punchline."
        if pacing < 75 else
        "Light music bed at -18 LUFS; do not duck under punchline."
    )

    b_roll: List[str] = []
    angle = str(_get(clip, "packaging_angle") or "")
    if angle:
        b_roll.append(f"Visual for angle: {angle}")
    if dead_scene_risk >= 60:
        b_roll.append("Cutaway every 2.5s to break talking-head dead scenes.")
    if "money" in transcript.lower() or "$" in transcript:
        b_roll.append("On-screen number animation when money is mentioned.")
    if not b_roll:
        b_roll.append("Topical stock cutaway aligned to the strongest noun in the transcript.")

    pacing_notes = (
        f"Target ~{max(2, int(round(duration / 3)))} cuts; open with motion in first 12 frames."
        if duration > 0 else
        "Open with motion in first 12 frames; aim for one cut every ~2.5s."
    )

    options = ["toggle_captions", "toggle_zoom_pulses", "toggle_music_bed", "toggle_b_roll", "swap_caption_palette"]
    if pacing < 70:
        options.append("auto_trim_silence")
    if dead_scene_risk >= 60:
        options.append("auto_insert_b_roll")

    next_actions: List[str] = []
    if hook_s < 65:
        next_actions.append("Rewrite first line for stronger hook.")
    if silence_risk >= 60:
        next_actions.append("Trim silences > 400ms.")
    if dead_scene_risk >= 60:
        next_actions.append("Insert at least 2 cutaways.")
    if not next_actions:
        next_actions.append("Approve and queue for export.")

    risks = list(risk_in)
    if _is_strategy_only(clip):
        risks.append("strategy_only_clip_no_render")
    if duration and duration > 90 and plat in {"tiktok", "reels", "shorts"}:
        risks.append("duration_exceeds_short_form_target")
    if duration and duration < 5:
        risks.append("duration_under_minimum_recommended")

    return AutoEditorBrain(
        status="heuristic",
        provider="heuristic",
        provider_note=fallback_reason or "heuristic-only enrichment",
        scores=scores,
        recommendations=AutoEditorRecommendations(
            caption_style_recommendation=cap_style,
            font_style_recommendation=font,
            edit_style_recommendation=edit_style,
            filter_recommendation=filt,
            music_sync_notes=music_sync,
            b_roll_suggestions=b_roll,
            pacing_notes=pacing_notes,
        ),
        export_profile_recommendation=_pick_profile(target_platform),
        customization=AutoEditorCustomization(options=options),
        next_edit_actions=next_actions,
        risk_flags=risks,
    )


# ---------------------------------------------------------------------------
# LLM provider chain
# ---------------------------------------------------------------------------

def _try_internal_helper() -> Optional[Any]:
    for path in (
        "app.services.llm",
        "app.services.ai_client",
        "app.services.anthropic_client",
        "app.services.openai_client",
        "app.services.providers",
    ):
        try:
            mod = importlib.import_module(path)
        except Exception:
            continue
        for fn_name in ("complete_json", "complete", "generate_json", "generate", "ainvoke"):
            fn = getattr(mod, fn_name, None)
            if callable(fn):
                return (path, fn_name, fn)
    return None


def _build_prompt(clip: Any, target_platform: Optional[str], source_type: Optional[str]) -> str:
    return (
        "You are the LWA Auto Editor Brain. Return STRICT JSON only. No prose. "
        "Score everything 0-100. silence_risk_score and dead_scene_risk_score are higher==worse.\n\n"
        f"target_platform: {target_platform}\nsource_type: {source_type}\n"
        f"duration_seconds: {_duration(clip)}\nscore: {_get(clip, 'score')}\n"
        f"hook_score: {_get(clip, 'hook_score')}\nconfidence_score: {_get(clip, 'confidence_score')}\n"
        f"hook: {_get(clip, 'hook')}\ncaption: {_get(clip, 'caption')}\n"
        f"packaging_angle: {_get(clip, 'packaging_angle')}\ntranscript: {_transcript(clip)[:1200]}\n\n"
        'Schema: {"scores":{"viral_score":0,"retention_score":0,"hook_score":0,'
        '"clarity_score":0,"focus_score":0,"silence_risk_score":0,'
        '"dead_scene_risk_score":0,"pacing_score":0},'
        '"recommendations":{"caption_style_recommendation":"","font_style_recommendation":"",'
        '"edit_style_recommendation":"","filter_recommendation":"","music_sync_notes":"",'
        '"b_roll_suggestions":[],"pacing_notes":""},'
        '"customization":{"options":[]},"next_edit_actions":[],"risk_flags":[]}'
    )


def _parse_json(text: str) -> Optional[dict]:
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def _merge(base: AutoEditorBrain, parsed: dict, provider: str) -> AutoEditorBrain:
    try:
        s = parsed.get("scores", {}) or {}
        r = parsed.get("recommendations", {}) or {}
        c = parsed.get("customization", {}) or {}

        def _f(name: str, fallback: float) -> float:
            v = s.get(name)
            return fallback if v is None else _clamp(_coerce_float(v, fallback))

        return AutoEditorBrain(
            status="ai",
            provider=provider,
            provider_note=f"ai-enrichment-applied via {provider}",
            scores=AutoEditorScores(
                viral_score=_f("viral_score", base.scores.viral_score),
                retention_score=_f("retention_score", base.scores.retention_score),
                hook_score=_f("hook_score", base.scores.hook_score),
                clarity_score=_f("clarity_score", base.scores.clarity_score),
                focus_score=_f("focus_score", base.scores.focus_score),
                silence_risk_score=_f("silence_risk_score", base.scores.silence_risk_score),
                dead_scene_risk_score=_f("dead_scene_risk_score", base.scores.dead_scene_risk_score),
                pacing_score=_f("pacing_score", base.scores.pacing_score),
            ),
            recommendations=AutoEditorRecommendations(
                caption_style_recommendation=r.get("caption_style_recommendation") or base.recommendations.caption_style_recommendation,
                font_style_recommendation=r.get("font_style_recommendation") or base.recommendations.font_style_recommendation,
                edit_style_recommendation=r.get("edit_style_recommendation") or base.recommendations.edit_style_recommendation,
                filter_recommendation=r.get("filter_recommendation") or base.recommendations.filter_recommendation,
                music_sync_notes=r.get("music_sync_notes") or base.recommendations.music_sync_notes,
                b_roll_suggestions=list(r.get("b_roll_suggestions") or base.recommendations.b_roll_suggestions),
                pacing_notes=r.get("pacing_notes") or base.recommendations.pacing_notes,
            ),
            export_profile_recommendation=base.export_profile_recommendation,
            customization=AutoEditorCustomization(options=list(c.get("options") or base.customization.options)),
            next_edit_actions=list(parsed.get("next_edit_actions") or base.next_edit_actions),
            risk_flags=list(parsed.get("risk_flags") or base.risk_flags),
        )
    except Exception:
        logger.warning("auto_editor_brain merge failed; keeping heuristic baseline")
        return base


async def _call_anthropic(prompt: str) -> Optional[str]:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # type: ignore
        client = anthropic.AsyncAnthropic()
        msg = await asyncio.wait_for(
            client.messages.create(
                model=os.environ.get("LWA_AUTO_EDITOR_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
                max_tokens=900,
                messages=[{"role": "user", "content": prompt}],
            ),
            timeout=_LLM_TIMEOUT_S,
        )
        return "\n".join(b.text for b in (getattr(msg, "content", []) or []) if hasattr(b, "text"))
    except Exception as exc:
        logger.warning("auto_editor_brain anthropic call failed: %s", type(exc).__name__)
        return None


async def _call_openai(prompt: str) -> Optional[str]:
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    try:
        import openai  # type: ignore
        client = openai.AsyncOpenAI()
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model=os.environ.get("LWA_AUTO_EDITOR_OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.2,
            ),
            timeout=_LLM_TIMEOUT_S,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        logger.warning("auto_editor_brain openai call failed: %s", type(exc).__name__)
        return None


async def _call_internal(helper: tuple, prompt: str) -> Optional[str]:
    _path, _name, fn = helper
    try:
        result = fn(prompt) if not asyncio.iscoroutinefunction(fn) else await asyncio.wait_for(fn(prompt), timeout=_LLM_TIMEOUT_S)
        if isinstance(result, dict):
            return json.dumps(result)
        return result if isinstance(result, str) else None
    except Exception as exc:
        logger.warning("auto_editor_brain internal helper failed: %s", type(exc).__name__)
        return None


async def _ai_upgrade(
    clip: Any,
    base: AutoEditorBrain,
    target_platform: Optional[str],
    source_type: Optional[str],
) -> AutoEditorBrain:
    prompt = _build_prompt(clip, target_platform, source_type)

    internal = _try_internal_helper()
    if internal is not None:
        for _ in range(_LLM_MAX_RETRIES + 1):
            parsed = _parse_json(await _call_internal(internal, prompt) or "")
            if parsed:
                return _merge(base, parsed, "internal")

    for _ in range(_LLM_MAX_RETRIES + 1):
        parsed = _parse_json(await _call_anthropic(prompt) or "")
        if parsed:
            return _merge(base, parsed, "anthropic")

    for _ in range(_LLM_MAX_RETRIES + 1):
        parsed = _parse_json(await _call_openai(prompt) or "")
        if parsed:
            return _merge(base, parsed, "openai")

    base.provider_note = "ai-enrichment-unavailable, returned heuristic"
    return base


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

async def _enrich_one_async(
    clip: Any,
    target_platform: Optional[str],
    source_type: Optional[str],
    fallback_reason: Optional[str],
) -> AutoEditorBrain:
    try:
        base = _heuristic_brain(clip, target_platform, source_type, fallback_reason)
    except Exception:
        logger.exception("auto_editor_brain heuristic failed; returning skipped brain")
        return AutoEditorBrain(
            status="skipped",
            provider="heuristic",
            provider_note="heuristic-computation-error",
            export_profile_recommendation=_pick_profile(target_platform),
        )
    try:
        return await asyncio.wait_for(
            _ai_upgrade(clip, base, target_platform, source_type),
            timeout=_LLM_TIMEOUT_S * (_LLM_MAX_RETRIES + 1) + 2.0,
        )
    except Exception:
        logger.warning("auto_editor_brain ai upgrade failed; returning heuristic")
        base.provider_note = "ai-enrichment-error, returned heuristic"
        return base


async def _safe_enrich_one(
    clip: Any,
    target_platform: Optional[str],
    source_type: Optional[str],
    fallback_reason: Optional[str],
) -> Any:
    """Wraps _enrich_one_async; returns clip with auto_editor attached. Never raises."""
    try:
        brain = await _enrich_one_async(
            clip,
            target_platform=target_platform or _get(clip, "target_platform"),
            source_type=source_type,
            fallback_reason=fallback_reason,
        )
        try:
            object.__setattr__(clip, "auto_editor", brain)
        except (AttributeError, TypeError):
            clip = clip.model_copy(update={"auto_editor": brain})
    except Exception:
        logger.exception("auto_editor_brain failed for one clip; attaching skipped brain")
        try:
            skipped = AutoEditorBrain(
                status="skipped",
                provider="heuristic",
                provider_note="per-clip-error",
                export_profile_recommendation=_pick_profile(target_platform),
            )
            try:
                object.__setattr__(clip, "auto_editor", skipped)
            except (AttributeError, TypeError):
                clip = clip.model_copy(update={"auto_editor": skipped})
        except Exception:
            pass
    return clip


async def enrich_clips_with_auto_editor_async(
    clips: Sequence[Any],
    target_platform: Optional[str] = None,
    source_type: Optional[str] = None,
    fallback_reason: Optional[str] = None,
) -> List[Any]:
    """
    Async entry point. Attaches `auto_editor` to each clip concurrently and returns
    the list in original order. Bounded concurrency (max 6) prevents runaway
    provider calls on large packs. Never raises.
    """
    if not clips:
        return list(clips or [])

    _MAX_CONCURRENT = 6
    sem = asyncio.Semaphore(_MAX_CONCURRENT)

    async def bounded(clip: Any) -> Any:
        async with sem:
            return await _safe_enrich_one(clip, target_platform, source_type, fallback_reason)

    return list(await asyncio.gather(*[bounded(c) for c in clips]))


__all__ = [
    "AutoEditorScores",
    "AutoEditorRecommendations",
    "AutoEditorCustomization",
    "AutoEditorExportProfile",
    "AutoEditorBrain",
    "enrich_clips_with_auto_editor_async",
]
