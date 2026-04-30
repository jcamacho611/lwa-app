from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from ...core.config import get_settings
from ...services.whop_entitlements import WhopEntitlementStore, verify_whop_signature

router = APIRouter(prefix="/v1/webhooks", tags=["webhooks"])
settings = get_settings()
whop_store = WhopEntitlementStore(settings.platform_db_path)


def _signature_from_request(request: Request) -> str | None:
    return (
        request.headers.get("whop-signature")
        or request.headers.get("x-whop-signature")
        or request.headers.get("x-signature")
    )


@router.post("/whop")
async def whop_webhook(request: Request) -> dict[str, object]:
    if not settings.enable_whop_verification:
        raise HTTPException(status_code=404, detail="Whop verification is not enabled")

    body = await request.body()
    signature = _signature_from_request(request)
    if not verify_whop_signature(body=body, signature=signature, secret=settings.whop_webhook_secret):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    try:
        payload = await request.json()
    except Exception as error:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from error

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Webhook payload must be an object")

    result = whop_store.process_event(payload)
    return {
        "status": "ok",
        "event_id": result.event_id,
        "event_type": result.event_type,
        "processed": result.processed,
        "replayed": result.replayed,
        "user_email": result.user_email,
        "plan": result.plan,
        "message": result.message,
    }
