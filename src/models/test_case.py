"""Test case models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Step:
    action: str = ""
    data: str = ""
    expected_result: str = ""


@dataclass
class TestCase:
    name: str
    steps: list[Step] = field(default_factory=list)
