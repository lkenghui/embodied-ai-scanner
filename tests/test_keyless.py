import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class KeylessScannerTests(unittest.TestCase):
    def setUp(self):
        os.environ.pop("OPENAI_API_KEY", None)
        self.tmp = tempfile.TemporaryDirectory()

        for name in list(sys.modules):
            if name == "config" or name.startswith("backend"):
                sys.modules.pop(name, None)

        config = importlib.import_module("config")
        config.DATABASE_PATH = str(Path(self.tmp.name) / "scanner.db")

        self.api = importlib.import_module("backend.api")
        self.client = TestClient(self.api.app)

    def tearDown(self):
        try:
            self.api.scheduler.shutdown(wait=False)
        except Exception:
            pass
        self.tmp.cleanup()

    def test_homepage_loads_without_key(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"AI Scanner", response.content)

    def test_scan_action_reports_missing_key(self):
        response = self.client.post("/api/scan")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "missing_openai_api_key")
        self.assertIn("OPENAI_API_KEY", payload["message"])

    def test_scan_status_is_available_without_key(self):
        response = self.client.get("/api/scan/status")
        self.assertEqual(response.status_code, 200)
        self.assertIn("running", response.json())


if __name__ == "__main__":
    unittest.main()
