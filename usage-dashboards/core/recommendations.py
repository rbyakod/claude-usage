from __future__ import annotations

from collections import Counter
from typing import Any

from .attribution import classify_command, estimate_output_tokens
from .models import CommandRecord, Recommendation, UsageRecord


def recommendations_for(
    commands: list[CommandRecord],
    usage: list[UsageRecord],
    thresholds: dict[str, int],
) -> list[Recommendation]:
    rows: list[Recommendation] = []
    warn_lines = thresholds.get("warn_output_lines", 300)
    warn_tokens = thresholds.get("warn_estimated_command_tokens", 5000)
    warn_full_tests = thresholds.get("warn_full_test_repeats", 2)
    warn_glm_repairs = thresholds.get("warn_glm_repair_cycles", 3)

    full_tests = 0
    repair_turns = 0
    broad_paths = ("project.pbxproj", "DerivedData", ".build", "SourcePackages")

    for command in commands:
        family = classify_command(command.command)
        output_lines = len(command.output.splitlines())
        estimated_tokens = estimate_output_tokens(command.output)
        if family == "xcodebuild" and output_lines > warn_lines:
            rows.append(
                Recommendation(
                    "warning",
                    "Verbose Xcode output",
                    "Use compact wrappers and targeted diagnostics instead of returning full build logs.",
                    command.command[:120],
                )
            )
        if family == "xcodebuild" and " test" in f" {command.command} " and "-only-testing" not in command.command:
            full_tests += 1
        if estimated_tokens > warn_tokens:
            rows.append(
                Recommendation(
                    "warning",
                    "High estimated command tokens",
                    f"Command output is estimated at {estimated_tokens} context tokens.",
                    command.command[:120],
                )
            )
        if any(path in command.command or path in command.output for path in broad_paths):
            rows.append(
                Recommendation(
                    "warning",
                    "Broad Xcode project exploration",
                    "Avoid project files, build artifacts, and generated dependency folders unless the task needs them.",
                    command.command[:120],
                )
            )
        if "repair" in command.command.lower() or "fix" in command.command.lower():
            repair_turns += 1

    if full_tests > warn_full_tests:
        rows.append(
            Recommendation(
                "warning",
                "Repeated full Xcode tests",
                "Run targeted tests during implementation and reserve full suite runs for checkpoints.",
                "xcodebuild test",
            )
        )

    glm_turns = sum(1 for record in usage if record.model.startswith("glm-"))
    if glm_turns and repair_turns >= warn_glm_repairs:
        rows.append(
            Recommendation(
                "warning",
                "GLM repair loop",
                "After repeated repair turns, escalate model choice or narrow the prompt.",
                "glm repair cycles",
            )
        )

    duplicate_titles = Counter(row.title for row in rows)
    if duplicate_titles:
        return _dedupe(rows)
    return rows


def _dedupe(rows: list[Recommendation]) -> list[Recommendation]:
    seen: set[tuple[str, str]] = set()
    deduped: list[Recommendation] = []
    for row in rows:
        key = (row.title, row.source)
        if key not in seen:
            deduped.append(row)
            seen.add(key)
    return deduped
