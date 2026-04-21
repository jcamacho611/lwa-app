from __future__ import annotations

import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import Settings
logger = logging.getLogger("uvicorn.error")


class OutputBuilder:
    """Service for building export bundles and output packages."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    async def create_clip_bundle(
        self,
        *,
        request_id: str,
        clips: List[Dict[str, Any]],
        bundle_format: str = "zip",
        include_metadata: bool = True,
    ) -> Dict[str, Any]:
        """Create a downloadable bundle from processed clips."""
        try:
            bundle_id = f"bundle_{uuid4().hex[:12]}"
            created_at = datetime.now(timezone.utc).isoformat()
            generated_dir = Path(self.settings.generated_assets_dir)
            request_bundle_dir = generated_dir / "bundles" / request_id
            bundle_dir = request_bundle_dir / bundle_id
            bundle_dir.mkdir(parents=True, exist_ok=True)
            
            metadata = {
                "request_id": request_id,
                "bundle_id": bundle_id,
                "created_at": created_at,
                "clip_count": len(clips),
                "bundle_format": bundle_format,
                "clips": clips,
            }

            metadata_path = bundle_dir / "metadata.json"
            readme_path = bundle_dir / "README.md"
            if include_metadata:
                metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            readme_path.write_text(
                self._build_readme(request_id=request_id, bundle_id=bundle_id, clips=clips, created_at=created_at),
                encoding="utf-8",
            )
            
            if bundle_format.lower() == "zip":
                bundle_path = request_bundle_dir / f"{bundle_id}.zip"
                with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle_zip:
                    for bundle_file in bundle_dir.iterdir():
                        if bundle_file.is_file():
                            bundle_zip.write(bundle_file, bundle_file.name)

                    for clip in clips:
                        clip_id = clip.get("id", "")
                        for field_name, suffix in (
                            ("preview_url", "preview"),
                            ("download_url", "download"),
                            ("edited_clip_url", "edited"),
                            ("clip_url", "clip"),
                            ("raw_clip_url", "raw"),
                        ):
                            asset_path = self._local_asset_path(clip.get(field_name))
                            if asset_path:
                                safe_clip_id = "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in str(clip_id or "clip"))
                                bundle_zip.write(asset_path, f"media/{safe_clip_id}_{suffix}{asset_path.suffix}")
            else:
                manifest_path = bundle_dir / f"{bundle_id}.json"
                manifest_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
                bundle_path = manifest_path
            
            return {
                "bundle_id": bundle_id,
                "file_name": bundle_path.name,
                "bundle_path": str(bundle_path),
                "bundle_dir": str(bundle_dir),
                "metadata_path": str(metadata_path),
                "readme_path": str(readme_path),
                "download_url": self._public_generated_url(bundle_path),
                "clip_count": len(clips),
                "created_at": created_at,
                "size_bytes": bundle_path.stat().st_size if bundle_path.exists() else 0,
            }
            
        except Exception as error:
            logger.error(f"output_builder_failed request_id={request_id} error={str(error)}")
            raise

    def _local_asset_path(self, value: object) -> Optional[Path]:
        if not isinstance(value, str) or not value.strip():
            return None

        candidate = value.strip()
        if candidate.startswith(("http://", "https://", "/generated/", "/uploads/")):
            return None

        path = Path(candidate)
        return path if path.exists() and path.is_file() else None

    def _public_generated_url(self, path: Path) -> str:
        generated_dir = Path(self.settings.generated_assets_dir).resolve()
        try:
            relative = path.resolve().relative_to(generated_dir)
        except ValueError:
            relative = path.name
        public_path = f"/generated/{relative.as_posix() if isinstance(relative, Path) else relative}"
        if self.settings.api_base_url:
            return f"{self.settings.api_base_url.rstrip('/')}{public_path}"
        return public_path

    def _build_readme(self, *, request_id: str, bundle_id: str, clips: List[Dict[str, Any]], created_at: str) -> str:
        lines = [
            f"# Clip Bundle {bundle_id}",
            "",
            f"Request: {request_id}",
            f"Generated: {created_at}",
            f"Total clips: {len(clips)}",
            "",
            "## Usage",
            "1. Review metadata.json for hooks, captions, timestamps, scores, and asset URLs.",
            "2. Use media files when local rendered assets were available in this bundle.",
            "3. Use the clip order and post rank fields to decide what ships first.",
            "",
        ]
        for index, clip in enumerate(clips, start=1):
            lines.extend(
                [
                    f"## Clip {index}",
                    f"- Title: {clip.get('title', 'Untitled')}",
                    f"- Hook: {clip.get('hook', '')}",
                    f"- Caption: {clip.get('caption', '')}",
                    f"- Score: {clip.get('score', '')}",
                    f"- Post rank: {clip.get('post_rank', '')}",
                    "",
                ]
            )
        return "\n".join(lines)
    
    def create_export_manifest(
        self,
        *,
        request_id: str,
        clips: List[Dict[str, Any]],
        export_format: str = "json",
    ) -> Dict[str, Any]:
        """Create an export manifest for batch processing."""
        try:
            manifest_id = f"manifest_{uuid4().hex[:12]}"
            created_at = datetime.now(timezone.utc).isoformat()
            
            # Create manifest data
            manifest_data = {
                "manifest_id": manifest_id,
                "request_id": request_id,
                "created_at": created_at,
                "export_format": export_format,
                "clip_count": len(clips),
                "clips": clips,
            }
            
            # Save manifest
            manifest_dir = Path(self.settings.generated_assets_dir) / request_id
            manifest_dir.mkdir(parents=True, exist_ok=True)
            
            manifest_path = manifest_dir / f"{manifest_id}.{export_format}"
            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f, indent=2)
            
            return {
                "manifest_id": manifest_id,
                "file_name": f"{manifest_id}.{export_format}",
                "manifest_path": str(manifest_path),
                "download_url": self._public_generated_url(manifest_path),
                "clip_count": len(clips),
                "created_at": created_at,
            }
            
        except Exception as error:
            logger.error(f"output_builder_manifest_failed request_id={request_id} error={str(error)}")
            raise
    
    def validate_export_request(self, user_id: str, clip_ids: List[str]) -> Dict[str, Any]:
        """Validate export request and check permissions."""
        from ..dependencies.auth import get_platform_store
        platform_store = get_platform_store()
        
        # Get user and check plan limits
        user = platform_store.get_user_by_id(user_id)
        if not user:
            return {"valid": False, "reason": "User not found"}
        
        # Check export limits based on plan
        plan_limits = {
            "free": {"max_clips_per_export": 5, "max_exports_per_day": 1},
            "pro": {"max_clips_per_export": 25, "max_exports_per_day": 10},
            "scale": {"max_clips_per_export": 100, "max_exports_per_day": 50},
        }
        
        user_plan = (user.plan or "free").lower()
        limits = plan_limits.get(user_plan, plan_limits["free"])
        
        if len(clip_ids) > limits["max_clips_per_export"]:
            return {
                "valid": False,
                "reason": f"Export limit exceeded. Maximum {limits['max_clips_per_export']} clips per export for {user_plan} plan.",
                "current_plan": user_plan,
                "limits": limits,
            }
        
        return {
            "valid": True,
            "reason": None,
            "current_plan": user_plan,
            "limits": limits,
            "clip_count": len(clip_ids),
        }
