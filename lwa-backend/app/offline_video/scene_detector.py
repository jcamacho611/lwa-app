from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .ffmpeg_probe import check_ffmpeg_available
from .models import SceneBoundary, VideoProbeResult

_PTS_TIME_RE = re.compile(r"pts_time:(\d+(?:\.\d+)?)")


def _fallback_boundaries(duration_seconds: float) -> list[SceneBoundary]:
    if duration_seconds <= 0:
        return [SceneBoundary(start_seconds=0.0, end_seconds=0.0, source="fallback", confidence=0.0, reason="empty_source")]
    if duration_seconds <= 15:
        return [SceneBoundary(start_seconds=0.0, end_seconds=duration_seconds, source="fallback", confidence=0.55, reason="short_video")]

    step = max(15.0, min(30.0, duration_seconds / 5.0))
    boundaries: list[SceneBoundary] = []
    start = 0.0
    while start < duration_seconds:
        end = min(duration_seconds, start + step)
        boundaries.append(
            SceneBoundary(
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                source="fallback",
                confidence=0.55,
                reason="deterministic_fallback_window",
            )
        )
        if end >= duration_seconds:
            break
        start = end
    return boundaries


def detect_scene_boundaries(
    path: str | Path,
    probe: VideoProbeResult,
    *,
    ffmpeg_binary: str = "ffmpeg",
) -> list[SceneBoundary]:
    input_path = Path(path)
    if not input_path.exists() or not input_path.is_file():
        return _fallback_boundaries(probe.duration_seconds)

    if not probe.available or not check_ffmpeg_available(ffmpeg_binary=ffmpeg_binary):
        return _fallback_boundaries(probe.duration_seconds)

    command = [
        ffmpeg_binary,
        "-hide_banner",
        "-nostats",
        "-i",
        str(input_path),
        "-filter:v",
        "select='gt(scene,0.30)',showinfo",
        "-f",
        "null",
        "-",
    ]

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return _fallback_boundaries(probe.duration_seconds)

    if completed.returncode != 0 and not completed.stderr:
        return _fallback_boundaries(probe.duration_seconds)

    scene_times: list[float] = []
    for line in (completed.stderr or "").splitlines():
        match = _PTS_TIME_RE.search(line)
        if not match:
            continue
        try:
            time_value = float(match.group(1))
        except ValueError:
            continue
        if 0.5 < time_value < max(probe.duration_seconds, 0.0):
            scene_times.append(time_value)

    unique_times = sorted(set(round(time_value, 3) for time_value in scene_times))
    if not unique_times:
        return _fallback_boundaries(probe.duration_seconds)

    duration_seconds = max(probe.duration_seconds, unique_times[-1])
    boundaries: list[SceneBoundary] = []
    start = 0.0
    for time_value in unique_times:
        if time_value <= start + 0.5:
            continue
        boundaries.append(
            SceneBoundary(
                start_seconds=round(start, 3),
                end_seconds=round(time_value, 3),
                source="ffmpeg-scene",
                confidence=0.92,
                reason="scene_change_detected",
            )
        )
        start = time_value

    if duration_seconds > start + 0.5:
        boundaries.append(
            SceneBoundary(
                start_seconds=round(start, 3),
                end_seconds=round(duration_seconds, 3),
                source="ffmpeg-scene",
                confidence=0.92,
                reason="scene_change_detected",
            )
        )

    return boundaries or _fallback_boundaries(probe.duration_seconds)
