#!/usr/bin/env python3
"""
Generate VISA-format manual test cases in Excel from a JSON file.

Usage:
    python visa_testcase_generator.py \
        --json sample_test_cases.json \
        --template VISASGF-4167_test_cases.xlsx \
        --output generated_test_cases.xlsx
"""

from __future__ import annotations

import argparse
import json
from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet


@dataclass
class Step:
    action: str = ""
    data: str = ""
    expected_result: str = ""


@dataclass
class TestCase:
    name: str
    steps: List[Step]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create VISA-format Excel test cases from JSON."
    )
    parser.add_argument(
        "--json",
        required=True,
        help="Path to the input JSON file with test case definitions.",
    )
    parser.add_argument(
        "--template",
        required=True,
        help="Path to the VISA Excel template used as the style source.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output Excel file (.xlsx).",
    )
    parser.add_argument(
        "--sheet",
        default=None,
        help="Sheet name to write into. Defaults to the first sheet in the template.",
    )
    return parser.parse_args()


def load_test_cases(json_path: str | Path) -> List[TestCase]:
    with open(json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    raw_cases = payload.get("test_cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("JSON must contain a non-empty 'test_cases' array.")

    test_cases: List[TestCase] = []
    for index, raw_case in enumerate(raw_cases, start=1):
        if not isinstance(raw_case, dict):
            raise ValueError(f"test_cases[{index}] must be an object.")

        name = str(raw_case.get("name", "")).strip()
        raw_steps = raw_case.get("steps", [])

        if not name:
            raise ValueError(f"test_cases[{index}] is missing 'name'.")
        if not isinstance(raw_steps, list) or not raw_steps:
            raise ValueError(f"test_cases[{index}] must contain a non-empty 'steps' array.")

        steps: List[Step] = []
        for step_index, raw_step in enumerate(raw_steps, start=1):
            if not isinstance(raw_step, dict):
                raise ValueError(
                    f"test_cases[{index}].steps[{step_index}] must be an object."
                )

            steps.append(
                Step(
                    action=str(raw_step.get("action", "") or ""),
                    data=str(raw_step.get("data", "") or ""),
                    expected_result=str(raw_step.get("expected_result", "") or ""),
                )
            )

        test_cases.append(TestCase(name=name, steps=steps))

    return test_cases


def copy_cell_style(src_cell, dst_cell) -> None:
    dst_cell.font = copy(src_cell.font)
    dst_cell.fill = copy(src_cell.fill)
    dst_cell.border = copy(src_cell.border)
    dst_cell.alignment = copy(src_cell.alignment)
    dst_cell.number_format = copy(src_cell.number_format)
    dst_cell.protection = copy(src_cell.protection)


def copy_template_row_style(ws: Worksheet, src_row: int, dst_row: int, max_col: int) -> None:
    for col in range(1, max_col + 1):
        copy_cell_style(ws.cell(src_row, col), ws.cell(dst_row, col))


def clear_sheet_values(ws: Worksheet) -> None:
    for row in ws.iter_rows():
        for cell in row:
            cell.value = None


def line_count(value: Any) -> int:
    text = "" if value is None else str(value)
    if not text:
        return 1
    return max(1, text.count("\n") + 1)


def step_row_height(step: Step, base_height: float) -> float:
    max_lines = max(
        line_count(step.action),
        line_count(step.data),
        line_count(step.expected_result),
    )
    # Keeps the original look for short rows, but grows when text wraps.
    return max(base_height, 18 * max_lines + 4)


def build_excel(
    template_path: str | Path,
    output_path: str | Path,
    test_cases: List[TestCase],
    sheet_name: str | None = None,
) -> None:
    wb = load_workbook(template_path)
    ws = wb[sheet_name] if sheet_name else wb[wb.sheetnames[0]]

    # Capture the original layout and styles from the sample block in the template.
    max_col = ws.max_column
    title_row_idx = 1
    header_row_idx = 2
    detail_row_idx = 3
    blank_row_idx = 6

    name_label = ws.cell(title_row_idx, 1).value or "Name:"
    headers = [
        ws.cell(header_row_idx, 1).value or "Action",
        ws.cell(header_row_idx, 2).value or "Data",
        ws.cell(header_row_idx, 3).value or "Expected Result",
    ]

    title_height = ws.row_dimensions[title_row_idx].height or 24
    header_height = ws.row_dimensions[header_row_idx].height or 22
    sample_detail_heights = [
        ws.row_dimensions[row_idx].height
        for row_idx in range(detail_row_idx, blank_row_idx)
        if ws.row_dimensions[row_idx].height
    ]
    detail_height = min(sample_detail_heights) if sample_detail_heights else 22
    blank_height = ws.row_dimensions[blank_row_idx].height or 10

    # Start from a clean sheet while keeping sheet-level layout (column widths, sheet name, etc.).
    clear_sheet_values(ws)

    current_row = 1
    for case in test_cases:
        # Title row
        copy_template_row_style(ws, title_row_idx, current_row, max_col)
        ws.row_dimensions[current_row].height = title_height
        ws.cell(current_row, 1).value = name_label
        ws.cell(current_row, 2).value = case.name
        if max_col >= 3:
            ws.cell(current_row, 3).value = None
        current_row += 1

        # Header row
        copy_template_row_style(ws, header_row_idx, current_row, max_col)
        ws.row_dimensions[current_row].height = header_height
        for col, header in enumerate(headers, start=1):
            ws.cell(current_row, col).value = header
        current_row += 1

        # Step rows
        for step in case.steps:
            copy_template_row_style(ws, detail_row_idx, current_row, max_col)
            ws.row_dimensions[current_row].height = step_row_height(step, detail_height)
            ws.cell(current_row, 1).value = step.action
            ws.cell(current_row, 2).value = step.data
            ws.cell(current_row, 3).value = step.expected_result
            current_row += 1

        # Blank separator row
        copy_template_row_style(ws, blank_row_idx, current_row, max_col)
        ws.row_dimensions[current_row].height = blank_height
        for col in range(1, max_col + 1):
            ws.cell(current_row, col).value = None
        current_row += 1

    # Optional cleanup: clear remaining old rows below the new content.
    for row in range(current_row, ws.max_row + 1):
        for col in range(1, max_col + 1):
            ws.cell(row, col).value = None

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output_path)


def main() -> None:
    args = parse_args()
    test_cases = load_test_cases(args.json)
    build_excel(
        template_path=args.template,
        output_path=args.output,
        test_cases=test_cases,
        sheet_name=args.sheet,
    )
    print(f"Created: {args.output}")


if __name__ == "__main__":
    main()
