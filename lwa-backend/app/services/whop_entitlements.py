from __future__ import annotations

import hmac
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from threading import Lock
from typing import Any, Iterator


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class WhopWebhookResult:
    event_id: str
    event_type: str
    processed: bool
    replayed: bool
    user_email: str | None
    plan: str | None
    message: str


def verify_whop_signature(*, body: bytes, signature: str | None, secret: str | None) -> bool:
    if not secret:
        return False
    provided = (signature or "").strip()
    if not provided:
        return False
    expected = hmac.new(secret.encode("utf-8"), body, sha256).hexdigest()
    candidates = {provided}
    if provided.startswith("sha256="):
        candidates.add(provided.split("=", 1)[1])
    return any(hmac.compare_digest(candidate, expected) for candidate in candidates)


def extract_event_id(payload: dict[str, Any]) -> str:
    return str(payload.get("id") or payload.get("event_id") or payload.get("webhook_id") or "").strip()


def extract_event_type(payload: dict[str, Any]) -> str:
    return str(payload.get("type") or payload.get("event") or payload.get("event_type") or "unknown").strip()


def extract_user_email(payload: dict[str, Any]) -> str | None:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    candidates = [
        data.get("email") if isinstance(data, dict) else None,
        data.get("user_email") if isinstance(data, dict) else None,
        data.get("customer_email") if isinstance(data, dict) else None,
        data.get("member", {}).get("email") if isinstance(data, dict) and isinstance(data.get("member"), dict) else None,
        data.get("user", {}).get("email") if isinstance(data, dict) and isinstance(data.get("user"), dict) else None,
    ]
    for candidate in candidates:
        value = str(candidate or "").strip().lower()
        if value and "@" in value:
            return value
    return None


def plan_for_event(event_type: str) -> str | None:
    normalized = event_type.strip().lower()
    valid_terms = ("valid", "paid", "succeeded", "active", "created", "renewed")
    invalid_terms = ("invalid", "cancel", "failed", "expired", "deleted", "refunded", "chargeback")
    if any(term in normalized for term in invalid_terms):
        return "free"
    if any(term in normalized for term in valid_terms):
        return "pro"
    return None


class WhopEntitlementStore:
    def __init__(self, path: str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self._path, check_same_thread=False)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS whop_webhook_events (
                    id TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_email TEXT,
                    plan TEXT,
                    payload_json TEXT NOT NULL,
                    processed_at TEXT NOT NULL
                );
                """
            )

    def process_event(self, payload: dict[str, Any]) -> WhopWebhookResult:
        event_id = extract_event_id(payload)
        if not event_id:
            event_id = sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        event_type = extract_event_type(payload)
        user_email = extract_user_email(payload)
        plan = plan_for_event(event_type)
        processed_at = utcnow()
        payload_json = json.dumps(payload, sort_keys=True)

        with self._lock, self._connect() as connection:
            existing = connection.execute(
                "SELECT id, event_type, user_email, plan FROM whop_webhook_events WHERE id = ?",
                (event_id,),
            ).fetchone()
            if existing:
                return WhopWebhookResult(
                    event_id=event_id,
                    event_type=str(existing["event_type"]),
                    processed=False,
                    replayed=True,
                    user_email=existing["user_email"],
                    plan=existing["plan"],
                    message="Webhook event already processed.",
                )

            connection.execute(
                """
                INSERT INTO whop_webhook_events (id, event_type, user_email, plan, payload_json, processed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (event_id, event_type, user_email, plan, payload_json, processed_at),
            )

            if user_email and plan:
                connection.execute("UPDATE users SET plan = ? WHERE email = ?", (plan, user_email))

        return WhopWebhookResult(
            event_id=event_id,
            event_type=event_type,
            processed=True,
            replayed=False,
            user_email=user_email,
            plan=plan,
            message="Webhook processed." if plan else "Webhook stored; no entitlement change required.",
        )
