from __future__ import annotations

import asyncio
import tempfile
import unittest
from starlette.requests import Request

from app.api.routes import generate as generate_routes
from app.services.entitlements import UsageStore


def build_request(client_id: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/v1/generate-analysis",
            "headers": [(b"x-lwa-client-id", client_id.encode("utf-8"))],
            "client": ("127.0.0.1", 8000),
        }
    )


class TextGenerationRoutesTests(unittest.TestCase):
    def test_router_keeps_primary_generate_contract_unique(self) -> None:
        post_generate_routes = [
            route
            for route in generate_routes.router.routes
            if getattr(route, "path", None) == "/generate"
            and "POST" in (getattr(route, "methods", set()) or set())
        ]
        analysis_routes = [
            route
            for route in generate_routes.router.routes
            if getattr(route, "path", None) == "/v1/generate-analysis"
            and "POST" in (getattr(route, "methods", set()) or set())
        ]

        self.assertEqual(len(post_generate_routes), 1)
        self.assertEqual(len(analysis_routes), 1)

    def test_generate_text_uses_current_entitlement_contract(self) -> None:
        with patched_usage_store():
            response = asyncio.run(
                generate_routes.generate_from_text(
                    generate_routes.TextGenerateRequest(
                        text=(
                            "This founder explains the exact moment a creator should stop guessing. "
                            "The strongest clip starts when the tension becomes obvious."
                        ),
                        min_clips=3,
                    ),
                    build_request("text-client"),
                )
            )

        self.assertTrue(response.success)
        self.assertTrue(response.strategy_only)
        self.assertTrue(response.job_id.startswith("text_"))
        self.assertGreaterEqual(len(response.clips), 3)

    def test_generate_analysis_uses_v1_analysis_route(self) -> None:
        with patched_usage_store():
            response = asyncio.run(
                generate_routes.generate_from_analysis(
                    generate_routes.AnalysisGenerateRequest(
                        text=(
                            "Most teams miss the first three seconds. "
                            "The hook has to create tension before the explanation starts."
                        ),
                        min_clips=3,
                        max_clips=4,
                    ),
                    build_request("analysis-client"),
                )
            )

        self.assertTrue(response.success)
        self.assertIn(response.method, {"analysis_engine", "emergency_fallback"})
        self.assertGreaterEqual(len(response.clips), 3)
        self.assertLessEqual(len(response.clips), 4)


class patched_usage_store:
    def __enter__(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._original_store = generate_routes.usage_store
        generate_routes.usage_store = UsageStore(f"{self._temp_dir.name}/usage.json")
        return self

    def __exit__(self, exc_type, exc, tb):
        generate_routes.usage_store = self._original_store
        self._temp_dir.cleanup()
        return False


if __name__ == "__main__":
    unittest.main()
