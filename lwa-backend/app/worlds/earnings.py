from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .errors import PayoutBlockedError, ValidationError
from .models import EarningEvent, EarningStatus, EarningsAccount, PayoutPlaceholder, PayoutPlaceholderStatus
from .repositories import EarningsRepository, PayoutPlaceholderRepository, WorldsStore
from .schemas import PayoutPlaceholderCreateRequest


PAYOUT_BLOCKED_REASON = (
    "Real payouts are disabled until Stripe Connect, KYC/tax, fraud, dispute, and legal controls are complete."
)


class EarningsService:
    def __init__(self, store: WorldsStore):
        self.earnings = EarningsRepository(store)
        self.payouts = PayoutPlaceholderRepository(store)
        self.audit = AuditService(store)

    def get_or_create_account(self, user_id: str) -> EarningsAccount:
        existing = self.earnings.get_account(user_id)
        if existing:
            return existing
        return self.earnings.save_account(EarningsAccount(user_id=user_id))

    def list_events(self, user_id: str):
        return self.earnings.list_events(user_id)

    def record_approved_submission(
        self,
        *,
        user_id: str,
        submission_public_id: str,
        gross_amount: int,
        platform_fee_percent: int,
        actor_user_id: str | None = None,
    ) -> EarningEvent | None:
        if gross_amount <= 0:
            return None

        existing = [
            event
            for event in self.earnings.list_events(user_id)
            if event.source_type == "submission" and event.source_public_id == submission_public_id
        ]
        if existing:
            return existing[0]

        platform_fee_amount = round(gross_amount * platform_fee_percent / 100)
        net_amount = max(0, gross_amount - platform_fee_amount)
        event = self.earnings.create_event(
            EarningEvent(
                public_id=f"earn_{uuid4().hex[:12]}",
                user_id=user_id,
                source_type="submission",
                source_public_id=submission_public_id,
                amount=gross_amount,
                platform_fee_amount=platform_fee_amount,
                net_amount=net_amount,
                status=EarningStatus.approved,
                note="Approved marketplace earning. Payout remains disabled until payout controls are complete.",
            )
        )

        account = self.get_or_create_account(user_id)
        account.approved_amount += net_amount
        self.earnings.save_account(account)
        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="earning_approved",
            target_type="earning_event",
            target_public_id=event.public_id,
            after_state=event.status.value,
            note="Approved earning recorded from marketplace submission; no payout created.",
        )
        return event

    def create_payout_placeholder(
        self,
        *,
        user_id: str,
        payload: PayoutPlaceholderCreateRequest,
    ) -> PayoutPlaceholder:
        if payload.amount <= 0:
            raise ValidationError("Payout placeholder amount must be greater than zero.")

        account = self.get_or_create_account(user_id)
        if account.payable_amount < payload.amount:
            status = PayoutPlaceholderStatus.blocked
            blocked_reason = "Requested amount exceeds payable placeholder balance. Real payouts are disabled."
        else:
            status = PayoutPlaceholderStatus.pending_review
            blocked_reason = PAYOUT_BLOCKED_REASON

        payout = self.payouts.create(
            PayoutPlaceholder(
                public_id=f"payout_{uuid4().hex[:12]}",
                user_id=user_id,
                amount=payload.amount,
                currency=account.currency,
                status=status,
                blocked_reason=blocked_reason,
            )
        )

        self.audit.record(
            actor_user_id=user_id,
            action_type="payout_placeholder_requested",
            target_type="payout_placeholder",
            target_public_id=payout.public_id,
            after_state=payout.status.value,
            note=payload.reason,
        )
        return payout

    def list_payout_placeholders(self, user_id: str) -> list[PayoutPlaceholder]:
        return self.payouts.list_for_user(user_id)

    def assert_real_payouts_blocked(self) -> None:
        raise PayoutBlockedError(PAYOUT_BLOCKED_REASON)
