from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class MoneyResponse(BaseModel):
    amount: int
    currency: str = "USD"


class BillingPlanResponse(BaseModel):
    plan_key: str
    name: str
    monthly_price_amount: int
    currency: str
    monthly_credits: int
    marketplace_fee_percent: int
    max_campaigns: int
    max_ugc_assets: int
    features: list[str] = Field(default_factory=list)


class UserEntitlementResponse(BaseModel):
    user_id: str
    plan_key: str
    status: str
    source: str
    source_reference_id: Optional[str]
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    created_at: str
    updated_at: str


class EntitlementGrantRequest(BaseModel):
    user_id: str = Field(min_length=1)
    plan_key: str = Field(min_length=1)
    source: str = "manual"
    source_reference_id: Optional[str] = None
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    reason: str = ""


class CreditBalanceResponse(BaseModel):
    user_id: str
    balance: int
    monthly_grant: int
    used_this_period: int
    period_start: Optional[str]
    period_end: Optional[str]
    updated_at: str


class CreditGrantRequest(BaseModel):
    user_id: str = Field(min_length=1)
    amount: int = Field(gt=0)
    reason: str = "Manual credit grant."


class CreditSpendRequest(BaseModel):
    amount: int = Field(gt=0)
    feature_key: str = Field(min_length=1)
    reason: str = "Credit spend."
    source_type: Optional[str] = None
    source_public_id: Optional[str] = None


class CreditTransactionResponse(BaseModel):
    public_id: str
    user_id: str
    transaction_type: str
    amount: int
    balance_after: int
    reason: str
    source_type: Optional[str]
    source_public_id: Optional[str]
    created_at: str


class MarketplaceFeeQuoteRequest(BaseModel):
    gross_amount: int = Field(gt=0)
    plan_key: str = "free"


class MarketplaceFeeQuoteResponse(BaseModel):
    gross_amount: int
    platform_fee_percent: int
    platform_fee_amount: int
    net_amount: int
    currency: str = "USD"
    note: str


class EarningsAccountResponse(BaseModel):
    user_id: str
    estimated_amount: int
    pending_review_amount: int
    approved_amount: int
    payable_amount: int
    paid_amount: int
    held_amount: int
    currency: str
    updated_at: str


class EarningEventResponse(BaseModel):
    public_id: str
    user_id: str
    source_type: str
    source_public_id: Optional[str]
    amount: int
    platform_fee_amount: int
    net_amount: int
    currency: str
    status: str
    note: str
    created_at: str


class PayoutPlaceholderCreateRequest(BaseModel):
    amount: int = Field(gt=0)
    reason: str = "Payout placeholder requested."


class PayoutPlaceholderResponse(BaseModel):
    public_id: str
    user_id: str
    amount: int
    currency: str
    status: str
    blocked_reason: str
    created_at: str
    updated_at: str


class StripeConnectReadinessResponse(BaseModel):
    enabled: bool
    ready: bool
    required_env_vars: list[str]
    missing_env_vars: list[str]
    blockers: list[str]
    note: str


class GateCheckResponse(BaseModel):
    allowed: bool
    plan_key: str
    required_plan: str
    reason: str


class CampaignCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    target_platform: str = "Multi"
    source_type: str = "video_url"
    budget_amount: int
    clip_count: int = 1
    deadline: Optional[str] = None
    requirements: list[str] = Field(default_factory=list)
    rights_required: str = ""


class CampaignResponse(BaseModel):
    public_id: str
    title: str
    description: str
    target_platform: str
    source_type: str
    budget: MoneyResponse
    platform_fee_percent: int
    clip_count: int
    deadline: Optional[str]
    status: str
    rights_required: str
    created_at: str


class SubmissionCreateRequest(BaseModel):
    campaign_public_id: str
    title: str = Field(min_length=1)
    hook: str = ""
    caption: str = ""
    asset_url: Optional[str] = None
    estimated_earnings_amount: int = 0
    rights_confirmed: bool


class SubmissionReviewRequest(BaseModel):
    action: str
    review_note: Optional[str] = None


class UGCAssetCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    asset_type: str = Field(min_length=1)
    description: str = Field(min_length=1)
    price_amount: int = 0
    license_summary: str = ""
    preview_url: Optional[str] = None
    rights_confirmed: bool


class UGCAssetReviewRequest(BaseModel):
    action: str
    reviewer_note: Optional[str] = None


class ModerationReviewRequest(BaseModel):
    action: str
    reviewer_note: Optional[str] = None


class FraudFlagCreateRequest(BaseModel):
    user_id: Optional[str] = None
    target_type: str = Field(min_length=1)
    target_public_id: Optional[str] = None
    flag_type: str = Field(min_length=1)
    severity: str = "medium"
    evidence: str = ""


class FraudFlagReviewRequest(BaseModel):
    action: str
    reviewer_note: Optional[str] = None


class ContentRightsClaimCreateRequest(BaseModel):
    claimant_name: str = Field(min_length=1)
    claimant_email: str = Field(min_length=3)
    target_type: str = Field(min_length=1)
    target_public_id: str = Field(min_length=1)
    claim_summary: str = Field(min_length=1)


class ContentRightsClaimReviewRequest(BaseModel):
    action: str
    admin_note: Optional[str] = None


class SubmissionResponse(BaseModel):
    public_id: str
    campaign_public_id: str
    title: str
    hook: str
    caption: str
    asset_url: Optional[str]
    status: str
    estimated_earnings: MoneyResponse
    review_note: Optional[str]
    rights_confirmed: bool
    created_at: str


class UGCAssetResponse(BaseModel):
    public_id: str
    creator_user_id: str
    title: str
    asset_type: str
    description: str
    price_amount: int
    currency: str
    status: str
    moderation_status: str
    rights_confirmed: bool
    license_summary: str
    preview_url: Optional[str]
    created_at: str


class ModerationQueueItemResponse(BaseModel):
    public_id: str
    target_type: str
    target_public_id: str
    submitted_by_user_id: Optional[str]
    status: str
    reason: str
    automated_score: Optional[int]
    reviewer_user_id: Optional[str]
    reviewer_note: Optional[str]
    created_at: str
    reviewed_at: Optional[str]


class FraudFlagResponse(BaseModel):
    public_id: str
    user_id: Optional[str]
    target_type: str
    target_public_id: Optional[str]
    flag_type: str
    status: str
    severity: str
    evidence: str
    reviewer_user_id: Optional[str]
    reviewer_note: Optional[str]
    created_at: str
    resolved_at: Optional[str]


class ContentRightsClaimResponse(BaseModel):
    public_id: str
    claimant_name: str
    claimant_email: str
    target_type: str
    target_public_id: str
    claim_summary: str
    status: str
    admin_note: Optional[str]
    created_at: str
    resolved_at: Optional[str]


class BadgeResponse(BaseModel):
    public_id: str
    name: str
    tier: str
    description: str
    lore: str
    created_at: str


class UserBadgeResponse(BaseModel):
    badge_public_id: str
    name: str
    tier: str
    description: str
    lore: str
    unlocked_at: str


class RelicResponse(BaseModel):
    public_id: str
    name: str
    tier: str
    description: str
    lore: str
    future_collectible_eligible: bool
    created_at: str


class UserRelicResponse(BaseModel):
    relic_public_id: str
    name: str
    tier: str
    description: str
    lore: str
    future_collectible_eligible: bool
    unlocked_at: str


class QuestResponse(BaseModel):
    public_id: str
    title: str
    description: str
    category: str
    goal: int
    reward_xp: int
    reward_badge_public_id: Optional[str]
    active: bool


class QuestCompletionResponse(BaseModel):
    quest_public_id: str
    user_id: str
    progress: int
    status: str
    completed_at: Optional[str]
    claimed_at: Optional[str]


class WorldProfileResponse(BaseModel):
    user_id: str
    display_name: str
    class_name: str
    faction: str
    level: int
    xp: int
    next_level_xp: int
    creator_reputation: int
    clipper_reputation: int
    marketplace_reputation: int


class RichWorldProfileResponse(WorldProfileResponse):
    badges: list[UserBadgeResponse] = Field(default_factory=list)
    relics: list[UserRelicResponse] = Field(default_factory=list)
    titles: list[str] = Field(default_factory=list)
    quests: list[QuestCompletionResponse] = Field(default_factory=list)


class LedgerEntryResponse(BaseModel):
    public_id: str
    user_id: Optional[str]
    event_type: str
    label: str
    amount: Optional[int]
    currency: str
    xp: Optional[int]
    reputation: Optional[int]
    status: str
    reference_id: Optional[str]
    created_at: str


class IntegrationStatusResponse(BaseModel):
    integration_key: str
    name: str
    category: str
    status: str
    description: str
    admin_only: bool


class AdminAuditActionResponse(BaseModel):
    public_id: str
    actor_user_id: Optional[str]
    action_type: str
    target_type: str
    target_public_id: Optional[str]
    before_state: Optional[str]
    after_state: Optional[str]
    note: Optional[str]
    created_at: str
