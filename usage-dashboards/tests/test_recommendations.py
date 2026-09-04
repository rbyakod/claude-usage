from __future__ import annotations

import unittest

from core.models import CommandRecord, UsageRecord
from core.recommendations import recommendations_for


THRESHOLDS = {
    "warn_output_lines": 3,
    "warn_estimated_command_tokens": 10,
    "warn_full_test_repeats": 2,
    "warn_glm_repair_cycles": 3,
}


class RecommendationTests(unittest.TestCase):
    def test_warns_for_verbose_xcode_output_and_high_estimated_tokens(self) -> None:
        recs = recommendations_for(
            [
                CommandRecord(
                    "anthropic",
                    "s",
                    "t",
                    "xcodebuild test -scheme MyApp",
                    "line\n" * 20,
                )
            ],
            [],
            THRESHOLDS,
        )
        titles = {rec.title for rec in recs}
        self.assertIn("Verbose Xcode output", titles)
        self.assertIn("High estimated command tokens", titles)

    def test_warns_for_repeated_full_tests_and_broad_paths(self) -> None:
        commands = [
            CommandRecord("anthropic", "s", "t1", "xcodebuild test -scheme MyApp", ""),
            CommandRecord("anthropic", "s", "t2", "xcodebuild test -scheme MyApp", ""),
            CommandRecord("anthropic", "s", "t3", "xcodebuild test -scheme MyApp", ""),
            CommandRecord("anthropic", "s", "t4", "cat MyApp.xcodeproj/project.pbxproj", ""),
        ]
        titles = {rec.title for rec in recommendations_for(commands, [], THRESHOLDS)}
        self.assertIn("Repeated full Xcode tests", titles)
        self.assertIn("Broad Xcode project exploration", titles)

    def test_warns_for_glm_repair_cycles(self) -> None:
        commands = [
            CommandRecord("zai", "s", "t1", "fix failing test", ""),
            CommandRecord("zai", "s", "t2", "repair compile error", ""),
            CommandRecord("zai", "s", "t3", "fix warning", ""),
        ]
        usage = [UsageRecord("zai", "s", "t1", "glm-5.3", "")]
        titles = {rec.title for rec in recommendations_for(commands, usage, THRESHOLDS)}
        self.assertIn("GLM repair loop", titles)


if __name__ == "__main__":
    unittest.main()
