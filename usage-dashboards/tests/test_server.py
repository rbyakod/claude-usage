from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.request import urlopen

from app.server import make_server
from core.db import connect, insert_usage, migrate
from core.models import UsageRecord


class ServerTests(unittest.TestCase):
    def test_summary_api_and_provider_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "usage.sqlite3"
            conn = connect(db_path)
            migrate(conn)
            insert_usage(
                conn,
                UsageRecord(
                    provider="codex",
                    session_id="s",
                    turn_id="t",
                    model="gpt-5.6-sol",
                    timestamp="2026-09-03T11:00:00Z",
                    input_tokens=10,
                    output_tokens=5,
                ),
            )
            conn.close()
            server = make_server("127.0.0.1", 0, db_path)
            port = server.server_address[1]
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                summary = json.loads(urlopen(f"http://127.0.0.1:{port}/api/summary?provider=codex", timeout=5).read())
                self.assertEqual(summary["provider"], "codex")
                self.assertEqual(summary["totals"]["total_tokens"], 15)
                for route in ("", "claude", "codex", "zai"):
                    body = urlopen(f"http://127.0.0.1:{port}/{route}", timeout=5).read().decode("utf-8")
                    self.assertIn("Usage Dashboards", body)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
