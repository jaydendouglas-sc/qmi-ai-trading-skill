from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .models import MarketInput


BASE_ALLOCATIONS = {
    "Strong Bull": {"BTC": 35, "ETH": 30, "SOL": 15, "LINK": 10, "CASH": 10},
    "Bull": {"BTC": 40, "ETH": 25, "SOL": 8, "LINK": 7, "CASH": 20},
    "Recovery": {"BTC": 40, "ETH": 20, "SOL": 5, "LINK": 5, "CASH": 30},
    "Neutral": {"BTC": 35, "ETH": 15, "SOL": 0, "LINK": 0, "CASH": 50},
    "Weak": {"BTC": 25, "ETH": 5, "SOL": 0, "LINK": 0, "CASH": 70},
    "Bear": {"BTC": 10, "ETH": 0, "SOL": 0, "LINK": 0, "CASH": 90},
    "High Risk": {"BTC": 0, "ETH": 0, "SOL": 0, "LINK": 0, "CASH": 100},
}


def _trend(m: MarketInput) -> float:
    return min(100.0, (
        (30 if m.btc_above_sma200 else 0)
        + (20 if m.btc_above_sma50 else 0)
        + (20 if m.ema21_above_ema55 else 0)
        + (15 if m.ema21_slope_positive else 0)
        + (15 if m.adx >= 20 else 7.5 if m.adx >= 15 else 0)
    ))


def _momentum(m: MarketInput) -> float:
    if 55 <= m.rsi <= 70:
        rsi = 35
    elif 50 <= m.rsi < 55:
        rsi = 25
    elif 40 <= m.rsi < 50:
        rsi = 15
    elif 30 <= m.rsi < 40:
        rsi = 8
    else:
        rsi = 0
    macd = 35 if m.macd_histogram_rising else 0
    roc = 30 if m.roc_20_pct > 5 else 20 if m.roc_20_pct >= 0 else 10 if m.roc_20_pct >= -5 else 0
    return float(rsi + macd + roc)


def _volume(m: MarketInput) -> float:
    ratio = 55 if m.volume_to_ma20 >= 1.30 else 40 if m.volume_to_ma20 >= 1.0 else 25 if m.volume_to_ma20 >= 0.8 else 10
    return float(ratio + (45 if m.obv_rising else 0))


def _rotation(m: MarketInput) -> float:
    return float(
        (30 if m.ethbtc_above_ma21 else 0)
        + (30 if m.ethbtc_ma21_above_ma55 else 0)
        + (20 if m.ethbtc_ma21_slope_positive else 0)
        + (20 if m.btc_dominance_falling else 0)
    )


def _sentiment(m: MarketInput) -> float:
    fg = 40 if 45 <= m.fear_greed <= 75 else 25 if 25 <= m.fear_greed < 45 else 20 if 75 < m.fear_greed <= 85 else 10 if 15 <= m.fear_greed < 25 else 0
    f = m.funding_rate_pct_8h
    funding = 30 if -0.01 <= f <= 0.03 else 20 if -0.03 <= f < -0.01 else 15 if 0.03 < f <= 0.08 else 0
    oi = m.open_interest_change_pct
    open_interest = 30 if -5 <= oi <= 8 else 15 if 8 < oi <= 15 else 5
    return float(fg + funding + open_interest)


def _volatility_quality(m: MarketInput) -> float:
    atr = 45 if 1.5 <= m.atr_pct <= 4.5 else 30 if 0.8 <= m.atr_pct < 1.5 else 20 if 4.5 < m.atr_pct <= 7 else 5
    rv = 35 if 20 <= m.realized_vol_percentile <= 70 else 20 if 70 < m.realized_vol_percentile <= 85 else 15 if m.realized_vol_percentile < 20 else 0
    shock = m.atr_pct > 7 or m.realized_vol_percentile > 90
    return float(atr + rv + (0 if shock else 20))


def _regime(confidence: float) -> str:
    if confidence >= 80:
        return "Strong Bull"
    if confidence >= 65:
        return "Bull"
    if confidence >= 55:
        return "Recovery"
    if confidence >= 45:
        return "Neutral"
    if confidence >= 30:
        return "Weak"
    return "Bear"


def _cap_allocation(allocation: dict[str, int], max_invested: int, remove_alts: bool = False) -> dict[str, int]:
    a = dict(allocation)
    if remove_alts:
        a["SOL"] = 0
        a["LINK"] = 0
    invested = a["BTC"] + a["ETH"] + a["SOL"] + a["LINK"]
    if invested > max_invested and invested > 0:
        scale = max_invested / invested
        for asset in ("BTC", "ETH", "SOL", "LINK"):
            a[asset] = int(round(a[asset] * scale))
        # Correct rounding by assigning remainder to BTC.
        new_invested = a["BTC"] + a["ETH"] + a["SOL"] + a["LINK"]
        a["BTC"] += max_invested - new_invested
    a["CASH"] = 100 - (a["BTC"] + a["ETH"] + a["SOL"] + a["LINK"])
    return a


def evaluate(m: MarketInput, max_data_age_minutes: int = 90) -> dict[str, Any]:
    age_minutes = (m.evaluated_at - m.data_timestamp).total_seconds() / 60
    if age_minutes < 0:
        raise ValueError("data_timestamp cannot be later than evaluated_at")

    scores = {
        "trend": _trend(m),
        "momentum": _momentum(m),
        "volume": _volume(m),
        "rotation": _rotation(m),
        "sentiment": _sentiment(m),
        "volatility_quality": _volatility_quality(m),
    }
    confidence = round(
        scores["trend"] * 0.30
        + scores["momentum"] * 0.20
        + scores["volume"] * 0.15
        + scores["rotation"] * 0.15
        + scores["sentiment"] * 0.10
        + scores["volatility_quality"] * 0.10,
        1,
    )

    warnings: list[str] = []
    evidence: list[str] = []
    risk_mode = "Normal"
    max_invested = 90
    forced_regime: str | None = None
    remove_alts = False

    if age_minutes > max_data_age_minutes:
        forced_regime = "High Risk"
        risk_mode = "Data Stop"
        max_invested = 0
        warnings.append(f"Input data is stale: {age_minutes:.1f} minutes old.")

    if m.daily_portfolio_loss_pct <= -3.0:
        forced_regime = "High Risk"
        risk_mode = "Circuit Breaker"
        max_invested = 0
        warnings.append("Daily-loss circuit breaker activated.")

    if m.drawdown_from_peak_pct <= -20.0:
        forced_regime = "High Risk"
        risk_mode = "Capped"
        max_invested = 0
        warnings.append("Maximum drawdown threshold reached.")
    elif m.drawdown_from_peak_pct <= -15.0:
        risk_mode = "Capped"
        max_invested = min(max_invested, 10)
        remove_alts = True
        warnings.append("Severe drawdown cap active.")
    elif m.drawdown_from_peak_pct <= -10.0:
        risk_mode = "Capped"
        max_invested = min(max_invested, 30)
        remove_alts = True
        warnings.append("Drawdown protection active.")

    if not m.btc_above_sma200:
        risk_mode = "Capped" if risk_mode == "Normal" else risk_mode
        max_invested = min(max_invested, 30)
        remove_alts = True
        warnings.append("BTC is below SMA200; exposure capped.")

    volatility_shock = m.atr_pct > 7 or m.realized_vol_percentile > 90
    if volatility_shock:
        risk_mode = "Volatility Shock" if risk_mode == "Normal" else risk_mode
        max_invested = min(max_invested, 25)
        remove_alts = True
        warnings.append("Volatility shock detected; spreads and slippage may be elevated.")

    if m.fear_greed < 15:
        max_invested = min(max_invested, 20)
        risk_mode = "Capped" if risk_mode == "Normal" else risk_mode
        warnings.append("Fear & Greed pause active.")

    if m.funding_rate_pct_8h > 0.10:
        max_invested = min(max_invested, 40)
        risk_mode = "Capped" if risk_mode == "Normal" else risk_mode
        warnings.append("Crowded positive funding detected; leverage prohibited.")

    regime = forced_regime or _regime(confidence)
    allocation = dict(BASE_ALLOCATIONS[regime])

    if regime in {"Strong Bull", "Bull", "Recovery"}:
        if scores["rotation"] >= 70 and allocation["BTC"] >= 5:
            allocation["BTC"] -= 5
            allocation["ETH"] += 5
            evidence.append("Rotation score favors ETH relative strength.")
        elif scores["rotation"] < 35 and allocation["ETH"] >= 5:
            allocation["ETH"] -= 5
            allocation["BTC"] += 5
            evidence.append("Rotation score favors BTC relative strength.")

    allocation = _cap_allocation(allocation, max_invested, remove_alts=remove_alts)

    evidence.extend([
        f"Trend score: {scores['trend']:.1f}/100.",
        f"Momentum score: {scores['momentum']:.1f}/100.",
        f"Weighted confidence: {confidence:.1f}/100.",
    ])

    if regime == "High Risk":
        action = "Do not open new risk positions; move to or remain at the defensive target."
    elif risk_mode != "Normal":
        action = "Reduce exposure to the capped target and do not use leverage."
    else:
        action = "Rebalance gradually toward the target allocation after the permitted daily evaluation."

    return {
        "skill": "qmi-market-regime",
        "version": "1.0.0",
        "evaluated_at": m.evaluated_at.isoformat(),
        "data_timestamp": m.data_timestamp.isoformat(),
        "data_quality": "Stale" if age_minutes > max_data_age_minutes else "Valid",
        "factor_scores": {k: round(v, 1) for k, v in scores.items()},
        "confidence": confidence,
        "regime": regime,
        "risk_mode": risk_mode,
        "maximum_invested_exposure": max_invested,
        "allocation": allocation,
        "action": action,
        "evidence": evidence,
        "invalidation_conditions": [
            "BTC closes below its 200-day moving average.",
            "Daily portfolio loss reaches the circuit-breaker threshold.",
            "Drawdown reaches the maximum configured threshold.",
            "Input data becomes stale, incomplete or inconsistent.",
            "A volatility shock or lower regime is confirmed.",
        ],
        "warnings": warnings,
        "risk_notice": "This output is a strategy demonstration and not investment advice.",
    }
