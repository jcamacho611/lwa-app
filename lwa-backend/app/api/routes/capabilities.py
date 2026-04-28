from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...services.capability_registry import (
    CapabilityCatalogResponse,
    CapabilityRecord,
    CapabilityStatusResponse,
    PublicClaimsResponse,
    RailwayServicePlan,
    capability_catalog,
    capability_status_payload,
    get_capability,
    known_statuses,
    public_claim_payload,
    railway_service_plan,
)

router = APIRouter(prefix="/v1/capabilities", tags=["capabilities"])


@router.get("", response_model=CapabilityCatalogResponse)
async def list_capability_catalog() -> CapabilityCatalogResponse:
    return capability_catalog()


@router.get("/public-claims", response_model=PublicClaimsResponse)
async def list_public_claims() -> PublicClaimsResponse:
    return public_claim_payload()


@router.get("/railway-plan", response_model=RailwayServicePlan)
async def get_railway_plan() -> RailwayServicePlan:
    return railway_service_plan()


@router.get("/status/{status}", response_model=CapabilityStatusResponse)
async def list_capabilities_for_status(status: str) -> CapabilityStatusResponse:
    normalized = status.strip().lower()
    if normalized not in known_statuses():
        raise HTTPException(status_code=404, detail="Capability status not found")
    return capability_status_payload(normalized)  # type: ignore[arg-type]


@router.get("/{capability_id}", response_model=CapabilityRecord)
async def get_capability_detail(capability_id: str) -> CapabilityRecord:
    capability = get_capability(capability_id)
    if capability is None:
        raise HTTPException(status_code=404, detail="Capability not found")
    return capability
