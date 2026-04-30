from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .credits import CreditService
from .dependencies import get_demo_user_id, get_optional_actor_id, get_worlds_store
from .earnings import EarningsService
from .entitlements import EntitlementService
from .errors import (
    ForbiddenTransitionError,
    NotFoundError,
    PayoutBlockedError,
    RightsConfirmationRequired,
    ValidationError,
)
from .fraud import FraudService
from .gates import can_create_campaign
from .integrations import IntegrationStatusService
from .ledger import LedgerService
from .moderation import ModerationService
from .pricing import list_plans, quote_marketplace_fee
from .quests import QuestService
from .relics import RelicService
from .repositories import AuditRepository, BadgeRepository, QuestRepository, WorldsStore
from .rights import ContentRightsService
from .schemas import (
    AdminAuditActionResponse,
    BadgeResponse,
    BillingPlanResponse,
    CampaignCreateRequest,
    CampaignResponse,
    ContentRightsClaimCreateRequest,
    ContentRightsClaimResponse,
    ContentRightsClaimReviewRequest,
    CreditBalanceResponse,
    CreditGrantRequest,
    CreditSpendRequest,
    CreditTransactionResponse,
    EarningEventResponse,
    EarningsAccountResponse,
    EntitlementGrantRequest,
    FraudFlagCreateRequest,
    FraudFlagResponse,
    FraudFlagReviewRequest,
    GateCheckResponse,
    IntegrationStatusResponse,
    LedgerEntryResponse,
    MarketplaceFeeQuoteRequest,
    MarketplaceFeeQuoteResponse,
    MoneyResponse,
    ModerationQueueItemResponse,
    ModerationReviewRequest,
    PayoutPlaceholderCreateRequest,
    PayoutPlaceholderResponse,
    QuestCompletionResponse,
    QuestResponse,
    RichWorldProfileResponse,
    RelicResponse,
    StripeConnectReadinessResponse,
    SubmissionCreateRequest,
    SubmissionResponse,
    SubmissionReviewRequest,
    UGCAssetCreateRequest,
    UGCAssetResponse,
    UGCAssetReviewRequest,
    UserEntitlementResponse,
    UserBadgeResponse,
    UserRelicResponse,
    WorldProfileResponse,
)
from .services import MarketplaceService
from .stripe_connect import stripe_connect_readiness
from .ugc import UGCService
from .xp import XpService

router = APIRouter(prefix="/worlds", tags=["lwa-worlds"])


def campaign_to_response(campaign) -> CampaignResponse:
    return CampaignResponse(
        public_id=campaign.public_id,
        title=campaign.title,
        description=campaign.description,
        target_platform=campaign.target_platform,
        source_type=campaign.source_type,
        budget=MoneyResponse(amount=campaign.budget_amount, currency=campaign.currency),
        platform_fee_percent=campaign.platform_fee_percent,
        clip_count=campaign.clip_count,
        deadline=campaign.deadline,
        status=campaign.status.value if hasattr(campaign.status, "value") else str(campaign.status),
        rights_required=campaign.rights_required,
        created_at=campaign.created_at,
    )


def submission_to_response(submission) -> SubmissionResponse:
    return SubmissionResponse(
        public_id=submission.public_id,
        campaign_public_id=submission.campaign_public_id,
        title=submission.title,
        hook=submission.hook,
        caption=submission.caption,
        asset_url=submission.asset_url,
        status=submission.status.value if hasattr(submission.status, "value") else str(submission.status),
        estimated_earnings=MoneyResponse(amount=submission.estimated_earnings_amount, currency=submission.currency),
        review_note=submission.review_note,
        rights_confirmed=submission.rights_confirmed,
        created_at=submission.created_at,
    )


def ledger_to_response(entry) -> LedgerEntryResponse:
    return LedgerEntryResponse(
        public_id=entry.public_id,
        user_id=entry.user_id,
        event_type=entry.event_type.value if hasattr(entry.event_type, "value") else str(entry.event_type),
        label=entry.label,
        amount=entry.amount,
        currency=entry.currency,
        xp=entry.xp,
        reputation=entry.reputation,
        status=entry.status,
        reference_id=entry.reference_id,
        created_at=entry.created_at,
    )


def billing_plan_to_response(plan) -> BillingPlanResponse:
    return BillingPlanResponse(
        plan_key=plan.plan_key,
        name=plan.name,
        monthly_price_amount=plan.monthly_price_amount,
        currency=plan.currency,
        monthly_credits=plan.monthly_credits,
        marketplace_fee_percent=plan.marketplace_fee_percent,
        max_campaigns=plan.max_campaigns,
        max_ugc_assets=plan.max_ugc_assets,
        features=list(plan.features),
    )


def entitlement_to_response(entitlement) -> UserEntitlementResponse:
    return UserEntitlementResponse(
        user_id=entitlement.user_id,
        plan_key=entitlement.plan_key,
        status=entitlement.status.value if hasattr(entitlement.status, "value") else str(entitlement.status),
        source=entitlement.source.value if hasattr(entitlement.source, "value") else str(entitlement.source),
        source_reference_id=entitlement.source_reference_id,
        current_period_start=entitlement.current_period_start,
        current_period_end=entitlement.current_period_end,
        created_at=entitlement.created_at,
        updated_at=entitlement.updated_at,
    )


def credit_balance_to_response(balance) -> CreditBalanceResponse:
    return CreditBalanceResponse(
        user_id=balance.user_id,
        balance=balance.balance,
        monthly_grant=balance.monthly_grant,
        used_this_period=balance.used_this_period,
        period_start=balance.period_start,
        period_end=balance.period_end,
        updated_at=balance.updated_at,
    )


def credit_transaction_to_response(transaction) -> CreditTransactionResponse:
    return CreditTransactionResponse(
        public_id=transaction.public_id,
        user_id=transaction.user_id,
        transaction_type=(
            transaction.transaction_type.value
            if hasattr(transaction.transaction_type, "value")
            else str(transaction.transaction_type)
        ),
        amount=transaction.amount,
        balance_after=transaction.balance_after,
        reason=transaction.reason,
        source_type=transaction.source_type,
        source_public_id=transaction.source_public_id,
        created_at=transaction.created_at,
    )


def earnings_account_to_response(account) -> EarningsAccountResponse:
    return EarningsAccountResponse(
        user_id=account.user_id,
        estimated_amount=account.estimated_amount,
        pending_review_amount=account.pending_review_amount,
        approved_amount=account.approved_amount,
        payable_amount=account.payable_amount,
        paid_amount=account.paid_amount,
        held_amount=account.held_amount,
        currency=account.currency,
        updated_at=account.updated_at,
    )


def earning_event_to_response(event) -> EarningEventResponse:
    return EarningEventResponse(
        public_id=event.public_id,
        user_id=event.user_id,
        source_type=event.source_type,
        source_public_id=event.source_public_id,
        amount=event.amount,
        platform_fee_amount=event.platform_fee_amount,
        net_amount=event.net_amount,
        currency=event.currency,
        status=event.status.value if hasattr(event.status, "value") else str(event.status),
        note=event.note,
        created_at=event.created_at,
    )


def payout_placeholder_to_response(payout) -> PayoutPlaceholderResponse:
    return PayoutPlaceholderResponse(
        public_id=payout.public_id,
        user_id=payout.user_id,
        amount=payout.amount,
        currency=payout.currency,
        status=payout.status.value if hasattr(payout.status, "value") else str(payout.status),
        blocked_reason=payout.blocked_reason,
        created_at=payout.created_at,
        updated_at=payout.updated_at,
    )


def ugc_to_response(asset) -> UGCAssetResponse:
    return UGCAssetResponse(
        public_id=asset.public_id,
        creator_user_id=asset.creator_user_id,
        title=asset.title,
        asset_type=asset.asset_type,
        description=asset.description,
        price_amount=asset.price_amount,
        currency=asset.currency,
        status=asset.status.value if hasattr(asset.status, "value") else str(asset.status),
        moderation_status=(
            asset.moderation_status.value
            if hasattr(asset.moderation_status, "value")
            else str(asset.moderation_status)
        ),
        rights_confirmed=asset.rights_confirmed,
        license_summary=asset.license_summary,
        preview_url=asset.preview_url,
        created_at=asset.created_at,
    )


def moderation_to_response(item) -> ModerationQueueItemResponse:
    return ModerationQueueItemResponse(
        public_id=item.public_id,
        target_type=item.target_type,
        target_public_id=item.target_public_id,
        submitted_by_user_id=item.submitted_by_user_id,
        status=item.status.value if hasattr(item.status, "value") else str(item.status),
        reason=item.reason,
        automated_score=item.automated_score,
        reviewer_user_id=item.reviewer_user_id,
        reviewer_note=item.reviewer_note,
        created_at=item.created_at,
        reviewed_at=item.reviewed_at,
    )


def fraud_to_response(flag) -> FraudFlagResponse:
    return FraudFlagResponse(
        public_id=flag.public_id,
        user_id=flag.user_id,
        target_type=flag.target_type,
        target_public_id=flag.target_public_id,
        flag_type=flag.flag_type,
        status=flag.status.value if hasattr(flag.status, "value") else str(flag.status),
        severity=flag.severity,
        evidence=flag.evidence,
        reviewer_user_id=flag.reviewer_user_id,
        reviewer_note=flag.reviewer_note,
        created_at=flag.created_at,
        resolved_at=flag.resolved_at,
    )


def rights_to_response(claim) -> ContentRightsClaimResponse:
    return ContentRightsClaimResponse(
        public_id=claim.public_id,
        claimant_name=claim.claimant_name,
        claimant_email=claim.claimant_email,
        target_type=claim.target_type,
        target_public_id=claim.target_public_id,
        claim_summary=claim.claim_summary,
        status=claim.status.value if hasattr(claim.status, "value") else str(claim.status),
        admin_note=claim.admin_note,
        created_at=claim.created_at,
        resolved_at=claim.resolved_at,
    )


def badge_to_response(badge) -> BadgeResponse:
    return BadgeResponse(
        public_id=badge.public_id,
        name=badge.name,
        tier=badge.tier,
        description=badge.description,
        lore=badge.lore,
        created_at=badge.created_at,
    )


def user_badge_to_response(user_badge, badge) -> UserBadgeResponse:
    return UserBadgeResponse(
        badge_public_id=badge.public_id,
        name=badge.name,
        tier=badge.tier,
        description=badge.description,
        lore=badge.lore,
        unlocked_at=user_badge.unlocked_at,
    )


def user_relic_to_response(user_relic, relic) -> UserRelicResponse:
    return UserRelicResponse(
        relic_public_id=relic.public_id,
        name=relic.name,
        tier=relic.tier,
        description=relic.description,
        lore=relic.lore,
        future_collectible_eligible=relic.future_collectible_eligible,
        unlocked_at=user_relic.unlocked_at,
    )


def quest_to_response(quest) -> QuestResponse:
    return QuestResponse(
        public_id=quest.public_id,
        title=quest.title,
        description=quest.description,
        category=quest.category,
        goal=quest.goal,
        reward_xp=quest.reward_xp,
        reward_badge_public_id=quest.reward_badge_public_id,
        active=quest.active,
    )


def quest_completion_to_response(completion) -> QuestCompletionResponse:
    return QuestCompletionResponse(
        quest_public_id=completion.quest_public_id,
        user_id=completion.user_id,
        progress=completion.progress,
        status=completion.status,
        completed_at=completion.completed_at,
        claimed_at=completion.claimed_at,
    )


def handle_worlds_error(error: Exception) -> None:
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, RightsConfirmationRequired):
        raise HTTPException(status_code=400, detail=str(error)) from error
    if isinstance(error, ForbiddenTransitionError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, PayoutBlockedError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, ValidationError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise error


@router.get("/health")
def worlds_health():
    return {"status": "ok", "service": "lwa-worlds", "phase": "persistent_sqlite_foundation"}


@router.get("/billing/plans", response_model=list[BillingPlanResponse])
def get_billing_plans():
    return [billing_plan_to_response(plan) for plan in list_plans()]


@router.get("/billing/entitlement/me", response_model=UserEntitlementResponse)
def get_my_entitlement(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    entitlement = EntitlementService(store).get_or_create(user_id)
    return entitlement_to_response(entitlement)


@router.post("/admin/billing/entitlements/grant", response_model=UserEntitlementResponse)
def grant_user_entitlement(
    payload: EntitlementGrantRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        entitlement = EntitlementService(store).grant(payload=payload, actor_user_id=actor_id)
        return entitlement_to_response(entitlement)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/billing/gates/create-campaign", response_model=GateCheckResponse)
def check_create_campaign_gate(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    plan_key = EntitlementService(store).current_plan_key(user_id)
    result = can_create_campaign(plan_key, 0)
    return GateCheckResponse(
        allowed=result.allowed,
        plan_key=result.plan_key,
        required_plan=result.required_plan,
        reason=result.reason,
    )


@router.get("/credits/me", response_model=CreditBalanceResponse)
def get_my_credits(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    plan_key = EntitlementService(store).current_plan_key(user_id)
    balance = CreditService(store).get_or_create_balance(user_id=user_id, plan_key=plan_key)
    return credit_balance_to_response(balance)


@router.post("/admin/credits/grant", response_model=CreditBalanceResponse)
def grant_user_credits(
    payload: CreditGrantRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        balance = CreditService(store).grant_credits(
            user_id=payload.user_id,
            amount=payload.amount,
            reason=payload.reason,
            actor_user_id=actor_id,
        )
        return credit_balance_to_response(balance)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/credits/spend", response_model=CreditBalanceResponse)
def spend_my_credits(
    payload: CreditSpendRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        balance = CreditService(store).spend_credits(user_id=user_id, payload=payload)
        return credit_balance_to_response(balance)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/credits/transactions/me", response_model=list[CreditTransactionResponse])
def list_my_credit_transactions(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [
        credit_transaction_to_response(transaction)
        for transaction in CreditService(store).list_transactions(user_id)
    ]


@router.post("/marketplace/fee-quote", response_model=MarketplaceFeeQuoteResponse)
def marketplace_fee_quote(payload: MarketplaceFeeQuoteRequest):
    try:
        return MarketplaceFeeQuoteResponse(**quote_marketplace_fee(payload.gross_amount, payload.plan_key))
    except Exception as error:
        handle_worlds_error(error)


@router.get("/earnings/account/me", response_model=EarningsAccountResponse)
def get_my_earnings_account(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return earnings_account_to_response(EarningsService(store).get_or_create_account(user_id))


@router.get("/earnings/events/me", response_model=list[EarningEventResponse])
def list_my_earning_events(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [earning_event_to_response(event) for event in EarningsService(store).list_events(user_id)]


@router.post("/payouts/placeholders", response_model=PayoutPlaceholderResponse)
def create_payout_placeholder(
    payload: PayoutPlaceholderCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        payout = EarningsService(store).create_payout_placeholder(user_id=user_id, payload=payload)
        return payout_placeholder_to_response(payout)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/payouts/placeholders/me", response_model=list[PayoutPlaceholderResponse])
def list_my_payout_placeholders(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [
        payout_placeholder_to_response(payout)
        for payout in EarningsService(store).list_payout_placeholders(user_id)
    ]


@router.get("/payouts/stripe-connect/readiness", response_model=StripeConnectReadinessResponse)
def get_stripe_connect_readiness():
    return StripeConnectReadinessResponse(**stripe_connect_readiness())


@router.post("/marketplace/campaigns", response_model=CampaignResponse)
def create_campaign(
    payload: CampaignCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        campaign = MarketplaceService(store).create_campaign(payload=payload, buyer_user_id=user_id)
        return campaign_to_response(campaign)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/marketplace/campaigns", response_model=list[CampaignResponse])
def list_campaigns(store: WorldsStore = Depends(get_worlds_store)):
    return [campaign_to_response(item) for item in MarketplaceService(store).list_campaigns()]


@router.get("/marketplace/campaigns/{campaign_public_id}", response_model=CampaignResponse)
def get_campaign(campaign_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    try:
        campaign = MarketplaceService(store).get_campaign(campaign_public_id)
        return campaign_to_response(campaign)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/marketplace/submissions", response_model=SubmissionResponse)
def create_submission(
    payload: SubmissionCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        submission = MarketplaceService(store).create_submission(payload=payload, clipper_user_id=user_id)
        return submission_to_response(submission)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/marketplace/submissions", response_model=list[SubmissionResponse])
def list_submissions(store: WorldsStore = Depends(get_worlds_store)):
    return [submission_to_response(item) for item in MarketplaceService(store).list_submissions()]


@router.post("/marketplace/submissions/{submission_public_id}/review", response_model=SubmissionResponse)
def review_submission(
    submission_public_id: str,
    payload: SubmissionReviewRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        submission = MarketplaceService(store).review_submission(
            submission_public_id=submission_public_id,
            action=payload.action,
            actor_user_id=actor_id or "system",
            review_note=payload.review_note,
        )
        return submission_to_response(submission)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/ugc/assets", response_model=UGCAssetResponse)
def create_ugc_asset(
    payload: UGCAssetCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        asset = UGCService(store).create_asset(payload=payload, creator_user_id=user_id)
        return ugc_to_response(asset)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/ugc/assets", response_model=list[UGCAssetResponse])
def list_ugc_assets(store: WorldsStore = Depends(get_worlds_store)):
    return [ugc_to_response(asset) for asset in UGCService(store).list_assets()]


@router.get("/ugc/assets/{asset_public_id}", response_model=UGCAssetResponse)
def get_ugc_asset(asset_public_id: str, store: WorldsStore = Depends(get_worlds_store)):
    try:
        return ugc_to_response(UGCService(store).get_asset(asset_public_id))
    except Exception as error:
        handle_worlds_error(error)


@router.post("/ugc/assets/{asset_public_id}/submit-review", response_model=UGCAssetResponse)
def submit_ugc_asset_for_review(
    asset_public_id: str,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        asset = UGCService(store).submit_for_review(asset_public_id=asset_public_id, actor_user_id=user_id)
        return ugc_to_response(asset)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/ugc/assets/{asset_public_id}/review", response_model=UGCAssetResponse)
def review_ugc_asset(
    asset_public_id: str,
    payload: UGCAssetReviewRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        asset = UGCService(store).review_asset(
            asset_public_id=asset_public_id,
            action=payload.action,
            reviewer_user_id=actor_id or "system",
            reviewer_note=payload.reviewer_note,
        )
        return ugc_to_response(asset)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/admin/moderation", response_model=list[ModerationQueueItemResponse])
def list_moderation_queue(store: WorldsStore = Depends(get_worlds_store)):
    return [moderation_to_response(item) for item in ModerationService(store).list_queue()]


@router.post("/admin/moderation/{moderation_public_id}/review", response_model=ModerationQueueItemResponse)
def review_moderation_item(
    moderation_public_id: str,
    payload: ModerationReviewRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        item = ModerationService(store).review(
            moderation_public_id=moderation_public_id,
            action=payload.action,
            reviewer_user_id=actor_id or "system",
            reviewer_note=payload.reviewer_note,
        )
        return moderation_to_response(item)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/admin/fraud", response_model=FraudFlagResponse)
def create_fraud_flag(
    payload: FraudFlagCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        flag = FraudService(store).create_flag(payload=payload, actor_user_id=actor_id)
        return fraud_to_response(flag)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/admin/fraud", response_model=list[FraudFlagResponse])
def list_fraud_flags(store: WorldsStore = Depends(get_worlds_store)):
    return [fraud_to_response(flag) for flag in FraudService(store).list_flags()]


@router.post("/admin/fraud/{fraud_public_id}/review", response_model=FraudFlagResponse)
def review_fraud_flag(
    fraud_public_id: str,
    payload: FraudFlagReviewRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        flag = FraudService(store).review_flag(
            fraud_public_id=fraud_public_id,
            action=payload.action,
            reviewer_user_id=actor_id or "system",
            reviewer_note=payload.reviewer_note,
        )
        return fraud_to_response(flag)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/rights/claims", response_model=ContentRightsClaimResponse)
def create_content_rights_claim(
    payload: ContentRightsClaimCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
):
    try:
        claim = ContentRightsService(store).create_claim(payload)
        return rights_to_response(claim)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/admin/rights/claims", response_model=list[ContentRightsClaimResponse])
def list_content_rights_claims(store: WorldsStore = Depends(get_worlds_store)):
    return [rights_to_response(claim) for claim in ContentRightsService(store).list_claims()]


@router.post("/admin/rights/claims/{claim_public_id}/review", response_model=ContentRightsClaimResponse)
def review_content_rights_claim(
    claim_public_id: str,
    payload: ContentRightsClaimReviewRequest,
    store: WorldsStore = Depends(get_worlds_store),
    actor_id: str | None = Depends(get_optional_actor_id),
):
    try:
        claim = ContentRightsService(store).review_claim(
            claim_public_id=claim_public_id,
            action=payload.action,
            actor_user_id=actor_id or "system",
            admin_note=payload.admin_note,
        )
        return rights_to_response(claim)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/profile/me", response_model=WorldProfileResponse)
def get_my_world_profile(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    profile = XpService(store).get_or_create_profile(user_id)
    return WorldProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name,
        class_name=profile.class_name,
        faction=profile.faction,
        level=profile.level,
        xp=profile.xp,
        next_level_xp=profile.next_level_xp,
        creator_reputation=profile.creator_reputation,
        clipper_reputation=profile.clipper_reputation,
        marketplace_reputation=profile.marketplace_reputation,
    )


@router.get("/profile/demo", response_model=WorldProfileResponse)
def get_demo_world_profile(store: WorldsStore = Depends(get_worlds_store)):
    return get_my_world_profile(store=store, user_id="demo_user")


@router.get("/badges", response_model=list[BadgeResponse])
def list_badges(store: WorldsStore = Depends(get_worlds_store)):
    return [badge_to_response(badge) for badge in BadgeRepository(store).list_badges()]


@router.get("/badges/me", response_model=list[UserBadgeResponse])
def list_my_badges(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [
        user_badge_to_response(user_badge, badge)
        for user_badge, badge in BadgeRepository(store).list_user_badges(user_id)
    ]


@router.get("/relics/me", response_model=list[UserRelicResponse])
def list_my_relics(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [
        user_relic_to_response(user_relic, relic)
        for user_relic, relic in RelicService(store).list_user_relics(user_id)
    ]


@router.get("/profile/me/rich", response_model=RichWorldProfileResponse)
def get_rich_world_profile(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    profile = XpService(store).get_or_create_profile(user_id)
    relic_service = RelicService(store)
    user_relics = relic_service.list_user_relics(user_id)
    titles = relic_service.list_user_titles(user_id)
    badge_repo = BadgeRepository(store)
    quest_repo = QuestRepository(store)

    quest_completions = []
    for quest in QuestService(store).list_quests():
        completion = quest_repo.get_completion(user_id, quest.public_id)
        if completion:
            quest_completions.append(quest_completion_to_response(completion))

    return RichWorldProfileResponse(
        user_id=profile.user_id,
        display_name=profile.display_name,
        class_name=profile.class_name,
        faction=profile.faction,
        level=profile.level,
        xp=profile.xp,
        next_level_xp=profile.next_level_xp,
        creator_reputation=profile.creator_reputation,
        clipper_reputation=profile.clipper_reputation,
        marketplace_reputation=profile.marketplace_reputation,
        badges=[
            user_badge_to_response(user_badge, badge)
            for user_badge, badge in badge_repo.list_user_badges(user_id)
        ],
        relics=[user_relic_to_response(user_relic, relic) for user_relic, relic in user_relics],
        titles=titles,
        quests=quest_completions,
    )


@router.get("/quests", response_model=list[QuestResponse])
def list_quests(store: WorldsStore = Depends(get_worlds_store)):
    return [quest_to_response(quest) for quest in QuestService(store).list_quests()]


@router.post("/quests/{quest_public_id}/progress", response_model=QuestCompletionResponse)
def progress_quest(
    quest_public_id: str,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        completion = QuestService(store).progress_quest(user_id=user_id, quest_public_id=quest_public_id)
        return quest_completion_to_response(completion)
    except Exception as error:
        handle_worlds_error(error)


@router.post("/quests/{quest_public_id}/claim", response_model=QuestCompletionResponse)
def claim_quest(
    quest_public_id: str,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        completion = QuestService(store).claim_quest(user_id=user_id, quest_public_id=quest_public_id)
        return quest_completion_to_response(completion)
    except Exception as error:
        handle_worlds_error(error)


@router.get("/ledger/me", response_model=list[LedgerEntryResponse])
def get_my_ledger(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [ledger_to_response(entry) for entry in LedgerService(store).list_for_user(user_id)]


@router.get("/ledger/demo", response_model=list[LedgerEntryResponse])
def get_demo_ledger(store: WorldsStore = Depends(get_worlds_store)):
    return [ledger_to_response(entry) for entry in LedgerService(store).list_for_user("demo_user")]


@router.get("/integrations", response_model=list[IntegrationStatusResponse])
def get_integrations(store: WorldsStore = Depends(get_worlds_store)):
    return [
        IntegrationStatusResponse(
            integration_key=item.integration_key,
            name=item.name,
            category=item.category,
            status=item.status,
            description=item.description,
            admin_only=item.admin_only,
        )
        for item in IntegrationStatusService(store).list_statuses()
    ]


@router.get("/integrations/demo", response_model=list[IntegrationStatusResponse])
def get_demo_integrations(store: WorldsStore = Depends(get_worlds_store)):
    return get_integrations(store)


@router.post("/integrations/sync", response_model=list[IntegrationStatusResponse])
def sync_integrations(store: WorldsStore = Depends(get_worlds_store)):
    return [
        IntegrationStatusResponse(
            integration_key=item.integration_key,
            name=item.name,
            category=item.category,
            status=item.status,
            description=item.description,
            admin_only=item.admin_only,
        )
        for item in IntegrationStatusService(store).sync_statuses()
    ]


@router.get("/admin/audit-log", response_model=list[AdminAuditActionResponse])
def get_admin_audit_log(store: WorldsStore = Depends(get_worlds_store)):
    return [
        AdminAuditActionResponse(
            public_id=item.public_id,
            actor_user_id=item.actor_user_id,
            action_type=item.action_type,
            target_type=item.target_type,
            target_public_id=item.target_public_id,
            before_state=item.before_state,
            after_state=item.after_state,
            note=item.note,
            created_at=item.created_at,
        )
        for item in AuditRepository(store).list()
    ]
