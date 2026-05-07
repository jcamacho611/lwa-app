#!/usr/bin/env python3
"""Lint each LWA backend engine module for contract conformance.

Every engine module under app/engines/ (except base.py, registry.py,
and __init__.py) must:

  1. Define a module-level `ENGINE` of type BackendEngine.
  2. Re-export the seven required module-level symbols:
        engine_id, name, status, health, capabilities,
        demo_run, next_required_integrations.
  3. Have a non-empty engine_id and name.
  4. Have a `status` from the EngineStatus literal set.
  5. Be discoverable from app.engines.registry.ENGINE_REGISTRY.

Exits 0 if all checks pass, 1 if any engine module is non-conformant.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND_ROOT = HERE.parent  # lwa-backend/
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.engines.base import BackendEngine, EngineStatus  # noqa: E402

REQUIRED_MODULE_SYMBOLS = (
    "engine_id",
    "name",
    "status",
    "health",
    "capabilities",
    "demo_run",
    "next_required_integrations",
)

VALID_STATUSES = (
    "scaffolded",
    "local_ready",
    "backend_ready",
    "provider_ready",
    "production_ready",
)


def lint_engine_module(module_path: Path) -> list[str]:
    """Return a list of error strings for one engine module. Empty = OK."""
    errors: list[str] = []
    rel = module_path.name
    module_name = f"app.engines.{module_path.stem}"
    try:
        import importlib

        mod = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover — defensive
        errors.append(f"{rel}: import failed: {exc}")
        return errors

    engine = getattr(mod, "ENGINE", None)
    if engine is None:
        errors.append(f"{rel}: missing module-level ENGINE")
    elif not isinstance(engine, BackendEngine):
        errors.append(f"{rel}: ENGINE is not a BackendEngine instance")
    else:
        if not engine.engine_id:
            errors.append(f"{rel}: ENGINE.engine_id is empty")
        if not engine.name:
            errors.append(f"{rel}: ENGINE.name is empty")
        if engine.status not in VALID_STATUSES:
            errors.append(
                f"{rel}: ENGINE.status={engine.status!r} not in {VALID_STATUSES}"
            )

    for sym in REQUIRED_MODULE_SYMBOLS:
        if not hasattr(mod, sym):
            errors.append(f"{rel}: missing module-level re-export `{sym}`")

    return errors


def main() -> int:
    engines_dir = BACKEND_ROOT / "app" / "engines"
    if not engines_dir.is_dir():
        print(f"engines dir not found: {engines_dir}", file=sys.stderr)
        return 1

    skip = {"__init__.py", "base.py", "registry.py"}
    engine_files = sorted(
        p for p in engines_dir.glob("*.py") if p.name not in skip
    )

    if not engine_files:
        print("no engine modules found")
        return 1

    total_errors: list[str] = []
    print(f"Linting {len(engine_files)} engine modules...")
    for path in engine_files:
        errors = lint_engine_module(path)
        if errors:
            for err in errors:
                print(f"  ✗ {err}")
            total_errors.extend(errors)
        else:
            print(f"  ✓ {path.name}")

    # Cross-check with the registry — every linted file must appear in it.
    from app.engines.registry import ENGINE_REGISTRY  # noqa: E402

    registered_ids = {e.engine_id for e in ENGINE_REGISTRY}
    for path in engine_files:
        # Best-effort module load to read engine_id without re-import side effects.
        import importlib

        mod = importlib.import_module(f"app.engines.{path.stem}")
        eid = getattr(mod, "engine_id", None) or getattr(
            getattr(mod, "ENGINE", None), "engine_id", None
        )
        if eid and eid not in registered_ids:
            msg = f"{path.name}: engine_id={eid!r} not present in ENGINE_REGISTRY"
            print(f"  ✗ {msg}")
            total_errors.append(msg)

    print()
    if total_errors:
        print(f"FAIL: {len(total_errors)} contract issue(s) found.")
        return 1
    print(f"OK: {len(engine_files)} engines conform to the contract.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
