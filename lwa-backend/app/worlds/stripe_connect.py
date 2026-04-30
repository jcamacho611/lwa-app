from __future__ import annotations

import os


REQUIRED_STRIPE_CONNECT_ENV_VARS = [
    "STRIPE_SECRET_KEY",
    "STRIPE_WEBHOOK_SECRET",
    "STRIPE_CONNECT_CLIENT_ID",
]


def stripe_connect_readiness() -> dict:
    missing = [key for key in REQUIRED_STRIPE_CONNECT_ENV_VARS if not os.getenv(key)]
    real_payouts_enabled = os.getenv("LWA_REAL_PAYOUTS_ENABLED", "false").lower() == "true"
    blockers = [
        "Stripe Connect transfers are not implemented.",
        "KYC/tax onboarding is not implemented.",
        "Dispute and fraud holds are placeholders only.",
        "Payout idempotency and reconciliation are not complete.",
    ]
    if missing:
        blockers.append("Required Stripe Connect environment variables are missing.")
    if real_payouts_enabled:
        blockers.append("LWA_REAL_PAYOUTS_ENABLED is true before payout controls are complete.")

    return {
        "enabled": real_payouts_enabled,
        "ready": False,
        "required_env_vars": REQUIRED_STRIPE_CONNECT_ENV_VARS,
        "missing_env_vars": missing,
        "blockers": blockers,
        "note": "Stripe Connect is readiness-only. No real payouts or transfers are performed.",
    }
