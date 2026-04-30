from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ClipMomentCreateRequest(BaseModel):
    source_public_id: str
    transcript_public_id: Optional[str] = None
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float = Field(default=0, ge=0)
    transcript_excerpt: str = ""
    moment_type: str = "unknown"
    reason: str = ""
    confidence: int = Field(default=0, ge=0, le=100)


class ClipMomentResponse(BaseModel):
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: Optional[str]
    start_seconds: float
    end_seconds: float
    transcript_excerpt: str
    moment_type: str
    reason: str
    confidence: int
    created_at: str


class ClipCandidateCreateRequest(BaseModel):
    source_public_id: str
    transcript_public_id: Optional[str] = None
    moment_public_id: Optional[str] = None
    title: str = ""
    hook: str = ""
    caption: str = ""
    start_seconds: float = Field(default=0, ge=0)
    end_seconds: float = Field(default=0, ge=0)
    target_platform: str = "Multi"
    transcript_excerpt: str = ""


class ClipCandidateScoreRequest(BaseModel):
    clip_candidate_public_id: str
    transcript_excerpt: str = ""
    target_platform: str = "Multi"


class ClipCandidateResponse(BaseModel):
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: Optional[str]
    moment_public_id: Optional[str]
    title: str
    hook: str
    caption: str
    start_seconds: float
    end_seconds: float
    target_platform: str
    status: str
    score_total: int
    score_hook: int
    score_retention: int
    score_clarity: int
    score_emotion: int
    score_shareability: int
    score_platform_fit: int
    risk_notes: list[str]
    render_asset_public_id: Optional[str]
    created_at: str
    updated_at: str


class ClipPackCreateRequest(BaseModel):
    source_public_id: str
    transcript_public_id: Optional[str] = None
    title: str = "Untitled clip pack"
    target_platform: str = "Multi"
    desired_clip_count: int = Field(default=10, ge=1, le=100)


class ClipPackResponse(BaseModel):
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: Optional[str]
    title: str
    target_platform: str
    desired_clip_count: int
    status: str
    selected_candidate_ids: list[str]
    job_public_id: Optional[str]
    created_at: str
    updated_at: str


class ClipPackDetailResponse(BaseModel):
    pack: ClipPackResponse
    moments: list[ClipMomentResponse]
    candidates: list[ClipCandidateResponse]


class ClipRenderContractCreateRequest(BaseModel):
    clip_candidate_public_id: str
    source_public_id: str
    output_format: str = "mp4"
    aspect_ratio: str = "9:16"
    resolution: str = "1080x1920"
    remove_silence: bool = True
    captions_enabled: bool = True
    caption_style_json: str = "{}"
    music_enabled: bool = False
    music_policy: str = "none"
    intro_seconds: float = 0
    outro_seconds: float = 0


class ClipRenderContractResponse(BaseModel):
    public_id: str
    owner_user_id: str
    clip_candidate_public_id: str
    source_public_id: str
    output_format: str
    aspect_ratio: str
    resolution: str
    remove_silence: bool
    captions_enabled: bool
    caption_style_json: str
    music_enabled: bool
    music_policy: str
    intro_seconds: float
    outro_seconds: float
    render_job_public_id: Optional[str]
    created_at: str
