class WorldsError(Exception):
    """Base error for LWA Worlds."""


class NotFoundError(WorldsError):
    """Resource not found."""


class ValidationError(WorldsError):
    """User input or state transition is invalid."""


class ForbiddenTransitionError(WorldsError):
    """Status transition is not allowed."""


class RightsConfirmationRequired(WorldsError):
    """Submission requires content rights confirmation."""


class PayoutBlockedError(WorldsError):
    """Payout is blocked by review, dispute, hold, or policy."""
