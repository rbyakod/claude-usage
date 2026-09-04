from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Any

from .models import CommandRecord, UsageRecord


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            project TEXT NOT NULL DEFAULT '',
            source_path TEXT NOT NULL DEFAULT '',
            started_at TEXT NOT NULL DEFAULT '',
            ended_at TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS turns (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            prompt_index INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT NOT NULL DEFAULT '',
            text_preview_hash TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'completed',
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            session_id TEXT NOT NULL,
            turn_id TEXT NOT NULL,
            model TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT '',
            input_tokens INTEGER NOT NULL DEFAULT 0,
            output_tokens INTEGER NOT NULL DEFAULT 0,
            cache_creation_tokens INTEGER NOT NULL DEFAULT 0,
            cache_read_tokens INTEGER NOT NULL DEFAULT 0,
            reasoning_tokens INTEGER NOT NULL DEFAULT 0,
            project TEXT NOT NULL DEFAULT '',
            source_path TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(turn_id) REFERENCES turns(id)
        );

        CREATE TABLE IF NOT EXISTS commands (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            session_id TEXT NOT NULL,
            turn_id TEXT NOT NULL,
            command_family TEXT NOT NULL DEFAULT 'other',
            command_preview TEXT NOT NULL,
            output_line_count INTEGER NOT NULL DEFAULT 0,
            output_char_count INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'unknown',
            timestamp TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(session_id) REFERENCES sessions(id),
            FOREIGN KEY(turn_id) REFERENCES turns(id)
        );

        CREATE TABLE IF NOT EXISTS command_attribution (
            id TEXT PRIMARY KEY,
            command_id TEXT NOT NULL,
            usage_record_id TEXT NOT NULL,
            estimated_input_tokens INTEGER NOT NULL DEFAULT 0,
            estimated_output_tokens INTEGER NOT NULL DEFAULT 0,
            estimated_cache_read_tokens INTEGER NOT NULL DEFAULT 0,
            estimated_total_tokens INTEGER NOT NULL DEFAULT 0,
            label TEXT NOT NULL DEFAULT 'estimated',
            FOREIGN KEY(command_id) REFERENCES commands(id),
            FOREIGN KEY(usage_record_id) REFERENCES usage_records(id)
        );

        CREATE TABLE IF NOT EXISTS cost_estimates (
            id TEXT PRIMARY KEY,
            usage_record_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            mode TEXT NOT NULL,
            usd REAL,
            credits REAL,
            confidence TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT '',
            FOREIGN KEY(usage_record_id) REFERENCES usage_records(id)
        );

        CREATE TABLE IF NOT EXISTS rate_cards (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            mode TEXT NOT NULL,
            rate_version TEXT NOT NULL,
            config_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reconciliations (
            id TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            mode TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            official_value TEXT NOT NULL,
            notes TEXT NOT NULL DEFAULT ''
        );
        """
    )
    conn.commit()


def stable_id(*parts: object) -> str:
    raw = "\x1f".join(str(part) for part in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _ensure_session_and_turn(conn: sqlite3.Connection, record: UsageRecord | CommandRecord) -> None:
    session_model = getattr(record, "model", "")
    conn.execute(
        """
        INSERT INTO sessions (id, provider, model, project, source_path, started_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            provider=excluded.provider,
            model=CASE WHEN excluded.model != '' THEN excluded.model ELSE sessions.model END,
            project=CASE WHEN excluded.project != '' THEN excluded.project ELSE sessions.project END,
            source_path=CASE WHEN excluded.source_path != '' THEN excluded.source_path ELSE sessions.source_path END
        """,
        (
            record.session_id,
            record.provider,
            session_model,
            getattr(record, "project", ""),
            getattr(record, "source_path", ""),
            record.timestamp,
        ),
    )
    conn.execute(
        """
        INSERT INTO turns (id, session_id, provider, timestamp)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO NOTHING
        """,
        (record.turn_id, record.session_id, record.provider, record.timestamp),
    )


def insert_usage(conn: sqlite3.Connection, record: UsageRecord) -> None:
    _ensure_session_and_turn(conn, record)
    row_id = stable_id(
        record.provider,
        record.session_id,
        record.turn_id,
        record.model,
        record.timestamp,
        record.source_path,
    )
    conn.execute(
        """
        INSERT INTO usage_records (
            id, provider, session_id, turn_id, model, timestamp, input_tokens,
            output_tokens, cache_creation_tokens, cache_read_tokens,
            reasoning_tokens, project, source_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            input_tokens=excluded.input_tokens,
            output_tokens=excluded.output_tokens,
            cache_creation_tokens=excluded.cache_creation_tokens,
            cache_read_tokens=excluded.cache_read_tokens,
            reasoning_tokens=excluded.reasoning_tokens
        """,
        (
            row_id,
            record.provider,
            record.session_id,
            record.turn_id,
            record.model,
            record.timestamp,
            record.input_tokens,
            record.output_tokens,
            record.cache_creation_tokens,
            record.cache_read_tokens,
            record.reasoning_tokens,
            record.project,
            record.source_path,
        ),
    )
    conn.commit()


def insert_command(conn: sqlite3.Connection, record: CommandRecord) -> None:
    _ensure_session_and_turn(conn, record)
    row_id = stable_id(record.provider, record.session_id, record.turn_id, record.command, record.timestamp)
    preview = record.command[:500]
    output_line_count = len(record.output.splitlines())
    conn.execute(
        """
        INSERT INTO commands (
            id, provider, session_id, turn_id, command_preview,
            output_line_count, output_char_count, status, timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            output_line_count=excluded.output_line_count,
            output_char_count=excluded.output_char_count,
            status=excluded.status
        """,
        (
            row_id,
            record.provider,
            record.session_id,
            record.turn_id,
            preview,
            output_line_count,
            len(record.output),
            record.status,
            record.timestamp,
        ),
    )
    conn.commit()


def summary(conn: sqlite3.Connection, provider: str | None = None) -> dict[str, Any]:
    params: list[str] = []
    where = ""
    if provider:
        where = "WHERE provider = ?"
        params.append(provider)

    totals = conn.execute(
        f"""
        SELECT
            COALESCE(SUM(input_tokens), 0) AS input_tokens,
            COALESCE(SUM(output_tokens), 0) AS output_tokens,
            COALESCE(SUM(cache_creation_tokens), 0) AS cache_creation_tokens,
            COALESCE(SUM(cache_read_tokens), 0) AS cache_read_tokens,
            COALESCE(SUM(reasoning_tokens), 0) AS reasoning_tokens,
            COUNT(*) AS usage_records
        FROM usage_records
        {where}
        """,
        params,
    ).fetchone()
    models = conn.execute(
        f"""
        SELECT model, COUNT(*) AS count,
               COALESCE(SUM(input_tokens + output_tokens + cache_creation_tokens + cache_read_tokens + reasoning_tokens), 0) AS tokens
        FROM usage_records
        {where}
        GROUP BY model
        ORDER BY tokens DESC, model
        """,
        params,
    ).fetchall()
    commands = conn.execute(
        f"""
        SELECT command_family, COUNT(*) AS count,
               COALESCE(SUM(output_line_count), 0) AS output_lines
        FROM commands
        {where}
        GROUP BY command_family
        ORDER BY output_lines DESC, command_family
        """,
        params,
    ).fetchall()
    total_tokens = sum(
        int(totals[key])
        for key in ("input_tokens", "output_tokens", "cache_creation_tokens", "cache_read_tokens", "reasoning_tokens")
    )
    return {
        "provider": provider or "all",
        "totals": {key: int(totals[key]) for key in totals.keys()} | {"total_tokens": total_tokens},
        "models": [dict(row) for row in models],
        "commands": [dict(row) for row in commands],
    }
