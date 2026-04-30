from __future__ import annotations

from uuid import uuid4

from .ledger import LedgerService
from .models import LedgerEventType, Relic, UserRelic, UserTitle
from .repositories import RelicRepository, UserTitleRepository, WorldsStore


GOLD_THREAD_RELIC = {
    "public_id": "relic_gold_thread_fragment",
    "name": "Gold Thread Fragment",
    "tier": "epic",
    "description": "Unlocked when creation becomes marketplace value.",
    "lore": "A sliver of proof pulled from the noise between signal and money.",
    "future_collectible_eligible": True,
}


class RelicService:
    def __init__(self, store: WorldsStore):
        self.relic_repo = RelicRepository(store)
        self.title_repo = UserTitleRepository(store)
        self.ledger = LedgerService(store)

    def ensure_relic_exists(self, relic_data: dict) -> Relic:
        existing = self.relic_repo.get_relic(relic_data["public_id"])
        if existing:
            return existing

        return self.relic_repo.create_relic(
            Relic(
                public_id=relic_data["public_id"],
                name=relic_data["name"],
                tier=relic_data["tier"],
                description=relic_data["description"],
                lore=relic_data["lore"],
                future_collectible_eligible=bool(relic_data["future_collectible_eligible"]),
            )
        )

    def award_relic_once(self, *, user_id: str, relic_data: dict) -> bool:
        relic = self.ensure_relic_exists(relic_data)
        if self.relic_repo.user_has_relic(user_id, relic.public_id):
            return False

        self.relic_repo.award_relic(UserRelic(user_id=user_id, relic_public_id=relic.public_id))
        self.ledger.record(
            user_id=user_id,
            event_type=LedgerEventType.collectible_awarded_placeholder,
            label=f"Relic unlocked: {relic.name}",
            reference_id=relic.public_id,
        )
        return True

    def award_title_once(self, *, user_id: str, title: str) -> bool:
        if self.title_repo.user_has_title(user_id, title):
            return False

        self.title_repo.award_title(UserTitle(user_id=user_id, title=title))
        self.ledger.record(
            user_id=user_id,
            event_type=LedgerEventType.reputation_awarded,
            label=f"Title unlocked: {title}",
            reference_id=f"title_{uuid4().hex[:8]}",
        )
        return True

    def list_user_relics(self, user_id: str):
        return self.relic_repo.list_user_relics(user_id)

    def list_user_titles(self, user_id: str) -> list[str]:
        return [item.title for item in self.title_repo.list_titles(user_id)]
