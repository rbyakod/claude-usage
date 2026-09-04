from __future__ import annotations

import unittest
from pathlib import Path

from core.attribution import classify_command
from core.codex_parser import parse_codex_jsonl


FIXTURES = Path(__file__).parent / "fixtures"


class CodexParserTests(unittest.TestCase):
    def test_parses_codex_usage_and_reasoning_tokens(self) -> None:
        usage, commands = parse_codex_jsonl(FIXTURES / "codex_session.jsonl")

        self.assertEqual(len(usage), 1)
        self.assertEqual(usage[0].provider, "codex")
        self.assertEqual(usage[0].model, "gpt-5.6-sol")
        self.assertEqual(usage[0].input_tokens, 8000)
        self.assertEqual(usage[0].cache_read_tokens, 2500)
        self.assertEqual(usage[0].output_tokens, 700)
        self.assertEqual(usage[0].reasoning_tokens, 1800)
        self.assertEqual(len(commands), 1)
        self.assertEqual(classify_command(commands[0].command), "git")

    def test_command_classifier_maps_known_families(self) -> None:
        self.assertEqual(classify_command("xcodebuild test -scheme MyApp"), "xcodebuild")
        self.assertEqual(classify_command("swift test"), "swift")
        self.assertEqual(classify_command("git diff"), "git")
        self.assertEqual(classify_command("rg ViewModel"), "rg")
        self.assertEqual(classify_command("find . -name '*.swift'"), "find")
        self.assertEqual(classify_command("xcrun simctl list"), "simctl")
        self.assertEqual(classify_command("log stream --predicate test"), "log")
        self.assertEqual(classify_command("python3 script.py"), "python")
        self.assertEqual(classify_command("npm test"), "npm")
        self.assertEqual(classify_command("echo hi"), "other")


if __name__ == "__main__":
    unittest.main()
