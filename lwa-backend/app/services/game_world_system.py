"""
Game World System v0

Turns creator work into progression through realms, quests, XP,
and unlockable rewards. Game layer supports business goals without distraction.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class RealmType(str, Enum):
    """Types of creator realms."""
    
    REALM_OF_SOURCES = "realm_of_sources"
    CLIP_FORGE = "clip_forge"
    PROOF_VAULT = "proof_vault"
    CAMPAIGN_TEMPLE = "campaign_temple"
    RENDER_FORGE = "render_forge"
    TIMELINE_TEMPLE = "timeline_temple"
    OFFER_MARKET = "offer_market"
    COUNCIL_CHAMBER = "council_chamber"
    LEE_WUH_THRONE_ROOM = "lee_wuh_throne_room"


class XPType(str, Enum):
    """Types of experience points."""
    
    CREATOR_XP = "creator_xp"
    TRUST_XP = "trust_xp"
    SALES_XP = "sales_xp"
    PROOF_XP = "proof_xp"
    QUEST_XP = "quest_xp"


class UnlockableType(str, Enum):
    """Types of unlockable rewards."""
    
    REALM_KEY = "realm_key"
    CHARACTER_SKIN = "character_skin"
    ABILITY_UNLOCK = "ability_unlock"
    CREATOR_TITLE = "creator_title"
    BADGE = "badge"
    EMOTE = "emote"
    EFFECT = "effect"


@dataclass
class CreatorRealm:
    """Creator realm with progression requirements."""
    
    realm_type: RealmType
    name: str
    description: str
    required_level: int
    required_quests: List[str] = field(default_factory=list)
    required_xp: Dict[XPType, int] = field(default_factory=dict)
    unlocked: bool = False
    unlocked_at: Optional[str] = None
    rewards: List[str] = field(default_factory=list)


@dataclass
class CreatorQuest:
    """Creator quest for progression."""
    
    id: str
    name: str
    description: str
    realm_type: RealmType
    requirements: Dict[str, int] = field(default_factory=dict)
    rewards: Dict[str, any] = field(default_factory=dict)
    difficulty: str = "medium"  # easy, medium, hard, legendary
    completed: bool = False
    completed_at: Optional[str] = None
    repeatable: bool = False


@dataclass
class CreatorXP:
    """Creator experience points."""
    
    creator_id: str
    xp_totals: Dict[XPType, int] = field(default_factory=dict)
    level: int = 1
    total_xp: int = 0
    next_level_xp: int = 100
    achievements: List[str] = field(default_factory=list)
    titles: List[str] = field(default_factory=list)


@dataclass
class Unlockable:
    """Unlockable reward."""
    
    id: str
    name: str
    description: str
    unlock_type: UnlockableType
    requirements: Dict[str, any] = field(default_factory=dict)
    unlocked: bool = False
    unlocked_at: Optional[str] = None
    rarity: str = "common"  # common, rare, epic, legendary


@dataclass
class GameProgress:
    """Complete game progress for a creator."""
    
    creator_id: str
    xp: CreatorXP
    unlocked_realms: List[RealmType] = field(default_factory=list)
    completed_quests: List[str] = field(default_factory=list)
    unlocked_items: List[str] = field(default_factory=list)
    current_realm: Optional[RealmType] = None
    achievements: List[str] = field(default_factory=list)


class GameWorldSystem:
    """
    Game world system for turning creator work into progression.
    
    Supports business goals without distracting from the core tool.
    """
    
    def __init__(self) -> None:
        self._realms: Dict[RealmType, CreatorRealm] = {}
        self._quests: Dict[str, CreatorQuest] = {}
        self._unlockables: Dict[str, Unlockable] = {}
        self._initialize_realms()
        self._initialize_quests()
        self._initialize_unlockables()
    
    def award_xp(
        self,
        creator_id: str,
        xp_type: XPType,
        amount: int,
        reason: str = ""
    ) -> CreatorXP:
        """
        Award experience points to creator.
        
        Args:
            creator_id: Creator ID
            xp_type: Type of XP to award
            amount: Amount of XP to award
            reason: Reason for awarding XP
            
        Returns:
            Updated CreatorXP
        """
        # In production, this would load from database
        xp = self._get_creator_xp(creator_id)
        
        # Add XP
        xp.xp_totals[xp_type] = xp.xp_totals.get(xp_type, 0) + amount
        xp.total_xp += amount
        
        # Check for level up
        while xp.total_xp >= xp.next_level_xp:
            xp.level += 1
            xp.next_level_xp = self._calculate_next_level_xp(xp.level)
            logger.info(f"creator_level_up creator_id={creator_id} new_level={xp.level}")
        
        # Check for realm unlocks
        self._check_realm_unlocks(creator_id, xp)
        
        logger.info(f"xp_awarded creator_id={creator_id} type={xp_type} amount={amount} reason={reason}")
        
        return xp
    
    def complete_quest(
        self,
        creator_id: str,
        quest_id: str,
        progress: Dict[str, int]
    ) -> bool:
        """
        Complete a creator quest.
        
        Args:
            creator_id: Creator ID
            quest_id: Quest ID to complete
            progress: Current progress data
            
        Returns:
            True if quest completed, False otherwise
        """
        quest = self._quests.get(quest_id)
        if not quest:
            return False
        
        # Check requirements
        for requirement, needed in quest.requirements.items():
            if progress.get(requirement, 0) < needed:
                return False
        
        # Complete quest
        quest.completed = True
        quest.completed_at = self._get_current_timestamp()
        
        # Award rewards
        self._award_quest_rewards(creator_id, quest)
        
        logger.info(f"quest_completed creator_id={creator_id} quest_id={quest_id}")
        
        return True
    
    def unlock_realm(
        self,
        creator_id: str,
        realm_type: RealmType
    ) -> bool:
        """
        Unlock a creator realm.
        
        Args:
            creator_id: Creator ID
            realm_type: Realm type to unlock
            
        Returns:
            True if realm unlocked, False otherwise
        """
        realm = self._realms.get(realm_type)
        if not realm or realm.unlocked:
            return False
        
        xp = self._get_creator_xp(creator_id)
        
        # Check requirements
        if xp.level < realm.required_level:
            return False
        
        for xp_type, required in realm.required_xp.items():
            if xp.xp_totals.get(xp_type, 0) < required:
                return False
        
        # Check quest requirements
        for quest_id in realm.required_quests:
            quest = self._quests.get(quest_id)
            if not quest or not quest.completed:
                return False
        
        # Unlock realm
        realm.unlocked = True
        realm.unlocked_at = self._get_current_timestamp()
        
        logger.info(f"realm_unlocked creator_id={creator_id} realm={realm_type}")
        
        return True
    
    def get_creator_progress(self, creator_id: str) -> GameProgress:
        """
        Get complete game progress for creator.
        
        Args:
            creator_id: Creator ID
            
        Returns:
            Complete GameProgress
        """
        xp = self._get_creator_xp(creator_id)
        
        unlocked_realms = [
            realm_type for realm_type, realm in self._realms.items()
            if realm.unlocked
        ]
        
        completed_quests = [
            quest_id for quest_id, quest in self._quests.items()
            if quest.completed
        ]
        
        unlocked_items = [
            item_id for item_id, item in self._unlockables.items()
            if item.unlocked
        ]
        
        return GameProgress(
            creator_id=creator_id,
            xp=xp,
            unlocked_realms=unlocked_realms,
            completed_quests=completed_quests,
            unlocked_items=unlocked_items,
            current_realm=self._get_current_realm(creator_id),
            achievements=xp.achievements
        )
    
    def get_available_quests(
        self,
        creator_id: str,
        realm_type: Optional[RealmType] = None
    ) -> List[CreatorQuest]:
        """
        Get available quests for creator.
        
        Args:
            creator_id: Creator ID
            realm_type: Optional realm filter
            
        Returns:
            List of available quests
        """
        xp = self._get_creator_xp(creator_id)
        available_quests = []
        
        for quest_id, quest in self._quests.items():
            if quest.completed:
                continue
            
            if realm_type and quest.realm_type != realm_type:
                continue
            
            # Check if quest is available based on level
            if self._is_quest_available(quest, xp):
                available_quests.append(quest)
        
        return available_quests
    
    def get_realm_recommendations(self, creator_id: str) -> List[str]:
        """
        Get recommendations for next realms to unlock.
        
        Args:
            creator_id: Creator ID
            
        Returns:
            List of realm recommendations
        """
        xp = self._get_creator_xp(creator_id)
        recommendations = []
        
        for realm_type, realm in self._realms.items():
            if realm.unlocked:
                continue
            
            # Check if close to unlocking
            if xp.level >= realm.required_level - 2:
                recommendations.append(f"Almost ready for {realm.name}!")
            elif self._get_realm_progress(realm, xp) > 0.5:
                recommendations.append(f"You're halfway to {realm.name}")
        
        return recommendations
    
    def _get_creator_xp(self, creator_id: str) -> CreatorXP:
        """Get or create creator XP."""
        # In production, this would load from database
        return CreatorXP(
            creator_id=creator_id,
            xp_totals={},
            level=1,
            total_xp=0,
            next_level_xp=100
        )
    
    def _calculate_next_level_xp(self, level: int) -> int:
        """Calculate XP needed for next level."""
        return int(100 * (1.5 ** (level - 1)))
    
    def _check_realm_unlocks(self, creator_id: str, xp: CreatorXP) -> None:
        """Check for realm unlocks based on XP."""
        for realm_type, realm in self._realms.items():
            if not realm.unlocked:
                self.unlock_realm(creator_id, realm_type)
    
    def _award_quest_rewards(self, creator_id: str, quest: CreatorQuest) -> None:
        """Award rewards for completing quest."""
        for reward_type, reward_value in quest.rewards.items():
            if reward_type == "xp":
                self.award_xp(creator_id, XPType.QUEST_XP, reward_value, f"Quest: {quest.name}")
            elif reward_type == "unlock":
                # Handle unlock rewards
                pass
    
    def _is_quest_available(self, quest: CreatorQuest, xp: CreatorXP) -> bool:
        """Check if quest is available based on creator level."""
        # Simple level-based availability
        level_requirements = {
            "easy": 1,
            "medium": 3,
            "hard": 5,
            "legendary": 10
        }
        
        required_level = level_requirements.get(quest.difficulty, 1)
        return xp.level >= required_level
    
    def _get_current_realm(self, creator_id: str) -> Optional[RealmType]:
        """Get creator's current active realm."""
        # In production, this would be stored in database
        return RealmType.REALM_OF_SOURCES
    
    def _get_realm_progress(self, realm: CreatorRealm, xp: CreatorXP) -> float:
        """Calculate progress percentage for realm unlock."""
        progress = 0.0
        
        # Level progress (40% weight)
        level_progress = min(1.0, xp.level / realm.required_level)
        progress += level_progress * 0.4
        
        # XP progress (30% weight)
        xp_progress = 0.0
        total_required_xp = sum(realm.required_xp.values())
        if total_required_xp > 0:
            total_current_xp = sum(xp.xp_totals.get(xp_type, 0) for xp_type in realm.required_xp)
            xp_progress = min(1.0, total_current_xp / total_required_xp)
        progress += xp_progress * 0.3
        
        # Quest progress (30% weight)
        quest_progress = 0.0
        if realm.required_quests:
            completed_quests = sum(1 for quest_id in realm.required_quests if self._quests.get(quest_id, {}).completed)
            quest_progress = completed_quests / len(realm.required_quests)
        progress += quest_progress * 0.3
        
        return progress
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _initialize_realms(self) -> None:
        """Initialize creator realms."""
        
        # Realm of Sources
        realm_of_sources = CreatorRealm(
            realm_type=RealmType.REALM_OF_SOURCES,
            name="Realm of Sources",
            description="Where all creative journeys begin",
            required_level=1,
            required_xp={XPType.CREATOR_XP: 100},
            rewards=["Source Spark", "Source Master Badge"]
        )
        
        # Clip Forge
        clip_forge = CreatorRealm(
            realm_type=RealmType.CLIP_FORGE,
            name="Clip Forge",
            description="Forge powerful clips from raw sources",
            required_level=3,
            required_xp={XPType.CREATOR_XP: 500, XPType.TRUST_XP: 100},
            required_quests=["first_clip"],
            rewards=["Clip Blade", "Clip Master Title"]
        )
        
        # Proof Vault
        proof_vault = CreatorRealm(
            realm_type=RealmType.PROOF_VAULT,
            name="Proof Vault",
            description="Store and showcase your proof assets",
            required_level=5,
            required_xp={XPType.PROOF_XP: 200},
            required_quests=["save_first_proof"],
            rewards=["Proof Sigil", "Proof Guardian Title"]
        )
        
        # Campaign Temple
        campaign_temple = CreatorRealm(
            realm_type=RealmType.CAMPAIGN_TEMPLE,
            name="Campaign Temple",
            description="Create and manage powerful campaigns",
            required_level=7,
            required_xp={XPType.SALES_XP: 300, XPType.CREATOR_XP: 1000},
            required_quests=["first_campaign"],
            rewards=["Campaign Forge", "Campaign Strategist Title"]
        )
        
        # Council Chamber
        council_chamber = CreatorRealm(
            realm_type=RealmType.COUNCIL_CHAMBER,
            name="Council Chamber",
            description="Meet with Lee-Wuh and the council",
            required_level=10,
            required_xp={XPType.CREATOR_XP: 2000, XPType.TRUST_XP: 500},
            required_quests=["council_summon"],
            rewards=["Council Access", "Council Member Title"]
        )
        
        # Lee-Wuh Throne Room
        lee_wuh_throne = CreatorRealm(
            realm_type=RealmType.LEE_WUH_THRONE_ROOM,
            name="Lee-Wuh Throne Room",
            description="The ultimate creator command center",
            required_level=15,
            required_xp={XPType.CREATOR_XP: 5000, XPType.TRUST_XP: 1000, XPType.SALES_XP: 500},
            required_quests=["master_creator"],
            rewards=["Throne Access", "Master Creator Title", "Lee-Wuh's Blessing"]
        )
        
        self._realms = {
            RealmType.REALM_OF_SOURCES: realm_of_sources,
            RealmType.CLIP_FORGE: clip_forge,
            RealmType.PROOF_VAULT: proof_vault,
            RealmType.CAMPAIGN_TEMPLE: campaign_temple,
            RealmType.COUNCIL_CHAMBER: council_chamber,
            RealmType.LEE_WUH_THRONE_ROOM: lee_wuh_throne
        }
    
    def _initialize_quests(self) -> None:
        """Initialize creator quests."""
        
        # First Source
        first_source = CreatorQuest(
            id="first_source",
            name="First Source",
            description="Upload your first source to begin your journey",
            realm_type=RealmType.REALM_OF_SOURCES,
            requirements={"sources_uploaded": 1},
            rewards={"xp": 100, "unlock": "source_spark"},
            difficulty="easy"
        )
        
        # First Clip
        first_clip = CreatorQuest(
            id="first_clip",
            name="First Clip",
            description="Generate your first viral clip",
            realm_type=RealmType.CLIP_FORGE,
            requirements={"clips_generated": 1},
            rewards={"xp": 200, "unlock": "clip_blade"},
            difficulty="easy"
        )
        
        # Save First Proof
        save_first_proof = CreatorQuest(
            id="save_first_proof",
            name="Save First Proof",
            description="Save your first proof asset",
            realm_type=RealmType.PROOF_VAULT,
            requirements={"proof_assets_saved": 1},
            rewards={"xp": 150, "unlock": "proof_sigil"},
            difficulty="easy"
        )
        
        # First Campaign
        first_campaign = CreatorQuest(
            id="first_campaign",
            name="First Campaign",
            description="Create your first multi-platform campaign",
            realm_type=RealmType.CAMPAIGN_TEMPLE,
            requirements={"campaigns_created": 1},
            rewards={"xp": 300, "unlock": "campaign_forge"},
            difficulty="medium"
        )
        
        # Council Summon
        council_summon = CreatorQuest(
            id="council_summon",
            name="Council Summon",
            description="Earn the council's attention and guidance",
            realm_type=RealmType.COUNCIL_CHAMBER,
            requirements={"level": 10, "trust_xp": 500},
            rewards={"xp": 500, "unlock": "council_access"},
            difficulty="hard"
        )
        
        self._quests = {
            "first_source": first_source,
            "first_clip": first_clip,
            "save_first_proof": save_first_proof,
            "first_campaign": first_campaign,
            "council_summon": council_summon
        }
    
    def _initialize_unlockables(self) -> None:
        """Initialize unlockable rewards."""
        
        # Source Spark
        source_spark = Unlockable(
            id="source_spark",
            name="Source Spark",
            description="A glowing spark that represents your first source",
            unlock_type=UnlockableType.BADGE,
            requirements={"quest": "first_source"},
            rarity="common"
        )
        
        # Clip Blade
        clip_blade = Unlockable(
            id="clip_blade",
            name="Clip Blade",
            description="A sharp blade for cutting viral clips",
            unlock_type=UnlockableType.ABILITY_UNLOCK,
            requirements={"quest": "first_clip"},
            rarity="common"
        )
        
        # Proof Sigil
        proof_sigil = Unlockable(
            id="proof_sigil",
            name="Proof Sigil",
            description="A mystical sigil representing proof assets",
            unlock_type=UnlockableType.BADGE,
            requirements={"quest": "save_first_proof"},
            rarity="rare"
        )
        
        self._unlockables = {
            "source_spark": source_spark,
            "clip_blade": clip_blade,
            "proof_sigil": proof_sigil
        }


# Singleton instance
game_world_system = GameWorldSystem()
