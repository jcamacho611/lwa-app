from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from ..models.schemas import ClipResult


class ProofType(str, Enum):
    testimonial = "testimonial"
    customer_win = "customer_win"
    transformation = "transformation"
    expertise = "expertise"
    founder_story = "founder_story"
    product_demo = "product_demo"
    result = "result"
    process = "process"
    authority = "authority"
    objection_handled = "objection_handled"
    offer_explanation = "offer_explanation"


class ProofSource(str, Enum):
    user_generated = "user_generated"
    customer_feedback = "customer_feedback"
    team_observation = "team_observation"
    external_validation = "external_validation"
    ai_analysis = "ai_analysis"


@dataclass(frozen=True)
class ProofAsset:
    id: str
    user_id: str
    source_type: ProofSource
    source_asset_id: Optional[str] = None  # Link to clip, job, etc.
    proof_type: ProofType
    title: str
    description: str
    confidence_score: int  # 0-100
    related_offer: Optional[str] = None  # What this proof supports
    related_audience: Optional[str] = None  # Who this proof targets
    content_url: Optional[str] = None  # Link to content
    thumbnail_url: Optional[str] = None  # Image/preview
    created_at: datetime
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProofGraph:
    user_id: str
    assets: List[ProofAsset]
    last_updated: datetime
    proof_summary: Dict[str, int] = field(default_factory=dict)  # Counts by type
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for the proof graph."""
        total_assets = len(self.assets)
        type_counts = {}
        confidence_total = 0
        
        for asset in self.assets:
            proof_type = asset.proof_type
            type_counts[proof_type] = type_counts.get(proof_type, 0) + 1
            confidence_total += asset.confidence_score
            
        return {
            "total_assets": total_assets,
            "by_type": type_counts,
            "average_confidence": confidence_total // total_assets if total_assets > 0 else 0,
            "last_updated": self.last_updated.isoformat(),
            "strongest_proof_type": max(type_counts.items(), key=lambda x: x[1]) if type_counts else None,
        }


class ProofGraphManager:
    """Manages user's proof graph - turning content into credibility assets."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
    
    def create_proof_asset(
        self,
        *,
        proof_type: ProofType,
        title: str,
        description: str,
        source_type: ProofSource = ProofSource.user_generated,
        source_asset_id: Optional[str] = None,
        related_offer: Optional[str] = None,
        related_audience: Optional[str] = None,
        confidence_score: int = 70,
        content_url: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> ProofAsset:
        """Create a new proof asset in the user's proof graph."""
        asset = ProofAsset(
            id=f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id=self.user_id,
            source_type=source_type,
            source_asset_id=source_asset_id,
            proof_type=proof_type,
            title=title,
            description=description,
            confidence_score=confidence_score,
            related_offer=related_offer,
            related_audience=related_audience,
            content_url=content_url,
            thumbnail_url=thumbnail_url,
            tags=tags or [],
            metadata=metadata or {},
            created_at=datetime.now(),
        )
        
        return asset
    
    def extract_proof_from_clip(
        self,
        clip: ClipResult,
        *,
        proof_type: ProofType,
        title_override: Optional[str] = None,
        description_override: Optional[str] = None,
        confidence_boost: int = 0,
    ) -> ProofAsset:
        """Extract proof potential from a generated clip."""
        # Determine best proof type based on clip content
        title = title_override or clip.title or "Untitled Proof"
        
        # Build description from clip analysis
        if description_override:
            description = description_override
        elif proof_type == ProofType.testimonial:
            description = f"Customer testimonial from: {clip.hook or clip.title}"
        elif proof_type == ProofType.customer_win:
            description = f"Customer success story featuring: {clip.hook or clip.title}"
        elif proof_type == ProofType.transformation:
            description = f"Before/after transformation: {clip.hook or clip.title}"
        elif proof_type == ProofType.expertise:
            description = f"Expert knowledge demonstration: {clip.hook or clip.title}"
        elif proof_type == ProofType.founder_story:
            description = f"Founder journey moment: {clip.hook or clip.title}"
        elif proof_type == ProofType.product_demo:
            description = f"Product capability showcase: {clip.hook or clip.title}"
        elif proof_type == ProofType.result:
            description = f"Result showcase: {clip.hook or clip.title}"
        elif proof_type == ProofType.process:
            description = f"Process explanation: {clip.hook or clip.title}"
        elif proof_type == ProofType.authority:
            description = f"Authority building content: {clip.hook or clip.title}"
        elif proof_type == ProofType.objection_handled:
            description = f"Objection handling example: {clip.hook or clip.title}"
        elif proof_type == ProofType.offer_explanation:
            description = f"Offer clarification: {clip.hook or clip.title}"
        else:
            description = f"Proof moment: {clip.hook or clip.title}"
        
        # Calculate confidence based on clip quality and proof type
        base_confidence = int(clip.confidence_score or clip.score or 70)
        confidence = min(95, base_confidence + confidence_boost)
        
        return ProofAsset(
            id=f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id=self.user_id,
            source_type=ProofSource.ai_analysis,
            source_asset_id=clip.id,
            proof_type=proof_type,
            title=title,
            description=description,
            confidence_score=confidence,
            related_offer=self._infer_related_offer(clip),
            related_audience=self._infer_audience(clip),
            content_url=clip.preview_url or clip.edited_clip_url or clip.clip_url,
            thumbnail_url=clip.thumbnail_url,
            tags=[clip.category or "ai_generated", proof_type.value],
            metadata={
                "original_clip_id": clip.id,
                "original_hook": clip.hook,
                "original_caption": clip.caption,
                "clip_score": clip.score,
                "extraction_method": "ai_analysis",
            },
        )
    
    def _infer_related_offer(self, clip: ClipResult) -> Optional[str]:
        """Infer what offer this proof might support."""
        text = " ".join([clip.hook or "", clip.caption or "", clip.reason or ""]).lower()
        
        # Simple keyword-based offer inference
        offer_keywords = {
            "coaching": ["coaching", "framework", "program", "course", "transformation"],
            "consulting": ["consulting", "strategy", "expert", "advice"],
            "product": ["product", "software", "tool", "platform", "service"],
            "local_business": ["local", "business", "service", "clinic", "restaurant"],
            "community": ["community", "membership", "tribe", "group", "join"],
            "content_creation": ["content", "creator", "media", "publishing"],
        }
        
        for offer, keywords in offer_keywords.items():
            if any(keyword in text for keyword in keywords):
                return offer
        
        return None
    
    def _infer_audience(self, clip: ClipResult) -> Optional[str]:
        """Infer target audience from clip content."""
        text = " ".join([clip.hook or "", clip.caption or "", clip.reason or ""]).lower()
        
        audience_patterns = {
            "creators": ["creator", "audience", "followers", "subscribers", "views", "engagement"],
            "business_owners": ["business", "owner", "entrepreneur", "company", "revenue", "profit"],
            "coaches": ["coach", "client", "transformation", "framework"],
            "local_customers": ["local", "customer", "neighborhood", "area", "community"],
            "job_seekers": ["job", "career", "hire", "resume", "professional"],
            "investors": ["invest", "funding", "roi", "return", "venture"],
            "general_consumers": ["everyone", "people", "public", "users"],
        }
        
        for audience, patterns in audience_patterns.items():
            if any(pattern in text for pattern in patterns):
                return audience
        
        return "general_consumers"
    
    def get_user_proof_graph(self) -> ProofGraph:
        """Get or create user's proof graph."""
        # In a real implementation, this would query from database
        # For now, return empty graph
        return ProofGraph(
            user_id=self.user_id,
            assets=[],
            last_updated=datetime.now(),
            proof_summary={},
        )
    
    def add_proof_assets_from_clips(
        self,
        clips: List[ClipResult],
        proof_types: List[ProofType] = None,
    ) -> List[ProofAsset]:
        """Convert multiple clips into proof assets."""
        if proof_types is None:
            proof_types = [
                ProofType.testimonial,
                ProofType.customer_win,
                ProofType.transformation,
                ProofType.expertise,
                ProofType.authority,
            ]
        
        assets = []
        for clip in clips:
            for proof_type in proof_types:
                asset = self.extract_proof_from_clip(clip, proof_type=proof_type)
                assets.append(asset)
        
        return assets
    
    def get_strongest_proofs(self, limit: int = 5) -> List[ProofAsset]:
        """Get user's strongest proof assets by confidence score."""
        # In real implementation, this would query from user's proof graph
        # For now, return empty list
        return []
    
    def get_proof_by_type(self, proof_type: ProofType) -> List[ProofAsset]:
        """Get all proof assets of a specific type."""
        # In real implementation, this would query from user's proof graph
        # For now, return empty list
        return []
    
    def get_proof_summary(self) -> Dict[str, Any]:
        """Get summary of user's proof graph."""
        # In real implementation, this would calculate from user's proof graph
        # For now, return basic summary
        return {
            "total_proofs": 0,
            "by_type": {},
            "average_confidence": 0,
            "last_updated": datetime.now().isoformat(),
        }
