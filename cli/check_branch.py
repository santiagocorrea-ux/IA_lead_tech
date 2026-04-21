#!/usr/bin/env python3
"""
Look up one or more branches in the task manager dashboard and
print a health report including Bitbucket commit metrics.

Usage (from project root):
    python cli/check_branch.py VISASGF-4369
    python cli/check_branch.py VISASGF-4369 VISASGF-4370 --partial
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from playwright.sync_api import sync_playwright

from src import config
from src.automation.browser import (
    get_branch_info,
    navigate_to_task_summary,
    navigate_to_task_table,
)
from src.clients import bitbucket


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Look up one or more branches in the task manager.")
    parser.add_argument("branches", nargs="+", help="Branch names, e.g. VISASGF-2864")
    parser.add_argument("--partial", action="store_true", help="Allow partial branch name matches.")
    return parser.parse_args()


def print_branch_report(info: dict[str, Any]) -> None:
    actions = [a["title"] for a in info["_meta"]["actions"] if a.get("title")]
    if "Upgrade instance" in actions:
        upgrade_text = "Requires upgrade"
    elif "Downgrade instance" in actions:
        upgrade_text = "No upgrade needed (downgrade available)"
    else:
        upgrade_text = "No action needed"

    print("=" * 70)
    print(f"Branch:              {info.get('Branch')}")
    print(f"Environment URL:     {info.get('Environment URL')}")
    print(f"Environment status:  {info.get('Status')}")
    print(f"AWS Instance Type:   {info.get('AWS Instance Type')}")
    print(f"Jira status:         {info.get('Jira status') or 'Not available'}")
    print(f"Jira ID:             {info['_meta'].get('jira_id') or 'Not available'}")
    print(f"Environment link:    {info['_meta'].get('environment_link') or 'Not available'}")
    print(f"Actions:             {', '.join(actions) if actions else 'None'}")
    print()
    print("Date comparison:")
    print(f"  Creation Date:       {info.get('Creation Date')}")
    print(f"  Days Since Creation: {info['Days Since Creation']}")
    print(f"  Older than {config.DAYS_THRESHOLD} days?  {info['Older Than Threshold']}")
    print(f"  Instance status:     {upgrade_text}")
    print()
    print("Bitbucket comparison vs master:")
    try:
        bb = bitbucket.commits_ahead_behind(info.get("Branch", ""))
        if not bb["exists"]:
            print(f"  Branch '{bb['branch']}' not found in Bitbucket.")
        else:
            print(f"  Ahead:  {bb['ahead']} commits")
            print(f"  Behind: {bb['behind']} commits")
    except Exception as e:
        print(f"  Bitbucket lookup failed: {e}")


def main() -> None:
    args = parse_args()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            config.CHROME_PROFILE_DIR,
            channel="chrome",
            headless=False,
            no_viewport=True,
            args=["--start-maximized"],
        )

        try:
            zero_page = context.pages[0] if context.pages else context.new_page()
            zero_page.goto(config.TARGET_URL, wait_until="domcontentloaded")
            zero_page.bring_to_front()

            summary_page = context.new_page()
            navigate_to_task_summary(summary_page)

            task_page = context.new_page()
            navigate_to_task_table(task_page)

            for branch_name in args.branches:
                try:
                    info = get_branch_info(task_page, branch_name, allow_partial=args.partial)
                    print_branch_report(info)
                except Exception as e:
                    print("=" * 70)
                    print(f"Error for branch '{branch_name}': {e}")

            input("Press Enter to close...")

        finally:
            context.close()


if __name__ == "__main__":
    main()
