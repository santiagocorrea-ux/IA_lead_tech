"""
Backward-compat wrapper. Logic now lives in src/clients/jira.py.

Usage (unchanged):
    python3 jira_reader.py VISASGF-3978
    python3 jira_reader.py VISASGF-3978 --json
"""

import argparse
import json

from src.clients.jira import get_issue, print_issue

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Read a Jira issue.")
    parser.add_argument("issue", help="Issue key like VISASGF-3978 or full browse URL.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of formatted text.")
    args = parser.parse_args()

    issue = get_issue(args.issue)

    if args.json:
        print(json.dumps(issue, indent=2, ensure_ascii=False))
    else:
        print_issue(issue)
