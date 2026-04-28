from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from ..core.config import Settings

logger = logging.getLogger("uvicorn.error")
_REDACTED_KEYS = {"api_key", "token", "secret", "authorization"}


def emit_event(
    *,
    settings: Settings,
    event: str,
    request_id: str | None = None,
    plan_code: str | None = None,
    subject_source: str | None = None,
    status: str = "ok",
    metadata: dict[str, Any] | None = None,
) -> None:
    if not getattr(settings, "event_log_enabled", True):
        return

    try:
        path = Path(settings.event_log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        _trim_log_if_oversized(
            path=path,
            max_bytes=max(int(getattr(settings, "event_log_max_bytes", 10_485_760)), 1),
        )
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "request_id": request_id,
            "plan_code": plan_code,
            "subject_source": subject_source,
            "status": status,
            "metadata": _sanitize_metadata(
                metadata or {},
                max_chars=max(getattr(settings, "event_log_max_metadata_chars", 2000), 1),
            ),
        }
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
        _trim_log_if_oversized(
            path=path,
            max_bytes=max(int(getattr(settings, "event_log_max_bytes", 10_485_760)), 1),
        )
    except Exception as error:
        logger.warning("event_log_write_failed event=%s error=%s", event, error)


def _trim_log_if_oversized(*, path: Path, max_bytes: int) -> None:
    if not path.exists():
        return
    try:
        if path.stat().st_size <= max_bytes:
            return
        keep_bytes = max_bytes // 2
        with path.open("rb") as handle:
            handle.seek(-keep_bytes, 2)
            tail = handle.read()
        newline_index = tail.find(b"\n")
        trimmed = tail[newline_index + 1 :] if newline_index >= 0 else tail
        path.write_bytes(trimmed)
    except OSError:
        raise


def _sanitize_metadata(metadata: dict[str, Any], *, max_chars: int) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, value in metadata.items():
        lowered = str(key).lower()
        if any(marker in lowered for marker in _REDACTED_KEYS):
            sanitized[key] = "[redacted]"
            continue
        sanitized[key] = _sanitize_value(key=lowered, value=value, max_chars=max_chars)
    return sanitized


def _sanitize_value(*, key: str, value: Any, max_chars: int) -> Any:
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, dict):
        return {
            str(child_key): _sanitize_value(key=f"{key}.{child_key}".lower(), value=child_value, max_chars=max_chars)
            for child_key, child_value in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_value(key=key, value=item, max_chars=max_chars) for item in value[:20]]

    text = str(value).strip()
    if not text:
        return ""
    if "url" in key and text.startswith(("http://", "https://")):
        return f"url_hash:{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"
    if len(text) > max_chars:
        return text[: max_chars - 1] + "…"
    return text
