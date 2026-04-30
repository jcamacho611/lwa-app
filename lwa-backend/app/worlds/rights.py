from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .errors import NotFoundError, ValidationError
from .models import ContentRightsClaim, ContentRightsClaimStatus
from .repositories import ContentRightsRepository, WorldsStore, utcnow
from .schemas import ContentRightsClaimCreateRequest


ALLOWED_RIGHTS_ACTIONS = {
    "review": ContentRightsClaimStatus.in_review,
    "request_info": ContentRightsClaimStatus.information_requested,
    "resolve": ContentRightsClaimStatus.resolved,
    "reject": ContentRightsClaimStatus.rejected,
    "escalate": ContentRightsClaimStatus.escalated,
}


class ContentRightsService:
    def __init__(self, store: WorldsStore):
        self.repo = ContentRightsRepository(store)
        self.audit = AuditService(store)

    def create_claim(self, payload: ContentRightsClaimCreateRequest) -> ContentRightsClaim:
        if "@" not in payload.claimant_email:
            raise ValidationError("Valid claimant email is required")

        claim = ContentRightsClaim(
            public_id=f"rights_{uuid4().hex[:12]}",
            claimant_name=payload.claimant_name,
            claimant_email=payload.claimant_email,
            target_type=payload.target_type,
            target_public_id=payload.target_public_id,
            claim_summary=payload.claim_summary,
            status=ContentRightsClaimStatus.open,
        )
        saved = self.repo.create(claim)

        self.audit.record(
            actor_user_id=None,
            action_type="content_rights_claim_created",
            target_type=saved.target_type,
            target_public_id=saved.target_public_id,
            after_state=saved.status.value,
            note=saved.claim_summary,
        )
        return saved

    def list_claims(self) -> list[ContentRightsClaim]:
        return self.repo.list()

    def review_claim(
        self,
        *,
        claim_public_id: str,
        action: str,
        actor_user_id: str,
        admin_note: str | None = None,
    ) -> ContentRightsClaim:
        if action not in ALLOWED_RIGHTS_ACTIONS:
            raise ValidationError("Invalid rights claim action")

        claim = self.repo.get_by_public_id(claim_public_id)
        if not claim:
            raise NotFoundError("Content rights claim not found")

        before = claim.status
        claim.status = ALLOWED_RIGHTS_ACTIONS[action]
        claim.admin_note = admin_note
        if claim.status in {ContentRightsClaimStatus.resolved, ContentRightsClaimStatus.rejected}:
            claim.resolved_at = utcnow()
        saved = self.repo.save(claim)

        self.audit.record(
            actor_user_id=actor_user_id,
            action_type=f"content_rights_{action}",
            target_type=saved.target_type,
            target_public_id=saved.target_public_id,
            before_state=before.value,
            after_state=saved.status.value,
            note=admin_note,
        )
        return saved
