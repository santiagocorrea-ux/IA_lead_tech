"""Bitbucket Cloud API client."""

from __future__ import annotations

from typing import Any

import requests

from src import config
from src.clients.base import make_session


def _require_credentials() -> tuple[str, str]:
    if not config.BITBUCKET_USERNAME or not config.BITBUCKET_TOKEN:
        raise ValueError(
            "Missing Bitbucket credentials. Set BITBUCKET_USERNAME and BITBUCKET_TOKEN "
            "in .env (or token.txt for backward compat)."
        )
    return config.BITBUCKET_USERNAME, config.BITBUCKET_TOKEN


def create_session() -> requests.Session:
    username, token = _require_credentials()
    return make_session(auth=(username, token), headers={"Accept": "application/json"})


def branch_exists(
    branch: str,
    workspace: str = config.BITBUCKET_WORKSPACE,
    repo: str = config.BITBUCKET_REPO,
) -> bool:
    session = create_session()
    url = f"{config.BITBUCKET_API_ROOT}/repositories/{workspace}/{repo}/refs/branches/{branch}"
    r = session.get(url, timeout=config.BITBUCKET_TIMEOUT)
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
    """Walk paginated commits endpoint; return total up to max_count."""
    session = create_session()
    url: str | None = (
        f"{config.BITBUCKET_API_ROOT}/repositories/{workspace}/{repo}/commits/"
        f"?include={include}&exclude={exclude}&pagelen={config.BITBUCKET_PAGE_SIZE}"
    )
    total = 0
    while url:
        r = session.get(url, timeout=config.BITBUCKET_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        total += len(data.get("values", []))
        if total >= max_count:
            return total
        url = data.get("next")
    return total


def commits_ahead_behind(
    branch: str,
    base: str = config.BITBUCKET_DEFAULT_BASE,
    *,
    workspace: str = config.BITBUCKET_WORKSPACE,
    repo: str = config.BITBUCKET_REPO,
) -> dict[str, Any]:
    """Return ahead/behind commit counts for `branch` relative to `base`."""
    if not branch_exists(branch, workspace=workspace, repo=repo):
        return {"branch": branch, "base": base, "ahead": None, "behind": None, "exists": False}

    ahead = _count_commits(branch, base, workspace=workspace, repo=repo)
    behind = _count_commits(base, branch, workspace=workspace, repo=repo)
    return {"branch": branch, "base": base, "ahead": ahead, "behind": behind, "exists": True}
