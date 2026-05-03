from __future__ import annotations

import uuid
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import re


class SourceAssetType(Enum):
    """Types of source assets that can be ingested."""
    URL = "url"
    VIDEO = "video"
    AUDIO = "audio"
    SONG = "song"
    IMAGE = "image"
    SCRIPT = "script"
    VOICE_NOTE = "voice_note"
    PODCAST = "podcast"
    MULTI_ASSET = "multi_asset"


class SourceAssetStatus(Enum):
    """Status of source asset processing."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class SourceAssetMetadata:
    """Metadata for a source asset."""
    filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class SourceAsset:
    """A source asset that can be used in Video OS jobs."""
    asset_id: str
    user_id: str
    asset_type: SourceAssetType
    status: SourceAssetStatus
    source_url: Optional[str] = None
    source_content: Optional[str] = None  # For scripts/text content
    metadata: Optional[SourceAssetMetadata] = None
    storage_provider: str = "local_placeholder"
    storage_path: Optional[str] = None
    storage_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SourceAssetRequest:
    """Request to create a source asset."""
    asset_type: str
    source_url: Optional[str] = None
    source_content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class IngestEngine:
    """Service for ingesting and managing source assets."""
    
    def __init__(self, storage_provider: str = "local_placeholder") -> None:
        self.storage_provider = storage_provider
        self._assets: Dict[str, SourceAsset] = {}  # In-memory storage for v0
    
    def create_source_asset(self, request: SourceAssetRequest, user_id: str = "guest:unknown") -> SourceAsset:
        """Create a new source asset."""
        # Validate request
        validation_error = self._validate_source_asset_request(request)
        if validation_error:
            return SourceAsset(
                asset_id=f"asset_{uuid4().hex}",
                user_id=user_id,
                asset_type=SourceAssetType.URL,  # Default
                status=SourceAssetStatus.FAILED,
                error_message=validation_error,
            )
        
        # Parse asset type
        try:
            asset_type = SourceAssetType(request.asset_type.lower())
        except ValueError:
            return SourceAsset(
                asset_id=f"asset_{uuid4().hex}",
                user_id=user_id,
                asset_type=SourceAssetType.URL,
                status=SourceAssetStatus.FAILED,
                error_message=f"Invalid asset type: {request.asset_type}",
            )
        
        # Create asset
        asset = SourceAsset(
            asset_id=f"asset_{uuid4().hex}",
            user_id=user_id,
            asset_type=asset_type,
            status=SourceAssetStatus.READY,  # Mock ready state for v0
            source_url=request.source_url,
            source_content=request.source_content,
            storage_provider=self.storage_provider,
        )
        
        # Add metadata if provided
        if request.metadata:
            asset.metadata = SourceAssetMetadata(
                filename=request.metadata.get("filename"),
                file_size_bytes=request.metadata.get("file_size_bytes"),
                mime_type=request.metadata.get("mime_type"),
                duration_seconds=request.metadata.get("duration_seconds"),
                width=request.metadata.get("width"),
                height=request.metadata.get("height"),
                frame_rate=request.metadata.get("frame_rate"),
                sample_rate=request.metadata.get("sample_rate"),
                channels=request.metadata.get("channels"),
                format=request.metadata.get("format"),
                checksum=request.metadata.get("checksum"),
            )
        
        # For URL assets, validate and extract basic info
        if asset.asset_type == SourceAssetType.URL and asset.source_url:
            url_validation = self._validate_url(asset.source_url)
            if not url_validation["valid"]:
                asset.status = SourceAssetStatus.FAILED
                asset.error_message = url_validation["error"]
            else:
                # Mock metadata extraction for URLs
                asset.metadata = asset.metadata or SourceAssetMetadata()
                asset.metadata.filename = url_validation["suggested_filename"]
        
        # Store asset
        self._assets[asset.asset_id] = asset
        
        return asset
    
    def get_source_asset(self, asset_id: str) -> Optional[SourceAsset]:
        """Get a source asset by ID."""
        return self._assets.get(asset_id)
    
    def list_source_assets(self, user_id: Optional[str] = None) -> List[SourceAsset]:
        """List source assets, optionally filtered by user."""
        assets = list(self._assets.values())
        if user_id:
            assets = [asset for asset in assets if asset.user_id == user_id]
        # Sort by created_at descending
        assets.sort(key=lambda x: x.created_at, reverse=True)
        return assets
    
    def delete_source_asset(self, asset_id: str) -> bool:
        """Delete a source asset."""
        if asset_id in self._assets:
            del self._assets[asset_id]
            return True
        return False
    
    def _validate_source_asset_request(self, request: SourceAssetRequest) -> Optional[str]:
        """Validate a source asset request."""
        if not request.asset_type:
            return "Asset type is required"
        
        # Check if we have source data
        if not request.source_url and not request.source_content:
            return "Either source_url or source_content is required"
        
        # Validate URL if provided
        if request.source_url:
            url_validation = self._validate_url(request.source_url)
            if not url_validation["valid"]:
                return url_validation["error"]
        
        # Validate content length if provided
        if request.source_content:
            if len(request.source_content) > 100000:  # 100KB limit for v0
                return "Source content too large (max 100KB)"
        
        return None
    
    def _validate_url(self, url: str) -> Dict[str, Any]:
        """Validate a URL and extract basic info."""
        url = url.strip()
        
        # Basic URL format validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return {"valid": False, "error": "Invalid URL format"}
        
        # Extract filename from URL
        filename = None
        if '/' in url:
            filename = url.split('/')[-1]
            if '?' in filename:
                filename = filename.split('?')[0]
            if not filename or '.' not in filename:
                filename = None
        
        return {
            "valid": True,
            "suggested_filename": filename
        }
    
    def get_asset_count(self, user_id: Optional[str] = None) -> int:
        """Get count of source assets."""
        return len(self.list_source_assets(user_id))
    
    def get_assets_by_type(self, asset_type: SourceAssetType, user_id: Optional[str] = None) -> List[SourceAsset]:
        """Get assets filtered by type."""
        assets = self.list_source_assets(user_id)
        return [asset for asset in assets if asset.asset_type == asset_type]


# Global instance for v0
_ingest_engine_instance = None


def get_ingest_engine(storage_provider: str = "local_placeholder") -> IngestEngine:
    """Get the global ingest engine instance."""
    global _ingest_engine_instance
    if _ingest_engine_instance is None:
        _ingest_engine_instance = IngestEngine(storage_provider)
    return _ingest_engine_instance


# Helper functions for Video OS integration
def get_asset_ids_for_video_job(asset_requests: List[SourceAssetRequest], user_id: str = "guest:unknown") -> List[str]:
    """Create source assets and return their IDs for use in Video OS jobs."""
    ingest_engine = get_ingest_engine()
    asset_ids = []
    
    for request in asset_requests:
        asset = ingest_engine.create_source_asset(request, user_id)
        if asset.status == SourceAssetStatus.READY:
            asset_ids.append(asset.asset_id)
    
    return asset_ids


def get_assets_for_video_job(asset_ids: List[str]) -> List[Dict[str, Any]]:
    """Get source assets in format suitable for Video OS jobs."""
    ingest_engine = get_ingest_engine()
    assets = []
    
    for asset_id in asset_ids:
        asset = ingest_engine.get_source_asset(asset_id)
        if asset and asset.status == SourceAssetStatus.READY:
            asset_dict = {
                "asset_id": asset.asset_id,
                "asset_type": asset.asset_type.value,
                "source_url": asset.source_url,
                "source_content": asset.source_content,
                "metadata": {
                    "filename": asset.metadata.filename if asset.metadata else None,
                    "file_size_bytes": asset.metadata.file_size_bytes if asset.metadata else None,
                    "duration_seconds": asset.metadata.duration_seconds if asset.metadata else None,
                }
            }
            assets.append(asset_dict)
    
    return assets
