from __future__ import annotations

from .audit import AuditService
from .errors import NotFoundError, ValidationError
from .models import ModerationStatus
from .repositories import ModerationRepository, WorldsStore, utcnow


ALLOWED_MODERATION_ACTIONS = {
    "approve": ModerationStatus.approved,
    "reject": ModerationStatus.rejected,
    "flag": ModerationStatus.flagged,
    "escalate": ModerationStatus.escalated,
    "remove": ModerationStatus.removed,
}


class ModerationService:
    def __init__(self, store: WorldsStore):
        self.repo = ModerationRepository(store)
        self.audit = AuditService(store)

    def list_queue(self):
        return self.repo.list()

    def review(
        self,
        *,
        moderation_public_id: str,
        action: str,
        reviewer_user_id: str,
        reviewer_note: str | None = None,
    ):
        if action not in ALLOWED_MODERATION_ACTIONS:
            raise ValidationError("Invalid moderation action")

        item = self.repo.get_by_public_id(moderation_public_id)
        if not item:
            raise NotFoundError("Moderation item not found")

        before = item.status
        item.status = ALLOWED_MODERATION_ACTIONS[action]
        item.reviewer_user_id = reviewer_user_id
        item.reviewer_note = reviewer_note
        item.reviewed_at = utcnow()
        saved = self.repo.save(item)

        self.audit.record(
            actor_user_id=reviewer_user_id,
            action_type=f"moderation_{action}",
            target_type=saved.target_type,
            target_public_id=saved.target_public_id,
            before_state=before.value,
            after_state=saved.status.value,
            note=reviewer_note,
        )
        return saved
