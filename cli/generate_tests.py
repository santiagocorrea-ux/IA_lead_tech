#!/usr/bin/env python3
"""
Generate VISA-format Excel test cases from a JSON file.

Usage (from project root):
    python cli/generate_tests.py \\
        --json test_cases/test_cases.json \\
        --template test_cases/VISASGF-4167_test_cases.xlsx \\
        --output test_cases/test_cases.xlsx

The --template and --output flags default to the standard project paths,
so for the typical workflow you only need:

    python cli/generate_tests.py --json test_cases/test_cases.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running directly from the project root without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config
from src.services.test_case_generator import build_excel, load_test_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create VISA-format Excel test cases from JSON.")
    parser.add_argument("--json", required=True, help="Path to the input JSON file.")
    parser.add_argument(
        "--template",
        default=str(config.EXCEL_TEMPLATE),
        help="Path to the VISA Excel template (default: test_cases/VISASGF-4167_test_cases.xlsx).",
    )
    parser.add_argument(
        "--output",
        default=str(config.DEFAULT_EXCEL_OUTPUT),
        help="Path to the output .xlsx file (default: test_cases/test_cases.xlsx).",
    )
    parser.add_argument(
        "--sheet",
        default=None,
        help="Sheet name. Defaults to the JSON filename stem.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sheet_name = args.sheet or Path(args.json).stem
    test_cases = load_test_cases(args.json)
    output = build_excel(
        template_path=args.template,
        output_path=args.output,
        test_cases=test_cases,
        sheet_name=sheet_name,
    )
    action = "Updated" if Path(args.output).exists() else "Created"
    print(f"{action}: {output}  (sheet: '{sheet_name}', {len(test_cases)} test case(s))")


if __name__ == "__main__":
    main()
