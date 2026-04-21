from __future__ import annotations

import re
import subprocess
from typing import Dict, List


def detect_silence_regions(
    video_path: str,
    *,
    ffmpeg_path: str = "ffmpeg",
    silence_db: int = -35,
    min_silence_duration: float = 0.35,
) -> List[Dict]:
    """
    Detect silence spans using FFmpeg's silencedetect filter.
    Returns regions shaped for downstream speech inversion.
    """
    command = [
        ffmpeg_path,
        "-hide_banner",
        "-i",
        video_path,
        "-af",
        f"silencedetect=noise={silence_db}dB:d={min_silence_duration}",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)

    silence_regions: List[Dict] = []
    current_start: float | None = None
    for line in result.stderr.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        if start_match:
            current_start = float(start_match.group(1))
            continue

        end_match = re.search(r"silence_end:\s*([0-9.]+)", line)
        if end_match and current_start is not None:
            silence_end = float(end_match.group(1))
            if silence_end > current_start:
                silence_regions.append(
                    {
                        "type": "silence",
                        "region_type": "silence",
                        "start_time": current_start,
                        "end_time": silence_end,
                        "duration": silence_end - current_start,
                    }
                )
            current_start = None

    return silence_regions


def trim_silence_windows(segments: List[Dict], max_silence_gap: float = 0.8) -> List[Dict]:
    """
    Lightweight silence-aware cleanup using transcript/audio segment gaps.
    Expects segments shaped like:
    { "start": float, "end": float, "text": str, "energy": float|None }
    """
    if not segments:
        return []

    cleaned = [segments[0]]

    for seg in segments[1:]:
        prev = cleaned[-1]
        gap = max(0.0, float(seg.get("start", 0)) - float(prev.get("end", 0)))

        # If silence gap is too large, keep as new beat.
        if gap > max_silence_gap:
            cleaned.append(seg)
            continue

        # Merge tiny-gap segments to tighten pacing.
        merged = {
            "start": prev.get("start", 0),
            "end": seg.get("end", prev.get("end", 0)),
            "text": f'{prev.get("text", "").strip()} {seg.get("text", "").strip()}'.strip(),
            "energy": max(float(prev.get("energy", 0) or 0), float(seg.get("energy", 0) or 0)),
        }
        cleaned[-1] = merged

    return cleaned
