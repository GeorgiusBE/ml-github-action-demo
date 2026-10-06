"""Fail the CI job if the trained model does not meet a quality threshold."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics",
        default="artifacts/metrics.json",
        help="Path to metrics JSON produced by train.py",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.95,
        help="Minimum required accuracy",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics_path = Path(args.metrics)

    if not metrics_path.exists():
        raise SystemExit(f"Metrics file not found: {metrics_path}")

    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    accuracy = float(metrics["accuracy"])

    print(f"Model accuracy: {accuracy:.4f}")
    print(f"Required accuracy: {args.threshold:.4f}")

    if accuracy < args.threshold:
        raise SystemExit(
            f"QUALITY GATE FAILED: accuracy {accuracy:.4f} < {args.threshold:.4f}"
        )

    print("QUALITY GATE PASSED")


if __name__ == "__main__":
    main()
