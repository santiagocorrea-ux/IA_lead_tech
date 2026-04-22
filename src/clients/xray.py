"""Xray Cloud REST API client.

Authentication uses Xray's own credentials (Client ID + Client Secret),
NOT the Jira API token. Get your keys at:
  Jira → Apps → Xray → API Keys → Create

Set in .env:
  XRAY_CLIENT_ID=your_client_id
  XRAY_CLIENT_SECRET=your_client_secret
"""

from __future__ import annotations

from typing import Any

import requests

from src import config

XRAY_BASE = "https://xray.cloud.getxray.app/api/v2"
AUTH_URL = f"{XRAY_BASE}/authenticate"


def _get_token() -> str:
    """Exchange Client ID + Secret for a short-lived JWT."""
    client_id = config.XRAY_CLIENT_ID
    client_secret = config.XRAY_CLIENT_SECRET
    if not client_id or not client_secret:
        raise ValueError(
            "Missing Xray credentials. Set XRAY_CLIENT_ID and XRAY_CLIENT_SECRET in .env\n"
            "Get them at: Jira → Apps → Xray → API Keys → Create"
        )
    r = requests.post(
        AUTH_URL,
        json={"client_id": client_id, "client_secret": client_secret},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()  # returns the JWT string directly


def _session() -> tuple[requests.Session, str]:
    """Return (session, base_url) with Authorization header set."""
    token = _get_token()
    s = requests.Session()
    s.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    return s, XRAY_BASE


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------

def get_folders(project_key: str, folder_id: str | None = None) -> dict[str, Any]:
    """
    Return the folder tree for a project's test repository.

    If folder_id is given, returns that specific folder and its children.
    Otherwise returns the root folder tree.
    """
    s, base = _session()
    if folder_id:
        url = f"{base}/testrepository/{project_key}/folders/{folder_id}"
    else:
        url = f"{base}/testrepository/{project_key}/folders"
    r = s.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def get_tests_in_folder(
    project_key: str,
    folder_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return tests inside a specific Xray folder."""
    s, base = _session()
    url = f"{base}/testrepository/{project_key}/folders/{folder_id}/tests"
    tests: list[dict[str, Any]] = []
    start = 0
    while True:
        r = s.get(url, params={"limit": limit, "start": start}, timeout=30)
        r.raise_for_status()
        data = r.json()
        batch = data.get("tests") or data if isinstance(data, list) else []
        tests.extend(batch)
        if len(batch) < limit:
            break
        start += limit
    return tests


def print_folder_tree(node: dict[str, Any], indent: int = 0) -> None:
    """Recursively print a folder tree."""
    prefix = "  " * indent
    name = node.get("name") or node.get("id", "?")
    folder_id = node.get("id", "")
    test_count = node.get("testCount", "")
    count_str = f" ({test_count} tests)" if test_count else ""
    print(f"{prefix}📁 {name}{count_str}  [{folder_id}]")
    for child in node.get("folders", []):
        print_folder_tree(child, indent + 1)
