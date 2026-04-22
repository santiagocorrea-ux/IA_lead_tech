"""
Central configuration.

Priority order for credentials:
  1. Environment variables (set in shell or loaded from .env)
  2. Legacy credential files (token_jira.txt / token.txt) for backward compat
  3. Hard-coded defaults (non-sensitive values only)

Add a .env file at the project root (see .env.example) and never commit it.
"""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# .env loader (optional – works if python-dotenv is installed)
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------

def _read_kv_file(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE text file, ignoring comments and blank lines."""
    if not path.exists():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def _get(env_key: str, file_keys: list[str], files: list[dict], default: str = "") -> str:
    """Resolve a config value: env var → file fallbacks → default."""
    if (val := os.environ.get(env_key)):
        return val
    for key in file_keys:
        for file_dict in files:
            if (val := file_dict.get(key)):
                return val
    return default


# Load legacy credential files once at import time.
_jira_file = _read_kv_file(ROOT / "token_jira.txt")
_bb_file = _read_kv_file(ROOT / "token.txt")


# ---------------------------------------------------------------------------
# Jira
# ---------------------------------------------------------------------------
JIRA_SITE: str = _get(
    "JIRA_SITE", ["JIRA_SITE"], [_jira_file],
    default="https://leadtech.atlassian.net",
).rstrip("/")

JIRA_EMAIL: str = _get(
    "JIRA_EMAIL", ["JIRA_EMAIL", "BITBUCKET_USERNAME"], [_jira_file, _bb_file],
)

JIRA_API_TOKEN: str = _get(
    "JIRA_API_TOKEN", ["JIRA_API_TOKEN", "BITBUCKET_TOKEN"], [_jira_file, _bb_file],
)

JIRA_API_SUFFIX = "/rest/api/3"
JIRA_TIMEOUT = 30  # seconds

# ---------------------------------------------------------------------------
# Bitbucket
# ---------------------------------------------------------------------------
BITBUCKET_WORKSPACE: str = _get(
    "BITBUCKET_WORKSPACE", ["BITBUCKET_WORKSPACE"], [_bb_file],
    default="grupoblidoo",
)

BITBUCKET_REPO: str = _get(
    "BITBUCKET_REPO", ["BITBUCKET_REPO"], [_bb_file],
    default="visas-public",
)

BITBUCKET_DEFAULT_BASE: str = _get(
    "BITBUCKET_DEFAULT_BASE", [], [],
    default="master",
)

BITBUCKET_USERNAME: str = _get(
    "BITBUCKET_USERNAME", ["BITBUCKET_USERNAME"], [_bb_file, _jira_file],
)

BITBUCKET_TOKEN: str = _get(
    "BITBUCKET_TOKEN", ["BITBUCKET_TOKEN"], [_bb_file, _jira_file],
)

BITBUCKET_API_ROOT = "https://api.bitbucket.org/2.0"
BITBUCKET_PAGE_SIZE = 100
BITBUCKET_TIMEOUT = 15  # seconds

# ---------------------------------------------------------------------------
# Xray Cloud
# ---------------------------------------------------------------------------
XRAY_CLIENT_ID: str = _get("XRAY_CLIENT_ID", ["XRAY_CLIENT_ID"], [])
XRAY_CLIENT_SECRET: str = _get("XRAY_CLIENT_SECRET", ["XRAY_CLIENT_SECRET"], [])

# ---------------------------------------------------------------------------
# Browser automation
# ---------------------------------------------------------------------------
CHROME_PROFILE_DIR: str = _get(
    "CHROME_PROFILE_DIR", [], [],
    default="/Users/10pearls/pw-debug-profile",
)

TARGET_URL = "https://zerotrust.1ecorp.net/"
TASK_MANAGER_URL = "https://task-manager.1evis.net/workspaces-info"
TASK_SUMMARY_URL = "https://task-manager.1evis.net/summary/visasgf"
GOOGLE_BUTTON_TEXT = "Continue as Santiago"

# ---------------------------------------------------------------------------
# Application constants
# ---------------------------------------------------------------------------
DAYS_THRESHOLD = 2
DATE_FORMAT = "%d/%m/%Y %H:%M"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
TEST_CASES_DIR = ROOT / "test_cases"
EXCEL_TEMPLATE = TEST_CASES_DIR / "VISASGF-4167_test_cases.xlsx"
DEFAULT_JSON_OUTPUT = TEST_CASES_DIR / "test_cases.json"
DEFAULT_EXCEL_OUTPUT = TEST_CASES_DIR / "test_cases.xlsx"
