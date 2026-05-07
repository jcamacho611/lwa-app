from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .ffmpeg_probe import check_ffmpeg_available
from .models import AudioWindow, VideoProbeResult

_SILENCE_START_RE = re.compile(r"silence_start:\s*(\d+(?:\.\d+)?)")
_SILENCE_END_RE = re.compile(r"silence_end:\s*(\d+(?:\.\d+)?)")


def _build_neutral_windows(duration_seconds: float) -> list[AudioWindow]:
    if duration_seconds <= 0:
        return [AudioWindow(start_seconds=0.0, end_seconds=0.0, silence_ratio=0.0, average_energy=0.5, peak_energy=0.5, source="fallback", has_speech_proxy=False)]

    window_size = 15.0
    windows: list[AudioWindow] = []
    start = 0.0
    while start < duration_seconds:
        end = min(duration_seconds, start + window_size)
        windows.append(
            AudioWindow(
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                silence_ratio=0.25,
                average_energy=0.65,
                peak_energy=0.55,
                source="fallback",
                has_speech_proxy=True,
                silence_detected=False,
            )
        )
        if end >= duration_seconds:
            break
        start = end
    return windows


def _overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def analyze_audio_windows(
    path: str | Path,
    probe: VideoProbeResult,
    *,
    ffmpeg_binary: str = "ffmpeg",
) -> list[AudioWindow]:
    input_path = Path(path)
    if not input_path.exists() or not input_path.is_file():
        return _build_neutral_windows(probe.duration_seconds)

    if not probe.available or not check_ffmpeg_available(ffmpeg_binary=ffmpeg_binary):
        return _build_neutral_windows(probe.duration_seconds)

    command = [
        ffmpeg_binary,
        "-hide_banner",
        "-nostats",
        "-i",
        str(input_path),
        "-af",
        "silencedetect=noise=-35dB:d=0.75",
        "-f",
        "null",
        "-",
    ]

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return _build_neutral_windows(probe.duration_seconds)

    silence_intervals: list[tuple[float, float]] = []
    current_start: float | None = None
    for line in (completed.stderr or "").splitlines():
        start_match = _SILENCE_START_RE.search(line)
        if start_match:
            try:
                current_start = float(start_match.group(1))
            except ValueError:
                current_start = None
            continue
        end_match = _SILENCE_END_RE.search(line)
        if end_match and current_start is not None:
            try:
                silence_end = float(end_match.group(1))
            except ValueError:
                current_start = None
                continue
            silence_intervals.append((current_start, silence_end))
            current_start = None

    if not silence_intervals:
        return _build_neutral_windows(probe.duration_seconds)

    duration_seconds = max(probe.duration_seconds, silence_intervals[-1][1])
    windows: list[AudioWindow] = []
    window_size = 15.0
    start = 0.0
    while start < duration_seconds:
        end = min(duration_seconds, start + window_size)
        overlap_seconds = sum(_overlap(start, end, silence_start, silence_end) for silence_start, silence_end in silence_intervals)
        window_length = max(end - start, 1e-6)
        silence_ratio = min(1.0, max(0.0, overlap_seconds / window_length))
        average_energy = round(max(0.05, 1.0 - silence_ratio * 0.9), 3)
        peak_energy = round(max(0.1, 1.0 - silence_ratio * 0.6), 3)
        windows.append(
            AudioWindow(
                start_seconds=round(start, 3),
                end_seconds=round(end, 3),
                silence_ratio=round(silence_ratio, 3),
                average_energy=average_energy,
                peak_energy=peak_energy,
                source="silencedetect",
                has_speech_proxy=silence_ratio < 0.7,
                silence_detected=silence_ratio > 0.0,
                warnings=[],
            )
        )
        if end >= duration_seconds:
            break
        start = end

    return windows or _build_neutral_windows(probe.duration_seconds)
