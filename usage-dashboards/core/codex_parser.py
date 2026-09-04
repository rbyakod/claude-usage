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


def _usage_from(data: dict[str, Any]) -> dict[str, Any]:
    usage = data.get("usage")
    if isinstance(usage, dict):
        return usage
    return data


def _extract_usage(data: dict[str, Any], path: Path, line_number: int) -> UsageRecord | None:
    usage = _usage_from(data)
    has_tokens = any(
        key in usage
        for key in ("input_tokens", "cached_input_tokens", "cache_read_input_tokens", "output_tokens", "reasoning_tokens")
    )
    if not has_tokens:
        return None
    session_id = str(data.get("session_id") or data.get("sessionId") or path.stem)
    turn_id = str(data.get("turn_id") or data.get("uuid") or data.get("id") or f"{path.stem}:{line_number}")
    return UsageRecord(
        provider="codex",
        session_id=session_id,
        turn_id=turn_id,
        model=str(data.get("model") or usage.get("model") or "unknown"),
        timestamp=str(data.get("timestamp") or ""),
        input_tokens=_as_int(usage.get("input_tokens")),
        output_tokens=_as_int(usage.get("output_tokens")),
        cache_creation_tokens=_as_int(usage.get("cache_creation_tokens") or usage.get("cache_creation_input_tokens")),
        cache_read_tokens=_as_int(usage.get("cached_input_tokens") or usage.get("cache_read_input_tokens")),
        reasoning_tokens=_as_int(usage.get("reasoning_tokens")),
        project=str(data.get("cwd") or data.get("project") or ""),
        source_path=str(path),
    )


def _extract_command(data: dict[str, Any], path: Path, line_number: int) -> CommandRecord | None:
    command = data.get("command") or data.get("cmd")
    tool = data.get("tool") if isinstance(data.get("tool"), dict) else {}
    command = command or tool.get("command")
    if not command:
        return None
    session_id = str(data.get("session_id") or data.get("sessionId") or path.stem)
    turn_id = str(data.get("turn_id") or data.get("uuid") or data.get("id") or f"{path.stem}:{line_number}")
    return CommandRecord(
        provider="codex",
        session_id=session_id,
        turn_id=turn_id,
        command=str(command),
        output=str(data.get("output") or data.get("content") or ""),
        status=str(data.get("status") or "unknown"),
        timestamp=str(data.get("timestamp") or ""),
    )


def parse_codex_jsonl(path: Path) -> tuple[list[UsageRecord], list[CommandRecord]]:
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
