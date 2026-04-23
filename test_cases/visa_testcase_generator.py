"""
Backward-compat wrapper. Logic now lives in src/services/test_case_generator.py.

Prefer: python cli/generate_tests.py --json test_cases/test_cases.json

Usage (unchanged):
    python3 test_cases/visa_testcase_generator.py \\
        --json test_cases/test_cases.json \\
        --template test_cases/VISASGF-4167_test_cases.xlsx \\
        --output test_cases/test_cases.xlsx
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.generate_tests import main

if __name__ == "__main__":
    main()
