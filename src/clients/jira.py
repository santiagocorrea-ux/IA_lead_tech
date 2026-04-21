"""Jira Cloud API client."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import requests

from src import config
from src.clients.base import make_session


def _require_credentials() -> tuple[str, str, str]:
    """Return (site, email, token), raising if any are missing."""
    if not config.JIRA_EMAIL or not config.JIRA_API_TOKEN:
        raise ValueError(
            "Missing Jira credentials. Set JIRA_EMAIL and JIRA_API_TOKEN in .env"
        )
    return config.JIRA_SITE, config.JIRA_EMAIL, config.JIRA_API_TOKEN


def create_session() -> requests.Session:
    site, email, token = _require_credentials()
    session = make_session(
        auth=(email, token),
        headers={"Accept": "application/json", "Content-Type": "application/json"},
    )
    session.jira_site = site  # type: ignore[attr-defined]
    session.jira_base_url = f"{site}{config.JIRA_API_SUFFIX}"  # type: ignore[attr-defined]
    return session


def extract_issue_key(issue_or_url: str) -> tuple[str, str | None]:
    """
    Accept an issue key ("VISASGF-3978") or a full browse URL.
    Returns (issue_key, site_override_or_None).
    """
    value = issue_or_url.strip()

    if value.startswith("http://") or value.startswith("https://"):
        parsed = urlparse(value)
        site = f"{parsed.scheme}://{parsed.netloc}"
        match = re.search(r"/browse/([^/?#]+)", parsed.path)
        if not match:
            raise ValueError(f"Could not extract Jira issue key from URL: {value}")
        return match.group(1).upper(), site

    if not re.fullmatch(r"[A-Z][A-Z0-9_]*-\d+", value, flags=re.IGNORECASE):
        raise ValueError("Expected an issue key like VISASGF-3978 or a Jira browse URL.")

    return value.upper(), None


def adf_to_text(node: Any) -> str:
    """Convert Atlassian Document Format nodes to plain text."""
    if node is None:
        return ""
    if isinstance(node, str):
        return node
    if isinstance(node, list):
        return "".join(adf_to_text(item) for item in node)
    if not isinstance(node, dict):
        return str(node)

    node_type = node.get("type")
    content = node.get("content", [])

    if node_type == "text":
        return node.get("text", "")
    if node_type == "hardBreak":
        return "\n"
    if node_type == "paragraph":
        text = "".join(adf_to_text(item) for item in content).strip()
        return f"{text}\n" if text else "\n"
    if node_type in {"bulletList", "orderedList"}:
        parts = [adf_to_text(item).strip() for item in content if adf_to_text(item).strip()]
        return "\n".join(parts) + ("\n" if parts else "")
    if node_type == "listItem":
        parts = [adf_to_text(item).strip() for item in content if adf_to_text(item).strip()]
        return ("- " + "\n  ".join(parts) + "\n") if parts else ""
    if node_type in {"doc", "blockquote", "panel"}:
        return "".join(adf_to_text(item) for item in content)

    return "".join(adf_to_text(item) for item in content)


def get_issue(
    issue_or_url: str,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """Fetch a Jira issue and return a structured dict."""
    issue_key, site_override = extract_issue_key(issue_or_url)
    session = create_session()

    if site_override:
        base_url = f"{site_override}{config.JIRA_API_SUFFIX}"
        effective_site = site_override
    else:
        base_url = session.jira_base_url  # type: ignore[attr-defined]
        effective_site = session.jira_site  # type: ignore[attr-defined]

    selected_fields = fields or [
        "summary", "description", "issuetype", "status",
        "priority", "labels", "assignee", "reporter", "comment",
        "customfield_15530",  # Acceptance Criteria
    ]

    url = f"{base_url}/issue/{issue_key}"
    response = session.get(url, params={"fields": ",".join(selected_fields)}, timeout=config.JIRA_TIMEOUT)

    if response.status_code == 401:
        raise PermissionError("401 Unauthorized. Check JIRA_EMAIL and JIRA_API_TOKEN.")
    if response.status_code == 403:
        raise PermissionError("403 Forbidden. Your account may not have permission to view this issue.")
    if response.status_code == 404:
        if "WWW-Authenticate" in response.headers:
            raise PermissionError(
                "Authentication failed on the issue endpoint. Verify credentials and token scope."
            )
        try:
            detail = " ".join(response.json().get("errorMessages") or [])
        except ValueError:
            detail = ""
        raise FileNotFoundError(
            f"Issue {issue_key} not found or not visible to your account."
            + (f" Jira said: {detail}" if detail else "")
        )

    response.raise_for_status()
    raw = response.json()
    f = raw.get("fields", {})

    comments = [
        {
            "author": (((item or {}).get("author") or {}).get("displayName") or ""),
            "created": (item or {}).get("created", ""),
            "body": adf_to_text((item or {}).get("body")).strip(),
        }
        for item in (f.get("comment") or {}).get("comments", [])
    ]

    ac_raw = f.get("customfield_15530")
    acceptance_criteria = adf_to_text(ac_raw).strip() if isinstance(ac_raw, dict) else (ac_raw or "").strip()

    return {
        "key": raw.get("key", ""),
        "id": raw.get("id", ""),
        "url": f"{effective_site}/browse/{raw.get('key', issue_key)}",
        "summary": f.get("summary", "") or "",
        "description": adf_to_text(f.get("description")).strip(),
        "acceptance_criteria": acceptance_criteria,
        "issue_type": ((f.get("issuetype") or {}).get("name") or ""),
        "status": ((f.get("status") or {}).get("name") or ""),
        "priority": ((f.get("priority") or {}).get("name") or ""),
        "labels": f.get("labels") or [],
        "assignee": ((f.get("assignee") or {}).get("displayName") or ""),
        "reporter": ((f.get("reporter") or {}).get("displayName") or ""),
        "comments": comments,
        "raw": raw,
    }


def print_issue(issue: dict[str, Any]) -> None:
    print("=" * 80)
    print(f"Key:        {issue['key']}")
    print(f"Type:       {issue['issue_type']}")
    print(f"Status:     {issue['status']}")
    print(f"Priority:   {issue['priority']}")
    print(f"Assignee:   {issue['assignee'] or '-'}")
    print(f"Reporter:   {issue['reporter'] or '-'}")
    print(f"Labels:     {', '.join(issue['labels']) if issue['labels'] else '-'}")
    print(f"Summary:    {issue['summary']}")
    print(f"Browse URL: {issue['url']}")
    print("-" * 80)
    print("Description:")
    print(issue["description"] or "(empty)")
    print("-" * 80)
    print("Acceptance Criteria:")
    print(issue.get("acceptance_criteria") or "(empty)")
    print("-" * 80)
    if issue["comments"]:
        print(f"Comments ({len(issue['comments'])}):")
        for i, c in enumerate(issue["comments"], start=1):
            print(f"[{i}] {c['author']} - {c['created']}")
            print(c["body"] or "(empty)")
            print("-" * 80)
    else:
        print("Comments: none")
        print("-" * 80)
