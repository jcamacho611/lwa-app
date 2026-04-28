from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ...services.intelligence_data_core import get_intelligence_core
from ...services.intelligence_registry import (
    build_unified_category_profile,
    build_unified_platform_profile,
    load_intelligence_tables,
    validate_intelligence_tables,
)

router = APIRouter(prefix="/v1/intelligence", tags=["intelligence"])


class ClaimCheckRequest(BaseModel):
    text: str


@router.get("")
def intelligence_index() -> dict[str, object]:
    core = get_intelligence_core()
    tables = load_intelligence_tables()
    return {
        "ok": True,
        "validation": validate_intelligence_tables(),
        "runtime_sources": tables.get("runtime_sources", {}),
        "counts": {
            "viral_signals": len(core.viral_signal_rules()),
            "platform_rules": len(core.viral_platform_rules()),
            "categories": len(core.viral_content_category_rules()),
            "hook_formulas": len(core.hook_formula_library()),
            "caption_styles": len(core.caption_presets()),
            "badge_rules": len(core.frontend_badge_rules()),
            "thumbnail_rules": len(core.thumbnail_rules()),
            "campaign_readiness_rules": len(core.campaign_readiness_rules()),
            "sales_rows": len(core.sales_positioning()),
            "competitor_rows": len(core.competitor_matrix()),
        },
    }


@router.get("/viral-signals")
def viral_signals() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.viral_signal_rules()}


@router.get("/platform-profiles")
def platform_profiles() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.unified_platform_profiles()}


@router.get("/category-profiles")
def category_profiles() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.unified_category_profiles()}


@router.get("/hook-formulas")
def hook_formulas() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.hook_formula_library()}


@router.get("/caption-styles")
def caption_styles() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.caption_presets()}


@router.get("/frontend-badges")
def frontend_badges() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.frontend_badge_rules()}


@router.get("/thumbnail-rules")
def thumbnail_rules() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.thumbnail_rules()}


@router.get("/campaign-readiness")
def campaign_readiness() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.campaign_readiness_rules()}


@router.get("/sales-positioning")
def sales_positioning() -> dict[str, object]:
    core = get_intelligence_core()
    return {"items": core.sales_positioning()}


@router.get("/platform-profiles/{platform}")
def platform_profile(platform: str) -> dict[str, object]:
    return {"item": build_unified_platform_profile(platform)}


@router.get("/category-profiles/{category}")
def category_profile(category: str) -> dict[str, object]:
    return {"item": build_unified_category_profile(category)}


@router.post("/claim-check")
def claim_check(request: ClaimCheckRequest) -> dict[str, object]:
    core = get_intelligence_core()
    return core.claim_guard_check(request.text)
