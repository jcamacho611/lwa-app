from __future__ import annotations

from uuid import uuid4

from .audit import AuditService
from .errors import ValidationError
from .ledger import LedgerService
from .models import CreditBalance, CreditTransaction, CreditTransactionType, LedgerEventType, UsageEvent, UsageEventStatus
from .pricing import get_plan
from .repositories import CreditRepository, UsageEventRepository, WorldsStore, utcnow
from .schemas import CreditSpendRequest


class CreditService:
    def __init__(self, store: WorldsStore):
        self.credits = CreditRepository(store)
        self.usage_events = UsageEventRepository(store)
        self.audit = AuditService(store)
        self.ledger = LedgerService(store)

    def get_or_create_balance(self, *, user_id: str, plan_key: str = "free") -> CreditBalance:
        existing = self.credits.get_balance(user_id)
        if existing:
            return existing

        plan = get_plan(plan_key)
        now = utcnow()
        balance = CreditBalance(
            user_id=user_id,
            balance=plan.monthly_credits,
            monthly_grant=plan.monthly_credits,
            used_this_period=0,
            period_start=now,
            updated_at=now,
        )
        saved = self.credits.save_balance(balance)
        self._record_transaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.grant,
            amount=plan.monthly_credits,
            balance_after=saved.balance,
            reason=f"Initial {plan.plan_key} monthly grant.",
            source_type="plan",
            source_public_id=plan.plan_key,
        )
        return saved

    def grant_credits(
        self,
        *,
        user_id: str,
        amount: int,
        reason: str,
        actor_user_id: str | None,
    ) -> CreditBalance:
        if amount <= 0:
            raise ValidationError("Credit grant amount must be greater than zero.")

        balance = self.get_or_create_balance(user_id=user_id)
        balance.balance += amount
        saved = self.credits.save_balance(balance)
        transaction = self._record_transaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.grant,
            amount=amount,
            balance_after=saved.balance,
            reason=reason,
            source_type="admin_grant",
            source_public_id=actor_user_id,
        )
        self.ledger.record(
            event_type=LedgerEventType.credit_granted,
            label="Credits granted",
            user_id=user_id,
            amount=amount,
            reference_id=transaction.public_id,
        )
        self.audit.record(
            actor_user_id=actor_user_id,
            action_type="credits_granted",
            target_type="credit_balance",
            target_public_id=user_id,
            after_state=str(saved.balance),
            note=reason,
        )
        return saved

    def spend_credits(self, *, user_id: str, payload: CreditSpendRequest) -> CreditBalance:
        balance = self.get_or_create_balance(user_id=user_id)
        if payload.amount <= 0:
            raise ValidationError("Credit spend amount must be greater than zero.")
        if balance.balance < payload.amount:
            raise ValidationError("Insufficient credits.")

        before = balance.balance
        balance.balance -= payload.amount
        balance.used_this_period += payload.amount
        saved = self.credits.save_balance(balance)

        usage = self.usage_events.create(
            UsageEvent(
                public_id=f"use_{uuid4().hex[:12]}",
                user_id=user_id,
                feature_key=payload.feature_key,
                amount=payload.amount,
                status=UsageEventStatus.recorded,
                source_type=payload.source_type,
                source_public_id=payload.source_public_id,
            )
        )
        transaction = self._record_transaction(
            user_id=user_id,
            transaction_type=CreditTransactionType.spend,
            amount=-payload.amount,
            balance_after=saved.balance,
            reason=payload.reason,
            source_type=payload.source_type or "usage_event",
            source_public_id=payload.source_public_id or usage.public_id,
        )
        self.ledger.record(
            event_type=LedgerEventType.credit_spent,
            label=f"Credits spent: {payload.feature_key}",
            user_id=user_id,
            amount=-payload.amount,
            reference_id=transaction.public_id,
        )
        self.audit.record(
            actor_user_id=user_id,
            action_type="credits_spent",
            target_type="credit_balance",
            target_public_id=user_id,
            before_state=str(before),
            after_state=str(saved.balance),
            note=payload.reason,
        )
        return saved

    def list_transactions(self, user_id: str) -> list[CreditTransaction]:
        return self.credits.list_transactions(user_id)

    def _record_transaction(
        self,
        *,
        user_id: str,
        transaction_type: CreditTransactionType,
        amount: int,
        balance_after: int,
        reason: str,
        source_type: str | None = None,
        source_public_id: str | None = None,
    ) -> CreditTransaction:
        return self.credits.create_transaction(
            CreditTransaction(
                public_id=f"credtx_{uuid4().hex[:12]}",
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                balance_after=balance_after,
                reason=reason,
                source_type=source_type,
                source_public_id=source_public_id,
            )
        )
