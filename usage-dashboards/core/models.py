from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UsageRecord:
    provider: str
    session_id: str
    turn_id: str
    model: str
    timestamp: str
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_tokens: int = 0
    cache_read_tokens: int = 0
    reasoning_tokens: int = 0
    project: str = ""
    source_path: str = ""


@dataclass(frozen=True)
class CommandRecord:
    provider: str
    session_id: str
    turn_id: str
    command: str
    output: str = ""
    status: str = "unknown"
    timestamp: str = ""


@dataclass(frozen=True)
class CostEstimate:
    provider: str
    model: str
    mode: str
    usd: float | None
    credits: float | None
    confidence: str
    notes: str = ""


@dataclass(frozen=True)
class Recommendation:
    severity: str
    title: str
    detail: str
    source: str
