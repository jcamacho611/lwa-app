from __future__ import annotations

import re
import shutil
import subprocess
from uuid import uuid4
from pathlib import Path

from .ffmpeg_probe import check_ffmpeg_available
from .models import MomentCandidate, RenderPlan

_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._-]+")


def _sanitize(value: str) -> str:
    return _SAFE_NAME_RE.sub("_", value).strip("._-") or "clip"


def _is_within_directory(candidate: Path, directory: Path) -> bool:
    try:
        candidate.resolve().relative_to(directory.resolve())
        return True
    except Exception:
        return False


def _reserve_unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for index in range(1, 100):
        candidate = parent / f"{stem}_{index}{suffix}"
        if not candidate.exists():
            return candidate
    return parent / f"{stem}_{uuid4().hex}{suffix}"


def build_render_plan(candidate: MomentCandidate, output_dir: str | Path) -> RenderPlan:
    base_dir = Path(output_dir)
    safe_candidate = _sanitize(candidate.candidate_id)
    start_tag = f"{candidate.start_seconds:.2f}".replace(".", "_")
    end_tag = f"{candidate.end_seconds:.2f}".replace(".", "_")
    output_path = base_dir / f"{safe_candidate}_{start_tag}_{end_tag}.mp4"
    thumbnail_path = base_dir / f"{safe_candidate}_{start_tag}_{end_tag}.jpg"
    return RenderPlan(
        candidate_id=candidate.candidate_id,
        source_path="",
        output_dir=str(base_dir),
        output_path=str(output_path),
        thumbnail_path=str(thumbnail_path),
        start_seconds=candidate.start_seconds,
        end_seconds=candidate.end_seconds,
        target_duration_seconds=candidate.target_duration_seconds,
    )


def render_clip(
    path: str | Path,
    render_plan: RenderPlan,
    *,
    ffmpeg_binary: str = "ffmpeg",
) -> dict[str, object]:
    source_path = Path(path)
    output_path = Path(render_plan.output_path)
    output_dir = Path(render_plan.output_dir)
    if not source_path.exists() or not source_path.is_file():
        return {
            "ok": False,
            "output_path": str(output_path),
            "error": "source_missing",
            "ffmpeg_available": False,
        }
    if not check_ffmpeg_available(ffmpeg_binary=ffmpeg_binary):
        return {
            "ok": False,
            "output_path": str(output_path),
            "error": "ffmpeg_unavailable",
            "ffmpeg_available": False,
        }
    if not _is_within_directory(output_path, output_dir):
        return {
            "ok": False,
            "output_path": str(output_path),
            "error": "unsafe_output_path",
            "ffmpeg_available": True,
        }

    output_dir.mkdir(parents=True, exist_ok=True)
    reserved_output = _reserve_unique_path(output_path)
    command = [
        ffmpeg_binary,
        "-hide_banner",
        "-nostats",
        "-y",
        "-ss",
        f"{render_plan.start_seconds:.3f}",
        "-i",
        str(source_path),
        "-t",
        f"{max(render_plan.end_seconds - render_plan.start_seconds, 0.5):.3f}",
        "-vf",
        "scale='min(1080,iw)':-2",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        str(reserved_output),
    ]

    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return {
            "ok": False,
            "output_path": str(reserved_output),
            "error": "ffmpeg_unavailable",
            "ffmpeg_available": False,
            "command": command,
        }

    if completed.returncode != 0:
        return {
            "ok": False,
            "output_path": str(reserved_output),
            "error": (completed.stderr or completed.stdout or "ffmpeg_failed").strip(),
            "ffmpeg_available": True,
            "command": command,
        }

    return {
        "ok": True,
        "output_path": str(reserved_output),
        "error": None,
        "ffmpeg_available": True,
        "command": command,
    }
