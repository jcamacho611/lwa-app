from __future__ import annotations

from dataclasses import dataclass


PLAN_ORDER = ["free", "creator", "pro", "agency", "enterprise", "founder"]


@dataclass(frozen=True, slots=True)
class GateResult:
    allowed: bool
    plan_key: str
    required_plan: str
    reason: str


def plan_rank(plan_key: str) -> int:
    try:
        return PLAN_ORDER.index(plan_key)
    except ValueError:
        return 0


def require_min_plan(plan_key: str, required_plan: str) -> GateResult:
    allowed = plan_rank(plan_key) >= plan_rank(required_plan)
    reason = "Allowed." if allowed else f"Requires {required_plan} plan or higher."
    return GateResult(
        allowed=allowed,
        plan_key=plan_key,
        required_plan=required_plan,
        reason=reason,
    )


def can_create_campaign(plan_key: str, existing_count: int) -> GateResult:
    minimum = "free"
    limits = {
        "free": 1,
        "creator": 5,
        "pro": 20,
        "agency": 100,
        "enterprise": 500,
        "founder": 250,
    }
    limit = limits.get(plan_key, limits["free"])
    allowed = existing_count < limit
    reason = "Allowed." if allowed else f"Campaign limit reached for {plan_key} plan."
    return GateResult(allowed=allowed, plan_key=plan_key, required_plan=minimum, reason=reason)


def can_create_ugc_asset(plan_key: str, existing_count: int) -> GateResult:
    minimum = "free"
    limits = {
        "free": 3,
        "creator": 25,
        "pro": 100,
        "agency": 500,
        "enterprise": 2000,
        "founder": 1000,
    }
    limit = limits.get(plan_key, limits["free"])
    allowed = existing_count < limit
    reason = "Allowed." if allowed else f"UGC asset limit reached for {plan_key} plan."
    return GateResult(allowed=allowed, plan_key=plan_key, required_plan=minimum, reason=reason)
