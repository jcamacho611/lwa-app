#!/usr/bin/env python3
"""Run a single LWA engine demo locally — no server required.

Usage:
    python scripts/engine_demo.py <engine_id> [json_payload]
    python scripts/engine_demo.py creator '{"source":"demo source"}'
    python scripts/engine_demo.py --list

Exits 0 on success, 1 on unknown engine, 2 on bad JSON, 3 on demo error.
No network calls, no payouts, no external posting, no paid providers.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Allow running from lwa-backend/ or from repo root.
HERE = Path(__file__).resolve().parent
BACKEND_ROOT = HERE.parent  # lwa-backend/
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.engines.registry import (  # noqa: E402  (sys.path setup above)
    ENGINE_REGISTRY,
    get_engine,
    get_engine_health,
    get_engine_registry,
    run_engine_demo,
)


def known_ids() -> list[str]:
    return [engine.engine_id for engine in ENGINE_REGISTRY]


def cmd_list() -> int:
    registry = get_engine_registry()
    health = get_engine_health()
    print(f"{registry['count']} engines · {health['healthy_count']} healthy")
    print("-" * 56)
    for engine_id in known_ids():
        record = registry["engines"][engine_id]
        h = record["health"]
        flag = "✓" if h["healthy"] else "·"
        print(f"  {flag} {engine_id:22s} {record['status']}")
    return 0


def cmd_run(engine_id: str, payload_str: str) -> int:
    if engine_id not in known_ids():
        print(f"unknown engine: {engine_id}", file=sys.stderr)
        print(f"known: {', '.join(known_ids())}", file=sys.stderr)
        return 1
    try:
        payload = json.loads(payload_str) if payload_str else {}
    except json.JSONDecodeError as exc:
        print(f"bad JSON payload: {exc}", file=sys.stderr)
        return 2
    try:
        result = run_engine_demo(engine_id, payload)
    except Exception as exc:  # pragma: no cover — defensive
        print(f"engine error: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(result, indent=2))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        print(__doc__)
        return 0
    if argv[1] in {"-l", "--list"}:
        return cmd_list()
    engine_id = argv[1]
    payload_str = argv[2] if len(argv) >= 3 else "{}"
    return cmd_run(engine_id, payload_str)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
