from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .ffmpeg_probe import check_ffmpeg_available
from .models import MomentCandidate, ThumbnailPlan

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize(value: str) -> str:
    return _SAFE_NAME_RE.sub("_", value).strip("._-") or "clip"


def build_thumbnail_plan(candidate: MomentCandidate) -> ThumbnailPlan:
    start_tag = f"{candidate.start_seconds:.2f}".replace(".", "_")
    suggested_filename = f"{_sanitize(candidate.candidate_id)}_{start_tag}.jpg"
    timestamp = candidate.start_seconds + min(1.0, max(0.0, (candidate.end_seconds - candidate.start_seconds) / 2.0))
    return ThumbnailPlan(
        candidate_id=candidate.candidate_id,
        source_path="",
        suggested_filename=suggested_filename,
        timestamp_seconds=round(timestamp, 3),
    )


def generate_thumbnail(
    path: str | Path,
    output_path: str | Path,
    timestamp: float,
    *,
    ffmpeg_binary: str = "ffmpeg",
) -> dict[str, object]:
    source_path = Path(path)
    destination = Path(output_path)
    if not source_path.exists() or not source_path.is_file():
        return {
            "ok": False,
            "output_path": str(destination),
            "error": "source_missing",
            "ffmpeg_available": False,
        }
    if not check_ffmpeg_available(ffmpeg_binary=ffmpeg_binary):
        return {
            "ok": False,
            "output_path": str(destination),
            "error": "ffmpeg_unavailable",
            "ffmpeg_available": False,
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_binary,
        "-hide_banner",
        "-nostats",
        "-y",
        "-ss",
        f"{max(timestamp, 0.0):.3f}",
        "-i",
        str(source_path),
        "-vframes",
        "1",
        "-q:v",
        "2",
        str(destination),
    ]

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {
            "ok": False,
            "output_path": str(destination),
            "error": "ffmpeg_unavailable",
            "ffmpeg_available": False,
            "command": command,
        }

    if completed.returncode != 0:
        return {
            "ok": False,
            "output_path": str(destination),
            "error": (completed.stderr or completed.stdout or "ffmpeg_failed").strip(),
            "ffmpeg_available": True,
            "command": command,
        }

    return {
        "ok": True,
        "output_path": str(destination),
        "error": None,
        "ffmpeg_available": True,
        "command": command,
    }
