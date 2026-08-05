from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


REQUIRED_FIELDS = {
    "data_timestamp",
    "evaluated_at",
    "btc_above_sma200",
    "btc_above_sma50",
    "ema21_above_ema55",
    "ema21_slope_positive",
    "adx",
    "rsi",
    "macd_histogram_rising",
    "roc_20_pct",
    "volume_to_ma20",
    "obv_rising",
    "ethbtc_above_ma21",
    "ethbtc_ma21_above_ma55",
    "ethbtc_ma21_slope_positive",
    "btc_dominance_falling",
    "fear_greed",
    "funding_rate_pct_8h",
    "open_interest_change_pct",
    "atr_pct",
    "realized_vol_percentile",
    "daily_portfolio_loss_pct",
    "drawdown_from_peak_pct",
}


@dataclass(frozen=True)
class MarketInput:
    data_timestamp: datetime
    evaluated_at: datetime
    btc_above_sma200: bool
    btc_above_sma50: bool
    ema21_above_ema55: bool
    ema21_slope_positive: bool
    adx: float
    rsi: float
    macd_histogram_rising: bool
    roc_20_pct: float
    volume_to_ma20: float
    obv_rising: bool
    ethbtc_above_ma21: bool
    ethbtc_ma21_above_ma55: bool
    ethbtc_ma21_slope_positive: bool
    btc_dominance_falling: bool
    fear_greed: float
    funding_rate_pct_8h: float
    open_interest_change_pct: float
    atr_pct: float
    realized_vol_percentile: float
    daily_portfolio_loss_pct: float
    drawdown_from_peak_pct: float

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "MarketInput":
        missing = sorted(REQUIRED_FIELDS - raw.keys())
        if missing:
            raise ValueError(f"Missing mandatory fields: {', '.join(missing)}")

        def dt(name: str) -> datetime:
            value = str(raw[name]).replace("Z", "+00:00")
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                raise ValueError(f"{name} must include a timezone")
            return parsed

        obj = cls(
            data_timestamp=dt("data_timestamp"),
            evaluated_at=dt("evaluated_at"),
            btc_above_sma200=bool(raw["btc_above_sma200"]),
            btc_above_sma50=bool(raw["btc_above_sma50"]),
            ema21_above_ema55=bool(raw["ema21_above_ema55"]),
            ema21_slope_positive=bool(raw["ema21_slope_positive"]),
            adx=float(raw["adx"]),
            rsi=float(raw["rsi"]),
            macd_histogram_rising=bool(raw["macd_histogram_rising"]),
            roc_20_pct=float(raw["roc_20_pct"]),
            volume_to_ma20=float(raw["volume_to_ma20"]),
            obv_rising=bool(raw["obv_rising"]),
            ethbtc_above_ma21=bool(raw["ethbtc_above_ma21"]),
            ethbtc_ma21_above_ma55=bool(raw["ethbtc_ma21_above_ma55"]),
            ethbtc_ma21_slope_positive=bool(raw["ethbtc_ma21_slope_positive"]),
            btc_dominance_falling=bool(raw["btc_dominance_falling"]),
            fear_greed=float(raw["fear_greed"]),
            funding_rate_pct_8h=float(raw["funding_rate_pct_8h"]),
            open_interest_change_pct=float(raw["open_interest_change_pct"]),
            atr_pct=float(raw["atr_pct"]),
            realized_vol_percentile=float(raw["realized_vol_percentile"]),
            daily_portfolio_loss_pct=float(raw["daily_portfolio_loss_pct"]),
            drawdown_from_peak_pct=float(raw["drawdown_from_peak_pct"]),
        )
        obj.validate_ranges()
        return obj

    def validate_ranges(self) -> None:
        checks = [
            (0 <= self.adx <= 100, "adx must be between 0 and 100"),
            (0 <= self.rsi <= 100, "rsi must be between 0 and 100"),
            (self.volume_to_ma20 >= 0, "volume_to_ma20 cannot be negative"),
            (0 <= self.fear_greed <= 100, "fear_greed must be between 0 and 100"),
            (self.atr_pct >= 0, "atr_pct cannot be negative"),
            (0 <= self.realized_vol_percentile <= 100, "realized_vol_percentile must be between 0 and 100"),
            (-100 <= self.daily_portfolio_loss_pct <= 100, "daily_portfolio_loss_pct outside plausible range"),
            (-100 <= self.drawdown_from_peak_pct <= 0, "drawdown_from_peak_pct must be between -100 and 0"),
        ]
        for ok, message in checks:
            if not ok:
                raise ValueError(message)
