"""
Proof Vault API Routes
Stores winning clips, rejected clips, proof assets, and performance memory per creator.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/v1/proof-vault", tags=["proof_vault"])

class ProofStatus(str, Enum):
    WINNING = "winning"
    REJECTED = "rejected"
    PENDING = "pending"
    ARCHIVED = "archived"

class ProofAssetType(str, Enum):
    CLIP = "clip"
    HOOK = "hook"
    CAPTION = "caption"
    THUMBNAIL = "thumbnail"
    FULL_VIDEO = "full_video"
    CAMPAIGN = "campaign"

class ProofAsset(BaseModel):
    id: str
    user_id: str
    project_id: Optional[str] = None
    asset_type: ProofAssetType
    status: ProofStatus
    source_url: Optional[str] = None
    clip_url: Optional[str] = None
    hook_text: Optional[str] = None
    caption_text: Optional[str] = None
    thumbnail_url: Optional[str] = None
    platform: Optional[str] = None
    duration_seconds: Optional[float] = None
    ai_score: Optional[float] = None
    performance_notes: Optional[Dict[str, Any]] = None
    style_tags: List[str] = []
    rejected_reason: Optional[str] = None
    approved_by: Optional[str] = None
    campaign_id: Optional[str] = None
    created_at: str
    updated_at: str

class ProofAssetCreate(BaseModel):
    asset_type: ProofAssetType
    source_url: Optional[str]
    clip_url: Optional[str]
    hook_text: Optional[str]
    caption_text: Optional[str]
    platform: Optional[str]
    duration_seconds: Optional[float]
    ai_score: Optional[float]
    style_tags: Optional[List[str]]
    project_id: Optional[str]

class ProofAssetUpdate(BaseModel):
    status: Optional[ProofStatus]
    performance_notes: Optional[Dict[str, Any]]
    style_tags: Optional[List[str]]
    rejected_reason: Optional[str]
    approved_by: Optional[str]

class ProofFilterRequest(BaseModel):
    asset_type: Optional[ProofAssetType]
    status: Optional[ProofStatus]
    platform: Optional[str]
    project_id: Optional[str]
    style_tags: Optional[List[str]]

# Mock proof vault storage
MOCK_PROOF_VAULT: Dict[str, ProofAsset] = {
    "proof_001": ProofAsset(
        id="proof_001",
        user_id="user_001",
        project_id="proj_podcast_001",
        asset_type=ProofAssetType.CLIP,
        status=ProofStatus.WINNING,
        source_url="https://youtube.com/watch?v=abc123",
        clip_url="/generated/clip_001.mp4",
        hook_text="You won't believe what happens at 3:42...",
        caption_text="The moment that changed everything",
        platform="tiktok",
        duration_seconds=15.5,
        ai_score=0.94,
        performance_notes={
            "views": 125000,
            "engagement_rate": 0.08,
            "shares": 3400,
            "comments": 890,
            "posted_at": "2025-04-15T10:00:00Z"
        },
        style_tags=["viral_hook", "suspense", "short_form", "podcast"],
        approved_by="creator",
        campaign_id="camp_001",
        created_at="2025-04-15T10:00:00Z",
        updated_at="2025-04-15T10:00:00Z"
    ),
    "proof_002": ProofAsset(
        id="proof_002",
        user_id="user_001",
        project_id="proj_podcast_001",
        asset_type=ProofAssetType.CLIP,
        status=ProofStatus.REJECTED,
        source_url="https://youtube.com/watch?v=abc123",
        hook_text="Check this out...",
        caption_text="Interesting moment",
        platform="tiktok",
        duration_seconds=22.0,
        ai_score=0.62,
        performance_notes={},
        style_tags=["weak_hook", "low_energy"],
        rejected_reason="Hook too generic, low AI score",
        created_at="2025-04-15T10:05:00Z",
        updated_at="2025-04-15T10:05:00Z"
    ),
    "proof_003": ProofAsset(
        id="proof_003",
        user_id="user_001",
        project_id="proj_tutorial_001",
        asset_type=ProofAssetType.CLIP,
        status=ProofStatus.WINNING,
        source_url="https://youtube.com/watch?v=def456",
        clip_url="/generated/clip_003.mp4",
        hook_text="Stop making this mistake...",
        caption_text="Common error fixed in 30 seconds",
        platform="youtube_shorts",
        duration_seconds=28.5,
        ai_score=0.91,
        performance_notes={
            "views": 89000,
            "engagement_rate": 0.12,
            "saves": 4200,
            "posted_at": "2025-04-20T14:00:00Z"
        },
        style_tags=["educational", "problem_solution", "tutorial"],
        approved_by="creator",
        created_at="2025-04-20T14:00:00Z",
        updated_at="2025-04-20T14:00:00Z"
    )
}

@router.get("/assets", response_model=Dict[str, Any])
async def list_proof_assets(
    user_id: str = "user_001",
    asset_type: Optional[ProofAssetType] = None,
    status: Optional[ProofStatus] = None,
    platform: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List proof assets with optional filtering."""
    assets = [a for a in MOCK_PROOF_VAULT.values() if a.user_id == user_id]
    
    if asset_type:
        assets = [a for a in assets if a.asset_type == asset_type]
    if status:
        assets = [a for a in assets if a.status == status]
    if platform:
        assets = [a for a in assets if a.platform == platform]
    if project_id:
        assets = [a for a in assets if a.project_id == project_id]
    
    total = len(assets)
    assets = assets[offset:offset + limit]
    
    return {
        "success": True,
        "assets": [a.dict() for a in assets],
        "total_count": total,
        "winning_count": len([a for a in assets if a.status == ProofStatus.WINNING]),
        "rejected_count": len([a for a in assets if a.status == ProofStatus.REJECTED]),
        "limit": limit,
        "offset": offset
    }

@router.post("/assets", response_model=Dict[str, Any])
async def save_proof_asset(asset: ProofAssetCreate, user_id: str = "user_001"):
    """Save a new proof asset to the vault."""
    proof_id = f"proof_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    new_asset = ProofAsset(
        id=proof_id,
        user_id=user_id,
        project_id=asset.project_id,
        asset_type=asset.asset_type,
        status=ProofStatus.PENDING,
        source_url=asset.source_url,
        clip_url=asset.clip_url,
        hook_text=asset.hook_text,
        caption_text=asset.caption_text,
        platform=asset.platform,
        duration_seconds=asset.duration_seconds,
        ai_score=asset.ai_score,
        performance_notes={},
        style_tags=asset.style_tags or [],
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    MOCK_PROOF_VAULT[proof_id] = new_asset
    
    return {
        "success": True,
        "asset": new_asset.dict(),
        "message": f"Proof asset saved with ID: {proof_id}"
    }

@router.get("/assets/{proof_id}", response_model=Dict[str, Any])
async def get_proof_asset(proof_id: str):
    """Get a specific proof asset."""
    if proof_id not in MOCK_PROOF_VAULT:
        raise HTTPException(status_code=404, detail="Proof asset not found")
    
    return {
        "success": True,
        "asset": MOCK_PROOF_VAULT[proof_id].dict()
    }

@router.patch("/assets/{proof_id}", response_model=Dict[str, Any])
async def update_proof_asset(proof_id: str, update: ProofAssetUpdate):
    """Update a proof asset (approve, reject, add notes)."""
    if proof_id not in MOCK_PROOF_VAULT:
        raise HTTPException(status_code=404, detail="Proof asset not found")
    
    asset = MOCK_PROOF_VAULT[proof_id]
    
    if update.status:
        asset.status = update.status
    if update.performance_notes:
        asset.performance_notes.update(update.performance_notes)
    if update.style_tags:
        asset.style_tags = update.style_tags
    if update.rejected_reason:
        asset.rejected_reason = update.rejected_reason
    if update.approved_by:
        asset.approved_by = update.approved_by
    
    asset.updated_at = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "asset": asset.dict(),
        "message": "Proof asset updated"
    }

@router.post("/filter", response_model=Dict[str, Any])
async def filter_proof_assets(filter_req: ProofFilterRequest, user_id: str = "user_001"):
    """Advanced filter for proof assets."""
    assets = [a for a in MOCK_PROOF_VAULT.values() if a.user_id == user_id]
    
    if filter_req.asset_type:
        assets = [a for a in assets if a.asset_type == filter_req.asset_type]
    if filter_req.status:
        assets = [a for a in assets if a.status == filter_req.status]
    if filter_req.platform:
        assets = [a for a in assets if a.platform == filter_req.platform]
    if filter_req.project_id:
        assets = [a for a in assets if a.project_id == filter_req.project_id]
    if filter_req.style_tags:
        assets = [a for a in assets if any(tag in a.style_tags for tag in filter_req.style_tags)]
    
    return {
        "success": True,
        "assets": [a.dict() for a in assets],
        "count": len(assets)
    }

@router.get("/stats", response_model=Dict[str, Any])
async def get_proof_vault_stats(user_id: str = "user_001"):
    """Get stats about the proof vault."""
    user_assets = [a for a in MOCK_PROOF_VAULT.values() if a.user_id == user_id]
    
    winning = [a for a in user_assets if a.status == ProofStatus.WINNING]
    rejected = [a for a in user_assets if a.status == ProofStatus.REJECTED]
    
    # Collect style tags
    all_tags = []
    for asset in user_assets:
        all_tags.extend(asset.style_tags)
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return {
        "success": True,
        "stats": {
            "total_assets": len(user_assets),
            "winning_count": len(winning),
            "rejected_count": len(rejected),
            "approval_rate": len(winning) / len(user_assets) if user_assets else 0,
            "top_style_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            "platforms_used": list(set([a.platform for a in user_assets if a.platform])),
            "projects_count": len(set([a.project_id for a in user_assets if a.project_id]))
        }
    }

@router.get("/patterns/winning", response_model=Dict[str, Any])
async def get_winning_patterns(user_id: str = "user_001"):
    """Extract patterns from winning clips."""
    winning = [a for a in MOCK_PROOF_VAULT.values() 
               if a.user_id == user_id and a.status == ProofStatus.WINNING]
    
    if not winning:
        return {
            "success": True,
            "patterns": None,
            "message": "No winning clips yet. Create and approve some clips!"
        }
    
    # Analyze patterns
    avg_duration = sum([a.duration_seconds or 0 for a in winning]) / len(winning)
    avg_ai_score = sum([a.ai_score or 0 for a in winning]) / len(winning)
    
    # Common style tags in winners
    winning_tags = []
    for asset in winning:
        winning_tags.extend(asset.style_tags)
    
    tag_counts = {}
    for tag in winning_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    top_patterns = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Hook patterns
    hook_starters = []
    for asset in winning:
        if asset.hook_text:
            first_word = asset.hook_text.split()[0].lower() if asset.hook_text else ""
            hook_starters.append(first_word)
    
    return {
        "success": True,
        "patterns": {
            "total_winning_clips": len(winning),
            "average_duration": avg_duration,
            "average_ai_score": avg_ai_score,
            "top_performing_tags": top_patterns,
            "common_hook_openers": list(set(hook_starters))[:5],
            "best_platforms": list(set([a.platform for a in winning if a.platform]))
        },
        "recommendations": [
            f"Your best clips average {avg_duration:.1f}s - aim for this length",
            f"Top performing style: {top_patterns[0][0] if top_patterns else 'N/A'}",
            "Use similar hook patterns to your winning clips"
        ]
    }

@router.get("/patterns/rejected", response_model=Dict[str, Any])
async def get_rejected_patterns(user_id: str = "user_001"):
    """Learn from rejected clips."""
    rejected = [a for a in MOCK_PROOF_VAULT.values() 
                  if a.user_id == user_id and a.status == ProofStatus.REJECTED]
    
    if not rejected:
        return {
            "success": True,
            "patterns": None,
            "message": "No rejected clips. Great job!"
        }
    
    # Common rejection reasons
    reasons = [a.rejected_reason for a in rejected if a.rejected_reason]
    
    return {
        "success": True,
        "patterns": {
            "total_rejected": len(rejected),
            "common_rejection_reasons": reasons,
            "average_rejected_ai_score": sum([a.ai_score or 0 for a in rejected]) / len(rejected) if rejected else 0
        },
        "lessons": [
            "Avoid weak hooks like 'Check this out'",
            "Higher AI score generally correlates with approval",
            "Specific hooks perform better than generic ones"
        ]
    }
