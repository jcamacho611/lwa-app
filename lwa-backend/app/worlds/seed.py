from __future__ import annotations

from .repositories import WorldsStore
from .xp import FIRST_APPROVED_SUBMISSION_BADGE, FIRST_CAMPAIGN_BADGE, XpService


def seed_worlds_defaults(store: WorldsStore) -> None:
    service = XpService(store)
    service.ensure_badge_exists(FIRST_CAMPAIGN_BADGE)
    service.ensure_badge_exists(FIRST_APPROVED_SUBMISSION_BADGE)
