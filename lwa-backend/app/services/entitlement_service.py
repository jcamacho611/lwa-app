"""Entitlement and credit management service for LWA.

Manages user credits, feature unlocks, and pay-per-use tracking
without relying on external subscription providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from uuid import uuid4


@dataclass
class UserEntitlement:
    user_id: str
    credits_remaining: int = 0
    total_credits_ever: int = 0
    free_mode_used: bool = False
    unlocked_features: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


@dataclass
class CreditTransaction:
    id: str
    user_id: str
    amount: int
    transaction_type: str  # "grant", "spend", "refund"
    feature: str
    description: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


# In-memory store (replace with database in production)
_USER_ENTITLEMENTS: dict[str, UserEntitlement] = {}
_CREDIT_TRANSACTIONS: list[CreditTransaction] = []

# Feature costs
FEATURE_COSTS = {
    "clip_generation": 1,
    "campaign_export": 2,
    "proof_vault_save": 0,
    "style_feedback": 0,
    "director_brain_score": 0,
    "video_render": 3,
    "caption_export": 1,
    "bulk_operation": 5,
}

FREE_LAUNCH_MODE = True  # Enable free mode for launch period


def get_or_create_entitlement(user_id: str) -> UserEntitlement:
    """Get existing entitlement or create new one with starter credits."""
    if user_id not in _USER_ENTITLEMENTS:
        # New user gets starter credits
        _USER_ENTITLEMENTS[user_id] = UserEntitlement(
            user_id=user_id,
            credits_remaining=10 if FREE_LAUNCH_MODE else 3,  # Generous free launch
            total_credits_ever=10 if FREE_LAUNCH_MODE else 3,
            unlocked_features=["clip_generation", "proof_vault_save", "style_feedback", "director_brain_score"],
        )
    return _USER_ENTITLEMENTS[user_id]


def check_entitlement(user_id: str, feature: str) -> dict:
    """Check if user has entitlement for a feature."""
    entitlement = get_or_create_entitlement(user_id)
    cost = FEATURE_COSTS.get(feature, 1)
    
    has_credits = entitlement.credits_remaining >= cost
    is_unlocked = feature in entitlement.unlocked_features or FREE_LAUNCH_MODE
    
    return {
        "success": True,
        "user_id": user_id,
        "feature": feature,
        "cost": cost,
        "has_access": has_credits and is_unlocked,
        "credits_required": cost,
        "credits_available": entitlement.credits_remaining,
        "credits_after": entitlement.credits_remaining - cost if has_credits else 0,
        "unlocked": is_unlocked,
        "free_mode_active": FREE_LAUNCH_MODE,
        "message": (
            "Access granted" if has_credits and is_unlocked
            else "Insufficient credits" if not has_credits
            else "Feature locked"
        ),
    }


def spend_credit(user_id: str, feature: str, description: str = "") -> dict:
    """Spend credit for a feature use."""
    entitlement = get_or_create_entitlement(user_id)
    cost = FEATURE_COSTS.get(feature, 1)
    
    if entitlement.credits_remaining < cost and not FREE_LAUNCH_MODE:
        return {
            "success": False,
            "user_id": user_id,
            "feature": feature,
            "cost": cost,
            "credits_available": entitlement.credits_remaining,
            "message": "Insufficient credits",
        }
    
    # Deduct credits (or simulate in free mode)
    if not FREE_LAUNCH_MODE:
        entitlement.credits_remaining -= cost
        entitlement.updated_at = datetime.utcnow().isoformat() + "Z"
    
    # Record transaction
    transaction = CreditTransaction(
        id=f"txn_{uuid4().hex[:16]}",
        user_id=user_id,
        amount=-cost,
        transaction_type="spend",
        feature=feature,
        description=description or f"Used {feature}",
    )
    _CREDIT_TRANSACTIONS.append(transaction)
    
    return {
        "success": True,
        "user_id": user_id,
        "feature": feature,
        "cost": cost,
        "credits_remaining": entitlement.credits_remaining,
        "credits_spent": cost,
        "free_mode": FREE_LAUNCH_MODE,
        "transaction_id": transaction.id,
        "message": "Credit spent successfully" if not FREE_LAUNCH_MODE else "Free mode - no charge",
    }


def grant_credits(user_id: str, amount: int, reason: str = "") -> dict:
    """Grant credits to a user (e.g., purchase, reward, promo)."""
    entitlement = get_or_create_entitlement(user_id)
    
    entitlement.credits_remaining += amount
    entitlement.total_credits_ever += amount
    entitlement.updated_at = datetime.utcnow().isoformat() + "Z"
    
    # Record transaction
    transaction = CreditTransaction(
        id=f"txn_{uuid4().hex[:16]}",
        user_id=user_id,
        amount=amount,
        transaction_type="grant",
        feature="credit_grant",
        description=reason or "Credits granted",
    )
    _CREDIT_TRANSACTIONS.append(transaction)
    
    return {
        "success": True,
        "user_id": user_id,
        "credits_granted": amount,
        "credits_total": entitlement.credits_remaining,
        "transaction_id": transaction.id,
        "message": f"Granted {amount} credits",
    }


def unlock_feature(user_id: str, feature: str, permanent: bool = False) -> dict:
    """Unlock a feature for a user."""
    entitlement = get_or_create_entitlement(user_id)
    
    if feature not in entitlement.unlocked_features:
        entitlement.unlocked_features.append(feature)
        entitlement.updated_at = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": True,
        "user_id": user_id,
        "feature": feature,
        "unlocked_features": entitlement.unlocked_features,
        "permanent": permanent,
        "message": f"Feature '{feature}' unlocked",
    }


def get_user_entitlement_status(user_id: str) -> dict:
    """Get full entitlement status for a user."""
    entitlement = get_or_create_entitlement(user_id)
    
    # Get recent transactions
    user_transactions = [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.transaction_type,
            "feature": t.feature,
            "description": t.description,
            "created_at": t.created_at,
        }
        for t in _CREDIT_TRANSACTIONS[-20:]  # Last 20
        if t.user_id == user_id
    ]
    
    return {
        "success": True,
        "user_id": user_id,
        "credits": {
            "remaining": entitlement.credits_remaining,
            "total_ever": entitlement.total_credits_ever,
        },
        "unlocked_features": entitlement.unlocked_features,
        "free_mode_active": FREE_LAUNCH_MODE,
        "feature_costs": FEATURE_COSTS,
        "recent_transactions": user_transactions,
    }


def get_entitlement_summary() -> dict:
    """Get system-wide entitlement summary (admin)."""
    total_users = len(_USER_ENTITLEMENTS)
    total_credits_in_system = sum(e.credits_remaining for e in _USER_ENTITLEMENTS.values())
    total_transactions = len(_CREDIT_TRANSACTIONS)
    
    return {
        "success": True,
        "total_users": total_users,
        "total_credits_in_system": total_credits_in_system,
        "total_transactions": total_transactions,
        "free_mode_active": FREE_LAUNCH_MODE,
        "feature_costs": FEATURE_COSTS,
    }
