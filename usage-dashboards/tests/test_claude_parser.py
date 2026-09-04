from __future__ import annotations

import unittest
from pathlib import Path

from core.attribution import classify_command
from core.claude_parser import parse_claude_jsonl


FIXTURES = Path(__file__).parent / "fixtures"


class ClaudeParserTests(unittest.TestCase):
    def test_parses_anthropic_usage_and_xcode_command(self) -> None:
        usage, commands = parse_claude_jsonl(FIXTURES / "claude_session.jsonl")

        self.assertEqual(len(usage), 1)
        self.assertEqual(usage[0].provider, "anthropic")
        self.assertEqual(usage[0].model, "claude-sonnet-4-5")
        self.assertEqual(usage[0].input_tokens, 12000)
        self.assertEqual(usage[0].output_tokens, 900)
        self.assertEqual(usage[0].cache_creation_tokens, 300)
        self.assertEqual(usage[0].cache_read_tokens, 4200)
        self.assertEqual(len(commands), 1)
        self.assertEqual(classify_command(commands[0].command), "xcodebuild")

    def test_preserves_zai_glm_model_ids(self) -> None:
        usage, commands = parse_claude_jsonl(FIXTURES / "zai_session.jsonl")

        self.assertEqual([record.provider for record in usage], ["zai", "zai"])
        self.assertEqual([record.model for record in usage], ["glm-5.3", "glm-5.3-flash"])
        self.assertEqual(commands, [])


if __name__ == "__main__":
    unittest.main()
