from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CampaignStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    open = "open"
    in_progress = "in_progress"
    submitted = "submitted"
    under_review = "under_review"
    revision_requested = "revision_requested"
    completed = "completed"
    cancelled = "cancelled"
    disputed = "disputed"


class SubmissionStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"
    revision_requested = "revision_requested"
    paid = "paid"
    disputed = "disputed"


class EarningStatus(str, Enum):
    estimated = "estimated"
    pending_review = "pending_review"
    approved = "approved"
    payable = "payable"
    processing = "processing"
    paid = "paid"
    failed = "failed"
    held = "held"
    disputed = "disputed"
    refunded = "refunded"
    cancelled = "cancelled"


class EntitlementStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    expired = "expired"
    cancelled = "cancelled"
    past_due = "past_due"
    manual_review = "manual_review"


class EntitlementSource(str, Enum):
    manual = "manual"
    whop = "whop"
    stripe = "stripe"
    apple = "apple"
    demo = "demo"


class CreditTransactionType(str, Enum):
    grant = "grant"
    spend = "spend"
    refund = "refund"
    adjustment = "adjustment"


class UsageEventStatus(str, Enum):
    recorded = "recorded"
    reversed = "reversed"
    failed = "failed"


class PayoutPlaceholderStatus(str, Enum):
    requested = "requested"
    pending_review = "pending_review"
    blocked = "blocked"
    held = "held"
    cancelled = "cancelled"


class WebhookProvider(str, Enum):
    whop = "whop"
    stripe = "stripe"
    apple = "apple"
    manual = "manual"


class JobType(str, Enum):
    upload_processing = "upload_processing"
    transcript_generation = "transcript_generation"
    ai_clip_score = "ai_clip_score"
    clip_generation = "clip_generation"
    render_generation = "render_generation"
    caption_generation = "caption_generation"
    ugc_moderation_scan = "ugc_moderation_scan"
    campaign_pack_generation = "campaign_pack_generation"
    social_import = "social_import"
    trend_import = "trend_import"


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    waiting = "waiting"
    succeeded = "succeeded"
    failed = "failed"
    cancelled = "cancelled"
    retrying = "retrying"
    expired = "expired"


class JobPriority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class ClipCandidateStatus(str, Enum):
    draft = "draft"
    scored = "scored"
    selected = "selected"
    rejected = "rejected"
    render_queued = "render_queued"
    rendered = "rendered"
    failed = "failed"


class ClipPackStatus(str, Enum):
    draft = "draft"
    detecting_moments = "detecting_moments"
    scoring = "scoring"
    ready_for_review = "ready_for_review"
    rendering = "rendering"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class LedgerEventType(str, Enum):
    credit_granted = "credit_granted"
    credit_spent = "credit_spent"
    clip_generated = "clip_generated"
    campaign_created = "campaign_created"
    submission_created = "submission_created"
    submission_approved = "submission_approved"
    submission_rejected = "submission_rejected"
    revision_requested = "revision_requested"
    earning_estimated = "earning_estimated"
    earning_pending = "earning_pending"
    earning_approved = "earning_approved"
    earning_paid = "earning_paid"
    platform_fee_collected = "platform_fee_collected"
    xp_awarded = "xp_awarded"
    badge_awarded = "badge_awarded"
    reputation_awarded = "reputation_awarded"
    reputation_penalized = "reputation_penalized"
    dispute_opened = "dispute_opened"
    dispute_resolved = "dispute_resolved"
    refund_created = "refund_created"
    wallet_connected_placeholder = "wallet_connected_placeholder"
    collectible_awarded_placeholder = "collectible_awarded_placeholder"


class UGCAssetStatus(str, Enum):
    draft = "draft"
    pending_review = "pending_review"
    approved = "approved"
    rejected = "rejected"
    removed = "removed"
    disputed = "disputed"


class ModerationStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    flagged = "flagged"
    escalated = "escalated"
    removed = "removed"
    appealed = "appealed"


class FraudFlagStatus(str, Enum):
    open = "open"
    in_review = "in_review"
    cleared = "cleared"
    confirmed = "confirmed"
    escalated = "escalated"


class ContentRightsClaimStatus(str, Enum):
    open = "open"
    in_review = "in_review"
    information_requested = "information_requested"
    resolved = "resolved"
    rejected = "rejected"
    escalated = "escalated"


@dataclass(slots=True)
class MarketplaceCampaign:
    public_id: str
    title: str
    description: str
    buyer_user_id: str | None = None
    target_platform: str = "Multi"
    source_type: str = "video_url"
    budget_amount: int = 0
    currency: str = "USD"
    platform_fee_percent: int = 20
    clip_count: int = 1
    deadline: str | None = None
    status: CampaignStatus = CampaignStatus.draft
    rights_required: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class CampaignSubmission:
    public_id: str
    campaign_public_id: str
    title: str
    clipper_user_id: str | None = None
    hook: str = ""
    caption: str = ""
    asset_url: str | None = None
    status: SubmissionStatus = SubmissionStatus.draft
    estimated_earnings_amount: int = 0
    currency: str = "USD"
    review_note: str | None = None
    rights_confirmed: bool = False
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class UserEntitlement:
    user_id: str
    plan_key: str = "free"
    status: EntitlementStatus = EntitlementStatus.active
    source: EntitlementSource = EntitlementSource.demo
    source_reference_id: str | None = None
    current_period_start: str | None = None
    current_period_end: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class CreditBalance:
    user_id: str
    balance: int = 0
    monthly_grant: int = 0
    used_this_period: int = 0
    period_start: str | None = None
    period_end: str | None = None
    updated_at: str = ""


@dataclass(slots=True)
class CreditTransaction:
    public_id: str
    user_id: str
    transaction_type: CreditTransactionType
    amount: int
    balance_after: int
    reason: str = ""
    source_type: str | None = None
    source_public_id: str | None = None
    created_at: str = ""


@dataclass(slots=True)
class UsageEvent:
    public_id: str
    user_id: str
    feature_key: str
    amount: int = 1
    status: UsageEventStatus = UsageEventStatus.recorded
    source_type: str | None = None
    source_public_id: str | None = None
    created_at: str = ""


@dataclass(slots=True)
class EarningsAccount:
    user_id: str
    estimated_amount: int = 0
    pending_review_amount: int = 0
    approved_amount: int = 0
    payable_amount: int = 0
    paid_amount: int = 0
    held_amount: int = 0
    currency: str = "USD"
    updated_at: str = ""


@dataclass(slots=True)
class EarningEvent:
    public_id: str
    user_id: str
    source_type: str
    amount: int
    platform_fee_amount: int = 0
    net_amount: int = 0
    source_public_id: str | None = None
    currency: str = "USD"
    status: EarningStatus = EarningStatus.estimated
    note: str = ""
    created_at: str = ""


@dataclass(slots=True)
class PayoutPlaceholder:
    public_id: str
    user_id: str
    amount: int
    currency: str = "USD"
    status: PayoutPlaceholderStatus = PayoutPlaceholderStatus.pending_review
    blocked_reason: str = "Real payouts are not enabled yet."
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class WebhookEvent:
    public_id: str
    provider: WebhookProvider
    event_type: str
    external_event_id: str | None = None
    processed: bool = False
    status: str = "received"
    note: str = ""
    created_at: str = ""
    processed_at: str | None = None


@dataclass(slots=True)
class WorldJob:
    public_id: str
    owner_user_id: str | None
    job_type: JobType
    status: JobStatus = JobStatus.queued
    priority: JobPriority = JobPriority.normal
    progress_percent: int = 0
    title: str = ""
    description: str = ""
    source_public_id: str | None = None
    target_type: str | None = None
    target_public_id: str | None = None
    input_json: str = "{}"
    output_json: str = "{}"
    error_message: str | None = None
    max_attempts: int = 3
    attempt_count: int = 0
    next_retry_at: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class WorldJobEvent:
    public_id: str
    job_public_id: str
    event_type: str
    message: str
    status_before: str | None = None
    status_after: str | None = None
    progress_percent: int | None = None
    metadata_json: str = "{}"
    created_at: str = ""


@dataclass(slots=True)
class WorldJobAttempt:
    public_id: str
    job_public_id: str
    attempt_number: int
    worker_name: str | None = None
    status: JobStatus = JobStatus.running
    error_message: str | None = None
    started_at: str = ""
    completed_at: str | None = None


@dataclass(slots=True)
class ClipMomentRecord:
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: str | None = None
    start_seconds: float = 0.0
    end_seconds: float = 0.0
    transcript_excerpt: str = ""
    moment_type: str = "unknown"
    reason: str = ""
    confidence: int = 0
    created_at: str = ""


@dataclass(slots=True)
class ClipCandidateRecord:
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: str | None = None
    moment_public_id: str | None = None
    title: str = ""
    hook: str = ""
    caption: str = ""
    start_seconds: float = 0.0
    end_seconds: float = 0.0
    target_platform: str = "Multi"
    status: ClipCandidateStatus = ClipCandidateStatus.draft
    score_total: int = 0
    score_hook: int = 0
    score_retention: int = 0
    score_clarity: int = 0
    score_emotion: int = 0
    score_shareability: int = 0
    score_platform_fit: int = 0
    risk_notes_json: str = "[]"
    render_asset_public_id: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class ClipPackRecord:
    public_id: str
    owner_user_id: str
    source_public_id: str
    transcript_public_id: str | None = None
    title: str = ""
    target_platform: str = "Multi"
    desired_clip_count: int = 10
    status: ClipPackStatus = ClipPackStatus.draft
    selected_candidate_ids_json: str = "[]"
    job_public_id: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class ClipRenderContract:
    public_id: str
    owner_user_id: str
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
    intro_seconds: float = 0.0
    outro_seconds: float = 0.0
    render_job_public_id: str | None = None
    created_at: str = ""


@dataclass(slots=True)
class UserWorldProfile:
    user_id: str
    display_name: str
    class_name: str = "Signalwright"
    faction: str = "The Signalwrights"
    level: int = 1
    xp: int = 0
    next_level_xp: int = 100
    creator_reputation: int = 0
    clipper_reputation: int = 0
    marketplace_reputation: int = 0
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class Badge:
    public_id: str
    name: str
    tier: str = "common"
    description: str = ""
    lore: str = ""
    created_at: str = ""


@dataclass(slots=True)
class UserBadge:
    user_id: str
    badge_public_id: str
    unlocked_at: str = ""


@dataclass(slots=True)
class UGCAsset:
    public_id: str
    creator_user_id: str
    title: str
    asset_type: str
    description: str
    price_amount: int = 0
    currency: str = "USD"
    status: UGCAssetStatus = UGCAssetStatus.draft
    moderation_status: ModerationStatus = ModerationStatus.pending
    rights_confirmed: bool = False
    license_summary: str = ""
    preview_url: str | None = None
    created_at: str = ""
    updated_at: str = ""


@dataclass(slots=True)
class ModerationQueueItem:
    public_id: str
    target_type: str
    target_public_id: str
    submitted_by_user_id: str | None = None
    status: ModerationStatus = ModerationStatus.pending
    reason: str = ""
    automated_score: int | None = None
    reviewer_user_id: str | None = None
    reviewer_note: str | None = None
    created_at: str = ""
    reviewed_at: str | None = None


@dataclass(slots=True)
class FraudFlag:
    public_id: str
    target_type: str
    flag_type: str
    user_id: str | None = None
    target_public_id: str | None = None
    status: FraudFlagStatus = FraudFlagStatus.open
    severity: str = "medium"
    evidence: str = ""
    reviewer_user_id: str | None = None
    reviewer_note: str | None = None
    created_at: str = ""
    resolved_at: str | None = None


@dataclass(slots=True)
class ContentRightsClaim:
    public_id: str
    claimant_name: str
    claimant_email: str
    target_type: str
    target_public_id: str
    claim_summary: str
    status: ContentRightsClaimStatus = ContentRightsClaimStatus.open
    admin_note: str | None = None
    created_at: str = ""
    resolved_at: str | None = None


@dataclass(slots=True)
class Relic:
    public_id: str
    name: str
    tier: str = "common"
    description: str = ""
    lore: str = ""
    future_collectible_eligible: bool = False
    created_at: str = ""


@dataclass(slots=True)
class UserRelic:
    user_id: str
    relic_public_id: str
    unlocked_at: str = ""


@dataclass(slots=True)
class UserTitle:
    user_id: str
    title: str
    unlocked_at: str = ""


@dataclass(slots=True)
class Quest:
    public_id: str
    title: str
    description: str
    category: str = "clipping"
    goal: int = 1
    reward_xp: int = 0
    reward_badge_public_id: str | None = None
    active: bool = True
    created_at: str = ""


@dataclass(slots=True)
class QuestCompletion:
    quest_public_id: str
    user_id: str
    progress: int = 0
    status: str = "in_progress"
    completed_at: str | None = None
    claimed_at: str | None = None


@dataclass(slots=True)
class InternalLedgerEntry:
    public_id: str
    event_type: LedgerEventType
    label: str
    user_id: str | None = None
    amount: int | None = None
    currency: str = "USD"
    xp: int | None = None
    reputation: int | None = None
    status: str = "recorded"
    reference_id: str | None = None
    created_at: str = ""


@dataclass(slots=True)
class ApiIntegrationStatus:
    integration_key: str
    name: str
    category: str
    status: str = "not_configured"
    description: str = ""
    admin_only: bool = False
    updated_at: str = ""


@dataclass(slots=True)
class IntegrationRequirement:
    integration_key: str
    env_var: str
    required_for_mvp: bool = False
    created_at: str = ""


@dataclass(slots=True)
class ReputationEvent:
    public_id: str
    user_id: str
    source_type: str
    reason: str
    source_public_id: str | None = None
    xp: int = 0
    creator_reputation: int = 0
    clipper_reputation: int = 0
    marketplace_reputation: int = 0
    created_at: str = ""


@dataclass(slots=True)
class AdminAuditAction:
    public_id: str
    action_type: str
    target_type: str
    actor_user_id: str | None = None
    target_public_id: str | None = None
    before_state: str | None = None
    after_state: str | None = None
    note: str | None = None
    created_at: str = ""
