import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

TOKEN_FILE = Path(__file__).parent / "token_jira.txt"
DEFAULT_JIRA_SITE = "https://leadtech.atlassian.net"
API_SUFFIX = "/rest/api/3"


def load_jira_credentials(path: Path = TOKEN_FILE) -> Tuple[str, str, str]:
    """
    Reads credentials from token_jira.txt.

    Supported keys:
      JIRA_SITE=https://leadtech.atlassian.net
      JIRA_EMAIL=your-email@company.com
      JIRA_API_TOKEN=your_api_token

    Backward-compatible fallback keys:
      BITBUCKET_USERNAME=your-email@company.com
      BITBUCKET_TOKEN=your_api_token
    """
    if not path.exists():
        raise FileNotFoundError(f"Credentials file not found: {path}")

    creds: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        creds[key.strip()] = value.strip()

    jira_site = (
        creds.get("JIRA_SITE")
        or os.environ.get("JIRA_SITE")
        or DEFAULT_JIRA_SITE
    ).rstrip("/")

    jira_email = (
        creds.get("JIRA_EMAIL")
        or os.environ.get("JIRA_EMAIL")
        or creds.get("BITBUCKET_USERNAME")
        or os.environ.get("BITBUCKET_USERNAME")
    )

    jira_token = (
        creds.get("JIRA_API_TOKEN")
        or os.environ.get("JIRA_API_TOKEN")
        or creds.get("BITBUCKET_TOKEN")
        or os.environ.get("BITBUCKET_TOKEN")
    )

    if not jira_email or not jira_token:
        raise ValueError(
            "Missing Jira credentials. Expected JIRA_EMAIL and JIRA_API_TOKEN "
            "in token_jira.txt (or BITBUCKET_USERNAME / BITBUCKET_TOKEN as fallback)."
        )

    return jira_site, jira_email, jira_token


def create_session() -> requests.Session:
    jira_site, jira_email, jira_token = load_jira_credentials()
    session = requests.Session()
    session.auth = (jira_email, jira_token)
    session.headers.update(
        {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    )
    session.jira_site = jira_site  # type: ignore[attr-defined]
    session.jira_base_url = f"{jira_site}{API_SUFFIX}"  # type: ignore[attr-defined]
    return session


def extract_issue_key(issue_or_url: str) -> Tuple[str, Optional[str]]:
    """
    Accepts:
      - VISASGF-3978
      - https://leadtech.atlassian.net/browse/VISASGF-3978

    Returns:
      (issue_key, site_override_or_none)
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
        raise ValueError(
            "Expected an issue key like VISASGF-3978 or a Jira browse URL."
        )

    return value.upper(), None


def adf_to_text(node: Any) -> str:
    """
    Converts common Atlassian Document Format nodes to plain text.
    """
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
        parts: List[str] = []
        for item in content:
            text = adf_to_text(item).strip()
            if text:
                parts.append(text)
        return "\n".join(parts) + ("\n" if parts else "")

    if node_type == "listItem":
        parts: List[str] = []
        for item in content:
            text = adf_to_text(item).strip()
            if text:
                parts.append(text)
        if not parts:
            return ""
        return "- " + "\n  ".join(parts) + "\n"

    if node_type in {"doc", "blockquote", "panel"}:
        return "".join(adf_to_text(item) for item in content)

    return "".join(adf_to_text(item) for item in content)


def get_issue(
    issue_or_url: str,
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    issue_key, site_override = extract_issue_key(issue_or_url)
    session = create_session()

    if site_override:
        base_url = f"{site_override}{API_SUFFIX}"
        effective_site = site_override
    else:
        base_url = session.jira_base_url  # type: ignore[attr-defined]
        effective_site = session.jira_site  # type: ignore[attr-defined]

    selected_fields = fields or [
        "summary",
        "description",
        "issuetype",
        "status",
        "priority",
        "labels",
        "assignee",
        "reporter",
        "comment",
    ]

    url = f"{base_url}/issue/{issue_key}"
    response = session.get(
        url,
        params={"fields": ",".join(selected_fields)},
        timeout=30,
    )

    if response.status_code == 401:
        raise PermissionError(
            "401 Unauthorized. Check JIRA_EMAIL and JIRA_API_TOKEN."
        )
    if response.status_code == 403:
        raise PermissionError(
            "403 Forbidden. Your account may not have permission to view this issue."
        )
    if response.status_code == 404:
        # Jira returns 404 for both "does not exist" and "no permission to see it".
        # Presence of WWW-Authenticate in the 404 response indicates auth itself failed.
        if "WWW-Authenticate" in response.headers:
            raise PermissionError(
                "Authentication failed on the issue endpoint. Verify JIRA_EMAIL and "
                "JIRA_API_TOKEN, and that the token's scope includes 'read:jira-work'."
            )
        try:
            detail = response.json().get("errorMessages") or []
            detail_msg = " ".join(detail) if detail else ""
        except ValueError:
            detail_msg = ""
        raise FileNotFoundError(
            f"Issue {issue_key} not found or not visible to your account/token scope."
            + (f" Jira said: {detail_msg}" if detail_msg else "")
        )

    response.raise_for_status()
    raw = response.json()
    f = raw.get("fields", {})

    comments_raw = (f.get("comment") or {}).get("comments", [])
    comments: List[Dict[str, str]] = []
    for item in comments_raw:
        comments.append(
            {
                "author": (((item or {}).get("author") or {}).get("displayName") or ""),
                "created": (item or {}).get("created", ""),
                "body": adf_to_text((item or {}).get("body")).strip(),
            }
        )

    return {
        "key": raw.get("key", ""),
        "id": raw.get("id", ""),
        "url": f"{effective_site}/browse/{raw.get('key', issue_key)}",
        "summary": f.get("summary", "") or "",
        "description": adf_to_text(f.get("description")).strip(),
        "issue_type": ((f.get("issuetype") or {}).get("name") or ""),
        "status": ((f.get("status") or {}).get("name") or ""),
        "priority": ((f.get("priority") or {}).get("name") or ""),
        "labels": f.get("labels") or [],
        "assignee": ((f.get("assignee") or {}).get("displayName") or ""),
        "reporter": ((f.get("reporter") or {}).get("displayName") or ""),
        "comments": comments,
        "raw": raw,
    }


def print_issue(issue: Dict[str, Any]) -> None:
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

    if issue["comments"]:
        print(f"Comments ({len(issue['comments'])}):")
        for i, comment in enumerate(issue["comments"], start=1):
            print(f"[{i}] {comment['author']} - {comment['created']}")
            print(comment["body"] or "(empty)")
            print("-" * 80)
    else:
        print("Comments: none")
        print("-" * 80)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Read a Jira user story from token_jira.txt credentials."
    )
    parser.add_argument(
        "issue",
        help="Issue key like VISASGF-3978 or full browse URL.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of formatted text.",
    )
    args = parser.parse_args()

    issue = get_issue(args.issue)

    if args.json:
        print(json.dumps(issue, indent=2, ensure_ascii=False))
    else:
        print_issue(issue)