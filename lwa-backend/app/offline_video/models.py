from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VideoProbeResult:
    input_path: str
    available: bool
    ffprobe_available: bool
    ffmpeg_available: bool
    duration_seconds: float
    width: int | None = None
    height: int | None = None
    has_audio: bool = False
    has_video: bool = False
    format_name: str | None = None
    video_codec: str | None = None
    audio_codec: str | None = None
    frame_rate: float | None = None
    bitrate_kbps: float | None = None
    stream_count: int = 0
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SceneBoundary:
    start_seconds: float
    end_seconds: float
    source: str = "fallback"
    confidence: float = 0.5
    reason: str = ""


@dataclass(slots=True)
class AudioWindow:
    start_seconds: float
    end_seconds: float
    silence_ratio: float
    average_energy: float
    peak_energy: float
    source: str = "fallback"
    has_speech_proxy: bool = True
    silence_detected: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MomentCandidate:
    candidate_id: str
    start_seconds: float
    end_seconds: float
    target_duration_seconds: float
    scene_indices: list[int] = field(default_factory=list)
    audio_window_indices: list[int] = field(default_factory=list)
    silence_ratio: float = 0.0
    visual_movement_proxy: float = 0.0
    hook_position_seconds: float = 0.0
    caption_readiness: float = 0.0
    platform_fit: float = 0.0
    transcript_available: bool = False
    selection_notes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class CaptionSegment:
    start_seconds: float
    end_seconds: float
    text: str
    source: str = "placeholder"
    transcript_available: bool = False
    placeholder: bool = True


@dataclass(slots=True)
class ClipScore:
    candidate_id: str
    total_score: float
    score_breakdown: dict[str, float] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    rank: int | None = None
    post_rank: int | None = None
    is_best_clip: bool = False
    render_ready: bool = False


@dataclass(slots=True)
class RenderPlan:
    candidate_id: str
    source_path: str
    output_dir: str
    output_path: str
    thumbnail_path: str
    start_seconds: float
    end_seconds: float
    target_duration_seconds: float
    crop_mode: str = "preserve"
    container_format: str = "mp4"


@dataclass(slots=True)
class ThumbnailPlan:
    candidate_id: str
    source_path: str
    suggested_filename: str
    timestamp_seconds: float


@dataclass(slots=True)
class OfflineVideoPipelineOptions:
    render: bool = False
    transcript: str | None = None
    target_durations: tuple[int, ...] = (15, 30, 45, 60)
    max_results: int = 3
    generate_thumbnails: bool = True
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"


@dataclass(slots=True)
class OfflineVideoPipelineResult:
    source_path: str
    output_dir: str
    probe: VideoProbeResult
    scene_boundaries: list[SceneBoundary] = field(default_factory=list)
    audio_windows: list[AudioWindow] = field(default_factory=list)
    candidates: list[MomentCandidate] = field(default_factory=list)
    scored_candidates: list[ClipScore] = field(default_factory=list)
    selected_candidates: list[ClipScore] = field(default_factory=list)
    render_plans: list[RenderPlan] = field(default_factory=list)
    render_outputs: list[dict[str, Any]] = field(default_factory=list)
    proof: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    render_requested: bool = False
    ffmpeg_available: bool = False
    success: bool = False
