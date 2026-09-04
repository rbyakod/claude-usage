from __future__ import annotations

from .models import CommandRecord, UsageRecord


def classify_command(command: str) -> str:
    stripped = command.strip()
    checks = (
        ("xcodebuild", "xcodebuild"),
        ("swift", "swift"),
        ("git", "git"),
        ("rg", "rg"),
        ("find", "find"),
        ("xcrun simctl", "simctl"),
        ("simctl", "simctl"),
        ("log stream", "log"),
        ("npm", "npm"),
        ("python", "python"),
        ("python3", "python"),
    )
    for prefix, family in checks:
        if stripped == prefix or stripped.startswith(prefix + " "):
            return family
    return "other"


def estimate_output_tokens(output: str) -> int:
    return max(1, len(output) // 4) if output else 0


def attribute_commands(commands: list[CommandRecord], usage: UsageRecord) -> list[dict[str, object]]:
    weights = [estimate_output_tokens(command.output) for command in commands]
    total_weight = sum(weights)
    exact_total = (
        usage.input_tokens
        + usage.output_tokens
        + usage.cache_creation_tokens
        + usage.cache_read_tokens
        + usage.reasoning_tokens
    )
    if not commands or total_weight == 0 or exact_total == 0:
        return []

    rows: list[dict[str, object]] = []
    for command, weight in zip(commands, weights, strict=True):
        share = weight / total_weight
        rows.append(
            {
                "command": command.command[:500],
                "family": classify_command(command.command),
                "estimated_total_tokens": int(round(exact_total * share)),
                "label": "estimated",
            }
        )
    return rows
