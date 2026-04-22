import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class TestVisualGenerationCompatibility(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())
        self.headers = {"x-lwa-client-id": "visual-compat-test"}

    def tearDown(self):
        self.client.close()

    def test_visual_generation_health(self):
        response = self.client.get("/v1/visual-generation/health", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get("ok"), True)
        self.assertEqual(body.get("provider"), "lwa")
        self.assertEqual(body.get("service"), "visual_generation")

    def test_visual_generation_idea_requires_prompt(self):
        response = self.client.post(
            "/v1/visual-generation/generate",
            headers=self.headers,
            json={"mode": "idea"},
        )
        self.assertEqual(response.status_code, 400)

    def test_visual_generation_idea_succeeds_with_prompt(self):
        response = self.client.post(
            "/v1/visual-generation/generate",
            headers=self.headers,
            json={
                "mode": "idea",
                "prompt": "Create a premium short-form visual concept for a creator brand",
                "provider": "lwa",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body.get("provider"), "lwa")
        self.assertEqual(body.get("mode"), "idea")
        self.assertIn("asset", body)

    def test_visual_generation_image_requires_source_or_prompt(self):
        response = self.client.post(
            "/v1/visual-generation/generate",
            headers=self.headers,
            json={"mode": "image"},
        )
        self.assertEqual(response.status_code, 400)

    def test_multimodal_video_stays_on_clipping_path(self):
        response = self.client.post(
            "/v1/generation/multimodal",
            headers=self.headers,
            json={"mode": "video", "provider": "lwa"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("clipping route", response.json().get("detail", "").lower())

    def test_multimodal_idea_works(self):
        response = self.client.post(
            "/v1/generation/multimodal",
            headers=self.headers,
            json={
                "mode": "idea",
                "prompt": "Build a social-ready visual direction from this concept",
                "provider": "lwa",
            },
        )
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(
            body.get("provider") == "lwa"
            or body.get("asset", {}).get("provider") == "lwa"
            or body.get("status") is not None
        )


if __name__ == "__main__":
    unittest.main()
