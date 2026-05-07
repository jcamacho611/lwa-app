from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import OfflineVideoPipelineResult


def build_offline_proof(result: OfflineVideoPipelineResult) -> dict[str, Any]:
    def _is_successful_render(output: dict[str, Any]) -> bool:
        if bool(output.get("ok")):
            return True
        nested_render = output.get("render")
        if isinstance(nested_render, dict):
            return bool(nested_render.get("ok"))
        return False

    selected_candidates: list[dict[str, Any]] = []
    for score in result.selected_candidates:
        selected_candidates.append(
            {
                "candidate_id": score.candidate_id,
                "rank": score.rank,
                "post_rank": score.post_rank,
                "score": score.total_score,
                "is_best_clip": score.is_best_clip,
                "reasons": score.reasons,
                "warnings": score.warnings,
                "score_breakdown": score.score_breakdown,
            }
        )

    render_status = "strategy_only"
    if result.render_requested:
        if any(_is_successful_render(output) for output in result.render_outputs):
            render_status = "rendered"
        elif result.ffmpeg_available:
            render_status = "render_failed"

    return {
        "source_filename": Path(result.source_path).name,
        "source_path": result.source_path,
        "output_dir": result.output_dir,
        "duration_seconds": result.probe.duration_seconds,
        "render_status": render_status,
        "selected_candidates": selected_candidates,
        "rendered_clip_count": sum(1 for output in result.render_outputs if _is_successful_render(output)),
        "warnings": list(result.warnings),
        "provider_calls": [],
        "paid_provider_called": False,
        "external_action_executed": False,
        "ffmpeg_available": result.ffmpeg_available,
        "render_requested": result.render_requested,
        "strategy_only": render_status == "strategy_only",
    }
