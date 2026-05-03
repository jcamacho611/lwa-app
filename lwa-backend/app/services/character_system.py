"""
Character System v0

Supports Lee-Wuh as the default character with metadata for
future council characters, states, skins, abilities, dialogue, unlocks, and quests.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class CharacterRole(str, Enum):
    """Character roles in the LWA ecosystem."""
    
    LEE_WUH = "lee_wuh"
    STRATEGIST = "strategist"
    EDITOR = "editor"
    AUDIO_ENGINEER = "audio_engineer"
    RENDER_SPECIALIST = "render_specialist"
    SALES_STRATEGIST = "sales_strategist"
    TREND_ANALYST = "trend_analyst"
    SAFETY_GUARD = "safety_guard"
    MARKETPLACE_GUIDE = "marketplace_guide"
    GAME_MASTER = "game_master"


class CharacterState(str, Enum):
    """Character visual and behavioral states."""
    
    IDLE = "idle"
    THINKING = "thinking"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    RENDERING = "rendering"
    ANALYZING = "analyzing"
    EXCITED = "excited"
    OVERLORD = "overlord"
    SLEEPING = "sleeping"
    WORKING = "working"


class CharacterRarity(str, Enum):
    """Character rarity for unlock progression."""
    
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


@dataclass
class CharacterSkin:
    """Character skin/appearance variant."""
    
    id: str
    name: str
    description: str
    rarity: CharacterRarity
    thumbnail_url: Optional[str] = None
    unlock_requirements: Dict[str, any] = field(default_factory=dict)
    unlocked: bool = False
    unlocked_at: Optional[str] = None


@dataclass
class CharacterAbility:
    """Character ability or power."""
    
    id: str
    name: str
    description: str
    ability_type: str  # passive, active, ultimate
    cooldown: Optional[int] = None
    unlock_level: int = 1
    icon: Optional[str] = None


@dataclass
class CharacterDialogue:
    """Character dialogue for specific states."""
    
    state: CharacterState
    lines: List[str]
    personality: str = "neutral"


@dataclass
class CharacterQuest:
    """Character-specific quest for progression."""
    
    id: str
    name: str
    description: str
    requirements: Dict[str, any]
    rewards: Dict[str, any]
    completed: bool = False
    completed_at: Optional[str] = None


@dataclass
class CharacterProfile:
    """Complete character profile."""
    
    id: str
    role: CharacterRole
    name: str
    description: str
    default_skin: str
    skins: List[CharacterSkin] = field(default_factory=list)
    abilities: List[CharacterAbility] = field(default_factory=list)
    dialogues: Dict[CharacterState, CharacterDialogue] = field(default_factory=dict)
    quests: List[CharacterQuest] = field(default_factory=list)
    unlocked: bool = True
    unlock_level: int = 1
    is_main_mascot: bool = False


class CharacterSystem:
    """
    Character system for managing Lee-Wuh and future characters.
    
    Supports Lee-Wuh as the main mascot with metadata for
    future council characters, skins, abilities, and quests.
    """
    
    def __init__(self) -> None:
        self._characters: Dict[str, CharacterProfile] = {}
        self._initialize_lee_wuh()
    
    def _initialize_lee_wuh(self) -> None:
        """Initialize Lee-Wuh as the main mascot character."""
        
        # Create default skin
        default_skin = CharacterSkin(
            id="lee_wuh_default",
            name="Classic Lee-Wuh",
            description="The original Lee-Wuh appearance",
            rarity=CharacterRarity.COMMON,
            unlocked=True
        )
        
        # Create additional skins
        overlord_skin = CharacterSkin(
            id="lee_wuh_overlord",
            name="Overlord Mode",
            description="Lee-Wuh in powerful overlord form",
            rarity=CharacterRarity.LEGENDARY,
            unlock_requirements={"level": 10, "quests_completed": 5}
        )
        
        golden_skin = CharacterSkin(
            id="lee_wuh_golden",
            name="Golden Council",
            description="Lee-Wuh with golden council accents",
            rarity=CharacterRarity.EPIC,
            unlock_requirements={"level": 5}
        )
        
        # Create abilities
        guidance_ability = CharacterAbility(
            id="guidance",
            name="Council Guidance",
            description="Provides intelligent guidance and next-best-actions",
            ability_type="passive",
            unlock_level=1
        )
        
        analysis_ability = CharacterAbility(
            id="analysis",
            name="Content Analysis",
            description="Analyzes content for hooks, proof, and opportunities",
            ability_type="active",
            cooldown=60,
            unlock_level=3
        )
        
        # Create dialogues
        idle_dialogue = CharacterDialogue(
            state=CharacterState.IDLE,
            lines=[
                "Drop the source. I'll find the first move.",
                "Welcome back. Let's create something powerful.",
                "Ready to turn your content into impact."
            ]
        )
        
        success_dialogue = CharacterDialogue(
            state=CharacterState.SUCCESS,
            lines=[
                "Excellent work. This one's ready to shine.",
                "Boss-level clip detected. Post this first.",
                "This one builds trust. Save it as proof."
            ]
        )
        
        thinking_dialogue = CharacterDialogue(
            state=CharacterState.THINKING,
            lines=[
                "I'm analyzing your source for breakout moments.",
                "Scanning hooks, proof, silence, and energy.",
                "The council is reviewing your content."
            ]
        )
        
        # Create quests
        first_source_quest = CharacterQuest(
            id="first_source",
            name="First Source",
            description="Upload your first source to LWA",
            requirements={"sources_uploaded": 1},
            rewards={"xp": 100, "unlock": "source_spark"}
        )
        
        first_clip_quest = CharacterQuest(
            id="first_clip",
            name="First Clip",
            description="Generate your first clip",
            requirements={"clips_generated": 1},
            rewards={"xp": 200, "unlock": "clip_blade"}
        )
        
        # Create Lee-Wuh profile
        lee_wuh = CharacterProfile(
            id="lee_wuh",
            role=CharacterRole.LEE_WUH,
            name="Lee-Wuh",
            description="The AI mascot, council leader, and creative guide",
            default_skin="lee_wuh_default",
            skins=[default_skin, overlord_skin, golden_skin],
            abilities=[guidance_ability, analysis_ability],
            dialogues={
                CharacterState.IDLE: idle_dialogue,
                CharacterState.SUCCESS: success_dialogue,
                CharacterState.THINKING: thinking_dialogue,
            },
            quests=[first_source_quest, first_clip_quest],
            unlocked=True,
            unlock_level=1,
            is_main_mascot=True
        )
        
        self._characters["lee_wuh"] = lee_wuh
    
    def get_character(self, character_id: str) -> Optional[CharacterProfile]:
        """Get character profile by ID."""
        return self._characters.get(character_id)
    
    def get_main_mascot(self) -> Optional[CharacterProfile]:
        """Get the main mascot character (Lee-Wuh)."""
        for character in self._characters.values():
            if character.is_main_mascot:
                return character
        return None
    
    def get_character_dialogue(
        self,
        character_id: str,
        state: CharacterState
    ) -> Optional[str]:
        """Get dialogue for character in specific state."""
        character = self.get_character(character_id)
        if not character:
            return None
        
        dialogue = character.dialogues.get(state)
        if not dialogue:
            return None
        
        import random
        return random.choice(dialogue.lines)
    
    def unlock_skin(
        self,
        character_id: str,
        skin_id: str,
        user_level: int,
        user_quests_completed: int
    ) -> bool:
        """
        Attempt to unlock a character skin.
        
        Args:
            character_id: Character ID
            skin_id: Skin ID to unlock
            user_level: User's current level
            user_quests_completed: Number of quests completed
            
        Returns:
            True if unlocked, False otherwise
        """
        character = self.get_character(character_id)
        if not character:
            return False
        
        for skin in character.skins:
            if skin.id == skin_id:
                # Check unlock requirements
                requirements = skin.unlock_requirements
                
                if "level" in requirements and user_level < requirements["level"]:
                    return False
                
                if "quests_completed" in requirements and user_quests_completed < requirements["quests_completed"]:
                    return False
                
                # Unlock skin
                skin.unlocked = True
                logger.info(f"skin_unlocked character={character_id} skin={skin_id}")
                return True
        
        return False
    
    def complete_quest(
        self,
        character_id: str,
        quest_id: str,
        user_progress: Dict[str, any]
    ) -> bool:
        """
        Attempt to complete a character quest.
        
        Args:
            character_id: Character ID
            quest_id: Quest ID to complete
            user_progress: User's current progress
            
        Returns:
            True if completed, False otherwise
        """
        character = self.get_character(character_id)
        if not character:
            return False
        
        for quest in character.quests:
            if quest.id == quest_id:
                # Check requirements
                requirements = quest.requirements
                
                for key, value in requirements.items():
                    if user_progress.get(key, 0) < value:
                        return False
                
                # Complete quest
                quest.completed = True
                logger.info(f"quest_completed character={character_id} quest={quest_id}")
                return True
        
        return False
    
    def get_unlocked_skins(self, character_id: str) -> List[CharacterSkin]:
        """Get all unlocked skins for a character."""
        character = self.get_character(character_id)
        if not character:
            return []
        
        return [skin for skin in character.skins if skin.unlocked]
    
    def get_available_abilities(
        self,
        character_id: str,
        user_level: int
    ) -> List[CharacterAbility]:
        """Get abilities available for user level."""
        character = self.get_character(character_id)
        if not character:
            return []
        
        return [
            ability for ability in character.abilities
            if ability.unlock_level <= user_level
        ]
    
    def add_future_character(
        self,
        character: CharacterProfile
    ) -> None:
        """
        Add a future council character (metadata only).
        
        Args:
            character: Character profile to add
        """
        self._characters[character.id] = character
        logger.info(f"character_added id={character.id} role={character.role}")
    
    def get_all_characters(self) -> List[CharacterProfile]:
        """Get all characters in the system."""
        return list(self._characters.values())
    
    def get_characters_by_role(self, role: CharacterRole) -> List[CharacterProfile]:
        """Get characters by role."""
        return [
            character for character in self._characters.values()
            if character.role == role
        ]


# Singleton instance
character_system = CharacterSystem()
