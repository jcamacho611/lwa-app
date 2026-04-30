from __future__ import annotations

from dataclasses import dataclass

from .errors import ValidationError


@dataclass(frozen=True, slots=True)
class BillingPlan:
    plan_key: str
    name: str
    monthly_price_amount: int
    monthly_credits: int
    marketplace_fee_percent: int
    max_campaigns: int
    max_ugc_assets: int
    features: tuple[str, ...]
    currency: str = "USD"


PLANS: tuple[BillingPlan, ...] = (
    BillingPlan(
        plan_key="free",
        name="Free",
        monthly_price_amount=0,
        monthly_credits=25,
        marketplace_fee_percent=30,
        max_campaigns=1,
        max_ugc_assets=3,
        features=("Upload-first clipping demo", "Mock fallback", "Basic marketplace preview"),
    ),
    BillingPlan(
        plan_key="creator",
        name="Creator",
        monthly_price_amount=1900,
        monthly_credits=250,
        marketplace_fee_percent=25,
        max_campaigns=5,
        max_ugc_assets=25,
        features=("Creator clip packages", "Campaign-ready exports", "UGC marketplace foundation"),
    ),
    BillingPlan(
        plan_key="pro",
        name="Pro",
        monthly_price_amount=4900,
        monthly_credits=900,
        marketplace_fee_percent=20,
        max_campaigns=20,
        max_ugc_assets=100,
        features=("Higher credit limits", "Advanced campaign workflow", "Lower marketplace fee"),
    ),
    BillingPlan(
        plan_key="agency",
        name="Agency",
        monthly_price_amount=14900,
        monthly_credits=3500,
        marketplace_fee_percent=15,
        max_campaigns=100,
        max_ugc_assets=500,
        features=("Agency-scale campaigns", "Team-ready operating model", "Priority review foundation"),
    ),
    BillingPlan(
        plan_key="enterprise",
        name="Enterprise",
        monthly_price_amount=49900,
        monthly_credits=12000,
        marketplace_fee_percent=12,
        max_campaigns=500,
        max_ugc_assets=2000,
        features=("Custom controls", "Private workflow planning", "Enterprise support path"),
    ),
    BillingPlan(
        plan_key="founder",
        name="Founder",
        monthly_price_amount=0,
        monthly_credits=5000,
        marketplace_fee_percent=10,
        max_campaigns=250,
        max_ugc_assets=1000,
        features=("Founder access", "Expanded credits", "Lowest marketplace fee foundation"),
    ),
)


def list_plans() -> list[BillingPlan]:
    return list(PLANS)


def get_plan(plan_key: str) -> BillingPlan:
    for plan in PLANS:
        if plan.plan_key == plan_key:
            return plan
    raise ValidationError("Unknown billing plan.")


def quote_marketplace_fee(gross_amount: int, plan_key: str) -> dict:
    if gross_amount <= 0:
        raise ValidationError("Gross amount must be greater than zero.")

    plan = get_plan(plan_key)
    platform_fee_amount = round(gross_amount * plan.marketplace_fee_percent / 100)
    net_amount = max(0, gross_amount - platform_fee_amount)

    return {
        "gross_amount": gross_amount,
        "platform_fee_percent": plan.marketplace_fee_percent,
        "platform_fee_amount": platform_fee_amount,
        "net_amount": net_amount,
        "currency": plan.currency,
        "note": "Fee quote is informational until marketplace payments are fully connected.",
    }
