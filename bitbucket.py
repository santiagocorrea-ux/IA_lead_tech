"""
Backward-compat wrapper. Logic now lives in src/clients/bitbucket.py.

Usage (unchanged):
    python3 bitbucket.py VISASGF-4369
    python3 bitbucket.py VISASGF-4369 master
"""

import sys

from src.clients.bitbucket import commits_ahead_behind
from src import config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 bitbucket.py <branch> [base]")
        sys.exit(1)

    branch = sys.argv[1]
    base = sys.argv[2] if len(sys.argv) > 2 else config.BITBUCKET_DEFAULT_BASE
    info = commits_ahead_behind(branch, base)

    if not info["exists"]:
        print(f"Branch '{branch}' not found in {config.BITBUCKET_WORKSPACE}/{config.BITBUCKET_REPO}.")
    else:
        print(f"{info['branch']} vs {info['base']}: ahead={info['ahead']}, behind={info['behind']}")
