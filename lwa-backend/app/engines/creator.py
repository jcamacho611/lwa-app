from __future__ import annotations

from typing import Any

from .base import BackendEngine, capability, build_demo_result


def _demo(payload: dict[str, Any]) -> dict[str, Any]:
    source = str(payload.get("source") or payload.get("source_url") or payload.get("title") or "demo source")
    return build_demo_result(
        summary="Creator engine reads the source and primes the first mission.",
        output={
            "source": source,
            "mission": "First Signal",
            "next_best_action": "Generate first clip pack",
            "signals": ["hook_first_3s", "standalone_coherence", "curiosity_gap"],
            "strategy_only_supported": True,
        },
        warnings=["No paid provider calls executed."],
    )


ENGINE = BackendEngine(
    engine_id="creator",
    name="Creator Engine",
    status="local_ready",
    capabilities_list=(
        capability("source_ingest", "Source ingest", "Normalize creator source inputs into a demo-ready packet."),
        capability("mission_seed", "Mission seed", "Pick the first creator mission from source context."),
        capability("clip_rank_preview", "Rank preview", "Preview retention-first ranking signals locally."),
    ),
    next_required_integrations_list=("source ingest service", "mission persistence", "clip export adapter"),
    demo_summary="Creator engine routes a source into the first mission.",
    demo_runner=_demo,
)

engine_id = ENGINE.engine_id
name = ENGINE.name
status = ENGINE.status
health = ENGINE.health
capabilities = ENGINE.capabilities
demo_run = ENGINE.demo_run
next_required_integrations = ENGINE.next_required_integrations
