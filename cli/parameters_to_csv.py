#!/usr/bin/env python3
"""
Convert test_cases/parameters.json → test_cases/templates_jira_parameters_import.csv

The JSON supports two formats:

  Format A — object with a "parameters" key (array of row objects):
    {
      "parameters": [
        {"row_id": 1, "template": "egypt1", "arrival_date": "2029-01-02"},
        {"row_id": 2, "template": "egyptseo", "arrival_date": "2029-01-02"}
      ]
    }

  Format B — direct array of row objects:
    [
      {"row_id": 1, "template": "egypt1"},
      {"row_id": 2, "template": "egyptseo"}
    ]

Column order follows the key order of the first object.
All values are written as plain strings.

Usage (from project root):
    python cli/parameters_to_csv.py
    python cli/parameters_to_csv.py --input test_cases/parameters.json --output test_cases/templates_jira_parameters_import.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config

DEFAULT_INPUT = config.TEST_CASES_DIR / "parameters.json"
DEFAULT_OUTPUT = config.TEST_CASES_DIR / "templates_jira_parameters_import.csv"


def load_parameters(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and "parameters" in data:
        rows = data["parameters"]
    else:
        raise ValueError(
            "parameters.json must be either a JSON array or an object with a "
            "'parameters' key containing an array."
        )

    if not rows:
        raise ValueError("No rows found in parameters.json.")
    if not all(isinstance(r, dict) for r in rows):
        raise ValueError("Every entry in 'parameters' must be a JSON object.")

    return rows


def write_csv(rows: list[dict], path: Path) -> None:
    # Collect all unique keys preserving first-seen order
    seen: dict[str, None] = {}
    for row in rows:
        for key in row:
            seen[key] = None
    headers = list(seen)

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            # Fill missing keys with empty string
            writer.writerow({h: row.get(h, "") for h in headers})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert parameters.json to Xray-compatible CSV."
    )
    parser.add_argument(
        "--input", default=str(DEFAULT_INPUT),
        help=f"Path to parameters.json (default: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output", default=str(DEFAULT_OUTPUT),
        help=f"Path to output CSV (default: {DEFAULT_OUTPUT})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    rows = load_parameters(input_path)
    write_csv(rows, output_path)

    print(f"Written {len(rows)} rows → {output_path}")
    print(f"Columns: {', '.join(rows[0].keys())}")


if __name__ == "__main__":
    main()
