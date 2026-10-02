"""Run with python -m gold_analysis from the repository root."""
import argparse
import sys
import pandas as pd
from .pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze contemporaneous GLD associations (not forecasts).")
    parser.add_argument("--input", required=True, help="CSV with YYYY-MM-DD dates")
    parser.add_argument("--output", default="outputs", help="Directory for replaceable generated results")
    args = parser.parse_args()
    try:
        run_pipeline(args.input, args.output)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
