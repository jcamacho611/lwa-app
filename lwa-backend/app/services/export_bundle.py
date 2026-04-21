from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from ..core.config import Settings


def _safe_name(value: str) -> str:
    normalized = "".join(character.lower() if character.isalnum() else "-" for character in value)
    normalized = "-".join(part for part in normalized.split("-") if part)
    return normalized[:72] or "clip-pack"


def create_export_bundle(
    *,
    settings: Settings,
    public_base_url: str,
    source_url: str,
    clips: list[dict[str, Any]],
) -> dict[str, Any]:
    export_dir = Path(settings.generated_assets_dir) / "export-bundles"
    export_dir.mkdir(parents=True, exist_ok=True)

    bundle_id = f"bundle_{uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    title_seed = str((clips[0] or {}).get("title") or "clip-pack") if clips else "clip-pack"
    file_name = f"{_safe_name(title_seed)}-{bundle_id[-8:]}.json"
    file_path = export_dir / file_name

    payload = {
        "bundle_id": bundle_id,
        "created_at": created_at,
        "source_url": source_url,
        "clip_count": len(clips),
        "clips": clips,
    }
    file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    public_base = public_base_url.rstrip("/")
    return {
        "bundle_id": bundle_id,
        "download_url": f"{public_base}/generated/export-bundles/{file_name}",
        "file_name": file_name,
        "clip_count": len(clips),
        "created_at": created_at,
    }
