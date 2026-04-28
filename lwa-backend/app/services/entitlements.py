from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from threading import Lock

from fastapi import HTTPException, Request

from ..core.config import Settings
from ..models.schemas import FeatureFlags
from ..models.user import UserRecord
from .event_log import emit_event


def usage_day_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def normalize_header_value(value: str | None) -> str:
    return (value or "").strip()


def stable_hash(value: str) -> str:
    normalized = normalize_header_value(value)
    if not normalized:
        return "anonymous"
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class PlanDefinition:
    code: str
    name: str
    daily_limit: int
    feature_flags: FeatureFlags


@dataclass(frozen=True)
class EntitlementContext:
    subject: str
    subject_source: str
    usage_day: str
    plan: PlanDefinition
    credits_remaining: int
    user_id: str | None = None


class UsageStore:
    def __init__(self, path: str, retention_days: int = 14) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._retention_days = retention_days

    def reserve(
        self,
        *,
        subject: str,
        daily_limit: int,
        error_detail: dict[str, object] | None = None,
    ) -> tuple[str, int]:
        usage_day = usage_day_key()
        with self._lock:
            payload = self._load()
            self._trim(payload)
            day_bucket = payload.setdefault(usage_day, {})
            current = int(day_bucket.get(subject, 0))
            if daily_limit >= 0 and current >= daily_limit:
                raise HTTPException(
                    status_code=402,
                    detail=error_detail or {
                        "code": "quota_exceeded",
                        "message": (
                            "Daily generation limit reached for the current plan. "
                            "Add a paid API key in Settings or upgrade on the web before running more jobs."
                        ),
                        "plan": "current",
                        "credits_remaining": 0,
                        "upgrade_hint": (
                            "Upgrade to Pro for more runs and premium packaging, "
                            "or Scale for higher-volume campaign workflows."
                        ),
                    },
                )

            updated = current + 1
            day_bucket[subject] = updated
            self._save(payload)

        if daily_limit < 0:
            return usage_day, 9999

        return usage_day, max(daily_limit - updated, 0)

    def release(self, *, subject: str, usage_day: str) -> None:
        with self._lock:
            payload = self._load()
            day_bucket = payload.get(usage_day)
            if not day_bucket or subject not in day_bucket:
                return

            updated = max(int(day_bucket[subject]) - 1, 0)
            if updated == 0:
                del day_bucket[subject]
            else:
                day_bucket[subject] = updated

            if not day_bucket:
                payload.pop(usage_day, None)

            self._save(payload)

    def _load(self) -> dict[str, dict[str, int]]:
        if not self._path.exists():
            return {}

        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _save(self, payload: dict[str, dict[str, int]]) -> None:
        temp_path = self._path.with_suffix(f"{self._path.suffix}.tmp")
        temp_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
        temp_path.replace(self._path)

    def _trim(self, payload: dict[str, dict[str, int]]) -> None:
        if len(payload) <= self._retention_days:
            return

        overflow = len(payload) - self._retention_days
        for usage_day in sorted(payload.keys())[:overflow]:
            payload.pop(usage_day, None)


def resolve_entitlement(
    *,
    request: Request,
    settings: Settings,
    usage_store: UsageStore,
    current_user: UserRecord | None = None,
) -> EntitlementContext:
    api_key = normalize_header_value(request.headers.get(settings.api_key_header_name))
    client_id = normalize_header_value(request.headers.get(settings.client_id_header_name))

    if api_key and api_key in settings.scale_api_keys:
        plan = build_scale_plan(settings)
        subject = f"scale:{stable_hash(api_key)}"
        subject_source = "scale_api_key"
    elif api_key and api_key in settings.pro_api_keys:
        plan = build_pro_plan(settings)
        subject = f"pro:{stable_hash(api_key)}"
        subject_source = "pro_api_key"
    elif current_user:
        plan = build_plan_from_user(settings, current_user.plan)
        subject = f"user:{current_user.id}"
        subject_source = "user"
    else:
        plan = build_free_plan(settings)
        # Client ID is a quota hint, not an authenticated identity.
        if client_id:
            subject = f"client:{stable_hash(client_id)}"
            subject_source = "client_id"
        else:
            remote_host = request.client.host if request.client else "anonymous"
            subject = f"ip:{stable_hash(remote_host)}"
            subject_source = "remote_ip"

    try:
        usage_day, credits_remaining = usage_store.reserve(
            subject=subject,
            daily_limit=plan.daily_limit,
            error_detail=build_quota_exceeded_detail(plan),
        )
    except HTTPException as error:
        if error.status_code == 402:
            emit_event(
                settings=settings,
                event="quota_exceeded",
                plan_code=plan.code,
                subject_source=subject_source,
                status="blocked",
                metadata={
                    "daily_limit": plan.daily_limit,
                    "client_hint": "present" if client_id else "missing",
                },
            )
        raise

    emit_event(
        settings=settings,
        event="quota_reserved",
        plan_code=plan.code,
        subject_source=subject_source,
        status="ok",
        metadata={
            "daily_limit": plan.daily_limit,
            "credits_remaining": credits_remaining,
        },
    )
    return EntitlementContext(
        subject=subject,
        subject_source=subject_source,
        usage_day=usage_day,
        plan=plan,
        credits_remaining=credits_remaining,
        user_id=current_user.id if current_user else None,
    )


def get_plan_for_user(*, settings: Settings, user: UserRecord) -> PlanDefinition:
    return build_plan_from_user(settings, user.plan)


def require_feature_access(
    *,
    settings: Settings,
    user: UserRecord,
    feature_name: str,
    detail: str,
) -> PlanDefinition:
    plan = get_plan_for_user(settings=settings, user=user)
    if bool(getattr(plan.feature_flags, feature_name, False)):
        return plan
    raise HTTPException(status_code=403, detail=detail)


def build_free_plan(settings: Settings) -> PlanDefinition:
    return PlanDefinition(
        code="free",
        name=settings.default_plan_name,
        daily_limit=settings.free_daily_limit,
        feature_flags=FeatureFlags(
            clip_limit=3,
            alt_hooks=False,
            campaign_mode=False,
            packaging_profiles=False,
            history_limit=10,
            caption_editor=False,
            timeline_editor=False,
            wallet_view=False,
            posting_queue=False,
            max_uploads_per_day=2,
            max_generations_per_day=settings.free_daily_limit,
            premium_exports=False,
            priority_processing=False,
        ),
    )


def build_pro_plan(settings: Settings) -> PlanDefinition:
    return PlanDefinition(
        code="pro",
        name="Pro",
        daily_limit=settings.pro_daily_limit,
        feature_flags=FeatureFlags(
            clip_limit=20,
            alt_hooks=True,
            campaign_mode=False,
            packaging_profiles=True,
            history_limit=25,
            caption_editor=True,
            timeline_editor=True,
            wallet_view=True,
            posting_queue=False,
            max_uploads_per_day=25,
            max_generations_per_day=settings.pro_daily_limit,
            premium_exports=True,
            priority_processing=True,
        ),
    )


def build_scale_plan(settings: Settings) -> PlanDefinition:
    return PlanDefinition(
        code="scale",
        name="Scale",
        daily_limit=settings.scale_daily_limit,
        feature_flags=FeatureFlags(
            clip_limit=40,
            alt_hooks=True,
            campaign_mode=True,
            packaging_profiles=True,
            history_limit=100,
            caption_editor=True,
            timeline_editor=True,
            wallet_view=True,
            posting_queue=True,
            max_uploads_per_day=100,
            max_generations_per_day=settings.scale_daily_limit,
            premium_exports=True,
            priority_processing=True,
        ),
    )


def build_plan_from_user(settings: Settings, plan_code: str) -> PlanDefinition:
    normalized = (plan_code or "free").strip().lower()
    if normalized == "scale":
        return build_scale_plan(settings)
    if normalized == "pro":
        return build_pro_plan(settings)
    return build_free_plan(settings)


def build_quota_exceeded_detail(plan: PlanDefinition) -> dict[str, object]:
    return {
        "code": "quota_exceeded",
        "message": (
            "You've used today's free generations." if plan.code == "free" else
            f"You've used today's {plan.name} generations."
        ),
        "plan": plan.name,
        "plan_code": plan.code,
        "credits_remaining": 0,
        "upgrade_hint": (
            "Upgrade or add your paid API key to keep generating. "
            "Your saved results are still available."
        ),
    }
