from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user_optional
from app.core.config import Settings, get_settings
from app.services.ai_cost_control import get_cost_control

router = APIRouter()


@router.get("/ai-costs/user-summary")
async def get_user_cost_summary(
    days: int = 7,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get cost summary for the current user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    cost_control = get_cost_control(settings)
    
    summary = cost_control.get_user_cost_summary(user_id, days)
    
    return JSONResponse(content={
        "user_id": user_id,
        "period_days": days,
        "summary": summary
    })


@router.get("/ai-costs/system-summary")
async def get_system_cost_summary(
    days: int = 7,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get system-wide cost summary (admin only)."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # For now, allow all authenticated users to see system summary
    # In production, this should be restricted to administrators
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    
    cost_control = get_cost_control(settings)
    summary = cost_control.get_system_cost_summary(days)
    
    return JSONResponse(content={
        "requested_by": user_id,
        "period_days": days,
        "summary": summary
    })


@router.get("/ai-costs/estimate")
async def estimate_request_cost(
    model: str,
    input_tokens: int = 1000,
    output_tokens: int = 1000,
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Estimate cost for an AI request."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    cost_control = get_cost_control(settings)
    estimated_cost = cost_control.estimate_request_cost(model, input_tokens, output_tokens)
    
    return JSONResponse(content={
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost,
        "cost_per_1k_tokens": cost_control.estimate_request_cost(model, 1000, 0) * 1000
    })


@router.get("/ai-costs/model-pricing")
async def get_model_pricing(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get pricing information for all available models."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    from ..services.ai_cost_control import MODEL_COSTS_PER_1K_TOKENS
    
    return JSONResponse(content={
        "model_costs_per_1k_tokens": MODEL_COSTS_PER_1K_TOKENS,
        "available_models": {
            "anthropic": {
                "opus": settings.anthropic_model_opus,
                "sonnet": settings.anthropic_model_sonnet,
                "haiku": settings.anthropic_model_haiku,
            },
            "openai": {
                "gpt_4_1_mini": settings.openai_model,
            }
        }
    })


@router.get("/ai-costs/usage-limits")
async def get_usage_limits(
    current_user: dict = Depends(get_current_user_optional),
    settings: Settings = Depends(get_settings),
):
    """Get current usage limits for the user."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    user_id = current_user.get("user_id", f"guest:{current_user.get('id', 'unknown')}")
    cost_control = get_cost_control(settings)
    
    today = cost_control.usage_data.get(cost_control.usage_data.get("today", ""), {})
    
    # Get today's usage
    today_key = list(cost_control.usage_data.keys())[-1] if cost_control.usage_data else None
    today_usage = cost_control.usage_data.get(today_key, {})
    
    daily_requests = 0
    daily_cost = 0.0
    
    for key, value in today_usage.items():
        if key.startswith(("clip_packaging:", "classify_metadata:")) and key.endswith(f":{user_id}"):
            daily_requests += value
        elif key.startswith(f"cost:{user_id}"):
            daily_cost += value
    
    # Determine limits
    is_guest = user_id.startswith("guest:")
    daily_request_limit = cost_control.rate_limit_guest_rpm if is_guest else 100
    daily_budget_limit = 10.0 if is_guest else 50.0
    
    return JSONResponse(content={
        "user_id": user_id,
        "is_guest": is_guest,
        "daily_limits": {
            "requests": daily_request_limit,
            "cost_usd": daily_budget_limit,
        },
        "today_usage": {
            "requests": daily_requests,
            "cost_usd": daily_cost,
            "requests_remaining": max(0, daily_request_limit - daily_requests),
            "cost_remaining": max(0.0, daily_budget_limit - daily_cost),
        }
    })
