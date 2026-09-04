from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Iterable

from .claude_parser import parse_claude_jsonl
from .codex_parser import parse_codex_jsonl
from .db import connect, insert_command, insert_usage, migrate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "usage.sqlite3"


def _expand(paths: Iterable[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        matches = [Path(item) for item in glob.glob(str(path), recursive=True)]
        expanded.extend(matches or [path])
    return [path for path in expanded if path.is_file() and path.suffix == ".jsonl"]


def _default_paths(include_claude: bool, include_codex: bool) -> list[Path]:
    home = Path.home()
    paths: list[Path] = []
    if include_claude:
        paths.extend(Path(item) for item in glob.glob(str(home / ".claude" / "projects" / "**" / "*.jsonl"), recursive=True))
    if include_codex:
        paths.extend(Path(item) for item in glob.glob(str(home / ".codex" / "sessions" / "**" / "*.jsonl"), recursive=True))
    return paths


def _detect_kind(path: Path) -> str:
    lowered = str(path).lower()
    if ".codex" in lowered or "codex" in path.name.lower():
        return "codex"
    try:
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                data = json.loads(line)
                usage = data.get("usage") if isinstance(data, dict) else {}
                model = str(data.get("model", ""))
                if isinstance(usage, dict) and ("reasoning_tokens" in usage or model.startswith("gpt-")):
                    return "codex"
                break
    except (OSError, json.JSONDecodeError):
        return "claude"
    return "claude"


def ingest_paths(paths: list[Path], db_path: Path, parser_kind: str = "auto") -> dict[str, int]:
    conn = connect(db_path)
    migrate(conn)
    counts = {
        "files_seen": 0,
        "files_parsed": 0,
        "usage_records": 0,
        "commands": 0,
        "skipped_lines": 0,
    }
    for path in _expand(paths):
        counts["files_seen"] += 1
        kind = parser_kind if parser_kind != "auto" else _detect_kind(path)
        parser = parse_codex_jsonl if kind == "codex" else parse_claude_jsonl
        usage_records, command_records = parser(path)
        if usage_records or command_records:
            counts["files_parsed"] += 1
        for record in usage_records:
            insert_usage(conn, record)
            counts["usage_records"] += 1
        for record in command_records:
            insert_command(conn, record)
            counts["commands"] += 1
    conn.close()
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest local Claude, Codex, and Z.ai usage JSONL files.")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--claude", action="store_true", help="Scan Claude default paths or force Claude parser for explicit paths.")
    parser.add_argument("--codex", action="store_true", help="Scan Codex default paths or force Codex parser for explicit paths.")
    args = parser.parse_args(argv)

    if args.claude and args.codex:
        parser_kind = "auto"
    elif args.claude:
        parser_kind = "claude"
    elif args.codex:
        parser_kind = "codex"
    else:
        parser_kind = "auto"

    paths = args.paths
    if not paths:
        include_claude = args.claude or not args.codex
        include_codex = args.codex or not args.claude
        paths = _default_paths(include_claude, include_codex)

    counts = ingest_paths(paths, args.db, parser_kind)
    print(f"DB: {args.db}")
    for key in ("files_seen", "files_parsed", "usage_records", "commands", "skipped_lines"):
        print(f"{key}: {counts[key]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
