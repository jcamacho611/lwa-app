from __future__ import annotations

from .errors import NotFoundError, ValidationError
from .ledger import LedgerService
from .models import LedgerEventType, Quest, QuestCompletion
from .repositories import QuestRepository, WorldsStore, utcnow
from .xp import XpService


DEFAULT_QUESTS = [
    {
        "public_id": "quest_generate_first_clip",
        "title": "Generate your first clip pack",
        "description": "Use the AI engine to turn one source into short-form assets.",
        "category": "clipping",
        "goal": 1,
        "reward_xp": 50,
    },
    {
        "public_id": "quest_create_first_campaign",
        "title": "Create your first marketplace campaign",
        "description": "Turn a clip pack into a buyer-funded marketplace job.",
        "category": "marketplace",
        "goal": 1,
        "reward_xp": 75,
    },
    {
        "public_id": "quest_submit_first_work",
        "title": "Submit your first campaign clip",
        "description": "Submit work to a campaign and enter review.",
        "category": "marketplace",
        "goal": 1,
        "reward_xp": 100,
    },
    {
        "public_id": "quest_create_first_ugc",
        "title": "Create your first UGC asset",
        "description": "Create a hook pack, quest, caption pack, or campaign template.",
        "category": "ugc",
        "goal": 1,
        "reward_xp": 80,
    },
]


class QuestService:
    def __init__(self, store: WorldsStore):
        self.repo = QuestRepository(store)
        self.xp = XpService(store)
        self.ledger = LedgerService(store)

    def seed_default_quests(self) -> list[Quest]:
        existing_public_ids = {quest.public_id for quest in self.repo.list_active()}
        for quest_data in DEFAULT_QUESTS:
            if quest_data["public_id"] in existing_public_ids:
                continue
            self.repo.create_quest(
                Quest(
                    public_id=quest_data["public_id"],
                    title=quest_data["title"],
                    description=quest_data["description"],
                    category=quest_data["category"],
                    goal=quest_data["goal"],
                    reward_xp=quest_data["reward_xp"],
                    active=True,
                )
            )
        return self.repo.list_active()

    def list_quests(self) -> list[Quest]:
        quests = self.repo.list_active()
        if not quests:
            return self.seed_default_quests()
        return quests

    def progress_quest(self, *, user_id: str, quest_public_id: str, amount: int = 1) -> QuestCompletion:
        quest = self.repo.get_by_public_id(quest_public_id)
        if not quest:
            quest = next((item for item in self.list_quests() if item.public_id == quest_public_id), None)
        if not quest:
            raise NotFoundError("Quest not found")

        completion = self.repo.get_completion(user_id, quest_public_id)
        if not completion:
            completion = QuestCompletion(
                quest_public_id=quest_public_id,
                user_id=user_id,
                progress=0,
                status="in_progress",
            )

        if completion.status in {"completed", "claimed"}:
            return completion

        completion.progress = min(quest.goal, completion.progress + amount)
        if completion.progress >= quest.goal:
            completion.status = "completed"
            completion.completed_at = utcnow()

        return self.repo.save_completion(completion)

    def claim_quest(self, *, user_id: str, quest_public_id: str) -> QuestCompletion:
        quest = self.repo.get_by_public_id(quest_public_id)
        if not quest:
            quest = next((item for item in self.list_quests() if item.public_id == quest_public_id), None)
        if not quest:
            raise NotFoundError("Quest not found")

        completion = self.repo.get_completion(user_id, quest_public_id)
        if not completion:
            raise ValidationError("Quest has not been started")

        if completion.status == "claimed":
            return completion
        if completion.status != "completed":
            raise ValidationError("Quest is not complete")

        completion.status = "claimed"
        completion.claimed_at = utcnow()
        saved = self.repo.save_completion(completion)

        self.xp.add_xp(
            user_id=user_id,
            xp=quest.reward_xp,
            creator_rep=2,
            marketplace_rep=2 if quest.category == "marketplace" else 0,
            reason=f"Quest claimed: {quest.title}",
            source_type="quest",
            source_public_id=quest.public_id,
        )
        self.ledger.record(
            user_id=user_id,
            event_type=LedgerEventType.xp_awarded,
            label=f"Quest reward claimed: {quest.title}",
            xp=quest.reward_xp,
            reference_id=quest.public_id,
        )
        return saved
