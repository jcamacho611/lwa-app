from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

from app.core.auth import get_current_user_optional
from app.core.config import Settings, get_settings
from app.services.proof_graph import ProofGraphManager, ProofAsset, ProofType

router = APIRouter()


class ProofAssetResponse(BaseModel):
    id: str
    proof_type: str
    title: str
    description: str
    confidence_score: int
    related_offer: Optional[str]
    related_audience: Optional[str]
    content_url: Optional[str]
    thumbnail_url: Optional[str]
    created_at: str
    tags: List[str]
    metadata: dict


class ProofGraphResponse(BaseModel):
    user_id: str
    assets: List[ProofAssetResponse]
    summary: dict
    last_updated: str


class CreateProofRequest(BaseModel):
    proof_type: str
    title: str
    description: str
    confidence_score: int = 70
    related_offer: Optional[str] = None
    related_audience: Optional[str] = None
    content_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    tags: List[str] = []


@router.post("/proof-graph/extract-from-clip", response_model=ProofAssetResponse)
async def extract_proof_from_clip(
    request: CreateProofRequest,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Extract proof potential from a generated clip."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Create a mock clip for proof extraction
    from app.models.schemas import ClipResult
    clip = ClipResult(
        id="proof_extraction",
        title=request.title or "",
        hook="",
        caption="",
        reason="",
        category="",
        transcript_excerpt="",
        score=request.confidence_score,
        confidence_score=request.confidence_score,
    )
    
    # Create proof manager and extract proof
    from app.services.proof_graph import ProofGraphManager
    proof_manager = ProofGraphManager(user_id)
    
    try:
        proof_type = ProofType(request.proof_type.lower())
        proof_asset = proof_manager.extract_proof_from_clip(
            clip=clip,
            proof_type=proof_type,
            title_override=request.title,
            description_override=request.description,
            confidence_boost=5,  # Boost confidence for manual proof creation
        )
        
        return ProofAssetResponse(
            id=proof_asset.id,
            proof_type=proof_asset.proof_type,
            title=proof_asset.title,
            description=proof_asset.description,
            confidence_score=proof_asset.confidence_score,
            related_offer=proof_asset.related_offer,
            related_audience=proof_asset.related_audience,
            content_url=proof_asset.content_url,
            thumbnail_url=proof_asset.thumbnail_url,
            created_at=proof_asset.created_at.isoformat(),
            tags=proof_asset.tags,
            metadata=proof_asset.metadata,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof extraction failed: {str(e)}")


@router.get("/proof-graph/user-graph", response_model=ProofGraphResponse)
async def get_user_proof_graph(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get user's complete proof graph."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Create proof manager and get user's proof graph
    proof_manager = ProofGraphManager(user_id)
    proof_graph = proof_manager.get_user_proof_graph()
    
    # Convert assets to response format
    asset_responses = []
    for asset in proof_graph.assets:
        asset_response = ProofAssetResponse(
            id=asset.id,
            proof_type=asset.proof_type,
            title=asset.title,
            description=asset.description,
            confidence_score=asset.confidence_score,
            related_offer=asset.related_offer,
            related_audience=asset.related_audience,
            content_url=asset.content_url,
            thumbnail_url=asset.thumbnail_url,
            created_at=asset.created_at.isoformat(),
            tags=asset.tags,
            metadata=asset.metadata,
        )
        asset_responses.append(asset_response)
    
    return ProofGraphResponse(
        user_id=user_id,
        assets=asset_responses,
        summary=proof_graph.get_summary_stats(),
        last_updated=proof_graph.last_updated.isoformat(),
    )


@router.post("/proof-graph/create-manual", response_model=ProofAssetResponse)
async def create_manual_proof(
    request: CreateProofRequest,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Create a manual proof asset."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    # Create proof manager and create manual proof
    proof_manager = ProofGraphManager(user_id)
    
    try:
        proof_type = ProofType(request.proof_type.lower())
        proof_asset = proof_manager.create_proof_asset(
            proof_type=proof_type,
            title=request.title,
            description=request.description,
            source_type="user_generated",  # Manual creation
            confidence_score=request.confidence_score,
            related_offer=request.related_offer,
            related_audience=request.related_audience,
            content_url=request.content_url,
            thumbnail_url=request.thumbnail_url,
            tags=request.tags,
            metadata={
                "manual_creation": True,
                "source": "user_input",
            },
        )
        
        return ProofAssetResponse(
            id=proof_asset.id,
            proof_type=proof_asset.proof_type,
            title=proof_asset.title,
            description=proof_asset.description,
            confidence_score=proof_asset.confidence_score,
            related_offer=proof_asset.related_offer,
            related_audience=proof_asset.related_audience,
            content_url=proof_asset.content_url,
            thumbnail_url=proof_asset.thumbnail_url,
            created_at=proof_asset.created_at.isoformat(),
            tags=proof_asset.tags,
            metadata=proof_asset.metadata,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Manual proof creation failed: {str(e)}")


@router.get("/proof-graph/summary/{user_id}")
async def get_user_proof_summary(
    user_id: str,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get proof summary for a specific user (admin endpoint)."""
    # Verify current user is admin or the target user
    current_user_id = current_user.get("user_id", "")
    if not current_user_id or current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create proof manager and get user's proof graph
    proof_manager = ProofGraphManager(user_id)
    proof_graph = proof_manager.get_user_proof_graph()
    
    return JSONResponse(content={
        "user_id": user_id,
        "summary": proof_graph.get_summary_stats(),
        "total_assets": len(proof_graph.assets),
        "last_updated": proof_graph.last_updated.isoformat(),
    })


@router.get("/proof-graph/types")
async def get_proof_types():
    """Get available proof types and their descriptions."""
    return JSONResponse(content={
        "proof_types": {
            proof_type.value: {
                "description": proof_type.description,
                "best_for": get_best_for_description(proof_type),
                "examples": get_example_for_type(proof_type),
            }
            for proof_type in ProofType
        }
    })


def get_best_for_description(proof_type: ProofType) -> str:
    """Get the 'best for' description for a proof type."""
    best_for_map = {
        ProofType.testimonial: "building trust and social proof",
        ProofType.customer_win: "demonstrating product/service value",
        ProofType.transformation: "showing before/after results",
        ProofType.expertise: "establishing authority and expertise",
        ProofType.founder_story: "sharing founder journey and vision",
        ProofType.product_demo: "showcasing product capabilities",
        ProofType.result: "highlighting achievements and outcomes",
        ProofType.process: "explaining methodologies and systems",
        ProofType.authority: "building professional credibility",
        ProofType.objection_handled: "addressing concerns and questions",
        ProofType.offer_explanation: "clarifying value propositions",
    }
    return best_for_map.get(proof_type, "general credibility building")


def get_example_for_type(proof_type: ProofType) -> List[str]:
    """Get example descriptions for a proof type."""
    examples = {
        ProofType.testimonial: [
            "Customer testimonial about coaching results",
            "Client success story with metrics",
            "Before/after transformation case study",
        ],
        ProofType.customer_win: [
            "Screenshot of customer achieving their goal",
            "Revenue increase from using your service",
            "Contract renewal or expansion",
        ],
        ProofType.transformation: [
            "Weight loss journey with photos",
            "Skill acquisition progress video",
            "Career change testimonial",
        ],
        ProofType.expertise: [
            "Speaking at industry conference",
            "Published research paper",
            "Technical demonstration video",
            "Certification achievement",
        ],
        ProofType.founder_story: [
            "Early company building story",
            "Funding journey presentation",
            "Product launch timeline",
        ],
        ProofType.product_demo: [
            "Screen recording showing software workflow",
            "Live product walkthrough",
            "Feature explanation video",
        ],
        ProofType.result: [
            "Campaign performance metrics",
            "Project completion showcase",
            "Award or recognition received",
        ],
        ProofType.process: [
            "Step-by-step methodology explanation",
            "System architecture diagram",
            "Workflow optimization guide",
        ],
        ProofType.authority: [
            "Media appearance or interview",
            "Published thought leadership article",
            "Professional certification showcase",
        ],
        ProofType.objection_handled: [
            "FAQ addressing common concerns",
            "Risk assessment response",
            "Comparison with alternatives",
        ],
        ProofType.offer_explanation: [
            "Value proposition breakdown",
            "ROI calculation demonstration",
            "Pricing justification document",
        ],
    }
    return examples.get(proof_type, [])
