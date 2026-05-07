"""Registry for local-safe LWA platform engines.

The dedicated Railway engine services select one of these engines with
LWA_ENGINE_SERVICE_ID. These engines are service-ready scaffolds, not claims of
production completion.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .base import EngineCapability, EngineDemoResult, EngineStatus, LwaEngine


class CreatorEngine(LwaEngine):
    engine_id = "creator"
    name = "Creator Engine"
    description = "Hooks, captions, clip-package planning, and creator workflow previews."
    status = EngineStatus.LOCAL_READY

    def capabilities(self):
        return [
            EngineCapability("hook_package", "Hook Package", "Creates local-safe hook/caption package previews."),
            EngineCapability("creator_plan", "Creator Plan", "Plans the next creator action without rendering externally."),
        ]

    def next_required_integrations(self):
        return ["clip job persistence", "render handoff", "proof event write", "export bundle audit"]


class BrainEngine(LwaEngine):
    engine_id = "brain"
    name = "LWA Brain Engine"
    description = "Provider-gated intelligence routing, style strategy, and decision recommendations."
    status = EngineStatus.LOCAL_READY

    def capabilities(self):
        return [
            EngineCapability("decision_route", "Decision Route", "Returns deterministic recommendations without paid providers."),
            EngineCapability("style_strategy", "Style Strategy", "Maps goals to suggested output style."),
        ]

    def next_required_integrations(self):
        return ["provider registry", "cost governance", "style memory persistence", "decision audit log"]


class RenderEngine(LwaEngine):
    engine_id = "render"
    name = "Render Engine"
    description = "Render planning, asset handoff, and queue boundary previews."
    status = EngineStatus.SCAFFOLDED

    def health_warnings(self):
        return ["Paid render providers and queues are disabled in demo mode."]

    def capabilities(self):
        return [
            EngineCapability("render_plan", "Render Plan", "Plans render work without creating a paid render job."),
            EngineCapability("asset_handoff", "Asset Handoff", "Describes required asset layers and fallbacks."),
        ]

    def next_required_integrations(self):
        return ["render queue", "asset CDN", "provider gateway", "cost guard", "job persistence"]


class MarketplaceEngine(LwaEngine):
    engine_id = "marketplace"
    name = "Marketplace Engine"
    description = "Campaign, opportunity, and creator-marketplace teaser logic."
    status = EngineStatus.SCAFFOLDED

    def health_warnings(self):
        return ["No real campaign claim, brand submission, or contract is created."]

    def next_required_integrations(self):
        return ["campaign database", "brand verification", "creator profiles", "contract workflow", "moderation"]


class WalletEntitlementsEngine(LwaEngine):
    engine_id = "wallet_entitlements"
    name = "Wallet / Entitlements Engine"
    description = "Credits and entitlement previews with no payment or payout execution."
    status = EngineStatus.SCAFFOLDED

    def health_warnings(self):
        return ["Real payments, wallet mutation, and payouts are disabled."]

    def next_required_integrations(self):
        return ["ledger database", "payment provider sandbox", "entitlement policy", "payout compliance", "fraud review"]


class ProofHistoryEngine(LwaEngine):
    engine_id = "proof_history"
    name = "Proof / History Engine"
    description = "Proof record previews, trust trail planning, and audit-safe history scaffolding."
    status = EngineStatus.LOCAL_READY

    def next_required_integrations(self):
        return ["proof database", "event persistence", "audit IDs", "campaign submission linkage"]


class WorldGameEngine(LwaEngine):
    engine_id = "world_game"
    name = "World / Game Engine"
    description = "Lee-Wuh world bridge for missions, XP, relics, and realm progression previews."
    status = EngineStatus.LOCAL_READY

    def next_required_integrations(self):
        return ["game state persistence", "reward ledger", "mission completion events", "anti-spam economy rules"]


class SafetyEngine(LwaEngine):
    engine_id = "safety"
    name = "Safety Engine"
    description = "Local-safe guardrails, claim checks, and external-action blocking."
    status = EngineStatus.LOCAL_READY

    def capabilities(self):
        return [
            EngineCapability("external_action_guard", "External Action Guard", "Confirms public demos do not post, pay, or call providers."),
            EngineCapability("risk_preview", "Risk Preview", "Returns local deterministic risk flags."),
        ]

    def next_required_integrations(self):
        return ["policy database", "fraud models", "rights classifier", "human review queue"]


class SocialDistributionEngine(LwaEngine):
    engine_id = "social_distribution"
    name = "Social Distribution Engine"
    description = "Social package previews without OAuth posting or external API calls."
    status = EngineStatus.SCAFFOLDED

    def health_warnings(self):
        return ["No OAuth posting or external social API call is executed."]

    def next_required_integrations(self):
        return ["platform OAuth", "posting APIs", "approval workflow", "rate limits", "analytics ingestion"]


class OperatorAdminEngine(LwaEngine):
    engine_id = "operator_admin"
    name = "Operator / Admin Engine"
    description = "Read-only readiness, service health, and operational snapshot engine."
    status = EngineStatus.LOCAL_READY

    def capabilities(self):
        return [
            EngineCapability("readiness", "Readiness", "Summarizes deployment and engine readiness."),
            EngineCapability("service_snapshot", "Service Snapshot", "Returns safe operational service metadata."),
        ]

    def next_required_integrations(self):
        return ["admin auth", "metrics store", "alerting", "moderation queue"]


_ENGINE_INSTANCES: Dict[str, LwaEngine] = {
    "creator": CreatorEngine(),
    "brain": BrainEngine(),
    "render": RenderEngine(),
    "marketplace": MarketplaceEngine(),
    "wallet_entitlements": WalletEntitlementsEngine(),
    "proof_history": ProofHistoryEngine(),
    "world_game": WorldGameEngine(),
    "safety": SafetyEngine(),
    "social_distribution": SocialDistributionEngine(),
    "operator_admin": OperatorAdminEngine(),
}


def engine_ids() -> list[str]:
    return list(_ENGINE_INSTANCES.keys())


def get_engine(engine_id: str) -> Optional[LwaEngine]:
    return _ENGINE_INSTANCES.get(engine_id)


def get_engine_registry() -> Dict[str, Dict[str, Any]]:
    return {engine_id: engine.metadata() for engine_id, engine in _ENGINE_INSTANCES.items()}


def get_engine_health() -> Dict[str, Dict[str, Any]]:
    return {engine_id: engine.health().to_dict() for engine_id, engine in _ENGINE_INSTANCES.items()}


def run_engine_demo(engine_id: str, payload: Optional[Mapping[str, Any]] = None) -> EngineDemoResult:
    engine = get_engine(engine_id)
    if engine is None:
        raise KeyError(f"Unknown LWA engine: {engine_id}")
    return engine.demo_run(payload)
