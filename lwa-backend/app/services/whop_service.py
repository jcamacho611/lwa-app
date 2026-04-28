from __future__ import annotations

from dataclasses import dataclass

from ..core.config import Settings


@dataclass(frozen=True)
class WhopVerificationState:
    enabled: bool
    configured: bool
    status: str
    missing_fields: tuple[str, ...]
    fallback_mode: str = "free_or_api_key"
    api_key_present: bool = False
    company_id_present: bool = False
    product_id_present: bool = False
    webhook_secret_present: bool = False

    def as_dict(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "configured": self.configured,
            "status": self.status,
            "missing_fields": list(self.missing_fields),
            "fallback_mode": self.fallback_mode,
            "api_key_present": self.api_key_present,
            "company_id_present": self.company_id_present,
            "product_id_present": self.product_id_present,
            "webhook_secret_present": self.webhook_secret_present,
        }


REQUIRED_VERIFICATION_FIELDS: tuple[tuple[str, str], ...] = (
    ("api_key", "WHOP_API_KEY"),
    ("company_id", "WHOP_COMPANY_ID"),
    ("product_id", "WHOP_PRODUCT_ID"),
)


def describe_whop_verification_state(settings: Settings) -> WhopVerificationState:
    field_values = {
        "api_key": bool((settings.whop_api_key or "").strip()),
        "company_id": bool((settings.whop_company_id or "").strip()),
        "product_id": bool((getattr(settings, "whop_product_id", "") or "").strip()),
        "webhook_secret": bool((getattr(settings, "whop_webhook_secret", "") or "").strip()),
    }
    missing_fields = tuple(
        env_name
        for field_name, env_name in REQUIRED_VERIFICATION_FIELDS
        if not field_values[field_name]
    )

    if not getattr(settings, "enable_whop_verification", False):
        return WhopVerificationState(
            enabled=False,
            configured=not missing_fields,
            status="disabled",
            missing_fields=missing_fields,
            api_key_present=field_values["api_key"],
            company_id_present=field_values["company_id"],
            product_id_present=field_values["product_id"],
            webhook_secret_present=field_values["webhook_secret"],
        )

    if missing_fields:
        return WhopVerificationState(
            enabled=True,
            configured=False,
            status="missing-config",
            missing_fields=missing_fields,
            api_key_present=field_values["api_key"],
            company_id_present=field_values["company_id"],
            product_id_present=field_values["product_id"],
            webhook_secret_present=field_values["webhook_secret"],
        )

    return WhopVerificationState(
        enabled=True,
        configured=True,
        status="configured",
        missing_fields=(),
        api_key_present=field_values["api_key"],
        company_id_present=field_values["company_id"],
        product_id_present=field_values["product_id"],
        webhook_secret_present=field_values["webhook_secret"],
    )


def build_whop_provider_health(settings: Settings) -> dict[str, object]:
    state = describe_whop_verification_state(settings)
    payload = state.as_dict()
    payload["mode"] = (
        "verification"
        if state.enabled and state.configured
        else "free_or_api_key_fallback"
    )
    payload["webhook_sync_ready"] = bool(state.webhook_secret_present)
    return payload
