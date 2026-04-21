from __future__ import annotations

import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import Settings
from ..models.schemas import ClipBatchResponse

logger = logging.getLogger("uvicorn.error")


class OutputBuilder:
    """Service for building export bundles and output packages."""
    
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
    
    def create_clip_bundle(
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
            
            # Create bundle directory
            bundle_dir = Path(self.settings.generated_assets_dir) / request_id
            bundle_dir.mkdir(parents=True, exist_ok=True)
            
            # Create metadata file
            metadata = {
                "request_id": request_id,
                "bundle_id": bundle_id,
                "created_at": created_at,
                "clip_count": len(clips),
                "bundle_format": bundle_format,
            }
            
            if include_metadata:
                metadata_path = bundle_dir / "metadata.json"
                with open(metadata_path, "w") as f:
                    import json
                    json.dump(metadata, f, indent=2)
            
            # Create bundle file
            bundle_path = bundle_dir / f"{bundle_id}.{bundle_format}"
            
            if bundle_format.lower() == "zip":
                with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as bundle_zip:
                    for clip in clips:
                        clip_id = clip.get("id", "")
                        if clip.get("preview_url"):
                            # Add preview clip
                            preview_path = bundle_dir / f"{clip_id}_preview.mp4"
                            if Path(clip["preview_url"]).exists():
                                bundle_zip.write(clip["preview_url"], f"{clip_id}_preview.mp4")
                        
                        if clip.get("download_url"):
                            # Add download clip
                            download_path = bundle_dir / f"{clip_id}_download.mp4"
                            if Path(clip["download_url"]).exists():
                                bundle_zip.write(clip["download_url"], f"{clip_id}_download.mp4")
                        
                        if clip.get("edited_clip_url"):
                            # Add edited clip
                            edited_path = bundle_dir / f"{clip_id}_edited.mp4"
                            if Path(clip["edited_clip_url"]).exists():
                                bundle_zip.write(clip["edited_clip_url"], f"{clip_id}_edited.mp4")
            
            # Add README to bundle
            readme_content = f"""# Clip Bundle {bundle_id}

Generated: {created_at}
Clips: {len(clips)}
Format: {bundle_format}

## Usage
1. Extract this bundle
2. Each clip is available in multiple formats:
   - Preview: {clip_id}_preview.mp4
   - Download: {clip_id}_download.mp4  
   - Edited: {clip_id}_edited.mp4

## File Structure
- metadata.json: Bundle metadata and clip information
- Various .mp4 files: Individual clip files in different formats

This bundle was created by LWA for batch processing and distribution.
"""
            
            with open(bundle_path / "README.md", "w") as f:
                f.write(readme_content)
            
            return {
                "bundle_id": bundle_id,
                "file_name": f"{bundle_id}.{bundle_format}",
                "bundle_path": str(bundle_path),
                "download_url": f"{self.settings.api_base_url or ''}/generated/{request_id}/{bundle_path.name}" if self.settings.api_base_url else "",
                "clip_count": len(clips),
                "created_at": created_at,
                "size_bytes": bundle_path.stat().st_size if bundle_path.exists() else 0,
            }
            
        except Exception as error:
            logger.error(f"output_builder_failed request_id={request_id} error={str(error)}")
            raise
    
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
                import json
                json.dump(manifest_data, f, indent=2)
            
            return {
                "manifest_id": manifest_id,
                "file_name": f"{manifest_id}.{export_format}",
                "manifest_path": str(manifest_path),
                "download_url": f"{self.settings.api_base_url or ''}/generated/{request_id}/{manifest_path.name}" if self.settings.api_base_url else "",
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
