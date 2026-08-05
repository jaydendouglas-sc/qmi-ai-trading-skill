# High-Risk Scenario

Change either of these sample fields:

```json
"daily_portfolio_loss_pct": -3.2
```

or:

```json
"drawdown_from_peak_pct": -20.0
```

The evaluator should return `High Risk` and a 100% cash target.
