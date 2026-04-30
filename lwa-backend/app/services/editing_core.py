from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# LWA OMEGA
# CLAUDE HANDOFF
# UPLOAD-FIRST CLIPPING ENGINE
# LOCAL-FIRST FALLBACK
# NONFATAL PIPELINE
# PRODUCTION EDITING CORE


@dataclass(frozen=True)
class EditSegment:
    start_seconds: float
    end_seconds: float
    role: str
    caption: str
    reason: str

    @property
    def duration_seconds(self) -> float:
        return max(0.0, self.end_seconds - self.start_seconds)


def _safe_float(value: Any, fallback: float) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return fallback


def build_default_segments(source: dict[str, Any], target_count: int = 5) -> list[EditSegment]:
    duration = max(_safe_float(source.get("duration_seconds") or source.get("duration"), 60.0), 15.0)
    window = min(30.0, max(8.0, duration / max(target_count, 1)))
    segments: list[EditSegment] = []
    for index in range(target_count):
        start = min(duration - 3.0, index * max(3.0, window * 0.75))
        end = min(duration, start + window)
        if end <= start:
            continue
        role = "hook" if index == 0 else "proof" if index < target_count - 1 else "payoff"
        segments.append(
            EditSegment(
                start_seconds=round(start, 2),
                end_seconds=round(end, 2),
                role=role,
                caption=f"Segment {index + 1}",
                reason="Deterministic fallback segment generated without failing the pipeline.",
            )
        )
    return segments


def apply_override_segments(segments: list[EditSegment], override_segments: list[dict[str, Any]] | None = None) -> list[EditSegment]:
    if not override_segments:
        return segments
    overrides: list[EditSegment] = []
    for index, item in enumerate(override_segments):
        start = _safe_float(item.get("start_seconds") or item.get("start"), 0.0)
        end = _safe_float(item.get("end_seconds") or item.get("end"), start + 15.0)
        if end <= start:
            continue
        overrides.append(
            EditSegment(
                start_seconds=round(start, 2),
                end_seconds=round(end, 2),
                role=str(item.get("role") or "override"),
                caption=str(item.get("caption") or f"Override {index + 1}"),
                reason=str(item.get("reason") or "Semantic cut graph override."),
            )
        )
    return overrides or segments


def build_edit_manifest(source: dict[str, Any], override_segments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    base_segments = build_default_segments(source)
    segments = apply_override_segments(base_segments, override_segments)
    return {
        "status": "ready",
        "source_id": source.get("id") or source.get("source_id") or "local-source",
        "fallback_mode": True,
        "segments": [segment.__dict__ | {"duration_seconds": segment.duration_seconds} for segment in segments],
        "notes": ["Nonfatal local editing manifest generated."],
    }
