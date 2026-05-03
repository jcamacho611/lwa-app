"""
Safety Rights Cost Engine v0

Provides safety checks, rights warnings, and cost estimation
for all generation paths before processing.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("uvicorn.error")


class SafetyLevel(str, Enum):
    """Safety classification levels."""
    
    SAFE = "safe"
    WARNING = "warning"
    RISK = "risk"
    BLOCKED = "blocked"


class RiskType(str, Enum):
    """Types of content risks."""
    
    COPYRIGHT = "copyright"
    LIKENESS = "likeness"
    CELEBRITY = "celebrity"
    BRAND_IMPERSONATION = "brand_impersonation"
    HARMFUL = "harmful"
    MISINFORMATION = "misinformation"
    COST = "cost"


@dataclass
class SafetyCheck:
    """Result of a safety check."""
    
    risk_type: RiskType
    level: SafetyLevel
    message: str
    requires_confirmation: bool = False
    blocked: bool = False


@dataclass
class RightsWarning:
    """Rights-related warning."""
    
    warning_type: str
    message: str
    severity: str  # low, medium, high
    requires_action: bool = False


@dataclass
class CostEstimate:
    """Cost estimation for generation."""
    
    estimated_cost: float
    currency: str = "USD"
    budget_limit: Optional[float] = None
    exceeds_budget: bool = False
    cost_breakdown: Dict[str, float] = field(default_factory=dict)


@dataclass
class SafetyAssessment:
    """Complete safety assessment."""
    
    safety_level: SafetyLevel
    safety_checks: List[SafetyCheck] = field(default_factory=list)
    rights_warnings: List[RightsWarning] = field(default_factory=list)
    cost_estimate: Optional[CostEstimate] = None
    overall_safe: bool = True
    requires_user_confirmation: bool = False


class SafetyEngine:
    """
    Safety, rights, and cost assessment engine.
    
    Ensures all generations include safety checks, rights warnings,
    and cost estimates before processing.
    """
    
    def __init__(self) -> None:
        self._risky_terms = self._build_risky_terms()
        self._celebrity_names = self._build_celebrity_names()
        self._brand_names = self._build_brand_names()
    
    def assess_generation(
        self,
        prompt: str,
        source_url: Optional[str] = None,
        budget_limit: Optional[float] = None,
        provider: str = "mock"
    ) -> SafetyAssessment:
        """
        Assess generation request for safety, rights, and cost.
        
        Args:
            prompt: Generation prompt
            source_url: Optional source URL
            budget_limit: Optional budget limit
            provider: AI provider being used
            
        Returns:
            Complete safety assessment
        """
        safety_checks = []
        rights_warnings = []
        
        # Safety checks
        safety_checks.extend(self._check_prompt_safety(prompt))
        safety_checks.extend(self._check_source_rights(source_url))
        
        # Rights warnings
        rights_warnings.extend(self._check_music_rights(prompt))
        rights_warnings.extend(self._check_likeness_rights(prompt))
        
        # Cost estimation
        cost_estimate = self._estimate_cost(prompt, provider, budget_limit)
        
        # Determine overall safety level
        safety_level = self._determine_safety_level(safety_checks, rights_warnings, cost_estimate)
        
        overall_safe = safety_level != SafetyLevel.BLOCKED
        requires_confirmation = any(check.requires_confirmation for check in safety_checks)
        
        return SafetyAssessment(
            safety_level=safety_level,
            safety_checks=safety_checks,
            rights_warnings=rights_warnings,
            cost_estimate=cost_estimate,
            overall_safe=overall_safe,
            requires_user_confirmation=requires_confirmation
        )
    
    def _check_prompt_safety(self, prompt: str) -> List[SafetyCheck]:
        """Check prompt for safety issues."""
        checks = []
        prompt_lower = prompt.lower()
        
        # Check for risky terms
        for term in self._risky_terms:
            if term in prompt_lower:
                checks.append(SafetyCheck(
                    risk_type=RiskType.HARMFUL,
                    level=SafetyLevel.WARNING,
                    message=f"Potentially risky term detected: {term}",
                    requires_confirmation=True
                ))
        
        # Check for guaranteed claims
        if "guaranteed" in prompt_lower or "risk free" in prompt_lower:
            checks.append(SafetyCheck(
                risk_type=RiskType.MISINFORMATION,
                level=SafetyLevel.WARNING,
                message="Avoid guaranteed claims in content",
                requires_confirmation=True
            ))
        
        return checks
    
    def _check_source_rights(self, source_url: Optional[str]) -> List[SafetyCheck]:
        """Check source URL for rights issues."""
        checks = []
        
        if not source_url:
            return checks
        
        url_lower = source_url.lower()
        
        # Check for private/restricted content
        if "private" in url_lower or "restricted" in url_lower:
            checks.append(SafetyCheck(
                risk_type=RiskType.COPYRIGHT,
                level=SafetyLevel.RISK,
                message="Source appears to be private or restricted content",
                requires_confirmation=True,
                blocked=True
            ))
        
        # Check for known problematic platforms
        if "facebook.com/private" in url_lower or "instagram.com/private" in url_lower:
            checks.append(SafetyCheck(
                risk_type=RiskType.COPYRIGHT,
                level=SafetyLevel.WARNING,
                message="Private social media content may not be accessible",
                requires_confirmation=True
            ))
        
        return checks
    
    def _check_music_rights(self, prompt: str) -> List[RightsWarning]:
        """Check for music rights issues."""
        warnings = []
        prompt_lower = prompt.lower()
        
        if "music" in prompt_lower or "song" in prompt_lower:
            warnings.append(RightsWarning(
                warning_type="music",
                message="Music may require licensing for commercial use",
                severity="medium",
                requires_action=True
            ))
        
        return warnings
    
    def _check_likeness_rights(self, prompt: str) -> List[RightsWarning]:
        """Check for likeness rights issues."""
        warnings = []
        prompt_lower = prompt.lower()
        
        # Check for celebrity names
        for celebrity in self._celebrity_names:
            if celebrity in prompt_lower:
                warnings.append(RightsWarning(
                    warning_type="likeness",
                    message=f"Potential celebrity likeness: {celebrity}",
                    severity="high",
                    requires_action=True
                ))
        
        # Check for brand names
        for brand in self._brand_names:
            if brand in prompt_lower:
                warnings.append(RightsWarning(
                    warning_type="brand",
                    message=f"Brand reference detected: {brand}",
                    severity="medium",
                    requires_action=True
                ))
        
        return warnings
    
    def _estimate_cost(
        self,
        prompt: str,
        provider: str,
        budget_limit: Optional[float]
    ) -> CostEstimate:
        """Estimate generation cost."""
        
        # Mock cost estimation
        # In production, this would use actual provider pricing
        base_cost = len(prompt) * 0.001
        
        if provider == "openai":
            base_cost *= 2.0
        elif provider == "anthropic":
            base_cost *= 1.5
        
        cost_breakdown = {
            "tokens": len(prompt),
            "base_cost": base_cost,
            "provider_multiplier": 2.0 if provider == "openai" else 1.5
        }
        
        exceeds_budget = budget_limit is not None and base_cost > budget_limit
        
        return CostEstimate(
            estimated_cost=base_cost,
            currency="USD",
            budget_limit=budget_limit,
            exceeds_budget=exceeds_budget,
            cost_breakdown=cost_breakdown
        )
    
    def _determine_safety_level(
        self,
        safety_checks: List[SafetyCheck],
        rights_warnings: List[RightsWarning],
        cost_estimate: Optional[CostEstimate]
    ) -> SafetyLevel:
        """Determine overall safety level."""
        
        # Check for blocked items
        if any(check.blocked for check in safety_checks):
            return SafetyLevel.BLOCKED
        
        # Check for budget exceeded
        if cost_estimate and cost_estimate.exceeds_budget:
            return SafetyLevel.BLOCKED
        
        # Check for high-severity warnings
        high_risks = [check for check in safety_checks if check.level == SafetyLevel.RISK]
        if high_risks:
            return SafetyLevel.RISK
        
        # Check for warnings
        if safety_checks or rights_warnings:
            return SafetyLevel.WARNING
        
        return SafetyLevel.SAFE
    
    def _build_risky_terms(self) -> List[str]:
        """Build list of risky terms to flag."""
        return [
            "guaranteed",
            "risk free",
            "passive income",
            "investment advice",
            "financial advice",
        ]
    
    def _build_celebrity_names(self) -> List[str]:
        """Build list of celebrity names to flag."""
        return [
            "elon musk",
            "kanye west",
            "taylor swift",
            "justin bieber",
        ]
    
    def _build_brand_names(self) -> List[str]:
        """Build list of brand names to flag."""
        return [
            "apple",
            "google",
            "microsoft",
            "amazon",
            "meta",
        ]


# Singleton instance
safety_engine = SafetyEngine()
