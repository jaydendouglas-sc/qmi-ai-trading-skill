# Quantum Market Intelligence (QMI)

> An explainable, rules-based crypto market-regime and risk-allocation Skill designed for AI-agent execution.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Status](https://img.shields.io/badge/status-submission--ready-success.svg)
![Strategy](https://img.shields.io/badge/strategy-multi--factor%20regime-purple.svg)
![Agent Ready](https://img.shields.io/badge/agent-ready-orange.svg)

## Overview

QMI converts market observations into a reviewable decision packet:

1. validate data quality;
2. score trend, momentum, volume, rotation, sentiment and volatility;
3. classify the market regime;
4. apply hard risk controls;
5. propose a capped BTC/ETH/SOL/LINK/cash allocation;
6. state the evidence, invalidation conditions and confidence.

QMI is **not a machine-learning model** and does not claim predictive intelligence. It is a deterministic strategy Skill that an AI Agent can call, explain and audit.

## Why this submission is different

- **Explainable:** every score maps to visible rules.
- **Executable:** a Python reference implementation and command-line interface are included.
- **Risk-first:** data failures, drawdown limits, daily-loss limits and volatility controls override opportunity signals.
- **Agent-friendly:** JSON input and JSON output have explicit schemas.
- **Original:** the strategy logic, scoring system, regime map and implementation were created for this submission.
- **Reviewable:** no invented performance statistics or unverified backtest claims are included.

## Strategy summary

QMI uses six factor groups:

| Factor | Weight |
|---|---:|
| Trend | 30% |
| Momentum | 20% |
| Volume | 15% |
| Rotation | 15% |
| Sentiment | 10% |
| Volatility quality | 10% |

The weighted score determines one of seven states:

| Score / condition | Regime |
|---|---|
| Hard risk trigger | High Risk |
| 80–100 | Strong Bull |
| 65–79.99 | Bull |
| 55–64.99 | Recovery |
| 45–54.99 | Neutral |
| 30–44.99 | Weak |
| 0–29.99 | Bear |

Risk controls may reduce exposure regardless of regime.

## Repository map

```text
qmi-ai-trading-skill/
├── README.md
├── SKILL.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
├── config/default-parameters.yaml
├── data/sample-market-input.json
├── docs/
├── examples/
├── src/qmi_skill/
├── tests/
└── assets/
```

## Quick start

```bash
python -m pip install -e .
qmi-skill data/sample-market-input.json
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Example output

```json
{
  "skill": "qmi-market-regime",
  "regime": "Bull",
  "confidence": 73.4,
  "risk_mode": "Normal",
  "allocation": {
    "BTC": 40,
    "ETH": 25,
    "SOL": 8,
    "LINK": 7,
    "CASH": 20
  },
  "action": "Rebalance gradually toward the target allocation.",
  "invalidation_conditions": [
    "BTC closes below its 200-day moving average.",
    "Daily portfolio loss reaches the configured circuit-breaker.",
    "Input data becomes stale or incomplete."
  ]
}
```

The actual sample result depends on the supplied inputs and configuration.

## Required submission content

The canonical strategy specification is in [`SKILL.md`](SKILL.md). It contains:

- Skill name
- Strategy type
- Applicable market
- Core logic
- Core parameters
- Risk notice
- Agent execution flow
- Standard output format
- Invalidation conditions
- Public GitHub link placeholder

## Important limitations

QMI does not place orders, hold API keys, guarantee returns or replace independent risk assessment. It does not include a claimed live or historical performance record. The included scenario outputs are demonstrations of rule execution, not evidence of profitability.

## Submission steps

1. Create a new public GitHub repository.
2. Upload the contents of this folder.
3. Replace the public-link placeholder in `SKILL.md`.
4. Confirm the repository is accessible without signing in.
5. Run the included tests.
6. Submit the public GitHub URL through the challenge activity form before the stated deadline.

## License

MIT. See [`LICENSE`](LICENSE).
