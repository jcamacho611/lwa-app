from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent
WEB_ROOT = REPO_ROOT / "lwa-web"
BACKEND_SCRIPT = BACKEND_ROOT / "scripts" / "engine_demo.py"
CONTRACT_LINT_SCRIPT = BACKEND_ROOT / "scripts" / "lint_engine_contract.py"
SMOKE_SCRIPT = REPO_ROOT / "scripts" / "smoke_engines.sh"
DEV_LAUNCHER = REPO_ROOT / "scripts" / "dev.sh"
MAKEFILE = REPO_ROOT / "Makefile"
ARCHITECTURE_DOC = REPO_ROOT / "docs" / "architecture" / "LWA_ENGINE_ARCHITECTURE.md"
ENGINE_ROOM_PAGE = WEB_ROOT / "app" / "engines" / "page.tsx"
DEMO_LOOP_PANEL = WEB_ROOT / "components" / "demo" / "LwaPublicDemoLoopPanel.tsx"
DEPLOY_ORDER_LIB = WEB_ROOT / "lib" / "lwa-engine-deploy-order.ts"
OPERATOR_SNAPSHOT = WEB_ROOT / "components" / "engines" / "OperatorSnapshot.tsx"
ENGINE_HEALTH_BADGE = WEB_ROOT / "components" / "engines" / "EngineHealthBadge.tsx"
ENGINE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "lwa-engine-tests.yml"
ENGINE_ISSUE_TEMPLATE = REPO_ROOT / ".github" / "ISSUE_TEMPLATE" / "engine-slice.yml"


class EngineSurfaceToolingTests(unittest.TestCase):
    def test_engine_demo_cli_lists_expected_engines(self) -> None:
        result = subprocess.run(
            [sys.executable, str(BACKEND_SCRIPT), "--list"],
            cwd=BACKEND_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("10 engines", result.stdout)
        self.assertIn("creator", result.stdout)
        self.assertIn("wallet_entitlements", result.stdout)
        self.assertIn("operator_admin", result.stdout)

    def test_engine_demo_cli_returns_json_payload_for_creator(self) -> None:
        payload = "{\"source\":\"demo source\",\"title\":\"Demo upload\"}"
        result = subprocess.run(
            [sys.executable, str(BACKEND_SCRIPT), "creator", payload],
            cwd=BACKEND_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        data = json.loads(result.stdout)
        self.assertEqual(data["engine_id"], "creator")
        self.assertTrue(data["summary"])
        self.assertIn("output", data)
        self.assertIn("warnings", data)
        self.assertIn("next_required_integrations", data)

    def test_smoke_script_has_expected_engine_ids_and_shell_syntax(self) -> None:
        syntax = subprocess.run(
            ["bash", "-n", str(SMOKE_SCRIPT)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(syntax.returncode, 0, msg=syntax.stderr)

        text = SMOKE_SCRIPT.read_text(encoding="utf-8")
        for engine_id in (
            "creator",
            "brain",
            "render",
            "marketplace",
            "wallet_entitlements",
            "proof_history",
            "world_game",
            "safety",
            "social_distribution",
            "operator_admin",
        ):
            self.assertIn(engine_id, text)

        self.assertIn('curl -fsS "$API_BASE/engines"', text)
        self.assertIn('POST /engines/$id/demo', text)

    def test_contract_lint_script_executes_cleanly(self) -> None:
        syntax = subprocess.run(
            [sys.executable, "-m", "py_compile", str(CONTRACT_LINT_SCRIPT)],
            cwd=BACKEND_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(syntax.returncode, 0, msg=syntax.stderr)

        result = subprocess.run(
            [sys.executable, str(CONTRACT_LINT_SCRIPT)],
            cwd=BACKEND_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Linting", result.stdout)
        self.assertIn("OK:", result.stdout)

    def test_engine_room_page_wires_backend_truth_surface(self) -> None:
        text = ENGINE_ROOM_PAGE.read_text(encoding="utf-8")
        self.assertIn("BackendEngineRoomPanel", text)
        self.assertIn("EngineHealthBadge", text)
        self.assertIn("OperatorSnapshot", text)
        self.assertIn("LWA_ENGINE_STAGE_BINDINGS", text)
        self.assertIn("getDeployOrder", text)
        self.assertIn("/engines/${binding.engineId}", text)
        self.assertIn("Railway services are deployable boxes", text)

    def test_public_demo_loop_panel_keeps_demo_loop_connections_visible(self) -> None:
        text = DEMO_LOOP_PANEL.read_text(encoding="utf-8")
        self.assertIn("getBlockingDemoChecks", text)
        self.assertIn("getDemoNarrativeForPersona", text)
        self.assertIn("getNextPublicDemoStage", text)
        self.assertIn("getPublicDemoStageById", text)
        self.assertIn("getEngineForStage", text)
        self.assertIn("Signal Sprint", text)
        self.assertIn("Open engine proof", text)
        self.assertIn("Next stage", text)
        self.assertIn("Reset demo", text)

    def test_deploy_order_data_keeps_risky_engines_out_of_demo(self) -> None:
        text = DEPLOY_ORDER_LIB.read_text(encoding="utf-8")
        self.assertIn('engineId: "operator_admin"', text)
        self.assertIn('engineId: "wallet_entitlements"', text)
        self.assertIn('engineId: "marketplace"', text)
        self.assertIn('engineId: "social_distribution"', text)
        self.assertIn('safeForDemo: false', text)
        self.assertIn('safeForDemo: true', text)

    def test_operator_snapshot_surface_remains_read_only(self) -> None:
        text = OPERATOR_SNAPSHOT.read_text(encoding="utf-8")
        self.assertIn("POST /engines/operator_admin/demo", text)
        self.assertIn("No payments, no posting, no paid providers", text)
        self.assertIn("recommended next action", text)
        self.assertIn("read-only roll-up", text)
        self.assertIn("runBackendEngineDemo", text)
        self.assertIn("operator_admin", text)
        self.assertIn("Refresh", text)

    def test_engine_health_badge_surface_hits_health_only(self) -> None:
        text = ENGINE_HEALTH_BADGE.read_text(encoding="utf-8")
        self.assertIn("/engines/health", text)
        self.assertIn("backend not configured", text)
        self.assertIn("healthy_count", text)
        self.assertIn("no_backend", text)
        self.assertNotIn("/engines/", text.split("/engines/health", 1)[0])

    def test_makefile_keeps_engine_and_validation_targets_visible(self) -> None:
        text = MAKEFILE.read_text(encoding="utf-8")
        self.assertIn("smoke-engines", text)
        self.assertIn("engine-cli", text)
        self.assertIn("engine-service", text)
        self.assertIn("backend-compile", text)
        self.assertIn("backend-test", text)
        self.assertIn("web-typecheck", text)
        self.assertIn("web-build", text)
        self.assertIn("web-lint", text)

    def test_engine_workflow_enforces_engine_foundation_and_forbidden_area_guards(self) -> None:
        text = ENGINE_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("LWA Engine Tests", text)
        self.assertIn("test_engine_service_runtime.py", text)
        self.assertIn("test_engine_service_app.py", text)
        self.assertIn("test_engines.py", text)
        self.assertIn("scripts/engine_demo.py", text)
        self.assertIn("scripts/smoke_engines.sh", text)
        self.assertIn("forbidden-areas", text)
        self.assertIn("LwaBrainEnginePanel\\.tsx", text)
        self.assertIn("lwa-backend/app/api/routes/generate\\.py", text)

    def test_dev_launcher_matches_documented_full_dev_flow(self) -> None:
        text = DEV_LAUNCHER.read_text(encoding="utf-8")
        self.assertIn("Launch LWA backend + web in one terminal", text)
        self.assertIn("uvicorn app.main:app", text)
        self.assertIn("npm run dev", text)
        self.assertIn("BACKEND_PORT", text)
        self.assertIn("WEB_PORT", text)
        self.assertIn("cleanup()", text)
        syntax = subprocess.run(
            ["bash", "-n", str(DEV_LAUNCHER)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(syntax.returncode, 0, msg=syntax.stderr)

    def test_engine_issue_template_keeps_issue_scope_structured(self) -> None:
        text = ENGINE_ISSUE_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("Engine slice", text)
        self.assertIn("Summary", text)
        self.assertIn("File paths / scope", text)
        self.assertIn("Verification", text)
        self.assertIn("Safety notes", text)

    def test_engine_architecture_doc_covers_all_layers(self) -> None:
        text = ARCHITECTURE_DOC.read_text(encoding="utf-8")
        self.assertIn("LWA Engine Architecture", text)
        self.assertIn("UNIFIED API", text)
        self.assertIn("BACKEND ENGINES", text)
        self.assertIn("PER-ENGINE RAILWAY SERVICES", text)
        self.assertIn("backend-engines-api", text.lower())
        self.assertIn("LWA_ENGINE_SERVICE_ID".lower(), text.lower())
        self.assertIn("make engine-service", text)
        self.assertIn("make smoke-engines", text)


if __name__ == "__main__":
    unittest.main()
