from __future__ import annotations

import unittest
from pathlib import Path

from core.costs import estimate_cost
from core.models import UsageRecord


CONFIG = Path(__file__).parents[1] / "config"


class CostTests(unittest.TestCase):
    def test_anthropic_api_cost(self) -> None:
        estimate = estimate_cost(
            UsageRecord("anthropic", "s", "t", "claude-sonnet-4-5", "", 1_000_000, 1_000_000, 0, 0, 0),
            CONFIG,
        )
        self.assertEqual(estimate.confidence, "priced_token_estimate")
        self.assertAlmostEqual(estimate.usd or 0, 18.0)

    def test_codex_api_cost_includes_reasoning(self) -> None:
        estimate = estimate_cost(
            UsageRecord("codex", "s", "t", "gpt-5.6-sol", "", 1_000_000, 1_000_000, 0, 0, 1_000_000),
            CONFIG,
        )
        self.assertEqual(estimate.confidence, "priced_token_estimate")
        self.assertAlmostEqual(estimate.usd or 0, 44.0)

    def test_zai_api_cost_uses_cached_input(self) -> None:
        estimate = estimate_cost(
            UsageRecord("zai", "s", "t", "glm-5.3", "", 1_000_000, 1_000_000, 0, 1_000_000, 0),
            CONFIG,
        )
        self.assertEqual(estimate.confidence, "priced_token_estimate")
        self.assertAlmostEqual(estimate.usd or 0, 6.06)

    def test_zai_coding_plan_returns_credits_not_usd(self) -> None:
        estimate = estimate_cost(
            UsageRecord("zai", "s", "t", "glm-5.3-flash", "", 10_000, 10_000, 0, 10_000, 0),
            CONFIG,
            billing_mode="coding_plan",
        )
        self.assertIsNone(estimate.usd)
        self.assertEqual(estimate.confidence, "priced_token_estimate")
        self.assertAlmostEqual(estimate.credits or 0, 1.05)

    def test_unknown_model_is_not_guessed(self) -> None:
        estimate = estimate_cost(UsageRecord("zai", "s", "t", "unknown-model", ""), CONFIG)
        self.assertIsNone(estimate.usd)
        self.assertEqual(estimate.confidence, "unpriced_model")


if __name__ == "__main__":
    unittest.main()
