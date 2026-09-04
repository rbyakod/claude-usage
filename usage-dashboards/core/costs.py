from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import CostEstimate, UsageRecord


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _usd(tokens: int, rate: float | int | None) -> float:
    if not tokens or rate is None:
        return 0.0
    return float(tokens) * float(rate) / 1_000_000


def _unknown(record: UsageRecord, mode: str) -> CostEstimate:
    return CostEstimate(
        provider=record.provider,
        model=record.model,
        mode=mode,
        usd=None,
        credits=None,
        confidence="unpriced_model",
        notes=f"No local rate configured for {record.provider}/{record.model}",
    )


def estimate_cost(record: UsageRecord, config_dir: Path, billing_mode: str = "api") -> CostEstimate:
    if record.provider == "anthropic":
        return _estimate_anthropic(record, config_dir)
    if record.provider == "codex":
        return _estimate_codex(record, config_dir)
    if record.provider == "zai" and billing_mode == "coding_plan":
        return _estimate_zai_plan(record, config_dir)
    if record.provider == "zai":
        return _estimate_zai_api(record, config_dir)
    return _unknown(record, billing_mode)


def _estimate_anthropic(record: UsageRecord, config_dir: Path) -> CostEstimate:
    config = _load_json(config_dir / "anthropic-pricing.json")
    rates = config.get("models", {}).get(record.model)
    if not rates:
        return _unknown(record, "api")
    total = (
        _usd(record.input_tokens, rates.get("input_per_million"))
        + _usd(record.cache_creation_tokens, rates.get("cache_creation_per_million"))
        + _usd(record.cache_read_tokens, rates.get("cache_read_per_million"))
        + _usd(record.output_tokens, rates.get("output_per_million"))
    )
    return CostEstimate(record.provider, record.model, "api", total, None, "priced_token_estimate", config["rate_version"])


def _estimate_codex(record: UsageRecord, config_dir: Path) -> CostEstimate:
    config = _load_json(config_dir / "codex-pricing.json")
    rates = config.get("models", {}).get(record.model)
    if not rates:
        return _unknown(record, "api")
    total = (
        _usd(record.input_tokens, rates.get("input_per_million"))
        + _usd(record.cache_read_tokens, rates.get("cached_input_per_million"))
        + _usd(record.output_tokens, rates.get("output_per_million"))
        + _usd(record.reasoning_tokens, rates.get("reasoning_per_million"))
    )
    return CostEstimate(record.provider, record.model, "api", total, None, "priced_token_estimate", config["rate_version"])


def _estimate_zai_api(record: UsageRecord, config_dir: Path) -> CostEstimate:
    config = _load_json(config_dir / "zai-pricing.json")
    rates = config.get("api", {}).get("models", {}).get(record.model)
    if not rates:
        return _unknown(record, "api")
    total = (
        _usd(record.input_tokens, rates.get("input_per_million"))
        + _usd(record.cache_read_tokens, rates.get("cached_input_per_million"))
        + _usd(record.output_tokens, rates.get("output_per_million"))
    )
    return CostEstimate(record.provider, record.model, "api", total, None, "priced_token_estimate", config["rate_version"])


def _estimate_zai_plan(record: UsageRecord, config_dir: Path) -> CostEstimate:
    config = _load_json(config_dir / "zai-pricing.json")
    plan = config.get("coding_plan", {})
    rates = plan.get("models", {}).get(record.model)
    if not rates:
        return _unknown(record, "coding_plan")
    denominator = float(plan.get("credit_denominator_tokens") or 10000)
    credits = (
        record.input_tokens * float(rates.get("input_multiplier", 0))
        + record.cache_read_tokens * float(rates.get("cached_input_multiplier", 0))
        + record.output_tokens * float(rates.get("output_multiplier", 0))
    ) / denominator
    return CostEstimate(record.provider, record.model, "coding_plan", None, credits, "priced_token_estimate", config["rate_version"])
