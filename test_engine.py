import json
import unittest
from pathlib import Path

from qmi_skill.engine import evaluate
from qmi_skill.models import MarketInput


ROOT = Path(__file__).resolve().parents[1]


class QMITestCase(unittest.TestCase):
    def sample(self):
        raw = json.loads((ROOT / "data/sample-market-input.json").read_text())
        return raw

    def test_sample_is_valid_and_allocates_100(self):
        result = evaluate(MarketInput.from_dict(self.sample()))
        self.assertEqual(result["data_quality"], "Valid")
        self.assertEqual(sum(result["allocation"].values()), 100)
        self.assertGreaterEqual(result["confidence"], 0)
        self.assertLessEqual(result["confidence"], 100)

    def test_stale_data_forces_high_risk(self):
        raw = self.sample()
        raw["evaluated_at"] = "2026-08-05T12:00:00+00:00"
        result = evaluate(MarketInput.from_dict(raw), max_data_age_minutes=90)
        self.assertEqual(result["regime"], "High Risk")
        self.assertEqual(result["allocation"]["CASH"], 100)
        self.assertEqual(result["risk_mode"], "Data Stop")

    def test_daily_loss_circuit_breaker(self):
        raw = self.sample()
        raw["daily_portfolio_loss_pct"] = -3.2
        result = evaluate(MarketInput.from_dict(raw))
        self.assertEqual(result["regime"], "High Risk")
        self.assertEqual(result["maximum_invested_exposure"], 0)

    def test_below_sma200_removes_alts_and_caps_exposure(self):
        raw = self.sample()
        raw["btc_above_sma200"] = False
        result = evaluate(MarketInput.from_dict(raw))
        self.assertLessEqual(result["maximum_invested_exposure"], 30)
        self.assertEqual(result["allocation"]["SOL"], 0)
        self.assertEqual(result["allocation"]["LINK"], 0)

    def test_missing_field_fails_closed(self):
        raw = self.sample()
        del raw["rsi"]
        with self.assertRaises(ValueError):
            MarketInput.from_dict(raw)


if __name__ == "__main__":
    unittest.main()
