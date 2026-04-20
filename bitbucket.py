import os
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

WORKSPACE = "grupoblidoo"
REPO_SLUG = "visas-public"
DEFAULT_BASE = "master"
TOKEN_FILE = Path(__file__).parent / "token.txt"
API_ROOT = "https://api.bitbucket.org/2.0"
PAGE_SIZE = 100


def load_credentials(path: Path = TOKEN_FILE) -> Tuple[str, str]:
    if not path.exists():
        raise FileNotFoundError(f"Credentials file not found: {path}")

    creds: Dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        creds[key.strip()] = value.strip()

    username = creds.get("BITBUCKET_USERNAME") or os.environ.get("BITBUCKET_USERNAME")
    token = creds.get("BITBUCKET_TOKEN") or os.environ.get("BITBUCKET_TOKEN")

    if not username or not token:
        raise ValueError(
            "Missing BITBUCKET_USERNAME or BITBUCKET_TOKEN in token.txt or env."
        )
    return username, token


def _session() -> requests.Session:
    username, token = load_credentials()
    s = requests.Session()
    s.auth = (username, token)
    s.headers.update({"Accept": "application/json"})
    return s


def branch_exists(branch: str, *, workspace: str = WORKSPACE, repo: str = REPO_SLUG) -> bool:
    s = _session()
    url = f"{API_ROOT}/repositories/{workspace}/{repo}/refs/branches/{branch}"
    r = s.get(url, timeout=15)
    if r.status_code == 404:
        return False
    r.raise_for_status()
    return True


def _count_commits(
    include: str,
    exclude: str,
    *,
    workspace: str,
    repo: str,
    max_count: int = 500,
) -> int:
    """Walk paginated commits endpoint, return total count up to max_count."""
    s = _session()
    url: Optional[str] = (
        f"{API_ROOT}/repositories/{workspace}/{repo}/commits/"
        f"?include={include}&exclude={exclude}&pagelen={PAGE_SIZE}"
    )
    total = 0
    while url:
        r = s.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        total += len(data.get("values", []))
        if total >= max_count:
            return total
        url = data.get("next")
    return total


def commits_ahead_behind(
    branch: str,
    base: str = DEFAULT_BASE,
    *,
    workspace: str = WORKSPACE,
    repo: str = REPO_SLUG,
) -> Dict[str, object]:
    """Return ahead/behind counts for `branch` relative to `base`.

    Returns dict with keys: branch, base, ahead, behind, exists.
    If the branch does not exist, ahead/behind are None.
    """
    if not branch_exists(branch, workspace=workspace, repo=repo):
        return {"branch": branch, "base": base, "ahead": None, "behind": None, "exists": False}

    ahead = _count_commits(branch, base, workspace=workspace, repo=repo)
    behind = _count_commits(base, branch, workspace=workspace, repo=repo)
    return {
        "branch": branch,
        "base": base,
        "ahead": ahead,
        "behind": behind,
        "exists": True,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 bitbucket.py <branch> [base]")
        sys.exit(1)
    branch = sys.argv[1]
    base = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BASE
    info = commits_ahead_behind(branch, base)
    if not info["exists"]:
        print(f"Branch '{branch}' not found in {WORKSPACE}/{REPO_SLUG}.")
    else:
        print(f"{info['branch']} vs {info['base']}: ahead={info['ahead']}, behind={info['behind']}")
