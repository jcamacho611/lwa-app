from __future__ import annotations

from threading import Lock
from time import time
from typing import Any

MAX_STATUS_RECORDS = 2_000
PRIVATE_STATUS_KEYS = {"local_asset_path", "updated_at_epoch"}

_lock = Lock()
_records: dict[str, dict[str, Any]] = {}
_latest_by_clip_id: dict[str, str] = {}


def _status_key(*, request_id: str | None, clip_id: str) -> str:
    return f"{request_id}:{clip_id}" if request_id else clip_id


def _playable_url(payload: dict[str, Any]) -> str | None:
    return (
        payload.get("preview_url")
        or payload.get("edited_clip_url")
        or payload.get("clip_url")
        or payload.get("raw_clip_url")
    )


def _trim_if_needed() -> None:
    if len(_records) <= MAX_STATUS_RECORDS:
        return

    oldest_keys = sorted(_records, key=lambda key: float(_records[key].get("updated_at_epoch", 0)))
    for key in oldest_keys[: len(_records) - MAX_STATUS_RECORDS]:
        clip_id = str(_records[key].get("id") or "")
        _records.pop(key, None)
        if clip_id and _latest_by_clip_id.get(clip_id) == key:
            _latest_by_clip_id.pop(clip_id, None)


def _public_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in PRIVATE_STATUS_KEYS}


def clip_to_status_payload(
    *,
    request_id: str,
    clip: Any,
    local_asset_path: str | None = None,
) -> dict[str, Any]:
    if hasattr(clip, "model_dump"):
        payload = clip.model_dump(mode="json")
    elif isinstance(clip, dict):
        payload = dict(clip)
    else:
        payload = {}

    clip_id = str(payload.get("id") or payload.get("clip_id") or "")
    preview_url = _playable_url(payload)
    render_status = str(payload.get("render_status") or ("ready" if preview_url else "pending"))

    payload.update(
        {
            "id": clip_id,
            "clip_id": payload.get("clip_id") or clip_id,
            "request_id": payload.get("request_id") or request_id,
            "preview_url": preview_url,
            "render_status": render_status,
            "status": "ready" if render_status == "ready" else "processing",
            "is_rendered": bool(preview_url),
            "is_strategy_only": not bool(preview_url),
            "local_asset_path": local_asset_path,
        }
    )
    return payload


def save_clip_status(
    *,
    request_id: str,
    clip: Any,
    local_asset_path: str | None = None,
) -> dict[str, Any]:
    payload = clip_to_status_payload(request_id=request_id, clip=clip, local_asset_path=local_asset_path)
    clip_id = str(payload["id"])
    key = _status_key(request_id=str(payload.get("request_id") or request_id), clip_id=clip_id)
    now = time()
    payload["updated_at_epoch"] = now

    with _lock:
        _records[key] = payload
        _latest_by_clip_id[clip_id] = key
        _trim_if_needed()

    return _public_payload(payload)


def register_clip_batch(
    *,
    request_id: str,
    clips: list[Any],
    local_asset_paths: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    local_asset_paths = local_asset_paths or {}
    return [
        save_clip_status(
            request_id=request_id,
            clip=clip,
            local_asset_path=local_asset_paths.get(getattr(clip, "id", "") if not isinstance(clip, dict) else str(clip.get("id") or "")),
        )
        for clip in clips
    ]


def update_clip_status(
    *,
    clip_id: str,
    request_id: str | None = None,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    key = _status_key(request_id=request_id, clip_id=clip_id) if request_id else _latest_by_clip_id.get(clip_id, clip_id)
    with _lock:
        current = _records.get(key)
        if current is None:
            return None
        current.update(updates)
        current["updated_at_epoch"] = time()
        preview_url = _playable_url(current)
        current["preview_url"] = preview_url
        current["is_rendered"] = bool(preview_url)
        current["is_strategy_only"] = not bool(preview_url)
        if preview_url and current.get("render_status") not in {"failed"}:
            current["render_status"] = "ready"
            current["status"] = "ready"
        _records[key] = current
        return _public_payload(current)


def get_clip_status(
    *,
    clip_id: str,
    request_id: str | None = None,
    include_internal: bool = False,
) -> dict[str, Any] | None:
    key = _status_key(request_id=request_id, clip_id=clip_id) if request_id else _latest_by_clip_id.get(clip_id, clip_id)
    with _lock:
        record = _records.get(key)
        if not record:
            return None
        return dict(record) if include_internal else _public_payload(record)
