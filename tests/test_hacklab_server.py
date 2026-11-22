"""Part 2: the diagram web server (no Docker needed).

We feed it a fake state provider and check that it serves the page, returns
state as JSON, and pushes a Server-Sent Event when the state changes.
"""

import json
import os
import sys
import time
import unittest
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from terminal_academy.hacklab.diagram_server import DiagramServer  # noqa: E402


class DiagramServerTest(unittest.TestCase):
    def setUp(self):
        self.state = {"diagram": "filesystem", "tick": 0}
        self.server = DiagramServer(lambda: dict(self.state))
        self.server.start()
        self.base = self.server.url

    def tearDown(self):
        self.server.stop()

    def _get(self, path, timeout=5):
        with urllib.request.urlopen(self.base.rstrip("/") + path, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8")

    def test_serves_html_page(self):
        status, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("<html", body.lower())
        self.assertIn("EventSource", body)  # the page subscribes to /events

    def test_state_endpoint_returns_json(self):
        # Give the poller a moment to take its first snapshot.
        for _ in range(50):
            status, body = self._get("/state")
            if body.strip() not in ("", "{}"):
                break
            time.sleep(0.05)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)["diagram"], "filesystem")

    def test_sse_pushes_an_update(self):
        req = urllib.request.urlopen(self.base.rstrip("/") + "/events", timeout=5)
        try:
            # Read the first pushed event.
            first = self._read_one_event(req)
            self.assertIn("filesystem", first)
            # Change the state; the poller should push the new value.
            self.state["tick"] = 42
            pushed = ""
            deadline = time.time() + 5
            while time.time() < deadline:
                pushed = self._read_one_event(req)
                if '"tick": 42' in pushed or '"tick":42' in pushed:
                    break
            self.assertIn("42", pushed)
        finally:
            req.close()

    @staticmethod
    def _read_one_event(resp):
        """Read lines until we have a full SSE 'data:' line."""
        for _ in range(100):
            raw = resp.readline()
            if not raw:
                return ""
            line = raw.decode("utf-8").strip()
            if line.startswith("data:"):
                return line[len("data:"):].strip()
        return ""


if __name__ == "__main__":
    unittest.main()
