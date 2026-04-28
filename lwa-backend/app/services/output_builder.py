from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from ..core.config import Settings
from .export_bundle import create_export_bundle
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
            return create_export_bundle(
                settings=self.settings,
                public_base_url=self.settings.api_base_url or "",
                source_url="",
                clips=clips,
                request_id=request_id,
            )
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
