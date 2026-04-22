import unittest

from fastapi.testclient import TestClient

from app.main import create_app


class TestVisualGenerationProviderHealth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(create_app())
        self.headers = {"x-lwa-client-id": "provider-health-test"}

    def tearDown(self):
        self.client.close()

    def test_visual_generation_health_endpoint(self):
        response = self.client.get("/v1/visual-generation/health", headers=self.headers)
        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload.get("ok"), True)
        self.assertEqual(payload.get("provider"), "lwa")
        self.assertEqual(payload.get("service"), "visual_generation")


if __name__ == "__main__":
    unittest.main()
