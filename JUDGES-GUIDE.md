# Reviewer Guide

For the fastest review:

1. Read [`SKILL.md`](SKILL.md) for the complete strategy specification.
2. Review [`DOC-RISK-MANAGEMENT.md`](DOC-RISK-MANAGEMENT.md) for override priority.
3. Inspect [`engine.py`](engine.py) for executable scoring and allocation logic.
4. Run `python -m unittest -v test_engine.py`.
5. Run `python cli.py sample-market-input.json`.

## Challenge criteria mapping

| Criterion | Evidence |
|---|---|
| Strategy completeness | `SKILL.md` sections 1–18 |
| Executability | `engine.py`, `models.py`, `cli.py`, tests |
| Risk awareness | hard stops, caps and invalidations |
| Agent adaptation | structured JSON input/output and Agent flow |
| Long-term content value | modular documentation and roadmap |
| CWC relevance | transparent Agent-ready crypto allocation Skill |
| Originality | explicit originality statement and custom implementation |

No historical return, win-rate or Sharpe claim is made without reproducible evidence.
