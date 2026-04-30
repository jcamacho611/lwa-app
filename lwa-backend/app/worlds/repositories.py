from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from threading import Lock
from typing import Iterator, Optional

from .models import (
    AdminAuditAction,
    ApiIntegrationStatus,
    Badge,
    CampaignStatus,
    CampaignSubmission,
    ClipCandidateRecord,
    ClipCandidateStatus,
    ClipMomentRecord,
    ClipPackRecord,
    ClipPackStatus,
    ClipRenderContract,
    ContentRightsClaim,
    ContentRightsClaimStatus,
    CreditBalance,
    CreditTransaction,
    CreditTransactionType,
    EarningStatus,
    EarningEvent,
    EarningsAccount,
    EntitlementSource,
    EntitlementStatus,
    FraudFlag,
    FraudFlagStatus,
    InternalLedgerEntry,
    JobPriority,
    JobStatus,
    JobType,
    LedgerEventType,
    MarketplaceCampaign,
    ModerationQueueItem,
    ModerationStatus,
    PayoutPlaceholder,
    PayoutPlaceholderStatus,
    Quest,
    QuestCompletion,
    ReputationEvent,
    Relic,
    SubmissionStatus,
    UGCAsset,
    UGCAssetStatus,
    UsageEvent,
    UsageEventStatus,
    UserEntitlement,
    UserBadge,
    UserRelic,
    UserTitle,
    UserWorldProfile,
    WebhookEvent,
    WebhookProvider,
    WorldJob,
    WorldJobAttempt,
    WorldJobEvent,
)


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _campaign_status(value: str) -> CampaignStatus:
    try:
        return CampaignStatus(value)
    except ValueError:
        return CampaignStatus.draft


def _submission_status(value: str) -> SubmissionStatus:
    try:
        return SubmissionStatus(value)
    except ValueError:
        return SubmissionStatus.draft


def _ledger_event_type(value: str) -> LedgerEventType:
    try:
        return LedgerEventType(value)
    except ValueError:
        return LedgerEventType.clip_generated


def _ugc_asset_status(value: str) -> UGCAssetStatus:
    try:
        return UGCAssetStatus(value)
    except ValueError:
        return UGCAssetStatus.draft


def _moderation_status(value: str) -> ModerationStatus:
    try:
        return ModerationStatus(value)
    except ValueError:
        return ModerationStatus.pending


def _fraud_flag_status(value: str) -> FraudFlagStatus:
    try:
        return FraudFlagStatus(value)
    except ValueError:
        return FraudFlagStatus.open


def _rights_claim_status(value: str) -> ContentRightsClaimStatus:
    try:
        return ContentRightsClaimStatus(value)
    except ValueError:
        return ContentRightsClaimStatus.open


def _entitlement_status(value: str) -> EntitlementStatus:
    try:
        return EntitlementStatus(value)
    except ValueError:
        return EntitlementStatus.active


def _entitlement_source(value: str) -> EntitlementSource:
    try:
        return EntitlementSource(value)
    except ValueError:
        return EntitlementSource.demo


def _credit_transaction_type(value: str) -> CreditTransactionType:
    try:
        return CreditTransactionType(value)
    except ValueError:
        return CreditTransactionType.adjustment


def _usage_event_status(value: str) -> UsageEventStatus:
    try:
        return UsageEventStatus(value)
    except ValueError:
        return UsageEventStatus.recorded


def _payout_placeholder_status(value: str) -> PayoutPlaceholderStatus:
    try:
        return PayoutPlaceholderStatus(value)
    except ValueError:
        return PayoutPlaceholderStatus.pending_review


def _webhook_provider(value: str) -> WebhookProvider:
    try:
        return WebhookProvider(value)
    except ValueError:
        return WebhookProvider.manual


def _earning_status(value: str) -> EarningStatus:
    try:
        return EarningStatus(value)
    except ValueError:
        return EarningStatus.estimated


def _job_type(value: str) -> JobType:
    try:
        return JobType(value)
    except ValueError:
        return JobType.clip_generation


def _job_status(value: str) -> JobStatus:
    try:
        return JobStatus(value)
    except ValueError:
        return JobStatus.queued


def _job_priority(value: str) -> JobPriority:
    try:
        return JobPriority(value)
    except ValueError:
        return JobPriority.normal


def _clip_candidate_status(value: str) -> ClipCandidateStatus:
    try:
        return ClipCandidateStatus(value)
    except ValueError:
        return ClipCandidateStatus.draft


def _clip_pack_status(value: str) -> ClipPackStatus:
    try:
        return ClipPackStatus(value)
    except ValueError:
        return ClipPackStatus.draft


class WorldsStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init_db(self) -> None:
        with self._lock, self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS marketplace_campaigns (
                    public_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    buyer_user_id TEXT,
                    target_platform TEXT NOT NULL DEFAULT 'Multi',
                    source_type TEXT NOT NULL DEFAULT 'video_url',
                    budget_amount INTEGER NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    platform_fee_percent INTEGER NOT NULL DEFAULT 20,
                    clip_count INTEGER NOT NULL DEFAULT 1,
                    deadline TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    rights_required TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS campaign_submissions (
                    public_id TEXT PRIMARY KEY,
                    campaign_public_id TEXT NOT NULL,
                    clipper_user_id TEXT,
                    title TEXT NOT NULL,
                    hook TEXT NOT NULL DEFAULT '',
                    caption TEXT NOT NULL DEFAULT '',
                    asset_url TEXT,
                    status TEXT NOT NULL DEFAULT 'draft',
                    estimated_earnings_amount INTEGER NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    review_note TEXT,
                    rights_confirmed INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_entitlements (
                    user_id TEXT PRIMARY KEY,
                    plan_key TEXT NOT NULL DEFAULT 'free',
                    status TEXT NOT NULL DEFAULT 'active',
                    source TEXT NOT NULL DEFAULT 'demo',
                    source_reference_id TEXT,
                    current_period_start TEXT,
                    current_period_end TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS credit_balances (
                    user_id TEXT PRIMARY KEY,
                    balance INTEGER NOT NULL DEFAULT 0,
                    monthly_grant INTEGER NOT NULL DEFAULT 0,
                    used_this_period INTEGER NOT NULL DEFAULT 0,
                    period_start TEXT,
                    period_end TEXT,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS credit_transactions (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    balance_after INTEGER NOT NULL,
                    reason TEXT NOT NULL DEFAULT '',
                    source_type TEXT,
                    source_public_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS usage_events (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    feature_key TEXT NOT NULL,
                    amount INTEGER NOT NULL DEFAULT 1,
                    status TEXT NOT NULL DEFAULT 'recorded',
                    source_type TEXT,
                    source_public_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS earnings_accounts (
                    user_id TEXT PRIMARY KEY,
                    estimated_amount INTEGER NOT NULL DEFAULT 0,
                    pending_review_amount INTEGER NOT NULL DEFAULT 0,
                    approved_amount INTEGER NOT NULL DEFAULT 0,
                    payable_amount INTEGER NOT NULL DEFAULT 0,
                    paid_amount INTEGER NOT NULL DEFAULT 0,
                    held_amount INTEGER NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS earning_events (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_public_id TEXT,
                    amount INTEGER NOT NULL,
                    platform_fee_amount INTEGER NOT NULL DEFAULT 0,
                    net_amount INTEGER NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    status TEXT NOT NULL DEFAULT 'estimated',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS payout_placeholders (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    status TEXT NOT NULL DEFAULT 'pending_review',
                    blocked_reason TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS webhook_events (
                    public_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    external_event_id TEXT,
                    event_type TEXT NOT NULL,
                    processed INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'received',
                    note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    processed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS world_jobs (
                    public_id TEXT PRIMARY KEY,
                    owner_user_id TEXT,
                    job_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    priority TEXT NOT NULL DEFAULT 'normal',
                    progress_percent INTEGER NOT NULL DEFAULT 0,
                    title TEXT NOT NULL DEFAULT '',
                    description TEXT NOT NULL DEFAULT '',
                    source_public_id TEXT,
                    target_type TEXT,
                    target_public_id TEXT,
                    input_json TEXT NOT NULL DEFAULT '{}',
                    output_json TEXT NOT NULL DEFAULT '{}',
                    error_message TEXT,
                    max_attempts INTEGER NOT NULL DEFAULT 3,
                    attempt_count INTEGER NOT NULL DEFAULT 0,
                    next_retry_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS world_job_events (
                    public_id TEXT PRIMARY KEY,
                    job_public_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status_before TEXT,
                    status_after TEXT,
                    progress_percent INTEGER,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS world_job_attempts (
                    public_id TEXT PRIMARY KEY,
                    job_public_id TEXT NOT NULL,
                    attempt_number INTEGER NOT NULL,
                    worker_name TEXT,
                    status TEXT NOT NULL DEFAULT 'running',
                    error_message TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS clip_moments (
                    public_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    source_public_id TEXT NOT NULL,
                    transcript_public_id TEXT,
                    start_seconds REAL NOT NULL DEFAULT 0,
                    end_seconds REAL NOT NULL DEFAULT 0,
                    transcript_excerpt TEXT NOT NULL DEFAULT '',
                    moment_type TEXT NOT NULL DEFAULT 'unknown',
                    reason TEXT NOT NULL DEFAULT '',
                    confidence INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clip_candidates (
                    public_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    source_public_id TEXT NOT NULL,
                    transcript_public_id TEXT,
                    moment_public_id TEXT,
                    title TEXT NOT NULL DEFAULT '',
                    hook TEXT NOT NULL DEFAULT '',
                    caption TEXT NOT NULL DEFAULT '',
                    start_seconds REAL NOT NULL DEFAULT 0,
                    end_seconds REAL NOT NULL DEFAULT 0,
                    target_platform TEXT NOT NULL DEFAULT 'Multi',
                    status TEXT NOT NULL DEFAULT 'draft',
                    score_total INTEGER NOT NULL DEFAULT 0,
                    score_hook INTEGER NOT NULL DEFAULT 0,
                    score_retention INTEGER NOT NULL DEFAULT 0,
                    score_clarity INTEGER NOT NULL DEFAULT 0,
                    score_emotion INTEGER NOT NULL DEFAULT 0,
                    score_shareability INTEGER NOT NULL DEFAULT 0,
                    score_platform_fit INTEGER NOT NULL DEFAULT 0,
                    risk_notes_json TEXT NOT NULL DEFAULT '[]',
                    render_asset_public_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clip_packs (
                    public_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    source_public_id TEXT NOT NULL,
                    transcript_public_id TEXT,
                    title TEXT NOT NULL DEFAULT '',
                    target_platform TEXT NOT NULL DEFAULT 'Multi',
                    desired_clip_count INTEGER NOT NULL DEFAULT 10,
                    status TEXT NOT NULL DEFAULT 'draft',
                    selected_candidate_ids_json TEXT NOT NULL DEFAULT '[]',
                    job_public_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clip_render_contracts (
                    public_id TEXT PRIMARY KEY,
                    owner_user_id TEXT NOT NULL,
                    clip_candidate_public_id TEXT NOT NULL,
                    source_public_id TEXT NOT NULL,
                    output_format TEXT NOT NULL DEFAULT 'mp4',
                    aspect_ratio TEXT NOT NULL DEFAULT '9:16',
                    resolution TEXT NOT NULL DEFAULT '1080x1920',
                    remove_silence INTEGER NOT NULL DEFAULT 1,
                    captions_enabled INTEGER NOT NULL DEFAULT 1,
                    caption_style_json TEXT NOT NULL DEFAULT '{}',
                    music_enabled INTEGER NOT NULL DEFAULT 0,
                    music_policy TEXT NOT NULL DEFAULT 'none',
                    intro_seconds REAL NOT NULL DEFAULT 0,
                    outro_seconds REAL NOT NULL DEFAULT 0,
                    render_job_public_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_world_profiles (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    class_name TEXT NOT NULL DEFAULT 'Signalwright',
                    faction TEXT NOT NULL DEFAULT 'The Signalwrights',
                    level INTEGER NOT NULL DEFAULT 1,
                    xp INTEGER NOT NULL DEFAULT 0,
                    next_level_xp INTEGER NOT NULL DEFAULT 100,
                    creator_reputation INTEGER NOT NULL DEFAULT 0,
                    clipper_reputation INTEGER NOT NULL DEFAULT 0,
                    marketplace_reputation INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS badges (
                    public_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tier TEXT NOT NULL DEFAULT 'common',
                    description TEXT NOT NULL DEFAULT '',
                    lore TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_badges (
                    user_id TEXT NOT NULL,
                    badge_public_id TEXT NOT NULL,
                    unlocked_at TEXT NOT NULL,
                    UNIQUE(user_id, badge_public_id)
                );

                CREATE TABLE IF NOT EXISTS ugc_assets (
                    public_id TEXT PRIMARY KEY,
                    creator_user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    price_amount INTEGER NOT NULL DEFAULT 0,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    status TEXT NOT NULL DEFAULT 'draft',
                    moderation_status TEXT NOT NULL DEFAULT 'pending',
                    rights_confirmed INTEGER NOT NULL DEFAULT 0,
                    license_summary TEXT NOT NULL DEFAULT '',
                    preview_url TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS moderation_queue_items (
                    public_id TEXT PRIMARY KEY,
                    target_type TEXT NOT NULL,
                    target_public_id TEXT NOT NULL,
                    submitted_by_user_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    reason TEXT NOT NULL DEFAULT '',
                    automated_score INTEGER,
                    reviewer_user_id TEXT,
                    reviewer_note TEXT,
                    created_at TEXT NOT NULL,
                    reviewed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS fraud_flags (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    target_type TEXT NOT NULL,
                    target_public_id TEXT,
                    flag_type TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    severity TEXT NOT NULL DEFAULT 'medium',
                    evidence TEXT NOT NULL DEFAULT '',
                    reviewer_user_id TEXT,
                    reviewer_note TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS content_rights_claims (
                    public_id TEXT PRIMARY KEY,
                    claimant_name TEXT NOT NULL,
                    claimant_email TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_public_id TEXT NOT NULL,
                    claim_summary TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    admin_note TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS relics (
                    public_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tier TEXT NOT NULL DEFAULT 'common',
                    description TEXT NOT NULL DEFAULT '',
                    lore TEXT NOT NULL DEFAULT '',
                    future_collectible_eligible INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_relics (
                    user_id TEXT NOT NULL,
                    relic_public_id TEXT NOT NULL,
                    unlocked_at TEXT NOT NULL,
                    UNIQUE(user_id, relic_public_id)
                );

                CREATE TABLE IF NOT EXISTS user_titles (
                    user_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    unlocked_at TEXT NOT NULL,
                    UNIQUE(user_id, title)
                );

                CREATE TABLE IF NOT EXISTS quests (
                    public_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'clipping',
                    goal INTEGER NOT NULL DEFAULT 1,
                    reward_xp INTEGER NOT NULL DEFAULT 0,
                    reward_badge_public_id TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS quest_completions (
                    quest_public_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    progress INTEGER NOT NULL DEFAULT 0,
                    status TEXT NOT NULL DEFAULT 'in_progress',
                    completed_at TEXT,
                    claimed_at TEXT,
                    UNIQUE(quest_public_id, user_id)
                );

                CREATE TABLE IF NOT EXISTS internal_ledger_entries (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    event_type TEXT NOT NULL,
                    label TEXT NOT NULL,
                    amount INTEGER,
                    currency TEXT NOT NULL DEFAULT 'USD',
                    xp INTEGER,
                    reputation INTEGER,
                    status TEXT NOT NULL DEFAULT 'recorded',
                    reference_id TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS api_integration_statuses (
                    integration_key TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'not_configured',
                    description TEXT NOT NULL DEFAULT '',
                    admin_only INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS integration_requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    integration_key TEXT NOT NULL,
                    env_var TEXT NOT NULL,
                    required_for_mvp INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reputation_events (
                    public_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_public_id TEXT,
                    xp INTEGER NOT NULL DEFAULT 0,
                    creator_reputation INTEGER NOT NULL DEFAULT 0,
                    clipper_reputation INTEGER NOT NULL DEFAULT 0,
                    marketplace_reputation INTEGER NOT NULL DEFAULT 0,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS admin_audit_actions (
                    public_id TEXT PRIMARY KEY,
                    actor_user_id TEXT,
                    action_type TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    target_public_id TEXT,
                    before_state TEXT,
                    after_state TEXT,
                    note TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_worlds_campaign_created_at ON marketplace_campaigns(created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_submission_campaign ON campaign_submissions(campaign_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_entitlement_plan ON user_entitlements(plan_key);
                CREATE INDEX IF NOT EXISTS idx_worlds_credit_tx_user_created ON credit_transactions(user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_usage_user_feature ON usage_events(user_id, feature_key);
                CREATE INDEX IF NOT EXISTS idx_worlds_earning_events_user_created ON earning_events(user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_payouts_user_created ON payout_placeholders(user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_webhook_external ON webhook_events(provider, external_event_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_jobs_owner_created ON world_jobs(owner_user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_jobs_status_created ON world_jobs(status, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_jobs_target ON world_jobs(target_type, target_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_job_events_job ON world_job_events(job_public_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_job_attempts_job ON world_job_attempts(job_public_id, started_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_clip_moments_source ON clip_moments(source_public_id, start_seconds);
                CREATE INDEX IF NOT EXISTS idx_worlds_clip_candidates_source ON clip_candidates(source_public_id, score_total);
                CREATE INDEX IF NOT EXISTS idx_worlds_clip_candidates_owner ON clip_candidates(owner_user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_clip_packs_owner ON clip_packs(owner_user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_clip_contract_candidate ON clip_render_contracts(clip_candidate_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_ledger_user_created ON internal_ledger_entries(user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_audit_target ON admin_audit_actions(target_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_reputation_user ON reputation_events(user_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_ugc_creator_created ON ugc_assets(creator_user_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_worlds_ugc_status ON ugc_assets(status);
                CREATE INDEX IF NOT EXISTS idx_worlds_moderation_target ON moderation_queue_items(target_type, target_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_fraud_target ON fraud_flags(target_type, target_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_rights_target ON content_rights_claims(target_type, target_public_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_user_relic_user ON user_relics(user_id);
                CREATE INDEX IF NOT EXISTS idx_worlds_user_title_user ON user_titles(user_id);
                """
            )


def _campaign_from_row(row: sqlite3.Row | None) -> MarketplaceCampaign | None:
    if row is None:
        return None
    return MarketplaceCampaign(
        public_id=row["public_id"],
        title=row["title"],
        description=row["description"],
        buyer_user_id=row["buyer_user_id"],
        target_platform=row["target_platform"],
        source_type=row["source_type"],
        budget_amount=int(row["budget_amount"]),
        currency=row["currency"],
        platform_fee_percent=int(row["platform_fee_percent"]),
        clip_count=int(row["clip_count"]),
        deadline=row["deadline"],
        status=_campaign_status(row["status"]),
        rights_required=row["rights_required"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _submission_from_row(row: sqlite3.Row | None) -> CampaignSubmission | None:
    if row is None:
        return None
    return CampaignSubmission(
        public_id=row["public_id"],
        campaign_public_id=row["campaign_public_id"],
        clipper_user_id=row["clipper_user_id"],
        title=row["title"],
        hook=row["hook"],
        caption=row["caption"],
        asset_url=row["asset_url"],
        status=_submission_status(row["status"]),
        estimated_earnings_amount=int(row["estimated_earnings_amount"]),
        currency=row["currency"],
        review_note=row["review_note"],
        rights_confirmed=bool(row["rights_confirmed"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _entitlement_from_row(row: sqlite3.Row | None) -> UserEntitlement | None:
    if row is None:
        return None
    return UserEntitlement(
        user_id=row["user_id"],
        plan_key=row["plan_key"],
        status=_entitlement_status(row["status"]),
        source=_entitlement_source(row["source"]),
        source_reference_id=row["source_reference_id"],
        current_period_start=row["current_period_start"],
        current_period_end=row["current_period_end"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _credit_balance_from_row(row: sqlite3.Row | None) -> CreditBalance | None:
    if row is None:
        return None
    return CreditBalance(
        user_id=row["user_id"],
        balance=int(row["balance"]),
        monthly_grant=int(row["monthly_grant"]),
        used_this_period=int(row["used_this_period"]),
        period_start=row["period_start"],
        period_end=row["period_end"],
        updated_at=row["updated_at"],
    )


def _credit_transaction_from_row(row: sqlite3.Row | None) -> CreditTransaction | None:
    if row is None:
        return None
    return CreditTransaction(
        public_id=row["public_id"],
        user_id=row["user_id"],
        transaction_type=_credit_transaction_type(row["transaction_type"]),
        amount=int(row["amount"]),
        balance_after=int(row["balance_after"]),
        reason=row["reason"],
        source_type=row["source_type"],
        source_public_id=row["source_public_id"],
        created_at=row["created_at"],
    )


def _usage_event_from_row(row: sqlite3.Row | None) -> UsageEvent | None:
    if row is None:
        return None
    return UsageEvent(
        public_id=row["public_id"],
        user_id=row["user_id"],
        feature_key=row["feature_key"],
        amount=int(row["amount"]),
        status=_usage_event_status(row["status"]),
        source_type=row["source_type"],
        source_public_id=row["source_public_id"],
        created_at=row["created_at"],
    )


def _earnings_account_from_row(row: sqlite3.Row | None) -> EarningsAccount | None:
    if row is None:
        return None
    return EarningsAccount(
        user_id=row["user_id"],
        estimated_amount=int(row["estimated_amount"]),
        pending_review_amount=int(row["pending_review_amount"]),
        approved_amount=int(row["approved_amount"]),
        payable_amount=int(row["payable_amount"]),
        paid_amount=int(row["paid_amount"]),
        held_amount=int(row["held_amount"]),
        currency=row["currency"],
        updated_at=row["updated_at"],
    )


def _earning_event_from_row(row: sqlite3.Row | None) -> EarningEvent | None:
    if row is None:
        return None
    return EarningEvent(
        public_id=row["public_id"],
        user_id=row["user_id"],
        source_type=row["source_type"],
        source_public_id=row["source_public_id"],
        amount=int(row["amount"]),
        platform_fee_amount=int(row["platform_fee_amount"]),
        net_amount=int(row["net_amount"]),
        currency=row["currency"],
        status=_earning_status(row["status"]),
        note=row["note"],
        created_at=row["created_at"],
    )


def _payout_placeholder_from_row(row: sqlite3.Row | None) -> PayoutPlaceholder | None:
    if row is None:
        return None
    return PayoutPlaceholder(
        public_id=row["public_id"],
        user_id=row["user_id"],
        amount=int(row["amount"]),
        currency=row["currency"],
        status=_payout_placeholder_status(row["status"]),
        blocked_reason=row["blocked_reason"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _webhook_event_from_row(row: sqlite3.Row | None) -> WebhookEvent | None:
    if row is None:
        return None
    return WebhookEvent(
        public_id=row["public_id"],
        provider=_webhook_provider(row["provider"]),
        external_event_id=row["external_event_id"],
        event_type=row["event_type"],
        processed=bool(row["processed"]),
        status=row["status"],
        note=row["note"],
        created_at=row["created_at"],
        processed_at=row["processed_at"],
    )


def _world_job_from_row(row: sqlite3.Row | None) -> WorldJob | None:
    if row is None:
        return None
    return WorldJob(
        public_id=row["public_id"],
        owner_user_id=row["owner_user_id"],
        job_type=_job_type(row["job_type"]),
        status=_job_status(row["status"]),
        priority=_job_priority(row["priority"]),
        progress_percent=int(row["progress_percent"]),
        title=row["title"],
        description=row["description"],
        source_public_id=row["source_public_id"],
        target_type=row["target_type"],
        target_public_id=row["target_public_id"],
        input_json=row["input_json"],
        output_json=row["output_json"],
        error_message=row["error_message"],
        max_attempts=int(row["max_attempts"]),
        attempt_count=int(row["attempt_count"]),
        next_retry_at=row["next_retry_at"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _world_job_event_from_row(row: sqlite3.Row | None) -> WorldJobEvent | None:
    if row is None:
        return None
    return WorldJobEvent(
        public_id=row["public_id"],
        job_public_id=row["job_public_id"],
        event_type=row["event_type"],
        message=row["message"],
        status_before=row["status_before"],
        status_after=row["status_after"],
        progress_percent=row["progress_percent"],
        metadata_json=row["metadata_json"],
        created_at=row["created_at"],
    )


def _world_job_attempt_from_row(row: sqlite3.Row | None) -> WorldJobAttempt | None:
    if row is None:
        return None
    return WorldJobAttempt(
        public_id=row["public_id"],
        job_public_id=row["job_public_id"],
        attempt_number=int(row["attempt_number"]),
        worker_name=row["worker_name"],
        status=_job_status(row["status"]),
        error_message=row["error_message"],
        started_at=row["started_at"],
        completed_at=row["completed_at"],
    )


def _clip_moment_from_row(row: sqlite3.Row | None) -> ClipMomentRecord | None:
    if row is None:
        return None
    return ClipMomentRecord(
        public_id=row["public_id"],
        owner_user_id=row["owner_user_id"],
        source_public_id=row["source_public_id"],
        transcript_public_id=row["transcript_public_id"],
        start_seconds=float(row["start_seconds"]),
        end_seconds=float(row["end_seconds"]),
        transcript_excerpt=row["transcript_excerpt"],
        moment_type=row["moment_type"],
        reason=row["reason"],
        confidence=int(row["confidence"]),
        created_at=row["created_at"],
    )


def _clip_candidate_from_row(row: sqlite3.Row | None) -> ClipCandidateRecord | None:
    if row is None:
        return None
    return ClipCandidateRecord(
        public_id=row["public_id"],
        owner_user_id=row["owner_user_id"],
        source_public_id=row["source_public_id"],
        transcript_public_id=row["transcript_public_id"],
        moment_public_id=row["moment_public_id"],
        title=row["title"],
        hook=row["hook"],
        caption=row["caption"],
        start_seconds=float(row["start_seconds"]),
        end_seconds=float(row["end_seconds"]),
        target_platform=row["target_platform"],
        status=_clip_candidate_status(row["status"]),
        score_total=int(row["score_total"]),
        score_hook=int(row["score_hook"]),
        score_retention=int(row["score_retention"]),
        score_clarity=int(row["score_clarity"]),
        score_emotion=int(row["score_emotion"]),
        score_shareability=int(row["score_shareability"]),
        score_platform_fit=int(row["score_platform_fit"]),
        risk_notes_json=row["risk_notes_json"],
        render_asset_public_id=row["render_asset_public_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _clip_pack_from_row(row: sqlite3.Row | None) -> ClipPackRecord | None:
    if row is None:
        return None
    return ClipPackRecord(
        public_id=row["public_id"],
        owner_user_id=row["owner_user_id"],
        source_public_id=row["source_public_id"],
        transcript_public_id=row["transcript_public_id"],
        title=row["title"],
        target_platform=row["target_platform"],
        desired_clip_count=int(row["desired_clip_count"]),
        status=_clip_pack_status(row["status"]),
        selected_candidate_ids_json=row["selected_candidate_ids_json"],
        job_public_id=row["job_public_id"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _clip_render_contract_from_row(row: sqlite3.Row | None) -> ClipRenderContract | None:
    if row is None:
        return None
    return ClipRenderContract(
        public_id=row["public_id"],
        owner_user_id=row["owner_user_id"],
        clip_candidate_public_id=row["clip_candidate_public_id"],
        source_public_id=row["source_public_id"],
        output_format=row["output_format"],
        aspect_ratio=row["aspect_ratio"],
        resolution=row["resolution"],
        remove_silence=bool(row["remove_silence"]),
        captions_enabled=bool(row["captions_enabled"]),
        caption_style_json=row["caption_style_json"],
        music_enabled=bool(row["music_enabled"]),
        music_policy=row["music_policy"],
        intro_seconds=float(row["intro_seconds"]),
        outro_seconds=float(row["outro_seconds"]),
        render_job_public_id=row["render_job_public_id"],
        created_at=row["created_at"],
    )


def _profile_from_row(row: sqlite3.Row | None) -> UserWorldProfile | None:
    if row is None:
        return None
    return UserWorldProfile(
        user_id=row["user_id"],
        display_name=row["display_name"],
        class_name=row["class_name"],
        faction=row["faction"],
        level=int(row["level"]),
        xp=int(row["xp"]),
        next_level_xp=int(row["next_level_xp"]),
        creator_reputation=int(row["creator_reputation"]),
        clipper_reputation=int(row["clipper_reputation"]),
        marketplace_reputation=int(row["marketplace_reputation"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _badge_from_row(row: sqlite3.Row | None) -> Badge | None:
    if row is None:
        return None
    return Badge(
        public_id=row["public_id"],
        name=row["name"],
        tier=row["tier"],
        description=row["description"],
        lore=row["lore"],
        created_at=row["created_at"],
    )


def _ledger_from_row(row: sqlite3.Row | None) -> InternalLedgerEntry | None:
    if row is None:
        return None
    return InternalLedgerEntry(
        public_id=row["public_id"],
        user_id=row["user_id"],
        event_type=_ledger_event_type(row["event_type"]),
        label=row["label"],
        amount=row["amount"],
        currency=row["currency"],
        xp=row["xp"],
        reputation=row["reputation"],
        status=row["status"],
        reference_id=row["reference_id"],
        created_at=row["created_at"],
    )


def _integration_from_row(row: sqlite3.Row | None) -> ApiIntegrationStatus | None:
    if row is None:
        return None
    return ApiIntegrationStatus(
        integration_key=row["integration_key"],
        name=row["name"],
        category=row["category"],
        status=row["status"],
        description=row["description"],
        admin_only=bool(row["admin_only"]),
        updated_at=row["updated_at"],
    )


def _audit_from_row(row: sqlite3.Row | None) -> AdminAuditAction | None:
    if row is None:
        return None
    return AdminAuditAction(
        public_id=row["public_id"],
        actor_user_id=row["actor_user_id"],
        action_type=row["action_type"],
        target_type=row["target_type"],
        target_public_id=row["target_public_id"],
        before_state=row["before_state"],
        after_state=row["after_state"],
        note=row["note"],
        created_at=row["created_at"],
    )


def _ugc_asset_from_row(row: sqlite3.Row | None) -> UGCAsset | None:
    if row is None:
        return None
    return UGCAsset(
        public_id=row["public_id"],
        creator_user_id=row["creator_user_id"],
        title=row["title"],
        asset_type=row["asset_type"],
        description=row["description"],
        price_amount=int(row["price_amount"]),
        currency=row["currency"],
        status=_ugc_asset_status(row["status"]),
        moderation_status=_moderation_status(row["moderation_status"]),
        rights_confirmed=bool(row["rights_confirmed"]),
        license_summary=row["license_summary"],
        preview_url=row["preview_url"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _moderation_from_row(row: sqlite3.Row | None) -> ModerationQueueItem | None:
    if row is None:
        return None
    return ModerationQueueItem(
        public_id=row["public_id"],
        target_type=row["target_type"],
        target_public_id=row["target_public_id"],
        submitted_by_user_id=row["submitted_by_user_id"],
        status=_moderation_status(row["status"]),
        reason=row["reason"],
        automated_score=row["automated_score"],
        reviewer_user_id=row["reviewer_user_id"],
        reviewer_note=row["reviewer_note"],
        created_at=row["created_at"],
        reviewed_at=row["reviewed_at"],
    )


def _fraud_from_row(row: sqlite3.Row | None) -> FraudFlag | None:
    if row is None:
        return None
    return FraudFlag(
        public_id=row["public_id"],
        user_id=row["user_id"],
        target_type=row["target_type"],
        target_public_id=row["target_public_id"],
        flag_type=row["flag_type"],
        status=_fraud_flag_status(row["status"]),
        severity=row["severity"],
        evidence=row["evidence"],
        reviewer_user_id=row["reviewer_user_id"],
        reviewer_note=row["reviewer_note"],
        created_at=row["created_at"],
        resolved_at=row["resolved_at"],
    )


def _rights_claim_from_row(row: sqlite3.Row | None) -> ContentRightsClaim | None:
    if row is None:
        return None
    return ContentRightsClaim(
        public_id=row["public_id"],
        claimant_name=row["claimant_name"],
        claimant_email=row["claimant_email"],
        target_type=row["target_type"],
        target_public_id=row["target_public_id"],
        claim_summary=row["claim_summary"],
        status=_rights_claim_status(row["status"]),
        admin_note=row["admin_note"],
        created_at=row["created_at"],
        resolved_at=row["resolved_at"],
    )


def _relic_from_row(row: sqlite3.Row | None) -> Relic | None:
    if row is None:
        return None
    return Relic(
        public_id=row["public_id"],
        name=row["name"],
        tier=row["tier"],
        description=row["description"],
        lore=row["lore"],
        future_collectible_eligible=bool(row["future_collectible_eligible"]),
        created_at=row["created_at"],
    )


class CampaignRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, campaign: MarketplaceCampaign) -> MarketplaceCampaign:
        now = utcnow()
        campaign.created_at = campaign.created_at or now
        campaign.updated_at = campaign.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO marketplace_campaigns (
                    public_id, title, description, buyer_user_id, target_platform, source_type,
                    budget_amount, currency, platform_fee_percent, clip_count, deadline, status,
                    rights_required, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    campaign.public_id,
                    campaign.title,
                    campaign.description,
                    campaign.buyer_user_id,
                    campaign.target_platform,
                    campaign.source_type,
                    campaign.budget_amount,
                    campaign.currency,
                    campaign.platform_fee_percent,
                    campaign.clip_count,
                    campaign.deadline,
                    campaign.status.value,
                    campaign.rights_required,
                    campaign.created_at,
                    campaign.updated_at,
                ),
            )
        return self.get_by_public_id(campaign.public_id) or campaign

    def list(self, limit: int = 100) -> list[MarketplaceCampaign]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM marketplace_campaigns ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_campaign_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[MarketplaceCampaign]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM marketplace_campaigns WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _campaign_from_row(row)

    def save(self, campaign: MarketplaceCampaign) -> MarketplaceCampaign:
        campaign.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE marketplace_campaigns
                SET title = ?, description = ?, buyer_user_id = ?, target_platform = ?,
                    source_type = ?, budget_amount = ?, currency = ?, platform_fee_percent = ?,
                    clip_count = ?, deadline = ?, status = ?, rights_required = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    campaign.title,
                    campaign.description,
                    campaign.buyer_user_id,
                    campaign.target_platform,
                    campaign.source_type,
                    campaign.budget_amount,
                    campaign.currency,
                    campaign.platform_fee_percent,
                    campaign.clip_count,
                    campaign.deadline,
                    campaign.status.value,
                    campaign.rights_required,
                    campaign.updated_at,
                    campaign.public_id,
                ),
            )
        return self.get_by_public_id(campaign.public_id) or campaign


class SubmissionRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, submission: CampaignSubmission) -> CampaignSubmission:
        now = utcnow()
        submission.created_at = submission.created_at or now
        submission.updated_at = submission.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO campaign_submissions (
                    public_id, campaign_public_id, clipper_user_id, title, hook, caption,
                    asset_url, status, estimated_earnings_amount, currency, review_note,
                    rights_confirmed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    submission.public_id,
                    submission.campaign_public_id,
                    submission.clipper_user_id,
                    submission.title,
                    submission.hook,
                    submission.caption,
                    submission.asset_url,
                    submission.status.value,
                    submission.estimated_earnings_amount,
                    submission.currency,
                    submission.review_note,
                    int(submission.rights_confirmed),
                    submission.created_at,
                    submission.updated_at,
                ),
            )
        return self.get_by_public_id(submission.public_id) or submission

    def list(self, limit: int = 100) -> list[CampaignSubmission]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM campaign_submissions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_submission_from_row(row) for row in rows) if item]

    def list_for_campaign(self, campaign_public_id: str) -> list[CampaignSubmission]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM campaign_submissions WHERE campaign_public_id = ? ORDER BY created_at DESC",
                (campaign_public_id,),
            ).fetchall()
        return [item for item in (_submission_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[CampaignSubmission]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM campaign_submissions WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _submission_from_row(row)

    def save(self, submission: CampaignSubmission) -> CampaignSubmission:
        submission.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE campaign_submissions
                SET title = ?, hook = ?, caption = ?, asset_url = ?, status = ?,
                    estimated_earnings_amount = ?, currency = ?, review_note = ?,
                    rights_confirmed = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    submission.title,
                    submission.hook,
                    submission.caption,
                    submission.asset_url,
                    submission.status.value,
                    submission.estimated_earnings_amount,
                    submission.currency,
                    submission.review_note,
                    int(submission.rights_confirmed),
                    submission.updated_at,
                    submission.public_id,
                ),
            )
        return self.get_by_public_id(submission.public_id) or submission


class EntitlementRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_by_user_id(self, user_id: str) -> Optional[UserEntitlement]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM user_entitlements WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return _entitlement_from_row(row)

    def save(self, entitlement: UserEntitlement) -> UserEntitlement:
        now = utcnow()
        entitlement.created_at = entitlement.created_at or now
        entitlement.updated_at = now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO user_entitlements (
                    user_id, plan_key, status, source, source_reference_id,
                    current_period_start, current_period_end, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    plan_key = excluded.plan_key,
                    status = excluded.status,
                    source = excluded.source,
                    source_reference_id = excluded.source_reference_id,
                    current_period_start = excluded.current_period_start,
                    current_period_end = excluded.current_period_end,
                    updated_at = excluded.updated_at
                """,
                (
                    entitlement.user_id,
                    entitlement.plan_key,
                    entitlement.status.value,
                    entitlement.source.value,
                    entitlement.source_reference_id,
                    entitlement.current_period_start,
                    entitlement.current_period_end,
                    entitlement.created_at,
                    entitlement.updated_at,
                ),
            )
        return self.get_by_user_id(entitlement.user_id) or entitlement


class CreditRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_balance(self, user_id: str) -> Optional[CreditBalance]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM credit_balances WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return _credit_balance_from_row(row)

    def save_balance(self, balance: CreditBalance) -> CreditBalance:
        balance.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO credit_balances (
                    user_id, balance, monthly_grant, used_this_period,
                    period_start, period_end, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    balance = excluded.balance,
                    monthly_grant = excluded.monthly_grant,
                    used_this_period = excluded.used_this_period,
                    period_start = excluded.period_start,
                    period_end = excluded.period_end,
                    updated_at = excluded.updated_at
                """,
                (
                    balance.user_id,
                    balance.balance,
                    balance.monthly_grant,
                    balance.used_this_period,
                    balance.period_start,
                    balance.period_end,
                    balance.updated_at,
                ),
            )
        return self.get_balance(balance.user_id) or balance

    def create_transaction(self, transaction: CreditTransaction) -> CreditTransaction:
        transaction.created_at = transaction.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO credit_transactions (
                    public_id, user_id, transaction_type, amount, balance_after,
                    reason, source_type, source_public_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    transaction.public_id,
                    transaction.user_id,
                    transaction.transaction_type.value,
                    transaction.amount,
                    transaction.balance_after,
                    transaction.reason,
                    transaction.source_type,
                    transaction.source_public_id,
                    transaction.created_at,
                ),
            )
        return transaction

    def list_transactions(self, user_id: str, limit: int = 100) -> list[CreditTransaction]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM credit_transactions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_credit_transaction_from_row(row) for row in rows) if item]


class UsageEventRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, event: UsageEvent) -> UsageEvent:
        event.created_at = event.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO usage_events (
                    public_id, user_id, feature_key, amount, status,
                    source_type, source_public_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.public_id,
                    event.user_id,
                    event.feature_key,
                    event.amount,
                    event.status.value,
                    event.source_type,
                    event.source_public_id,
                    event.created_at,
                ),
            )
        return event


class EarningsRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_account(self, user_id: str) -> Optional[EarningsAccount]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM earnings_accounts WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return _earnings_account_from_row(row)

    def save_account(self, account: EarningsAccount) -> EarningsAccount:
        account.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO earnings_accounts (
                    user_id, estimated_amount, pending_review_amount, approved_amount,
                    payable_amount, paid_amount, held_amount, currency, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    estimated_amount = excluded.estimated_amount,
                    pending_review_amount = excluded.pending_review_amount,
                    approved_amount = excluded.approved_amount,
                    payable_amount = excluded.payable_amount,
                    paid_amount = excluded.paid_amount,
                    held_amount = excluded.held_amount,
                    currency = excluded.currency,
                    updated_at = excluded.updated_at
                """,
                (
                    account.user_id,
                    account.estimated_amount,
                    account.pending_review_amount,
                    account.approved_amount,
                    account.payable_amount,
                    account.paid_amount,
                    account.held_amount,
                    account.currency,
                    account.updated_at,
                ),
            )
        return self.get_account(account.user_id) or account

    def create_event(self, event: EarningEvent) -> EarningEvent:
        event.created_at = event.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO earning_events (
                    public_id, user_id, source_type, source_public_id, amount,
                    platform_fee_amount, net_amount, currency, status, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.public_id,
                    event.user_id,
                    event.source_type,
                    event.source_public_id,
                    event.amount,
                    event.platform_fee_amount,
                    event.net_amount,
                    event.currency,
                    event.status.value,
                    event.note,
                    event.created_at,
                ),
            )
        return event

    def list_events(self, user_id: str, limit: int = 100) -> list[EarningEvent]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM earning_events
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_earning_event_from_row(row) for row in rows) if item]


class PayoutPlaceholderRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, payout: PayoutPlaceholder) -> PayoutPlaceholder:
        now = utcnow()
        payout.created_at = payout.created_at or now
        payout.updated_at = payout.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO payout_placeholders (
                    public_id, user_id, amount, currency, status, blocked_reason,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payout.public_id,
                    payout.user_id,
                    payout.amount,
                    payout.currency,
                    payout.status.value,
                    payout.blocked_reason,
                    payout.created_at,
                    payout.updated_at,
                ),
            )
        return payout

    def list_for_user(self, user_id: str, limit: int = 100) -> list[PayoutPlaceholder]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM payout_placeholders
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_payout_placeholder_from_row(row) for row in rows) if item]


class WebhookEventRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, event: WebhookEvent) -> WebhookEvent:
        event.created_at = event.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO webhook_events (
                    public_id, provider, external_event_id, event_type, processed,
                    status, note, created_at, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.public_id,
                    event.provider.value,
                    event.external_event_id,
                    event.event_type,
                    int(event.processed),
                    event.status,
                    event.note,
                    event.created_at,
                    event.processed_at,
                ),
            )
        return event

    def get_by_external_id(self, provider: WebhookProvider, external_event_id: str) -> Optional[WebhookEvent]:
        with self.store.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM webhook_events
                WHERE provider = ? AND external_event_id = ?
                """,
                (provider.value, external_event_id),
            ).fetchone()
        return _webhook_event_from_row(row)


class WorldJobRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, job: WorldJob) -> WorldJob:
        now = utcnow()
        job.created_at = job.created_at or now
        job.updated_at = job.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO world_jobs (
                    public_id, owner_user_id, job_type, status, priority, progress_percent,
                    title, description, source_public_id, target_type, target_public_id,
                    input_json, output_json, error_message, max_attempts, attempt_count,
                    next_retry_at, started_at, completed_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.public_id,
                    job.owner_user_id,
                    job.job_type.value,
                    job.status.value,
                    job.priority.value,
                    job.progress_percent,
                    job.title,
                    job.description,
                    job.source_public_id,
                    job.target_type,
                    job.target_public_id,
                    job.input_json,
                    job.output_json,
                    job.error_message,
                    job.max_attempts,
                    job.attempt_count,
                    job.next_retry_at,
                    job.started_at,
                    job.completed_at,
                    job.created_at,
                    job.updated_at,
                ),
            )
        return self.get_by_public_id(job.public_id) or job

    def save(self, job: WorldJob) -> WorldJob:
        job.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE world_jobs
                SET owner_user_id = ?, job_type = ?, status = ?, priority = ?,
                    progress_percent = ?, title = ?, description = ?, source_public_id = ?,
                    target_type = ?, target_public_id = ?, input_json = ?, output_json = ?,
                    error_message = ?, max_attempts = ?, attempt_count = ?, next_retry_at = ?,
                    started_at = ?, completed_at = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    job.owner_user_id,
                    job.job_type.value,
                    job.status.value,
                    job.priority.value,
                    job.progress_percent,
                    job.title,
                    job.description,
                    job.source_public_id,
                    job.target_type,
                    job.target_public_id,
                    job.input_json,
                    job.output_json,
                    job.error_message,
                    job.max_attempts,
                    job.attempt_count,
                    job.next_retry_at,
                    job.started_at,
                    job.completed_at,
                    job.updated_at,
                    job.public_id,
                ),
            )
        return self.get_by_public_id(job.public_id) or job

    def get_by_public_id(self, public_id: str) -> Optional[WorldJob]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM world_jobs WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _world_job_from_row(row)

    def list_for_user(self, user_id: str, limit: int = 100) -> list[WorldJob]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM world_jobs
                WHERE owner_user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_world_job_from_row(row) for row in rows) if item]

    def list_recent(self, limit: int = 100) -> list[WorldJob]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM world_jobs ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_world_job_from_row(row) for row in rows) if item]

    def list_ready_to_run(self, limit: int = 25) -> list[WorldJob]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM world_jobs
                WHERE status IN ('queued', 'retrying')
                ORDER BY
                    CASE priority
                        WHEN 'urgent' THEN 4
                        WHEN 'high' THEN 3
                        WHEN 'normal' THEN 2
                        ELSE 1
                    END DESC,
                    created_at ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [item for item in (_world_job_from_row(row) for row in rows) if item]


class WorldJobEventRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, event: WorldJobEvent) -> WorldJobEvent:
        event.created_at = event.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO world_job_events (
                    public_id, job_public_id, event_type, message, status_before,
                    status_after, progress_percent, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.public_id,
                    event.job_public_id,
                    event.event_type,
                    event.message,
                    event.status_before,
                    event.status_after,
                    event.progress_percent,
                    event.metadata_json,
                    event.created_at,
                ),
            )
        return event

    def list_for_job(self, job_public_id: str) -> list[WorldJobEvent]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM world_job_events
                WHERE job_public_id = ?
                ORDER BY created_at ASC
                """,
                (job_public_id,),
            ).fetchall()
        return [item for item in (_world_job_event_from_row(row) for row in rows) if item]


class WorldJobAttemptRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, attempt: WorldJobAttempt) -> WorldJobAttempt:
        attempt.started_at = attempt.started_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO world_job_attempts (
                    public_id, job_public_id, attempt_number, worker_name, status,
                    error_message, started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attempt.public_id,
                    attempt.job_public_id,
                    attempt.attempt_number,
                    attempt.worker_name,
                    attempt.status.value,
                    attempt.error_message,
                    attempt.started_at,
                    attempt.completed_at,
                ),
            )
        return attempt

    def save(self, attempt: WorldJobAttempt) -> WorldJobAttempt:
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE world_job_attempts
                SET worker_name = ?, status = ?, error_message = ?, completed_at = ?
                WHERE public_id = ?
                """,
                (
                    attempt.worker_name,
                    attempt.status.value,
                    attempt.error_message,
                    attempt.completed_at,
                    attempt.public_id,
                ),
            )
        return attempt

    def list_for_job(self, job_public_id: str) -> list[WorldJobAttempt]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM world_job_attempts
                WHERE job_public_id = ?
                ORDER BY started_at ASC
                """,
                (job_public_id,),
            ).fetchall()
        return [item for item in (_world_job_attempt_from_row(row) for row in rows) if item]


class ClipMomentRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, moment: ClipMomentRecord) -> ClipMomentRecord:
        moment.created_at = moment.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO clip_moments (
                    public_id, owner_user_id, source_public_id, transcript_public_id,
                    start_seconds, end_seconds, transcript_excerpt, moment_type,
                    reason, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    moment.public_id,
                    moment.owner_user_id,
                    moment.source_public_id,
                    moment.transcript_public_id,
                    moment.start_seconds,
                    moment.end_seconds,
                    moment.transcript_excerpt,
                    moment.moment_type,
                    moment.reason,
                    moment.confidence,
                    moment.created_at,
                ),
            )
        return moment

    def list_for_source(self, source_public_id: str) -> list[ClipMomentRecord]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM clip_moments
                WHERE source_public_id = ?
                ORDER BY start_seconds ASC
                """,
                (source_public_id,),
            ).fetchall()
        return [item for item in (_clip_moment_from_row(row) for row in rows) if item]


class ClipCandidateRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, candidate: ClipCandidateRecord) -> ClipCandidateRecord:
        now = utcnow()
        candidate.created_at = candidate.created_at or now
        candidate.updated_at = candidate.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO clip_candidates (
                    public_id, owner_user_id, source_public_id, transcript_public_id,
                    moment_public_id, title, hook, caption, start_seconds, end_seconds,
                    target_platform, status, score_total, score_hook, score_retention,
                    score_clarity, score_emotion, score_shareability, score_platform_fit,
                    risk_notes_json, render_asset_public_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.public_id,
                    candidate.owner_user_id,
                    candidate.source_public_id,
                    candidate.transcript_public_id,
                    candidate.moment_public_id,
                    candidate.title,
                    candidate.hook,
                    candidate.caption,
                    candidate.start_seconds,
                    candidate.end_seconds,
                    candidate.target_platform,
                    candidate.status.value,
                    candidate.score_total,
                    candidate.score_hook,
                    candidate.score_retention,
                    candidate.score_clarity,
                    candidate.score_emotion,
                    candidate.score_shareability,
                    candidate.score_platform_fit,
                    candidate.risk_notes_json,
                    candidate.render_asset_public_id,
                    candidate.created_at,
                    candidate.updated_at,
                ),
            )
        return self.get_by_public_id(candidate.public_id) or candidate

    def save(self, candidate: ClipCandidateRecord) -> ClipCandidateRecord:
        candidate.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE clip_candidates
                SET title = ?, hook = ?, caption = ?, start_seconds = ?, end_seconds = ?,
                    target_platform = ?, status = ?, score_total = ?, score_hook = ?,
                    score_retention = ?, score_clarity = ?, score_emotion = ?,
                    score_shareability = ?, score_platform_fit = ?, risk_notes_json = ?,
                    render_asset_public_id = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    candidate.title,
                    candidate.hook,
                    candidate.caption,
                    candidate.start_seconds,
                    candidate.end_seconds,
                    candidate.target_platform,
                    candidate.status.value,
                    candidate.score_total,
                    candidate.score_hook,
                    candidate.score_retention,
                    candidate.score_clarity,
                    candidate.score_emotion,
                    candidate.score_shareability,
                    candidate.score_platform_fit,
                    candidate.risk_notes_json,
                    candidate.render_asset_public_id,
                    candidate.updated_at,
                    candidate.public_id,
                ),
            )
        return self.get_by_public_id(candidate.public_id) or candidate

    def get_by_public_id(self, public_id: str) -> Optional[ClipCandidateRecord]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM clip_candidates WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _clip_candidate_from_row(row)

    def list_for_source(self, source_public_id: str) -> list[ClipCandidateRecord]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM clip_candidates
                WHERE source_public_id = ?
                ORDER BY score_total DESC, created_at DESC
                """,
                (source_public_id,),
            ).fetchall()
        return [item for item in (_clip_candidate_from_row(row) for row in rows) if item]


class ClipPackRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, pack: ClipPackRecord) -> ClipPackRecord:
        now = utcnow()
        pack.created_at = pack.created_at or now
        pack.updated_at = pack.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO clip_packs (
                    public_id, owner_user_id, source_public_id, transcript_public_id,
                    title, target_platform, desired_clip_count, status,
                    selected_candidate_ids_json, job_public_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pack.public_id,
                    pack.owner_user_id,
                    pack.source_public_id,
                    pack.transcript_public_id,
                    pack.title,
                    pack.target_platform,
                    pack.desired_clip_count,
                    pack.status.value,
                    pack.selected_candidate_ids_json,
                    pack.job_public_id,
                    pack.created_at,
                    pack.updated_at,
                ),
            )
        return self.get_by_public_id(pack.public_id) or pack

    def save(self, pack: ClipPackRecord) -> ClipPackRecord:
        pack.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE clip_packs
                SET title = ?, target_platform = ?, desired_clip_count = ?, status = ?,
                    selected_candidate_ids_json = ?, job_public_id = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    pack.title,
                    pack.target_platform,
                    pack.desired_clip_count,
                    pack.status.value,
                    pack.selected_candidate_ids_json,
                    pack.job_public_id,
                    pack.updated_at,
                    pack.public_id,
                ),
            )
        return self.get_by_public_id(pack.public_id) or pack

    def get_by_public_id(self, public_id: str) -> Optional[ClipPackRecord]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM clip_packs WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _clip_pack_from_row(row)

    def list_for_user(self, user_id: str, limit: int = 100) -> list[ClipPackRecord]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM clip_packs
                WHERE owner_user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_clip_pack_from_row(row) for row in rows) if item]


class ClipRenderContractRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, contract: ClipRenderContract) -> ClipRenderContract:
        contract.created_at = contract.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO clip_render_contracts (
                    public_id, owner_user_id, clip_candidate_public_id, source_public_id,
                    output_format, aspect_ratio, resolution, remove_silence,
                    captions_enabled, caption_style_json, music_enabled, music_policy,
                    intro_seconds, outro_seconds, render_job_public_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    contract.public_id,
                    contract.owner_user_id,
                    contract.clip_candidate_public_id,
                    contract.source_public_id,
                    contract.output_format,
                    contract.aspect_ratio,
                    contract.resolution,
                    int(contract.remove_silence),
                    int(contract.captions_enabled),
                    contract.caption_style_json,
                    int(contract.music_enabled),
                    contract.music_policy,
                    contract.intro_seconds,
                    contract.outro_seconds,
                    contract.render_job_public_id,
                    contract.created_at,
                ),
            )
        return self.get_by_public_id(contract.public_id) or contract

    def save(self, contract: ClipRenderContract) -> ClipRenderContract:
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE clip_render_contracts
                SET render_job_public_id = ?
                WHERE public_id = ?
                """,
                (contract.render_job_public_id, contract.public_id),
            )
        return self.get_by_public_id(contract.public_id) or contract

    def get_by_public_id(self, public_id: str) -> Optional[ClipRenderContract]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM clip_render_contracts WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _clip_render_contract_from_row(row)


class WorldProfileRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_by_user_id(self, user_id: str) -> Optional[UserWorldProfile]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM user_world_profiles WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return _profile_from_row(row)

    def create(self, profile: UserWorldProfile) -> UserWorldProfile:
        now = utcnow()
        profile.created_at = profile.created_at or now
        profile.updated_at = profile.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO user_world_profiles (
                    user_id, display_name, class_name, faction, level, xp, next_level_xp,
                    creator_reputation, clipper_reputation, marketplace_reputation,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile.user_id,
                    profile.display_name,
                    profile.class_name,
                    profile.faction,
                    profile.level,
                    profile.xp,
                    profile.next_level_xp,
                    profile.creator_reputation,
                    profile.clipper_reputation,
                    profile.marketplace_reputation,
                    profile.created_at,
                    profile.updated_at,
                ),
            )
        return self.get_by_user_id(profile.user_id) or profile

    def save(self, profile: UserWorldProfile) -> UserWorldProfile:
        profile.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE user_world_profiles
                SET display_name = ?, class_name = ?, faction = ?, level = ?, xp = ?,
                    next_level_xp = ?, creator_reputation = ?, clipper_reputation = ?,
                    marketplace_reputation = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (
                    profile.display_name,
                    profile.class_name,
                    profile.faction,
                    profile.level,
                    profile.xp,
                    profile.next_level_xp,
                    profile.creator_reputation,
                    profile.clipper_reputation,
                    profile.marketplace_reputation,
                    profile.updated_at,
                    profile.user_id,
                ),
            )
        return self.get_by_user_id(profile.user_id) or profile


class LedgerRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, entry: InternalLedgerEntry) -> InternalLedgerEntry:
        entry.created_at = entry.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO internal_ledger_entries (
                    public_id, user_id, event_type, label, amount, currency, xp,
                    reputation, status, reference_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.public_id,
                    entry.user_id,
                    entry.event_type.value,
                    entry.label,
                    entry.amount,
                    entry.currency,
                    entry.xp,
                    entry.reputation,
                    entry.status,
                    entry.reference_id,
                    entry.created_at,
                ),
            )
        return entry

    def list_for_user(self, user_id: str, limit: int = 100) -> list[InternalLedgerEntry]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM internal_ledger_entries
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()
        return [item for item in (_ledger_from_row(row) for row in rows) if item]


class BadgeRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_badge(self, badge_public_id: str) -> Optional[Badge]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM badges WHERE public_id = ?",
                (badge_public_id,),
            ).fetchone()
        return _badge_from_row(row)

    def list_badges(self) -> list[Badge]:
        with self.store.connect() as connection:
            rows = connection.execute("SELECT * FROM badges ORDER BY name").fetchall()
        return [item for item in (_badge_from_row(row) for row in rows) if item]

    def list_user_badges(self, user_id: str) -> list[tuple[UserBadge, Badge]]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT ub.user_id, ub.badge_public_id, ub.unlocked_at,
                       b.public_id, b.name, b.tier, b.description, b.lore, b.created_at
                FROM user_badges ub
                JOIN badges b ON b.public_id = ub.badge_public_id
                WHERE ub.user_id = ?
                ORDER BY ub.unlocked_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            (
                UserBadge(
                    user_id=row["user_id"],
                    badge_public_id=row["badge_public_id"],
                    unlocked_at=row["unlocked_at"],
                ),
                Badge(
                    public_id=row["public_id"],
                    name=row["name"],
                    tier=row["tier"],
                    description=row["description"],
                    lore=row["lore"],
                    created_at=row["created_at"],
                ),
            )
            for row in rows
        ]

    def create_badge(self, badge: Badge) -> Badge:
        badge.created_at = badge.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO badges (public_id, name, tier, description, lore, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (badge.public_id, badge.name, badge.tier, badge.description, badge.lore, badge.created_at),
            )
        return self.get_badge(badge.public_id) or badge

    def user_has_badge(self, user_id: str, badge_public_id: str) -> bool:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM user_badges WHERE user_id = ? AND badge_public_id = ?",
                (user_id, badge_public_id),
            ).fetchone()
        return row is not None

    def award_badge(self, user_badge: UserBadge) -> UserBadge:
        user_badge.unlocked_at = user_badge.unlocked_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO user_badges (user_id, badge_public_id, unlocked_at)
                VALUES (?, ?, ?)
                """,
                (user_badge.user_id, user_badge.badge_public_id, user_badge.unlocked_at),
            )
        return user_badge


class QuestRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create_quest(self, quest: Quest) -> Quest:
        quest.created_at = quest.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO quests (
                    public_id, title, description, category, goal, reward_xp,
                    reward_badge_public_id, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    quest.public_id,
                    quest.title,
                    quest.description,
                    quest.category,
                    quest.goal,
                    quest.reward_xp,
                    quest.reward_badge_public_id,
                    int(quest.active),
                    quest.created_at,
                ),
            )
        return quest

    def get_by_public_id(self, public_id: str) -> Optional[Quest]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM quests WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        if row is None:
            return None
        return Quest(
            public_id=row["public_id"],
            title=row["title"],
            description=row["description"],
            category=row["category"],
            goal=int(row["goal"]),
            reward_xp=int(row["reward_xp"]),
            reward_badge_public_id=row["reward_badge_public_id"],
            active=bool(row["active"]),
            created_at=row["created_at"],
        )

    def list_active(self) -> list[Quest]:
        with self.store.connect() as connection:
            rows = connection.execute("SELECT * FROM quests WHERE active = 1 ORDER BY created_at").fetchall()
        return [
            Quest(
                public_id=row["public_id"],
                title=row["title"],
                description=row["description"],
                category=row["category"],
                goal=int(row["goal"]),
                reward_xp=int(row["reward_xp"]),
                reward_badge_public_id=row["reward_badge_public_id"],
                active=bool(row["active"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_completion(self, user_id: str, quest_public_id: str) -> Optional[QuestCompletion]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM quest_completions WHERE user_id = ? AND quest_public_id = ?",
                (user_id, quest_public_id),
            ).fetchone()
        if row is None:
            return None
        return QuestCompletion(
            quest_public_id=row["quest_public_id"],
            user_id=row["user_id"],
            progress=int(row["progress"]),
            status=row["status"],
            completed_at=row["completed_at"],
            claimed_at=row["claimed_at"],
        )

    def save_completion(self, completion: QuestCompletion) -> QuestCompletion:
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO quest_completions (
                    quest_public_id, user_id, progress, status, completed_at, claimed_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(quest_public_id, user_id) DO UPDATE SET
                    progress = excluded.progress,
                    status = excluded.status,
                    completed_at = excluded.completed_at,
                    claimed_at = excluded.claimed_at
                """,
                (
                    completion.quest_public_id,
                    completion.user_id,
                    completion.progress,
                    completion.status,
                    completion.completed_at,
                    completion.claimed_at,
                ),
            )
        return completion


class IntegrationRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def list(self) -> list[ApiIntegrationStatus]:
        with self.store.connect() as connection:
            rows = connection.execute("SELECT * FROM api_integration_statuses ORDER BY name").fetchall()
        return [item for item in (_integration_from_row(row) for row in rows) if item]

    def upsert(self, status: ApiIntegrationStatus) -> ApiIntegrationStatus:
        status.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO api_integration_statuses (
                    integration_key, name, category, status, description, admin_only, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(integration_key) DO UPDATE SET
                    name = excluded.name,
                    category = excluded.category,
                    status = excluded.status,
                    description = excluded.description,
                    admin_only = excluded.admin_only,
                    updated_at = excluded.updated_at
                """,
                (
                    status.integration_key,
                    status.name,
                    status.category,
                    status.status,
                    status.description,
                    int(status.admin_only),
                    status.updated_at,
                ),
            )
        return status


class AuditRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, audit: AdminAuditAction) -> AdminAuditAction:
        audit.created_at = audit.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO admin_audit_actions (
                    public_id, actor_user_id, action_type, target_type, target_public_id,
                    before_state, after_state, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit.public_id,
                    audit.actor_user_id,
                    audit.action_type,
                    audit.target_type,
                    audit.target_public_id,
                    audit.before_state,
                    audit.after_state,
                    audit.note,
                    audit.created_at,
                ),
            )
        return audit

    def list(self, limit: int = 100) -> list[AdminAuditAction]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM admin_audit_actions ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_audit_from_row(row) for row in rows) if item]


class ReputationRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, event: ReputationEvent) -> ReputationEvent:
        event.created_at = event.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO reputation_events (
                    public_id, user_id, source_type, source_public_id, xp,
                    creator_reputation, clipper_reputation, marketplace_reputation,
                    reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.public_id,
                    event.user_id,
                    event.source_type,
                    event.source_public_id,
                    event.xp,
                    event.creator_reputation,
                    event.clipper_reputation,
                    event.marketplace_reputation,
                    event.reason,
                    event.created_at,
                ),
            )
        return event


class UGCAssetRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, asset: UGCAsset) -> UGCAsset:
        now = utcnow()
        asset.created_at = asset.created_at or now
        asset.updated_at = asset.updated_at or now
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO ugc_assets (
                    public_id, creator_user_id, title, asset_type, description,
                    price_amount, currency, status, moderation_status,
                    rights_confirmed, license_summary, preview_url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset.public_id,
                    asset.creator_user_id,
                    asset.title,
                    asset.asset_type,
                    asset.description,
                    asset.price_amount,
                    asset.currency,
                    asset.status.value,
                    asset.moderation_status.value,
                    int(asset.rights_confirmed),
                    asset.license_summary,
                    asset.preview_url,
                    asset.created_at,
                    asset.updated_at,
                ),
            )
        return self.get_by_public_id(asset.public_id) or asset

    def list(self, limit: int = 100) -> list[UGCAsset]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ugc_assets ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_ugc_asset_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[UGCAsset]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM ugc_assets WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _ugc_asset_from_row(row)

    def save(self, asset: UGCAsset) -> UGCAsset:
        asset.updated_at = utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE ugc_assets
                SET title = ?, asset_type = ?, description = ?, price_amount = ?,
                    currency = ?, status = ?, moderation_status = ?, rights_confirmed = ?,
                    license_summary = ?, preview_url = ?, updated_at = ?
                WHERE public_id = ?
                """,
                (
                    asset.title,
                    asset.asset_type,
                    asset.description,
                    asset.price_amount,
                    asset.currency,
                    asset.status.value,
                    asset.moderation_status.value,
                    int(asset.rights_confirmed),
                    asset.license_summary,
                    asset.preview_url,
                    asset.updated_at,
                    asset.public_id,
                ),
            )
        return self.get_by_public_id(asset.public_id) or asset


class ModerationRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, item: ModerationQueueItem) -> ModerationQueueItem:
        item.created_at = item.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO moderation_queue_items (
                    public_id, target_type, target_public_id, submitted_by_user_id,
                    status, reason, automated_score, reviewer_user_id, reviewer_note,
                    created_at, reviewed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.public_id,
                    item.target_type,
                    item.target_public_id,
                    item.submitted_by_user_id,
                    item.status.value,
                    item.reason,
                    item.automated_score,
                    item.reviewer_user_id,
                    item.reviewer_note,
                    item.created_at,
                    item.reviewed_at,
                ),
            )
        return self.get_by_public_id(item.public_id) or item

    def list(self, limit: int = 100) -> list[ModerationQueueItem]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM moderation_queue_items ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_moderation_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[ModerationQueueItem]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM moderation_queue_items WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _moderation_from_row(row)

    def save(self, item: ModerationQueueItem) -> ModerationQueueItem:
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE moderation_queue_items
                SET status = ?, reason = ?, automated_score = ?, reviewer_user_id = ?,
                    reviewer_note = ?, reviewed_at = ?
                WHERE public_id = ?
                """,
                (
                    item.status.value,
                    item.reason,
                    item.automated_score,
                    item.reviewer_user_id,
                    item.reviewer_note,
                    item.reviewed_at,
                    item.public_id,
                ),
            )
        return self.get_by_public_id(item.public_id) or item


class FraudRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, flag: FraudFlag) -> FraudFlag:
        flag.created_at = flag.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO fraud_flags (
                    public_id, user_id, target_type, target_public_id, flag_type,
                    status, severity, evidence, reviewer_user_id, reviewer_note,
                    created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flag.public_id,
                    flag.user_id,
                    flag.target_type,
                    flag.target_public_id,
                    flag.flag_type,
                    flag.status.value,
                    flag.severity,
                    flag.evidence,
                    flag.reviewer_user_id,
                    flag.reviewer_note,
                    flag.created_at,
                    flag.resolved_at,
                ),
            )
        return self.get_by_public_id(flag.public_id) or flag

    def list(self, limit: int = 100) -> list[FraudFlag]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM fraud_flags ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_fraud_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[FraudFlag]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM fraud_flags WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _fraud_from_row(row)

    def save(self, flag: FraudFlag) -> FraudFlag:
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE fraud_flags
                SET status = ?, severity = ?, evidence = ?, reviewer_user_id = ?,
                    reviewer_note = ?, resolved_at = ?
                WHERE public_id = ?
                """,
                (
                    flag.status.value,
                    flag.severity,
                    flag.evidence,
                    flag.reviewer_user_id,
                    flag.reviewer_note,
                    flag.resolved_at,
                    flag.public_id,
                ),
            )
        return self.get_by_public_id(flag.public_id) or flag


class ContentRightsRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def create(self, claim: ContentRightsClaim) -> ContentRightsClaim:
        claim.created_at = claim.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT INTO content_rights_claims (
                    public_id, claimant_name, claimant_email, target_type, target_public_id,
                    claim_summary, status, admin_note, created_at, resolved_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    claim.public_id,
                    claim.claimant_name,
                    claim.claimant_email,
                    claim.target_type,
                    claim.target_public_id,
                    claim.claim_summary,
                    claim.status.value,
                    claim.admin_note,
                    claim.created_at,
                    claim.resolved_at,
                ),
            )
        return self.get_by_public_id(claim.public_id) or claim

    def list(self, limit: int = 100) -> list[ContentRightsClaim]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM content_rights_claims ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [item for item in (_rights_claim_from_row(row) for row in rows) if item]

    def get_by_public_id(self, public_id: str) -> Optional[ContentRightsClaim]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM content_rights_claims WHERE public_id = ?",
                (public_id,),
            ).fetchone()
        return _rights_claim_from_row(row)

    def save(self, claim: ContentRightsClaim) -> ContentRightsClaim:
        with self.store.connect() as connection:
            connection.execute(
                """
                UPDATE content_rights_claims
                SET status = ?, admin_note = ?, resolved_at = ?
                WHERE public_id = ?
                """,
                (
                    claim.status.value,
                    claim.admin_note,
                    claim.resolved_at,
                    claim.public_id,
                ),
            )
        return self.get_by_public_id(claim.public_id) or claim


class RelicRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def get_relic(self, relic_public_id: str) -> Optional[Relic]:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT * FROM relics WHERE public_id = ?",
                (relic_public_id,),
            ).fetchone()
        return _relic_from_row(row)

    def create_relic(self, relic: Relic) -> Relic:
        relic.created_at = relic.created_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO relics (
                    public_id, name, tier, description, lore, future_collectible_eligible, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    relic.public_id,
                    relic.name,
                    relic.tier,
                    relic.description,
                    relic.lore,
                    int(relic.future_collectible_eligible),
                    relic.created_at,
                ),
            )
        return self.get_relic(relic.public_id) or relic

    def list_relics(self) -> list[Relic]:
        with self.store.connect() as connection:
            rows = connection.execute("SELECT * FROM relics ORDER BY created_at DESC").fetchall()
        return [item for item in (_relic_from_row(row) for row in rows) if item]

    def user_has_relic(self, user_id: str, relic_public_id: str) -> bool:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM user_relics WHERE user_id = ? AND relic_public_id = ?",
                (user_id, relic_public_id),
            ).fetchone()
        return row is not None

    def award_relic(self, user_relic: UserRelic) -> UserRelic:
        user_relic.unlocked_at = user_relic.unlocked_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO user_relics (user_id, relic_public_id, unlocked_at)
                VALUES (?, ?, ?)
                """,
                (user_relic.user_id, user_relic.relic_public_id, user_relic.unlocked_at),
            )
        return user_relic

    def list_user_relics(self, user_id: str) -> list[tuple[UserRelic, Relic]]:
        with self.store.connect() as connection:
            rows = connection.execute(
                """
                SELECT ur.user_id, ur.relic_public_id, ur.unlocked_at,
                       r.public_id, r.name, r.tier, r.description, r.lore,
                       r.future_collectible_eligible, r.created_at
                FROM user_relics ur
                JOIN relics r ON r.public_id = ur.relic_public_id
                WHERE ur.user_id = ?
                ORDER BY ur.unlocked_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            (
                UserRelic(
                    user_id=row["user_id"],
                    relic_public_id=row["relic_public_id"],
                    unlocked_at=row["unlocked_at"],
                ),
                Relic(
                    public_id=row["public_id"],
                    name=row["name"],
                    tier=row["tier"],
                    description=row["description"],
                    lore=row["lore"],
                    future_collectible_eligible=bool(row["future_collectible_eligible"]),
                    created_at=row["created_at"],
                ),
            )
            for row in rows
        ]


class UserTitleRepository:
    def __init__(self, store: WorldsStore):
        self.store = store

    def list_titles(self, user_id: str) -> list[UserTitle]:
        with self.store.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM user_titles WHERE user_id = ? ORDER BY unlocked_at DESC",
                (user_id,),
            ).fetchall()
        return [
            UserTitle(
                user_id=row["user_id"],
                title=row["title"],
                unlocked_at=row["unlocked_at"],
            )
            for row in rows
        ]

    def user_has_title(self, user_id: str, title: str) -> bool:
        with self.store.connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM user_titles WHERE user_id = ? AND title = ?",
                (user_id, title),
            ).fetchone()
        return row is not None

    def award_title(self, title: UserTitle) -> UserTitle:
        title.unlocked_at = title.unlocked_at or utcnow()
        with self.store.connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO user_titles (user_id, title, unlocked_at)
                VALUES (?, ?, ?)
                """,
                (title.user_id, title.title, title.unlocked_at),
            )
        return title
