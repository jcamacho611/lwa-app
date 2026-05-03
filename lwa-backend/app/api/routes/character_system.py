"""
Character System API Routes

Provides endpoints for the Character System:
- Character profiles
- Character states and dialogue
- Character skins and abilities
- Quest management
- XP and progression
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
from pydantic import BaseModel

from ...services.character_system import character_system
from ...services.character_system import CharacterState, CharacterRole, CharacterRarity

router = APIRouter(prefix="/v1/character", tags=["character"])

# Request/Response Models
class CharacterDialogueRequest(BaseModel):
    character_id: str
    state: str

class CharacterSkinUnlockRequest(BaseModel):
    character_id: str
    skin_id: str
    user_level: int
    user_quests_completed: int

class QuestCompleteRequest(BaseModel):
    character_id: str
    quest_id: str
    user_progress: Dict[str, int]

class XPAwardRequest(BaseModel):
    character_id: str
    xp_type: str
    amount: int
    reason: Optional[str] = ""

# Character Profiles
@router.get("/profiles")
async def get_all_characters() -> Dict[str, Any]:
    """Get all character profiles."""
    try:
        characters = character_system.get_all_characters()
        return {
            "success": True,
            "characters": [
                {
                    "id": char.id,
                    "role": char.role.value,
                    "name": char.name,
                    "description": char.description,
                    "unlocked": char.unlocked,
                    "is_main_mascot": char.is_main_mascot,
                    "skins_count": len(char.skins),
                    "abilities_count": len(char.abilities),
                    "quests_count": len(char.quests)
                }
                for char in characters
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles/{character_id}")
async def get_character_profile(character_id: str) -> Dict[str, Any]:
    """Get specific character profile."""
    try:
        character = character_system.get_character(character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return {
            "success": True,
            "character": {
                "id": character.id,
                "role": character.role.value,
                "name": character.name,
                "description": character.description,
                "unlocked": character.unlocked,
                "is_main_mascot": character.is_main_mascot,
                "skins": [
                    {
                        "id": skin.id,
                        "name": skin.name,
                        "description": skin.description,
                        "rarity": skin.rarity.value,
                        "unlocked": skin.unlocked,
                        "unlock_requirements": skin.unlock_requirements
                    }
                    for skin in character.skins
                ],
                "abilities": [
                    {
                        "id": ability.id,
                        "name": ability.name,
                        "description": ability.description,
                        "ability_type": ability.ability_type,
                        "unlock_level": ability.unlock_level
                    }
                    for ability in character.abilities
                ],
                "quests": [
                    {
                        "id": quest.id,
                        "name": quest.name,
                        "description": quest.description,
                        "requirements": quest.requirements,
                        "rewards": quest.rewards,
                        "difficulty": quest.difficulty,
                        "completed": quest.completed
                    }
                    for quest in character.quests
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/main-mascot")
async def get_main_mascot() -> Dict[str, Any]:
    """Get the main mascot character (Lee-Wuh)."""
    try:
        character = character_system.get_main_mascot()
        if not character:
            raise HTTPException(status_code=404, detail="Main mascot not found")
        
        return {
            "success": True,
            "character": {
                "id": character.id,
                "name": character.name,
                "description": character.description,
                "role": character.role.value
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Character Dialogue
@router.post("/dialogue")
async def get_character_dialogue(request: CharacterDialogueRequest) -> Dict[str, Any]:
    """Get dialogue for character in specific state."""
    try:
        state = CharacterState(request.state)
        dialogue = character_system.get_character_dialogue(request.character_id, state)
        
        return {
            "success": True,
            "character_id": request.character_id,
            "state": request.state,
            "dialogue": dialogue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dialogue/{character_id}/{state}")
async def get_character_dialogue_by_path(character_id: str, state: str) -> Dict[str, Any]:
    """Get dialogue for character in specific state (path version)."""
    try:
        state_enum = CharacterState(state)
        dialogue = character_system.get_character_dialogue(character_id, state_enum)
        
        return {
            "success": True,
            "character_id": character_id,
            "state": state,
            "dialogue": dialogue
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Character Skins
@router.post("/skins/unlock")
async def unlock_character_skin(request: CharacterSkinUnlockRequest) -> Dict[str, Any]:
    """Attempt to unlock a character skin."""
    try:
        unlocked = character_system.unlock_skin(
            character_id=request.character_id,
            skin_id=request.skin_id,
            user_level=request.user_level,
            user_quests_completed=request.user_quests_completed
        )
        
        return {
            "success": True,
            "unlocked": unlocked,
            "character_id": request.character_id,
            "skin_id": request.skin_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/skins/{character_id}")
async def get_unlocked_skins(character_id: str) -> Dict[str, Any]:
    """Get unlocked skins for a character."""
    try:
        skins = character_system.get_unlocked_skins(character_id)
        
        return {
            "success": True,
            "character_id": character_id,
            "skins": [
                {
                    "id": skin.id,
                    "name": skin.name,
                    "description": skin.description,
                    "rarity": skin.rarity.value,
                    "unlocked": skin.unlocked,
                    "unlocked_at": skin.unlocked_at
                }
                for skin in skins
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Quest Management
@router.post("/quests/complete")
async def complete_quest(request: QuestCompleteRequest) -> Dict[str, Any]:
    """Attempt to complete a character quest."""
    try:
        completed = character_system.complete_quest(
            character_id=request.character_id,
            quest_id=request.quest_id,
            user_progress=request.user_progress
        )
        
        return {
            "success": True,
            "completed": completed,
            "character_id": request.character_id,
            "quest_id": request.quest_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quests/{character_id}")
async def get_available_quests(character_id: str, realm_type: Optional[str] = None) -> Dict[str, Any]:
    """Get available quests for a character."""
    try:
        from ...services.character_system import RealmType
        realm = RealmType(realm_type) if realm_type else None
        
        quests = character_system.get_available_quests(character_id, realm)
        
        return {
            "success": True,
            "character_id": character_id,
            "realm_type": realm_type,
            "quests": [
                {
                    "id": quest.id,
                    "name": quest.name,
                    "description": quest.description,
                    "requirements": quest.requirements,
                    "rewards": quest.rewards,
                    "difficulty": quest.difficulty,
                    "completed": quest.completed
                }
                for quest in quests
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Character Abilities
@router.get("/abilities/{character_id}")
async def get_available_abilities(character_id: str, user_level: int = 1) -> Dict[str, Any]:
    """Get abilities available for user level."""
    try:
        abilities = character_system.get_available_abilities(character_id, user_level)
        
        return {
            "success": True,
            "character_id": character_id,
            "user_level": user_level,
            "abilities": [
                {
                    "id": ability.id,
                    "name": ability.name,
                    "description": ability.description,
                    "ability_type": ability.ability_type,
                    "unlock_level": ability.unlock_level
                }
                for ability in abilities
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Information
@router.get("/states")
async def get_character_states() -> Dict[str, List[str]]:
    """Get available character states."""
    return {
        "states": [state.value for state in CharacterState],
        "default": CharacterState.IDLE.value
    }

@router.get("/roles")
async def get_character_roles() -> Dict[str, List[str]]:
    """Get available character roles."""
    return {
        "roles": [role.value for role in CharacterRole],
        "main_mascot": CharacterRole.LEE_WUH.value
    }

@router.get("/rarities")
async def get_skin_rarities() -> Dict[str, List[str]]:
    """Get available skin rarities."""
    return {
        "rarities": [rarity.value for rarity in CharacterRarity],
        "order": ["common", "rare", "epic", "legendary", "mythic"]
    }

# Health check
@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Check health of character system."""
    main_mascot = character_system.get_main_mascot()
    return {
        "status": "healthy",
        "main_mascot": main_mascot.name if main_mascot else "none",
        "total_characters": len(character_system.get_all_characters())
    }
