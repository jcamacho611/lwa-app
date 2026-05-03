from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, List, Dict
from uuid import uuid4


class VideoJobType(str, Enum):
    TEXT_TO_VIDEO = "text_to_video"
    IMAGE_TO_VIDEO = "image_to_video"
    VIDEO_TO_VIDEO = "video_to_video"
    CLIP_TO_VIDEO = "clip_to_video"
    AUDIO_TO_VIDEO = "audio_to_video"
    SONG_VISUALIZER = "song_visualizer"
    TIMELINE_RENDER = "timeline_render"
    MULTI_ASSET_MASTERPIECE = "multi_asset_masterpiece"


class VideoJobStatus(str, Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PROVIDER_NOT_CONFIGURED = "provider_not_configured"
    CANCELED = "canceled"


@dataclass
class TimelineClip:
    id: str
    source_url: Optional[str] = None
    start_seconds: Optional[float] = None
    end_seconds: Optional[float] = None
    text: Optional[str] = None
    kind: str = "video"


@dataclass
class TimelineTrack:
    id: str
    kind: str
    clips: List[TimelineClip] = field(default_factory=list)


@dataclass
class TimelinePlan:
    id: str
    title: str
    aspect_ratio: str
    duration_seconds: int
    tracks: List[TimelineTrack] = field(default_factory=list)


@dataclass
class VideoJobRequest:
    job_type: VideoJobType
    prompt: Optional[str] = None
    input_urls: List[str] = field(default_factory=list)
    source_asset_ids: List[str] = field(default_factory=list)
    aspect_ratio: str = "9:16"
    duration_seconds: int = 15
    resolution: str = "720p"
    style_preset: Optional[str] = None


@dataclass
class VideoJob:
    job_id: str
    user_id: str
    job_type: VideoJobType
    provider: str
    status: VideoJobStatus
    prompt: Optional[str] = None
    input_urls: List[str] = field(default_factory=list)
    source_asset_ids: List[str] = field(default_factory=list)
    aspect_ratio: str = "9:16"
    duration_seconds: int = 15
    resolution: str = "720p"
    style_preset: Optional[str] = None
    cost_estimate_usd: float = 0.0
    progress: int = 0
    preview_url: Optional[str] = None
    output_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    error_message: Optional[str] = None
    timeline_plan: Optional[TimelinePlan] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class VideoProviderAdapter:
    provider_name = "base"

    def create_job(self, request: VideoJobRequest, user_id: str) -> VideoJob:
        raise NotImplementedError

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        raise NotImplementedError

    def cancel_job(self, job_id: str) -> Optional[VideoJob]:
        raise NotImplementedError


class MockVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "mock"

    def __init__(self) -> None:
        self.jobs: Dict[str, VideoJob] = {}

    def create_job(self, request: VideoJobRequest, user_id: str) -> VideoJob:
        job = VideoJob(
            job_id=f"video_job_{uuid4().hex}",
            user_id=user_id,
            job_type=request.job_type,
            provider=self.provider_name,
            status=VideoJobStatus.COMPLETED,
            prompt=request.prompt,
            input_urls=request.input_urls,
            source_asset_ids=request.source_asset_ids,
            aspect_ratio=request.aspect_ratio,
            duration_seconds=request.duration_seconds,
            resolution=request.resolution,
            style_preset=request.style_preset,
            cost_estimate_usd=estimate_video_job_cost(request),
            progress=100,
            output_url=None,
            preview_url=None,
            thumbnail_url=None,
            error_message="mock_render_completed_no_asset",
            timeline_plan=build_mock_timeline_plan(request),
        )
        self.jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        return self.jobs.get(job_id)

    def cancel_job(self, job_id: str) -> Optional[VideoJob]:
        job = self.jobs.get(job_id)
        if job:
            job.status = VideoJobStatus.CANCELED
            job.updated_at = datetime.utcnow().isoformat()
        return job


def estimate_video_job_cost(request: VideoJobRequest) -> float:
    base = 0.02
    duration_multiplier = max(1, request.duration_seconds / 10)
    resolution_multiplier = {
        "480p": 0.5,
        "720p": 1.0,
        "1080p": 2.0,
        "4k": 6.0,
    }.get(request.resolution, 1.0)
    return round(base * duration_multiplier * resolution_multiplier, 4)


def build_mock_timeline_plan(request: VideoJobRequest) -> TimelinePlan:
    return TimelinePlan(
        id=f"timeline_{uuid4().hex}",
        title=request.prompt or "LWA generated video plan",
        aspect_ratio=request.aspect_ratio,
        duration_seconds=request.duration_seconds,
        tracks=[
            TimelineTrack(
                id="track_video_1",
                kind="video",
                clips=[
                    TimelineClip(
                        id="clip_1",
                        source_url=request.input_urls[0] if request.input_urls else None,
                        start_seconds=0,
                        end_seconds=request.duration_seconds,
                        text=request.prompt,
                        kind="video",
                    )
                ],
            ),
            TimelineTrack(id="track_captions_1", kind="captions"),
            TimelineTrack(id="track_audio_1", kind="audio"),
        ],
    )


class VideoOSOrchestrator:
    def __init__(self, enabled: bool = False, provider: str = "mock") -> None:
        self.enabled = enabled
        self.provider_name = provider
        self.mock_provider = MockVideoProviderAdapter()

    def create_video_job(self, request: VideoJobRequest, user_id: str = "guest:unknown") -> VideoJob:
        validation_error = validate_video_job_request(request)
        if validation_error:
            return VideoJob(
                job_id=f"video_job_{uuid4().hex}",
                user_id=user_id,
                job_type=request.job_type,
                provider=self.provider_name,
                status=VideoJobStatus.FAILED,
                error_message=validation_error,
            )

        if not self.enabled:
            return VideoJob(
                job_id=f"video_job_{uuid4().hex}",
                user_id=user_id,
                job_type=request.job_type,
                provider=self.provider_name,
                status=VideoJobStatus.PROVIDER_NOT_CONFIGURED,
                prompt=request.prompt,
                input_urls=request.input_urls,
                source_asset_ids=request.source_asset_ids,
                aspect_ratio=request.aspect_ratio,
                duration_seconds=request.duration_seconds,
                resolution=request.resolution,
                style_preset=request.style_preset,
                cost_estimate_usd=estimate_video_job_cost(request),
                error_message="Video OS is disabled. Set LWA_VIDEO_OS_ENABLED=true to enable mock jobs.",
            )

        return self.mock_provider.create_job(request, user_id)

    def get_video_job(self, job_id: str) -> Optional[VideoJob]:
        return self.mock_provider.get_job(job_id)

    def list_video_jobs(self) -> List[VideoJob]:
        return list(self.mock_provider.jobs.values())

    def cancel_video_job(self, job_id: str) -> Optional[VideoJob]:
        return self.mock_provider.cancel_job(job_id)


def validate_video_job_request(request: VideoJobRequest) -> Optional[str]:
    allowed_aspect_ratios = {"9:16", "16:9", "1:1", "4:5"}
    allowed_resolutions = {"480p", "720p", "1080p"}

    if request.aspect_ratio not in allowed_aspect_ratios:
        return "unsupported_aspect_ratio"

    if request.resolution not in allowed_resolutions:
        return "unsupported_resolution"

    if request.duration_seconds < 1 or request.duration_seconds > 30:
        return "duration_out_of_range"

    if len(request.input_urls) > 10:
        return "too_many_inputs"

    return None


# Future provider adapters (placeholders for future implementation)
class SoraVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "sora"
    # TODO: Implement Sora API integration


class SeedanceVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "seedance"
    # TODO: Implement Seedance API integration


class RunwayVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "runway"
    # TODO: Implement Runway API integration


class VeoVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "veo"
    # TODO: Implement Veo API integration


class PikaVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "pika"
    # TODO: Implement Pika API integration


class LumaVideoProviderAdapter(VideoProviderAdapter):
    provider_name = "luma"
    # TODO: Implement Luma API integration


class ShotstackTimelineProviderAdapter(VideoProviderAdapter):
    provider_name = "shotstack"
    # TODO: Implement Shotstack timeline rendering


class RemotionRenderProviderAdapter(VideoProviderAdapter):
    provider_name = "remotion"
    # TODO: Implement Remotion rendering


class LocalFFmpegProviderAdapter(VideoProviderAdapter):
    provider_name = "ffmpeg"
    # TODO: Implement local FFmpeg rendering


class ElevenLabsAudioProviderAdapter(VideoProviderAdapter):
    provider_name = "elevenlabs"
    # TODO: Implement ElevenLabs audio generation
