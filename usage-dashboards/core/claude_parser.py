from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import CommandRecord, UsageRecord


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _provider_for(model: str, data: dict[str, Any]) -> str:
    if model.startswith("glm-"):
        return "zai"
    base_url = str(data.get("anthropic_base_url") or data.get("base_url") or "")
    if "z.ai" in base_url:
        return "zai"
    return "anthropic"


def _extract_usage(data: dict[str, Any], path: Path, line_number: int) -> UsageRecord | None:
    message = data.get("message") if isinstance(data.get("message"), dict) else {}
    usage = message.get("usage") or data.get("usage") or {}
    if not isinstance(usage, dict) or not usage:
        return None

    model = str(data.get("model") or message.get("model") or "unknown")
    provider = _provider_for(model, data)
    session_id = str(data.get("session_id") or data.get("sessionId") or path.stem)
    turn_id = str(data.get("uuid") or data.get("turn_id") or data.get("id") or f"{path.stem}:{line_number}")
    return UsageRecord(
        provider=provider,
        session_id=session_id,
        turn_id=turn_id,
        model=model,
        timestamp=str(data.get("timestamp") or ""),
        input_tokens=_as_int(usage.get("input_tokens")),
        output_tokens=_as_int(usage.get("output_tokens")),
        cache_creation_tokens=_as_int(
            usage.get("cache_creation_input_tokens") or usage.get("cache_creation_tokens")
        ),
        cache_read_tokens=_as_int(usage.get("cache_read_input_tokens") or usage.get("cache_read_tokens")),
        reasoning_tokens=_as_int(usage.get("reasoning_tokens")),
        project=str(data.get("project") or ""),
        source_path=str(path),
    )


def _extract_command(data: dict[str, Any], path: Path, line_number: int) -> CommandRecord | None:
    tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
    command = data.get("command") or data.get("cmd") or tool_input.get("command")
    if not command:
        return None

    output = data.get("output") or data.get("content") or data.get("result") or ""
    model = str(data.get("model") or "")
    provider = _provider_for(model, data) if model else "anthropic"
    session_id = str(data.get("session_id") or data.get("sessionId") or path.stem)
    turn_id = str(data.get("uuid") or data.get("turn_id") or data.get("id") or f"{path.stem}:{line_number}")
    return CommandRecord(
        provider=provider,
        session_id=session_id,
        turn_id=turn_id,
        command=str(command),
        output=str(output),
        status=str(data.get("status") or "unknown"),
        timestamp=str(data.get("timestamp") or ""),
    )


def parse_claude_jsonl(path: Path) -> tuple[list[UsageRecord], list[CommandRecord]]:
    usage_records: list[UsageRecord] = []
    command_records: list[CommandRecord] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(data, dict):
                continue
            usage = _extract_usage(data, path, line_number)
            if usage:
                usage_records.append(usage)
            command = _extract_command(data, path, line_number)
            if command:
                command_records.append(command)
    return usage_records, command_records
