from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import evaluate
from .models import MarketInput


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the QMI market-regime Skill.")
    parser.add_argument("input", type=Path, help="Path to a JSON market-input file.")
    parser.add_argument("--max-data-age-minutes", type=int, default=90)
    args = parser.parse_args()

    try:
        raw = json.loads(args.input.read_text(encoding="utf-8"))
        market = MarketInput.from_dict(raw)
        result = evaluate(market, max_data_age_minutes=args.max_data_age_minutes)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(str(exc))
        return

    print(json.dumps(result, indent=2, sort_keys=False))


if __name__ == "__main__":
    main()
