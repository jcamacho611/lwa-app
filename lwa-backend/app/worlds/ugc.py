from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .errors import NotFoundError, RightsConfirmationRequired, ValidationError
from .ledger import LedgerService
from .models import LedgerEventType, ModerationQueueItem, ModerationStatus, UGCAsset, UGCAssetStatus
from .repositories import ModerationRepository, UGCAssetRepository, WorldsStore
from .schemas import UGCAssetCreateRequest
from .xp import XpService


ALLOWED_UGC_REVIEW_ACTIONS = {
    "approve": (UGCAssetStatus.approved, ModerationStatus.approved),
    "reject": (UGCAssetStatus.rejected, ModerationStatus.rejected),
    "remove": (UGCAssetStatus.removed, ModerationStatus.removed),
    "escalate": (UGCAssetStatus.pending_review, ModerationStatus.escalated),
}


class UGCService:
    def __init__(self, store: WorldsStore):
        self.assets = UGCAssetRepository(store)
        self.moderation = ModerationRepository(store)
        self.audit = AuditService(store)
        self.ledger = LedgerService(store)
        self.xp = XpService(store)

    def create_asset(self, *, payload: UGCAssetCreateRequest, creator_user_id: str) -> UGCAsset:
        if not payload.rights_confirmed:
            raise RightsConfirmationRequired("UGC asset requires rights confirmation.")
        if payload.price_amount < 0:
            raise ValidationError("Price cannot be negative.")

        asset = UGCAsset(
            public_id=f"ugc_{uuid4().hex[:12]}",
            creator_user_id=creator_user_id,
            title=payload.title.strip(),
            asset_type=payload.asset_type.strip(),
            description=payload.description.strip(),
            price_amount=payload.price_amount,
            status=UGCAssetStatus.draft,
            moderation_status=ModerationStatus.pending,
            rights_confirmed=payload.rights_confirmed,
            license_summary=payload.license_summary.strip(),
            preview_url=payload.preview_url,
        )
        saved = self.assets.create(asset)

        self.ledger.record(
            event_type=LedgerEventType.reputation_awarded,
            label="Created UGC asset draft",
            user_id=creator_user_id,
            xp=40,
            reputation=2,
            reference_id=saved.public_id,
        )
        self.xp.add_xp(
            user_id=creator_user_id,
            xp=40,
            creator_rep=2,
            reason="Created UGC asset draft",
            source_type="ugc_asset",
            source_public_id=saved.public_id,
        )
        self.audit.record(
            actor_user_id=creator_user_id,
            action_type="ugc_asset_created",
            target_type="ugc_asset",
            target_public_id=saved.public_id,
            after_state=saved.status.value,
        )
        return saved

    def submit_for_review(self, *, asset_public_id: str, actor_user_id: str) -> UGCAsset:
        asset = self.assets.get_by_public_id(asset_public_id)
        if not asset:
            raise NotFoundError("UGC asset not found")

        before = asset.status
        asset.status = UGCAssetStatus.pending_review
        asset.moderation_status = ModerationStatus.pending
        saved = self.assets.save(asset)

        self.moderation.create(
            ModerationQueueItem(
                public_id=f"mod_{uuid4().hex[:12]}",
                target_type="ugc_asset",
                target_public_id=saved.public_id,
                submitted_by_user_id=saved.creator_user_id,
                status=ModerationStatus.pending,
                reason="UGC asset submitted for marketplace review.",
            )
        )
        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="ugc_asset_submitted_for_review",
            target_type="ugc_asset",
            target_public_id=saved.public_id,
            before_state=before.value,
            after_state=saved.status.value,
        )
        return saved

    def review_asset(
        self,
        *,
        asset_public_id: str,
        action: str,
        reviewer_user_id: str,
        reviewer_note: str | None = None,
    ) -> UGCAsset:
        if action not in ALLOWED_UGC_REVIEW_ACTIONS:
            raise ValidationError("Invalid UGC review action")

        asset = self.assets.get_by_public_id(asset_public_id)
        if not asset:
            raise NotFoundError("UGC asset not found")

        before_status = asset.status
        after_asset_status, after_mod_status = ALLOWED_UGC_REVIEW_ACTIONS[action]
        asset.status = after_asset_status
        asset.moderation_status = after_mod_status
        saved = self.assets.save(asset)

        if after_asset_status == UGCAssetStatus.approved and before_status != UGCAssetStatus.approved:
            self.xp.add_xp(
                user_id=saved.creator_user_id,
                xp=100,
                creator_rep=8,
                marketplace_rep=3,
                reason="UGC asset approved",
                source_type="ugc_asset",
                source_public_id=saved.public_id,
            )

        self.audit.record(
            actor_user_id=reviewer_user_id,
            action_type=f"ugc_asset_{action}",
            target_type="ugc_asset",
            target_public_id=saved.public_id,
            before_state=before_status.value,
            after_state=saved.status.value,
            note=reviewer_note,
        )
        return saved

    def list_assets(self) -> list[UGCAsset]:
        return self.assets.list()

    def get_asset(self, asset_public_id: str) -> UGCAsset:
        asset = self.assets.get_by_public_id(asset_public_id)
        if not asset:
            raise NotFoundError("UGC asset not found")
        return asset
