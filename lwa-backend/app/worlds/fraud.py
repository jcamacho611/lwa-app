from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .errors import NotFoundError, ValidationError
from .models import FraudFlag, FraudFlagStatus
from .repositories import FraudRepository, WorldsStore, utcnow
from .schemas import FraudFlagCreateRequest


ALLOWED_FRAUD_ACTIONS = {
    "clear": FraudFlagStatus.cleared,
    "confirm": FraudFlagStatus.confirmed,
    "escalate": FraudFlagStatus.escalated,
    "review": FraudFlagStatus.in_review,
}


class FraudService:
    def __init__(self, store: WorldsStore):
        self.repo = FraudRepository(store)
        self.audit = AuditService(store)

    def create_flag(self, *, payload: FraudFlagCreateRequest, actor_user_id: str | None = None) -> FraudFlag:
        if payload.severity not in {"low", "medium", "high", "critical"}:
            raise ValidationError("Invalid severity")

        flag = FraudFlag(
            public_id=f"fraud_{uuid4().hex[:12]}",
            user_id=payload.user_id,
            target_type=payload.target_type,
            target_public_id=payload.target_public_id,
            flag_type=payload.flag_type,
            severity=payload.severity,
            evidence=payload.evidence,
            status=FraudFlagStatus.open,
        )
        saved = self.repo.create(flag)

        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="fraud_flag_created",
            target_type=saved.target_type,
            target_public_id=saved.target_public_id,
            after_state=saved.status.value,
            note=saved.flag_type,
        )
        return saved

    def list_flags(self) -> list[FraudFlag]:
        return self.repo.list()

    def review_flag(
        self,
        *,
        fraud_public_id: str,
        action: str,
        reviewer_user_id: str,
        reviewer_note: str | None = None,
    ) -> FraudFlag:
        if action not in ALLOWED_FRAUD_ACTIONS:
            raise ValidationError("Invalid fraud action")

        flag = self.repo.get_by_public_id(fraud_public_id)
        if not flag:
            raise NotFoundError("Fraud flag not found")

        before = flag.status
        flag.status = ALLOWED_FRAUD_ACTIONS[action]
        flag.reviewer_user_id = reviewer_user_id
        flag.reviewer_note = reviewer_note
        flag.resolved_at = utcnow() if flag.status in {FraudFlagStatus.cleared, FraudFlagStatus.confirmed} else None
        saved = self.repo.save(flag)

        self.audit.record(
            actor_user_id=reviewer_user_id,
            action_type=f"fraud_{action}",
            target_type=saved.target_type,
            target_public_id=saved.target_public_id,
            before_state=before.value,
            after_state=saved.status.value,
            note=reviewer_note,
        )
        return saved
