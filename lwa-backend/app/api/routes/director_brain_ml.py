"""Director Brain API routes.

Provides deterministic, explainable scoring/ranking endpoints for hooks,
captions, clip summaries, offers, opportunities, and campaign angles.
"""

from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...services.director_brain_ml import get_status, learn_event, rank_candidates, score_text

router = APIRouter(prefix="/api/v1/director-brain", tags=["director_brain"])

ContentType = Literal[
    "hook",
    "caption",
    "title",
    "offer",
    "description",
    "clip_summary",
    "opportunity",
    "campaign_angle",
]
Goal = Literal["engagement", "conversion", "viral", "personal", "balanced"]
LearningLabel = Literal["winning", "rejected", "neutral"]
SignalType = Literal["save", "share", "click", "export", "purchase", "manual_feedback"]


class DirectorBrainScoreRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    content_type: ContentType = "hook"
    platform: Optional[str] = None
    goal: Goal = "balanced"
    style_memory: Optional[Dict[str, Any]] = None
    proof_signals: Optional[Dict[str, Any]] = None


class DirectorBrainRankRequest(BaseModel):
    candidates: List[str] = Field(..., min_length=1, max_length=50)
    content_type: ContentType = "hook"
    platform: Optional[str] = None
    goal: Goal = "balanced"
    style_memory: Optional[Dict[str, Any]] = None
    proof_signals: Optional[Dict[str, Any]] = None


class DirectorBrainLearnRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4000)
    label: LearningLabel = "neutral"
    signal_type: SignalType = "manual_feedback"
    weight: float = Field(1.0, ge=0, le=5)
    metadata: Optional[Dict[str, Any]] = None


@router.post("/score", response_model=Dict[str, Any])
async def score_director_brain_text(request: DirectorBrainScoreRequest):
    """Score one text asset with explainable Director Brain v0 heuristics."""
    try:
        return score_text(
            request.text,
            content_type=request.content_type,
            platform=request.platform,
            goal=request.goal,
            style_memory=request.style_memory,
            proof_signals=request.proof_signals,
        )
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=500, detail=f"Director Brain score failed: {exc}") from exc


@router.post("/rank", response_model=Dict[str, Any])
async def rank_director_brain_candidates(request: DirectorBrainRankRequest):
    """Rank candidate hooks/captions/ideas with the same explainable scoring model."""
    try:
        return rank_candidates(
            request.candidates,
            content_type=request.content_type,
            platform=request.platform,
            goal=request.goal,
            style_memory=request.style_memory,
            proof_signals=request.proof_signals,
        )
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=500, detail=f"Director Brain rank failed: {exc}") from exc


@router.post("/learn", response_model=Dict[str, Any])
async def submit_director_brain_learning_event(request: DirectorBrainLearnRequest):
    """Store a metadata-only learning signal for future personalization."""
    try:
        return learn_event(
            request.text,
            label=request.label,
            signal_type=request.signal_type,
            weight=request.weight,
            metadata=request.metadata,
        )
    except Exception as exc:  # pragma: no cover - defensive API guard
        raise HTTPException(status_code=500, detail=f"Director Brain learn failed: {exc}") from exc


@router.get("/status", response_model=Dict[str, Any])
async def get_director_brain_status():
    """Report Director Brain mode, supported fields, and learning-event count."""
    return get_status()
