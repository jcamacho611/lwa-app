from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from app.core.auth import get_current_user_optional
from app.services.ingest_engine import (
    IngestEngine,
    SourceAssetRequest,
    SourceAsset,
    SourceAssetType,
    SourceAssetStatus,
    get_ingest_engine,
)


router = APIRouter()


class SourceAssetCreateRequest(BaseModel):
    asset_type: str = Field(..., description="Type of source asset")
    source_url: Optional[str] = Field(None, description="URL of the source asset")
    source_content: Optional[str] = Field(None, description="Text content for scripts/notes")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class SourceAssetResponse(BaseModel):
    asset_id: str
    user_id: str
    asset_type: str
    status: str
    source_url: Optional[str]
    source_content: Optional[str]
    storage_provider: str
    storage_path: Optional[str]
    storage_url: Optional[str]
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str
    updated_at: str


class SourceAssetListResponse(BaseModel):
    assets: List[SourceAssetResponse]
    total_count: int


class DeleteResponse(BaseModel):
    message: str
    asset_id: str
    deleted: bool


def get_ingest_engine_instance() -> IngestEngine:
    """Get the ingest engine instance."""
    return get_ingest_engine()


def _asset_to_response(asset: SourceAsset) -> SourceAssetResponse:
    """Convert SourceAsset to response model."""
    metadata_dict = None
    if asset.metadata:
        metadata_dict = {
            "filename": asset.metadata.filename,
            "file_size_bytes": asset.metadata.file_size_bytes,
            "mime_type": asset.metadata.mime_type,
            "duration_seconds": asset.metadata.duration_seconds,
            "width": asset.metadata.width,
            "height": asset.metadata.height,
            "frame_rate": asset.metadata.frame_rate,
            "sample_rate": asset.metadata.sample_rate,
            "channels": asset.metadata.channels,
            "format": asset.metadata.format,
            "checksum": asset.metadata.checksum,
        }
        # Remove None values
        metadata_dict = {k: v for k, v in metadata_dict.items() if v is not None}
    
    return SourceAssetResponse(
        asset_id=asset.asset_id,
        user_id=asset.user_id,
        asset_type=asset.asset_type.value,
        status=asset.status.value,
        source_url=asset.source_url,
        source_content=asset.source_content,
        storage_provider=asset.storage_provider,
        storage_path=asset.storage_path,
        storage_url=asset.storage_url,
        error_message=asset.error_message,
        metadata=metadata_dict,
        created_at=asset.created_at,
        updated_at=asset.updated_at,
    )


@router.post("/source-assets", response_model=SourceAssetResponse)
async def create_source_asset(
    request: SourceAssetCreateRequest,
    current_user: dict = Depends(get_current_user_optional),
):
    """Create a new source asset."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Create ingest request
    ingest_request = SourceAssetRequest(
        asset_type=request.asset_type,
        source_url=request.source_url,
        source_content=request.source_content,
        metadata=request.metadata,
    )
    
    # Create asset
    ingest_engine = get_ingest_engine_instance()
    asset = ingest_engine.create_source_asset(ingest_request, user_id)
    
    if asset.status == SourceAssetStatus.FAILED:
        raise HTTPException(status_code=400, detail=asset.error_message or "Failed to create source asset")
    
    return _asset_to_response(asset)


@router.get("/source-assets/{asset_id}", response_model=SourceAssetResponse)
async def get_source_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Get a specific source asset."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    ingest_engine = get_ingest_engine_instance()
    asset = ingest_engine.get_source_asset(asset_id)
    
    if not asset:
        raise HTTPException(status_code=404, detail="Source asset not found")
    
    # In production, verify user owns this asset. For v0, skip strict user checking
    
    return _asset_to_response(asset)


@router.get("/source-assets", response_model=SourceAssetListResponse)
async def list_source_assets(
    current_user: dict = Depends(get_current_user_optional),
):
    """List source assets for the current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    ingest_engine = get_ingest_engine_instance()
    assets = ingest_engine.list_source_assets(user_id)
    
    asset_responses = [_asset_to_response(asset) for asset in assets]
    
    return SourceAssetListResponse(
        assets=asset_responses,
        total_count=len(asset_responses)
    )


@router.delete("/source-assets/{asset_id}", response_model=DeleteResponse)
async def delete_source_asset(
    asset_id: str,
    current_user: dict = Depends(get_current_user_optional),
):
    """Delete a source asset."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    ingest_engine = get_ingest_engine_instance()
    
    # Verify asset exists
    asset = ingest_engine.get_source_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Source asset not found")
    
    # In production, verify user owns this asset. For v0, skip strict user checking
    
    deleted = ingest_engine.delete_source_asset(asset_id)
    
    return DeleteResponse(
        message="Source asset deleted successfully" if deleted else "Failed to delete source asset",
        asset_id=asset_id,
        deleted=deleted
    )


@router.get("/source-assets/types")
async def get_source_asset_types(
    current_user: dict = Depends(get_current_user_optional),
):
    """Get available source asset types."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    return {
        "asset_types": [asset_type.value for asset_type in SourceAssetType],
        "descriptions": {
            "url": "URL to video, audio, or image content",
            "video": "Uploaded video file",
            "audio": "Uploaded audio file",
            "song": "Music file for visualizer or soundtrack",
            "image": "Static image for animation or background",
            "script": "Text script for video generation",
            "voice_note": "Voice recording for narration",
            "podcast": "Podcast episode for analysis or clipping",
            "multi_asset": "Multiple assets packaged together"
        }
    }


@router.get("/source-assets/stats")
async def get_source_asset_stats(
    current_user: dict = Depends(get_current_user_optional),
):
    """Get statistics about source assets."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    ingest_engine = get_ingest_engine_instance()
    
    # Get stats for current user
    all_assets = ingest_engine.list_source_assets(user_id)
    
    # Count by type
    type_counts = {}
    for asset_type in SourceAssetType:
        type_counts[asset_type.value] = 0
    
    for asset in all_assets:
        type_counts[asset.asset_type.value] += 1
    
    # Count by status
    status_counts = {}
    for status in SourceAssetStatus:
        status_counts[status.value] = 0
    
    for asset in all_assets:
        status_counts[asset.status.value] += 1
    
    return {
        "total_assets": len(all_assets),
        "by_type": type_counts,
        "by_status": status_counts,
        "storage_provider": ingest_engine.storage_provider,
        "metadata_only": ingest_engine.storage_provider == "local_placeholder"
    }


@router.post("/source-assets/batch", response_model=SourceAssetListResponse)
async def create_source_assets_batch(
    requests: List[SourceAssetCreateRequest],
    current_user: dict = Depends(get_current_user_optional),
):
    """Create multiple source assets at once."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    if len(requests) > 10:  # Reasonable batch limit
        raise HTTPException(status_code=400, detail="Too many assets in batch (max 10)")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    ingest_engine = get_ingest_engine_instance()
    created_assets = []
    
    for request in requests:
        ingest_request = SourceAssetRequest(
            asset_type=request.asset_type,
            source_url=request.source_url,
            source_content=request.source_content,
            metadata=request.metadata,
        )
        
        asset = ingest_engine.create_source_asset(ingest_request, user_id)
        if asset.status != SourceAssetStatus.FAILED:
            created_assets.append(_asset_to_response(asset))
    
    return SourceAssetListResponse(
        assets=created_assets,
        total_count=len(created_assets)
    )
