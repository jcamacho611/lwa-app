from __future__ import annotations

from uuid import uuid4

from .ledger import LedgerService
from .models import Badge, LedgerEventType, ReputationEvent, UserBadge, UserWorldProfile
from .repositories import BadgeRepository, ReputationRepository, WorldsStore, WorldProfileRepository


FIRST_CAMPAIGN_BADGE = {
    "public_id": "badge_first_campaign",
    "name": "Campaign Hunter",
    "tier": "rare",
    "description": "Created your first marketplace campaign.",
    "lore": "The market moves for those who can turn signal into demand.",
}

FIRST_APPROVED_SUBMISSION_BADGE = {
    "public_id": "badge_approved_earner",
    "name": "Approved Earner",
    "tier": "epic",
    "description": "Earned approval on marketplace work.",
    "lore": "Creation became value, and the ledger remembered.",
}


class XpService:
    def __init__(self, store: WorldsStore):
        self.profile_repo = WorldProfileRepository(store)
        self.badge_repo = BadgeRepository(store)
        self.rep_repo = ReputationRepository(store)
        self.ledger_service = LedgerService(store)

    def get_or_create_profile(self, user_id: str, display_name: str = "LWA Founder") -> UserWorldProfile:
        existing = self.profile_repo.get_by_user_id(user_id)
        if existing:
            return existing

        return self.profile_repo.create(
            UserWorldProfile(
                user_id=user_id,
                display_name=display_name,
                class_name="Signalwright",
                faction="The Signalwrights",
                level=1,
                xp=0,
                next_level_xp=100,
            )
        )

    def add_xp(
        self,
        *,
        user_id: str,
        xp: int,
        creator_rep: int = 0,
        clipper_rep: int = 0,
        marketplace_rep: int = 0,
        reason: str,
        source_type: str,
        source_public_id: str | None = None,
    ) -> UserWorldProfile:
        profile = self.get_or_create_profile(user_id)
        profile.xp += xp
        profile.creator_reputation += creator_rep
        profile.clipper_reputation += clipper_rep
        profile.marketplace_reputation += marketplace_rep

        while profile.xp >= profile.next_level_xp:
            profile.xp -= profile.next_level_xp
            profile.level += 1
            profile.next_level_xp = max(int(profile.next_level_xp * 1.35), profile.next_level_xp + 1)

        saved = self.profile_repo.save(profile)
        self.rep_repo.create(
            ReputationEvent(
                public_id=f"rep_{uuid4().hex[:12]}",
                user_id=user_id,
                source_type=source_type,
                source_public_id=source_public_id,
                xp=xp,
                creator_reputation=creator_rep,
                clipper_reputation=clipper_rep,
                marketplace_reputation=marketplace_rep,
                reason=reason,
            )
        )
        self.ledger_service.record(
            user_id=user_id,
            event_type=LedgerEventType.xp_awarded,
            label=reason,
            xp=xp,
            reputation=creator_rep + clipper_rep + marketplace_rep,
            reference_id=source_public_id,
        )
        return saved

    def ensure_badge_exists(self, badge_data: dict[str, str]) -> Badge:
        existing = self.badge_repo.get_badge(badge_data["public_id"])
        if existing:
            return existing
        return self.badge_repo.create_badge(
            Badge(
                public_id=badge_data["public_id"],
                name=badge_data["name"],
                tier=badge_data["tier"],
                description=badge_data["description"],
                lore=badge_data["lore"],
            )
        )

    def award_badge_once(self, *, user_id: str, badge_data: dict[str, str]) -> bool:
        badge = self.ensure_badge_exists(badge_data)
        if self.badge_repo.user_has_badge(user_id, badge.public_id):
            return False

        self.badge_repo.award_badge(UserBadge(user_id=user_id, badge_public_id=badge.public_id))
        self.ledger_service.record(
            user_id=user_id,
            event_type=LedgerEventType.badge_awarded,
            label=f"Badge unlocked: {badge.name}",
            reference_id=badge.public_id,
        )
        return True

    def on_campaign_created(self, user_id: str, campaign_public_id: str) -> UserWorldProfile:
        profile = self.add_xp(
            user_id=user_id,
            xp=75,
            creator_rep=5,
            marketplace_rep=5,
            reason="Created marketplace campaign",
            source_type="campaign",
            source_public_id=campaign_public_id,
        )
        self.award_badge_once(user_id=user_id, badge_data=FIRST_CAMPAIGN_BADGE)
        return profile

    def on_submission_approved(self, user_id: str, submission_public_id: str) -> UserWorldProfile:
        profile = self.add_xp(
            user_id=user_id,
            xp=125,
            clipper_rep=10,
            marketplace_rep=10,
            reason="Marketplace submission approved",
            source_type="submission",
            source_public_id=submission_public_id,
        )
        self.award_badge_once(user_id=user_id, badge_data=FIRST_APPROVED_SUBMISSION_BADGE)
        return profile
