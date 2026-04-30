from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# LWA OPERATOR DASHBOARD FOUNDATION
# REAL SYSTEM STATE ONLY
# NO FAKE SOCIAL METRICS
# NO FAKE DIRECT POSTING
# NO MARKETPLACE PAYOUT CLAIMS


@dataclass(frozen=True)
class OperatorDashboardSummary:
    total_runs: int
    total_clips: int
    rendered_clips: int
    strategy_only_clips: int
    attention_needed_count: int
    best_score: int | None


READY_KEYS = ("preview_url", "clip_url", "edited_clip_url", "download_url", "raw_clip_url")


def _clip_score(clip: dict[str, Any]) -> int:
    value = clip.get("score") or clip.get("virality_score") or clip.get("confidence_score") or 0
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _has_asset(clip: dict[str, Any]) -> bool:
    return any(isinstance(clip.get(key), str) and bool(str(clip.get(key)).strip()) for key in READY_KEYS)


def _is_strategy_only(clip: dict[str, Any]) -> bool:
    return bool(
        clip.get("strategy_only")
        or clip.get("is_strategy_only")
        or str(clip.get("visual_engine_status") or "").lower() == "strategy_only"
        or not _has_asset(clip)
    )


def summarize_operator_runs(runs: list[dict[str, Any]]) -> OperatorDashboardSummary:
    clips: list[dict[str, Any]] = []
    for run in runs:
        clips.extend([clip for clip in run.get("clips", []) if isinstance(clip, dict)])

    rendered = [clip for clip in clips if _has_asset(clip) and not _is_strategy_only(clip)]
    strategy = [clip for clip in clips if _is_strategy_only(clip)]
    attention_needed = [
        clip
        for clip in clips
        if clip.get("quality_gate_status") in {"warning", "fail"}
        or clip.get("visual_engine_status") in {"recoverable", "render_failed"}
    ]
    scores = [_clip_score(clip) for clip in clips]
    return OperatorDashboardSummary(
        total_runs=len(runs),
        total_clips=len(clips),
        rendered_clips=len(rendered),
        strategy_only_clips=len(strategy),
        attention_needed_count=len(attention_needed),
        best_score=max(scores) if scores else None,
    )


def build_attention_cards(runs: list[dict[str, Any]], limit: int = 10) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for run in runs:
        request_id = run.get("request_id") or run.get("id") or "unknown-run"
        for clip in run.get("clips", []):
            if not isinstance(clip, dict):
                continue
            reason = None
            if clip.get("quality_gate_status") == "fail":
                reason = "quality gate failed"
            elif clip.get("quality_gate_status") == "warning":
                reason = "quality gate warning"
            elif clip.get("visual_engine_status") == "recoverable":
                reason = "render recoverable"
            elif clip.get("visual_engine_status") == "render_failed":
                reason = "render failed"
            elif _is_strategy_only(clip):
                reason = "strategy-only output"
            if reason:
                cards.append(
                    {
                        "request_id": request_id,
                        "clip_id": clip.get("id") or clip.get("clip_id"),
                        "title": clip.get("title") or clip.get("hook") or "Untitled clip",
                        "reason": reason,
                        "score": _clip_score(clip),
                    }
                )
    return sorted(cards, key=lambda item: item.get("score", 0), reverse=True)[:limit]


def operator_disclosure() -> str:
    return "Operator metrics summarize available LWA run data only. External social performance metrics require verified integrations."
