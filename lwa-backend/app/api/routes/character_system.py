"""
Character System API Routes
Handles character profiles, attributes, progression, and state management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/api/v1/character", tags=["character_system"])

# Pydantic models
class CharacterAttribute(BaseModel):
    name: str
    value: float
    max_value: float
    description: str

class CharacterSkill(BaseModel):
    name: str
    level: int
    max_level: int
    experience: int
    description: str

class CharacterState(BaseModel):
    mood: str
    energy: float
    focus: float
    creativity: float
    last_updated: str

class CharacterProfile(BaseModel):
    id: str
    name: str
    display_name: str
    avatar_url: Optional[str]
    bio: str
    level: int
    experience: int
    next_level_exp: int
    attributes: List[CharacterAttribute]
    skills: List[CharacterSkill]
    state: CharacterState
    created_at: str
    updated_at: str

class CharacterCreateRequest(BaseModel):
    name: str
    display_name: str
    bio: Optional[str] = ""

class CharacterUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class CharacterActionRequest(BaseModel):
    action_type: str
    action_data: Optional[Dict[str, Any]] = None

class CharacterActionResponse(BaseModel):
    success: bool
    message: str
    character: Optional[CharacterProfile]
    rewards: Optional[Dict[str, Any]] = None

class ProgressionUpdate(BaseModel):
    experience_gained: int
    skill_improvements: Optional[List[Dict[str, Any]]] = None
    attribute_changes: Optional[List[Dict[str, Any]]] = None

# Mock character database
MOCK_CHARACTERS = {
    "char_lee_wuh_001": CharacterProfile(
        id="char_lee_wuh_001",
        name="lee_wuh",
        display_name="Lee-Wuh",
        avatar_url="/brand/lee-wuh/lee-wuh-avatar.png",
        bio="The final boss of lazy content. Guardian of the creator engine.",
        level=42,
        experience=87500,
        next_level_exp=100000,
        attributes=[
            CharacterAttribute(name="creativity", value=95, max_value=100, description="Ability to generate novel ideas and approaches"),
            CharacterAttribute(name="focus", value=88, max_value=100, description="Capacity to maintain deep work states"),
            CharacterAttribute(name="energy", value=92, max_value=100, description="Stamina for sustained creative output"),
            CharacterAttribute(name="analytical", value=85, max_value=100, description="Skill at breaking down complex problems"),
            CharacterAttribute(name="social", value=78, max_value=100, description="Ability to connect with audiences"),
        ],
        skills=[
            CharacterSkill(name="clip_generation", level=15, max_level=20, experience=7500, description="Automatically identify and package video moments"),
            CharacterSkill(name="hook_writing", level=12, max_level=20, experience=6000, description="Craft compelling opening lines"),
            CharacterSkill(name="caption_optimization", level=11, max_level=20, experience=5500, description="Perfect text overlays for engagement"),
            CharacterSkill(name="thumbnail_design", level=10, max_level=20, experience=5000, description="Create scroll-stopping visuals"),
            CharacterSkill(name="platform_strategy", level=13, max_level=20, experience=6500, description="Optimize content for each platform"),
        ],
        state=CharacterState(
            mood="inspired",
            energy=0.92,
            focus=0.88,
            creativity=0.95,
            last_updated=datetime.utcnow().isoformat()
        ),
        created_at="2024-01-15T00:00:00Z",
        updated_at=datetime.utcnow().isoformat()
    )
}

@router.get("/profiles", response_model=Dict[str, Any])
async def list_character_profiles(
    limit: int = 50,
    offset: int = 0,
    include_system: bool = True
):
    """List all character profiles."""
    characters = list(MOCK_CHARACTERS.values())
    total = len(characters)
    
    return {
        "success": True,
        "characters": [char.dict() for char in characters[offset:offset + limit]],
        "total_count": total,
        "limit": limit,
        "offset": offset
    }

@router.get("/profile/{character_id}", response_model=Dict[str, Any])
async def get_character_profile(character_id: str):
    """Get detailed character profile."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    return {
        "success": True,
        "character": MOCK_CHARACTERS[character_id].dict()
    }

@router.post("/profile", response_model=Dict[str, Any])
async def create_character_profile(request: CharacterCreateRequest):
    """Create a new character profile."""
    character_id = f"char_{request.name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    
    new_character = CharacterProfile(
        id=character_id,
        name=request.name,
        display_name=request.display_name,
        bio=request.bio or "",
        level=1,
        experience=0,
        next_level_exp=1000,
        attributes=[
            CharacterAttribute(name="creativity", value=50, max_value=100, description="Creative capacity"),
            CharacterAttribute(name="focus", value=50, max_value=100, description="Focus ability"),
            CharacterAttribute(name="energy", value=50, max_value=100, description="Energy level"),
        ],
        skills=[],
        state=CharacterState(
            mood="neutral",
            energy=0.75,
            focus=0.75,
            creativity=0.75,
            last_updated=datetime.utcnow().isoformat()
        ),
        created_at=datetime.utcnow().isoformat(),
        updated_at=datetime.utcnow().isoformat()
    )
    
    MOCK_CHARACTERS[character_id] = new_character
    
    return {
        "success": True,
        "character": new_character.dict(),
        "message": f"Character '{request.display_name}' created successfully"
    }

@router.patch("/profile/{character_id}", response_model=Dict[str, Any])
async def update_character_profile(character_id: str, request: CharacterUpdateRequest):
    """Update character profile."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = MOCK_CHARACTERS[character_id]
    
    if request.display_name:
        character.display_name = request.display_name
    if request.bio is not None:
        character.bio = request.bio
    if request.avatar_url:
        character.avatar_url = request.avatar_url
    
    character.updated_at = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "character": character.dict(),
        "message": "Character updated successfully"
    }

@router.post("/profile/{character_id}/action", response_model=CharacterActionResponse)
async def perform_character_action(character_id: str, request: CharacterActionRequest):
    """Perform an action with the character."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = MOCK_CHARACTERS[character_id]
    
    # Simulate action processing
    action_rewards = {
        "experience_gained": 100,
        "attributes_improved": [],
        "mood_change": "positive"
    }
    
    # Update character state
    character.experience += action_rewards["experience_gained"]
    if character.experience >= character.next_level_exp:
        character.level += 1
        character.next_level_exp = int(character.next_level_exp * 1.5)
        action_rewards["level_up"] = True
    
    character.state.last_updated = datetime.utcnow().isoformat()
    character.updated_at = datetime.utcnow().isoformat()
    
    return CharacterActionResponse(
        success=True,
        message=f"Action '{request.action_type}' completed successfully",
        character=character,
        rewards=action_rewards
    )

@router.get("/profile/{character_id}/progression", response_model=Dict[str, Any])
async def get_character_progression(character_id: str):
    """Get character progression history."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = MOCK_CHARACTERS[character_id]
    
    return {
        "success": True,
        "character_id": character_id,
        "level": character.level,
        "experience": character.experience,
        "next_level_exp": character.next_level_exp,
        "progress_percentage": (character.experience / character.next_level_exp) * 100,
        "attributes": [attr.dict() for attr in character.attributes],
        "skills": [skill.dict() for skill in character.skills]
    }

@router.post("/profile/{character_id}/progression", response_model=Dict[str, Any])
async def update_character_progression(character_id: str, update: ProgressionUpdate):
    """Update character progression."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = MOCK_CHARACTERS[character_id]
    
    # Add experience
    character.experience += update.experience_gained
    
    # Check for level up
    level_ups = 0
    while character.experience >= character.next_level_exp:
        character.level += 1
        character.next_level_exp = int(character.next_level_exp * 1.5)
        level_ups += 1
    
    character.updated_at = datetime.utcnow().isoformat()
    
    return {
        "success": True,
        "message": f"Progression updated: {update.experience_gained} XP gained" + 
                   (f", {level_ups} level(s) gained!" if level_ups > 0 else ""),
        "character": character.dict()
    }

@router.get("/profile/{character_id}/state", response_model=Dict[str, Any])
async def get_character_state(character_id: str):
    """Get current character state."""
    if character_id not in MOCK_CHARACTERS:
        raise HTTPException(status_code=404, detail="Character not found")
    
    character = MOCK_CHARACTERS[character_id]
    
    return {
        "success": True,
        "character_id": character_id,
        "state": character.state.dict(),
        "current_mood": character.state.mood,
        "energy_level": character.state.energy,
        "focus_level": character.state.focus,
        "creativity_level": character.state.creativity
    }

@router.get("/templates", response_model=Dict[str, Any])
async def list_character_templates():
    """List available character templates."""
    templates = [
        {
            "id": "template_creator",
            "name": "Creator",
            "description": "A creative powerhouse focused on content generation",
            "starting_attributes": {
                "creativity": 70,
                "focus": 60,
                "energy": 65
            }
        },
        {
            "id": "template_analyst",
            "name": "Analyst",
            "description": "Data-driven and detail-oriented",
            "starting_attributes": {
                "analytical": 70,
                "focus": 75,
                "creativity": 50
            }
        },
        {
            "id": "template_strategist",
            "name": "Strategist",
            "description": "Big picture thinker with strong planning skills",
            "starting_attributes": {
                "analytical": 65,
                "social": 60,
                "focus": 70
            }
        },
        {
            "id": "template_mascot",
            "name": "Brand Mascot",
            "description": "Charismatic brand representative",
            "starting_attributes": {
                "social": 80,
                "creativity": 75,
                "energy": 85
            }
        }
    ]
    
    return {
        "success": True,
        "templates": templates,
        "total_count": len(templates)
    }
