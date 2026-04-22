"""
Read Xray test issues via the standard Jira API.

Works with your existing JIRA_API_TOKEN — no Xray credentials needed.

Limitation: folder structure and test steps are stored in Xray's own
database and are NOT accessible through the Jira REST API.
"""

from __future__ import annotations

from typing import Any

from src import config
from src.clients.jira import adf_to_text, create_session

FIELD_TEST_TYPE = "customfield_11864"     # Manual / Automated
FIELD_CURRENT_STATUS = "customfield_12524"  # Ready for Testing / etc.
FIELD_AC = "customfield_15530"            # Acceptance Criteria

DEFAULT_FIELDS = [
    "summary", "status", "assignee", "priority", "labels",
    FIELD_TEST_TYPE, FIELD_CURRENT_STATUS, FIELD_AC,
]


def search_tests(
    project: str,
    jql_extra: str = "",
    max_results: int = 100,
    fields: list[str] | None = None,
) -> dict[str, Any]:
    """
    Search for Test issues in a Jira project.

    Args:
        project:    Jira project key, e.g. 'VISASGF'
        jql_extra:  Additional JQL clauses, e.g. 'AND summary ~ "login"'
        max_results: Max issues to return per call (use get_all_tests for pagination)
        fields:     Fields to fetch (defaults to summary + status + Xray fields)

    Returns dict with keys: total, issues
    """
    session = create_session()
    jql = f'project = {project} AND issuetype = Test {jql_extra} ORDER BY created DESC'

    r = session.post(
        f"{config.JIRA_SITE}{config.JIRA_API_SUFFIX}/search/jql",
        json={"jql": jql, "maxResults": max_results, "fields": fields or DEFAULT_FIELDS},
        timeout=config.JIRA_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def get_all_tests(
    project: str,
    jql_extra: str = "",
    fields: list[str] | None = None,
    page_size: int = 100,
) -> list[dict[str, Any]]:
    """Fetch all Test issues, handling pagination automatically."""
    session = create_session()
    jql = f'project = {project} AND issuetype = Test {jql_extra} ORDER BY created DESC'
    all_issues: list[dict[str, Any]] = []
    start = 0

    while True:
        r = session.post(
            f"{config.JIRA_SITE}{config.JIRA_API_SUFFIX}/search/jql",
            json={
                "jql": jql,
                "maxResults": page_size,
                "startAt": start,
                "fields": fields or DEFAULT_FIELDS,
            },
            timeout=config.JIRA_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        batch = data.get("issues", [])
        all_issues.extend(batch)
        if len(all_issues) >= (data.get("total") or 0) or not batch:
            break
        start += len(batch)

    return all_issues


def parse_test(issue: dict[str, Any]) -> dict[str, Any]:
    """Flatten a raw Jira issue into a clean test case dict."""
    f = issue.get("fields", {})
    ac_raw = f.get(FIELD_AC)
    ac = adf_to_text(ac_raw).strip() if isinstance(ac_raw, dict) else (ac_raw or "").strip()

    return {
        "key": issue.get("key", ""),
        "summary": f.get("summary", ""),
        "status": (f.get("status") or {}).get("name", ""),
        "assignee": ((f.get("assignee") or {}).get("displayName") or ""),
        "priority": ((f.get("priority") or {}).get("name") or ""),
        "labels": f.get("labels") or [],
        "test_type": (f.get(FIELD_TEST_TYPE) or {}).get("value", ""),
        "current_status": f.get(FIELD_CURRENT_STATUS) or "",
        "acceptance_criteria": ac,
    }
