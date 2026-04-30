from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException

from app.worlds.dependencies import get_demo_user_id, get_worlds_store
from app.worlds.errors import ForbiddenTransitionError, NotFoundError, ValidationError
from app.worlds.repositories import WorldsStore

from .schemas import (
    ClipCandidateCreateRequest,
    ClipCandidateResponse,
    ClipCandidateScoreRequest,
    ClipMomentCreateRequest,
    ClipMomentResponse,
    ClipPackCreateRequest,
    ClipPackDetailResponse,
    ClipPackResponse,
    ClipRenderContractCreateRequest,
    ClipRenderContractResponse,
)
from .service import ClippingService

router = APIRouter(prefix="/worlds/clipping", tags=["lwa-worlds-clipping"])


def handle_clipping_error(error: Exception) -> None:
    if isinstance(error, NotFoundError):
        raise HTTPException(status_code=404, detail=str(error)) from error
    if isinstance(error, ForbiddenTransitionError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    if isinstance(error, ValidationError):
        raise HTTPException(status_code=400, detail=str(error)) from error
    raise error


def moment_to_response(moment) -> ClipMomentResponse:
    return ClipMomentResponse(
        public_id=moment.public_id,
        owner_user_id=moment.owner_user_id,
        source_public_id=moment.source_public_id,
        transcript_public_id=moment.transcript_public_id,
        start_seconds=moment.start_seconds,
        end_seconds=moment.end_seconds,
        transcript_excerpt=moment.transcript_excerpt,
        moment_type=moment.moment_type,
        reason=moment.reason,
        confidence=moment.confidence,
        created_at=moment.created_at,
    )


def candidate_to_response(candidate) -> ClipCandidateResponse:
    return ClipCandidateResponse(
        public_id=candidate.public_id,
        owner_user_id=candidate.owner_user_id,
        source_public_id=candidate.source_public_id,
        transcript_public_id=candidate.transcript_public_id,
        moment_public_id=candidate.moment_public_id,
        title=candidate.title,
        hook=candidate.hook,
        caption=candidate.caption,
        start_seconds=candidate.start_seconds,
        end_seconds=candidate.end_seconds,
        target_platform=candidate.target_platform,
        status=candidate.status.value if hasattr(candidate.status, "value") else str(candidate.status),
        score_total=candidate.score_total,
        score_hook=candidate.score_hook,
        score_retention=candidate.score_retention,
        score_clarity=candidate.score_clarity,
        score_emotion=candidate.score_emotion,
        score_shareability=candidate.score_shareability,
        score_platform_fit=candidate.score_platform_fit,
        risk_notes=json.loads(candidate.risk_notes_json),
        render_asset_public_id=candidate.render_asset_public_id,
        created_at=candidate.created_at,
        updated_at=candidate.updated_at,
    )


def pack_to_response(pack) -> ClipPackResponse:
    return ClipPackResponse(
        public_id=pack.public_id,
        owner_user_id=pack.owner_user_id,
        source_public_id=pack.source_public_id,
        transcript_public_id=pack.transcript_public_id,
        title=pack.title,
        target_platform=pack.target_platform,
        desired_clip_count=pack.desired_clip_count,
        status=pack.status.value if hasattr(pack.status, "value") else str(pack.status),
        selected_candidate_ids=json.loads(pack.selected_candidate_ids_json),
        job_public_id=pack.job_public_id,
        created_at=pack.created_at,
        updated_at=pack.updated_at,
    )


def render_contract_to_response(contract) -> ClipRenderContractResponse:
    return ClipRenderContractResponse(
        public_id=contract.public_id,
        owner_user_id=contract.owner_user_id,
        clip_candidate_public_id=contract.clip_candidate_public_id,
        source_public_id=contract.source_public_id,
        output_format=contract.output_format,
        aspect_ratio=contract.aspect_ratio,
        resolution=contract.resolution,
        remove_silence=contract.remove_silence,
        captions_enabled=contract.captions_enabled,
        caption_style_json=contract.caption_style_json,
        music_enabled=contract.music_enabled,
        music_policy=contract.music_policy,
        intro_seconds=contract.intro_seconds,
        outro_seconds=contract.outro_seconds,
        render_job_public_id=contract.render_job_public_id,
        created_at=contract.created_at,
    )


@router.post("/packs", response_model=ClipPackResponse)
def create_clip_pack(
    payload: ClipPackCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return pack_to_response(ClippingService(store).create_pack(payload=payload, user_id=user_id))
    except Exception as error:
        handle_clipping_error(error)


@router.get("/packs", response_model=list[ClipPackResponse])
def list_my_clip_packs(
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    return [pack_to_response(pack) for pack in ClippingService(store).list_packs(user_id)]


@router.get("/packs/{pack_public_id}", response_model=ClipPackDetailResponse)
def get_clip_pack(
    pack_public_id: str,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        service = ClippingService(store)
        pack = service.get_pack(pack_public_id, user_id)
        return ClipPackDetailResponse(
            pack=pack_to_response(pack),
            moments=[moment_to_response(item) for item in service.list_pack_moments(pack)],
            candidates=[candidate_to_response(item) for item in service.list_pack_candidates(pack)],
        )
    except Exception as error:
        handle_clipping_error(error)


@router.post("/moments", response_model=ClipMomentResponse)
def create_clip_moment(
    payload: ClipMomentCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return moment_to_response(ClippingService(store).create_moment(payload=payload, user_id=user_id))
    except Exception as error:
        handle_clipping_error(error)


@router.post("/candidates", response_model=ClipCandidateResponse)
def create_clip_candidate(
    payload: ClipCandidateCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return candidate_to_response(ClippingService(store).create_candidate(payload=payload, user_id=user_id))
    except Exception as error:
        handle_clipping_error(error)


@router.post("/candidates/score", response_model=ClipCandidateResponse)
def score_clip_candidate(
    payload: ClipCandidateScoreRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return candidate_to_response(ClippingService(store).score_candidate(payload=payload, user_id=user_id))
    except Exception as error:
        handle_clipping_error(error)


@router.post("/render-contracts", response_model=ClipRenderContractResponse)
def create_render_contract(
    payload: ClipRenderContractCreateRequest,
    store: WorldsStore = Depends(get_worlds_store),
    user_id: str = Depends(get_demo_user_id),
):
    try:
        return render_contract_to_response(
            ClippingService(store).create_render_contract(payload=payload, user_id=user_id)
        )
    except Exception as error:
        handle_clipping_error(error)
