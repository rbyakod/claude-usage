from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.db import connect, insert_command, insert_usage, migrate, summary
from core.models import CommandRecord, UsageRecord


class DatabaseTests(unittest.TestCase):
    def test_insert_usage_and_command_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "usage.sqlite3")
            migrate(conn)
            insert_usage(
                conn,
                UsageRecord(
                    provider="zai",
                    session_id="s1",
                    turn_id="t1",
                    model="glm-5.3",
                    timestamp="2026-09-03T12:00:00Z",
                    input_tokens=100,
                    output_tokens=25,
                    cache_read_tokens=300,
                    project="Fixture",
                    source_path="fixture.jsonl",
                ),
            )
            insert_command(
                conn,
                CommandRecord(
                    provider="zai",
                    session_id="s1",
                    turn_id="t1",
                    command="xcodebuild test -scheme Fixture",
                    output="line one\nline two",
                    status="failed",
                    timestamp="2026-09-03T12:01:00Z",
                ),
            )

            data = summary(conn, "zai")

        self.assertEqual(data["totals"]["total_tokens"], 425)
        self.assertEqual(data["models"][0]["model"], "glm-5.3")
        self.assertEqual(data["commands"][0]["output_lines"], 2)


if __name__ == "__main__":
    unittest.main()
