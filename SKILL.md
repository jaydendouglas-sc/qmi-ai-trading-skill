---
name: qmi-market-regime
description: >
  Quantum Market Intelligence is an explainable multi-factor crypto market-regime
  and portfolio-allocation Skill. It evaluates trend, momentum, volume, market
  rotation, sentiment and volatility, then applies hard risk controls before
  producing a bounded BTC/ETH/SOL/LINK/cash allocation and an auditable JSON decision.
version: 1.0.1
license: MIT
---

# Quantum Market Intelligence — Market Regime and Risk Allocation Skill

## 1. Skill Name

**Quantum Market Intelligence (QMI): Market Regime and Risk Allocation**

## 2. Strategy Type

**Explainable multi-factor regime classification and risk-controlled portfolio rotation**

QMI combines trend following, momentum confirmation, relative-strength rotation and portfolio-risk controls. It is deterministic and rules-based. It is designed for use by an AI Agent that needs a transparent decision procedure rather than an opaque prediction.

## 3. Applicable Market

- **Primary market:** liquid crypto spot markets
- **Reference assets:** BTC, ETH, SOL and LINK
- **Quote currency:** USD or USDT-equivalent
- **Primary timeframe:** 1D
- **Confirmation timeframe:** 4H
- **Optional execution timeframe:** 1H
- **Default rebalance frequency:** once after the daily close
- **Not suitable for:** illiquid tokens, newly listed assets without sufficient history, or data feeds with unreliable volume

Perpetual futures can be observed as sentiment inputs, but the default allocation is for unleveraged spot exposure. Any futures implementation must independently account for funding, liquidation, slippage and exchange risk.

## 4. Objective

The Skill answers:

> What market regime is supported by the available evidence, how much portfolio risk is justified, and what bounded allocation is appropriate?

It does not attempt to forecast exact prices.

## 5. Required Inputs

The Agent must supply current, timestamped values for:

### Trend
- BTC close relative to SMA50 and SMA200
- EMA21 relative to EMA55
- ADX(14)

### Momentum
- RSI(14)
- MACD histogram direction
- 20-period rate of change

### Volume
- Current volume relative to 20-period average
- On-balance-volume direction

### Rotation
- ETH/BTC relative to its 21- and 55-period averages
- BTC dominance trend

### Sentiment
- Fear & Greed value
- aggregate perpetual funding rate
- open-interest change

### Volatility and portfolio state
- ATR as a percentage of price
- realized-volatility percentile
- current daily portfolio loss
- peak-to-current drawdown
- data age and missing-field status

If a mandatory field is missing or stale, the Skill must not issue an expansionary trade action.

## 6. Core Logic

### 6.1 Factor scores

Each factor is scored from 0 to 100.

#### Trend score

```text
+30 if BTC is above SMA200, else +0
+20 if BTC is above SMA50, else +0
+20 if EMA21 is above EMA55, else +0
+15 if EMA21 slope is positive, else +0
+15 if ADX >= 20, else +7.5 if ADX >= 15, else +0
```

#### Momentum score

```text
RSI:
  55–70  -> 35
  50–54.99 -> 25
  40–49.99 -> 15
  30–39.99 -> 8
  otherwise -> 0

MACD histogram rising -> 35
20-period ROC:
  > 5% -> 30
  0% to 5% -> 20
  -5% to 0% -> 10
  below -5% -> 0
```

#### Volume score

```text
Volume / MA20:
  >= 1.30 -> 55
  >= 1.00 -> 40
  >= 0.80 -> 25
  otherwise -> 10

OBV rising -> 45
```

#### Rotation score

```text
ETH/BTC above MA21 -> 30
ETH/BTC MA21 above MA55 -> 30
ETH/BTC MA21 slope positive -> 20
BTC dominance falling -> 20
```

This score identifies broad risk appetite. It does not force an ETH-heavy portfolio when portfolio-level risk controls are active.

#### Sentiment score

Fear & Greed:

```text
45–75 -> 40
25–44 -> 25
76–85 -> 20
15–24 -> 10
otherwise -> 0
```

Funding:

```text
-0.01% to +0.03% per 8h -> 30
-0.03% to -0.01% -> 20
+0.03% to +0.08% -> 15
otherwise -> 0
```

Open interest:

```text
-5% to +8% change -> 30
+8% to +15% -> 15
otherwise -> 5
```

#### Volatility-quality score

```text
ATR percentage:
  1.5%–4.5% -> 45
  0.8%–1.49% -> 30
  4.51%–7.0% -> 20
  otherwise -> 5

Realized-volatility percentile:
  20–70 -> 35
  70–85 -> 20
  below 20 -> 15
  above 85 -> 0

No volatility shock -> 20
```

### 6.2 Weighted confidence

```text
confidence =
  trend * 0.30 +
  momentum * 0.20 +
  volume * 0.15 +
  rotation * 0.15 +
  sentiment * 0.10 +
  volatility_quality * 0.10
```

The value is rounded to one decimal place.

### 6.3 Regime classification

```text
Hard risk trigger -> High Risk
80–100 -> Strong Bull
65–79.99 -> Bull
55–64.99 -> Recovery
45–54.99 -> Neutral
30–44.99 -> Weak
0–29.99 -> Bear
```

### 6.4 Base portfolio targets

All values are percentages of total portfolio equity.

| Regime | BTC | ETH | SOL | LINK | Cash |
|---|---:|---:|---:|---:|---:|
| Strong Bull | 35 | 30 | 15 | 10 | 10 |
| Bull | 40 | 25 | 8 | 7 | 20 |
| Recovery | 40 | 20 | 5 | 5 | 30 |
| Neutral | 35 | 15 | 0 | 0 | 50 |
| Weak | 25 | 5 | 0 | 0 | 70 |
| Bear | 10 | 0 | 0 | 0 | 90 |
| High Risk | 0 | 0 | 0 | 0 | 100 |

### 6.5 Rotation adjustment

Only in Strong Bull, Bull or Recovery:

- If rotation score is at least 70, shift 5 percentage points from BTC to ETH.
- If rotation score is below 35, shift 5 percentage points from ETH to BTC.
- No adjustment may reduce an asset below zero or cause invested exposure to exceed the active risk cap.

## 7. Hard Risk Controls

Risk controls override factor scores.

### 7.1 Data-quality stop

Set **High Risk** and return no expansionary action if:

- a mandatory field is missing;
- market data is older than the configured maximum age;
- values are non-finite or outside plausible validation bounds.

### 7.2 Daily-loss circuit breaker

If daily portfolio loss is at or below `-3%`:

- set risk mode to `Circuit Breaker`;
- prohibit new entries;
- target 100% cash in the reference implementation;
- require a new daily session before normal operation can resume.

### 7.3 Drawdown protection

If drawdown from peak is:

- at least 10%: maximum invested exposure is 30%;
- at least 15%: maximum invested exposure is 10%;
- at least 20%: High Risk, target 100% cash.

### 7.4 Trend protection

If BTC is below SMA200:

- maximum invested exposure is 30%;
- SOL and LINK allocations are set to zero;
- no leveraged exposure is permitted.

### 7.5 Volatility shock

A volatility shock exists when either:

- ATR is above 7% of price; or
- realized volatility is above the 90th percentile.

During a shock:

- maximum invested exposure is 25%;
- SOL and LINK allocations are zero;
- the Agent must state that widened spreads and slippage may invalidate nominal signals.

### 7.6 Sentiment pause

If Fear & Greed is below 15:

- no new risk expansion;
- maximum invested exposure is 20%.

If aggregate funding is above +0.10% per 8h:

- treat leverage conditions as crowded;
- maximum invested exposure is 40%;
- do not use leverage.

### 7.7 Leverage

The reference implementation does not open leveraged trades. A derivative adapter may never exceed 2× gross leverage and must also obey stricter exchange-specific controls. Leverage is zero in Weak, Bear, High Risk, circuit-breaker or volatility-shock states.

## 8. Position and Execution Rules

- Rebalance no more than once per daily close unless a hard risk control activates.
- Move toward the target in no more than two equal tranches when allocation changes by over 20 percentage points.
- Do not trade when the expected order size is below exchange minimums.
- Use limit orders where practical; define a maximum slippage tolerance before execution.
- Do not average down after a hard risk trigger.
- The Skill returns a target allocation, not exchange credentials or direct order placement.

## 9. Invalidation Conditions

A normal or bullish signal is invalidated when any of the following occurs:

1. BTC closes below SMA200.
2. The daily-loss circuit breaker activates.
3. Drawdown reaches the configured maximum.
4. Data becomes stale, incomplete or inconsistent.
5. A volatility shock activates.
6. The next daily close moves the weighted score into a lower regime.
7. Exchange availability, liquidity or spread conditions make execution unsafe.

## 10. Agent Execution Flow

```text
1. Fetch timestamped market and portfolio data.
2. Validate schema, freshness and plausible ranges.
3. Calculate or receive the required indicators.
4. Score the six factor groups.
5. Calculate weighted confidence.
6. Check hard risk controls.
7. Classify the market regime.
8. Build the base allocation.
9. Apply the rotation adjustment.
10. Apply exposure caps and asset restrictions.
11. Compare current and target allocations.
12. Return a structured decision packet.
13. Log inputs, configuration version and output for audit.
14. Wait until the next permitted evaluation time unless a risk trigger occurs.
```

## 11. Standard Output Format

```json
{
  "skill": "qmi-market-regime",
  "version": "1.0.1",
  "evaluated_at": "ISO-8601 timestamp",
  "data_timestamp": "ISO-8601 timestamp",
  "data_quality": "Valid | Invalid | Stale",
  "factor_scores": {
    "trend": 0,
    "momentum": 0,
    "volume": 0,
    "rotation": 0,
    "sentiment": 0,
    "volatility_quality": 0
  },
  "confidence": 0.0,
  "regime": "Strong Bull | Bull | Recovery | Neutral | Weak | Bear | High Risk",
  "risk_mode": "Normal | Capped | Volatility Shock | Circuit Breaker | Data Stop",
  "maximum_invested_exposure": 0,
  "allocation": {
    "BTC": 0,
    "ETH": 0,
    "SOL": 0,
    "LINK": 0,
    "CASH": 100
  },
  "action": "Plain-language executable instruction",
  "evidence": ["Reason 1", "Reason 2"],
  "invalidation_conditions": ["Condition 1", "Condition 2"],
  "warnings": ["Warning 1"],
  "risk_notice": "This output is a strategy demonstration and not investment advice."
}
```

## 12. Core Parameters

| Parameter | Default | Purpose |
|---|---:|---|
| `trend_weight` | 0.30 | Weight of trend score |
| `momentum_weight` | 0.20 | Weight of momentum score |
| `volume_weight` | 0.15 | Weight of volume score |
| `rotation_weight` | 0.15 | Weight of rotation score |
| `sentiment_weight` | 0.10 | Weight of sentiment score |
| `volatility_weight` | 0.10 | Weight of volatility-quality score |
| `max_data_age_minutes` | 90 | Data-freshness limit |
| `daily_loss_limit_pct` | -3.0 | Daily circuit breaker |
| `drawdown_cap_pct` | -10.0 | First drawdown exposure cap |
| `max_drawdown_pct` | -20.0 | Full risk-off threshold |
| `volatility_shock_atr_pct` | 7.0 | ATR shock threshold |
| `volatility_shock_percentile` | 90 | Realized-volatility shock |
| `fear_pause` | 15 | Sentiment pause threshold |
| `crowded_funding_pct` | 0.10 | Funding crowding threshold |
| `max_leverage` | 2.0 | Absolute derivative ceiling |
| `rebalance_frequency` | 1D close | Normal evaluation frequency |

## 13. Executability

This repository includes:

- a Python package in the repository root;
- a command-line interface;
- sample JSON market input;
- deterministic unit tests;
- default YAML parameters;
- scenario examples;
- an output schema;
- architecture and risk documentation.

The reference code produces allocations only. It intentionally excludes exchange keys and direct order execution.

## 14. Backtesting and Evidence Policy

No performance metric may be presented unless produced from a reproducible test with:

- named data source;
- date range;
- fees;
- slippage assumptions;
- rebalance timing;
- survivorship treatment;
- configuration version;
- downloadable results or code.

This v1.0 submission does **not** claim a win rate, Sharpe ratio, profit factor or expected return. Scenario examples are illustrative rule executions only.

## 15. Risk Notice

Crypto assets are highly volatile and can lose substantial or total value. Moving averages and momentum indicators are lagging and can produce repeated false signals. Correlations can rise sharply during market stress, making nominal diversification ineffective. Stablecoins, exchanges, data vendors and network infrastructure each introduce separate failure risks. Funding, fees, slippage, taxation and liquidity can materially change results.

QMI is educational software and a strategy demonstration. It is not investment, financial, legal or tax advice; it does not guarantee returns; and it should not be used with real funds without independent testing, supervision and controls.

## 16. Originality and Attribution

This submission was built as an original response to the challenge requirements. The challenge's public reference format informed the presence of standard sections such as market, logic, parameters, risks and Agent flow. The strategy rules, scoring, allocation system, implementation and documentation are original to this repository.

Contributors must not add copied strategy text, proprietary code or unlicensed data.

## 17. Public GitHub Link

```text
https://github.com/jaydendouglas-sc/qmi-ai-trading-skill
```

## 18. Submission Checklist

- [x] Skill name
- [x] Strategy type
- [x] Applicable market
- [x] Core logic
- [x] Core parameters
- [x] Risk notice
- [x] Agent execution flow
- [x] Output format
- [x] Invalidation conditions
- [x] Executable reference implementation
- [x] Unit tests
- [x] Originality statement
- [x] Public GitHub link inserted
- [x] Repository visibility confirmed as public
- [ ] Final activity-form submission completed
