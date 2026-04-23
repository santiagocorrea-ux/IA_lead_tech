"""Jira issue model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Comment:
    author: str
    created: str
    body: str


@dataclass
class JiraIssue:
    key: str
    id: str
    url: str
    summary: str
    description: str
    issue_type: str
    status: str
    priority: str
    labels: list[str] = field(default_factory=list)
    assignee: str = ""
    reporter: str = ""
    comments: list[Comment] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "JiraIssue":
        return cls(
            key=data.get("key", ""),
            id=data.get("id", ""),
            url=data.get("url", ""),
            summary=data.get("summary", ""),
            description=data.get("description", ""),
            issue_type=data.get("issue_type", ""),
            status=data.get("status", ""),
            priority=data.get("priority", ""),
            labels=data.get("labels", []),
            assignee=data.get("assignee", ""),
            reporter=data.get("reporter", ""),
            comments=[Comment(**c) for c in data.get("comments", [])],
            raw=data.get("raw", {}),
        )
