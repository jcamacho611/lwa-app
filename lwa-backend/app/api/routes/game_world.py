"""
Game World System API Routes

Provides endpoints for the Game World System:
- Creator realms and progression
- Quest management
- XP and leveling
- Unlockable rewards
- Game progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...services.game_world_system import game_world_system
from ...services.game_world_system import RealmType, XPType, UnlockableType

router = APIRouter(prefix="/v1/game-world", tags=["game-world"])

# Request/Response Models
class XPAwardRequest(BaseModel):
    creator_id: str
    xp_type: str
    amount: int
    reason: Optional[str] = ""

class QuestCompleteRequest(BaseModel):
    creator_id: str
    quest_id: str
    progress: Dict[str, int]

class RealmUnlockRequest(BaseModel):
    creator_id: str
    realm_type: str

# Creator Progress
@router.get("/progress/{creator_id}")
async def get_creator_progress(creator_id: str) -> Dict[str, Any]:
    """Get complete game progress for a creator."""
    try:
        progress = game_world_system.get_creator_progress(creator_id)
        
        return {
            "success": True,
            "creator_id": creator_id,
            "xp": {
                "creator_id": progress.xp.creator_id,
                "level": progress.xp.level,
                "total_xp": progress.xp.total_xp,
                "next_level_xp": progress.xp.next_level_xp,
                "xp_totals": {
                    xp_type.value: amount for xp_type, amount in progress.xp.xp_totals.items()
                },
                "achievements": progress.xp.achievements,
                "titles": progress.xp.titles
            },
            "unlocked_realms": [realm.value for realm in progress.unlocked_realms],
            "completed_quests": progress.completed_quests,
            "unlocked_items": progress.unlocked_items,
            "current_realm": progress.current_realm.value if progress.current_realm else None,
            "achievements": progress.achievements
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# XP Management
@router.post("/xp/award")
async def award_xp(request: XPAwardRequest) -> Dict[str, Any]:
    """Award experience points to a creator."""
    try:
        xp_type = XPType(request.xp_type)
        updated_xp = game_world_system.award_xp(
            creator_id=request.creator_id,
            xp_type=xp_type,
            amount=request.amount,
            reason=request.reason or "API award"
        )
        
        return {
            "success": True,
            "creator_id": request.creator_id,
            "xp_type": request.xp_type,
            "amount": request.amount,
            "updated_xp": {
                "level": updated_xp.level,
                "total_xp": updated_xp.total_xp,
                "next_level_xp": updated_xp.next_level_xp,
                "xp_totals": {
                    xp_type.value: amount for xp_type, amount in updated_xp.xp_totals.items()
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quest Management
@router.post("/quests/complete")
async def complete_quest(request: QuestCompleteRequest) -> Dict[str, Any]:
    """Complete a creator quest."""
    try:
        completed = game_world_system.complete_quest(
            creator_id=request.creator_id,
            quest_id=request.quest_id,
            progress=request.progress
        )
        
        return {
            "success": True,
            "completed": completed,
            "creator_id": request.creator_id,
            "quest_id": request.quest_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quests/{creator_id}")
async def get_available_quests(creator_id: str, realm_type: Optional[str] = None) -> Dict[str, Any]:
    """Get available quests for a creator."""
    try:
        realm = RealmType(realm_type) if realm_type else None
        quests = game_world_system.get_available_quests(creator_id, realm)
        
        return {
            "success": True,
            "creator_id": creator_id,
            "realm_type": realm_type,
            "quests": [
                {
                    "id": quest.id,
                    "name": quest.name,
                    "description": quest.description,
                    "realm_type": quest.realm_type.value,
                    "requirements": quest.requirements,
                    "rewards": quest.rewards,
                    "difficulty": quest.difficulty,
                    "completed": quest.completed,
                    "repeatable": quest.repeatable
                }
                for quest in quests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Realm Management
@router.post("/realms/unlock")
async def unlock_realm(request: RealmUnlockRequest) -> Dict[str, Any]:
    """Unlock a creator realm."""
    try:
        realm_type = RealmType(request.realm_type)
        unlocked = game_world_system.unlock_realm(request.creator_id, realm_type)
        
        return {
            "success": True,
            "unlocked": unlocked,
            "creator_id": request.creator_id,
            "realm_type": request.realm_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realms")
async def get_all_realms() -> Dict[str, Any]:
    """Get all available realms."""
    try:
        realms = []
        for realm_type, realm in game_world_system._realms.items():
            realms.append({
                "realm_type": realm.realm_type.value,
                "name": realm.name,
                "description": realm.description,
                "required_level": realm.required_level,
                "required_xp": {
                    xp_type.value: amount for xp_type, amount in realm.required_xp.items()
                },
                "required_quests": realm.required_quests,
                "unlocked": realm.unlocked,
                "rewards": realm.rewards
            })
        
        return {
            "success": True,
            "realms": realms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realms/{creator_id}/recommendations")
async def get_realm_recommendations(creator_id: str) -> Dict[str, Any]:
    """Get recommendations for next realms to unlock."""
    try:
        recommendations = game_world_system.get_realm_recommendations(creator_id)
        
        return {
            "success": True,
            "creator_id": creator_id,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Information
@router.get("/realm-types")
async def get_realm_types() -> Dict[str, List[str]]:
    """Get available realm types."""
    return {
        "realm_types": [realm.value for realm in RealmType],
        "progression_order": [
            RealmType.REALM_OF_SOURCES.value,
            RealmType.CLIP_FORGE.value,
            RealmType.PROOF_VAULT.value,
            RealmType.CAMPAIGN_TEMPLE.value,
            RealmType.RENDER_FORGE.value,
            RealmType.TIMELINE_TEMPLE.value,
            RealmType.OFFER_MARKET.value,
            RealmType.COUNCIL_CHAMBER.value,
            RealmType.LEE_WUH_THRONE_ROOM.value
        ]
    }

@router.get("/xp-types")
async def get_xp_types() -> Dict[str, List[str]]:
    """Get available XP types."""
    return {
        "xp_types": [xp_type.value for xp_type in XPType],
        "primary": XPType.CREATOR_XP.value,
        "special": [XPType.TRUST_XP.value, XPType.SALES_XP.value, XPType.PROOF_XP.value]
    }

@router.get("/unlockable-types")
async def get_unlockable_types() -> Dict[str, List[str]]:
    """Get available unlockable types."""
    return {
        "unlockable_types": [unlockable.value for unlockable in UnlockableType],
        "categories": {
            "items": [UnlockableType.REALM_KEY.value, UnlockableType.BADGE.value, UnlockableType.EMOTE.value],
            "cosmetics": [UnlockableType.CHARACTER_SKIN.value, UnlockableType.EFFECT.value],
            "abilities": [UnlockableType.ABILITY_UNLOCK.value],
            "status": [UnlockableType.CREATOR_TITLE.value]
        }
    }

# Leaderboard (placeholder for future implementation)
@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10) -> Dict[str, Any]:
    """Get creator leaderboard (placeholder)."""
    return {
        "success": True,
        "leaderboard": [],
        "limit": limit,
        "note": "Leaderboard system not yet implemented"
    }

# Health check
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Check health of game world system."""
    realms = game_world_system._realms
    return {
        "status": "healthy",
        "total_realms": len(realms),
        "main_realm": RealmType.REALM_OF_SOURCES.value,
        "ultimate_realm": RealmType.LEE_WUH_THRONE_ROOM.value
    }
