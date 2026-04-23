"""Branch info model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BranchInfo:
    name: str
    environment_url: str
    status: str
    creation_date: datetime
    aws_instance_type: str
    jira_status: str
    jira_id: str
    days_since_creation: int
    older_than_threshold: bool
    actions: list[str]
    # Bitbucket data (None if branch not found in Bitbucket)
    commits_ahead: int | None = None
    commits_behind: int | None = None
    exists_in_bitbucket: bool = False
