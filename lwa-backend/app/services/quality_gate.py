from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualityGateResult:
    quality_gate_status: str
    render_readiness_score: int
    warnings: list[str]
    strategy_only: bool


def clamp_score(value: int) -> int:
    return max(0, min(100, int(value)))


def evaluate_quality_gate(
    *,
    rendered_url: str | None = None,
    asset_url: str | None = None,
    start: int | float | None = None,
    end: int | float | None = None,
    duration_seconds: int | float | None = None,
    strategy_only: bool = False,
    audio_present: bool | None = None,
) -> QualityGateResult:
    warnings: list[str] = []
    score = 80

    has_asset = bool(rendered_url or asset_url)
    if strategy_only:
        warnings.append("Strategy-only package; no playable render is claimed.")
        score -= 25
    elif not has_asset:
        warnings.append("No rendered asset URL is available.")
        score -= 35

    if start is not None and end is not None:
        if float(end) <= float(start):
            warnings.append("Clip timestamps are invalid.")
            score -= 30
    else:
        warnings.append("Clip timestamps are incomplete.")
        score -= 10

    if duration_seconds is not None:
        if float(duration_seconds) <= 0:
            warnings.append("Clip duration is invalid.")
            score -= 30
        elif float(duration_seconds) > 180:
            warnings.append("Clip may be too long for short-form packaging.")
            score -= 10

    if audio_present is False:
        warnings.append("Audio may be missing or unavailable.")
        score -= 15

    final_score = clamp_score(score)
    if final_score >= 75 and not warnings:
        status = "pass"
    elif final_score >= 45:
        status = "warning"
    else:
        status = "fail"

    return QualityGateResult(
        quality_gate_status=status,
        render_readiness_score=final_score,
        warnings=warnings,
        strategy_only=strategy_only,
    )


def quality_gate_dict(**kwargs: object) -> dict[str, object]:
    result = evaluate_quality_gate(
        rendered_url=str(kwargs.get("rendered_url") or "") or None,
        asset_url=str(kwargs.get("asset_url") or "") or None,
        start=kwargs.get("start"),
        end=kwargs.get("end"),
        duration_seconds=kwargs.get("duration_seconds"),
        strategy_only=bool(kwargs.get("strategy_only", False)),
        audio_present=kwargs.get("audio_present") if isinstance(kwargs.get("audio_present"), bool) else None,
    )
    return result.__dict__.copy()
