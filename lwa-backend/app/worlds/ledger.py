from __future__ import annotations

from uuid import uuid4

from .models import InternalLedgerEntry, LedgerEventType
from .repositories import LedgerRepository, WorldsStore


class LedgerService:
    def __init__(self, store: WorldsStore):
        self.ledger_repo = LedgerRepository(store)

    def record(
        self,
        *,
        event_type: LedgerEventType,
        label: str,
        user_id: str | None = None,
        amount: int | None = None,
        currency: str = "USD",
        xp: int | None = None,
        reputation: int | None = None,
        reference_id: str | None = None,
        status: str = "recorded",
    ) -> InternalLedgerEntry:
        return self.ledger_repo.create(
            InternalLedgerEntry(
                public_id=f"led_{uuid4().hex[:12]}",
                user_id=user_id,
                event_type=event_type,
                label=label,
                amount=amount,
                currency=currency,
                xp=xp,
                reputation=reputation,
                reference_id=reference_id,
                status=status,
            )
        )

    def record_campaign_created(self, user_id: str, campaign_public_id: str) -> InternalLedgerEntry:
        return self.record(
            user_id=user_id,
            event_type=LedgerEventType.campaign_created,
            label="Created marketplace campaign",
            xp=75,
            reputation=5,
            reference_id=campaign_public_id,
        )

    def record_submission_created(self, user_id: str, submission_public_id: str) -> InternalLedgerEntry:
        return self.record(
            user_id=user_id,
            event_type=LedgerEventType.submission_created,
            label="Submitted marketplace work",
            xp=50,
            reputation=3,
            reference_id=submission_public_id,
        )

    def record_submission_approved(
        self,
        user_id: str,
        submission_public_id: str,
        amount: int,
    ) -> InternalLedgerEntry:
        return self.record(
            user_id=user_id,
            event_type=LedgerEventType.earning_approved,
            label="Marketplace submission approved",
            amount=amount,
            xp=125,
            reputation=10,
            reference_id=submission_public_id,
        )

    def list_for_user(self, user_id: str) -> list[InternalLedgerEntry]:
        return self.ledger_repo.list_for_user(user_id)
