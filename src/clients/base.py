"""Shared HTTP session factory with retry and backoff."""

from __future__ import annotations

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def make_session(
    auth: tuple[str, str] | None = None,
    headers: dict[str, str] | None = None,
    retries: int = 3,
    backoff: float = 0.5,
) -> requests.Session:
    """Return a requests.Session with automatic retry on transient errors."""
    session = requests.Session()

    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if auth:
        session.auth = auth
    if headers:
        session.headers.update(headers)

    return session
