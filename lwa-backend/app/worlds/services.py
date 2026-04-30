from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .earnings import EarningsService
from .errors import ForbiddenTransitionError, NotFoundError, RightsConfirmationRequired, ValidationError
from .ledger import LedgerService
from .models import CampaignStatus, CampaignSubmission, MarketplaceCampaign, SubmissionStatus
from .relics import GOLD_THREAD_RELIC, RelicService
from .repositories import CampaignRepository, SubmissionRepository, WorldsStore
from .schemas import CampaignCreateRequest, SubmissionCreateRequest
from .xp import XpService


ALLOWED_SUBMISSION_REVIEW_ACTIONS = {
    "approve": SubmissionStatus.approved,
    "reject": SubmissionStatus.rejected,
    "request_revision": SubmissionStatus.revision_requested,
    "dispute": SubmissionStatus.disputed,
}


class MarketplaceService:
    def __init__(self, store: WorldsStore):
        self.campaigns = CampaignRepository(store)
        self.submissions = SubmissionRepository(store)
        self.ledger = LedgerService(store)
        self.xp = XpService(store)
        self.audit = AuditService(store)
        self.relics = RelicService(store)
        self.earnings = EarningsService(store)

    def create_campaign(self, *, payload: CampaignCreateRequest, buyer_user_id: str) -> MarketplaceCampaign:
        if payload.budget_amount <= 0:
            raise ValidationError("Campaign budget must be greater than zero.")
        if payload.clip_count <= 0:
            raise ValidationError("Clip count must be greater than zero.")

        campaign = MarketplaceCampaign(
            public_id=f"camp_{uuid4().hex[:12]}",
            title=payload.title.strip(),
            description=payload.description.strip(),
            buyer_user_id=buyer_user_id,
            target_platform=payload.target_platform,
            source_type=payload.source_type,
            budget_amount=payload.budget_amount,
            clip_count=payload.clip_count,
            deadline=payload.deadline,
            status=CampaignStatus.pending_review,
            rights_required=payload.rights_required,
        )
        saved = self.campaigns.create(campaign)

        self.ledger.record_campaign_created(buyer_user_id, saved.public_id)
        self.xp.on_campaign_created(buyer_user_id, saved.public_id)
        self.audit.record(
            actor_user_id=buyer_user_id,
            action_type="campaign_created",
            target_type="campaign",
            target_public_id=saved.public_id,
            after_state=saved.status.value,
            note="Campaign created and moved to pending review.",
        )
        return saved

    def list_campaigns(self) -> list[MarketplaceCampaign]:
        return self.campaigns.list()

    def get_campaign(self, public_id: str) -> MarketplaceCampaign:
        campaign = self.campaigns.get_by_public_id(public_id)
        if not campaign:
            raise NotFoundError("Campaign not found")
        return campaign

    def create_submission(
        self,
        *,
        payload: SubmissionCreateRequest,
        clipper_user_id: str,
    ) -> CampaignSubmission:
        if not payload.rights_confirmed:
            raise RightsConfirmationRequired("Rights confirmation is required.")

        campaign = self.campaigns.get_by_public_id(payload.campaign_public_id)
        if not campaign:
            raise NotFoundError("Campaign not found")

        if campaign.status not in {CampaignStatus.open, CampaignStatus.pending_review, CampaignStatus.under_review}:
            raise ForbiddenTransitionError(
                f"Cannot submit work to campaign with status {campaign.status.value}."
            )

        submission = CampaignSubmission(
            public_id=f"sub_{uuid4().hex[:12]}",
            campaign_public_id=payload.campaign_public_id,
            clipper_user_id=clipper_user_id,
            title=payload.title.strip(),
            hook=payload.hook.strip(),
            caption=payload.caption.strip(),
            asset_url=payload.asset_url,
            status=SubmissionStatus.submitted,
            estimated_earnings_amount=payload.estimated_earnings_amount,
            rights_confirmed=payload.rights_confirmed,
        )
        saved = self.submissions.create(submission)
        self.ledger.record_submission_created(clipper_user_id, saved.public_id)
        self.audit.record(
            actor_user_id=clipper_user_id,
            action_type="submission_created",
            target_type="submission",
            target_public_id=saved.public_id,
            after_state=saved.status.value,
        )
        return saved

    def list_submissions(self) -> list[CampaignSubmission]:
        return self.submissions.list()

    def review_submission(
        self,
        *,
        submission_public_id: str,
        action: str,
        actor_user_id: str,
        review_note: str | None = None,
    ) -> CampaignSubmission:
        submission = self.submissions.get_by_public_id(submission_public_id)
        if not submission:
            raise NotFoundError("Submission not found")
        if action not in ALLOWED_SUBMISSION_REVIEW_ACTIONS:
            raise ValidationError("Invalid review action")

        before = submission.status
        after = ALLOWED_SUBMISSION_REVIEW_ACTIONS[action]
        if before in {SubmissionStatus.paid, SubmissionStatus.disputed} and after != before:
            raise ForbiddenTransitionError(f"Cannot move submission from {before.value} to {after.value}.")

        submission.status = after
        submission.review_note = review_note
        saved = self.submissions.save(submission)

        if after == SubmissionStatus.approved and before != SubmissionStatus.approved and saved.clipper_user_id:
            campaign = self.campaigns.get_by_public_id(saved.campaign_public_id)
            self.ledger.record_submission_approved(
                saved.clipper_user_id,
                saved.public_id,
                saved.estimated_earnings_amount,
            )
            self.earnings.record_approved_submission(
                user_id=saved.clipper_user_id,
                submission_public_id=saved.public_id,
                gross_amount=saved.estimated_earnings_amount,
                platform_fee_percent=campaign.platform_fee_percent if campaign else 20,
                actor_user_id=actor_user_id,
            )
            self.xp.on_submission_approved(saved.clipper_user_id, saved.public_id)
            self.relics.award_relic_once(
                user_id=saved.clipper_user_id,
                relic_data=GOLD_THREAD_RELIC,
            )
            self.relics.award_title_once(
                user_id=saved.clipper_user_id,
                title="Approved Earner",
            )

        self.audit.record(
            actor_user_id=actor_user_id,
            action_type=f"submission_{action}",
            target_type="submission",
            target_public_id=saved.public_id,
            before_state=before.value,
            after_state=after.value,
            note=review_note,
        )
        return saved
