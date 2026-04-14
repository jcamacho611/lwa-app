from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, EmailStr, Field


PlanCode = Literal["free", "pro", "scale", "enterprise"]
UserRole = Literal["creator", "clipper", "admin"]
UploadStatus = Literal["uploaded", "ready", "processing", "failed"]
BatchStatus = Literal["queued", "processing", "completed", "failed"]
CampaignStatus = Literal["draft", "active", "paused", "completed", "archived"]
LedgerKind = Literal["credit", "debit", "hold", "release", "payout"]
PayoutStatus = Literal["pending", "approved", "sent", "failed", "rejected"]
PostStatus = Literal["draft", "queued", "scheduled", "published", "failed"]
SourceKind = Literal["url", "upload"]
PackagingAngle = Literal["shock", "story", "value", "controversy", "curiosity"]


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    display_name: Optional[str] = None
    plan_code: PlanCode = "free"
    role: UserRole = "creator"
    created_at: datetime


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class UploadAsset(BaseModel):
    id: str
    owner_user_id: str
    filename: str
    content_type: str
    size_bytes: int
    source_kind: SourceKind = "upload"
    storage_path: str
    public_url: Optional[str] = None
    status: UploadStatus = "uploaded"
    created_at: datetime


class SourceRef(BaseModel):
    source_kind: SourceKind
    video_url: Optional[str] = None
    upload_id: Optional[str] = None


class ClipEditState(BaseModel):
    clip_id: str
    trim_start_seconds: Optional[float] = None
    trim_end_seconds: Optional[float] = None
    caption_override: Optional[str] = None
    hook_override: Optional[str] = None
    cta_override: Optional[str] = None
    thumbnail_text_override: Optional[str] = None
    caption_style_override: Optional[str] = None
    packaging_angle_override: Optional[PackagingAngle] = None


class BatchCreateRequest(BaseModel):
    title: str
    target_platform: str
    selected_trend: Optional[str] = None
    sources: List[SourceRef] = Field(default_factory=list)


class BatchSummary(BaseModel):
    id: str
    owner_user_id: str
    title: str
    target_platform: str
    status: BatchStatus
    total_sources: int
    completed_sources: int
    failed_sources: int
    created_at: datetime


class CampaignRequirement(BaseModel):
    allowed_platforms: List[str] = Field(default_factory=list)
    min_duration_seconds: Optional[int] = None
    max_duration_seconds: Optional[int] = None
    disclosure_required: bool = False
    notes: Optional[str] = None


class CampaignSummary(BaseModel):
    id: str
    owner_user_id: str
    title: str
    description: Optional[str] = None
    status: CampaignStatus = "draft"
    payout_cents_per_1000_views: Optional[int] = None
    requirements: CampaignRequirement
    created_at: datetime


class WalletLedgerEntryResponse(BaseModel):
    id: str
    user_id: str
    kind: LedgerKind
    amount_cents: int
    currency: str = "USD"
    status: str
    description: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    created_at: datetime


class WalletSummary(BaseModel):
    pending_cents: int = 0
    available_cents: int = 0
    lifetime_cents: int = 0
    currency: str = "USD"
    recent_entries: List[WalletLedgerEntryResponse] = Field(default_factory=list)


class PayoutRequestResponse(BaseModel):
    id: str
    user_id: str
    amount_cents: int
    currency: str = "USD"
    status: PayoutStatus
    created_at: datetime


class PostingConnectionSummary(BaseModel):
    id: str
    user_id: str
    provider: str
    account_label: Optional[str] = None
    is_active: bool = True
    created_at: datetime


class ScheduledPostResponse(BaseModel):
    id: str
    owner_user_id: str
    provider: str
    status: PostStatus
    scheduled_for: Optional[datetime] = None
    clip_id: str
    caption: Optional[str] = None
    created_at: datetime
