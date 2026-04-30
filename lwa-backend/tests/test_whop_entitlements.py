import hmac
import json
from hashlib import sha256
from pathlib import Path

from app.auth.security import hash_password
from app.services.platform_store import PlatformStore
from app.services.whop_entitlements import (
    WhopEntitlementStore,
    extract_user_email,
    plan_for_event,
    verify_whop_signature,
)


def sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()


def test_verify_whop_signature_accepts_hex_and_prefixed_signature() -> None:
    body = b'{"id":"evt_1"}'
    secret = "test-secret"
    signature = sign(body, secret)
    assert verify_whop_signature(body=body, signature=signature, secret=secret)
    assert verify_whop_signature(body=body, signature=f"sha256={signature}", secret=secret)
    assert not verify_whop_signature(body=body, signature="bad", secret=secret)


def test_extract_user_email_from_common_payload_shapes() -> None:
    assert extract_user_email({"data": {"member": {"email": "USER@EXAMPLE.COM"}}}) == "user@example.com"
    assert extract_user_email({"data": {"user": {"email": "user@example.com"}}}) == "user@example.com"
    assert extract_user_email({"data": {"customer_email": "user@example.com"}}) == "user@example.com"


def test_plan_for_event_maps_valid_and_invalid_memberships() -> None:
    assert plan_for_event("membership.went_valid") == "pro"
    assert plan_for_event("payment.succeeded") == "pro"
    assert plan_for_event("membership.went_invalid") == "free"
    assert plan_for_event("payment.failed") == "free"
    assert plan_for_event("unknown.event") is None


def test_whop_event_is_idempotent_and_updates_user_plan(tmp_path: Path) -> None:
    db_path = str(tmp_path / "platform.sqlite3")
    platform_store = PlatformStore(db_path)
    platform_store.create_user(
        email="buyer@example.com",
        password_hash=hash_password("password123"),
        plan="free",
    )
    whop_store = WhopEntitlementStore(db_path)

    payload = {
        "id": "evt_123",
        "type": "membership.went_valid",
        "data": {"member": {"email": "buyer@example.com"}},
    }

    result = whop_store.process_event(payload)
    assert result.processed is True
    assert result.replayed is False
    assert result.plan == "pro"
    assert platform_store.get_user_by_email("buyer@example.com").plan == "pro"

    replay = whop_store.process_event(payload)
    assert replay.processed is False
    assert replay.replayed is True
    assert platform_store.get_user_by_email("buyer@example.com").plan == "pro"


def test_whop_invalid_event_downgrades_user_to_free(tmp_path: Path) -> None:
    db_path = str(tmp_path / "platform.sqlite3")
    platform_store = PlatformStore(db_path)
    platform_store.create_user(
        email="buyer@example.com",
        password_hash=hash_password("password123"),
        plan="pro",
    )
    whop_store = WhopEntitlementStore(db_path)

    payload = {
        "id": "evt_124",
        "type": "membership.went_invalid",
        "data": {"member": {"email": "buyer@example.com"}},
    }

    result = whop_store.process_event(payload)
    assert result.processed is True
    assert result.plan == "free"
    assert platform_store.get_user_by_email("buyer@example.com").plan == "free"


def test_event_without_email_is_stored_without_entitlement_change(tmp_path: Path) -> None:
    db_path = str(tmp_path / "platform.sqlite3")
    whop_store = WhopEntitlementStore(db_path)
    payload = {"id": "evt_no_email", "type": "payment.succeeded", "data": {}}
    result = whop_store.process_event(payload)
    assert result.processed is True
    assert result.user_email is None
    assert result.plan == "pro"
    assert "processed" in result.message.lower()


def test_signature_matches_json_body() -> None:
    payload = {"id": "evt_json", "type": "payment.succeeded"}
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    secret = "secret"
    assert verify_whop_signature(body=body, signature=sign(body, secret), secret=secret)
