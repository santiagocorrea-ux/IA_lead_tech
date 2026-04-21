"""
Backward-compat wrapper. Logic now lives in src/automation/browser.py.

Prefer: python cli/check_branch.py VISASGF-4369 [--partial]
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path when run directly.
sys.path.insert(0, str(Path(__file__).parent))

from cli.check_branch import main

if __name__ == "__main__":
    main()
