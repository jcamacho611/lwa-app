from __future__ import annotations

from uuid import uuid4

from .models import AdminAuditAction
from .repositories import AuditRepository, WorldsStore


class AuditService:
    def __init__(self, store: WorldsStore):
        self.repo = AuditRepository(store)

    def record(
        self,
        *,
        actor_user_id: str | None,
        action_type: str,
        target_type: str,
        target_public_id: str | None = None,
        before_state: str | None = None,
        after_state: str | None = None,
        note: str | None = None,
    ) -> AdminAuditAction:
        return self.repo.create(
            AdminAuditAction(
                public_id=f"audit_{uuid4().hex[:12]}",
                actor_user_id=actor_user_id,
                action_type=action_type,
                target_type=target_type,
                target_public_id=target_public_id,
                before_state=before_state,
                after_state=after_state,
                note=note,
            )
        )
