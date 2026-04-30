from __future__ import annotations

from .audit import AuditService
from .models import EntitlementSource, EntitlementStatus, UserEntitlement
from .pricing import get_plan
from .repositories import EntitlementRepository, WorldsStore
from .schemas import EntitlementGrantRequest


class EntitlementService:
    def __init__(self, store: WorldsStore):
        self.entitlements = EntitlementRepository(store)
        self.audit = AuditService(store)

    def get_or_create(self, user_id: str) -> UserEntitlement:
        existing = self.entitlements.get_by_user_id(user_id)
        if existing:
            return existing

        entitlement = UserEntitlement(
            user_id=user_id,
            plan_key="free",
            status=EntitlementStatus.active,
            source=EntitlementSource.demo,
        )
        return self.entitlements.save(entitlement)

    def current_plan_key(self, user_id: str) -> str:
        entitlement = self.get_or_create(user_id)
        if entitlement.status != EntitlementStatus.active:
            return "free"
        try:
            get_plan(entitlement.plan_key)
            return entitlement.plan_key
        except Exception:
            return "free"

    def grant(
        self,
        *,
        payload: EntitlementGrantRequest,
        actor_user_id: str | None,
    ) -> UserEntitlement:
        get_plan(payload.plan_key)

        try:
            source = EntitlementSource(payload.source)
        except ValueError:
            source = EntitlementSource.manual

        before = self.entitlements.get_by_user_id(payload.user_id)
        entitlement = UserEntitlement(
            user_id=payload.user_id,
            plan_key=payload.plan_key,
            status=EntitlementStatus.active,
            source=source,
            source_reference_id=payload.source_reference_id,
            current_period_start=payload.current_period_start,
            current_period_end=payload.current_period_end,
            created_at=before.created_at if before else "",
        )
        saved = self.entitlements.save(entitlement)

        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="entitlement_granted",
            target_type="user_entitlement",
            target_public_id=saved.user_id,
            before_state=before.plan_key if before else None,
            after_state=saved.plan_key,
            note=payload.reason,
        )
        return saved
