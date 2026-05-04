"""Entitlement and credit management API routes.

Provides endpoints for checking access, spending credits,
and managing feature unlocks.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ...services.entitlement_service import (
    check_entitlement,
    spend_credit,
    grant_credits,
    unlock_feature,
    get_user_entitlement_status,
    get_entitlement_summary,
    FEATURE_COSTS,
)

router = APIRouter(prefix="/api/v1/entitlements", tags=["entitlements"])


class CheckEntitlementRequest(BaseModel):
    feature: str


class CheckEntitlementResponse(BaseModel):
    success: bool
    user_id: str
    feature: str
    cost: int
    has_access: bool
    credits_required: int
    credits_available: int
    credits_after: int
    unlocked: bool
    free_mode_active: bool
    message: str


class SpendCreditRequest(BaseModel):
    feature: str
    description: Optional[str] = None


class SpendCreditResponse(BaseModel):
    success: bool
    user_id: str
    feature: str
    cost: int
    credits_remaining: int
    credits_spent: int
    free_mode: bool
    transaction_id: str
    message: str


class GrantCreditsRequest(BaseModel):
    amount: int = Field(..., ge=1, le=1000)
    reason: Optional[str] = None


class GrantCreditsResponse(BaseModel):
    success: bool
    user_id: str
    credits_granted: int
    credits_total: int
    transaction_id: str
    message: str


class UnlockFeatureRequest(BaseModel):
    feature: str
    permanent: bool = True


class UnlockFeatureResponse(BaseModel):
    success: bool
    user_id: str
    feature: str
    unlocked_features: list[str]
    permanent: bool
    message: str


class UserEntitlementStatusResponse(BaseModel):
    success: bool
    user_id: str
    credits: dict
    unlocked_features: list[str]
    free_mode_active: bool
    feature_costs: dict[str, int]
    recent_transactions: list[dict]


class EntitlementSummaryResponse(BaseModel):
    success: bool
    total_users: int
    total_credits_in_system: int
    total_transactions: int
    free_mode_active: bool
    feature_costs: dict[str, int]


# Mock user ID - replace with auth
MOCK_USER_ID = "user_demo_001"


@router.post("/check", response_model=CheckEntitlementResponse)
async def api_check_entitlement(request: CheckEntitlementRequest):
    """Check if user has entitlement for a feature."""
    try:
        result = check_entitlement(MOCK_USER_ID, request.feature)
        return CheckEntitlementResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Entitlement check failed: {exc}")


@router.post("/spend", response_model=SpendCreditResponse)
async def api_spend_credit(request: SpendCreditRequest):
    """Spend credit for a feature use."""
    try:
        result = spend_credit(MOCK_USER_ID, request.feature, request.description or "")
        if not result["success"]:
            raise HTTPException(status_code=402, detail=result["message"])
        return SpendCreditResponse(**result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Credit spend failed: {exc}")


@router.post("/grant", response_model=GrantCreditsResponse)
async def api_grant_credits(request: GrantCreditsRequest):
    """Grant credits to user (admin/purchase/reward)."""
    try:
        result = grant_credits(MOCK_USER_ID, request.amount, request.reason or "")
        return GrantCreditsResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Grant credits failed: {exc}")


@router.post("/unlock", response_model=UnlockFeatureResponse)
async def api_unlock_feature(request: UnlockFeatureRequest):
    """Unlock a feature for the user."""
    try:
        result = unlock_feature(MOCK_USER_ID, request.feature, request.permanent)
        return UnlockFeatureResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unlock feature failed: {exc}")


@router.get("/status", response_model=UserEntitlementStatusResponse)
async def api_get_user_status():
    """Get full entitlement status for current user."""
    try:
        result = get_user_entitlement_status(MOCK_USER_ID)
        return UserEntitlementStatusResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Get status failed: {exc}")


@router.get("/summary", response_model=EntitlementSummaryResponse)
async def api_get_entitlement_summary():
    """Get system-wide entitlement summary (admin)."""
    try:
        result = get_entitlement_summary()
        return EntitlementSummaryResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Get summary failed: {exc}")


@router.get("/feature-costs")
async def api_get_feature_costs():
    """Get all feature costs."""
    return {
        "success": True,
        "feature_costs": FEATURE_COSTS,
        "free_mode_active": True,
    }
